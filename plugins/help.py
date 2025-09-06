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

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variables for help navigation
help_sessions = {}  # {user_id: {'page': int, 'message': message_obj}}
help_active = {}    # {user_id: True/False}

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"{signature} Help Plugin loaded - Navigation system ready")

def get_plugin_info():
    """Get information about all loaded plugins"""
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
                # Try to import and get plugin info
                plugin_path = f"plugins.{plugin_name}"
                if plugin_path in globals():
                    plugin_module = globals()[plugin_path]
                else:
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
        from emoji_handler import vzoel_emoji
        
        user_id = event.sender_id
        
        # Initialize help session
        help_sessions[user_id] = {'page': 0, 'message': None}
        help_active[user_id] = True
        
        # Get plugin information
        plugins_info = get_plugin_info()
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

{vzoel_emoji.get_emoji('centang')} **Navigation Commands:**
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
    signature = vzoel_emoji.get_vzoel_signature()
    help_content = f"""**{signature} VZOEL ASSISTANT HELP**

{vzoel_emoji.get_emoji('utama')} **Total Plugins:** {total_plugins}
{vzoel_emoji.get_emoji('telegram')} **Total Commands:** {total_commands}
{vzoel_emoji.get_emoji('aktif')} **Page:** {page + 1}/{total_pages}

"""
    
    # Add plugins for current page
    for i, plugin in enumerate(page_plugins, 1):
        plugin_num = start_idx + i
        commands_str = ", ".join(plugin.get('commands', []))
        
        help_content += f"""**{plugin_num}. {plugin['name']}**
{vzoel_emoji.get_emoji('proses')} {plugin['description']}
{vzoel_emoji.get_emoji('centang')} Commands: {commands_str}

"""
    
    # Add footer
    help_content += f"""{vzoel_emoji.get_emoji('petir')} **Navigation:**
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
    
    from emoji_handler import vzoel_emoji
    
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
    
    from emoji_handler import vzoel_emoji
    
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
    
    from emoji_handler import vzoel_emoji
    
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
        from emoji_handler import vzoel_emoji
        
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

{vzoel_emoji.get_emoji('centang')} **Navigation Commands:**
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
        from emoji_handler import vzoel_emoji
        
        plugins_info = get_plugin_info()
        total_plugins = len(plugins_info)
        total_commands = sum(len(plugin.get('commands', [])) for plugin in plugins_info)
        
        current_page = help_sessions[user_id]['page']
        new_page = max(current_page - 1, 0)
        
        if new_page != current_page:
            help_sessions[user_id]['page'] = new_page
            help_msg = await create_help_page(new_page, plugins_info, total_plugins, total_commands, vzoel_emoji)
            
            alternative_help = f"""{help_msg}

{vzoel_emoji.get_emoji('centang')} **Navigation Commands:**
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
        from emoji_handler import vzoel_emoji
        
        # Close help session
        help_active[user_id] = False
        del help_sessions[user_id]
        
        close_msg = vzoel_emoji.format_emoji_response(
            ['centang'], "Help closed. Use .help to open again."
        )
        await event.edit(close_msg)
        vzoel_client.increment_command_count()

# Register handlers
help_handler.handler = help_handler.handler
help_handler.command = ".help"

help_next_handler.handler = help_next_handler.handler
help_next_handler.command = ".next"

help_back_handler.handler = help_back_handler.handler  
help_back_handler.command = ".back"

help_exit_handler.handler = help_exit_handler.handler
help_exit_handler.command = ".exit"