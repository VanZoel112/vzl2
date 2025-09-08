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

# Import from central emoji template (VzoelFox style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

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
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Alive Plugin loaded - 12-phase animation ready")

@events.register(events.NewMessage(pattern=r'\.alive'))
async def alive_handler(event):
    """Advanced alive command with 12-phase animation"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
        
        # Get plugin count for features display  
        plugin_count = 13  # Static count since vzoel_client might not be available
        
        # 12-phase animation with VzoelFox emojis
        animation_phases = [
            f"{get_emoji('loading')} Initializing VzoelFox's Assistant...",
            f"{get_emoji('proses')} Loading premium systems...",
            f"{get_emoji('petir')} Activating power modules...",
            f"{get_emoji('aktif')} Configuring features...",
            f"{get_emoji('telegram')} Establishing connections...",
            f"{get_emoji('kuning')} Running diagnostics...",
            f"{get_emoji('biru')} Checking permissions...",
            f"{get_emoji('merah')} Validating plugins...",
            f"{get_emoji('adder1')} Applying enhancements...",
            f"{get_emoji('adder2')} Finalizing configuration...",
            f"{get_emoji('centang')} System ready...",
            f"{get_emoji('utama')} VzoelFox's Assistant ONLINE!"
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
        random_emoji1 = get_emoji(random.choice(available_emojis))
        random_emoji2 = get_emoji(random.choice(available_emojis))
        
        # Build final alive display with premium emojis
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        alive_display = f"""{get_emoji('utama')} **VzoelFox's Assistant v2**

{get_emoji('centang')} **Founder Userbot** : Vzoel Fox's (Lutpan) {get_emoji('utama')}
{get_emoji('centang')} **Code** : python3, python2
{get_emoji('centang')} **Fitur** : {plugin_count}
{get_emoji('centang')} **Instagram** : vzoel.fox_s
{get_emoji('centang')} **Zone** : Indonesia 🇮🇩

{random_emoji1} **NOTE !!!** :
Jangan diperjualbelikan atau dikomersilkan!
Repo ini hanya untuk pembelajaran dan pengembangan.

{random_emoji2} **©2025 ~ VZOEL FOX'S ASSISTANT**"""
        
        # Display final result
        await safe_edit_premium(msg, alive_display)
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.ainfo'))
async def alive_info_handler(event):
    """Show information about alive command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        alive_info = f"""**{signature} VzoelFox Alive System**

{get_emoji('utama')} **Features:**
• 12-phase animated loading sequence
• Premium emoji integration throughout
• Dynamic plugin count display
• Indonesian flag zone indicator
• Random emoji selection for notices

{get_emoji('centang')} **Animation Phases:**
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

{get_emoji('telegram')} **Display Info:**
• Founder: Vzoel Fox's (Lutpan)
• Programming: Python3, Python2
• Features: Dynamic plugin count
• Social: vzoel.fox_s (Instagram)
• Location: Indonesia 🇮🇩

**By VzoelFox Assistant**"""
        
        
        msg = await event.edit(alive_info)
        await safe_edit_premium(msg, alive_info)
        if vzoel_client:
            vzoel_client.increment_command_count()

