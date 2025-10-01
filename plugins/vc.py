"""
VZOEL ASSISTANT - Voice Chat Plugin
Userbot voice chat with PyTgCalls GroupCallFactory

Commands:
- .jvc - Join voice chat
- .lvc - Leave voice chat

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# Try import PyTgCalls dengan GroupCallFactory
try:
    from pytgcalls import GroupCallFactory
    from pytgcalls.mtproto_client_type import MTProtoClientType
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    GroupCallFactory = None
    MTProtoClientType = None

# Global references
vzoel_client = None
vzoel_emoji = None
group_call_factory = None
active_calls = {}


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, group_call_factory

    vzoel_client = client
    vzoel_emoji = emoji_handler

    if PYTGCALLS_AVAILABLE:
        try:
            # Initialize GroupCallFactory dengan Telethon client
            group_call_factory = GroupCallFactory(
                client.client,
                mtproto_backend=MTProtoClientType.TELETHON
            )
            print(f"{get_emoji('utama')} VC Plugin loaded - GroupCallFactory ready")
        except Exception as e:
            print(f"{get_emoji('merah')} GroupCallFactory error: {e}")
            group_call_factory = None
    else:
        print(f"{get_emoji('kuning')} PyTgCalls not installed")


@events.register(events.NewMessage(pattern=r'\.jvc'))
async def join_vc_handler(event):
    """Join voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, group_call_factory, active_calls

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
            return

        if not PYTGCALLS_AVAILABLE or not group_call_factory:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTgCalls not installed\n\n{get_emoji('telegram')} Install: pip install py-tgcalls\n\nVZOEL ASSISTANT")
            return

        chat_id = event.chat_id

        if chat_id in active_calls:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Already in VC\n\nVZOEL ASSISTANT")
            return

        processing_msg = f"""{get_emoji('loading')} JOINING VOICE CHAT

{get_emoji('proses')} Connecting with GroupCall
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        try:
            # Create group call dengan silent file
            group_call = group_call_factory.get_file_group_call(
                'http://duramecho.com/Misc/SilentCd/Silence01s.wav'
            )

            # Join group call
            await group_call.start(chat_id)

            # Store active call
            active_calls[chat_id] = group_call

            response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for streaming

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        except Exception as e:
            response = f"""{get_emoji('merah')} JOIN FAILED

{get_emoji('kuning')} Error: {str(e)[:80]}

VZOEL ASSISTANT"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.lvc'))
async def leave_vc_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, active_calls

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
            return

        if not PYTGCALLS_AVAILABLE:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTgCalls not installed\n\nVZOEL ASSISTANT")
            return

        chat_id = event.chat_id

        if chat_id not in active_calls:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Not in VC\n\nVZOEL ASSISTANT")
            return

        processing_msg = f"""{get_emoji('loading')} LEAVING VOICE CHAT

{get_emoji('proses')} Disconnecting

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        try:
            group_call = active_calls[chat_id]
            await group_call.stop()
            del active_calls[chat_id]

            response = f"""{get_emoji('centang')} LEFT VOICE CHAT

{get_emoji('aktif')} Disconnected

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        except Exception as e:
            response = f"""{get_emoji('merah')} LEAVE FAILED

{get_emoji('kuning')} Error: {str(e)[:80]}

VZOEL ASSISTANT"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
