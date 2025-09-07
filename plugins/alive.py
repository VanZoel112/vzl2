"""
VzoelFox's Assistant Alive Plugin
Advanced alive display with 12-phase animation
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
import asyncio
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"{signature} Alive Plugin loaded - 12-phase animation ready")

@events.register(events.NewMessage(pattern=r'\.alive'))
async def alive_handler(event):
    """Advanced alive command with 12-phase animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
        
        # Get plugin count for features display
        plugin_count = len(vzoel_client.plugin_manager.plugins) if vzoel_client.plugin_manager else 0
        
        # 12-phase animation sequence
        animation_phases = [
            "Initializing VzoelFox Assistant...",
            "Loading premium components...", 
            "Connecting to VzoelFox servers...",
            "Validating premium emojis...",
            "Scanning installed plugins...",
            "Checking system integrity...",
            "Verifying VzoelFox credentials...",
            "Loading assistant profile...",
            "Preparing display interface...",
            "Finalizing system status...",
            "VzoelFox Assistant ready!",
            "Generating status display..."
        ]
        
        # Start animation with first phase
        msg = await event.edit(animation_phases[0])
        
        # Animate through all 12 phases
        for i in range(1, 12):
            await asyncio.sleep(0.8)  # 0.8 second delay between phases
            await msg.edit(animation_phases[i])
        
        # Final delay before showing result
        await asyncio.sleep(1)
        
        # Get random emoji for NOTE section (from premium mapping)
        available_emojis = ['utama', 'centang', 'petir', 'kuning', 'biru', 'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram']
        random_emoji1 = vzoel_emoji.get_emoji(random.choice(available_emojis))
        random_emoji2 = vzoel_emoji.get_emoji(random.choice(available_emojis))
        
        # Build final alive display exactly as requested
        alive_display = f"""{vzoel_emoji.get_emoji('utama')} **Vzoel Assistant**

{vzoel_emoji.get_emoji('centang')} **Founder Userbot** : Vzoel Fox's (Lutpan) {vzoel_emoji.get_emoji('utama')}
{vzoel_emoji.get_emoji('centang')} **Code** : python3,python2
{vzoel_emoji.get_emoji('centang')} **Fitur** : {plugin_count}
{vzoel_emoji.get_emoji('centang')} **IG** : vzoel.fox_s
{vzoel_emoji.get_emoji('centang')} **Zone** : ID 🇮🇩

{random_emoji1} **NOTE !!!** :
Userbot ini dibuat dengan repo murni oleh Vzoel Fox's..
Bukan hasil fork maupun beli dari seller manapun!!!
Hak cipta sepenuhnya milik Vzoel..

{random_emoji2} **©2025 ~ Vzoel Fox's (LTPN)**"""
        
        # Display final result
        await msg.edit(alive_display)
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.ainfo'))
async def alive_info_handler(event):
    """Show information about alive command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
        
        signature = vzoel_emoji.get_vzoel_signature()
        
        alive_info = f"""**{signature} VzoelFox Alive System**

{vzoel_emoji.get_emoji('utama')} **Features:**
• 12-phase animated loading sequence
• Premium emoji integration throughout
• Dynamic plugin count display
• Indonesian flag zone indicator
• Random emoji selection for notices

{vzoel_emoji.get_emoji('centang')} **Animation Phases:**
1. Initializing VzoelFox Assistant
2. Loading premium components
3. Connecting to VzoelFox servers
4. Validating premium emojis
5. Scanning installed plugins
6. Checking system integrity
7. Verifying VzoelFox credentials
8. Loading assistant profile
9. Preparing display interface
10. Finalizing system status
11. VzoelFox Assistant ready
12. Generating status display

{vzoel_emoji.get_emoji('telegram')} **Display Info:**
• Founder: Vzoel Fox's (Lutpan)
• Programming: Python3, Python2
• Features: Dynamic plugin count
• Social: vzoel.fox_s (Instagram)
• Location: Indonesia 🇮🇩

**By VzoelFox Assistant**"""
        
        await event.edit(alive_info)
        vzoel_client.increment_command_count()

