"""
VZOEL ASSISTANT - Voice Chat Plugin
Pure userbot voice chat control with PyTgCalls

Commands:
- .jvc - Join voice chat (as userbot)
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
    "version": "3.1.0",
    "description": "Pure userbot voice chat control with PyTgCalls",
    "author": "Vzoel Fox's",
    "commands": [".jvc", ".lvc", ".startvc", ".vcinfo"],
    "features": ["VC join as userbot", "Silent mode", "PyTgCalls integration", "Pure userbot mode"]
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
        print(f"{get_emoji('utama')} VZOEL ASSISTANT Voice Chat System loaded (pure userbot)")
    except Exception as e:
        print(f"{get_emoji('merah')} Voice chat init error: {e}")


@events.register(events.NewMessage(pattern=r'\.jvc'))
async def join_vc_handler(event):
    """Join voice chat as userbot"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\nVZOEL ASSISTANT")
            return

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan")
            return

        # Check if PyTgCalls is available
        stats = vc_manager.get_stats()
        if not stats['available']:
            response = f"""{get_emoji('merah')} PYTGCALLS NOT INSTALLED

{get_emoji('kuning')} Installation Required:
{get_emoji('telegram')} pip install py-tgcalls -U

{get_emoji('aktif')} PyTgCalls is required for userbot voice chat

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
            await safe_edit_premium(event, response)
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} JOINING VOICE CHAT

{get_emoji('proses')} Connecting as userbot
{get_emoji('telegram')} Mode: Silent stream
{get_emoji('aktif')} Please wait

VZOEL ASSISTANT"""

        await safe_edit_premium(event, processing_msg)

        # Join voice chat with silent stream (pure userbot mode)
        success = await vc_manager.join_voice_chat(event.chat_id, silent=True)

        if success:
            response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Connected as userbot
{get_emoji('telegram')} Mode: Silent stream
{get_emoji('proses')} Ready for audio streaming

{get_emoji('biru')} Commands:
{get_emoji('telegram')} .play - Stream music
{get_emoji('telegram')} .lvc - Leave voice chat

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
        else:
            response = f"""{get_emoji('merah')} JOIN FAILED

{get_emoji('kuning')} Possible reasons:
{get_emoji('telegram')} No active voice chat in group
{get_emoji('telegram')} PyTgCalls connection error
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

        # Check if in VC
        if not vc_manager.is_in_voice_chat(event.chat_id):
            await safe_edit_premium(event, f"{get_emoji('kuning')} NOT IN VOICE CHAT\n\n{get_emoji('telegram')} Use .jvc to join first\n\nVZOEL ASSISTANT")
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
            response = f"""{get_emoji('merah')} LEAVE FAILED

{get_emoji('kuning')} Error disconnecting from voice chat

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

{get_emoji('proses')} Auto-joining as userbot

VZOEL ASSISTANT"""

            await safe_edit_premium(event, response)

            # Auto-join after creation
            await asyncio.sleep(2)
            join_success = await vc_manager.join_voice_chat(event.chat_id, silent=True)

            if join_success:
                response = f"""{get_emoji('centang')} VOICE CHAT CREATED AND JOINED

{get_emoji('aktif')} Connected as userbot
{get_emoji('telegram')} Mode: Silent stream
{get_emoji('proses')} Ready for audio streaming

{get_emoji('biru')} Commands:
{get_emoji('telegram')} .play - Stream music
{get_emoji('telegram')} .lvc - Leave voice chat

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
                await safe_edit_premium(event, response)

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
        vc_mode = "N/A"
        if not event.is_private:
            is_connected = vc_manager.is_in_voice_chat(event.chat_id)
            if is_connected:
                chat_info = active_chats.get(event.chat_id, {})
                vc_mode = chat_info.get('mode', 'unknown')

        response = f"""{get_emoji('utama')} VOICE CHAT SYSTEM INFO

{get_emoji('centang')} SYSTEM STATUS:
{get_emoji('telegram')} Available: {'Yes' if stats['available'] else 'No'}
{get_emoji('telegram')} Initialized: {'Yes' if stats['initialized'] else 'No'}
{get_emoji('telegram')} Mode: {stats.get('mode', 'unknown')}
{get_emoji('telegram')} Active chats: {stats['active_chats']}"""

        if not event.is_private:
            response += f"""

{get_emoji('proses')} CURRENT CHAT:
{get_emoji('telegram')} Connected: {'Yes' if is_connected else 'No'}
{get_emoji('telegram')} VC Mode: {vc_mode}
{get_emoji('telegram')} Chat ID: {event.chat_id}"""

        response += f"""

{get_emoji('aktif')} AVAILABLE COMMANDS:
{get_emoji('telegram')} .jvc - Join voice chat as userbot
{get_emoji('telegram')} .lvc - Leave voice chat
{get_emoji('telegram')} .startvc - Create new voice chat
{get_emoji('telegram')} .play - Stream music to VC
{get_emoji('telegram')} .vcinfo - Show this info

{get_emoji('biru')} ARCHITECTURE:
{get_emoji('telegram')} Pure userbot mode (not bot)
{get_emoji('telegram')} PyTgCalls integration
{get_emoji('telegram')} Silent stream for idle presence
{get_emoji('telegram')} Direct voice chat control

{get_emoji('kuning')} REQUIREMENTS:
{get_emoji('telegram')} PyTgCalls installed
{get_emoji('telegram')} Active voice chat in group
{get_emoji('telegram')} Userbot account (not bot)

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
