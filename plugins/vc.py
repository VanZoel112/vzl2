import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
VzoelFox's Assistant Voice Chat Plugin
Advanced voice chat management for userbot with PyTgCalls integration
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
import asyncio
import logging

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variables for voice chat state
vc_instances = {}
vc_status = {}

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Voice Chat Plugin loaded - VC management ready")

def check_pytgcalls():
    """Check if PyTgCalls is available"""
    try:
        import pytgcalls
        return True
    except ImportError:
        return False

@events.register(events.NewMessage(pattern=r'\.vcjoin'))
async def vc_join_handler(event):
    """Join voice chat in current group"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        # Check if we're in a group
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"
            msg = await event.edit(error_msg)
            await safe_edit_premium(msg, error_msg)
            return
        
        # Check PyTgCalls availability
        if not check_pytgcalls():
            error_msg = f"{get_emoji('merah')} PyTgCalls not installed. Install with: pip install py-tgcalls"
            msg = await event.edit(error_msg)
            await safe_edit_premium(msg, error_msg)
            return
        
        chat_id = event.chat_id
        
        # Process animation
        process_phases = [
            "Initializing voice chat connection...",
            "Connecting to voice chat servers...",
            "Preparing audio stream...",
            "Joining voice chat..."
        ]
        
        
        msg = await event.edit(f"{get_emoji('loading')} {process_phases[0]}")
        
        for i, phase in enumerate(process_phases[1:], 1):
            await asyncio.sleep(0.8)
            await safe_edit_premium(msg, f"{get_emoji('proses')} {phase}")
        
        try:
            # Import PyTgCalls dynamically
            from pytgcalls import PyTgCalls
            from pytgcalls.types.input_stream import InputAudioStream, InputStream
            # Create PyTgCalls instance if not exists
            if chat_id not in vc_instances:
                vc_instances[chat_id] = PyTgCalls(event.client)
                await vc_instances[chat_id].start()
            # Join voice chat with blank audio stream
            await vc_instances[chat_id].join_group_call(
                chat_id,
                InputStream(InputAudioStream()),
                stream_type="blank"
            )
            vc_status[chat_id] = {
                'joined': True,
                'muted': False,
                'chat_title': (await event.get_chat()).title
            }
            success_msg = f"{get_emoji('centang')} **Voice Chat Joined**\\nChat: {vc_status[chat_id]['chat_title']}\\nStatus: Connected\\nAudio: Ready"
            await safe_edit_premium(msg, success_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to join voice chat: {str(e)}"
            await safe_edit_premium(msg, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcleave'))
async def vc_leave_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"
            msg = await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = f"{get_emoji('kuning')} Not currently in voice chat"
            msg = await event.edit(not_joined_msg)
            return
        
        # Process animation
        leaving_msg = f"{get_emoji('loading')} Leaving voice chat..."
        msg = await event.edit(leaving_msg)
        await asyncio.sleep(1)
        
        try:
            # Leave voice chat
            await vc_instances[chat_id].leave_group_call(chat_id)
            # Update status
            vc_status[chat_id]['joined'] = False
            success_msg = f"{get_emoji('centang')} **Left Voice Chat**\\nChat: {vc_status[chat_id]['chat_title']}\\nStatus: Disconnected"
            await safe_edit_premium(msg, success_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to leave voice chat: {str(e)}"
            await safe_edit_premium(msg, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcmute'))
async def vc_mute_handler(event):
    """Mute in voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"

            msg = await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = f"{get_emoji('kuning')} Not currently in voice chat"
            msg = await event.edit(not_joined_msg)
            return
        
        try:
            # Mute stream
            await vc_instances[chat_id].mute_stream(chat_id)
            vc_status[chat_id]['muted'] = True
            muted_msg = f"{get_emoji('proses')} **Voice Chat Muted**\\nChat: {vc_status[chat_id]['chat_title']}\\nStatus: Muted"
            msg = await event.edit(muted_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to mute: {str(e)}"
            msg = await event.edit(error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcunmute'))
async def vc_unmute_handler(event):
    """Unmute in voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"

            msg = await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = f"{get_emoji('kuning')} Not currently in voice chat"
            msg = await event.edit(not_joined_msg)
            return
        
        try:
            # Unmute stream
            await vc_instances[chat_id].unmute_stream(chat_id)
            vc_status[chat_id]['muted'] = False
            unmuted_msg = f"{get_emoji('centang')} **Voice Chat Unmuted**\\nChat: {vc_status[chat_id]['chat_title']}\\nStatus: Speaking"
            msg = await event.edit(unmuted_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to unmute: {str(e)}"
            msg = await event.edit(error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcstatus'))
async def vc_status_handler(event):
    """Show voice chat status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"

            msg = await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        chat = await event.get_chat()
        
        # Check if PyTgCalls is available
        pytgcalls_status = f"{get_emoji('centang')} Installed" if check_pytgcalls() else f"{get_emoji('merah')} Not Installed"
        
        # Check voice chat status
        if chat_id in vc_status and vc_status[chat_id].get('joined', False):
            vc_connection = f"{get_emoji('centang')} Connected"
            audio_status = "🔇 Muted" if vc_status[chat_id].get('muted', False) else "🎤 Speaking"
        else:
            vc_connection = f"{get_emoji('merah')} Not Connected"
            audio_status = f"{get_emoji('merah')} N/A"
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        status_text = f"""**{signature} Voice Chat Status**

{get_emoji('telegram')} **Chat:** {chat.title}
{get_emoji('utama')} **PyTgCalls:** {pytgcalls_status}
{get_emoji('aktif')} **Connection:** {vc_connection}
{get_emoji('proses')} **Audio:** {audio_status}

{get_emoji('centang')} **Available Commands:**
• `.vcjoin` - Join voice chat
• `.vcleave` - Leave voice chat
• `.vcmute` - Mute microphone
• `.vcunmute` - Unmute microphone
• `.vcstatus` - Show this status

**By VzoelFox Assistant**"""
        
        msg = await event.edit(status_text)
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcinstall'))
async def vc_install_handler(event):
    """Show installation instructions for PyTgCalls"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        

        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        install_text = f"""**{signature} VzoelFox Voice Chat Setup**

{get_emoji('loading')} **Installation Required:**

{get_emoji('utama')} **Step 1:** Install PyTgCalls
```bash
pip install py-tgcalls -U
```

{get_emoji('centang')} **Step 2:** Install FFmpeg (if needed)
```bash
# Ubuntu/Debian
apt install ffmpeg

# Termux
pkg install ffmpeg
```

{get_emoji('aktif')} **Step 3:** Restart VzoelFox Assistant
```bash
.restart
```

{get_emoji('telegram')} **Features After Installation:**
• Join voice chats in groups
• Mute/unmute microphone
• Professional voice chat management
• Audio streaming capabilities

{get_emoji('petir')} **Note:** Voice chat requires user account (not bot)

**By VzoelFox Assistant**"""
        
        msg = await event.edit(install_text)
        if vzoel_client:
            vzoel_client.increment_command_count()
