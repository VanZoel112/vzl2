import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
VzoelFox's Assistant Fun Plugin
Entertainment and fun commands
Created by: Vzoel Fox's
"""

from telethon import events
import random
import asyncio

# Plugin info
__version__ = "1.0.0"
__author__ = "Vzoel Fox's"

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
        msg = await safe_edit_premium(event, rolling_msg)
        
        await asyncio.sleep(1)
        
        # Roll dice
        result = random.randint(1, 6)
        dice_emojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        
        result_msg = f"{get_emoji('utama')} **VzoelFox Dice Roll**\n\n{dice_emojis[result-1]} You rolled: **{result}**"
        
        await safe_edit_premium(msg, result_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.flip'))
async def flip_handler(event):
    """Flip a coin"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        
        flipping_msg = f"{get_emoji('proses')} Flipping coin..."
        msg = await safe_edit_premium(event, flipping_msg)
        
        await asyncio.sleep(1)
        
        result = random.choice(['Heads', 'Tails'])
        emoji = '👑' if result == 'Heads' else '🪙'
        
        result_msg = f"{get_emoji('kuning')} **VzoelFox Coin Flip**\\n\\n{emoji} Result: **{result}**"
        
        await safe_edit_premium(msg, result_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.quote'))
async def quote_handler(event):
    """Send a random VzoelFox quote"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        vzoel_quotes = [
            "The fox always finds a way 🦊",
            "Premium emojis make everything better 🤩",
            "VzoelFox's domain knows no limits ⛈",
            "Enhanced by Vzoel Fox's Ltpn 🎚",
            "Every command is a work of art 💟",
            "The storm follows the fox ⛈🦊",
            "Premium features for premium users 😈",
            "VzoelFox's Assistant at your service 👽"
        ]
        
        quote = random.choice(vzoel_quotes)

        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        quote_msg = f"**{signature} VzoelFox Quote**\n\n*\"{quote}\"*\n\n— **Vzoel Fox's**"
        
        await safe_edit_premium(event, quote_msg)
        vzoel_client.increment_command_count()
