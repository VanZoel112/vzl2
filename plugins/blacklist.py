import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced Blacklist Plugin for VzoelFox Userbot - Premium Edition
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

# Global variables
blacklist_words = {}  # {chat_id: [words]}
locked_users = {}     # {chat_id: [user_ids]}
blacklist_active = {}  # {chat_id: True/False}

# File for persistent storage
BLACKLIST_FILE = "blacklist_data.json"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    global blacklist_words, locked_users, blacklist_active
    
    # Load existing blacklist data
    load_blacklist_data()
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Blacklist Plugin loaded - Word filtering ready")

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
        from client import vzoel_client
        
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
            help_msg = f"""{get_emoji('kuning')} **Blacklist Usage:**
• `.bl <kata>` - Tambah kata ke blacklist
• `.bl` (reply) - Tambah pesan yang direply
• `.wl <kata>` - Hapus dari blacklist
• `.lock @user` - Lock user (hapus semua pesan)
• `.blinfo` - Info blacklist system"""
            msg = await event.edit(help_msg)
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
            success_msg = f"""**{get_emoji('centang')} BLACKLIST UPDATED**

{get_emoji('merah')} **Kata Ditambahkan:** {len(added_words)}
{get_emoji('aktif')} **Words:** {', '.join(added_words)}
{get_emoji('telegram')} **Total Blacklist:** {len(blacklist_words[chat_id])} kata
{get_emoji('petir')} **Status:** Auto-delete aktif

{get_emoji('proses')} **Pesan yang mengandung kata ini akan otomatis dihapus**

**VzoelFox Blacklist System**"""
        else:
            success_msg = f"{get_emoji('kuning')} Semua kata sudah ada di blacklist"
        
        
        msg = await event.edit(success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.wl( (.+))?'))
async def remove_blacklist_handler(event):
    """Remove words from blacklist (whitelist)"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
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
                current_msg = f"""**{get_emoji('telegram')} BLACKLIST CURRENT**

{get_emoji('merah')} **Total:** {len(blacklist_words[chat_id])} kata
{get_emoji('aktif')} **Words:** {blacklist_list[:500]}{'...' if len(blacklist_list) > 500 else ''}

{get_emoji('centang')} **Untuk menghapus:** `.wl <kata>`
{get_emoji('kuning')} **Clear semua:** `.wl clear`

**VzoelFox Blacklist**"""
            else:
                current_msg = f"{get_emoji('kuning')} Blacklist kosong di chat ini"
                
            msg = await event.edit(current_msg)
            return
        
        if chat_id not in blacklist_words:
            blacklist_words[chat_id] = []
        
        # Handle clear command
        if whitelist_text.lower() == 'clear':
            cleared_count = len(blacklist_words[chat_id])
            blacklist_words[chat_id] = []
            save_blacklist_data()
            clear_msg = f"""**{get_emoji('centang')} BLACKLIST CLEARED**

{get_emoji('aktif')} **Dihapus:** {cleared_count} kata
{get_emoji('telegram')} **Status:** Blacklist kosong
{get_emoji('proses')} **Auto-delete:** Non-aktif

**VzoelFox Blacklist System**"""
            msg = await event.edit(clear_msg)
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
            success_msg = f"""**{get_emoji('centang')} WHITELIST UPDATED**

{get_emoji('aktif')} **Kata Dihapus:** {len(removed_words)}
{get_emoji('telegram')} **Words:** {', '.join(removed_words)}
{get_emoji('proses')} **Sisa Blacklist:** {len(blacklist_words[chat_id])} kata

{get_emoji('centang')} **Kata ini tidak akan dihapus lagi**

**VzoelFox Whitelist System**"""
        else:
            success_msg = f"{get_emoji('kuning')} Kata tidak ditemukan di blacklist"
        
        
        msg = await event.edit(success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.lock( (.+))?'))
async def lock_user_handler(event):
    """Lock user to delete all their messages"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
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
                    msg = await event.edit(error_msg)
                    return
        
        if not target_user:
help_msg = f"{get_emoji('kuning')} {signature} **VZOEL Lock Usage:**\n•  - Lock user by username\n•  (reply) - Lock user dari reply\n•  - Unlock user\n•  - List locked users"
• `.unlock @username` - Unlock user
• `.locked` - List locked users
"

{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)**
            msg = await event.edit(help_msg)
            return
        
        # Initialize chat locked users if not exists
        if chat_id not in locked_users:
            locked_users[chat_id] = []
        
        # Add user to locked list
        if target_user not in locked_users[chat_id]:
            locked_users[chat_id].append(target_user)
            save_blacklist_data()
            # Get user info
            try:
                user_info = await event.client.get_entity(target_user)
                user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
            except:
                user_display = f"User ID: {target_user}"
            lock_msg = f"""**{get_emoji('merah')} USER LOCKED**

{get_emoji('aktif')} **User:** {user_display}
{get_emoji('telegram')} **Status:** Semua pesan akan dihapus
{get_emoji('petir')} **Total Locked:** {len(locked_users[chat_id])} user
{get_emoji('proses')} **Auto-delete:** Aktif untuk user ini

{get_emoji('centang')} **Perintah unlock:** `.unlock {user_display}`

**VzoelFox Lock System**"""
            msg = await event.edit(lock_msg)
        else:
            already_msg = f"{get_emoji('kuning')} User sudah di-lock sebelumnya"
            msg = await event.edit(already_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.unlock( (.+))?'))
async def unlock_user_handler(event):
    """Unlock user to stop deleting their messages"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
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
                    msg = await event.edit(error_msg)
                    return
        
        if not target_user:
            # Show locked users
            if chat_id in locked_users and locked_users[chat_id]:
                locked_list = []
                for user_id in locked_users[chat_id][:10]:  # Max 10 users
                    try:
                        user_info = await event.client.get_entity(user_id)
                        user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
                        locked_list.append(user_display)
                    except:
                        locked_list.append(f"ID: {user_id}")
                
                locked_msg = f"""**{get_emoji('telegram')} LOCKED USERS**

{get_emoji('merah')} **Total:** {len(locked_users[chat_id])} user
{get_emoji('aktif')} **Users:** {', '.join(locked_list)}

{get_emoji('centang')} **Untuk unlock:** `.unlock @username`
{get_emoji('kuning')} **Clear semua:** `.unlock clear`

**VzoelFox Lock System**"""
            else:
                locked_msg = f"{get_emoji('kuning')} Tidak ada user yang di-lock"
                msg = await event.edit(locked_msg)
            return
        
        if chat_id not in locked_users:
            locked_users[chat_id] = []
        
        # Remove user from locked list
        if target_user in locked_users[chat_id]:
            locked_users[chat_id].remove(target_user)
            save_blacklist_data()
            try:
                user_info = await event.client.get_entity(target_user)
                user_display = f"@{user_info.username}" if user_info.username else f"{user_info.first_name}"
            except:
                user_display = f"User ID: {target_user}"
            unlock_msg = f"""**{get_emoji('centang')} USER UNLOCKED**

{get_emoji('aktif')} **User:** {user_display}
{get_emoji('telegram')} **Status:** Pesan tidak akan dihapus lagi
{get_emoji('proses')} **Sisa Locked:** {len(locked_users[chat_id])} user

**VzoelFox Unlock System**"""
            msg = await event.edit(unlock_msg)
        else:
            not_locked_msg = f"{get_emoji('kuning')} User tidak dalam daftar lock"
            msg = await event.edit(not_locked_msg)
        
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
        # Check if user is locked
        if chat_id in locked_users and sender_id in locked_users[chat_id]:
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
        from client import vzoel_client

        
        chat_id = event.chat_id
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Get stats
        word_count = len(blacklist_words.get(chat_id, []))
        locked_count = len(locked_users.get(chat_id, []))
        status = "Aktif" if blacklist_active.get(chat_id, True) else "Non-aktif"
        
        blacklist_info = f"""**{signature} Blacklist System Info**

{get_emoji('merah')} **Blacklist Words:** {word_count} kata
{get_emoji('aktif')} **Locked Users:** {locked_count} user  
{get_emoji('telegram')} **Status:** {status}

{get_emoji('centang')} **Commands:**
• `.bl <kata>` - Add blacklist word
• `.wl <kata>` - Remove blacklist word
• `.lock @user` - Lock user (delete all messages)
• `.unlock @user` - Unlock user

{get_emoji('proses')} **Features:**
• Auto-delete pesan dengan kata blacklist
• Lock user untuk hapus semua pesan mereka
• Support text dan reply mode
• Persistent storage (saved to file)

{get_emoji('petir')} **How it works:**
Sistem akan otomatis menghapus pesan yang mengandung kata blacklist atau dari user yang di-lock, bahkan jika hanya sebagian kata yang match.

**VzoelFox Blacklist System**"""
        
        msg = await event.edit(blacklist_info)
        vzoel_client.increment_command_count()
