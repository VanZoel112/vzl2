"""
Enhanced Tagall Plugin for Vzoel Fox's Userbot - Premium Edition
Fitur: Advanced mention system dengan premium controls dan batch editing
Founder Userbot: Vzoel Fox's Ltpn
Version: 4.0.0 - Smart Batch Tagall System
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
__version__ = "4.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Global variables for tagall state
tagall_tasks = {}
tagall_active = {}
tagall_messages = {}  # Store tagall messages for editing
tagall_progress = {}  # Track progress per chat

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Tagall Plugin loaded - Member tagging ready")

@events.register(events.NewMessage(pattern=r'\.tagall( (.+))?'))
async def tagall_handler(event):
    """Tag all members in group with animated feedback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
                
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
        else:
            # Text mode - get text after .tagall
            match = event.pattern_match
            if match and match.group(2):
                message_text = match.group(2)
            else:
                message_text = ""
        
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
            # Initialize tagall tracking
            tagall_progress[chat_id] = {'total': len(participants), 'processed': 0}

            # Start tagall task
            tagall_tasks[chat_id] = asyncio.create_task(
                perform_batch_tagall(event, participants, message_text, chat_title)
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
            # Clean up tracking data
            if chat_id in tagall_progress:
                del tagall_progress[chat_id]
            if chat_id in tagall_messages:
                del tagall_messages[chat_id]
        
        vzoel_client.increment_command_count()

async def perform_batch_tagall(event, participants, message_text, chat_title):
    """Perform tagall with smart batch editing system - 5 users per message edit"""

    chat_id = event.chat_id
    total_users = len(participants)
    processed_count = 0
    batch_size = 5

    # Premium emoji mapping for visual appeal
    emoji_mapping = {
        0: 'utama',    # 🤩 - Main emoji
        1: 'centang',  # 👍 - Success
        2: 'petir',    # ⛈ - Power
        3: 'aktif',    # 🎚 - Active
        4: 'adder1'    # 😈 - Special
    }

    # Status emojis for different phases
    status_emojis = ['loading', 'proses', 'kuning', 'biru', 'merah']

    # Create initial tagall message that will be edited with user batches
    initial_msg = f"{get_emoji('loading')} Memulai smart batch tagall..."
    tagall_msg = await event.client.send_message(chat_id, initial_msg)
    tagall_messages[chat_id] = tagall_msg

    # Process users in batches of 5
    for i in range(0, total_users, batch_size):
        if not tagall_active.get(chat_id, False):
            break

        try:
            batch = participants[i:i + batch_size]
            batch_mentions = []
            batch_display = []

            # Process each user in the current batch
            for idx, participant in enumerate(batch):
                if not tagall_active.get(chat_id, False):
                    break

                # Get user info
                username = f"@{participant.username}" if participant.username else "User"
                full_name = f"{participant.first_name or ''} {participant.last_name or ''}".strip()
                if not full_name:
                    full_name = "Unknown User"

                # Create mention link
                mention = f"[{full_name}](tg://user?id={participant.id})"
                batch_mentions.append(mention)

                # Get emoji for this position in batch
                emoji_key = emoji_mapping.get(idx, 'telegram')
                emoji_char = get_emoji(emoji_key)

                # Create display info
                batch_display.append(f"{emoji_char} {full_name}")
                processed_count += 1

            # Create batch message with mentions and message text
            if batch_mentions:
                mention_text = " ".join(batch_mentions)
                if message_text:
                    batch_message = f"{mention_text} {message_text}"
                else:
                    batch_message = mention_text

                # Edit the tagall message with current batch info
                batch_number = (i // batch_size) + 1
                total_batches = (total_users + batch_size - 1) // batch_size
                progress_emoji = get_emoji(random.choice(status_emojis))

                status_display = f"""{get_emoji('petir')} VZL2 SMART BATCH TAGALL

{get_emoji('centang')} Batch {batch_number}/{total_batches} - Target Users:

""" + "\n".join(batch_display) + f"""

{progress_emoji} Progress: {processed_count}/{total_users} users
{get_emoji('aktif')} Pesan: {message_text or 'Default tagall'}
{get_emoji('telegram')} Grup: {chat_title}

By Vzoel Fox's Assistant"""

                # Edit the main tracking message
                await safe_edit_premium(event, status_display)

                # Edit the tagall message with the actual mentions
                await tagall_msg.edit(batch_message)

                # Update progress tracking
                tagall_progress[chat_id]['processed'] = processed_count

                # Delay between batches to avoid flood
                await asyncio.sleep(3)

        except FloodWaitError as e:
            # Handle flood wait
            wait_msg = f"{get_emoji('kuning')} Flood wait {e.seconds} detik, menunggu..."
            await safe_edit_premium(event, wait_msg)
            await asyncio.sleep(e.seconds)
        except Exception as e:
            # Skip problematic batch and continue
            print(f"[Tagall] Error in batch {i//batch_size + 1}: {e}")
            continue

    # Final completion message with success summary
    if tagall_active.get(chat_id, False):
        success_emojis = [get_emoji(key) for key in ['centang', 'utama', 'petir', 'aktif', 'adder1']]
        emoji_line = " ".join(success_emojis)

        completion_msg = f"""{emoji_line} TAGALL COMPLETED

{get_emoji('centang')} Total Tagged: {processed_count} users
{get_emoji('utama')} Batches Processed: {(processed_count + batch_size - 1) // batch_size}
{get_emoji('aktif')} Message: {message_text or 'Default tagall'}
{get_emoji('petir')} Group: {chat_title}
{get_emoji('adder1')} Method: Smart Batch Editing

{get_emoji('proses')} Status: Successfully Completed
{get_emoji('telegram')} System: VZL2 Premium Tagall v4.0

By Vzoel Fox's Assistant"""

        await safe_edit_premium(event, completion_msg)

        # Clean up tracking data
        if chat_id in tagall_progress:
            del tagall_progress[chat_id]
        if chat_id in tagall_messages:
            del tagall_messages[chat_id]

@events.register(events.NewMessage(pattern=r'\.stop'))
async def stop_tagall_handler(event):
    """Stop ongoing tagall process"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
                
        chat_id = event.chat_id
        
        if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
            # Cancel the tagall task
            tagall_tasks[chat_id].cancel()
            tagall_active[chat_id] = False

            # Clean up tracking data
            if chat_id in tagall_progress:
                del tagall_progress[chat_id]
            if chat_id in tagall_messages:
                del tagall_messages[chat_id]

            stop_msg = f"{get_emoji('centang')} Smart Batch Tagall Stopped\n\n{get_emoji('kuning')} Cleanup completed\n{get_emoji('telegram')} VZL2 Tagall v4.0"
            await safe_edit_premium(event, stop_msg)
        else:
            no_tagall_msg = f"{get_emoji('kuning')} Tidak ada proses tagall yang sedang berjalan"
            await safe_edit_premium(event, no_tagall_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.taginfo'))
async def tagall_info_handler(event):
    """Show information about tagall system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
                
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        tagall_info = f"""{signature} Smart Batch Tagall System v4.0

{get_emoji('utama')} Apa itu Smart Batch Tagall?
Sistem mention member grup dengan teknologi batch editing - tidak spam, lebih efisien, dan elegan dengan premium emoji mapping.

{get_emoji('centang')} Cara Penggunaan:
• .tagall <pesan> - Tag semua member dengan pesan
• .tagall (reply) - Tag semua member dengan pesan yang direply
• .stop - Hentikan proses tagall yang sedang berjalan

{get_emoji('aktif')} Fitur Smart Batch v4.0:
• Batch Editing System - 5 user per edit (tidak spam)
• Premium Emoji Mapping - Visual appeal dengan VZL2 emojis
• Real-time Progress - Track progress per batch
• Single Message Editing - Satu pesan di-edit untuk semua mentions
• Smart Status Display - Animated feedback dengan premium emojis
• Flood Protection - 3 detik delay per batch

{get_emoji('petir')} Keunggulan v4.0:
• Anti-Spam: Tidak menghasilkan banyak pesan terpisah
• Batch Processing: 5 user sekaligus per edit
• Premium Visual: Setiap user mendapat emoji unik
• Progress Tracking: Real-time batch dan user count
• Smart Cleanup: Auto-cleanup tracking data
• Error Handling: Skip batch bermasalah, lanjutkan proses

{get_emoji('proses')} Safety & Performance:
• Skip bot accounts otomatis
• Handle deleted accounts dengan aman
• Flood wait protection dengan delay dinamis
• Admin permission checking
• Batch error recovery system
• Memory efficient dengan auto cleanup

{get_emoji('adder1')} Technical Specs:
• Batch size: 5 users per message edit
• Delay: 3 detik per batch (optimal anti-flood)
• Emoji mapping: 5 premium emojis per batch
• Progress tracking: Real-time batch/user counting
• Memory management: Auto cleanup setelah selesai

By Vzoel Fox's Assistant - Premium Tagall Technology"""
        
        await safe_edit_premium(event, tagall_info)
        vzoel_client.increment_command_count()
