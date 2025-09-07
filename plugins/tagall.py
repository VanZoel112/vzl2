"""
VzoelFox's Assistant Tagall Plugin
Advanced member tagging with animated feedback and loop control
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import FloodWaitError, ChatAdminRequiredError
import asyncio
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variables for tagall state
tagall_tasks = {}
tagall_active = {}

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Tagall Plugin loaded - Member tagging ready")

@events.register(events.NewMessage(pattern=r'\.tagall( (.+))?'))
async def tagall_handler(event):
    """Tag all members in group with animated feedback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
                
        # Check if we're in a group
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Tagall hanya bisa digunakan di grup"
            await safe_edit_premium(event, error_msg)
            return
        
        chat_id = event.chat_id
        
        # Stop any existing tagall in this chat
        if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
            tagall_tasks[chat_id].cancel()
            tagall_active[chat_id] = False
        
        # Get message content
        message_text = None
        if event.reply_to_msg_id:
            # Reply mode - get replied message
            replied_msg = await event.get_reply_message()
            message_text = replied_msg.message or "📢 Tagged by VzoelFox"
        else:
            # Text mode - get text after .tagall
            match = event.pattern_match
            if match and match.group(2):
                message_text = match.group(2)
            else:
                message_text = "📢 Tagged by VzoelFox"
        
        # Start tagall process
        tagall_active[chat_id] = True
        
        # Initial process message
        process_msg = f"{get_emoji('loading')} Memulai proses tagall..."
        msg = await safe_edit_premium(event, process_msg)
        
        # Get chat info
        try:
            chat = await event.get_chat()
            chat_title = chat.title
            
            # Get all members
            await asyncio.sleep(1)
            await safe_edit_premium(msg, f"{get_emoji('proses')} Mengambil daftar member dari {chat_title}...")
            
            participants = []
            async for user in event.client.iter_participants(chat_id):
                if not user.bot and not user.deleted:
                    participants.append(user)
            
            if not participants:
                no_members_msg = f"{get_emoji('kuning')} Tidak ada member yang bisa di-tag"
                await safe_edit_premium(msg, no_members_msg)
                return
            
            await asyncio.sleep(1)
            await safe_edit_premium(msg, f"{get_emoji('centang')} Ditemukan {len(participants)} member. Memulai tagall...")
            
            # Start tagall task
            tagall_tasks[chat_id] = asyncio.create_task(
                perform_tagall(event, participants, message_text, chat_title)
            )
            
            # Wait for task completion
            try:
                await tagall_tasks[chat_id]
            except asyncio.CancelledError:
                cancel_msg = f"{get_emoji('kuning')} Tagall dihentikan oleh pengguna"
                await safe_edit_premium(msg, cancel_msg)
            
        except ChatAdminRequiredError:
            error_msg = f"{get_emoji('merah')} Bot membutuhkan akses admin untuk melihat member"
            await safe_edit_premium(msg, error_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Error saat tagall: {str(e)}"
            await safe_edit_premium(msg, error_msg)
        finally:
            tagall_active[chat_id] = False
        
        vzoel_client.increment_command_count()

async def perform_tagall(event, participants, message_text, chat_title):
    """Perform the actual tagall with animated feedback"""
        
    chat_id = event.chat_id
    user_count = 0
    
    # Animation phases
    animation_phases = [
        "Mengirim tagall ke member...",
        "Memproses daftar member...",
        "Mengirim mention ke grup...",
        "Melanjutkan proses tagall...",
        "Tagall sedang berjalan..."
    ]
    
    for participant in participants:
        if not tagall_active.get(chat_id, False):
            break
        
        try:
            # Get user info
            username = f"@{participant.username}" if participant.username else "User"
            full_name = f"{participant.first_name or ''} {participant.last_name or ''}".strip()
            if not full_name:
                full_name = "Unknown User"
            
            user_count += 1
            
            # Random premium emoji for animation
            premium_emojis = ['utama', 'centang', 'petir', 'kuning', 'biru', 'merah', 'proses', 'aktif']
            random_emoji = get_emoji(random.choice(premium_emojis, premium=True))
            
            # Create animated status message
            animation_text = f"""**{get_emoji('telegram', premium=True)} VZOEL TAGALL PROCESS**

{get_emoji('aktif', premium=True)} **Username:** {username}
{get_emoji('utama', premium=True)} **Nama:** {full_name}
{random_emoji} **Status:** {random.choice(animation_phases)}
{get_emoji('centang', premium=True)} **Tagall by:** Vzoel Fox's Assistant
{get_emoji('proses', premium=True)} **Progress:** {user_count}/{len(participants)}

**Pesan:** {message_text}

{get_emoji('petir', premium=True)} **Grup:** {chat_title}"""
            
            # Send tag message
            tag_message = f"[{full_name}](tg://user?id={participant.id}) {message_text}"
            
            # Send the actual tag
            await event.client.send_message(chat_id, tag_message)
            
            # Show animation in original message
            await safe_edit_premium(event, animation_text)
            
            # Delay to avoid flood
            await asyncio.sleep(2)
            
        except FloodWaitError as e:
            # Handle flood wait
            wait_msg = f"{get_emoji('kuning')} Flood wait {e.seconds} detik, menunggu..."
            await safe_edit_premium(event, wait_msg)
            await asyncio.sleep(e.seconds)
        except Exception as e:
            # Skip problematic users
            continue
    
    # Final completion message
    if tagall_active.get(chat_id, False):
        completion_msg = f"""**{get_emoji('centang', premium=True)} TAGALL SELESAI**

{get_emoji('utama', premium=True)} **Total Member Tagged:** {user_count}
{get_emoji('telegram', premium=True)} **Grup:** {chat_title}
{get_emoji('aktif', premium=True)} **Pesan:** {message_text}
{get_emoji('petir', premium=True)} **Status:** Completed Successfully

**By VzoelFox Assistant**"""
        
        await safe_edit_premium(event, completion_msg)

@events.register(events.NewMessage(pattern=r'\.stop'))
async def stop_tagall_handler(event):
    """Stop ongoing tagall process"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
                
        chat_id = event.chat_id
        
        if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
            # Cancel the tagall task
            tagall_tasks[chat_id].cancel()
            tagall_active[chat_id] = False
            
            stop_msg = f"{get_emoji('centang')} **Tagall Dihentikan**\\nProses tagall telah diberhentikan oleh pengguna\\nStatus: Cancelled"
            await safe_edit_premium(event, stop_msg)
        else:
            no_tagall_msg = f"{get_emoji('kuning')} Tidak ada proses tagall yang sedang berjalan"
            await safe_edit_premium(event, no_tagall_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.taginfo'))
async def tagall_info_handler(event):
    """Show information about tagall system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
                
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        tagall_info = f"""**{signature} Tagall System Information**

{get_emoji('utama', premium=True)} **Apa itu Tagall?**
Tagall adalah sistem untuk mention seluruh member grup dengan animasi real-time dan kontrol penuh.

{get_emoji('centang', premium=True)} **Cara Penggunaan:**
• `.tagall <pesan>` - Tag semua member dengan pesan
• `.tagall` (reply) - Tag semua member dengan pesan yang direply
• `.stop` - Hentikan proses tagall yang sedang berjalan

{get_emoji('aktif', premium=True)} **Fitur Tagall:**
• Real-time animated feedback
• Progress tracking per member
• Username dan nama lengkap display
• Random premium emoji animation
• Flood protection dengan auto-delay
• Cancellation support dengan .stop

{get_emoji('telegram', premium=True)} **Animasi Display:**
1. Username member di grup
2. Nama lengkap member  
3. Random premium emoji
4. "Tagall by Vzoel Fox's Assistant"
5. Isi pesan yang ditulis/direply

{get_emoji('proses', premium=True)} **Safety Features:**
• Skip bot accounts automatically
• Handle deleted accounts
• Flood wait protection
• Admin permission checking
• Error handling untuk user bermasalah

{get_emoji('petir', premium=True)} **Performance:**
• 2 detik delay per member (flood protection)
• Async processing untuk efisiensi
• Real-time progress display
• Automatic cleanup setelah selesai

**By VzoelFox Assistant**"""
        
        await safe_edit_premium(event, tagall_info)
        vzoel_client.increment_command_count()
