"""
Vzoel Fox's Lutpan - Voice Chat Plugin
Pure userbot voice chat control

Commands:
- .join - Join voice chat
- .leave - Leave voice chat
- .jlvc - Join/Leave voice chat toggle (legacy)
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
    "commands": [".join", ".leave", ".jlvc", ".startvc", ".vcinfo"],
    "features": ["VC join/leave", "VC creation", "Pure userbot mode", "Status info"]
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


@events.register(events.NewMessage(pattern=r'\.join'))
async def join_vc_handler(event):
    """Join voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT\nBY VZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} JOINING VOICE CHAT

{get_emoji('proses')} Connecting to voice chat
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Join voice chat
        success = await vc_manager.join_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for streaming

{get_emoji('proses')} Use .play to stream music
{get_emoji('kuning')} Use .leave to disconnect

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN
~2025 Vzoel Fox's Lutpan"""
        else:
            response = f"""{get_emoji('merah')} JOIN FAILED

{get_emoji('kuning')} Possible reasons:
• PyTgCalls not installed
• No active voice chat in group
• Permission denied

{get_emoji('aktif')} Try .startvc to create VC first

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN
~2025 Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.leave'))
async def leave_vc_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL ASSISTANT\nBY VZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} LEAVING VOICE CHAT

{get_emoji('proses')} Disconnecting
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Leave voice chat
        success = await vc_manager.leave_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} LEFT VOICE CHAT

{get_emoji('aktif')} Disconnected successfully

{get_emoji('telegram')} Use .join to rejoin

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN
~2025 Vzoel Fox's Lutpan"""
        else:
            response = f"""{get_emoji('kuning')} NOT IN VOICE CHAT

{get_emoji('telegram')} Use .join to connect first

VZOEL ASSISTANT
BY VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.jlvc'))
async def join_leave_vc_handler(event):
    """Join/Leave voice chat toggle"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} PROCESSING VOICE CHAT REQUEST

{get_emoji('proses')} Checking voice chat status
{get_emoji('telegram')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Toggle join/leave
        success, action = await vc_manager.toggle_voice_chat(event.chat_id)

        if success:
            if action == 'joined':
                response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Ready for streaming
{get_emoji('telegram')} Use .play to stream music

{get_emoji('proses')} Use .jlvc again to leave

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""
            elif action == 'left':
                response = f"""{get_emoji('centang')} LEFT VOICE CHAT

{get_emoji('aktif')} Disconnected successfully

{get_emoji('telegram')} Use .jlvc to rejoin

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""
            else:
                response = f"""{get_emoji('kuning')} VOICE CHAT ACTION COMPLETED

{get_emoji('telegram')} Status updated

VZOEL FOX'S LUTPAN"""
        else:
            response = f"""{get_emoji('merah')} VOICE CHAT OPERATION FAILED

{get_emoji('kuning')} Possible reasons:
• PyTgCalls not installed
• No active voice chat in group
• Permission denied

{get_emoji('aktif')} Try creating VC with .startvc

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.startvc'))
async def start_vc_handler(event):
    """Create new voice chat in group"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Check if in private chat
        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} This command only works in groups\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} CREATING VOICE CHAT

{get_emoji('proses')} Initializing voice chat
{get_emoji('telegram')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Create voice chat
        success = await vc_manager.create_voice_chat(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} VOICE CHAT CREATED

{get_emoji('aktif')} Voice chat started successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .jlvc to join
{get_emoji('biru')} Use .play to stream music

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""

            # Auto-join after creation
            join_success, _ = await vc_manager.toggle_voice_chat(event.chat_id)
            if join_success:
                response = f"""{get_emoji('centang')} VOICE CHAT CREATED AND JOINED

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for audio streaming

{get_emoji('proses')} Use .play to stream music
{get_emoji('kuning')} Use .jlvc to leave

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""

        else:
            response = f"""{get_emoji('merah')} VOICE CHAT CREATION FAILED

{get_emoji('kuning')} Possible reasons:
• Admin rights required
• Voice chat already exists
• Group restrictions

{get_emoji('aktif')} Check permissions and try again

VZOEL FOX'S LUTPAN Voice Chat
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcinfo'))
async def vc_info_handler(event):
    """Show voice chat system info"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vc_manager

        if not vc_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Voice chat system not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        stats = vc_manager.get_stats()
        active_chats = vc_manager.get_active_chats()
        is_connected = vc_manager.is_in_voice_chat(event.chat_id)

        response = f"""{get_emoji('utama')} VOICE CHAT SYSTEM INFO

{get_emoji('centang')} SYSTEM STATUS:
• Available: {'Yes' if stats['available'] else 'No'}
• Initialized: {'Yes' if stats['initialized'] else 'No'}
• Active chats: {stats['active_chats']}

{get_emoji('proses')} CURRENT CHAT:
• Connected: {'Yes' if is_connected else 'No'}
• Chat ID: {event.chat_id}

{get_emoji('aktif')} AVAILABLE COMMANDS:
• .jlvc - Join/leave voice chat toggle
• .startvc - Create new voice chat
• .play - Stream music to VC
• .vcinfo - Show this info

{get_emoji('telegram')} ARCHITECTURE:
• Pure userbot mode
• PyTgCalls integration
• Direct voice chat control

VZOEL FOX'S LUTPAN Voice Chat System
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
