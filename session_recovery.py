"""
Vzoel Fox's Session Recovery System
Automatic session recovery and regeneration for expired sessions
Created by: Vzoel Fox's
Enhanced by: Claude Code Assistant
"""

import os
import asyncio
import logging
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionRevokedError, 
    AuthKeyUnregisteredError,
    AuthKeyDuplicatedError,
    UnauthorizedError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    SessionPasswordNeededError
)

from config import Config
from vzoel_simple import vzoel_emoji

logger = logging.getLogger(__name__)

class SessionRecoveryManager:
    """Advanced Session Recovery and Management System"""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = Path("session_backups")
        self.recovery_log_file = "session_recovery.log"
        self.session_info_file = ".session_info.json"
        self.max_backup_files = 5
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        info = {
            "last_check": None,
            "backup_count": 0,
            "recovery_count": 0,
            "last_recovery": None,
            "session_type": "string" if self.config.STRING_SESSION else "file"
        }
        
        if os.path.exists(self.session_info_file):
            try:
                with open(self.session_info_file, 'r') as f:
                    info.update(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to load session info: {e}")
        
        return info
    
    def save_session_info(self, info: Dict[str, Any]):
        """Save session information"""
        try:
            with open(self.session_info_file, 'w') as f:
                json.dump(info, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save session info: {e}")
    
    def backup_current_session(self) -> bool:
        """Backup current session files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = self.backup_dir / f"backup_{timestamp}"
            backup_subdir.mkdir(exist_ok=True)
            
            backed_up = False
            
            # Backup string session from .env
            if self.config.STRING_SESSION:
                env_backup = backup_subdir / ".env.backup"
                if os.path.exists(".env"):
                    shutil.copy2(".env", env_backup)
                    backed_up = True
                    logger.info(f"📁 Backed up .env to {env_backup}")
            
            # Backup session files
            session_files = [
                "vzl2_session.session",
                ":memory:.session",
                "vzl2_session.session-journal"
            ]
            
            for session_file in session_files:
                if os.path.exists(session_file):
                    backup_file = backup_subdir / session_file
                    shutil.copy2(session_file, backup_file)
                    backed_up = True
                    logger.info(f"📁 Backed up {session_file} to {backup_file}")
            
            if backed_up:
                # Update session info
                info = self.get_session_info()
                info["backup_count"] = info.get("backup_count", 0) + 1
                info["last_backup"] = datetime.now().isoformat()
                self.save_session_info(info)
                
                # Clean old backups
                self._cleanup_old_backups()
                
                logger.info(f"✅ Session backup completed: {backup_subdir}")
                return True
            else:
                # Remove empty backup directory
                backup_subdir.rmdir()
                logger.warning("⚠️ No session files found to backup")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to backup session: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Keep only the latest backup files"""
        try:
            backup_dirs = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()], 
                                key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove excess backups
            for old_backup in backup_dirs[self.max_backup_files:]:
                shutil.rmtree(old_backup)
                logger.info(f"🗑️ Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {e}")
    
    def remove_expired_sessions(self):
        """Remove expired session files"""
        try:
            session_files = [
                "vzl2_session.session",
                ":memory:.session",
                "vzl2_session.session-journal"
            ]
            
            removed_files = []
            for session_file in session_files:
                if os.path.exists(session_file):
                    os.remove(session_file)
                    removed_files.append(session_file)
                    logger.info(f"🗑️ Removed expired session: {session_file}")
            
            return removed_files
            
        except Exception as e:
            logger.error(f"❌ Failed to remove expired sessions: {e}")
            return []
    
    async def check_session_validity(self) -> Dict[str, Any]:
        """Check if current session is valid"""
        result = {
            "valid": False,
            "error": None,
            "error_type": None,
            "needs_recovery": False
        }
        
        try:
            # Create temporary client for testing
            if self.config.STRING_SESSION:
                test_client = TelegramClient(
                    StringSession(self.config.STRING_SESSION),
                    self.config.API_ID,
                    self.config.API_HASH
                )
            else:
                test_client = TelegramClient(
                    'vzl2_session_test',
                    self.config.API_ID,
                    self.config.API_HASH
                )
            
            await test_client.connect()
            
            # Check authorization
            if await test_client.is_user_authorized():
                # Additional check - try to get user info
                me = await test_client.get_me()
                result["valid"] = True
                result["user_info"] = {
                    "id": me.id,
                    "first_name": me.first_name,
                    "username": me.username
                }
                logger.info(f"✅ Session valid for user: {me.first_name} ({me.id})")
            else:
                result["needs_recovery"] = True
                result["error"] = "Session not authorized"
                result["error_type"] = "unauthorized"
                logger.warning("⚠️ Session not authorized")
            
            await test_client.disconnect()
            
        except SessionRevokedError as e:
            result["needs_recovery"] = True
            result["error"] = str(e)
            result["error_type"] = "session_revoked"
            logger.error(f"❌ Session revoked: {e}")
            
        except AuthKeyUnregisteredError as e:
            result["needs_recovery"] = True
            result["error"] = str(e)
            result["error_type"] = "auth_key_unregistered"
            logger.error(f"❌ Auth key unregistered: {e}")
            
        except AuthKeyDuplicatedError as e:
            result["needs_recovery"] = True
            result["error"] = str(e)
            result["error_type"] = "auth_key_duplicated"
            logger.error(f"❌ Auth key duplicated: {e}")
            
        except UnauthorizedError as e:
            result["needs_recovery"] = True
            result["error"] = str(e)
            result["error_type"] = "unauthorized"
            logger.error(f"❌ Unauthorized: {e}")
            
        except Exception as e:
            result["error"] = str(e)
            result["error_type"] = "unknown"
            logger.error(f"❌ Session check failed: {e}")
        
        # Update session info
        info = self.get_session_info()
        info["last_check"] = datetime.now().isoformat()
        self.save_session_info(info)
        
        return result
    
    async def interactive_recovery(self) -> bool:
        """Interactive session recovery process"""
        try:
            signature = vzoel_emoji.get_vzoel_signature()
            print(f"\n{signature} VZOEL SESSION RECOVERY MODE")
            print("=" * 50)
            print("🔄 Starting session recovery process...")
            print("📱 You will need access to your phone number for verification\n")
            
            # Get phone number
            while True:
                phone = input("📞 Enter your phone number (with country code, e.g., +628123456789): ").strip()
                if phone:
                    if not phone.startswith('+'):
                        phone = '+' + phone
                    break
                print("❌ Phone number cannot be empty!")
            
            # Create new client for recovery
            print("\n🔄 Creating new session...")
            client = TelegramClient(StringSession(), self.config.API_ID, self.config.API_HASH)
            await client.connect()
            
            # Send verification code
            print(f"📞 Sending verification code to: {phone}")
            try:
                await client.send_code_request(phone)
            except PhoneNumberInvalidError:
                print(f"❌ Invalid phone number: {phone}")
                print("   Please check the format (example: +628123456789)")
                await client.disconnect()
                return False
            except Exception as e:
                print(f"❌ Failed to send verification code: {e}")
                await client.disconnect()
                return False
            
            print("✅ Verification code sent!")
            print("📨 Check your Telegram app for the verification code\n")
            
            # Get verification code
            while True:
                try:
                    code = input("🔢 Enter verification code: ").strip()
                    if not code:
                        print("❌ Verification code cannot be empty!")
                        continue
                    
                    print("🔄 Verifying code...")
                    await client.sign_in(phone, code)
                    break
                    
                except PhoneCodeInvalidError:
                    print("❌ Invalid verification code! Please try again.")
                    continue
                except SessionPasswordNeededError:
                    # 2FA is enabled
                    print("\n🔐 Your account has 2FA (Two-Factor Authentication) enabled")
                    while True:
                        password = input("🔒 Enter your 2FA password: ")
                        try:
                            await client.sign_in(password=password)
                            break
                        except Exception as e:
                            print(f"❌ Invalid 2FA password: {e}")
                    break
                except Exception as e:
                    print(f"❌ Sign in error: {e}")
                    continue
            
            # Get user info
            me = await client.get_me()
            
            # Generate new string session
            new_string_session = client.session.save()
            
            print(f"\n🎉 New session created successfully!")
            print(f"👤 User: {me.first_name}")
            print(f"🆔 User ID: {me.id}")
            print(f"📞 Username: @{me.username or 'None'}")
            
            # Update .env file
            self._update_env_with_new_session(new_string_session)
            
            # Update session info
            info = self.get_session_info()
            info["recovery_count"] = info.get("recovery_count", 0) + 1
            info["last_recovery"] = datetime.now().isoformat()
            info["session_type"] = "string"
            self.save_session_info(info)
            
            await client.disconnect()
            
            print(f"\n✅ Session recovery completed!")
            print(f"📁 New session saved to .env file")
            print(f"🚀 You can now restart your bot")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n❌ Recovery process cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Recovery failed: {e}")
            return False
    
    def _update_env_with_new_session(self, new_string_session: str):
        """Update .env file with new string session"""
        try:
            if os.path.exists(".env"):
                with open(".env", 'r') as f:
                    content = f.read()
                
                # Replace STRING_SESSION line
                lines = content.split('\n')
                updated_lines = []
                session_updated = False
                
                for line in lines:
                    if line.startswith('STRING_SESSION='):
                        updated_lines.append(f'STRING_SESSION={new_string_session}')
                        session_updated = True
                    else:
                        updated_lines.append(line)
                
                # If STRING_SESSION line doesn't exist, add it
                if not session_updated:
                    # Find a good place to add it (after API_HASH)
                    for i, line in enumerate(updated_lines):
                        if line.startswith('API_HASH='):
                            updated_lines.insert(i + 1, f'STRING_SESSION={new_string_session}')
                            break
                
                # Write back to file
                with open(".env", 'w') as f:
                    f.write('\n'.join(updated_lines))
                
                logger.info("✅ Updated .env file with new session")
            
        except Exception as e:
            logger.error(f"❌ Failed to update .env file: {e}")
    
    async def auto_recovery_check(self) -> bool:
        """Automatic recovery check - non-interactive"""
        try:
            check_result = await self.check_session_validity()
            
            if check_result["valid"]:
                logger.info("✅ Session is valid, no recovery needed")
                return True
            
            if check_result["needs_recovery"]:
                signature = vzoel_emoji.get_vzoel_signature()
                logger.warning(f"⚠️ Session recovery needed: {check_result['error_type']}")
                
                # Backup current session before recovery
                self.backup_current_session()
                
                # Log the recovery event
                recovery_msg = vzoel_emoji.format_emoji_response(
                    ['warning', 'tools'],
                    f"**Session Recovery Required**\n"
                    f"Error: {check_result['error_type']}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Run recovery manually with: python session_recovery.py"
                )
                
                logger.warning(recovery_msg)
                
                # Remove expired session files
                removed_files = self.remove_expired_sessions()
                if removed_files:
                    logger.info(f"🗑️ Removed expired session files: {removed_files}")
                
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Auto recovery check failed: {e}")
            return False
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get recovery status and statistics"""
        info = self.get_session_info()
        backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        
        return {
            "session_info": info,
            "backup_count": len(backup_dirs),
            "backup_dir": str(self.backup_dir),
            "recovery_log_exists": os.path.exists(self.recovery_log_file),
            "last_check": info.get("last_check"),
            "last_recovery": info.get("last_recovery"),
            "total_recoveries": info.get("recovery_count", 0)
        }

async def main():
    """Main function for standalone execution"""
    try:
        print("""
╔══════════════════════════════════════════════════════════╗
║         🦊 Vzoel Fox's Session Recovery Tool               ║
║        Automatic Session Recovery and Management         ║
║            Created by: Vzoel Fox's                       ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        config = Config()
        recovery_manager = SessionRecoveryManager(config)
        
        print("🔍 Checking current session validity...")
        check_result = await recovery_manager.check_session_validity()
        
        if check_result["valid"]:
            print("✅ Current session is valid!")
            user_info = check_result.get("user_info", {})
            print(f"👤 User: {user_info.get('first_name', 'Unknown')}")
            print(f"🆔 ID: {user_info.get('id', 'Unknown')}")
            return
        
        if check_result["needs_recovery"]:
            print(f"⚠️ Session recovery needed: {check_result['error_type']}")
            print(f"❌ Error: {check_result['error']}")
            
            choice = input("\n🔄 Start recovery process? (y/n): ").strip().lower()
            if choice in ['y', 'yes', 'ya']:
                # Backup before recovery
                print("📁 Backing up current session...")
                recovery_manager.backup_current_session()
                
                # Start recovery
                success = await recovery_manager.interactive_recovery()
                
                if success:
                    print("\n🎉 Session recovery completed successfully!")
                    print("🚀 You can now restart your bot with the new session.")
                else:
                    print("\n❌ Session recovery failed.")
            else:
                print("❌ Recovery cancelled by user.")
        else:
            print(f"❌ Session check failed: {check_result['error']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())