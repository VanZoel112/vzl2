"""
VzoelFox Telegram Userbot v2
Enhanced with Telethon and Premium Emoji Support
Created by: Vzoel Fox's
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import DocumentAttributeCustomEmoji

from emoji_handler import vzoel_emoji
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vzl2.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VzoelFoxBot:
    """VzoelFox Telegram Userbot v2"""
    
    def __init__(self):
        self.client = None
        self.config = Config()
        self.is_running = False
        
    async def start_client(self):
        """Start Telegram client"""
        try:
            self.client = TelegramClient(
                'vzl2_session', 
                self.config.API_ID, 
                self.config.API_HASH
            )
            
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                logger.info("Client not authorized, please login")
                phone = input("Enter phone number: ")
                await self.client.send_code_request(phone)
                code = input("Enter code: ")
                
                try:
                    await self.client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    password = input("Enter 2FA password: ")
                    await self.client.sign_in(password=password)
            
            self.is_running = True
            logger.info("VzoelFox Bot v2 started successfully!")
            
            # Display startup message with signature emojis
            signature = vzoel_emoji.get_vzoel_signature()
            startup_msg = vzoel_emoji.format_emoji_response(
                ['utama', 'petir', 'aktif'], 
                "VzoelFox Userbot v2 is now ACTIVE!"
            )
            logger.info(f"{signature} {startup_msg}")
            
        except Exception as e:
            logger.error(f"Failed to start client: {e}")
            sys.exit(1)
    
    async def stop_client(self):
        """Stop Telegram client"""
        if self.client:
            await self.client.disconnect()
            self.is_running = False
            logger.info("VzoelFox Bot v2 stopped")

# Event handlers
bot = VzoelFoxBot()

@events.register(events.NewMessage(pattern=r'\.ping'))
async def ping_handler(event):
    """Ping command with VzoelFox emojis"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        start_time = asyncio.get_event_loop().time()
        
        # Loading emoji
        loading_msg = vzoel_emoji.format_emoji_response(['loading'], "Pinging...")
        msg = await event.edit(loading_msg)
        
        end_time = asyncio.get_event_loop().time()
        ping_time = (end_time - start_time) * 1000
        
        # Success emoji with ping result
        ping_emojis = vzoel_emoji.get_command_emojis('ping')
        response = vzoel_emoji.format_emoji_response(
            ping_emojis, 
            f"**VzoelFox Pong!**\n**Speed:** `{ping_time:.2f}ms`"
        )
        await msg.edit(response)

@events.register(events.NewMessage(pattern=r'\.alive'))
async def alive_handler(event):
    """Alive command with VzoelFox signature"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        alive_emojis = vzoel_emoji.get_command_emojis('alive')
        signature = vzoel_emoji.get_vzoel_signature()
        
        alive_text = f"""**VzoelFox Userbot v2**
        
{signature} **Status:** ALIVE & RUNNING
{vzoel_emoji.get_emoji('aktif')} **Version:** v2.0.0-vzoel
{vzoel_emoji.get_emoji('telegram')} **Engine:** Telethon
{vzoel_emoji.get_emoji('centang')} **Premium Emojis:** Loaded
        
**Created by:** Vzoel Fox's
**Enhanced by:** Vzoel Fox's Ltpn"""
        
        response = vzoel_emoji.format_emoji_response(alive_emojis, alive_text)
        await event.edit(response)

@events.register(events.NewMessage(pattern=r'\.vzoel'))
async def vzoel_handler(event):
    """Special VzoelFox command"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        vzoel_emojis = vzoel_emoji.get_command_emojis('vzoel')
        signature = vzoel_emoji.get_vzoel_signature()
        
        vzoel_text = f"""**{signature} VZOEL FOX'S TERRITORY {signature}**

{vzoel_emoji.get_emoji('utama')} **Welcome to VzoelFox's Domain**
{vzoel_emoji.get_emoji('petir')} **Power:** UNLIMITED
{vzoel_emoji.get_emoji('adder1')} **Mode:** PREMIUM ACTIVATED
{vzoel_emoji.get_emoji('aktif')} **Status:** DOMINATING

**© Vzoel Fox's - Enhanced Userbot Experience**"""
        
        await event.edit(vzoel_text)

@events.register(events.NewMessage(pattern=r'\.emo (\w+)'))
async def emoji_info_handler(event):
    """Get emoji information"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        emoji_name = event.pattern_match.group(1)
        emoji_info = vzoel_emoji.get_emoji_info(emoji_name)
        
        if emoji_info:
            response = f"""**{emoji_info['emoji_char']} Emoji Info**

**Name:** {emoji_info['name']}
**Category:** {emoji_info['category']}
**Description:** {emoji_info['description']}
**Usage:** {emoji_info['usage']}
**Theme:** {emoji_info['color_theme']}
**Custom ID:** `{emoji_info['custom_emoji_id']}`"""
            
            await event.edit(response)
        else:
            error_emojis = vzoel_emoji.get_status_emojis('error')
            error_msg = vzoel_emoji.format_emoji_response(
                error_emojis, 
                f"Emoji `{emoji_name}` not found in VzoelFox collection"
            )
            await event.edit(error_msg)

@events.register(events.NewMessage(pattern=r'\.emojis'))
async def list_emojis_handler(event):
    """List all available emojis"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        all_emojis = vzoel_emoji.get_all_emojis()
        
        emoji_list = "**VzoelFox's Premium Emoji Collection**\n\n"
        
        for category_name, category_data in vzoel_emoji.categories.items():
            emoji_list += f"**{category_data['description']}**\n"
            for emoji_name in category_data['emojis']:
                emoji_data = all_emojis.get(emoji_name, {})
                emoji_char = emoji_data.get('emoji_char', '')
                emoji_list += f"{emoji_char} `{emoji_name}` - {emoji_data.get('description', '')}\n"
            emoji_list += "\n"
        
        signature = vzoel_emoji.get_vzoel_signature()
        emoji_list += f"\n{signature} **Total:** {len(all_emojis)} Premium Emojis"
        
        await event.edit(emoji_list)

@events.register(events.NewMessage(pattern=r'\.help'))
async def help_handler(event):
    """Help command"""
    if event.is_private or event.sender_id == (await bot.client.get_me()).id:
        help_text = f"""**{vzoel_emoji.get_vzoel_signature()} VzoelFox Userbot v2 Commands**

{vzoel_emoji.get_emoji('centang')} **Basic Commands:**
`.ping` - Check bot speed
`.alive` - Bot status
`.vzoel` - Special VzoelFox command

{vzoel_emoji.get_emoji('telegram')} **Emoji Commands:**
`.emo <name>` - Get emoji info
`.emojis` - List all emojis
`.help` - Show this help

{vzoel_emoji.get_emoji('utama')} **Premium Features:**
• Custom premium emoji support
• VzoelFox signature collection
• Enhanced Telethon integration

**Created by Vzoel Fox's**
**Enhanced by Vzoel Fox's Ltpn**"""
        
        await event.edit(help_text)

async def main():
    """Main function"""
    logger.info("Starting VzoelFox Userbot v2...")
    
    try:
        await bot.start_client()
        
        # Register event handlers
        bot.client.add_event_handler(ping_handler)
        bot.client.add_event_handler(alive_handler)
        bot.client.add_event_handler(vzoel_handler)
        bot.client.add_event_handler(emoji_info_handler)
        bot.client.add_event_handler(list_emojis_handler)
        bot.client.add_event_handler(help_handler)
        
        logger.info("All event handlers registered successfully")
        
        # Keep the bot running
        await bot.client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop_client()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)