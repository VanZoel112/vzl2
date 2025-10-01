"""
Vzoel Fox's Assistant v2 Configuration
Environment variables and settings management
"""

import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for Vzoel Fox's Assistant"""
    
    # API Configuration
    API_ID: int = int(os.getenv("API_ID", "29919905"))
    API_HASH: str = os.getenv("API_HASH", "717957f0e3ae20a7db004d08b66bfd30")
    
    # Bot Configuration
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    STRING_SESSION: Optional[str] = os.getenv("STRING_SESSION")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///vzl2.db")
    
    # Vzoel Fox's Specific Settings
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
    GCAST_BLACKLIST: List[int] = [-1001999857761, -1001722785066, -1001351989497]

    # Locked Users Settings (Auto-delete all messages)
    LOCKED_USERS_GLOBAL: List[int] = [1166600226, 1927430008, 615294917, 6547201613, 7951832209, 7360660998, 7442506962, 1847641730, 7112380570, 8167904373, 1789196664, 6854220685, 5413892013, 1413644201, 6771085223, 1371061365, 7989719706, 1813821608, 5560310674, 8132000594, 6443032343, 890425915, 5721720953, 6824859389, 5228075978, 695641283, 6881236382, 7393424532, 1259598471, 1472568994, 7389203556, 7350402824, 6124356218, 6497538375, 5267752498, 7207241320, 6388304691, 6910823135, 8056444100, 7806802729, 7453811064, 1354355299, 6315279074, 1918315459, 6299801952, 7436524387]
    
    # Heroku/Deploy Settings
    HEROKU_APP_NAME: Optional[str] = os.getenv("HEROKU_APP_NAME")
    HEROKU_API_KEY: Optional[str] = os.getenv("HEROKU_API_KEY")
    
    # Music System Configuration
    MUSIC_DOWNLOAD_PATH: str = os.getenv("MUSIC_DOWNLOAD_PATH", "downloads/musik")
    MUSIC_COOLDOWN: int = int(os.getenv("MUSIC_COOLDOWN", "3"))
    MUSIC_ENABLED: bool = os.getenv("MUSIC_ENABLED", "true").lower() == "true"
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))
    AUDIO_QUALITY: str = os.getenv("AUDIO_QUALITY", "bestaudio[ext=m4a]/bestaudio")

    # YouTube Cookies (helps bypass bot detection)
    YOUTUBE_COOKIES_FROM_BROWSER: Optional[str] = os.getenv("YOUTUBE_COOKIES_FROM_BROWSER", "")
    YOUTUBE_COOKIES_FILE: Optional[str] = os.getenv("YOUTUBE_COOKIES_FILE", "cookies.txt")

    # Vzoel Fox's Branding
    VZOEL_VERSION: str = "v2.0.0-lutpan"
    VZOEL_CREATOR: str = "Vzoel Fox's"
    VZOEL_ENHANCED_BY: str = "Vzoel Fox's Lutpan"
    VZOEL_CONTACT: str = "@VZLfxs"
    
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
            if "GCAST_BLACKLIST: List[int] = [-1001999857761, -1001722785066, -1001351989497]" in content:
                content = content.replace(
                    "GCAST_BLACKLIST: List[int] = [-1001999857761, -1001722785066, -1001351989497]",
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

        # Load locked users from environment
        try:
            locked_env = os.getenv("LOCKED_USERS_GLOBAL", "")
            if locked_env:
                import json
                cls.LOCKED_USERS_GLOBAL = json.loads(locked_env)
        except Exception:
            pass

    @classmethod
    def add_locked_user(cls, user_id: int) -> bool:
        """Add user ID to global locked users list"""
        if user_id not in cls.LOCKED_USERS_GLOBAL:
            cls.LOCKED_USERS_GLOBAL.append(user_id)
            cls._save_locked_users()
            cls._update_env_locked_users()
            return True
        return False

    @classmethod
    def remove_locked_user(cls, user_id: int) -> bool:
        """Remove user ID from global locked users list"""
        if user_id in cls.LOCKED_USERS_GLOBAL:
            cls.LOCKED_USERS_GLOBAL.remove(user_id)
            cls._save_locked_users()
            cls._update_env_locked_users()
            return True
        return False

    @classmethod
    def is_locked_user(cls, user_id: int) -> bool:
        """Check if user ID is globally locked"""
        return user_id in cls.LOCKED_USERS_GLOBAL

    @classmethod
    def _save_locked_users(cls):
        """Save locked users to config file"""
        try:
            # Read current config file
            config_file = "config.py"
            with open(config_file, 'r') as f:
                content = f.read()

            # Update LOCKED_USERS_GLOBAL line
            if "LOCKED_USERS_GLOBAL: List[int] = [1166600226, 1927430008, 615294917, 6547201613, 7951832209, 7360660998, 7442506962, 1847641730, 7112380570, 8167904373, 1789196664, 6854220685, 5413892013, 1413644201, 6771085223, 1371061365, 7989719706, 1813821608, 5560310674, 8132000594, 6443032343, 890425915, 5721720953, 6824859389, 5228075978, 695641283, 6881236382, 7393424532, 1259598471, 1472568994, 7389203556, 7350402824, 6124356218, 6497538375, 5267752498, 7207241320, 6388304691, 6910823135, 8056444100, 7806802729, 7453811064, 1354355299, 6315279074, 1918315459, 6299801952, 7436524387]" in content:
                content = content.replace(
                    "LOCKED_USERS_GLOBAL: List[int] = [1166600226, 1927430008, 615294917, 6547201613, 7951832209, 7360660998, 7442506962, 1847641730, 7112380570, 8167904373, 1789196664, 6854220685, 5413892013, 1413644201, 6771085223, 1371061365, 7989719706, 1813821608, 5560310674, 8132000594, 6443032343, 890425915, 5721720953, 6824859389, 5228075978, 695641283, 6881236382, 7393424532, 1259598471, 1472568994, 7389203556, 7350402824, 6124356218, 6497538375, 5267752498, 7207241320, 6388304691, 6910823135, 8056444100, 7806802729, 7453811064, 1354355299, 6315279074, 1918315459, 6299801952, 7436524387]",
                    f"LOCKED_USERS_GLOBAL: List[int] = {cls.LOCKED_USERS_GLOBAL}"
                )
            elif "LOCKED_USERS_GLOBAL: List[int] = [" in content:
                import re
                pattern = r"LOCKED_USERS_GLOBAL: List\[int\] = \[.*?\]"
                content = re.sub(pattern, f"LOCKED_USERS_GLOBAL: List[int] = {cls.LOCKED_USERS_GLOBAL}", content)

            # Write back to file
            with open(config_file, 'w') as f:
                f.write(content)

        except Exception as e:
            print(f"Failed to save locked users: {e}")

    @classmethod
    def _update_env_locked_users(cls):
        """Update .env file with locked users"""
        try:
            import json

            env_file = ".env"
            env_content = []

            # Read current .env file
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    env_content = f.readlines()

            # Find and update LOCKED_USERS_GLOBAL line
            locked_users_line = f"LOCKED_USERS_GLOBAL={json.dumps(cls.LOCKED_USERS_GLOBAL)}\n"
            found = False

            for i, line in enumerate(env_content):
                if line.startswith("LOCKED_USERS_GLOBAL="):
                    env_content[i] = locked_users_line
                    found = True
                    break

            # Add new line if not found
            if not found:
                env_content.append(locked_users_line)

            # Write back to .env file
            with open(env_file, 'w') as f:
                f.writelines(env_content)

        except Exception as e:
            print(f"Failed to update .env with locked users: {e}")

    @classmethod
    def print_config(cls):
        """Print current configuration (hide sensitive data)"""
        print(f"""
🦊 Vzoel Fox's Assistant v2 Configuration

📱 API Settings:
   API_ID: {'✅ Set' if cls.API_ID else '❌ Not Set'}
   API_HASH: {'✅ Set' if cls.API_HASH else '❌ Not Set'}

🤖 Assistant Settings:
   Prefix: {cls.VZOEL_PREFIX}
   Premium Emojis: {'✅ Enabled' if cls.PREMIUM_EMOJIS_ENABLED else '❌ Disabled'}
   Workers: {cls.WORKERS}
   Gcast Blacklist: {len(cls.GCAST_BLACKLIST)} chats
   Locked Users: {len(cls.LOCKED_USERS_GLOBAL)} users

🎭 Vzoel Fox's Info:
   Version: {cls.VZOEL_VERSION}
   Creator: {cls.VZOEL_CREATOR}
   Enhanced by: {cls.VZOEL_ENHANCED_BY}
        """)

# Environment template for easy setup
ENV_TEMPLATE = """
# Vzoel Fox's Assistant v2 Environment Configuration
# Copy this to .env and fill in your values

# API Configuration (Required)
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Optional Settings
BOT_TOKEN=your_bot_token_if_using_bot_mode
STRING_SESSION=your_string_session_if_available

# Vzoel Fox's Specific
VZOEL_PREFIX=.
# VZOEL_OWNER_ID=123456789
# VZOEL_LOG_CHAT=-1001234567890

# Premium Features
PREMIUM_EMOJIS_ENABLED=true
EMOJI_MAPPING_FILE=emoji_mapping.json

# Advanced Settings
WORKERS=4
LOAD_UNOFFICIAL_PLUGINS=false

# Security Settings
GCAST_BLACKLIST=[]
LOCKED_USERS_GLOBAL=[]

# Music System
YOUTUBE_COOKIES=cookies.txt

# Database
DATABASE_URL=sqlite:///vzl2.db

# Deployment (Optional)
HEROKU_APP_NAME=
HEROKU_API_KEY=
"""