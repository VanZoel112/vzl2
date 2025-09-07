"""
VzoelFox's Assistant v2 Configuration
Environment variables and settings management
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for VzoelFox's Assistant"""
    
    # API Configuration
    API_ID: int = int(os.getenv("API_ID", "29919905"))
    API_HASH: str = os.getenv("API_HASH", "717957f0e3ae20a7db004d08b66bfd30")
    
    # Bot Configuration
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    STRING_SESSION: Optional[str] = os.getenv("STRING_SESSION")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///vzl2.db")
    
    # VzoelFox Specific Settings
    VZOEL_PREFIX: str = os.getenv("VZOEL_PREFIX", ".")
    
    @classmethod
    def _safe_int_env(cls, env_var: str, default: int = 0) -> Optional[int]:
        """Safely convert environment variable to integer"""
        try:
            value = os.getenv(env_var, str(default))
            if not value or value in ['your_telegram_user_id', 'your_log_chat_id', '0']:
                return None
            return int(value)
        except (ValueError, TypeError):
            return None
    
    VZOEL_OWNER_ID: Optional[int] = None
    VZOEL_LOG_CHAT: Optional[int] = None
    
    # Premium Emoji Settings
    PREMIUM_EMOJIS_ENABLED: bool = os.getenv("PREMIUM_EMOJIS_ENABLED", "true").lower() == "true"
    EMOJI_MAPPING_FILE: str = os.getenv("EMOJI_MAPPING_FILE", "emoji_mapping.json")
    
    # Security Settings
    PRIVATE_GROUP_BOT_API_ID: Optional[int] = None
    PRIVATE_GROUP_ID: Optional[int] = None
    
    # Advanced Settings
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    LOAD_UNOFFICIAL_PLUGINS: bool = os.getenv("LOAD_UNOFFICIAL_PLUGINS", "false").lower() == "true"
    
    # Gcast Blacklist Settings
    GCAST_BLACKLIST: List[int] = []
    
    # Heroku/Deploy Settings
    HEROKU_APP_NAME: Optional[str] = os.getenv("HEROKU_APP_NAME")
    HEROKU_API_KEY: Optional[str] = os.getenv("HEROKU_API_KEY")
    
    # VzoelFox Branding
    VZOEL_VERSION: str = "v2.0.0-vzoel"
    VZOEL_CREATOR: str = "Vzoel Fox's"
    VZOEL_ENHANCED_BY: str = "Vzoel Fox's Ltpn"
    
    def __init__(self):
        """Initialize config values safely"""
        Config.VZOEL_OWNER_ID = Config._safe_int_env("VZOEL_OWNER_ID")
        Config.VZOEL_LOG_CHAT = Config._safe_int_env("VZOEL_LOG_CHAT")
        Config.PRIVATE_GROUP_BOT_API_ID = Config._safe_int_env("PRIVATE_GROUP_BOT_API_ID")
        Config.PRIVATE_GROUP_ID = Config._safe_int_env("PRIVATE_GROUP_ID")
    
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
    def add_to_blacklist(cls, chat_id: int) -> bool:
        """Add chat ID to gcast blacklist"""
        if chat_id not in cls.GCAST_BLACKLIST:
            cls.GCAST_BLACKLIST.append(chat_id)
            cls._save_blacklist()
            return True
        return False
    
    @classmethod
    def remove_from_blacklist(cls, chat_id: int) -> bool:
        """Remove chat ID from gcast blacklist"""
        if chat_id in cls.GCAST_BLACKLIST:
            cls.GCAST_BLACKLIST.remove(chat_id)
            cls._save_blacklist()
            return True
        return False
    
    @classmethod
    def is_blacklisted(cls, chat_id: int) -> bool:
        """Check if chat ID is blacklisted"""
        return chat_id in cls.GCAST_BLACKLIST
    
    @classmethod
    def _save_blacklist(cls):
        """Save blacklist to config file"""
        import json
        try:
            # Read current config file
            config_file = "config.py"
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Update GCAST_BLACKLIST line
            blacklist_str = str(cls.GCAST_BLACKLIST).replace("'", '"')
            if "GCAST_BLACKLIST: List[int] = []" in content:
                content = content.replace(
                    "GCAST_BLACKLIST: List[int] = []",
                    f"GCAST_BLACKLIST: List[int] = {cls.GCAST_BLACKLIST}"
                )
            elif "GCAST_BLACKLIST: List[int] = [" in content:
                import re
                pattern = r"GCAST_BLACKLIST: List\[int\] = \[.*?\]"
                content = re.sub(pattern, f"GCAST_BLACKLIST: List[int] = {cls.GCAST_BLACKLIST}", content)
            
            # Write back to file
            with open(config_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Failed to save blacklist: {e}")
    
    @classmethod
    def load_blacklist(cls):
        """Load blacklist from environment or config"""
        try:
            blacklist_env = os.getenv("GCAST_BLACKLIST", "")
            if blacklist_env:
                import json
                cls.GCAST_BLACKLIST = json.loads(blacklist_env)
        except Exception:
            pass
    
    @classmethod
    def print_config(cls):
        """Print current configuration (hide sensitive data)"""
        print(f"""
🦊 VzoelFox's Assistant v2 Configuration

📱 API Settings:
   API_ID: {'✅ Set' if cls.API_ID else '❌ Not Set'}
   API_HASH: {'✅ Set' if cls.API_HASH else '❌ Not Set'}

🤖 Assistant Settings:
   Prefix: {cls.VZOEL_PREFIX}
   Premium Emojis: {'✅ Enabled' if cls.PREMIUM_EMOJIS_ENABLED else '❌ Disabled'}
   Workers: {cls.WORKERS}
   Gcast Blacklist: {len(cls.GCAST_BLACKLIST)} chats

🎭 VzoelFox Info:
   Version: {cls.VZOEL_VERSION}
   Creator: {cls.VZOEL_CREATOR}
   Enhanced by: {cls.VZOEL_ENHANCED_BY}
        """)

# Environment template for easy setup
ENV_TEMPLATE = """
# VzoelFox's Assistant v2 Environment Configuration
# Copy this to .env and fill in your values

# API Configuration (Required)
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Optional Settings
BOT_TOKEN=your_bot_token_if_using_bot_mode
STRING_SESSION=your_string_session_if_available

# VzoelFox Specific
VZOEL_PREFIX=.
# VZOEL_OWNER_ID=123456789
# VZOEL_LOG_CHAT=-1001234567890

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