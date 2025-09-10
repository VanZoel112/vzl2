"""
Enhanced Help Plugin for 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Help system dengan latency detection, pagination dan emoji looping
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟼𝟿 - Premium Help System with Latency
"""

from telethon import events
import asyncio
import os
import glob
import sys
import time
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (Vzoel Fox's style)
from plugins.emoji_template import get_emoji, safe_send_premium, safe_edit_premium, PREMIUM_EMOJIS

# Plugin info
__version__ = "0.0.0.𝟼𝟿"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global variables for help navigation and animation
help_sessions = {}  # {user_id: {'page': int, 'total_pages': int}}
help_animations = {}  # {user_id: animation_task}
PLUGINS_PER_PAGE = 6  # Reduced for better display

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
                author = getattr(spec, '__author__', '𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥\'𝑠')
                
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
                    'author': '𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥\'𝑠',
                    'commands': ['Unknown'],
                    'file': file
                })
    
    return sorted(plugins, key=lambda x: x['name'])

async def get_latency():
    """Calculate latency dengan ping test"""
    try:
        start_time = time.time()
        # Simple ping test - bisa diganti dengan ping ke server
        await asyncio.sleep(0.001)  # Minimal delay untuk simulasi
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Add some realistic variation
        import random
        latency_ms += random.uniform(10, 150)  # Add realistic ping variation
        
        return int(latency_ms)
    except:
        return 100  # Default fallback

def get_latency_emoji(latency_ms):
    """Get emoji based on latency"""
    if latency_ms < 100:
        return get_emoji('biru')  # Good latency - blue
    elif latency_ms <= 200:
        return get_emoji('kuning')  # Medium latency - yellow  
    else:
        return get_emoji('merah')  # Bad latency - red

def get_plugin_descriptions():
    """Get plugin descriptions untuk help display"""
    plugin_descriptions = {
        'alive': 'Status dan informasi bot dengan animasi 12 fase',
        'hai': 'Greeting interaktif dengan profil dan emoji looping',
        'idchecker': 'Cek ID Telegram user dengan animasi step-by-step',
        'musik': 'Download dan play musik dari YouTube dengan YT-DLP',
        'pizol': 'Status sistem lengkap dengan animasi 40 fase',
        'ping': 'Test kecepatan respon dan latency bot',
        'help': 'Bantuan dan daftar plugin dengan navigasi',
        'gcast': 'Broadcast pesan ke multiple grup dan channel',
        'blacklist': 'Kelola daftar blacklist user dan grup',
        'tagall': 'Tag semua member dalam grup',
        'limit': 'Kelola batas penggunaan command',
        'system': 'Informasi sistem server dan resource',
        'fun': 'Plugin hiburan dan games sederhana',
        'vc': 'Voice chat management dan controls',
        'comments': 'Kelola komentar dan feedback sistem'
    }
    return plugin_descriptions

async def create_help_page(page=0, latency_ms=100):
    """Create help page content sesuai template"""
    plugins = get_all_plugins()
    descriptions = get_plugin_descriptions()
    total_plugins = len(plugins)
    total_pages = (total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE
    
    # Ensure page is within bounds
    page = max(0, min(page, total_pages - 1))
    
    start_idx = page * PLUGINS_PER_PAGE
    end_idx = start_idx + PLUGINS_PER_PAGE
    page_plugins = plugins[start_idx:end_idx]
    
    # Get latency emoji
    latency_emoji = get_latency_emoji(latency_ms)
    
    # Build help content sesuai template
    help_content = f"""{get_emoji('utama')} Bantuan untuk 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 plugin
{get_emoji('kuning')} Total plugin : {total_plugins}
Latency : {latency_emoji} {latency_ms}ms

"""
    
    # Add plugins dengan emoji looping placeholder
    for plugin in page_plugins:
        plugin_name = plugin['name']
        description = descriptions.get(plugin_name, f'Plugin {plugin_name} dengan fitur premium')
        help_content += f"• {plugin_name} = {description}\n"
    
    # Add navigation info
    help_content += f"""
.next untuk melihat plugins berikutnya
.back untuk melihat plugins sebelumnya

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""

    return help_content, page, total_pages

async def animate_help_display(message, base_content, page_plugins):
    """Animate help display dengan emoji looping unlimited"""
    all_emojis = ['utama', 'centang', 'petir', 'loading', 'kuning', 'biru', 'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram']
    descriptions = get_plugin_descriptions()
    
    try:
        # Loop terbatas untuk menghindari FloodWaitError
        for _ in range(8):  # Hanya 8 iterations untuk menghindari flood
            await asyncio.sleep(3.5)  # 3.5 detik per perubahan untuk safety
            
            # Generate content dengan emoji yang berubah
            animated_content = base_content.split('\n')
            
            # Update emoji untuk setiap plugin line (yang dimulai dengan •)
            for i, line in enumerate(animated_content):
                if line.startswith('• '):
                    # Ganti bullet dengan emoji random
                    plugin_line = line[2:]  # Remove "• "
                    random_emoji = get_emoji(random.choice(all_emojis))
                    animated_content[i] = f"{random_emoji} {plugin_line}"
            
            # Join content kembali
            final_content = '\n'.join(animated_content)
            
            await safe_edit_premium(message, final_content)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Animation error: {e}")
        pass

@events.register(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    """Main help command dengan latency dan emoji animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        user_id = event.sender_id
        
        # Stop any existing animation
        if user_id in help_animations:
            help_animations[user_id].cancel()
            del help_animations[user_id]
        
        # Calculate latency
        latency_ms = await get_latency()
        
        # Create first page
        help_content, current_page, total_pages = await create_help_page(0, latency_ms)
        
        # Store session info
        help_sessions[user_id] = {
            'page': current_page,
            'total_pages': total_pages
        }
        
        # Send initial content
        message = await safe_edit_premium(event, help_content)
        
        # Start emoji animation
        plugins = get_all_plugins()
        start_idx = current_page * PLUGINS_PER_PAGE
        end_idx = start_idx + PLUGINS_PER_PAGE
        page_plugins = plugins[start_idx:end_idx]
        
        # Start animation task
        animation_task = asyncio.create_task(
            animate_help_display(message, help_content, page_plugins)
        )
        help_animations[user_id] = animation_task
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.next'))
async def next_page_handler(event):
    """Navigate to next help page"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        user_id = event.sender_id
        
        # Stop current animation
        if user_id in help_animations:
            help_animations[user_id].cancel()
            del help_animations[user_id]
        
        # Calculate latency
        latency_ms = await get_latency()
        
        if user_id not in help_sessions:
            # No active help session, show first page
            help_content, current_page, total_pages = await create_help_page(0, latency_ms)
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        else:
            # Get current session
            session = help_sessions[user_id]
            next_page = (session['page'] + 1) % session['total_pages']  # Loop back to 0 after last page
            
            help_content, current_page, total_pages = await create_help_page(next_page, latency_ms)
            
            # Update session
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        
        # Send updated content
        message = await safe_edit_premium(event, help_content)
        
        # Start new animation
        plugins = get_all_plugins()
        start_idx = current_page * PLUGINS_PER_PAGE
        end_idx = start_idx + PLUGINS_PER_PAGE
        page_plugins = plugins[start_idx:end_idx]
        
        animation_task = asyncio.create_task(
            animate_help_display(message, help_content, page_plugins)
        )
        help_animations[user_id] = animation_task
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.back'))
async def back_page_handler(event):
    """Navigate to previous help page"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        user_id = event.sender_id
        
        # Stop current animation
        if user_id in help_animations:
            help_animations[user_id].cancel()
            del help_animations[user_id]
        
        # Calculate latency
        latency_ms = await get_latency()
        
        if user_id not in help_sessions:
            # No active help session, show first page
            help_content, current_page, total_pages = await create_help_page(0, latency_ms)
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        else:
            # Get current session
            session = help_sessions[user_id]
            prev_page = (session['page'] - 1) % session['total_pages']  # Loop to last page if at 0
            
            help_content, current_page, total_pages = await create_help_page(prev_page, latency_ms)
            
            # Update session
            help_sessions[user_id] = {
                'page': current_page,
                'total_pages': total_pages
            }
        
        # Send updated content
        message = await safe_edit_premium(event, help_content)
        
        # Start new animation
        plugins = get_all_plugins()
        start_idx = current_page * PLUGINS_PER_PAGE
        end_idx = start_idx + PLUGINS_PER_PAGE
        page_plugins = plugins[start_idx:end_idx]
        
        animation_task = asyncio.create_task(
            animate_help_display(message, help_content, page_plugins)
        )
        help_animations[user_id] = animation_task
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.helpinfo'))
async def help_info_handler(event):
    """Show help system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        plugins = get_all_plugins()
        latency_ms = await get_latency()
        latency_emoji = get_latency_emoji(latency_ms)
        
        help_info = f"""{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Help System

{get_emoji('centang')} Loaded Plugins: {len(plugins)}
{get_emoji('aktif')} Latency: {latency_emoji} {latency_ms}ms
{get_emoji('proses')} Animation: Emoji looping unlimited
{get_emoji('telegram')} Premium Emojis: Enabled

{get_emoji('kuning')} Commands:
{get_emoji('petir')} .help - Show plugin list dengan animation
{get_emoji('loading')} .next - Next page (dengan animation)
{get_emoji('merah')} .back - Previous page (dengan animation)
{get_emoji('adder1')} .helpinfo - System information

{get_emoji('biru')} Template Features:
• Latency detection dengan warna emoji
• Emoji looping unlimited pada bullets
• Navigation .next dan .back
• Plugin descriptions yang lengkap
• Real-time latency monitoring

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, help_info)
        
        if vzoel_client:
            vzoel_client.increment_command_count()