"""
VzoelFox's Assistant v2
Enhanced userbot with Premium Emoji Support
Created by: Vzoel Fox's
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import json

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError, PhoneCodeInvalidError, PhoneNumberInvalidError
from telethon.tl.types import DocumentAttributeCustomEmoji
from telethon.sessions import StringSession

from emoji_handler import vzoel_emoji
from config import Config
from client import vzoel_client

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

class SessionGenerator:
    """VzoelFox's Assistant Session String Generator"""
    
    def __init__(self):
        self.config_file = ".env"
        
    def save_session_to_env(self, session_string: str):
        """Save session string to .env file"""
        env_content = []
        
        # Read existing .env file if it exists
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                env_content = f.readlines()
        
        # Update or add STRING_SESSION
        session_found = False
        for i, line in enumerate(env_content):
            if line.startswith('STRING_SESSION='):
                env_content[i] = f'STRING_SESSION={session_string}\n'
                session_found = True
                break
        
        if not session_found:
            env_content.append(f'STRING_SESSION={session_string}\n')
        
        # Write back to file
        with open(self.config_file, 'w') as f:
            f.writelines(env_content)
        
        logger.info(f"🤩 Session string saved to {self.config_file}")
    
    async def validate_api_credentials(self, api_id: int, api_hash: str) -> bool:
        """Validate API credentials"""
        try:
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            
            # Try to get updates to test API validity
            if await client.is_user_authorized():
                await client.disconnect()
                return True
            
            await client.disconnect()
            return True  # If we can connect, credentials are valid
            
        except ApiIdInvalidError:
            logger.error("❌ Invalid API ID or API Hash")
            return False
        except Exception as e:
            logger.error(f"❌ API validation error: {e}")
            return False
    
    async def generate_session_string(self) -> str:
        """Generate session string with VzoelFox branding"""
        signature = vzoel_emoji.get_vzoel_signature()
        print(f"\n{signature} VzoelFox's Assistant Session Generator {signature}\n")
        
        # Get API credentials
        while True:
            api_id_input = input("🤩 Enter API ID (or press Enter for default): ").strip()
            api_hash_input = input("⛈ Enter API Hash (or press Enter for default): ").strip()
            
            # Use provided defaults if empty
            api_id = int(api_id_input) if api_id_input else Config.API_ID
            api_hash = api_hash_input if api_hash_input else Config.API_HASH
            
            print(f"\n{vzoel_emoji.get_emoji('loading')} Validating API credentials...")
            
            # Validate API credentials
            if await self.validate_api_credentials(api_id, api_hash):
                print(f"{vzoel_emoji.get_emoji('centang')} API credentials are valid!")
                break
            else:
                print(f"{vzoel_emoji.get_emoji('merah')} Invalid API credentials, please try again.\n")
                continue
        
        # Generate session string
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        
        # Phone number input
        while True:
            try:
                phone = input(f"\n{vzoel_emoji.get_emoji('telegram')} Enter phone number (with country code): ").strip()
                
                print(f"{vzoel_emoji.get_emoji('proses')} Sending verification code...")
                await client.send_code_request(phone)
                break
                
            except PhoneNumberInvalidError:
                print(f"{vzoel_emoji.get_emoji('merah')} Invalid phone number format, please try again.")
            except Exception as e:
                print(f"{vzoel_emoji.get_emoji('merah')} Error: {e}")
        
        # Verification code input
        while True:
            try:
                code = input(f"\n{vzoel_emoji.get_emoji('kuning')} Enter verification code: ").strip()
                
                print(f"{vzoel_emoji.get_emoji('loading')} Verifying code...")
                await client.sign_in(phone, code)
                break
                
            except PhoneCodeInvalidError:
                print(f"{vzoel_emoji.get_emoji('merah')} Invalid verification code, please try again.")
            except SessionPasswordNeededError:
                # 2FA password required
                while True:
                    try:
                        password = input(f"\n{vzoel_emoji.get_emoji('aktif')} Enter 2FA password: ").strip()
                        await client.sign_in(password=password)
                        break
                    except Exception as e:
                        print(f"{vzoel_emoji.get_emoji('merah')} Invalid password: {e}")
                break
            except Exception as e:
                print(f"{vzoel_emoji.get_emoji('merah')} Error: {e}")
        
        # Get session string
        session_string = client.session.save()
        await client.disconnect()
        
        print(f"\n{vzoel_emoji.get_emoji('utama')} Session string generated successfully!")
        print(f"{vzoel_emoji.get_emoji('biru')} Saving to environment file...")
        
        # Save to .env file
        self.save_session_to_env(session_string)
        
        print(f"\n{signature} VzoelFox's Assistant Setup Complete! {signature}")
        print(f"{vzoel_emoji.get_emoji('centang')} You can now run the assistant with: python main.py")
        
        return session_string

class VzoelFoxBot:
    """VzoelFox's Assistant v2"""
    
    def __init__(self):
        self.client = None
        self.config = Config()
        self.is_running = False
        
    async def start_client(self):
        """Start client with string session or generate new one"""
        try:
            # Check if string session exists
            if self.config.STRING_SESSION:
                logger.info("Using existing string session...")
                self.client = TelegramClient(
                    StringSession(self.config.STRING_SESSION),
                    self.config.API_ID,
                    self.config.API_HASH
                )
            else:
                # Use file session as fallback
                self.client = TelegramClient(
                    'vzl2_session',
                    self.config.API_ID,
                    self.config.API_HASH
                )
            
            await self.client.start()
            
            # If not authorized and no string session, suggest generating one
            if not await self.client.is_user_authorized() and not self.config.STRING_SESSION:
                logger.info("🤩 Client not authorized and no string session found")
                logger.info("⛈ Run: python main.py --generate-session to create a session")
                return False
            
            self.is_running = True
            logger.info("VzoelFox's Assistant v2 started successfully!")
            
            # Display startup message with signature emojis
            signature = vzoel_emoji.get_vzoel_signature()
            startup_msg = vzoel_emoji.format_emoji_response(
                ['utama', 'petir', 'aktif'], 
                "VzoelFox's Assistant v2 is now ACTIVE!"
            )
            logger.info(f"{signature} {startup_msg}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start client: {e}")
            return False
    
    async def stop_client(self):
        """Stop Telegram client"""
        if self.client:
            await self.client.disconnect()
            self.is_running = False
            logger.info("VzoelFox's Assistant v2 stopped")

# Event handlers
bot = VzoelFoxBot()


@events.register(events.NewMessage(pattern=r'\.vzoel'))
async def vzoel_handler(event):
    """Special VzoelFox command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        vzoel_emojis = vzoel_emoji.get_command_emojis('vzoel')
        signature = vzoel_emoji.get_vzoel_signature()
        
        vzoel_text = f"""**{signature} VZOEL FOX'S TERRITORY {signature}**

{vzoel_emoji.get_emoji('utama')} **Welcome to VzoelFox's Domain**
{vzoel_emoji.get_emoji('petir')} **Power:** UNLIMITED
{vzoel_emoji.get_emoji('adder1')} **Mode:** PREMIUM ACTIVATED
{vzoel_emoji.get_emoji('aktif')} **Status:** DOMINATING

**© Vzoel Fox's - Enhanced Assistant Experience**"""
        
        await event.edit(vzoel_text)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.emo (\w+)'))
async def emoji_info_handler(event):
    """Get emoji information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
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
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.emojis'))
async def list_emojis_handler(event):
    """List all available emojis"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
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
        vzoel_client.increment_command_count()

# Help handler removed - now handled by plugins/help.py
# This prevents duplicate help responses

def show_usage():
    """Show usage instructions"""
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"""
{signature} VzoelFox's Assistant v2 Usage {signature}

🤩 Commands:
  python main.py                    - Start the assistant
  python main.py --generate-session - Generate new session string
  python main.py --help            - Show this help

⛈ First Time Setup:
  1. Run: python main.py --generate-session
  2. Follow the prompts to authenticate
  3. Run: python main.py to start

🎚 Created by Vzoel Fox's • Enhanced by Vzoel Fox's Ltpn
    """)

async def main():
    """Main function"""
    # Check for help argument
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_usage()
        return
    
    # Check for session generation argument
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-session":
        logger.info("🦊 VzoelFox's Assistant Session Generator")
        generator = SessionGenerator()
        await generator.generate_session_string()
        return
    
    try:
        # Start the advanced client
        client_started = await vzoel_client.start()
        if not client_started:
            logger.error("Failed to start client - run with --generate-session first")
            return
        
        # Register built-in event handlers to the client (ping and alive moved to plugins)
        vzoel_client.client.add_event_handler(vzoel_handler)
        vzoel_client.client.add_event_handler(emoji_info_handler)
        vzoel_client.client.add_event_handler(list_emojis_handler)
        # help_handler now handled by plugins/help.py
        
        logger.info("🎚 Built-in event handlers registered")
        
        # Keep the assistant running
        await vzoel_client.client.run_until_disconnected()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await vzoel_client.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)