"""
VzoelFox's Assistant Ping Plugin
Advanced ping variants with latency detection and bot triggers
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
import asyncio
import time

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"{signature} Ping Plugin loaded - 4 ping variants ready")

@events.register(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    """Standard ping with anti-delay message"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        
        start_time = time.time()
        
        # Edit message to calculate ping
        msg = await event.edit("Calculating...")
        
        end_time = time.time()
        ping_time = (end_time - start_time) * 1000
        
        # Show ping with anti-delay message
        ping_response = f"**PONG!!!! VzoelFox Assistant Anti Delay**"
        
        await msg.edit(ping_response)
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pink'))
async def pink_handler(event):
    """Pink command with latency display"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        
        start_time = time.time()
        
        # Edit message to calculate latency
        msg = await event.edit("Testing latency...")
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        
        # Show pink response with latency
        pink_response = f"**PONG!!!! Latency {latency:.2f}ms**"
        
        await msg.edit(pink_response)
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pong'))
async def pong_handler(event):
    """Pong command that triggers @spambot to reduce floodwait"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        
        start_time = time.time()
        
        # Calculate latency first
        test_msg = await event.edit("Testing...")
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        
        # Determine emoji based on latency (using mapped emojis)
        if latency < 100:
            # Good latency - use green/positive emoji
            latency_emoji = vzoel_emoji.get_emoji('centang')  # Green checkmark
        elif latency < 300:
            # Medium latency - use yellow emoji  
            latency_emoji = vzoel_emoji.get_emoji('kuning')   # Yellow popcorn
        else:
            # High latency - use red emoji
            latency_emoji = vzoel_emoji.get_emoji('merah')    # Red crazy face
        
        try:
            # Try to send message to @spambot to reduce floodwait
            try:
                await event.client.send_message('@spambot', '/start')
                await asyncio.sleep(1)
            except:
                pass  # Ignore if spambot interaction fails
            
            # Send the PONG message with latency emoji
            pong_response = f"**PONG {latency_emoji}**"
            
            # If we can forward from spambot, do it, otherwise just show response
            try:
                # Try to get recent message from spambot
                async for message in event.client.iter_messages('@spambot', limit=1):
                    if message.text:
                        # Forward the message content style
                        pong_response = f"**PONG {latency_emoji}**\n\n`Forwarded from @spambot to reduce limits`"
                        break
            except:
                pass
                
        except Exception as e:
            # Fallback response if spambot interaction fails
            pong_response = f"**PONG {latency_emoji}**\n\n`Failed to contact @spambot`"
        
        await test_msg.edit(pong_response)
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.ponk'))
async def ponk_handler(event):
    """Ponk command that shows PONGGGGGG and triggers .alive"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        
        # Show PONGGGGGG message first
        ponk_msg = await event.edit("**PONGGGGGG!!!!**")
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
            alive_emojis = vzoel_emoji.get_command_emojis('alive')
            signature = vzoel_emoji.get_vzoel_signature()
            
            alive_text = f"""**VzoelFox's Assistant v2**
            
{signature} **Status:** ALIVE & RUNNING
{vzoel_emoji.get_emoji('aktif')} **Version:** v2.0.0-vzoel
{vzoel_emoji.get_emoji('telegram')} **Engine:** Enhanced
{vzoel_emoji.get_emoji('centang')} **Premium Emojis:** Loaded
            
**Created by:** Vzoel Fox's
**Enhanced by:** Vzoel Fox's Ltpn"""
            
            response = vzoel_emoji.format_emoji_response(alive_emojis, alive_text)
            await ponk_msg.edit(response)
        
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator

@events.register(events.NewMessage(pattern=r'\.pings'))
async def pings_info_handler(event):
    """Show information about all ping commands"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        
        signature = vzoel_emoji.get_vzoel_signature()
        
        pings_info = f"""**{signature} VzoelFox Ping Commands**

{vzoel_emoji.get_emoji('utama')} **Available Commands:**

{vzoel_emoji.get_emoji('centang')} `.ping` - PONG!!!! Anti Delay
{vzoel_emoji.get_emoji('aktif')} `.pink` - PONG!!!! with Latency
{vzoel_emoji.get_emoji('proses')} `.pong` - PONG + @spambot trigger
{vzoel_emoji.get_emoji('petir')} `.ponk` - PONGGGGGG + .alive trigger

{vzoel_emoji.get_emoji('telegram')} **Features:**
• Anti-delay messaging system
• Latency-based emoji responses  
• @spambot integration for limit reduction
• Automatic .alive command triggering

**By VzoelFox Assistant**"""
        
        await event.edit(pings_info)
        vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator