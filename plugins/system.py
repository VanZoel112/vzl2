import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
VzoelFox's Assistant System Plugin
Core system commands and update functionality
Created by: Vzoel Fox's
"""

from telethon import events
import asyncio
import subprocess
import sys
import os

# Plugin info
__version__ = "1.0.0"
__author__ = "Vzoel Fox's"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} System Plugin loaded - Update & Stats commands ready")

@events.register(events.NewMessage(pattern=r'\.update(?: (.+))?'))
async def update_handler(event):
    """Manual update command with force option"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        args = event.pattern_match.group(1)
        force = args and args.strip().lower() == 'force'
        
        
        # Show loading
        loading_msg = f"{get_emoji('loading')} Checking for updates..."
        msg = await safe_edit_premium(event, loading_msg)
        
        # Check for updates
        update_info = await vzoel_client.auto_updater.check_for_updates()
        
        if "error" in update_info:
            error_msg = f"{get_emoji('merah')} Update check failed: {update_info['error']}"
            await safe_edit_premium(msg, error_msg)
            return
        
        # If no updates and not force
        if not update_info.get("needs_update", False) and not force:
            up_to_date_msg = f"{get_emoji('centang')} Already up to date!\nCurrent: `{update_info['current_commit']}`"
            await safe_edit_premium(msg, up_to_date_msg)
            return
        
        # Show update progress
        progress_msg = f"{get_emoji('proses')} Updating VzoelFox's Assistant...\n" + \
            (f"Current: `{update_info['current_commit']}`\nLatest: `{update_info['remote_commit']}`" if not force else "Force updating...")
        await safe_edit_premium(msg, progress_msg)
        
        # Perform update
        result = await vzoel_client.auto_updater.perform_update(force=force)
        
        if result.get("status") == "success":
            success_msg = f"{get_emoji('utama')} {get_emoji('centang')} **Update Successful!**\n{result['message']}\n\n⚠️ Restart required to apply changes"
            await safe_edit_premium(msg, success_msg)
        else:
            error_msg = f"{get_emoji('merah')} **Update Failed**\n{result.get('message', 'Unknown error')}"
            await safe_edit_premium(msg, error_msg)

@events.register(events.NewMessage(pattern=r'\.stats'))
async def stats_handler(event):
    """Show assistant statistics"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        stats = vzoel_client.get_stats()
        me = await event.client.get_me()
        
        # Get current git info
        try:
            git_result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h - %s'], 
                                      capture_output=True, text=True, cwd=os.getcwd())
            current_commit = git_result.stdout.strip() if git_result.returncode == 0 else "Unknown"
        except:
            current_commit = "Unknown"
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        stats_text = f"""**{signature} VzoelFox's Assistant Stats**

👤 **User:** {me.first_name}
🆔 **ID:** `{me.id}`
⏱ **Uptime:** {stats['uptime_formatted']}
📊 **Commands:** {stats['commands_executed']}
🔌 **Plugins:** {stats['plugins_loaded']}
📝 **Version:** {current_commit}
🎚 **Status:** {'🟢 Running' if stats['is_running'] else '🔴 Stopped'}

**© Vzoel Fox's - Enhanced Assistant**"""
        
        await safe_edit_premium(event, stats_text)

@events.register(events.NewMessage(pattern=r'\.plugins'))
async def plugins_handler(event):
    """List loaded plugins"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        plugin_list = vzoel_client.plugin_manager.get_plugin_list()
        
        if not plugin_list:
            no_plugins_msg = f"{get_emoji('kuning')} No plugins loaded"
            await safe_edit_premium(event, no_plugins_msg)
            return
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        plugins_text = f"**{signature} Loaded Plugins ({len(plugin_list)})**\n\n"
        
        for plugin in plugin_list:
            description = plugin['description'].split('\n')[0] if plugin['description'] else 'No description'
            commands = ', '.join([f"`{cmd}`" for cmd in plugin['commands']]) if plugin['commands'] else 'No commands'
            
            plugins_text += f"🔌 **{plugin['name']}**\n"
            plugins_text += f"📄 {description[:50]}{'...' if len(description) > 50 else ''}\n"
            plugins_text += f"⚡ {commands}\n\n"
        
        plugins_text += "**© VzoelFox's Plugin System**"
        
        await safe_edit_premium(event, plugins_text)

@events.register(events.NewMessage(pattern=r'\.restart'))
async def restart_handler(event):
    """Restart the assistant"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client

        
        restart_msg = f"{get_emoji('loading')} Restarting VzoelFox's Assistant..."
        await safe_edit_premium(event, restart_msg)
        
        # Stop client gracefully
        await vzoel_client.stop()
        
        # Restart process
        os.execv(sys.executable, ['python'] + sys.argv)
