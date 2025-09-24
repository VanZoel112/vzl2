import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS
from config import Config

"""
Enhanced Blacklist Plugin for Vzoel Fox's Userbot - Premium Edition
Fitur: Advanced blacklist system dengan premium filtering
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Blacklist System
"""

from telethon import events
from telethon.errors import MessageDeleteForbiddenError, ChatAdminRequiredError
import asyncio
import json
import os
import re

# Plugin info
__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Global variables
blacklist_words = {}  # {chat_id: [words]}
locked_users = {}     # {chat_id: [user_ids]}
blacklist_active = {}  # {chat_id: True/False}

# File for persistent storage
BLACKLIST_FILE = "blacklist_data.json"

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, blacklist_words, locked_users, blacklist_active

    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler

    # Load existing blacklist data
    load_blacklist_data()

    # Initialize config and load global locked users
    Config.load_blacklist()

    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Blacklist Plugin loaded - Word filtering ready")
    print(f"{signature} Global locked users: {len(Config.LOCKED_USERS_GLOBAL)}")

def load_blacklist_data():
    """Load blacklist data from file"""
    global blacklist_words, locked_users, blacklist_active
    
    try:
        if os.path.exists(BLACKLIST_FILE):
            with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                blacklist_words = {int(k): v for k, v in data.get('blacklist_words', {}).items()}
                locked_users = {int(k): v for k, v in data.get('locked_users', {}).items()}
                blacklist_active = {int(k): v for k, v in data.get('blacklist_active', {}).items()}
    except Exception as e:
        print(f"Error loading blacklist data: {e}")
        blacklist_words = {}
        locked_users = {}
        blacklist_active = {}

def save_blacklist_data():
    """Save blacklist data to file"""
    try:
        data = {
            'blacklist_words': {str(k): v for k, v in blacklist_words.items()},
            'locked_users': {str(k): v for k, v in locked_users.items()},
            'blacklist_active': {str(k): v for k, v in blacklist_active.items()}
        }
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving blacklist data: {e}")

@events.register(events.NewMessage(pattern=r'\.bl( (.+))?'))
async def add_blacklist_handler(event):
    """Add words to blacklist for automatic deletion"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        chat_id = event.chat_id
        
        # Get words to blacklist
        blacklist_text = None
        if event.reply_to_msg_id:
            # Reply mode - get replied message
            replied_msg = await event.get_reply_message()
            blacklist_text = replied_msg.message
        else:
            # Text mode - get text after .bl
            match = event.pattern_match
            if match and match.group(2):
                blacklist_text = match.group(2)
        
        if not blacklist_text:
            help_msg = f"""{get_emoji('kuning')} Blacklist Usage:
• `.bl <kata>` - Tambah kata ke blacklist
• `.bl` (reply) - Tambah pesan yang direply
• `.wl <kata>` - Hapus dari blacklist
• `.lock @user` - Lock user (hapus semua pesan)
• `.blinfo` - Info blacklist system"""
            await safe_edit_premium(event, help_msg)
            return
        
        # Initialize chat blacklist if not exists
        if chat_id not in blacklist_words:
            blacklist_words[chat_id] = []
            blacklist_active[chat_id] = True
        
        # Process words (split by spaces, commas, etc.)
        words = re.split(r'[,\s]+', blacklist_text.strip())
        words = [word.lower().strip() for word in words if word.strip()]
        
        added_words = []
        for word in words:
            if word not in blacklist_words[chat_id]:
                blacklist_words[chat_id].append(word)
                added_words.append(word)
        
        # Save data
        save_blacklist_data()
        
        if added_words:
            success_msg = f"""{get_emoji('centang')} BLACKLIST UPDATED

{get_emoji('merah')} Kata Ditambahkan: {len(added_words)}
{get_emoji('aktif')} Words: {', '.join(added_words)}
{get_emoji('telegram')} Total Blacklist: {len(blacklist_words[chat_id])} kata
{get_emoji('petir')} Status: Auto-delete aktif

{get_emoji('proses')} Pesan yang mengandung kata ini akan otomatis dihapus

Vzoel Fox's Blacklist System"""
        else:
            success_msg = f"{get_emoji('kuning')} Semua kata sudah ada di blacklist"
        
        await safe_edit_premium(event, success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.wl( (.+))?'))
async def remove_blacklist_handler(event):
    """Remove words from blacklist (whitelist)"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        chat_id = event.chat_id
        
        # Get words to whitelist
        whitelist_text = None
        if event.reply_to_msg_id:
            # Reply mode - get replied message
            replied_msg = await event.get_reply_message()
            whitelist_text = replied_msg.message
        else:
            # Text mode - get text after .wl
            match = event.pattern_match
            if match and match.group(2):
                whitelist_text = match.group(2)
        
        if not whitelist_text:
            # Show current blacklist
            if chat_id in blacklist_words and blacklist_words[chat_id]:
                blacklist_list = ', '.join(blacklist_words[chat_id])
                current_msg = f"""{get_emoji('telegram')} BLACKLIST CURRENT

{get_emoji('merah')} Total: {len(blacklist_words[chat_id])} kata
{get_emoji('aktif')} Words: {blacklist_list[:500]}{'...' if len(blacklist_list) > 500 else ''}

{get_emoji('centang')} Untuk menghapus: `.wl <kata>`
{get_emoji('kuning')} Clear semua: `.wl clear`

Vzoel Fox's Blacklist"""
            else:
                current_msg = f"{get_emoji('kuning')} Blacklist kosong di chat ini"
                
            await safe_edit_premium(event, current_msg)
            return
        
        if chat_id not in blacklist_words:
            blacklist_words[chat_id] = []
        
        # Handle clear command
        if whitelist_text.lower() == 'clear':
            cleared_count = len(blacklist_words[chat_id])
            blacklist_words[chat_id] = []
            save_blacklist_data()
            clear_msg = f"""{get_emoji('centang')} BLACKLIST CLEARED

{get_emoji('aktif')} Dihapus: {cleared_count} kata
{get_emoji('telegram')} Status: Blacklist kosong
{get_emoji('proses')} Auto-delete: Non-aktif

Vzoel Fox's Blacklist System"""
            await safe_edit_premium(event, clear_msg)
            return
        
        # Process words to remove
        words = re.split(r'[,\s]+', whitelist_text.strip())
        words = [word.lower().strip() for word in words if word.strip()]
        
        removed_words = []
        for word in words:
            if word in blacklist_words[chat_id]:
                blacklist_words[chat_id].remove(word)
                removed_words.append(word)
        
        # Save data
        save_blacklist_data()
        
        if removed_words:
            success_msg = f"""{get_emoji('centang')} WHITELIST UPDATED

{get_emoji('aktif')} Kata Dihapus: {len(removed_words)}
{get_emoji('telegram')} Words: {', '.join(removed_words)}
{get_emoji('proses')} Sisa Blacklist: {len(blacklist_words[chat_id])} kata

{get_emoji('centang')} Kata ini tidak akan dihapus lagi

Vzoel Fox's Whitelist System"""
        else:
            success_msg = f"{get_emoji('kuning')} Kata tidak ditemukan di blacklist"
        
        await safe_edit_premium(event, success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.lock( (.+))?'))
async def lock_user_handler(event):
    """Lock user to delete all their messages"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        chat_id = event.chat_id
        target_user = None
        
        # Get target user
        if event.reply_to_msg_id:
            # Reply mode - get user from replied message
            replied_msg = await event.get_reply_message()
            target_user = replied_msg.sender_id
        else:
            # Username mode - get text after .lock
            match = event.pattern_match
            if match and match.group(2):
                username = match.group(2).strip().replace('@', '')
                try:
                    # Get user entity
                    user_entity = await event.client.get_entity(username)
                    target_user = user_entity.id
                except Exception:
                    error_msg = f"{get_emoji('merah')} User @{username} tidak ditemukan"
                    await safe_edit_premium(event, error_msg)
                    return
        
        if not target_user:
            help_msg = f"""{get_emoji('kuning')} Lock usage: .lock @user

Commands: .lock @user, .unlock @user, .locked
• `.unlock @username` - Unlock user
• `.locked` - List locked users

{get_emoji('telegram')} - 2025 Vzoel Fox's (LTPN)"""
            await safe_edit_premium(event, help_msg)
            return
        
        # Initialize chat locked users if not exists
        if chat_id not in locked_users:
            locked_users[chat_id] = []
        
        # Add user to local and global locked list
        local_added = False
        global_added = False

        # Add to local chat lock
        if target_user not in locked_users[chat_id]:
            locked_users[chat_id].append(target_user)
            local_added = True

        # Add to global config lock (auto-update config and env)
        global_added = Config.add_locked_user(target_user)

        if local_added or global_added:
            save_blacklist_data()

            # Get user info
            try:
                user_info = await event.client.get_entity(target_user)
                user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
            except:
                user_display = f"User ID: {target_user}"

            status_text = []
            if local_added:
                status_text.append(f"{get_emoji('telegram')} Local chat lock")
            if global_added:
                status_text.append(f"{get_emoji('petir')} Global config lock")

            lock_msg = f"""{get_emoji('merah')} USER LOCKED

{get_emoji('aktif')} User: {user_display}
{get_emoji('proses')} Status: {' + '.join(status_text) if status_text else 'Already locked'}
{get_emoji('centang')} Local locked: {len(locked_users[chat_id])} users
{get_emoji('telegram')} Global locked: {len(Config.LOCKED_USERS_GLOBAL)} users

{get_emoji('kuning')} Config.py & .env auto-updated
{get_emoji('proses')} Semua pesan user ini akan dihapus

{get_emoji('centang')} Unlock: `.unlock {user_display}`

Vzoel Fox's Enhanced Lock System"""
            await safe_edit_premium(event, lock_msg)
        else:
            already_msg = f"{get_emoji('kuning')} User sudah di-lock sebelumnya (local & global)"
            await safe_edit_premium(event, already_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.unlock( (.+))?'))
async def unlock_user_handler(event):
    """Unlock user to stop deleting their messages"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        chat_id = event.chat_id
        target_user = None
        
        # Get target user (same logic as lock)
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            target_user = replied_msg.sender_id
        else:
            match = event.pattern_match
            if match and match.group(2):
                username = match.group(2).strip().replace('@', '')
                try:
                    user_entity = await event.client.get_entity(username)
                    target_user = user_entity.id
                except Exception:
                    error_msg = f"{get_emoji('merah')} User @{username} tidak ditemukan"
                    await safe_edit_premium(event, error_msg)
                    return
        
        if not target_user:
            # Show locked users (local and global)
            local_locked = locked_users.get(chat_id, [])
            global_locked = Config.LOCKED_USERS_GLOBAL

            if local_locked or global_locked:
                # Show local locked users
                local_list = []
                for user_id in local_locked[:5]:  # Max 5 users
                    try:
                        user_info = await event.client.get_entity(user_id)
                        user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
                        local_list.append(user_display)
                    except:
                        local_list.append(f"ID: {user_id}")

                # Show global locked users
                global_list = []
                for user_id in global_locked[:5]:  # Max 5 users
                    try:
                        user_info = await event.client.get_entity(user_id)
                        user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
                        global_list.append(user_display)
                    except:
                        global_list.append(f"ID: {user_id}")

                locked_msg = f"""{get_emoji('telegram')} LOCKED USERS STATUS

{get_emoji('centang')} Local Chat ({len(local_locked)} users):
{', '.join(local_list) if local_list else 'None'}

{get_emoji('petir')} Global Config ({len(global_locked)} users):
{', '.join(global_list) if global_list else 'None'}

{get_emoji('aktif')} Total Effective: {len(set(local_locked + global_locked))} unique users

{get_emoji('kuning')} Commands:
• `.unlock @username` - Unlock user
• `.unlock clear` - Clear local locks

Vzoel Fox's Enhanced Lock System"""
            else:
                locked_msg = f"{get_emoji('kuning')} Tidak ada user yang di-lock (local atau global)"
            await safe_edit_premium(event, locked_msg)
            return
        
        if chat_id not in locked_users:
            locked_users[chat_id] = []
        
        # Remove user from local and global locked list
        local_removed = False
        global_removed = False

        # Remove from local chat lock
        if target_user in locked_users[chat_id]:
            locked_users[chat_id].remove(target_user)
            local_removed = True

        # Remove from global config lock (auto-update config and env)
        global_removed = Config.remove_locked_user(target_user)

        if local_removed or global_removed:
            save_blacklist_data()

            try:
                user_info = await event.client.get_entity(target_user)
                user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
            except:
                user_display = f"User ID: {target_user}"

            status_text = []
            if local_removed:
                status_text.append(f"{get_emoji('telegram')} Local chat unlock")
            if global_removed:
                status_text.append(f"{get_emoji('petir')} Global config unlock")

            unlock_msg = f"""{get_emoji('centang')} USER UNLOCKED

{get_emoji('aktif')} User: {user_display}
{get_emoji('proses')} Removed: {' + '.join(status_text) if status_text else 'Not in lists'}
{get_emoji('centang')} Local locked: {len(locked_users[chat_id])} users
{get_emoji('telegram')} Global locked: {len(Config.LOCKED_USERS_GLOBAL)} users

{get_emoji('kuning')} Config.py & .env auto-updated
{get_emoji('proses')} Pesan user tidak akan dihapus lagi

Vzoel Fox's Enhanced Unlock System"""
            await safe_edit_premium(event, unlock_msg)
        else:
            not_locked_msg = f"{get_emoji('kuning')} User tidak dalam daftar lock (local atau global)"
            await safe_edit_premium(event, not_locked_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(incoming=True))
async def auto_delete_handler(event):
    """Automatically delete messages based on blacklist and locked users"""
    # Skip if it's our own message
    if event.sender_id == (await event.client.get_me()).id:
        return
    
    chat_id = event.chat_id
    sender_id = event.sender_id
    
    try:
        # Check if user is locked (local or global)
        local_locked = chat_id in locked_users and sender_id in locked_users[chat_id]
        global_locked = Config.is_locked_user(sender_id)

        if local_locked or global_locked:
            await event.delete()
            return
        
        # Check blacklist words
        if (chat_id in blacklist_words and 
            blacklist_words[chat_id] and 
            blacklist_active.get(chat_id, True) and 
            event.message):
            message_text = event.message.lower()
            # Check if any blacklist word is in the message
            for word in blacklist_words[chat_id]:
                if word in message_text:
                    await event.delete()
                    return
                    
    except (MessageDeleteForbiddenError, ChatAdminRequiredError):
        # Can't delete message (no permission)
        pass
    except Exception as e:
        # Log error but don't break
        print(f"Auto-delete error: {e}")

@events.register(events.NewMessage(pattern=r'\.blinfo'))
async def blacklist_info_handler(event):
    """Show blacklist system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        
        chat_id = event.chat_id
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Get stats
        word_count = len(blacklist_words.get(chat_id, []))
        local_locked_count = len(locked_users.get(chat_id, []))
        global_locked_count = len(Config.LOCKED_USERS_GLOBAL)
        status = "Aktif" if blacklist_active.get(chat_id, True) else "Non-aktif"

        blacklist_info = f"""{signature} Enhanced Blacklist System

{get_emoji('merah')} Blacklist Words: {word_count} kata
{get_emoji('centang')} Local Locked: {local_locked_count} users
{get_emoji('petir')} Global Locked: {global_locked_count} users
{get_emoji('telegram')} Status: {status}

{get_emoji('centang')} Word Commands:
• `.bl <kata>` - Add blacklist word
• `.wl <kata>` - Remove blacklist word
• `.wl clear` - Clear all blacklist words

{get_emoji('aktif')} User Lock Commands:
• `.lock @user` - Lock user (local + global)
• `.unlock @user` - Unlock user (local + global)
• `.unlock` - Show locked users status
• `.blchat` - Lock entire chat globally

{get_emoji('proses')} Enhanced Features:
• Dual-layer locking (local chat + global config)
• Auto-update config.py and .env files
• Persistent storage across restarts
• Global user locks work in all chats
• Smart status reporting

{get_emoji('petir')} Auto-Delete Logic:
Sistem akan otomatis menghapus pesan dari:
1. User yang di-lock secara lokal di chat ini
2. User yang di-lock secara global (semua chat)
3. Pesan yang mengandung kata blacklist

{get_emoji('kuning')} Config Integration:
Locked users otomatis tersimpan ke config.py dan .env untuk persistence maksimal.

Vzoel Fox's Enhanced Blacklist System v3.0"""
        
        await safe_edit_premium(event, blacklist_info)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.blchat'))
async def blacklist_chat_handler(event):
    """Lock entire chat globally (blacklist chat)"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        chat_id = event.chat_id

        # Add chat to gcast blacklist using Config system
        chat_added = Config.add_to_blacklist(chat_id)

        if chat_added:
            try:
                chat_info = await event.client.get_entity(chat_id)
                chat_display = chat_info.title if hasattr(chat_info, 'title') else f"Chat ID: {chat_id}"
            except:
                chat_display = f"Chat ID: {chat_id}"

            blchat_msg = f"""{get_emoji('merah')} CHAT GLOBALLY LOCKED

{get_emoji('aktif')} Chat: {chat_display}
{get_emoji('telegram')} Chat ID: {chat_id}
{get_emoji('petir')} Status: Ditambah ke gcast blacklist
{get_emoji('proses')} Total Blacklisted Chats: {len(Config.GCAST_BLACKLIST)}

{get_emoji('kuning')} Effects:
• Gcast tidak akan dikirim ke chat ini
• Chat ID tersimpan di config.py dan .env
• Berlaku global untuk semua gcast operations

{get_emoji('centang')} Untuk remove: hapus manual dari config

Vzoel Fox's Chat Blacklist System"""
        else:
            blchat_msg = f"{get_emoji('kuning')} Chat sudah ada di gcast blacklist sebelumnya"

        await safe_edit_premium(event, blchat_msg)
        vzoel_client.increment_command_count()
