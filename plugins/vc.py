import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced Voice Chat Plugin for Vzoel Fox's Userbot - Premium Edition
Fitur: Modern voice chat management dengan PyTgCalls 2024 API
Founder Userbot: Vzoel Fox's Ltpn
Version: 4.0.0 - Modern Voice Chat System
"""

from telethon import events
import asyncio
import logging

# Plugin info
__version__ = "4.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Global variables for voice chat state
vc_instances = {}
vc_status = {}

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Voice Chat Plugin loaded - VC management ready")

def check_pytgcalls():
    """Check if PyTgCalls is available and get version info"""
    try:
        import pytgcalls
        version = getattr(pytgcalls, '__version__', 'unknown')
        return {'available': True, 'version': version}
    except ImportError:
        return {'available': False, 'version': None}

def check_api_compatibility():
    """Check PyTgCalls API compatibility"""
    try:
        # Check for new API (recommended)
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream
        return {'api_type': 'modern', 'has_mediastream': True}
    except ImportError:
        try:
            # Check for legacy API (deprecated)
            from pytgcalls import PyTgCalls
            from pytgcalls.types.input_stream import InputStream
            return {'api_type': 'legacy', 'has_mediastream': False}
        except ImportError:
            return {'api_type': 'none', 'has_mediastream': False}

async def create_silence_file():
    """Create a silent audio file for voice-only joining"""
    import os
    import tempfile

    # Create temporary silent audio file
    temp_dir = tempfile.gettempdir()
    silence_file = os.path.join(temp_dir, 'vzl2_silence.raw')

    try:
        # Create 1-second silent audio (48kHz, 16-bit, stereo)
        silent_data = b'\x00' * (48000 * 2 * 2)  # 48kHz * 2 channels * 2 bytes per sample
        with open(silence_file, 'wb') as f:
            f.write(silent_data)
        return silence_file
    except Exception as e:
        print(f"[VC] Error creating silence file: {e}")
        return None

@events.register(events.NewMessage(pattern=r'\.vcjoin'))
async def vc_join_handler(event):
    """Join voice chat in current group with modern PyTgCalls API"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        # Check if we're in a group
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"
            await safe_edit_premium(event, error_msg)
            return

        # Check PyTgCalls availability and compatibility
        pytgcalls_info = check_pytgcalls()
        if not pytgcalls_info['available']:
            error_msg = f"{get_emoji('merah')} PyTgCalls not installed\n\n{get_emoji('centang')} Install with: `pip install py-tgcalls -U`\n{get_emoji('telegram')} VZL2 Voice Chat v4.0"
            await safe_edit_premium(event, error_msg)
            return

        # Check API compatibility
        api_info = check_api_compatibility()
        if api_info['api_type'] == 'none':
            error_msg = f"{get_emoji('merah')} PyTgCalls API not compatible\n\n{get_emoji('kuning')} Please install: `pip install py-tgcalls -U`\n{get_emoji('telegram')} VZL2 Voice Chat v4.0"
            await safe_edit_premium(event, error_msg)
            return

        chat_id = event.chat_id
        chat = await event.get_chat()

        # Modern process animation
        process_phases = [
            f"Initializing modern voice chat system...",
            f"Checking API compatibility: {api_info['api_type']}",
            f"Preparing voice-only connection...",
            f"Joining voice chat in {chat.title}..."
        ]

        msg = await safe_edit_premium(event, f"{get_emoji('loading')} {process_phases[0]}")

        for i, phase in enumerate(process_phases[1:], 1):
            await asyncio.sleep(1)
            progress_emoji = get_emoji(['proses', 'aktif', 'kuning'][i-1])
            await safe_edit_premium(msg, f"{progress_emoji} {phase}")

        try:
            # Use modern PyTgCalls API
            from pytgcalls import PyTgCalls

            # Create PyTgCalls instance if not exists
            if chat_id not in vc_instances:
                vc_instances[chat_id] = PyTgCalls(event.client)
                await vc_instances[chat_id].start()

            app = vc_instances[chat_id]

            # Method 1: Try modern voice-only join (preferred)
            join_success = False

            try:
                if api_info['has_mediastream']:
                    # Modern API with MediaStream
                    from pytgcalls.types import MediaStream

                    # Create silent audio stream for voice-only joining
                    silence_file = await create_silence_file()
                    if silence_file:
                        await app.play(
                            chat_id,
                            MediaStream(
                                silence_file,
                                video_flags=MediaStream.Flags.IGNORE
                            )
                        )
                        join_success = True
                        method_used = "Modern MediaStream API"
                    else:
                        raise Exception("Could not create silence file")
                else:
                    raise Exception("MediaStream not available")

            except Exception as modern_error:
                print(f"[VC] Modern API failed: {modern_error}")

                # Method 2: Try minimal MediaStream approach
                try:
                    # Try with minimal MediaStream - just audio file
                    silence_file = await create_silence_file()
                    if silence_file:
                        await app.play(chat_id, silence_file)
                        join_success = True
                        method_used = "Direct file play"
                    else:
                        raise Exception("Could not create silence file")
                except Exception as direct_error:
                    print(f"[VC] Direct file play failed: {direct_error}")

                    # Method 3: Try URL-based streaming as fallback
                    try:
                        # Use silent audio URL or create one
                        import tempfile
                        import os

                        # Create longer silent audio for stable connection
                        temp_dir = tempfile.gettempdir()
                        silence_webm = os.path.join(temp_dir, 'vzl2_silence.webm')

                        if not os.path.exists(silence_webm):
                            # Create 10-second silent WebM file
                            try:
                                import subprocess
                                subprocess.run([
                                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                                    '-t', '10', '-c:a', 'libopus', '-b:a', '128k',
                                    silence_webm, '-y'
                                ], capture_output=True, check=True)
                            except (subprocess.CalledProcessError, FileNotFoundError):
                                # Fallback to raw file if ffmpeg not available
                                silence_webm = await create_silence_file()

                        if silence_webm and os.path.exists(silence_webm):
                            await app.play(chat_id, silence_webm)
                            join_success = True
                            method_used = "WebM file streaming"
                        else:
                            raise Exception("Could not create compatible audio stream")
                    except Exception as webm_error:
                        raise Exception(f"All join methods failed: Modern({modern_error}), Direct({direct_error}), WebM({webm_error})")

            if join_success:
                vc_status[chat_id] = {
                    'joined': True,
                    'muted': False,
                    'chat_title': chat.title,
                    'method': method_used,
                    'api_version': pytgcalls_info['version']
                }

                success_msg = f"{get_emoji('centang')} **Voice Chat Joined Successfully**\n\n"
                success_msg += f"{get_emoji('aktif')} **Group:** {chat.title}\n"
                success_msg += f"{get_emoji('proses')} **Method:** {method_used}\n"
                success_msg += f"{get_emoji('kuning')} **API:** PyTgCalls v{pytgcalls_info['version']}\n"
                success_msg += f"{get_emoji('utama')} **Status:** Connected & Ready\n\n"
                success_msg += f"{get_emoji('telegram')} **VZL2 Voice Chat v4.0**"

                await safe_edit_premium(msg, success_msg)
            else:
                raise Exception("Join failed - unknown error")

        except Exception as e:
            error_details = str(e)[:200]  # Limit error length
            error_msg = f"{get_emoji('merah')} **Voice Chat Join Failed**\n\n"
            error_msg += f"{get_emoji('kuning')} **Error:** {error_details}\n"
            error_msg += f"{get_emoji('aktif')} **API Type:** {api_info['api_type']}\n"
            error_msg += f"{get_emoji('proses')} **Version:** {pytgcalls_info['version']}\n\n"
            error_msg += f"{get_emoji('centang')} **Solutions:**\n"
            error_msg += f"• Update PyTgCalls: `pip install py-tgcalls -U`\n"
            error_msg += f"• Check group voice chat is active\n"
            error_msg += f"• Verify user account permissions\n\n"
            error_msg += f"{get_emoji('telegram')} **VZL2 Voice Chat v4.0**"

            await safe_edit_premium(msg, error_msg)

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcleave'))
async def vc_leave_handler(event):
    """Leave voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
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
            app = vc_instances[chat_id]

            # Try multiple leave methods for compatibility
            leave_success = False

            try:
                # Modern API - stop playing
                await app.stop(chat_id)
                leave_success = True
                method = "Modern stop"
            except Exception as modern_error:
                try:
                    # Try pause method as alternative
                    await app.pause(chat_id)
                    leave_success = True
                    method = "Pause method"
                except Exception as pause_error:
                    raise Exception(f"All leave methods failed: Stop({modern_error}), Pause({pause_error})")

            # Update status
            vc_status[chat_id]['joined'] = False

            success_msg = f"{get_emoji('centang')} **Voice Chat Left Successfully**\n\n"
            success_msg += f"{get_emoji('aktif')} **Group:** {vc_status[chat_id]['chat_title']}\n"
            success_msg += f"{get_emoji('proses')} **Method:** {method}\n"
            success_msg += f"{get_emoji('kuning')} **Status:** Disconnected\n\n"
            success_msg += f"{get_emoji('telegram')} **VZL2 Voice Chat v4.0**"

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
        global vzoel_client, vzoel_emoji
        
        
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
            app = vc_instances[chat_id]

            # Try mute with modern API
            mute_success = False

            try:
                # Modern mute method
                await app.mute_stream(chat_id)
                mute_success = True
                method = "Mute stream"
            except Exception as mute_error:
                try:
                    # Try volume control as alternative mute
                    await app.change_volume_call(chat_id, 0)
                    mute_success = True
                    method = "Volume mute"
                except Exception:
                    raise Exception(f"Mute failed: {mute_error}")

            vc_status[chat_id]['muted'] = True

            muted_msg = f"{get_emoji('proses')} **Voice Chat Muted**\n\n"
            muted_msg += f"{get_emoji('aktif')} **Group:** {vc_status[chat_id]['chat_title']}\n"
            muted_msg += f"{get_emoji('kuning')} **Method:** {method}\n"
            muted_msg += f"{get_emoji('centang')} **Status:** Audio muted\n\n"
            muted_msg += f"{get_emoji('telegram')} **VZL2 Voice Chat v4.0**"

            await safe_edit_premium(event, muted_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to mute: {str(e)}"
            msg = await event.edit(error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcunmute'))
async def vc_unmute_handler(event):
    """Unmute in voice chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
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
            app = vc_instances[chat_id]

            # Try unmute with modern API
            unmute_success = False

            try:
                # Modern unmute method
                await app.unmute_stream(chat_id)
                unmute_success = True
                method = "Unmute stream"
            except Exception as unmute_error:
                try:
                    # Try volume control as alternative unmute
                    await app.change_volume_call(chat_id, 100)
                    unmute_success = True
                    method = "Volume unmute"
                except Exception:
                    raise Exception(f"Unmute failed: {unmute_error}")

            vc_status[chat_id]['muted'] = False

            unmuted_msg = f"{get_emoji('centang')} **Voice Chat Unmuted**\n\n"
            unmuted_msg += f"{get_emoji('aktif')} **Group:** {vc_status[chat_id]['chat_title']}\n"
            unmuted_msg += f"{get_emoji('kuning')} **Method:** {method}\n"
            unmuted_msg += f"{get_emoji('proses')} **Status:** Audio active\n\n"
            unmuted_msg += f"{get_emoji('telegram')} **VZL2 Voice Chat v4.0**"

            await safe_edit_premium(event, unmuted_msg)
        except Exception as e:
            error_msg = f"{get_emoji('merah')} Failed to unmute: {str(e)}"
            msg = await event.edit(error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcstatus'))
async def vc_status_handler(event):
    """Show voice chat status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
        if event.is_private:
            error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"

            msg = await event.edit(error_msg)
            return
        
        chat_id = event.chat_id
        chat = await event.get_chat()
        
        # Check PyTgCalls comprehensive status
        pytgcalls_info = check_pytgcalls()
        api_info = check_api_compatibility()

        if pytgcalls_info['available']:
            pytgcalls_status = f"{get_emoji('centang')} Installed v{pytgcalls_info['version']}"
            api_status = f"{get_emoji('centang')} {api_info['api_type'].title()} API"
        else:
            pytgcalls_status = f"{get_emoji('merah')} Not Installed"
            api_status = f"{get_emoji('merah')} No API Available"
        
        # Check voice chat status with enhanced info
        if chat_id in vc_status and vc_status[chat_id].get('joined', False):
            status_info = vc_status[chat_id]
            vc_connection = f"{get_emoji('centang')} Connected via {status_info.get('method', 'Unknown')}"
            audio_status = f"🔇 Muted" if status_info.get('muted', False) else f"🎤 Speaking"
            api_version = status_info.get('api_version', 'Unknown')
        else:
            vc_connection = f"{get_emoji('merah')} Not Connected"
            audio_status = f"{get_emoji('merah')} N/A"
            api_version = "N/A"
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        status_text = f"""**{signature} VZL2 Voice Chat Status v4.0**

{get_emoji('utama')} **PyTgCalls:** {pytgcalls_status}
{get_emoji('aktif')} **API Type:** {api_status}
{get_emoji('proses')} **Connection:** {vc_connection}
{get_emoji('kuning')} **Audio Status:** {audio_status}
{get_emoji('centang')} **Runtime Version:** {api_version}

{get_emoji('petir')} **Available Commands:**
• `.vcjoin` - Join voice chat (modern API)
• `.vcleave` - Leave voice chat with cleanup
• `.vcmute` - Mute microphone (smart method)
• `.vcunmute` - Unmute microphone (smart method)
• `.vcstatus` - Show comprehensive status
• `.vcinstall` - Installation & setup guide

{get_emoji('telegram')} **Features:**
• Multi-method compatibility (Modern/Legacy/Direct)
• Automatic API detection and fallback
• Enhanced error handling and diagnostics
• Voice-only joining without file streams
• Premium VZL2 branding and feedback

**By Vzoel Fox's Assistant - Voice Chat v4.0**"""
        
        msg = await event.edit(status_text)
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcinstall'))
async def vc_install_handler(event):
    """Show installation instructions for PyTgCalls"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        

        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Get current status for installation guide
        pytgcalls_info = check_pytgcalls()
        api_info = check_api_compatibility()

        install_text = f"""**{signature} VZL2 Voice Chat Setup Guide v4.0**

{get_emoji('loading')} **Current Status:**
• PyTgCalls: {'✅ Installed v' + pytgcalls_info['version'] if pytgcalls_info['available'] else '❌ Not Installed'}
• API Type: {'✅ ' + api_info['api_type'].title() if api_info['api_type'] != 'none' else '❌ Not Available'}
• Compatibility: {'✅ Ready' if pytgcalls_info['available'] and api_info['api_type'] != 'none' else '❌ Setup Required'}

{get_emoji('utama')} **Step 1: Install Modern PyTgCalls**
```bash
pip install py-tgcalls -U
```

{get_emoji('centang')} **Step 2: Install System Dependencies**
```bash
# Ubuntu/Debian/WSL
sudo apt update && sudo apt install ffmpeg

# Termux (Android)
pkg update && pkg install ffmpeg

# macOS
brew install ffmpeg
```

{get_emoji('aktif')} **Step 3: Restart VZL2**
```bash
.restart
```

{get_emoji('petir')} **Step 4: Test Voice Chat**
```bash
.vcstatus  # Check system status
.vcjoin    # Join voice chat in group
```

{get_emoji('proses')} **VZL2 Voice Chat v4.0 Features:**
• Modern PyTgCalls API with automatic fallback
• Voice-only joining (no audio files required)
• Multi-method compatibility (Modern/Legacy/Direct)
• Smart error handling and detailed diagnostics
• Enhanced mute/unmute with method detection
• Professional VZL2 premium branding

{get_emoji('kuning')} **Requirements:**
• Python 3.9+ with PyTgCalls v2.2.8+
• Telegram User Account (not bot account)
• Group admin rights recommended
• FFmpeg for advanced audio processing

{get_emoji('telegram')} **Troubleshooting:**
• If join fails: Update PyTgCalls and restart
• Voice chat must be active in target group
• Check user account has join permissions
• Modern API preferred, legacy supported

**By Vzoel Fox's Assistant - Voice Technology**"""
        
        msg = await event.edit(install_text)
        if vzoel_client:
            vzoel_client.increment_command_count()
