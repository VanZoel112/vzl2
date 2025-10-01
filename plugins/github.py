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
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        token = event.pattern_match.group(1).strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Configuring GitHub token**

{get_emoji('proses')} Validating token
{get_emoji('telegram')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Delete original message for security
        try:
            await event.delete()
        except:
            pass

        # Set token
        success = git_manager.set_token(token)

        if success:
            response = f"""{get_emoji('centang')} **GitHub token configured**

{get_emoji('aktif')} Token saved securely
{get_emoji('telegram')} Ready for push/pull operations

{get_emoji('proses')} Use .push to push changes
{get_emoji('biru')} Use .pull to pull updates

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} **Token configuration failed**

{get_emoji('kuning')} Please try again

**Vzoel Fox's Lutpan**"""

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
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Get custom message if provided
        custom_message = None
        match = event.pattern_match.group(1)
        if match:
            custom_message = match.strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Pushing to GitHub**

{get_emoji('proses')} Checking repository status
{get_emoji('telegram')} Committing changes
{get_emoji('aktif')} Preparing push

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Push
        success, message = git_manager.push(custom_message)

        if success:
            status = git_manager.get_status()
            response = f"""{get_emoji('centang')} **Push successful**

{get_emoji('aktif')} Branch: {status['branch']}
{get_emoji('telegram')} Last commit: {status['last_commit']}
{get_emoji('proses')} Changes synced to remote

{get_emoji('biru')} Your code is now on GitHub

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} **Push failed**

{get_emoji('kuning')} Error: {message}

{get_emoji('aktif')} Possible solutions:
• Check your GitHub token (.settoken)
• Pull latest changes first (.pull)
• Check repository permissions

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.pull'))
async def pull_handler(event):
    """Pull changes from GitHub"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Pulling from GitHub**

{get_emoji('proses')} Fetching remote changes
{get_emoji('telegram')} Checking for conflicts
{get_emoji('aktif')} Applying updates

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Pull
        success, message = git_manager.pull()

        if success:
            status = git_manager.get_status()
            response = f"""{get_emoji('centang')} **Pull successful**

{get_emoji('aktif')} Branch: {status['branch']}
{get_emoji('telegram')} Last commit: {status['last_commit']}
{get_emoji('proses')} Local repository updated

{get_emoji('biru')} Your code is now up to date

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} **Pull failed**

{get_emoji('kuning')} Error: {message}

{get_emoji('aktif')} Possible solutions:
• Check your GitHub token (.settoken)
• Resolve merge conflicts manually
• Check repository permissions

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.gitstatus'))
async def git_status_handler(event):
    """Show repository status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, git_manager

        if not git_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Git manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Checking repository status**

{get_emoji('proses')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Get status
        info = git_manager.get_git_info()

        if 'error' in info:
            response = f"""{get_emoji('merah')} **Status check failed**

{get_emoji('kuning')} Error: {info['error']}

**Vzoel Fox's Lutpan**"""
        else:
            # Build status message
            has_changes_icon = get_emoji('centang') if info['has_changes'] else get_emoji('kuning')
            changes_status = "Yes" if info['has_changes'] else "No"
            token_status = "Configured" if info['has_token'] else "Not configured"

            response = f"""{get_emoji('utama')} **Repository Status**

{get_emoji('proses')} **Branch:** {info['branch']}
{get_emoji('telegram')} **Remote:** {info['remote']}
{get_emoji('aktif')} **Total commits:** {info['total_commits']}

{get_emoji('biru')} **Changes:**
• Modified files: {info['modified']}
• Untracked files: {info['untracked']}
• Has changes: {changes_status}

{get_emoji('kuning')} **Sync Status:**
• Commits ahead: {info['commits_ahead']}
• Commits behind: {info['commits_behind']}

{get_emoji('centang')} **Last Commit:**
{info['last_commit']}

{has_changes_icon} **GitHub Token:** {token_status}

{get_emoji('adder1')} **Available Commands:**
• .push - Push changes
• .pull - Pull updates
• .settoken - Configure token

**Vzoel Fox's Lutpan** GitHub Integration
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
