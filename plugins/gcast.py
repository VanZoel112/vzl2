"""
VzoelFox's Assistant Gcast & Blacklist Plugin
Advanced broadcast system with blacklist management
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError
from telethon.tl.types import Channel, Chat
import asyncio
import time
import re

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    from config import Config
    Config.load_blacklist()
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"{signature} Gcast & Blacklist Plugin loaded - Broadcast system ready")

@events.register(events.NewMessage(pattern=r'\.addbl(?: (.+))?'))
async def add_blacklist_handler(event):
    """Add chat to gcast blacklist"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        from emoji_handler import vzoel_emoji
        
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
                error_msg = vzoel_emoji.format_emoji_response(
                    ['merah'], "Invalid chat ID format"
                )
                await event.edit(error_msg)
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
                success_msg = vzoel_emoji.format_emoji_response(
                    ['centang'], 
                    f"**Blacklist Added**\n"
                    f"Chat: `{chat_title}`\n"
                    f"ID: `{chat_id}`\n"
                    f"Total Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
                )
                await event.edit(success_msg)
            else:
                already_msg = vzoel_emoji.format_emoji_response(
                    ['kuning'], 
                    f"**Already Blacklisted**\n"
                    f"Chat: `{chat_title}`\n"
                    f"ID: `{chat_id}`"
                )
                await event.edit(already_msg)
        else:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Could not determine chat ID"
            )
            await event.edit(error_msg)
        
        vzoel_client.increment_command_count()

add_blacklist_handler.handler = add_blacklist_handler.handler
add_blacklist_handler.command = ".addbl"

@events.register(events.NewMessage(pattern=r'\.rembl(?: (.+))?'))
async def remove_blacklist_handler(event):
    """Remove chat from gcast blacklist"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        from emoji_handler import vzoel_emoji
        
        args = event.pattern_match.group(1)
        chat_id = None
        
        if args:
            try:
                chat_id = int(args.strip())
            except ValueError:
                error_msg = vzoel_emoji.format_emoji_response(
                    ['merah'], "Invalid chat ID format"
                )
                await event.edit(error_msg)
                return
        else:
            chat_id = event.chat_id
        
        if Config.remove_from_blacklist(chat_id):
            success_msg = vzoel_emoji.format_emoji_response(
                ['centang'], 
                f"**Blacklist Removed**\n"
                f"ID: `{chat_id}`\n"
                f"Total Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
            )
            await event.edit(success_msg)
        else:
            not_found_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], f"ID `{chat_id}` not in blacklist"
            )
            await event.edit(not_found_msg)
        
        vzoel_client.increment_command_count()

remove_blacklist_handler.handler = remove_blacklist_handler.handler
remove_blacklist_handler.command = ".rembl"

@events.register(events.NewMessage(pattern=r'\.listbl'))
async def list_blacklist_handler(event):
    """List all blacklisted chats"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        from emoji_handler import vzoel_emoji
        
        if not Config.GCAST_BLACKLIST:
            empty_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "Blacklist is empty"
            )
            await event.edit(empty_msg)
            return
        
        blacklist_text = f"**VzoelFox Gcast Blacklist ({len(Config.GCAST_BLACKLIST)})**\n\n"
        
        for i, chat_id in enumerate(Config.GCAST_BLACKLIST, 1):
            try:
                chat = await event.client.get_entity(chat_id)
                chat_title = chat.title if hasattr(chat, 'title') else f"Private {chat_id}"
                blacklist_text += f"`{i}.` **{chat_title}**\n   ID: `{chat_id}`\n\n"
            except:
                blacklist_text += f"`{i}.` **Unknown Chat**\n   ID: `{chat_id}`\n\n"
        
        blacklist_text += f"**By VzoelFox Assistant**"
        await event.edit(blacklist_text)
        vzoel_client.increment_command_count()

list_blacklist_handler.handler = list_blacklist_handler.handler
list_blacklist_handler.command = ".listbl"

@events.register(events.NewMessage(pattern=r'\.gcast(?: (.+))?'))
async def gcast_handler(event):
    """Advanced gcast with animated feedback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        from emoji_handler import vzoel_emoji
        
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
                    error_msg = vzoel_emoji.format_emoji_response(
                        ['merah'], "Cannot broadcast empty message"
                    )
                    await event.edit(error_msg)
                    return
        
        if not message_text and not reply_message:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Please provide message text or reply to a message"
            )
            await event.edit(error_msg)
            return
        
        # Start gcast process with animation
        start_time = time.time()
        
        # Animation phase 1: Process setup
        process_msg = vzoel_emoji.format_emoji_response(
            ['loading'], "Initializing broadcast process..."
        )
        msg = await event.edit(process_msg)
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
            no_chats_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "No groups/channels available for broadcast"
            )
            await msg.edit(no_chats_msg)
            return
        
        # Animation phase 2: Starting broadcast
        start_msg = vzoel_emoji.format_emoji_response(
            ['proses'], 
            f"**Broadcasting Started**\n"
            f"Target Chats: `{total_chats}`\n"
            f"Blacklisted: `{blacklisted_count}`\n"
            f"Status: Processing..."
        )
        await msg.edit(start_msg)
        await asyncio.sleep(1)
        
        # Broadcast loop
        successful_sends = 0
        failed_sends = 0
        
        for i, dialog in enumerate(dialogs, 1):
            try:
                # Update progress every 5 chats or on last chat
                if i % 5 == 0 or i == total_chats:
                    progress_msg = vzoel_emoji.format_emoji_response(
                        ['aktif'],
                        f"**Broadcasting in Progress**\n"
                        f"Progress: `{i}/{total_chats}`\n"
                        f"Success: `{successful_sends}`\n"
                        f"Failed: `{failed_sends}`\n"
                        f"Current: `{dialog.title or 'Unknown'}`"
                    )
                    await msg.edit(progress_msg)
                
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
        complete_msg = vzoel_emoji.format_emoji_response(
            ['utama'], 
            f"**1. Process Completed**\n"
            f"**2. By VzoelFox Assistant**\n"
            f"**3. Groups Sent: {successful_sends}**\n"
            f"**4. Duration: {duration:.1f} seconds**\n"
            f"**5. Success Rate: {success_rate:.1f}%**\n"
            f"**6. Ready for next command...**"
        )
        await msg.edit(complete_msg)
        
        vzoel_client.increment_command_count()

gcast_handler.handler = gcast_handler.handler  
gcast_handler.command = ".gcast"

@events.register(events.NewMessage(pattern=r'\.ginfo'))
async def gcast_info_handler(event):
    """Show gcast information with animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config
        from emoji_handler import vzoel_emoji
        
        # Animation phase 1: Loading info
        loading_msg = vzoel_emoji.format_emoji_response(
            ['loading'], "Loading gcast information..."
        )
        msg = await event.edit(loading_msg)
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
        signature = vzoel_emoji.get_vzoel_signature()
        
        info_text = f"""**{signature} Gcast Information**

**Available Targets:**
{vzoel_emoji.get_emoji('centang')} Groups: `{total_groups}`
{vzoel_emoji.get_emoji('telegram')} Channels: `{total_channels}`
{vzoel_emoji.get_emoji('utama')} Total Available: `{total_available}`

**Blacklist Status:**
{vzoel_emoji.get_emoji('merah')} Blacklisted: `{blacklisted_count}`
{vzoel_emoji.get_emoji('aktif')} Will Broadcast To: `{total_available}`

**Commands:**
{vzoel_emoji.get_emoji('proses')} `.gcast <text>` - Broadcast text
{vzoel_emoji.get_emoji('kuning')} `.gcast` (reply) - Broadcast reply
{vzoel_emoji.get_emoji('adder1')} `.addbl <id>` - Add to blacklist
{vzoel_emoji.get_emoji('adder2')} `.listbl` - Show blacklist

**By VzoelFox Assistant**"""
        
        await msg.edit(info_text)
        vzoel_client.increment_command_count()

gcast_info_handler.handler = gcast_info_handler.handler
gcast_info_handler.command = ".ginfo"