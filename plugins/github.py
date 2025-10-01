"""
Vzoel Fox's Lutpan - GitHub Integration Plugin
Direct repository management from Telegram

Commands:
- .settoken <token> - Configure GitHub personal access token
- .push [message] - Commit and push changes
- .pull - Pull latest changes with auto-rebase
- .gitstatus - Show repository status

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.git_manager import GitManager

# Plugin info
PLUGIN_INFO = {
    "name": "github",
    "version": "2.0.0",
    "description": "Direct GitHub repository management from Telegram",
    "author": "Vzoel Fox's",
    "commands": [".settoken", ".push", ".pull", ".gitstatus"],
    "features": ["Token management", "Auto-commit", "Auto-rebase", "Conflict detection"]
}

# Global references
vzoel_client = None
vzoel_emoji = None
git_manager = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, git_manager

    vzoel_client = client
    vzoel_emoji = emoji_handler

    # Initialize git manager
    try:
        git_manager = GitManager()
        print(f"{get_emoji('utama')} Vzoel Fox's Lutpan GitHub Integration loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Git manager init error: {e}")


@events.register(events.NewMessage(pattern=r'\.settoken (.+)'))
async def set_token_handler(event):
    """Set GitHub token"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        token = event.pattern_match.group(1).strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} CONFIGURING GITHUB TOKEN

{get_emoji('proses')} Validating token
{get_emoji('telegram')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Delete original message for security
        try:
            await event.delete()
        except:
            pass

        # Set token
        success = git_manager.set_token(token)

        if success:
            response = f"""{get_emoji('centang')} GITHUB TOKEN CONFIGURED

{get_emoji('aktif')} Token saved securely
{get_emoji('telegram')} Ready for push/pull operations

{get_emoji('proses')} Use .push to push changes
{get_emoji('biru')} Use .pull to pull updates

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} TOKEN CONFIGURATION FAILED

{get_emoji('kuning')} Please try again

VZOEL FOX'S LUTPAN"""

        # Send as new message (original deleted)
        await event.respond(response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.push(?: (.+))?'))
async def push_handler(event):
    """Push changes to GitHub"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Get custom message if provided
        custom_message = None
        match = event.pattern_match.group(1)
        if match:
            custom_message = match.strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} PUSHING TO GITHUB

{get_emoji('proses')} Checking repository status
{get_emoji('telegram')} Committing changes
{get_emoji('aktif')} Preparing push

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Push
        success, message = git_manager.push(custom_message)

        if success:
            status = git_manager.get_status()
            response = f"""{get_emoji('centang')} PUSH SUCCESSFUL

{get_emoji('aktif')} Branch: {status['branch']}
{get_emoji('telegram')} Last commit: {status['last_commit']}
{get_emoji('proses')} Changes synced to remote

{get_emoji('biru')} Your code is now on GitHub

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} PUSH FAILED

{get_emoji('kuning')} Error: {message}

{get_emoji('aktif')} Possible solutions:
• Check your GitHub token (.settoken)
• Pull latest changes first (.pull)
• Check repository permissions

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.pull'))
async def pull_handler(event):
    """Pull changes from GitHub"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} PULLING FROM GITHUB

{get_emoji('proses')} Fetching remote changes
{get_emoji('telegram')} Checking for conflicts
{get_emoji('aktif')} Applying updates

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Pull
        success, message = git_manager.pull()

        if success:
            status = git_manager.get_status()
            response = f"""{get_emoji('centang')} PULL SUCCESSFUL

{get_emoji('aktif')} Branch: {status['branch']}
{get_emoji('telegram')} Last commit: {status['last_commit']}
{get_emoji('proses')} Local repository updated

{get_emoji('biru')} Your code is now up to date

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} PULL FAILED

{get_emoji('kuning')} Error: {message}

{get_emoji('aktif')} Possible solutions:
• Check your GitHub token (.settoken)
• Resolve merge conflicts manually
• Check repository permissions

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.gitstatus'))
async def git_status_handler(event):
    """Show repository status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} CHECKING REPOSITORY STATUS

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Get status
        info = git_manager.get_git_info()

        if 'error' in info:
            response = f"""{get_emoji('merah')} STATUS CHECK FAILED

{get_emoji('kuning')} Error: {info['error']}

VZOEL FOX'S LUTPAN"""
        else:
            # Build status message
            has_changes_icon = get_emoji('centang') if info['has_changes'] else get_emoji('kuning')
            changes_status = "Yes" if info['has_changes'] else "No"
            token_status = "Configured" if info['has_token'] else "Not configured"

            response = f"""{get_emoji('utama')} REPOSITORY STATUS

{get_emoji('proses')} BRANCH: {info['branch']}
{get_emoji('telegram')} REMOTE: {info['remote']}
{get_emoji('aktif')} TOTAL COMMITS: {info['total_commits']}

{get_emoji('biru')} CHANGES:
• Modified files: {info['modified']}
• Untracked files: {info['untracked']}
• Has changes: {changes_status}

{get_emoji('kuning')} SYNC STATUS:
• Commits ahead: {info['commits_ahead']}
• Commits behind: {info['commits_behind']}

{get_emoji('centang')} LAST COMMIT:
{info['last_commit']}

{has_changes_icon} GITHUB TOKEN: {token_status}

{get_emoji('adder1')} AVAILABLE COMMANDS:
• .push - Push changes
• .pull - Pull updates
• .settoken - Configure token

VZOEL FOX'S LUTPAN GitHub Integration
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
