"""
VzoelFox Userbot v2 Configuration
Environment variables and settings management
"""

import os
from typing import Optional

class Config:
    """Configuration class for VzoelFox Userbot"""
    
    # Telegram API Configuration
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    
    # Bot Configuration
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    STRING_SESSION: Optional[str] = os.getenv("STRING_SESSION")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///vzl2.db")
    
    # VzoelFox Specific Settings
    VZOEL_PREFIX: str = os.getenv("VZOEL_PREFIX", ".")
    VZOEL_OWNER_ID: Optional[int] = int(os.getenv("VZOEL_OWNER_ID", "0")) if os.getenv("VZOEL_OWNER_ID") else None
    VZOEL_LOG_CHAT: Optional[int] = int(os.getenv("VZOEL_LOG_CHAT", "0")) if os.getenv("VZOEL_LOG_CHAT") else None
    
    # Premium Emoji Settings
    PREMIUM_EMOJIS_ENABLED: bool = os.getenv("PREMIUM_EMOJIS_ENABLED", "true").lower() == "true"
    EMOJI_MAPPING_FILE: str = os.getenv("EMOJI_MAPPING_FILE", "emoji_mapping.json")
    
    # Security Settings
    PRIVATE_GROUP_BOT_API_ID: Optional[int] = int(os.getenv("PRIVATE_GROUP_BOT_API_ID", "0")) if os.getenv("PRIVATE_GROUP_BOT_API_ID") else None
    PRIVATE_GROUP_ID: Optional[int] = int(os.getenv("PRIVATE_GROUP_ID", "0")) if os.getenv("PRIVATE_GROUP_ID") else None
    
    # Advanced Settings
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    LOAD_UNOFFICIAL_PLUGINS: bool = os.getenv("LOAD_UNOFFICIAL_PLUGINS", "false").lower() == "true"
    
    # Heroku/Deploy Settings
    HEROKU_APP_NAME: Optional[str] = os.getenv("HEROKU_APP_NAME")
    HEROKU_API_KEY: Optional[str] = os.getenv("HEROKU_API_KEY")
    
    # VzoelFox Branding
    VZOEL_VERSION: str = "v2.0.0-vzoel"
    VZOEL_CREATOR: str = "Vzoel Fox's"
    VZOEL_ENHANCED_BY: str = "Vzoel Fox's Ltpn"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration"""
        if not cls.API_ID or cls.API_ID == 0:
            print("❌ API_ID is required")
            return False
            
        if not cls.API_HASH:
            print("❌ API_HASH is required")
            return False
            
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (hide sensitive data)"""
        print(f"""
🦊 VzoelFox Userbot v2 Configuration

📱 Telegram API:
   API_ID: {'✅ Set' if cls.API_ID else '❌ Not Set'}
   API_HASH: {'✅ Set' if cls.API_HASH else '❌ Not Set'}

🤖 Bot Settings:
   Prefix: {cls.VZOEL_PREFIX}
   Premium Emojis: {'✅ Enabled' if cls.PREMIUM_EMOJIS_ENABLED else '❌ Disabled'}
   Workers: {cls.WORKERS}

🎭 VzoelFox Info:
   Version: {cls.VZOEL_VERSION}
   Creator: {cls.VZOEL_CREATOR}
   Enhanced by: {cls.VZOEL_ENHANCED_BY}
        """)

# Environment template for easy setup
ENV_TEMPLATE = """
# VzoelFox Userbot v2 Environment Configuration
# Copy this to .env and fill in your values

# Telegram API (Required)
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Optional Settings
BOT_TOKEN=your_bot_token_if_using_bot_mode
STRING_SESSION=your_string_session_if_available

# VzoelFox Specific
VZOEL_PREFIX=.
VZOEL_OWNER_ID=your_telegram_user_id
VZOEL_LOG_CHAT=your_log_chat_id

# Premium Features
PREMIUM_EMOJIS_ENABLED=true
EMOJI_MAPPING_FILE=emoji_mapping.json

# Advanced Settings
WORKERS=4
LOAD_UNOFFICIAL_PLUGINS=false

# Database
DATABASE_URL=sqlite:///vzl2.db

# Deployment (Optional)
HEROKU_APP_NAME=
HEROKU_API_KEY=
"""