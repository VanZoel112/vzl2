#!/usr/bin/env python3
"""
Simple Help Plugin for VzoelFox Userbot - Direct Plugin List with Premium Emojis
Fitur: 10 plugins per page, .next/.back navigation, detailed plugin info
Founder Userbot: Vzoel Fox's Ltpn 🤩
Version: 4.0.0 - Simple Template System
"""

import os
import glob
from telethon import events
from telethon.tl.types import MessageEntityCustomEmoji

# Font helper tidak diperlukan - removed unused import

# ===== Plugin Info =====
PLUGIN_INFO = {
    "name": "help",
    "version": "4.0.0", 
    "description": "Simple help system - 10 plugins per page dengan premium emoji support",
    "author": "Founder Userbot: Vzoel Fox's Ltpn 🤩",
    "commands": [".help", ".next", ".back", ".help <plugin>"],
    "features": ["simple template", "10 plugins per page", "premium emoji integration", "plugin details"]
}

# ===== PREMIUM EMOJI CONFIGURATION =====
PREMIUM_EMOJIS = {
    'main': {'id': '6156784006194009426', 'char': '🤩'},
    'check': {'id': '5794353925360457382', 'char': '⚙️'},
    'adder1': {'id': '5794407002566300853', 'char': '⛈'},
    'adder2': {'id': '5793913811471700779', 'char': '✅'},
    'adder3': {'id': '5321412209992033736', 'char': '👽'},
    'adder4': {'id': '5793973133559993740', 'char': '✈️'},
    'adder5': {'id': '5357404860566235955', 'char': '😈'},
    'adder6': {'id': '5794323465452394551', 'char': '🎚️'}
}

# Global navigation state
HELP_STATE = {
    'current_page': 0,
    'plugins_per_page': 10
}

def get_emoji(emoji_type):
    """Get premium emoji character"""
    return PREMIUM_EMOJIS.get(emoji_type, {}).get('char', '🤩')

def create_premium_entities(text):
    """Create premium emoji entities for text with UTF-16 support"""
    try:
        entities = []
        current_offset = 0
        i = 0
        
        while i < len(text):
            found_emoji = False
            
            for emoji_type, emoji_data in PREMIUM_EMOJIS.items():
                emoji_char = emoji_data['char']
                emoji_id = emoji_data['id']
                
                if text[i:].startswith(emoji_char):
                    try:
                        emoji_bytes = emoji_char.encode('utf-16-le')
                        utf16_length = len(emoji_bytes) // 2
                        
                        entities.append(MessageEntityCustomEmoji(
                            offset=current_offset,
                            length=utf16_length,
                            document_id=int(emoji_id)
                        ))
                        
                        i += len(emoji_char)
                        current_offset += utf16_length
                        found_emoji = True
                        break
                        
                    except Exception:
                        break
            
            if not found_emoji:
                char = text[i]
                char_bytes = char.encode('utf-16-le')
                char_utf16_length = len(char_bytes) // 2
                current_offset += char_utf16_length
                i += 1
        
        return entities
    except Exception:
        return []

async def safe_send_premium(event, text):
    """Send message with premium entities"""
    try:
        entities = create_premium_entities(text)
        if entities:
            return await event.reply(text, formatting_entities=entities)
        else:
            return await event.reply(text)
    except Exception as e:
        # Fallback to plain text if premium emoji fails
        print(f"[Help] Premium emoji error: {e}")
        return await event.reply(text)

def get_all_plugins():
    """Get all plugin files from plugins directory"""
    try:
        plugin_files = glob.glob("plugins/*.py")
        plugins = []
        
        for plugin_file in plugin_files:
            plugin_name = os.path.basename(plugin_file).replace('.py', '')
            if plugin_name not in ['__init__', 'database_helper', 'nsfw_downloader']:
                plugins.append(plugin_name)
        
        return sorted(plugins)
    except Exception:
        return []

def get_plugin_info_from_file(plugin_name):
    """Get plugin info from file if available"""
    try:
        import importlib
        import sys
        
        # Add plugins to path
        if 'plugins' not in sys.path:
            sys.path.append('plugins')
            
        plugin_module = importlib.import_module(plugin_name)
        
        if hasattr(plugin_module, 'get_plugin_info'):
            return plugin_module.get_plugin_info()
        elif hasattr(plugin_module, 'PLUGIN_INFO'):
            return plugin_module.PLUGIN_INFO
        else:
            return {
                'name': plugin_name,
                'description': 'Plugin deskripsi tidak tersedia',
                'commands': ['Lihat source code untuk commands']
            }
    except Exception:
        return {
            'name': plugin_name,
            'description': 'Plugin tidak dapat dimuat',
            'commands': ['Error loading plugin']
        }

def get_help_page(page=0):
    """Generate help page with 10 plugins per page showing their commands"""
    all_plugins = get_all_plugins()

    # Add core plugins to the list
    all_plugins.insert(0, 'core')

    plugins_per_page = HELP_STATE['plugins_per_page']
    start_idx = page * plugins_per_page
    end_idx = start_idx + plugins_per_page
    page_plugins = all_plugins[start_idx:end_idx]

    total_plugins = len(all_plugins)
    total_pages = (total_plugins - 1) // plugins_per_page + 1

    help_text = f"""{get_emoji('main')} {convert_font('VZOELFOX PLUGINS', 'bold')} (Page {page + 1}/{total_pages})

{get_emoji('check')} {convert_font('Total Plugins:', 'bold')} {total_plugins}
{get_emoji('adder4')} {convert_font('Page:', 'bold')} {page + 1} of {total_pages}

"""

    for idx, plugin_name in enumerate(page_plugins, start_idx + 1):
        if plugin_name == 'core':
            # Handle core commands
            core_commands = ['.alive', '.ping', '.restart', '.plugins']
            help_text += f"{get_emoji('adder2')} {convert_font(f'{idx}.', 'bold')} {convert_font('core', 'mono')}\n"
            help_text += f"   └ Commands: {convert_font(', '.join(core_commands), 'mono')}\n"
            help_text += f"   └ Core userbot functions\n\n"
        else:
            # Handle plugin commands
            plugin_info = get_plugin_info_from_file(plugin_name)
            commands = plugin_info.get('commands', [])
            description = plugin_info.get('description', 'No description')[:50]

            help_text += f"{get_emoji('adder2')} {convert_font(f'{idx}.', 'bold')} {convert_font(plugin_name, 'mono')}\n"

            if commands:
                # Show commands in a more compact format
                if len(commands) <= 3:
                    help_text += f"   └ Commands: {convert_font(', '.join(commands), 'mono')}\n"
                else:
                    help_text += f"   └ Commands: {convert_font(', '.join(commands[:3]), 'mono')} + {len(commands)-3} more\n"
            else:
                help_text += f"   └ Commands: {convert_font('See plugin for details', 'mono')}\n"

            help_text += f"   └ {description}\n\n"

    help_text += f"{get_emoji('adder6')} {convert_font('Navigation:', 'bold')}\n"
    if page > 0:
        help_text += f"{get_emoji('adder1')} {convert_font('.back', 'mono')} - Previous page\n"
    if page < total_pages - 1:
        help_text += f"{get_emoji('adder1')} {convert_font('.next', 'mono')} - Next page\n"

    help_text += f"{get_emoji('adder3')} {convert_font('.help <plugin>', 'mono')} - Plugin details\n"
    help_text += f"\n{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}\n"
    help_text += f"{get_emoji('adder5')} Powered by Vzoel Fox's Technology\n"
    help_text += f"{get_emoji('adder6')} - 2025 Vzoel Fox's (LTPN)"

    return help_text

def get_plugin_details(plugin_name):
    """Get detailed plugin information"""
    plugin_info = get_plugin_info_from_file(plugin_name)
    
    help_text = f"""{get_emoji('main')} {convert_font(f'PLUGIN: {plugin_name.upper()}', 'bold')}

{get_emoji('check')} {convert_font('Description:', 'bold')}
{plugin_info.get('description', 'Tidak ada deskripsi')}

{get_emoji('adder2')} {convert_font('Commands:', 'bold')}
"""
    
    commands = plugin_info.get('commands', [])
    if commands:
        for cmd in commands:
            help_text += f"{get_emoji('adder4')} {convert_font(cmd, 'mono')}\n"
    else:
        help_text += f"{get_emoji('adder5')} Tidak ada commands tersedia\n"
    
    if 'features' in plugin_info:
        help_text += f"\n{get_emoji('adder3')} {convert_font('Features:', 'bold')}\n"
        for feature in plugin_info['features']:
            help_text += f"{get_emoji('adder6')} {feature}\n"
    
    if 'author' in plugin_info:
        help_text += f"\n{get_emoji('main')} {convert_font('Author:', 'bold')} {plugin_info['author']}\n"
    
    if 'version' in plugin_info:
        help_text += f"{get_emoji('check')} {convert_font('Version:', 'bold')} {plugin_info['version']}\n"
    
    help_text += f"\n{get_emoji('adder1')} {convert_font('.help', 'mono')} - Back to main help\n"
    help_text += f"\n{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}\n"
    help_text += f"{get_emoji('adder5')} Powered by Vzoel Fox's Technology\n"
    help_text += f"{get_emoji('adder6')} - 2025 Vzoel Fox's (LTPN)"
    
    return help_text

async def is_owner_check(client, user_id):
    """Check if user is bot owner"""
    try:
        owner_id = os.getenv("OWNER_ID")
        if owner_id:
            return user_id == int(owner_id)
        me = await client.get_me()
        return user_id == me.id
    except Exception:
        return False

# Global client reference
client = None

async def help_handler(event):
    """Main help command handler"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return
    
    try:
        args = event.text.split(maxsplit=1)
        
        if len(args) > 1:
            # Show specific plugin details
            plugin_name = args[1].strip().lower()
            all_plugins = get_all_plugins()
            
            if plugin_name in all_plugins:
                help_text = get_plugin_details(plugin_name)
                await safe_send_premium(event, help_text)
                return
            else:
                error_text = f"""{get_emoji('adder5')} {convert_font('Plugin tidak ditemukan:', 'bold')} {convert_font(plugin_name, 'mono')}

{get_emoji('adder3')} {convert_font('Available plugins:', 'bold')}
{', '.join([convert_font(p, 'mono') for p in all_plugins[:10]])}...

{get_emoji('adder1')} {convert_font('.help', 'mono')} - Show all plugins

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}"""
                await safe_send_premium(event, error_text)
                return
        
        # Reset to page 0 and show main help
        HELP_STATE['current_page'] = 0
        help_text = get_help_page(0)
        await safe_send_premium(event, help_text)
        
    except Exception as e:
        error_text = f"""{get_emoji('adder5')} {convert_font('Help error:', 'bold')} {str(e)}

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}
{get_emoji('adder6')} - 2025 Vzoel Fox's (LTPN)"""
        await safe_send_premium(event, error_text)

async def next_handler(event):
    """Handle .next command for pagination"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    try:
        all_plugins = get_all_plugins()
        # Add core to total count
        total_plugins = len(all_plugins) + 1  # +1 for core
        plugins_per_page = HELP_STATE['plugins_per_page']
        total_pages = (total_plugins - 1) // plugins_per_page + 1
        current_page = HELP_STATE['current_page']

        if current_page < total_pages - 1:
            HELP_STATE['current_page'] = current_page + 1
            help_text = get_help_page(HELP_STATE['current_page'])
            await safe_send_premium(event, help_text)
        else:
            error_text = f"""{get_emoji('adder5')} {convert_font('Already at last page!', 'bold')}

{get_emoji('check')} Current page: {current_page + 1}/{total_pages}
{get_emoji('adder1')} {convert_font('.back', 'mono')} - Previous page
{get_emoji('adder3')} {convert_font('.help', 'mono')} - First page

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}"""
            await safe_send_premium(event, error_text)

    except Exception as e:
        error_text = f"""{get_emoji('adder5')} {convert_font('Next error:', 'bold')} {str(e)}

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}"""
        await safe_send_premium(event, error_text)

async def back_handler(event):
    """Handle .back command for navigation"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return
    
    try:
        current_page = HELP_STATE['current_page']
        
        if current_page > 0:
            HELP_STATE['current_page'] = current_page - 1
            help_text = get_help_page(HELP_STATE['current_page'])
            await safe_send_premium(event, help_text)
        else:
            error_text = f"""{get_emoji('adder5')} {convert_font('Already at first page!', 'bold')}

{get_emoji('check')} Current page: 1
{get_emoji('adder1')} {convert_font('.next', 'mono')} - Next page
{get_emoji('adder3')} {convert_font('.help <plugin>', 'mono')} - Plugin details

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}"""
            await safe_send_premium(event, error_text)
        
    except Exception as e:
        error_text = f"""{get_emoji('adder5')} {convert_font('Back error:', 'bold')} {str(e)}

{get_emoji('main')} {convert_font('VzoelFox Premium System', 'bold')}"""
        await safe_send_premium(event, error_text)

def get_plugin_info():
    return PLUGIN_INFO

def setup(client_instance):
    """Setup function untuk register event handlers"""
    global client
    client = client_instance
    
    client.add_event_handler(help_handler, events.NewMessage(pattern=r'\.help(?:\s+(.+))?$'))
    client.add_event_handler(next_handler, events.NewMessage(pattern=r'\.next$'))
    client.add_event_handler(back_handler, events.NewMessage(pattern=r'\.back$'))
    
    print(f"✅ [Help] Simple template system loaded v{PLUGIN_INFO['version']} - 10 plugins per page")

def cleanup_plugin():
    """Cleanup plugin resources"""
    global client
    try:
        print("[Help] Plugin cleanup initiated")
        client = None
        print("[Help] Plugin cleanup completed")
    except Exception as e:
        print(f"[Help] Cleanup error: {e}")

# Export functions
__all__ = ['setup', 'cleanup_plugin', 'get_plugin_info', 'help_handler', 'next_handler', 'back_handler']