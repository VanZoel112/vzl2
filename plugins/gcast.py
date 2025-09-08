import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced Gcast Plugin for VzoelFox Userbot - Premium Edition
Fitur: Global cast dengan blacklist support dan premium emoji
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Gcast System
"""

from telethon import events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError
from telethon.tl.types import Channel, Chat
import asyncio
import time
import re

# Plugin info
__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    from config import Config
    Config.load_blacklist()
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Gcast & Blacklist Plugin loaded - Broadcast system ready")

@events.register(events.NewMessage(pattern=r'\.addbl(?: (.+))?'))
async def add_blacklist_handler(event):
    """Add chat to gcast blacklist"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        
        args = event.pattern_match.group(1)
        chat_id = None
        chat_title = "Unknown"
        
        # Check if replying to a forwarded message
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.forward:
                if reply_msg.forward.chat:
                    chat_id = reply_msg.forward.chat.id
                    try:
                        chat = await event.client.get_entity(chat_id)
                        chat_title = chat.title if hasattr(chat, 'title') else str(chat_id)
                    except:
                        chat_title = str(chat_id)
        
        # Check if ID provided as argument
        elif args:
            try:
                chat_id = int(args.strip())
                try:
                    chat = await event.client.get_entity(chat_id)
                    chat_title = chat.title if hasattr(chat, 'title') else str(chat_id)
                except:
                    chat_title = str(chat_id)
            except ValueError:
                error_msg = f"{get_emoji('merah')} Invalid chat ID format"
                await safe_edit_premium(event, error_msg)
                return
        
        # Use current chat if nothing specified
        else:
            chat_id = event.chat_id
            try:
                chat = await event.client.get_entity(chat_id)
                chat_title = chat.title if hasattr(chat, 'title') else str(chat_id)
            except:
                chat_title = str(chat_id)
        
        if chat_id:
            # Add to blacklist
            if Config.add_to_blacklist(chat_id):
                success_msg = f"{get_emoji('centang')} {signature} **VZOEL Blacklist Added**
"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)** + \
                    f"Chat: `{chat_title}`
" + \
                    f"ID: `{chat_id}`
" + \
                    f"Total Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
                
                await safe_edit_premium(event, success_msg)
            else:
                already_msg = f"{get_emoji('kuning')} {signature} **VZOEL Already Blacklisted**
"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)** + \
                    f"Chat: `{chat_title}`
" + \
                    f"ID: `{chat_id}`"
                
                await safe_edit_premium(event, already_msg)
        else:
            error_msg = f"{get_emoji('merah')} Could not determine chat ID"
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.rembl(?: (.+))?'))
async def remove_blacklist_handler(event):
    """Remove chat from gcast blacklist"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        
        args = event.pattern_match.group(1)
        chat_id = None
        
        if args:
            try:
                chat_id = int(args.strip())
            except ValueError:
                error_msg = f"{get_emoji('merah')} Invalid chat ID format"
                await safe_edit_premium(event, error_msg)
                return
        else:
            chat_id = event.chat_id
        
        if Config.remove_from_blacklist(chat_id):
            success_msg = f"{get_emoji('centang')} {signature} **VZOEL Blacklist Removed**
"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)** + \
                f"ID: `{chat_id}`
" + \
                f"Total Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
            await safe_edit_premium(event, success_msg)
        else:
            not_found_msg = f"{get_emoji('kuning')} ID `{chat_id}` not in blacklist"
            await safe_edit_premium(event, not_found_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.listbl'))
async def list_blacklist_handler(event):
    """List all blacklisted chats"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        
        if not Config.GCAST_BLACKLIST:
            empty_msg = f"{get_emoji('kuning')} Blacklist is empty"
            await safe_edit_premium(event, empty_msg)
            return
        
        blacklist_text = f"{signature} **VZOEL VzoelFox Gcast Blacklist ({len(Config.GCAST_BLACKLIST)})**

"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)**
        
        for i, chat_id in enumerate(Config.GCAST_BLACKLIST, 1):
            try:
                chat = await event.client.get_entity(chat_id)
                chat_title = chat.title if hasattr(chat, 'title') else f"Private {chat_id}"
                blacklist_text += f"`{i}.` **{chat_title}**
   ID: `{chat_id}`

"
            except:
                blacklist_text += f"`{i}.` {signature} **VZOEL Unknown Chat**
   ID: `{chat_id}`

"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)**
        
        blacklist_text += f"{signature} **VZOEL By VzoelFox Assistant**"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)**
        
        await safe_edit_premium(event, blacklist_text)
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.gcast(?: (.+))?'))
async def gcast_handler(event):
    """Advanced gcast with animated feedback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        
        # Get message content
        message_text = event.pattern_match.group(1)
        reply_message = None
        
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            if not message_text and reply_message:
                # Use replied message
                if reply_message.text:
                    message_text = reply_message.text
                elif reply_message.media:
                    # Keep media message as is
                    pass
                else:
                    error_msg = f"{get_emoji('merah')} Cannot broadcast empty message"
                    await safe_edit_premium(event, error_msg)
                    return
        
        if not message_text and not reply_message:
            error_msg = f"{get_emoji('merah')} Please provide message text or reply to a message"
            await safe_edit_premium(event, error_msg)
            return
        
        # Start gcast process with animation
        start_time = time.time()
        
        # Animation phase 1: Process setup
        process_msg = f"{get_emoji('loading')} {get_emoji('telegram')} Mempersiapkan global cast..."
        
        await safe_edit_premium(event, process_msg)
        await asyncio.sleep(1)
        
        # Get all dialogs (groups and channels)
        dialogs = []
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                if not Config.is_blacklisted(dialog.id):
                    dialogs.append(dialog)
        
        total_chats = len(dialogs)
        blacklisted_count = len(Config.GCAST_BLACKLIST)
        
        if total_chats == 0:
            no_chats_msg = f"{get_emoji('kuning')} No groups/channels available for broadcast"
            await safe_edit_premium(event, no_chats_msg)
            return
        
        # Animation phase 2: Starting broadcast
        start_msg = f"{get_emoji('proses')} {signature} **VZOEL Broadcasting Started**
"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)** + \
            f"Target Chats: `{total_chats}`
" + \
            f"Blacklisted: `{blacklisted_count}`
" + \
            f"Status: Processing..."
        await safe_edit_premium(event, start_msg)
        await asyncio.sleep(1)
        
        # Broadcast loop
        successful_sends = 0
        failed_sends = 0
        
        for i, dialog in enumerate(dialogs, 1):
            try:
                # Update progress every 5 chats or on last chat
                if i % 5 == 0 or i == total_chats:
                    progress_msg = f"{get_emoji('aktif')} {signature} **VZOEL Broadcasting in Progress**
"
{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)** + \
                        f"Progress: `{i}/{total_chats}`
" + \
                        f"Success: `{successful_sends}`
" + \
                        f"Failed: `{failed_sends}`
" + \
                        f"Current: `{dialog.title or 'Unknown'}`"
                    await safe_edit_premium(event, progress_msg)
                
                # Send message
                if reply_message and reply_message.media:
                    # Forward media message
                    await event.client.send_message(
                        dialog.id, 
                        reply_message.text or "", 
                        file=reply_message.media
                    )
                else:
                    # Send text message (supports unlimited premium emojis)
                    await event.client.send_message(dialog.id, message_text)
                
                successful_sends += 1
                
            except FloodWaitError as e:
                # Handle flood wait
                await asyncio.sleep(e.seconds)
                try:
                    if reply_message and reply_message.media:
                        await event.client.send_message(
                            dialog.id, 
                            reply_message.text or "", 
                            file=reply_message.media
                        )
                    else:
                        await event.client.send_message(dialog.id, message_text)
                    successful_sends += 1
                except:
                    failed_sends += 1
                    
            except (ChatWriteForbiddenError, UserBannedInChannelError):
                failed_sends += 1
                
            except Exception:
                failed_sends += 1
            # Small delay between sends
            await asyncio.sleep(0.1)
        
        # Calculate final stats
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (successful_sends / total_chats * 100) if total_chats > 0 else 0
        
        # Animation phase 3: Process completed
        complete_msg = f"""{get_emoji('utama')} **{get_emoji('centang')} Berhasil diselesaikan!**

{get_emoji('centang')} **By {get_emoji('adder1')} VzoelFox's Assistant**
{get_emoji('telegram')} **Groups Sent:** {successful_sends}
{get_emoji('aktif')} **Duration:** {duration:.1f} seconds
{get_emoji('proses')} **Success Rate:** {success_rate:.1f}%
{get_emoji('petir')} **Ready for next command...**"""
        await safe_edit_premium(event, complete_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.ginfo'))
async def gcast_info_handler(event):
    """Show gcast information with animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config

        
        # Animation phase 1: Loading info
        loading_msg = f"{get_emoji('loading')} Loading gcast information..."
        
        await safe_edit_premium(event, loading_msg)
        await asyncio.sleep(1)
        
        # Count available chats
        total_groups = 0
        total_channels = 0
        
        async for dialog in event.client.iter_dialogs():
            if dialog.is_group and not Config.is_blacklisted(dialog.id):
                total_groups += 1
            elif dialog.is_channel and not Config.is_blacklisted(dialog.id):
                total_channels += 1
        
        total_available = total_groups + total_channels
        blacklisted_count = len(Config.GCAST_BLACKLIST)
        
        # Animation phase 2: Show complete info
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        info_text = f"""**{signature} Gcast Information**

**Available Targets:**
{get_emoji('centang')} Groups: `{total_groups}`
{get_emoji('telegram')} Channels: `{total_channels}`
{get_emoji('utama')} Total Available: `{total_available}`

**Blacklist Status:**
{get_emoji('merah')} Blacklisted: `{blacklisted_count}`
{get_emoji('aktif')} Will Broadcast To: `{total_available}`

**Commands:**
{get_emoji('proses')} `.gcast <text>` - Broadcast text
{get_emoji('kuning')} `.gcast` (reply) - Broadcast reply
{get_emoji('adder1')} `.addbl <id>` - Add to blacklist
{get_emoji('adder2')} `.listbl` - Show blacklist

**By VzoelFox Assistant**"""
        
        await safe_edit_premium(event, info_text)
        if vzoel_client:
            vzoel_client.increment_command_count()
