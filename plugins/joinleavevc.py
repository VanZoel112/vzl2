import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Auto Join/Leave Voice Chat Plugin for Vzoel Fox's Userbot - Premium Clone Edition
Fitur: Otomatis join/leave voice chat untuk clone accounts tanpa menggunakan akun asli
Founder Userbot: Vzoel Fox's Ltpn
Version: 4.0.0 - Advanced Auto Voice Chat System
"""

from telethon import events
import asyncio
import logging
import json
import time
from datetime import datetime, timedelta

# Plugin info
__version__ = "4.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global variables for auto voice chat management
auto_vc_settings = {
    'enabled': False,
    'auto_join_groups': [],
    'auto_leave_delay': 300,  # 5 minutes default
    'clone_mode': True,
    'stealth_mode': True,
    'join_on_activity': True,
    'leave_on_empty': True
}

vc_instances = {}
vc_status = {}
vc_timers = {}

# Settings file path
SETTINGS_FILE = "database/joinleavevc_settings.json"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Auto Join/Leave VC Plugin loaded - Clone mode ready")
    await load_settings()

def check_pytgcalls():
    """Check if PyTgCalls is available"""
    try:
        import pytgcalls
        return True
    except ImportError:
        return False

async def load_settings():
    """Load auto vc settings from file"""
    global auto_vc_settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                auto_vc_settings.update(json.load(f))
    except Exception as e:
        logging.error(f"Failed to load auto vc settings: {e}")

async def save_settings():
    """Save auto vc settings to file"""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(auto_vc_settings, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save auto vc settings: {e}")

async def auto_join_vc(client, chat_id, stealth=True):
    """Auto join voice chat in stealth mode"""
    try:
        if not check_pytgcalls():
            return False

        from pytgcalls import PyTgCalls
        from pytgcalls.types.input_stream import InputAudioStream, InputStream

        # Create PyTgCalls instance if not exists
        if chat_id not in vc_instances:
            vc_instances[chat_id] = PyTgCalls(client)
            await vc_instances[chat_id].start()

        # Join voice chat with blank audio stream (stealth mode)
        await vc_instances[chat_id].join_group_call(
            chat_id,
            InputStream(InputAudioStream()),
            stream_type="blank"
        )

        vc_status[chat_id] = {
            'joined': True,
            'muted': True,  # Always start muted in stealth mode
            'auto_joined': True,
            'join_time': datetime.now(),
            'stealth': stealth
        }

        # Set auto leave timer if enabled
        if auto_vc_settings['auto_leave_delay'] > 0:
            vc_timers[chat_id] = asyncio.create_task(
                auto_leave_timer(client, chat_id, auto_vc_settings['auto_leave_delay'])
            )

        return True
    except Exception as e:
        logging.error(f"Auto join VC failed for {chat_id}: {e}")
        return False

async def auto_leave_vc(client, chat_id, reason="timer"):
    """Auto leave voice chat"""
    try:
        if chat_id in vc_instances and vc_status.get(chat_id, {}).get('joined', False):
            await vc_instances[chat_id].leave_group_call(chat_id)
            vc_status[chat_id]['joined'] = False
            vc_status[chat_id]['leave_reason'] = reason
            vc_status[chat_id]['leave_time'] = datetime.now()

            # Cancel timer if exists
            if chat_id in vc_timers:
                vc_timers[chat_id].cancel()
                del vc_timers[chat_id]

            return True
    except Exception as e:
        logging.error(f"Auto leave VC failed for {chat_id}: {e}")
        return False

async def auto_leave_timer(client, chat_id, delay):
    """Timer for auto leave"""
    try:
        await asyncio.sleep(delay)
        await auto_leave_vc(client, chat_id, "timer")
    except asyncio.CancelledError:
        pass

@events.register(events.NewMessage(pattern=r'\.autojoin\s*(.*)'))
async def auto_join_handler(event):
    """Enable/disable auto join for current group"""
    if event.is_private or not await is_owner(event.client, event.sender_id):
        return

    from client import vzoel_client

    args = event.pattern_match.group(1).strip().lower()

    if event.is_private:
        error_msg = f"{get_emoji('merah')} Auto join only works in groups"
        msg = await event.edit(error_msg)
        return

    chat_id = event.chat_id
    chat = await event.get_chat()

    if args == "on" or args == "enable":
        if chat_id not in auto_vc_settings['auto_join_groups']:
            auto_vc_settings['auto_join_groups'].append(chat_id)
            await save_settings()

        success_msg = f"""{get_emoji('centang')} **Auto Join VC Enabled**

{get_emoji('aktif')} Group: {chat.title}
{get_emoji('utama')} Mode: Stealth Clone
{get_emoji('proses')} Auto leave: {auto_vc_settings['auto_leave_delay']}s"""

        msg = await event.edit(success_msg)

        # Auto join immediately if voice chat is active
        if auto_vc_settings['enabled']:
            await auto_join_vc(event.client, chat_id, stealth=True)

    elif args == "off" or args == "disable":
        if chat_id in auto_vc_settings['auto_join_groups']:
            auto_vc_settings['auto_join_groups'].remove(chat_id)
            await save_settings()

        # Leave if currently joined
        await auto_leave_vc(event.client, chat_id, "disabled")

        success_msg = f"""{get_emoji('kuning')} **Auto Join VC Disabled**

{get_emoji('merah')} Group: {chat.title}
{get_emoji('centang')} Left voice chat"""

        msg = await event.edit(success_msg)
    else:
        status = "enabled" if chat_id in auto_vc_settings['auto_join_groups'] else "disabled"
        vc_conn = "connected" if vc_status.get(chat_id, {}).get('joined', False) else "not connected"

        info_msg = f"""{get_emoji('utama')} **Auto Join VC Status**

{get_emoji('aktif')} Group: {chat.title}
{get_emoji('proses')} Status: {status}
{get_emoji('centang')} VC: {vc_conn}

**Usage:**
• `.autojoin on` - Enable auto join
• `.autojoin off` - Disable auto join"""

        msg = await event.edit(info_msg)

    if vzoel_client:
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.autovc\s*(.*)'))
async def auto_vc_handler(event):
    """Global auto vc settings"""
    if not await is_owner(event.client, event.sender_id):
        return

    from client import vzoel_client

    args = event.pattern_match.group(1).strip().lower()

    if args == "on" or args == "enable":
        auto_vc_settings['enabled'] = True
        await save_settings()

        success_msg = f"""{get_emoji('centang')} **Auto VC System Enabled**

{get_emoji('aktif')} Clone mode: Active
{get_emoji('utama')} Stealth mode: Enabled
{get_emoji('proses')} Auto groups: {len(auto_vc_settings['auto_join_groups'])}
{get_emoji('centang')} Auto leave: {auto_vc_settings['auto_leave_delay']}s"""

        msg = await event.edit(success_msg)

    elif args == "off" or args == "disable":
        auto_vc_settings['enabled'] = False
        await save_settings()

        # Leave all auto-joined VCs
        for chat_id in list(vc_status.keys()):
            if vc_status[chat_id].get('auto_joined', False):
                await auto_leave_vc(event.client, chat_id, "system_disabled")

        success_msg = f"""{get_emoji('kuning')} **Auto VC System Disabled**

{get_emoji('merah')} All auto joins stopped
{get_emoji('centang')} Left all voice chats"""

        msg = await event.edit(success_msg)

    elif args.startswith("delay "):
        try:
            delay = int(args.split()[1])
            auto_vc_settings['auto_leave_delay'] = delay
            await save_settings()

            success_msg = f"""{get_emoji('centang')} **Auto Leave Delay Updated**

{get_emoji('proses')} New delay: {delay} seconds"""

            msg = await event.edit(success_msg)
        except (ValueError, IndexError):
            error_msg = f"{get_emoji('merah')} Invalid delay format. Use: `.autovc delay 300`"
            msg = await event.edit(error_msg)
    else:
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        status = "enabled" if auto_vc_settings['enabled'] else "disabled"

        info_msg = f"""**{signature} Auto VC System**

{get_emoji('aktif')} **Status:** {status}
{get_emoji('utama')} **Clone Mode:** {auto_vc_settings['clone_mode']}
{get_emoji('proses')} **Stealth Mode:** {auto_vc_settings['stealth_mode']}
{get_emoji('centang')} **Auto Groups:** {len(auto_vc_settings['auto_join_groups'])}
{get_emoji('loading')} **Auto Leave:** {auto_vc_settings['auto_leave_delay']}s

**Commands:**
• `.autovc on/off` - Enable/disable system
• `.autovc delay <seconds>` - Set auto leave delay
• `.autojoin on/off` - Enable for current group
• `.vcstatus` - Show detailed status

**Features:**
• Clone account voice chat
• Stealth mode (muted join)
• Auto leave timer
• Group-specific settings

**By Vzoel Fox's Assistant**"""

        msg = await event.edit(info_msg)

    if vzoel_client:
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.joinvc'))
async def manual_join_handler(event):
    """Manual join voice chat with clone mode"""
    if event.is_private or not await is_owner(event.client, event.sender_id):
        return

    from client import vzoel_client

    if event.is_private:
        error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"
        msg = await event.edit(error_msg)
        return

    if not check_pytgcalls():
        error_msg = f"{get_emoji('merah')} PyTgCalls not installed. Use `.vcinstall` for setup"
        msg = await event.edit(error_msg)
        return

    chat_id = event.chat_id

    # Process animation
    process_phases = [
        "Initializing clone mode...",
        "Connecting stealth voice chat...",
        "Preparing silent audio stream...",
        "Joining voice chat in clone mode..."
    ]

    msg = await event.edit(f"{get_emoji('loading')} {process_phases[0]}")

    for i, phase in enumerate(process_phases[1:], 1):
        await asyncio.sleep(0.8)
        await safe_edit_premium(msg, f"{get_emoji('proses')} {phase}")

    success = await auto_join_vc(event.client, chat_id, stealth=True)

    if success:
        success_msg = f"""{get_emoji('centang')} **Voice Chat Joined - Clone Mode**

{get_emoji('aktif')} Mode: Stealth Clone
{get_emoji('utama')} Audio: Muted (Silent)
{get_emoji('proses')} Type: Background Join
{get_emoji('centang')} Status: Connected"""

        await safe_edit_premium(msg, success_msg)
    else:
        error_msg = f"{get_emoji('merah')} Failed to join voice chat in clone mode"
        await safe_edit_premium(msg, error_msg)

    if vzoel_client:
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.leavevc'))
async def manual_leave_handler(event):
    """Manual leave voice chat"""
    if event.is_private or not await is_owner(event.client, event.sender_id):
        return

    from client import vzoel_client

    if event.is_private:
        error_msg = f"{get_emoji('merah')} Voice chat commands only work in groups"
        msg = await event.edit(error_msg)
        return

    chat_id = event.chat_id

    if not vc_status.get(chat_id, {}).get('joined', False):
        not_joined_msg = f"{get_emoji('kuning')} Not currently in voice chat"
        msg = await event.edit(not_joined_msg)
        return

    leaving_msg = f"{get_emoji('loading')} Leaving voice chat..."
    msg = await event.edit(leaving_msg)
    await asyncio.sleep(1)

    success = await auto_leave_vc(event.client, chat_id, "manual")

    if success:
        success_msg = f"{get_emoji('centang')} Left Voice Chat"
        await safe_edit_premium(msg, success_msg)
    else:
        error_msg = f"{get_emoji('merah')} Failed to leave voice chat"
        await safe_edit_premium(msg, error_msg)

    if vzoel_client:
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.vcstatus'))
async def vc_status_handler(event):
    """Show comprehensive voice chat status"""
    if not await is_owner(event.client, event.sender_id):
        return

    from client import vzoel_client

    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"

    # Check if PyTgCalls is available
    pytgcalls_status = f"{get_emoji('centang')} Installed" if check_pytgcalls() else f"{get_emoji('merah')} Not Installed"

    # System status
    system_status = f"{get_emoji('centang')} Enabled" if auto_vc_settings['enabled'] else f"{get_emoji('merah')} Disabled"

    # Count active connections
    active_vcs = sum(1 for status in vc_status.values() if status.get('joined', False))

    # Auto join groups count
    auto_groups = len(auto_vc_settings['auto_join_groups'])

    if not event.is_private:
        chat_id = event.chat_id
        chat = await event.get_chat()

        # Current group VC status
        if chat_id in vc_status and vc_status[chat_id].get('joined', False):
            vc_connection = f"{get_emoji('centang')} Connected"
            join_mode = "Stealth Clone" if vc_status[chat_id].get('stealth', False) else "Normal"
            join_time = vc_status[chat_id].get('join_time', 'Unknown')
        else:
            vc_connection = f"{get_emoji('merah')} Not Connected"
            join_mode = "N/A"
            join_time = "N/A"

        auto_join_enabled = chat_id in auto_vc_settings['auto_join_groups']

        status_text = f"""**{signature} Voice Chat Status**

{get_emoji('utama')} **System Status:**
• PyTgCalls: {pytgcalls_status}
• Auto VC: {system_status}
• Active VCs: {active_vcs}
• Auto Groups: {auto_groups}

{get_emoji('aktif')} **Current Group:**
• Connection: {vc_connection}
• Join Mode: {join_mode}
• Auto Join: {'Enabled' if auto_join_enabled else 'Disabled'}
• Auto Leave: {auto_vc_settings['auto_leave_delay']}s

{get_emoji('centang')} **Commands:**
• `.joinvc` - Join in clone mode
• `.leavevc` - Leave voice chat
• `.autojoin on/off` - Auto join this group
• `.autovc on/off` - Enable/disable system

**By Vzoel Fox's Assistant**"""
    else:
        status_text = f"""**{signature} Voice Chat System**

{get_emoji('utama')} **Global Status:**
• PyTgCalls: {pytgcalls_status}
• Auto VC: {system_status}
• Active VCs: {active_vcs}
• Auto Groups: {auto_groups}
• Auto Leave: {auto_vc_settings['auto_leave_delay']}s

{get_emoji('aktif')} **Features:**
• Clone mode voice chat
• Stealth joining (muted)
• Auto join/leave system
• Group-specific settings

{get_emoji('centang')} **Setup:**
Use `.vcinstall` for installation guide

**By Vzoel Fox's Assistant**"""

    msg = await event.edit(status_text)
    if vzoel_client:
        vzoel_client.increment_command_count()

# Event listeners for auto join functionality
@events.register(events.ChatAction)
async def handle_voice_chat_events(event):
    """Handle voice chat start/end events for auto join"""
    if not auto_vc_settings['enabled']:
        return

    chat_id = event.chat_id

    # Only process if auto join is enabled for this group
    if chat_id not in auto_vc_settings['auto_join_groups']:
        return

    # Voice chat started
    if hasattr(event.action, 'call') and event.action.call:
        if auto_vc_settings['join_on_activity']:
            await asyncio.sleep(2)  # Small delay to ensure VC is ready
            await auto_join_vc(event.client, chat_id, stealth=True)

    # Voice chat ended
    elif hasattr(event.action, 'call') and not event.action.call:
        if auto_vc_settings['leave_on_empty']:
            await auto_leave_vc(event.client, chat_id, "vc_ended")