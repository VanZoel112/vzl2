"""
VZOEL ASSISTANT - Voice Chat Plugin
Pure userbot voice chat control with modern PyTgCalls

Commands:
- .jvc - Join voice chat
- .lvc - Leave voice chat
- .startvc - Create new voice chat
- .vcinfo - Voice chat system info

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.voice_chat import VoiceChatManager

# Plugin info
PLUGIN_INFO = {
    "name": "voicechat",
    "version": "3.0.0",
    "description": "Pure userbot voice chat control",
    "author": "Vzoel Fox's",
    "commands": [".jvc", ".lvc", ".startvc", ".vcinfo"],
    "features": ["VC join/leave", "VC creation", "Pure userbot mode", "PyTgCalls integration"]
}

# Global references
vzoel_client = None
vzoel_emoji = None
vc_manager = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, vc_manager

    vzoel_client = client
    vzoel_emoji = emoji_handler

    # Initialize voice chat manager
    try:
        vc_manager = VoiceChatManager(client.client)
        await vc_manager.start()
        print(f"{get_emoji('utama')} VZOEL ASSISTANT Voice Chat System loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Voice chat init error: {e}")


@events.register(events.NewMessage(pattern=r'\.jvc'))
async def join_vc_handler(event):
    """Join voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\nVZOEL ASSISTANT")
            return

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} JOINING VOICE CHAT

{get_emoji('proses')} Connecting to voice chat
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""

        await safe_edit_premium(event, processing_msg)

        # Join voice chat
        success = await vc_manager.join_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for streaming

{get_emoji('proses')} Use .play to stream music
{get_emoji('kuning')} Use .lvc to disconnect

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
        else:
            response = f"""{get_emoji('merah')} JOIN FAILED

{get_emoji('kuning')} Possible reasons:
{get_emoji('telegram')} PyTgCalls not installed
{get_emoji('telegram')} No active voice chat in group
{get_emoji('telegram')} Permission denied

{get_emoji('aktif')} Try .startvc to create VC first

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.lvc'))
async def leave_vc_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\nVZOEL ASSISTANT")
            return

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} LEAVING VOICE CHAT

{get_emoji('proses')} Disconnecting
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""

        await safe_edit_premium(event, processing_msg)

        # Leave voice chat
        success = await vc_manager.leave_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} LEFT VOICE CHAT

{get_emoji('aktif')} Disconnected successfully

{get_emoji('telegram')} Use .jvc to rejoin

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
        else:
            response = f"""{get_emoji('kuning')} NOT IN VOICE CHAT

{get_emoji('telegram')} Use .jvc to connect first

VZOEL ASSISTANT"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.startvc'))
async def start_vc_handler(event):
    """Create new voice chat in group"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\nVZOEL ASSISTANT")
            return

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} CREATING VOICE CHAT

{get_emoji('proses')} Initializing voice chat
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""

        await safe_edit_premium(event, processing_msg)

        # Create voice chat
        success = await vc_manager.create_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} VOICE CHAT CREATED

{get_emoji('aktif')} Voice chat started successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .jvc to join
{get_emoji('biru')} Use .play to stream music

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

            # Auto-join after creation
            await asyncio.sleep(1)
            join_success = await vc_manager.join_voice_chat(event.chat_id)
            if join_success:
                response = f"""{get_emoji('centang')} VOICE CHAT CREATED AND JOINED

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .play to stream music
{get_emoji('kuning')} Use .lvc to leave

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        else:
            response = f"""{get_emoji('merah')} VOICE CHAT CREATION FAILED

{get_emoji('kuning')} Possible reasons:
{get_emoji('telegram')} Admin rights required
{get_emoji('telegram')} Voice chat already exists
{get_emoji('telegram')} Group restrictions

{get_emoji('aktif')} Check permissions and try again

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcinfo'))
async def vc_info_handler(event):
    """Show voice chat system info"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT")
            return

        stats = vc_manager.get_stats()
        active_chats = vc_manager.get_active_chats()

        # Check if in VC (only for group chats)
        is_connected = False
        if not event.is_private:
            is_connected = vc_manager.is_in_voice_chat(event.chat_id)

        response = f"""{get_emoji('utama')} VOICE CHAT SYSTEM INFO

{get_emoji('centang')} SYSTEM STATUS:
{get_emoji('telegram')} Available: {'Yes' if stats['available'] else 'No'}
{get_emoji('telegram')} Initialized: {'Yes' if stats['initialized'] else 'No'}
{get_emoji('telegram')} Active chats: {stats['active_chats']}"""

        if not event.is_private:
            response += f"""

{get_emoji('proses')} CURRENT CHAT:
{get_emoji('telegram')} Connected: {'Yes' if is_connected else 'No'}
{get_emoji('telegram')} Chat ID: {event.chat_id}"""

        response += f"""

{get_emoji('aktif')} AVAILABLE COMMANDS:
{get_emoji('telegram')} .jvc - Join voice chat
{get_emoji('telegram')} .lvc - Leave voice chat
{get_emoji('telegram')} .startvc - Create new voice chat
{get_emoji('telegram')} .play - Stream music to VC
{get_emoji('telegram')} .vcinfo - Show this info

{get_emoji('biru')} ARCHITECTURE:
{get_emoji('telegram')} Pure userbot mode
{get_emoji('telegram')} PyTgCalls integration
{get_emoji('telegram')} Direct voice chat control

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
