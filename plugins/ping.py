"""
Enhanced Ping Plugin for 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Advanced ping variants dengan premium emoji dan response time analysis
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟼𝟿 - Premium Ping System
"""

from telethon import events
import asyncio
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (Vzoel Fox's style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "ping",
    "version": "0.0.0.𝟼𝟿",
    "description": "Enhanced ping dengan premium emoji dan latency analysis",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".ping", ".pink", ".pong", ".ponk"],
    "features": ["premium emoji", "latency analysis", "uptime tracking"]
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
    print(f"✅ [Ping] Premium system loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [Ping] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧")

@events.register(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    """Standard ping with anti-delay message"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        start_time = time.time()
        
        # Edit message to calculate ping with premium emoji
        calculating_msg = f"{get_emoji('loading')} Menghitung..."
        
        await safe_edit_premium(event, calculating_msg)
        
        end_time = time.time()
        ping_time = (end_time - start_time) * 1000
        
        # Show Vzoel Fox's ping result with signature
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        ping_response = f"{get_emoji('utama')} PONG: {ping_time:.2f}ms\n\n𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"
        await safe_edit_premium(event, ping_response)
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pink'))
async def pink_handler(event):
    global vzoel_client, vzoel_emoji
    """Pink command with latency display"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        
        
        
        start_time = time.time()
        
        # Edit message to calculate latency
        testing_msg = f"{get_emoji('loading')} Testing latency..."
        
        await safe_edit_premium(event, testing_msg)
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        
        # Show Vzoel Fox's pink result with signature
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        pink_response = f"{signature} PINK: {latency:.2f}ms\n\n𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"
        await safe_edit_premium(event, pink_response)
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pong'))
async def pong_handler(event):
    global vzoel_client, vzoel_emoji
    """Pong command that triggers @spambot to reduce floodwait"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        
        
        
        start_time = time.time()
        
        # Calculate latency first
        testing_msg = f"{get_emoji('loading')} Testing..."
        
        await safe_edit_premium(event, testing_msg)
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        
        # Determine emoji based on latency (using premium mapped emojis)
        if latency < 100:
            # Good latency - use green/positive emoji (premium)
            latency_emoji = get_emoji('centang')
        elif latency < 300:
            # Medium latency - use yellow emoji (premium)
            latency_emoji = get_emoji('kuning')
        else:
            # High latency - use red emoji (premium)
            latency_emoji = get_emoji('merah')
        
        try:
            # Try to send message to @spambot to reduce floodwait
            try:
                await event.client.send_message('@spambot', '/start')
                await asyncio.sleep(1)
            except:
                pass  # Ignore if spambot interaction fails
            # Send the PONG message with latency emoji
            signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
            pong_response = f"{signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 PONG {latency_emoji}"

            # If we can forward from spambot, do it, otherwise just show response
            try:
                # Try to get recent message from spambot
                async for message in event.client.iter_messages('@spambot', limit=1):
                    if message.text:
                        # Forward the message content style
                        pong_response = f"{signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 PONG {latency_emoji}\n\nForwarded from @spambot to reduce limits"
                        break
            except:
                pass
                
        except Exception as e:
            # Fallback response if spambot interaction fails
            pong_response = f"{signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 PONG {latency_emoji}\n\nFailed to contact @spambot"
        await safe_edit_premium(event, pong_response)
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.ponk'))
async def ponk_handler(event):
    global vzoel_client, vzoel_emoji
    """Ponk command that shows PONGGGGGG and triggers .alive"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        
        
        
        # Show PONGGGGGG message first with premium emoji
        await safe_edit_premium(event, "PONGGGGGG!!!!")
        await asyncio.sleep(1)
        
        # Trigger the alive plugin functionality by simulating .alive command
        try:
            # Import the alive plugin and call its handler
            import importlib.util
            spec = importlib.util.spec_from_file_location("alive", "plugins/alive.py")
            alive_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(alive_module)
            # Call the alive handler directly
            await alive_module.alive_handler(event)
        except Exception as e:
            # Fallback to simple alive display if plugin loading fails
            signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
            alive_text = f"""𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 v2
{signature} Status: ALIVE & RUNNING
{get_emoji('aktif')} Version: 0.0.0.𝟼𝟿
{get_emoji('centang')} Premium Emojis: Loaded
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝
©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
            await safe_edit_premium(event, alive_text)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pings'))
async def pings_info_handler(event):
    global vzoel_client, vzoel_emoji
    """Show information about all ping commands"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        
        
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        pings_info = f"""{signature} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Ping Commands

{get_emoji('utama')} Available Commands:

{get_emoji('centang')} .ping - PONG!!!! Anti Delay
{get_emoji('aktif')} .pink - PONG!!!! with Latency
{get_emoji('proses')} .pong - PONG + @spambot trigger
{get_emoji('petir')} .ponk - PONGGGGGG + .alive trigger

• Anti-delay messaging system
• Latency-based emoji responses  
• @spambot integration for limit reduction
• Automatic .alive command triggering

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        await safe_edit_premium(event, pings_info)
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator