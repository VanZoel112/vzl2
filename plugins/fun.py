import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from vzoel_simple import vzoel_comments

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

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = vzoel_emoji.get_vzoel_signature(premium=True)
    print(f"{signature} Fun Plugin loaded - Entertainment commands ready")

@events.register(events.NewMessage(pattern=r'\.dice'))
async def dice_handler(event):
    """Roll a dice with VzoelFox style"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        from emoji_handler_premium import vzoel_emoji
        
        # Show rolling animation
        rolling_msg = vzoel_emoji.format_emoji_response(
            ['loading'], "Rolling dice..."
        )
        msg = await event.edit(rolling_msg)
        
        await asyncio.sleep(1)
        
        # Roll dice
        result = random.randint(1, 6)
        dice_emojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
        
        result_msg = vzoel_emoji.format_emoji_response(
            ['utama'], f"**VzoelFox Dice Roll**\n\n{dice_emojis[result-1]} You rolled: **{result}**"
        )
        
        await msg.edit(result_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.flip'))
async def flip_handler(event):
    """Flip a coin"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        from emoji_handler_premium import vzoel_emoji
        
        flipping_msg = vzoel_emoji.format_emoji_response(
            ['proses'], "Flipping coin..."
        )
        msg = await event.edit(flipping_msg)
        
        await asyncio.sleep(1)
        
        result = random.choice(['Heads', 'Tails'])
        emoji = '👑' if result == 'Heads' else '🪙'
        
        result_msg = vzoel_emoji.format_emoji_response(
            ['kuning'], f"**VzoelFox Coin Flip**\n\n{emoji} Result: **{result}**"
        )
        
        await msg.edit(result_msg)
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
        from emoji_handler_premium import vzoel_emoji

        
        signature = vzoel_emoji.get_vzoel_signature(premium=True)
        
        quote_msg = f"**{signature} VzoelFox Quote**\n\n*\"{quote}\"*\n\n— **Vzoel Fox's**"
        
        await event.edit(quote_msg)
        vzoel_client.increment_command_count()
