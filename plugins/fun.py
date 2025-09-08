import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced Fun Plugin for VzoelFox Userbot - Premium Edition
Fitur: Entertainment dan fun commands dengan premium emoji support
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Fun System
"""

from telethon import events
import random
import asyncio

# Plugin Info
PLUGIN_INFO = {
    "name": "fun",
    "version": "3.0.0",
    "description": "Entertainment dan fun commands dengan premium emoji support",
    "author": "Founder Userbot: Vzoel Fox's Ltpn",
    "commands": [".dice", ".flip", ".quote"],
    "features": ["dice rolling", "coin flipping", "VzoelFox quotes", "premium emoji"]
}

__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Fun Plugin loaded - Entertainment commands ready")

@events.register(events.NewMessage(pattern=r'\.dice'))
async def dice_handler(event):
    """Roll a dice with VzoelFox style"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        # Show rolling animation
        rolling_msg = f"{get_emoji('loading')} Rolling dice..."
        
        msg = await event.edit(rolling_msg)
        
        await asyncio.sleep(1)
        
        # Roll dice
        result = random.randint(1, 6)
        dice_emojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        result_msg = f"{signature} DICE ROLLED!\n\n{dice_emojis[result-1]} Result: {result}\n\nBy VzoelFox Assistant"
        
        await safe_edit_premium(msg, result_msg)
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.flip'))
async def flip_handler(event):
    """Flip a coin"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        flipping_msg = f"{get_emoji('proses')} Flipping coin..."
        
        msg = await event.edit(flipping_msg)
        
        await asyncio.sleep(1)
        
        result = random.choice(['Heads', 'Tails'])
        emoji = get_emoji('utama') if result == 'Heads' else get_emoji('kuning')
        
        result_msg = f"{emoji} Coin Result: {result}\n\nBy VzoelFox Assistant"
        
        await safe_edit_premium(msg, result_msg)
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.quote'))
async def quote_handler(event):
    """Send a random VzoelFox quote"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        vzoel_quotes = [
            f"The fox always finds a way {get_emoji('adder1')}",
            f"Premium emojis make everything better {get_emoji('utama')}",
            f"VzoelFox's domain knows no limits {get_emoji('petir')}",
            f"Enhanced by Vzoel Fox's Ltpn {get_emoji('aktif')}",
            f"Every command is a work of art {get_emoji('adder2')}",
            f"The storm follows the fox {get_emoji('petir')}{get_emoji('adder1')}",
            f"Premium features for premium users {get_emoji('adder1')}",
            f"VzoelFox's Assistant at your service {get_emoji('proses')}"
        ]
        
        quote = random.choice(vzoel_quotes)

        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        quote_msg = f"{signature} VzoelFox Quote\n\n\"{quote}\"\n\n— Vzoel Fox's"
        
        
        msg = await event.edit(quote_msg)
        await safe_edit_premium(msg, quote_msg)
        if vzoel_client:
            vzoel_client.increment_command_count()
