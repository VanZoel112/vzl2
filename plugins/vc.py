"""
VZOEL ASSISTANT - Voice Chat Plugin
Simple join/leave VC commands

Commands:
- .jvc - Join voice chat
- .lvc - Leave voice chat

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# Try import PyTgCalls
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types.input_stream import AudioPiped
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    PyTgCalls = None
    AudioPiped = None

# Global references
vzoel_client = None
vzoel_emoji = None
pytg_app = None
active_vcs = {}


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, pytg_app

    vzoel_client = client
    vzoel_emoji = emoji_handler

    if PYTGCALLS_AVAILABLE:
        try:
            pytg_app = PyTgCalls(client.client)
            await pytg_app.start()
            print(f"{get_emoji('utama')} VC Plugin loaded - PyTgCalls ready")
        except Exception as e:
            print(f"{get_emoji('merah')} PyTgCalls error: {e}")
            pytg_app = None
    else:
        print(f"{get_emoji('kuning')} PyTgCalls not installed")


@events.register(events.NewMessage(pattern=r'\.jvc'))
async def join_vc_handler(event):
    """Join voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, pytg_app, active_vcs

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
            return

        if not PYTGCALLS_AVAILABLE or not pytg_app:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTgCalls not installed\n\n{get_emoji('telegram')} Install: pip install py-tgcalls\n\nVZOEL ASSISTANT")
            return

        chat_id = event.chat_id

        if chat_id in active_vcs:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Already in VC\n\nVZOEL ASSISTANT")
            return

        processing_msg = f"""{get_emoji('loading')} JOINING VOICE CHAT

{get_emoji('proses')} Connecting
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        try:
            # Join with silent stream
            await pytg_app.join_group_call(
                chat_id,
                AudioPiped("http://duramecho.com/Misc/SilentCd/Silence01s.wav")
            )

            active_vcs[chat_id] = True

            response = f"""{get_emoji('centang')} JOINED VOICE CHAT

{get_emoji('aktif')} Connected successfully
{get_emoji('telegram')} Ready for streaming

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        except Exception as e:
            response = f"""{get_emoji('merah')} JOIN FAILED

{get_emoji('kuning')} Error: {str(e)[:50]}

VZOEL ASSISTANT"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.lvc'))
async def leave_vc_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, pytg_app, active_vcs

        if event.is_private:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
            return

        if not PYTGCALLS_AVAILABLE or not pytg_app:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTgCalls not installed\n\nVZOEL ASSISTANT")
            return

        chat_id = event.chat_id

        if chat_id not in active_vcs:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Not in VC\n\nVZOEL ASSISTANT")
            return

        processing_msg = f"""{get_emoji('loading')} LEAVING VOICE CHAT

{get_emoji('proses')} Disconnecting

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        try:
            await pytg_app.leave_group_call(chat_id)
            del active_vcs[chat_id]

            response = f"""{get_emoji('centang')} LEFT VOICE CHAT

{get_emoji('aktif')} Disconnected

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

        except Exception as e:
            response = f"""{get_emoji('merah')} LEAVE FAILED

{get_emoji('kuning')} Error: {str(e)[:50]}

VZOEL ASSISTANT"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
