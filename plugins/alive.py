"""
Enhanced Alive Plugin for 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Advanced alive display dengan 12-phase animation dan premium emoji
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟼𝟿 - Premium Alive System
"""

from telethon import events
import asyncio
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (Vzoel Fox's style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "alive",
    "version": "0.0.0.𝟼𝟿",
    "description": "Enhanced alive display dengan 12-phase animation dan premium emoji",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".alive", ".ainfo"],
    "features": ["12-phase animation", "premium emoji", "system status", "Vzoel Fox's branding"]
}

__version__ = "0.0.0.𝟼𝟿"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

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
        
        # 12-phase animation with Vzoel Fox's emojis
        animation_phases = [
            f"{get_emoji('loading')} Initializing Vzoel Fox's's Assistant...",
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
            f"{get_emoji('utama')} Vzoel Fox's's Assistant ONLINE!"
        ]
        
        # Start animation with first phase using safe_edit_premium
        await safe_edit_premium(event, animation_phases[0])
        
        # Animate through reduced phases to prevent flood wait
        for i in range(1, 7):  # Reduced from 12 to 7 phases
            await asyncio.sleep(3.0)  # Increased from 0.8s to 3.0s delay
            await safe_edit_premium(event, animation_phases[i])
        
        # Final delay before showing result
        await asyncio.sleep(1)
        
        # Get random emoji for NOTE section (from premium mapping)
        available_emojis = ['utama', 'centang', 'petir', 'kuning', 'biru', 'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram']
        random_emoji1 = get_emoji(random.choice(available_emojis))
        random_emoji2 = get_emoji(random.choice(available_emojis))
        
        # Build final alive display with premium emojis
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        alive_display = f"""{signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧

{get_emoji('centang')} 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 {get_emoji('utama')}
{get_emoji('centang')} Code : Python 3.12+ Enhanced
{get_emoji('centang')} Plugins : {plugin_count} Premium Modules
{get_emoji('centang')} Instagram : vzoel.fox_s
{get_emoji('centang')} Zone : Indonesia 🇮🇩

{random_emoji1} PREMIUM FEATURES :
• Advanced Premium Emoji System
• Vzoel Fox's Branded Interface
• Enhanced Performance & Stability

{get_emoji('adder2')} Powered by Vzoel Fox's Technology
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

{random_emoji2} ©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
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
        
        alive_info = f"""{signature} Vzoel Fox's Alive System

{get_emoji('utama')} Features:
• 12-phase animated loading sequence
• Premium emoji integration throughout
• Dynamic plugin count display
• Indonesian flag zone indicator
• Random emoji selection for notices

{get_emoji('centang')} Animation Phases:
1. Initializing Vzoel Fox's Assistant
2. Loading premium components
3. Connecting to Vzoel Fox's servers
4. Validating premium emojis
5. Scanning installed plugins
6. Checking system integrity
7. Verifying Vzoel Fox's credentials
8. Loading assistant profile
9. Preparing display interface
10. Finalizing system status
11. Vzoel Fox's Assistant ready
12. Generating status display

{get_emoji('telegram')} Display Info:
• Founder: Vzoel Fox's (Lutpan)
• Programming: Python3, Python2
• Features: Dynamic plugin count
• Social: vzoel.fox_s (Instagram)
• Location: Indonesia 🇮🇩

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        
        # Display alive info with premium emoji support
        await safe_edit_premium(event, alive_info)
        if vzoel_client:
            vzoel_client.increment_command_count()

