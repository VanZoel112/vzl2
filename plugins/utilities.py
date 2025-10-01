"""
Vzoel Fox's Lutpan - Utilities Plugin
Essential operational tools

Commands:
- .sendlog - Send bot logs to current chat
- .install <package> - Install dependencies from Telegram

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events
import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# Plugin info
PLUGIN_INFO = {
    "name": "utilities",
    "version": "2.0.0",
    "description": "Essential operational tools",
    "author": "Vzoel Fox's",
    "commands": [".sendlog", ".install"],
    "features": ["Log sending", "Package installation", "Remote management"]
}

# Global references
vzoel_client = None
vzoel_emoji = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    print(f"{get_emoji('utama')} Vzoel Fox's Lutpan Utilities loaded")


@events.register(events.NewMessage(pattern=r'\.sendlog'))
async def send_log_handler(event):
    """Send bot logs to current chat"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        # Processing message
        processing_msg = f"""{get_emoji('loading')} READING LOGS

{get_emoji('proses')} Locating log file
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT
By Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, processing_msg)

        # Find log file
        log_files = [
            Path("vzl2.log"),
            Path("bot.log"),
            Path("userbot.log"),
            Path("logs/vzl2.log"),
            Path("logs/latest.log")
        ]

        log_file = None
        for log_path in log_files:
            if log_path.exists():
                log_file = log_path
                break

        if log_file and log_file.exists():
            try:
                # Get file size
                file_size = log_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)

                # Delete processing message
                await event.delete()

                # Send log file
                await event.client.send_file(
                    event.chat_id,
                    str(log_file),
                    caption=f"""{get_emoji('centang')} LOG FILE

{get_emoji('aktif')} File: {log_file.name}
{get_emoji('proses')} Size: {file_size_mb:.2f} MB
{get_emoji('telegram')} Latest system logs

VZOEL ASSISTANT
By Vzoel Fox's Lutpan
~2025 Vzoel Fox's Lutpan"""
                )

            except Exception as e:
                response = f"""{get_emoji('merah')} SEND FAILED

{get_emoji('kuning')} Error: {str(e)[:100]}

VZOEL ASSISTANT
By Vzoel Fox's Lutpan"""

                await event.respond(response)

        else:
            response = f"""{get_emoji('kuning')} LOG FILE NOT FOUND

{get_emoji('telegram')} Possible reasons:
• No logs generated yet
• Logging not configured
• Log file moved or deleted

{get_emoji('aktif')} Check logging configuration

VZOEL ASSISTANT
By Vzoel Fox's Lutpan
~2025 Vzoel Fox's Lutpan"""

            await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.install (.+)'))
async def install_handler(event):
    """Install dependencies from Telegram"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        # Parse command
        args = event.pattern_match.group(1).strip().split()
        if not args:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Usage: .install <package_manager> <package>\n\nVZOEL ASSISTANT\nBy Vzoel Fox's Lutpan")
            return

        # Determine package manager
        if args[0] in ['pip', 'pip3']:
            pm = args[0]
            packages = ' '.join(args[1:])
            install_cmd = [pm, 'install', '--upgrade'] + args[1:]
        elif args[0] in ['npm', 'yarn']:
            pm = args[0]
            packages = ' '.join(args[1:])
            install_cmd = [pm, 'install', '-g'] + args[1:]
        elif args[0] in ['pkg', 'apt', 'apt-get']:
            pm = args[0]
            packages = ' '.join(args[1:])
            install_cmd = [pm, 'install', '-y'] + args[1:]
        else:
            # Default to pip
            pm = 'pip'
            packages = ' '.join(args)
            install_cmd = ['pip', 'install', '--upgrade'] + args

        # Processing message
        processing_msg = f"""{get_emoji('loading')} INSTALLING PACKAGE

{get_emoji('proses')} Manager: {pm}
{get_emoji('telegram')} Package: {packages}
{get_emoji('aktif')} Installing...

VZOEL ASSISTANT
By Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, processing_msg)

        # Run installation
        try:
            result = subprocess.run(
                install_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                # Success
                output_preview = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout

                response = f"""{get_emoji('centang')} INSTALLATION COMPLETE

{get_emoji('aktif')} Manager: {pm}
{get_emoji('proses')} Package: {packages}
{get_emoji('telegram')} Status: Installed successfully

{get_emoji('biru')} Output:
{output_preview}

VZOEL ASSISTANT
By Vzoel Fox's Lutpan
~2025 Vzoel Fox's Lutpan"""

            else:
                # Failed
                error_preview = result.stderr[-500:] if len(result.stderr) > 500 else result.stderr

                response = f"""{get_emoji('merah')} INSTALLATION FAILED

{get_emoji('kuning')} Manager: {pm}
{get_emoji('proses')} Package: {packages}
{get_emoji('aktif')} Return code: {result.returncode}

{get_emoji('telegram')} Error:
{error_preview}

VZOEL ASSISTANT
By Vzoel Fox's Lutpan
~2025 Vzoel Fox's Lutpan"""

        except subprocess.TimeoutExpired:
            response = f"""{get_emoji('merah')} INSTALLATION TIMEOUT

{get_emoji('kuning')} Command took longer than 5 minutes
{get_emoji('telegram')} Try manually or check network

VZOEL ASSISTANT
By Vzoel Fox's Lutpan"""

        except Exception as e:
            response = f"""{get_emoji('merah')} INSTALLATION ERROR

{get_emoji('kuning')} Error: {str(e)[:200]}

VZOEL ASSISTANT
By Vzoel Fox's Lutpan"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
