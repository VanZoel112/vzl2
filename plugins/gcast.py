import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS
import unicodedata
from telethon.tl.types import MessageEntityCustomEmoji

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

def create_unlimited_premium_entities(text):
    """Create premium emoji entities for ALL unicode emojis (unlimited support)"""
    try:
        import re
        entities = []
        
        # Regex pattern untuk mendeteksi semua emoji unicode
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002600-\U000026FF"  # Miscellaneous Symbols
            "\U00002700-\U000027BF"  # Dingbats
            "\U0000FE00-\U0000FE0F"  # Variation Selectors
            "\U0001F170-\U0001F251"  # Enclosed characters
            "]+", 
            re.UNICODE
        )
        
        # Default premium emoji ID untuk semua emoji yang tidak ada di mapping
        DEFAULT_PREMIUM_ID = "6156784006194009426"  # Gunakan ID dari 'utama'
        
        offset = 0
        for match in emoji_pattern.finditer(text):
            emoji_char = match.group()
            start_pos = match.start()
            
            # Cek apakah emoji ini ada di mapping premium kita
            premium_id = None
            for emoji_type, emoji_data in PREMIUM_EMOJIS.items():
                if emoji_data['char'] == emoji_char:
                    premium_id = emoji_data['id']
                    break
            
            # Jika tidak ada di mapping, gunakan default premium ID
            if not premium_id:
                premium_id = DEFAULT_PREMIUM_ID
            
            # Calculate proper UTF-16 offset
            text_before = text[:start_pos]
            utf16_offset = len(text_before.encode('utf-16-le')) // 2
            
            # Calculate UTF-16 length of emoji
            emoji_utf16_length = len(emoji_char.encode('utf-16-le')) // 2
            
            entities.append(MessageEntityCustomEmoji(
                offset=utf16_offset,
                length=emoji_utf16_length,
                document_id=int(premium_id)
            ))
        
        return entities
    except Exception as e:
        print(f"Error creating unlimited premium entities: {e}")
        return []

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    from config import Config
    Config.load_blacklist()
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Gcast & Blacklist Plugin loaded - Unlimited premium emoji broadcast ready")

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
                success_msg = f"{get_emoji('centang')} Added to blacklist\nChat: `{chat_title}`\nID: `{chat_id}`\nTotal Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
                
                await safe_edit_premium(event, success_msg)
            else:
                signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
                already_msg = f"{get_emoji('kuning')} Already Blacklisted\nChat: `{chat_title}`\nID: `{chat_id}`"
                
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
            signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
            success_msg = f"{get_emoji('centang')} Blacklist Removed\nID: `{chat_id}`\nTotal Blacklisted: `{len(Config.GCAST_BLACKLIST)}`"
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
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        blacklist_text = f"{signature} VzoelFox Gcast Blacklist ({len(Config.GCAST_BLACKLIST)})\n\n"
        
        for i, chat_id in enumerate(Config.GCAST_BLACKLIST, 1):
            try:
                chat = await event.client.get_entity(chat_id)
                chat_title = chat.title if hasattr(chat, 'title') else f"Private {chat_id}"
                blacklist_text += f"{i}. {chat_title}\n   ID: {chat_id}\n\n"

            except:
                blacklist_text += f"{i}. Unknown Chat\n   ID: {chat_id}\n\n"


        
        blacklist_text += "\nBy VzoelFox Assistant"

        
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
        
        # Animation phase 1: Process setup dengan estetik lebih baik
        setup_frames = [
            f"{get_emoji('loading')} Memulai persiapan...",
            f"{get_emoji('proses')} Memuat sistem broadcast...",
            f"{get_emoji('aktif')} Menghitung target chat...",
            f"{get_emoji('petir')} Menyiapkan pesan..."
        ]
        
        for frame in setup_frames:
            await safe_edit_premium(event, frame)
            await asyncio.sleep(0.8)
        
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
        
        # Animation phase 2: Starting broadcast dengan estetik
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Frame animasi startup yang lebih estetik
        startup_frames = [
            f"{signature} MEMULAI BROADCAST\n\n{get_emoji('centang')} Target Chat: `{total_chats}`\n{get_emoji('merah')} Blacklist: `{blacklisted_count}`\n{get_emoji('loading')} Menyiapkan engine...",
            f"{signature} VZOEL BROADCAST ENGINE\n\n{get_emoji('aktif')} Target Chat: `{total_chats}`\n{get_emoji('kuning')} Blacklist: `{blacklisted_count}`\n{get_emoji('proses')} Mengaktifkan sistem...",
            f"{signature} BROADCAST DIMULAI!\n\n{get_emoji('petir')} Target Chat: `{total_chats}`\n{get_emoji('biru')} Blacklist: `{blacklisted_count}`\n{get_emoji('telegram')} Status: ACTIVE"
        ]
        
        for frame in startup_frames:
            await safe_edit_premium(event, frame)
            await asyncio.sleep(1.2)
        
        # Broadcast loop
        successful_sends = 0
        failed_sends = 0
        
        for i, dialog in enumerate(dialogs, 1):
            try:
                # Update progress dengan animasi yang lebih estetik
                if i % 3 == 0 or i == total_chats:
                    # Progress bar estetik
                    progress_percentage = int((i / total_chats) * 100)
                    progress_bar = "█" * (progress_percentage // 10) + "░" * (10 - (progress_percentage // 10))
                    
                    # Emoji dinamis berdasarkan progress
                    if progress_percentage < 30:
                        status_emoji = get_emoji('loading')
                        status_text = "MEMULAI"
                    elif progress_percentage < 70:
                        status_emoji = get_emoji('proses')
                        status_text = "PROSES"
                    else:
                        status_emoji = get_emoji('aktif')
                        status_text = "HAMPIR SELESAI"
                    
                    progress_msg = f"""{signature} VZOEL BROADCAST {status_text}
                    
{status_emoji} Progress: [{progress_bar}] {progress_percentage}%
{get_emoji('centang')} Berhasil: `{successful_sends}`
{get_emoji('merah')} Gagal: `{failed_sends}`
{get_emoji('telegram')} Sedang: `{dialog.title[:25] or 'Unknown'}...`
{get_emoji('petir')} Status: `{i}/{total_chats}` chat"""
                    await safe_edit_premium(event, progress_msg)
                
                # Send message with premium emoji support
                if reply_message and reply_message.media:
                    # Forward media message with premium emoji support
                    if reply_message.text:
                        # Create unlimited premium entities for media caption
                        entities = create_unlimited_premium_entities(reply_message.text)
                        await event.client.send_message(
                            dialog.id, 
                            reply_message.text, 
                            file=reply_message.media,
                            formatting_entities=entities
                        )
                    else:
                        await event.client.send_message(
                            dialog.id, 
                            reply_message.text or "", 
                            file=reply_message.media
                        )
                else:
                    # Send text message with unlimited premium emoji support
                    entities = create_unlimited_premium_entities(message_text)
                    await event.client.send_message(
                        dialog.id, 
                        message_text, 
                        formatting_entities=entities
                    )
                
                successful_sends += 1
                
            except FloodWaitError as e:
                # Handle flood wait dengan premium emoji support
                await asyncio.sleep(e.seconds)
                try:
                    if reply_message and reply_message.media:
                        if reply_message.text:
                            entities = create_unlimited_premium_entities(reply_message.text)
                            await event.client.send_message(
                                dialog.id, 
                                reply_message.text, 
                                file=reply_message.media,
                                formatting_entities=entities
                            )
                        else:
                            await event.client.send_message(
                                dialog.id, 
                                reply_message.text or "", 
                                file=reply_message.media
                            )
                    else:
                        entities = create_unlimited_premium_entities(message_text)
                        await event.client.send_message(
                            dialog.id, 
                            message_text, 
                            formatting_entities=entities
                        )
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
        
        # Animation phase 3: Process completed dengan animasi akhir yang estetik
        completion_frames = [
            f"{signature} MENYELESAIKAN BROADCAST...\n\n{get_emoji('loading')} Menghitung hasil akhir...",
            f"{signature} MENGANALISA HASIL...\n\n{get_emoji('proses')} Processing statistics...",
            f"{signature} BROADCAST SELESAI!\n\n{get_emoji('centang')} Analisa hasil berhasil!"
        ]
        
        for frame in completion_frames:
            await safe_edit_premium(event, frame)
            await asyncio.sleep(1)
        
        # Final result dengan format yang lebih estetik
        final_progress_bar = "█" * 10  # Full bar
        success_emoji = get_emoji('centang') if success_rate >= 70 else get_emoji('kuning') if success_rate >= 40 else get_emoji('merah')
        
        complete_msg = f"""{signature} VZOEL BROADCAST COMPLETED!

{success_emoji} HASIL BROADCAST:
├ Progress: [{final_progress_bar}] 100%
├ Berhasil: `{successful_sends}` chat
├ Gagal: `{failed_sends}` chat  
├ Total Target: `{total_chats}` chat
└ Success Rate: `{success_rate:.1f}%`

{get_emoji('aktif')} STATISTIK WAKTU:
├ Durasi: `{duration:.1f}` detik
├ Rata-rata: `{(duration/total_chats):.2f}s` per chat
└ Speed: {get_emoji('petir')} VZOEL ENGINE

{get_emoji('adder2')} Ready for next broadcast!
{get_emoji('telegram')} by VzoelFox Assistant"""
        await safe_edit_premium(event, complete_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.ginfo'))
async def gcast_info_handler(event):
    """Show gcast information with animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from config import Config

        
        # Animation phase 1: Loading info dengan estetik
        loading_frames = [
            f"{get_emoji('loading')} Memuat informasi gcast...",
            f"{get_emoji('proses')} Menghitung chat tersedia...",
            f"{get_emoji('aktif')} Menganalisa blacklist...",
            f"{get_emoji('petir')} Menyiapkan statistik..."
        ]
        
        for frame in loading_frames:
            await safe_edit_premium(event, frame)
            await asyncio.sleep(0.8)
        
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
        
        # Animation phase 2: Show complete info dengan format lebih estetik
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        info_text = f"""{signature} VZOEL GCAST INFORMATION

{get_emoji('telegram')} TARGETS TERSEDIA:
├ Groups: `{total_groups}` chat
├ Channels: `{total_channels}` chat  
└ Total Available: `{total_available}` chat

{get_emoji('merah')} BLACKLIST STATUS:
├ Blacklisted: `{blacklisted_count}` chat
├ Will Broadcast: `{total_available}` chat
└ Protection: {get_emoji('centang')} ACTIVE

{get_emoji('petir')} COMMAND LIST:
├ .gcast <text> - Broadcast pesan text
├ .gcast (reply) - Broadcast dari reply
├ .addbl <id> - Tambah ke blacklist  
├ .rembl <id> - Hapus dari blacklist
├ .listbl - Lihat daftar blacklist
└ .ginfo - Info sistem gcast

{get_emoji('aktif')} ENGINE STATUS:
├ System: VZOEL BROADCAST ENGINE
├ Speed: {get_emoji('petir')} OPTIMIZED  
├ Safety: {get_emoji('centang')} BLACKLIST PROTECTED
└ Version: 3.0.0 PREMIUM

{get_emoji('adder2')} Powered by VzoelFox Technology"""
        
        await safe_edit_premium(event, info_text)
        if vzoel_client:
            vzoel_client.increment_command_count()
