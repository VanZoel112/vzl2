"""
Enhanced Alive Plugin for VzoelFox Userbot - Premium Edition
Fitur: Advanced alive display dengan 12-phase animation dan premium emoji
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Alive System
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

# Plugin Info
PLUGIN_INFO = {
    "name": "alive",
    "version": "3.0.0",
    "description": "Enhanced alive display dengan 12-phase animation dan premium emoji",
    "author": "Founder Userbot: Vzoel Fox's Ltpn",
    "commands": [".alive", ".ainfo"],
    "features": ["12-phase animation", "premium emoji", "system status", "VzoelFox branding"]
}

__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

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
        
        # Start animation with first phase using safe_edit_premium
        await safe_edit_premium(event, animation_phases[0])
        
        # Animate through all 12 phases
        for i in range(1, 12):
            await asyncio.sleep(0.8)  # 0.8 second delay between phases
            await safe_edit_premium(event, animation_phases[i])
        
        # Final delay before showing result
        await asyncio.sleep(1)
        
        # Get random emoji for NOTE section (from premium mapping)
        available_emojis = ['utama', 'centang', 'petir', 'kuning', 'biru', 'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram']
        random_emoji1 = get_emoji(random.choice(available_emojis))
        random_emoji2 = get_emoji(random.choice(available_emojis))
        
        # Build final alive display with premium emojis
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        alive_display = f"""{signature} **VZOEL ASSISTANT**

{get_emoji('centang')} **Founder Userbot** : Vzoel Fox's Ltpn {get_emoji('utama')}
{get_emoji('centang')} **Code** : Python 3.12+ Enhanced
{get_emoji('centang')} **Plugins** : {plugin_count} Premium Modules
{get_emoji('centang')} **Instagram** : vzoel.fox_s
{get_emoji('centang')} **Zone** : Indonesia 🇮🇩

{random_emoji1} **PREMIUM FEATURES** :
• Advanced Premium Emoji System
• VzoelFox Branded Interface
• Enhanced Performance & Stability

{get_emoji('adder2')} **Powered by VzoelFox Technology**
{get_emoji('telegram')} **- 2025 Vzoel Fox's (LTPN)**

{random_emoji2} **©2025 ~ VZOEL FOX'S PREMIUM SYSTEM**"""
        
        # Display final result
        await safe_edit_premium(event, alive_display)
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
        
        # Display alive info with premium emoji support
        await safe_edit_premium(event, alive_info)
        if vzoel_client:
            vzoel_client.increment_command_count()

