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

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = vzoel_emoji.get_vzoel_signature(premium=True)
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
        from emoji_handler_premium import vzoel_emoji
        
        # Check if we're in a group
        if event.is_private:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Voice chat commands only work in groups"
            )
            await event.edit(error_msg)
            return
        
        # Check PyTgCalls availability
        if not check_pytgcalls():
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "PyTgCalls not installed. Install with: pip install py-tgcalls"
            )
            await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        # Process animation
        process_phases = [
            "Initializing voice chat connection...",
            "Connecting to voice chat servers...",
            "Preparing audio stream...",
            "Joining voice chat..."
        ]
        
        msg = await event.edit(vzoel_emoji.format_emoji_response(['loading'], process_phases[0]))
        
        for i, phase in enumerate(process_phases[1:], 1):
            await asyncio.sleep(0.8)
            await msg.edit(vzoel_emoji.format_emoji_response(['proses'], phase))
        
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
            
            success_msg = vzoel_emoji.format_emoji_response(
                ['centang'], 
                f"**Voice Chat Joined**\n"
                f"Chat: {vc_status[chat_id]['chat_title']}\n"
                f"Status: Connected\n"
                f"Audio: Ready"
            )
            await msg.edit(success_msg)
            
        except Exception as e:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], f"Failed to join voice chat: {str(e)}"
            )
            await msg.edit(error_msg)
        
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcleave'))
async def vc_leave_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        if event.is_private:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Voice chat commands only work in groups"
            )
            await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "Not currently in voice chat"
            )
            await event.edit(not_joined_msg)
            return
        
        # Process animation
        leaving_msg = vzoel_emoji.format_emoji_response(
            ['loading'], "Leaving voice chat..."
        )
        msg = await event.edit(leaving_msg)
        await asyncio.sleep(1)
        
        try:
            # Leave voice chat
            await vc_instances[chat_id].leave_group_call(chat_id)
            
            # Update status
            vc_status[chat_id]['joined'] = False
            
            success_msg = vzoel_emoji.format_emoji_response(
                ['centang'], 
                f"**Left Voice Chat**\n"
                f"Chat: {vc_status[chat_id]['chat_title']}\n"
                f"Status: Disconnected"
            )
            await msg.edit(success_msg)
            
        except Exception as e:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], f"Failed to leave voice chat: {str(e)}"
            )
            await msg.edit(error_msg)
        
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcmute'))
async def vc_mute_handler(event):
    """Mute in voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        if event.is_private:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Voice chat commands only work in groups"
            )
            await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "Not currently in voice chat"
            )
            await event.edit(not_joined_msg)
            return
        
        try:
            # Mute stream
            await vc_instances[chat_id].mute_stream(chat_id)
            vc_status[chat_id]['muted'] = True
            
            muted_msg = vzoel_emoji.format_emoji_response(
                ['proses'], 
                f"**Voice Chat Muted**\n"
                f"Chat: {vc_status[chat_id]['chat_title']}\n"
                f"Status: Muted"
            )
            await event.edit(muted_msg)
            
        except Exception as e:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], f"Failed to mute: {str(e)}"
            )
            await event.edit(error_msg)
        
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcunmute'))
async def vc_unmute_handler(event):
    """Unmute in voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        if event.is_private:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Voice chat commands only work in groups"
            )
            await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        
        if chat_id not in vc_instances or not vc_status.get(chat_id, {}).get('joined', False):
            not_joined_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "Not currently in voice chat"
            )
            await event.edit(not_joined_msg)
            return
        
        try:
            # Unmute stream
            await vc_instances[chat_id].unmute_stream(chat_id)
            vc_status[chat_id]['muted'] = False
            
            unmuted_msg = vzoel_emoji.format_emoji_response(
                ['centang'], 
                f"**Voice Chat Unmuted**\n"
                f"Chat: {vc_status[chat_id]['chat_title']}\n"
                f"Status: Speaking"
            )
            await event.edit(unmuted_msg)
            
        except Exception as e:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], f"Failed to unmute: {str(e)}"
            )
            await event.edit(error_msg)
        
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcstatus'))
async def vc_status_handler(event):
    """Show voice chat status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        if event.is_private:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], "Voice chat commands only work in groups"
            )
            await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        chat = await event.get_chat()
        
        # Check if PyTgCalls is available
        pytgcalls_status = "✅ Installed" if check_pytgcalls() else "❌ Not Installed"
        
        # Check voice chat status
        if chat_id in vc_status and vc_status[chat_id].get('joined', False):
            vc_connection = "✅ Connected"
            audio_status = "🔇 Muted" if vc_status[chat_id].get('muted', False) else "🎤 Speaking"
        else:
            vc_connection = "❌ Not Connected"
            audio_status = "❌ N/A"
        
        signature = vzoel_emoji.get_vzoel_signature(premium=True)
        
        status_text = f"""**{signature} Voice Chat Status**

{vzoel_emoji.getemoji('telegram', premium=True)} **Chat:** {chat.title}
{vzoel_emoji.getemoji('utama', premium=True)} **PyTgCalls:** {pytgcalls_status}
{vzoel_emoji.getemoji('aktif', premium=True)} **Connection:** {vc_connection}
{vzoel_emoji.getemoji('proses', premium=True)} **Audio:** {audio_status}

{vzoel_emoji.getemoji('centang', premium=True)} **Available Commands:**
• `.vcjoin` - Join voice chat
• `.vcleave` - Leave voice chat
• `.vcmute` - Mute microphone
• `.vcunmute` - Unmute microphone
• `.vcstatus` - Show this status

**By VzoelFox Assistant**"""
        
        await event.edit(status_text)
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.vcinstall'))
async def vc_install_handler(event):
    """Show installation instructions for PyTgCalls"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from plugins.comments import vzoel_comments
        
        signature = vzoel_emoji.get_vzoel_signature(premium=True)
        
        install_text = f"""**{signature} VzoelFox Voice Chat Setup**

{vzoel_emoji.getemoji('loading', premium=True)} **Installation Required:**

{vzoel_emoji.getemoji('utama', premium=True)} **Step 1:** Install PyTgCalls
```bash
pip install py-tgcalls -U
```

{vzoel_emoji.getemoji('centang', premium=True)} **Step 2:** Install FFmpeg (if needed)
```bash
# Ubuntu/Debian
apt install ffmpeg

# Termux
pkg install ffmpeg
```

{vzoel_emoji.getemoji('aktif', premium=True)} **Step 3:** Restart VzoelFox Assistant
```bash
.restart
```

{vzoel_emoji.getemoji('telegram', premium=True)} **Features After Installation:**
• Join voice chats in groups
• Mute/unmute microphone
• Professional voice chat management
• Audio streaming capabilities

{vzoel_emoji.getemoji('petir', premium=True)} **Note:** Voice chat requires user account (not bot)

**By VzoelFox Assistant**"""
        
        await event.edit(install_text)
        vzoel_client.increment_command_count()

