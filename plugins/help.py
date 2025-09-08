"""
Enhanced Help Plugin for VzoelFox Userbot - Premium Edition
Fitur: Simple help system dengan premium emoji dan navigation
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Help System
"""

from telethon import events
import asyncio
import os
import glob
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VzoelFox style)
from plugins.emoji_template import get_emoji, safe_send_premium, safe_edit_premium, PREMIUM_EMOJIS

# Plugin info
__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global variables for help navigation
help_sessions = {}  # {user_id: {'page': int, 'total_pages': int}}
PLUGINS_PER_PAGE = 8

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Help Plugin loaded - Simple navigation ready")

def get_all_plugins():
    """Get all plugin files and their info"""
    plugins = []
    plugin_dir = "plugins"
    
    if os.path.exists(plugin_dir):
        for file in glob.glob(f"{plugin_dir}/*.py"):
            if file.endswith('__init__.py') or file.endswith('emoji_template.py'):
                continue
                
            plugin_name = os.path.basename(file)[:-3]  # Remove .py extension
            
            # Try to get plugin info
            try:
                spec = __import__(f'plugins.{plugin_name}', fromlist=['__version__', '__author__'])
                version = getattr(spec, '__version__', 'Unknown')
                author = getattr(spec, '__author__', 'VzoelFox')
                
                # Get commands by looking for @events.register patterns
                commands = []
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        import re
                        patterns = re.findall(r'pattern=r["\']\\\.([^"\']+)["\']', content)
                        commands = [f'.{cmd}' for cmd in patterns]
                except:
                    commands = ['Unknown']
                
                plugins.append({
                    'name': plugin_name,
                    'version': version,
                    'author': author,
                    'commands': commands[:3],  # Show max 3 commands
                    'file': file
                })
            except:
                plugins.append({
                    'name': plugin_name,
                    'version': 'Unknown',
                    'author': 'VzoelFox',
                    'commands': ['Unknown'],
                    'file': file
                })
    
    return sorted(plugins, key=lambda x: x['name'])

def create_help_page(page=0):
    """Create help page content"""
    plugins = get_all_plugins()
    total_plugins = len(plugins)
    total_pages = (total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE
    
    # Ensure page is within bounds
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * PLUGINS_PER_PAGE
    end_idx = start_idx + PLUGINS_PER_PAGE
    page_plugins = plugins[start_idx:end_idx]
    
    # Build help header with premium emojis
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    
    help_content = f"""{signature} **VZOEL ASSISTANT HELP**

{get_emoji('utama')} **Total Plugins:** {total_plugins}
{get_emoji('telegram')} **Page:** {page + 1}/{total_pages}
{get_emoji('aktif')} **Navigation:** .next for next page

"""
    
    # Add plugins for current page
    for i, plugin in enumerate(page_plugins, 1):
        plugin_num = start_idx + i
        commands_str = ', '.join(plugin['commands']) if plugin['commands'] else 'No commands'
        
        help_content += f"{get_emoji('centang')} **{plugin_num}. {plugin['name'].title()}**\\n"
        help_content += f"{get_emoji('proses')} Version: {plugin['version']}\\n"  
        help_content += f"{get_emoji('kuning')} Commands: {commands_str}\\n\\n"
    
    # Add footer
    help_content += f"""
{get_emoji('telegram')} **Navigation Commands:**
{get_emoji('petir')} .next - Next page
{get_emoji('loading')} .help - Refresh help

{get_emoji('adder1')} **Created by VzoelFox's Assistant**
{get_emoji('adder2')} **Enhanced by Vzoel Fox's Ltpn**"""

    return help_content, page, total_pages

@events.register(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    """Main help command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        user_id = event.sender_id
        
        # Create first page
        help_content, current_page, total_pages = create_help_page(0)
        
        # Store session info
        help_sessions[user_id] = {
            'page': current_page,
            'total_pages': total_pages
        }
        
        await safe_edit_premium(event, help_content)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.next'))
async def next_page_handler(event):
    """Navigate to next help page"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        user_id = event.sender_id
        
        if user_id not in help_sessions:
            # No active help session, show first page
            help_content, current_page, total_pages = create_help_page(0)
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        else:
            # Get current session
            session = help_sessions[user_id]
            next_page = (session['page'] + 1) % session['total_pages']  # Loop back to 0 after last page
            
            help_content, current_page, total_pages = create_help_page(next_page)
            
            # Update session
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        
        await safe_edit_premium(event, help_content)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.helpinfo'))
async def help_info_handler(event):
    """Show help system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        plugins = get_all_plugins()
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        help_info = f"""{signature} **VzoelFox Help System**

{get_emoji('utama')} **System Status:**
{get_emoji('centang')} Loaded Plugins: {len(plugins)}
{get_emoji('aktif')} Navigation: Simple (.next only)
{get_emoji('proses')} Auto-refresh: Every .help call
{get_emoji('telegram')} Premium Emojis: Enabled

{get_emoji('kuning')} **Commands:**
{get_emoji('petir')} .help - Show plugin list
{get_emoji('loading')} .next - Next page (loops)
{get_emoji('adder1')} .helpinfo - This information

{get_emoji('biru')} **Features:**
• Simple navigation without buttons
• Auto-discovery of all plugins
• Real-time command detection
• Premium emoji integration
• Auto-updating plugin list

{get_emoji('adder2')} **By VzoelFox Assistant**"""
        
        await safe_edit_premium(event, help_info)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Auto-register event handlers
def register_handlers(client):
    """Register all event handlers"""
    client.add_event_handler(help_handler)
    client.add_event_handler(next_page_handler) 
    client.add_event_handler(help_info_handler)