"""
VzoelFox's Assistant Help Plugin
Comprehensive help system with pagination and navigation
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
from telethon.tl.custom import Button
import asyncio
import math
import importlib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VzoelFox style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variables for help navigation
help_sessions = {}  # {user_id: {'page': int, 'message': message_obj}}
help_active = {}    # {user_id: True/False}
plugin_cache = {}   # Cache for plugin info
cache_timestamp = 0 # Last cache update time

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Help Plugin loaded - Navigation system ready")

def get_plugin_info(force_refresh=False):
    """Get information about all loaded plugins from plugin manager"""
    global plugin_cache, cache_timestamp
    
    # Check cache validity (refresh every 30 seconds or on force)
    current_time = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
    cache_valid = (current_time - cache_timestamp) < 30 and plugin_cache and not force_refresh
    
    if cache_valid:
        return plugin_cache
    
    try:
        # Import client to access plugin manager
        from client import vzoel_client
        
        # Get loaded plugins from plugin manager
        if hasattr(vzoel_client, 'plugin_manager') and vzoel_client.plugin_manager:
            plugins_info = vzoel_client.plugin_manager.get_plugin_list()
            
            # Process plugin info for help display
            processed_plugins = []
            for plugin in plugins_info:
                # Clean up description
                description = plugin.get('description', 'No description')
                if description and isinstance(description, str):
                    # Extract first meaningful line from docstring
                    lines = description.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('"""') and not line.startswith("'''"):
                            description = line[:80] + '...' if len(line) > 80 else line
                            break
                    if not description or description.startswith('"""'):
                        description = f"{plugin['name'].title()} plugin functionality"
                
                processed_plugin = {
                    'name': plugin['name'].title(),
                    'description': description,
                    'commands': plugin.get('commands', [f".{plugin['name']}"]),
                    'file': plugin.get('file', f"{plugin['name']}.py")
                }
                processed_plugins.append(processed_plugin)
            
            # Update cache
            plugin_cache = processed_plugins
            cache_timestamp = current_time
            
            return processed_plugins
        else:
            # Fallback: scan files if plugin manager not available
            fallback_plugins = get_plugin_info_fallback()
            plugin_cache = fallback_plugins
            cache_timestamp = current_time
            return fallback_plugins
            
    except Exception as e:
        # Fallback: scan files manually
        print(f"Error accessing plugin manager: {e}")
        fallback_plugins = get_plugin_info_fallback()
        plugin_cache = fallback_plugins
        cache_timestamp = current_time
        return fallback_plugins

def get_plugin_info_fallback():
    """Fallback method to scan plugin files manually"""
    plugins_info = []
    
    # Get plugin directory
    plugin_dir = "plugins"
    if not os.path.exists(plugin_dir):
        return plugins_info
    
    # Scan all plugin files
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            plugin_name = filename[:-3]  # Remove .py extension
            
            try:
                # Try to load plugin info without full import
                plugin_info = get_plugin_metadata(f"{plugin_dir}/{filename}")
                if plugin_info:
                    plugins_info.append(plugin_info)
                    continue
                
                # Fallback: basic info from filename
                plugins_info.append({
                    'name': plugin_name.title(),
                    'description': f"{plugin_name.title()} plugin functionality",
                    'commands': [f".{plugin_name}"],
                    'file': filename
                })
                
            except Exception as e:
                # Skip problematic plugins
                continue
    
    return plugins_info

def get_plugin_metadata(file_path):
    """Extract plugin metadata from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract plugin info
        plugin_name = os.path.basename(file_path)[:-3].title()
        
        # Try to find description from docstring
        description = "Plugin functionality"
        if '"""' in content:
            docstring_start = content.find('"""')
            docstring_end = content.find('"""', docstring_start + 3)
            if docstring_end != -1:
                docstring = content[docstring_start + 3:docstring_end]
                lines = docstring.strip().split('\n')
                if len(lines) > 1:
                    description = lines[1].strip()
        
        # Extract commands from @events.register patterns
        commands = []
        lines = content.split('\n')
        for line in lines:
            if 'pattern=' in line and 'events.register' in content:
                # Try to extract command pattern
                if 'pattern=r' in line:
                    pattern_start = line.find("'") or line.find('"')
                    if pattern_start != -1:
                        pattern_end = line.find(line[pattern_start], pattern_start + 1)
                        if pattern_end != -1:
                            pattern = line[pattern_start + 1:pattern_end]
                            if pattern.startswith('\\\\'):
                                # Extract command from regex pattern
                                cmd = pattern.split('(')[0].replace('\\\\', '').replace('.', '')
                                if cmd:
                                    commands.append(f".{cmd}")
        
        # If no commands found, use plugin name as command
        if not commands:
            commands = [f".{plugin_name.lower()}"]
        
        return {
            'name': plugin_name,
            'description': description,
            'commands': commands[:3],  # Max 3 commands shown
            'file': os.path.basename(file_path)
        }
        
    except Exception:
        return None

@events.register(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    """Show comprehensive help system with pagination"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        user_id = event.sender_id
        
        # Initialize help session
        help_sessions[user_id] = {'page': 0, 'message': None}
        help_active[user_id] = True
        
        # Get plugin information (force refresh to get latest plugins)
        plugins_info = get_plugin_info(force_refresh=True)
        total_plugins = len(plugins_info)
        
        # Count total commands
        total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
        
        # Create help message
        help_msg = await create_help_page(0, plugins_info, total_plugins, total_commands, vzoel_emoji)
        
        try:
            # Try to create inline buttons (Telegram Bot-like)
            buttons = [
                [Button.inline("◀️ Back", b"help_prev"), Button.inline("Next ▶️", b"help_next")],
                [Button.inline("❌ Close", b"help_close")]
            ]
            
            msg = await event.edit(help_msg, buttons=buttons)
            help_sessions[user_id]['message'] = msg
            
        except Exception:
            # Fallback: Use alternative commands
            alternative_help = f"""{help_msg}

{vzoel_emoji.get_emoji('centang', premium=True)} **Navigation Commands:**
• `.next` - Next page
• `.back` - Previous page  
• `.exit` - Close help

**Use navigation commands while help is active**"""
            
            msg = await event.edit(alternative_help)
            help_sessions[user_id]['message'] = msg
        
        vzoel_client.increment_command_count()

async def create_help_page(page, plugins_info, total_plugins, total_commands, vzoel_emoji):
    """Create help page content"""
    plugins_per_page = 10
    total_pages = math.ceil(len(plugins_info) / plugins_per_page)
    
    # Ensure page is within bounds
    page = max(0, min(page, total_pages - 1))
    
    # Get plugins for current page
    start_idx = page * plugins_per_page
    end_idx = start_idx + plugins_per_page
    page_plugins = plugins_info[start_idx:end_idx]
    
    # Build help header
    signature = vzoel_emoji.get_vzoel_signature(premium=True)
    help_content = f"""**{signature} VZOEL ASSISTANT HELP**

{vzoel_emoji.get_emoji('utama', premium=True)} **Total Plugins:** {total_plugins}
{vzoel_emoji.get_emoji('telegram', premium=True)} **Total Commands:** {total_commands}
{vzoel_emoji.get_emoji('aktif', premium=True)} **Page:** {page + 1}/{total_pages}

"""
    
    # Add plugins for current page
    for i, plugin in enumerate(page_plugins, 1):
        plugin_num = start_idx + i
        commands_str = ", ".join(plugin.get('commands', []))
        
        help_content += f"""**{plugin_num}. {plugin['name']}**
{vzoel_emoji.get_emoji('proses', premium=True)} {plugin['description']}
{vzoel_emoji.get_emoji('centang', premium=True)} Commands: {commands_str}

"""
    
    # Add footer
    help_content += f"""{vzoel_emoji.get_emoji('petir', premium=True)} **Navigation:**
Page {page + 1} of {total_pages} • Use buttons or commands to navigate

**©2025 ~ VzoelFox Assistant Help System**"""
    
    return help_content

@events.register(events.CallbackQuery(data=b'help_next'))
async def help_next_callback(event):
    """Handle next page button"""
    user_id = event.sender_id
    if user_id not in help_sessions or not help_active.get(user_id):
        await event.answer("Help session expired", alert=True)
        return
    
    from emoji_handler_premium import vzoel_emoji
    
    # Get plugin info and update page
    plugins_info = get_plugin_info()
    total_plugins = len(plugins_info)
    total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
    
    plugins_per_page = 10
    total_pages = math.ceil(len(plugins_info) / plugins_per_page)
    
    current_page = help_sessions[user_id]['page']
    new_page = min(current_page + 1, total_pages - 1)
    
    if new_page != current_page:
        help_sessions[user_id]['page'] = new_page
        help_msg = await create_help_page(new_page, plugins_info, total_plugins, total_commands, vzoel_emoji)
        
        buttons = [
            [Button.inline("◀️ Back", b"help_prev"), Button.inline("Next ▶️", b"help_next")],
            [Button.inline("❌ Close", b"help_close")]
        ]
        
        await event.edit(help_msg, buttons=buttons)
        await event.answer()
    else:
        await event.answer("Already at last page")

@events.register(events.CallbackQuery(data=b'help_prev'))
async def help_prev_callback(event):
    """Handle previous page button"""
    user_id = event.sender_id
    if user_id not in help_sessions or not help_active.get(user_id):
        await event.answer("Help session expired", alert=True)
        return
    
    from emoji_handler_premium import vzoel_emoji
    
    # Get plugin info and update page
    plugins_info = get_plugin_info()
    total_plugins = len(plugins_info)
    total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
    
    current_page = help_sessions[user_id]['page']
    new_page = max(current_page - 1, 0)
    
    if new_page != current_page:
        help_sessions[user_id]['page'] = new_page
        help_msg = await create_help_page(new_page, plugins_info, total_plugins, total_commands, vzoel_emoji)
        
        buttons = [
            [Button.inline("◀️ Back", b"help_prev"), Button.inline("Next ▶️", b"help_next")],
            [Button.inline("❌ Close", b"help_close")]
        ]
        
        await event.edit(help_msg, buttons=buttons)
        await event.answer()
    else:
        await event.answer("Already at first page")

@events.register(events.CallbackQuery(data=b'help_close'))
async def help_close_callback(event):
    """Handle close help button"""
    user_id = event.sender_id
    if user_id in help_sessions:
        help_active[user_id] = False
        del help_sessions[user_id]
    
    from emoji_handler_premium import vzoel_emoji
    
    close_msg = vzoel_emoji.format_emoji_response(
        ['centang'], "Help closed. Use .help to open again."
    )
    await event.edit(close_msg)
    await event.answer()

# Alternative navigation commands for fallback
@events.register(events.NewMessage(pattern=r'\.next'))
async def help_next_handler(event):
    """Alternative next command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        user_id = event.sender_id
        
        if user_id not in help_sessions or not help_active.get(user_id):
            return  # Help not active
        
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        # Same logic as callback
        plugins_info = get_plugin_info()
        total_plugins = len(plugins_info)
        total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
        
        plugins_per_page = 10
        total_pages = math.ceil(len(plugins_info) / plugins_per_page)
        
        current_page = help_sessions[user_id]['page']
        new_page = min(current_page + 1, total_pages - 1)
        
        if new_page != current_page:
            help_sessions[user_id]['page'] = new_page
            help_msg = await create_help_page(new_page, plugins_info, total_plugins, total_commands, vzoel_emoji)
            
            alternative_help = f"""{help_msg}

{vzoel_emoji.get_emoji('centang', premium=True)} **Navigation Commands:**
• `.next` - Next page
• `.back` - Previous page  
• `.exit` - Close help"""
            
            await event.edit(alternative_help)
        else:
            await event.edit(vzoel_emoji.format_emoji_response(
                ['kuning'], "Already at last page"
            ))
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.back'))
async def help_back_handler(event):
    """Alternative back command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        user_id = event.sender_id
        
        if user_id not in help_sessions or not help_active.get(user_id):
            return  # Help not active
        
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        plugins_info = get_plugin_info()
        total_plugins = len(plugins_info)
        total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
        
        current_page = help_sessions[user_id]['page']
        new_page = max(current_page - 1, 0)
        
        if new_page != current_page:
            help_sessions[user_id]['page'] = new_page
            help_msg = await create_help_page(new_page, plugins_info, total_plugins, total_commands, vzoel_emoji)
            
            alternative_help = f"""{help_msg}

{vzoel_emoji.get_emoji('centang', premium=True)} **Navigation Commands:**
• `.next` - Next page
• `.back` - Previous page  
• `.exit` - Close help"""
            
            await event.edit(alternative_help)
        else:
            await event.edit(vzoel_emoji.format_emoji_response(
                ['kuning'], "Already at first page"
            ))
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.exit'))
async def help_exit_handler(event):
    """Alternative exit command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        user_id = event.sender_id
        
        if user_id not in help_sessions or not help_active.get(user_id):
            return  # Help not active
        
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        # Close help session
        help_active[user_id] = False
        del help_sessions[user_id]
        
        close_msg = vzoel_emoji.format_emoji_response(
            ['centang'], "Help closed. Use .help to open again."
        )
        await event.edit(close_msg)
        vzoel_client.increment_command_count()

# Register handlers




@events.register(events.NewMessage(pattern=r'\.helprefresh'))
async def help_refresh_handler(event):
    """Refresh help plugin cache to detect new plugins"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        # Force refresh plugin cache
        plugins_info = get_plugin_info(force_refresh=True)
        total_plugins = len(plugins_info)
        total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
        
        refresh_msg = f"""**{vzoel_emoji.get_emoji('centang', premium=True)} HELP CACHE REFRESHED**

{vzoel_emoji.get_emoji('utama', premium=True)} **Plugins Detected:** {total_plugins}
{vzoel_emoji.get_emoji('telegram', premium=True)} **Commands Found:** {total_commands}
{vzoel_emoji.get_emoji('aktif', premium=True)} **Cache Status:** Updated
{vzoel_emoji.get_emoji('proses', premium=True)} **Source:** Plugin Manager

{vzoel_emoji.get_emoji('petir', premium=True)} **Auto-refresh:** Help akan otomatis detect plugin baru setelah .update force atau restart

**Use .help to view updated plugin list**"""
        
        await event.edit(refresh_msg)
        vzoel_client.increment_command_count()

