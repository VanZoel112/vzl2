"""
Vzoel Fox's Lutpan - Voice Chat Plugin
Pure userbot voice chat control

Commands:
- .jlvc - Join/Leave voice chat toggle
- .startvc - Create new voice chat in group

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.voice_chat import VoiceChatManager

# Plugin info
PLUGIN_INFO = {
    "name": "voicechat",
    "version": "2.0.0",
    "description": "Pure userbot voice chat control",
    "author": "Vzoel Fox's",
    "commands": [".jlvc", ".startvc"],
    "features": ["VC join/leave toggle", "VC creation", "Pure userbot mode"]
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
        print(f"{get_emoji('utama')} Vzoel Fox's Lutpan Voice Chat System loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Voice chat init error: {e}")


@events.register(events.NewMessage(pattern=r'\.jlvc'))
async def join_leave_vc_handler(event):
    """Join/Leave voice chat toggle"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Processing voice chat request**

{get_emoji('proses')} Checking voice chat status
{get_emoji('telegram')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Toggle join/leave
        success, action = await vc_manager.toggle_voice_chat(event.chat_id)

        if success:
            if action == 'joined':
                response = f"""{get_emoji('centang')} **Joined voice chat**

{get_emoji('aktif')} Ready for streaming
{get_emoji('telegram')} Use .play to stream music

{get_emoji('proses')} Use .jlvc again to leave

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""
            elif action == 'left':
                response = f"""{get_emoji('centang')} **Left voice chat**

{get_emoji('aktif')} Disconnected successfully

{get_emoji('telegram')} Use .jlvc to rejoin

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""
            else:
                response = f"""{get_emoji('kuning')} **Voice chat action completed**

{get_emoji('telegram')} Status updated

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('merah')} **Voice chat operation failed**

{get_emoji('kuning')} Possible reasons:
• PyTgCalls not installed
• No active voice chat in group
• Permission denied

{get_emoji('aktif')} Try creating VC with .startvc

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.startvc'))
async def start_vc_handler(event):
    """Create new voice chat in group"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Check if in private chat
        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Creating voice chat**

{get_emoji('proses')} Initializing voice chat
{get_emoji('telegram')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Create voice chat
        success = await vc_manager.create_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} **Voice chat created**

{get_emoji('aktif')} Voice chat started successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .jlvc to join
{get_emoji('biru')} Use .play to stream music

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""

            # Auto-join after creation
            join_success, _ = await vc_manager.toggle_voice_chat(event.chat_id)
            if join_success:
                response = f"""{get_emoji('centang')} **Voice chat created and joined**

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .play to stream music
{get_emoji('kuning')} Use .jlvc to leave

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""

        else:
            response = f"""{get_emoji('merah')} **Voice chat creation failed**

{get_emoji('kuning')} Possible reasons:
• Admin rights required
• Voice chat already exists
• Group restrictions

{get_emoji('aktif')} Check permissions and try again

**Vzoel Fox's Lutpan** Voice Chat
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcinfo'))
async def vc_info_handler(event):
    """Show voice chat system info"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        stats = vc_manager.get_stats()
        active_chats = vc_manager.get_active_chats()
        is_connected = vc_manager.is_in_voice_chat(event.chat_id)

        response = f"""{get_emoji('utama')} **Voice Chat System Info**

{get_emoji('centang')} **System Status:**
• Available: {'Yes' if stats['available'] else 'No'}
• Initialized: {'Yes' if stats['initialized'] else 'No'}
• Active chats: {stats['active_chats']}

{get_emoji('proses')} **Current Chat:**
• Connected: {'Yes' if is_connected else 'No'}
• Chat ID: {event.chat_id}

{get_emoji('aktif')} **Available Commands:**
• .jlvc - Join/leave voice chat toggle
• .startvc - Create new voice chat
• .play - Stream music to VC
• .vcinfo - Show this info

{get_emoji('telegram')} **Architecture:**
• Pure userbot mode
• PyTgCalls integration
• Direct voice chat control

**Vzoel Fox's Lutpan** Voice Chat System
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
