"""
VzoelFox's Assistant v2 - Advanced Client
Enhanced client with plugin system and auto-update features
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

import os
import sys
import asyncio
import logging
import importlib
import importlib.util
import inspect
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import json
import time
import hashlib

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, ApiIdInvalidError
from telethon.tl.types import User
from telethon.sessions import StringSession

from emoji_handler_premium import vzoel_emoji
from config import Config

logger = logging.getLogger(__name__)

class PluginManager:
    """VzoelFox's Advanced Plugin Manager"""
    
    def __init__(self, client, vzoel_client_instance=None):
        self.client = client
        self.vzoel_client = vzoel_client_instance
        self.plugins: Dict[str, Any] = {}
        self.plugin_commands: Dict[str, str] = {}
        self.plugins_dir = Path("plugins")
        self.plugin_info_file = ".plugin_info.json"
        self.load_order = []
        
    def create_plugins_directory(self):
        """Create plugins directory if it doesn't exist"""
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(exist_ok=True)
            logger.info(f"🤩 Created plugins directory: {self.plugins_dir}")
            
            # Create __init__.py for proper module import
            init_file = self.plugins_dir / "__init__.py"
            init_file.write_text("# VzoelFox's Assistant Plugins\n")
    
    def save_plugin_info(self):
        """Save plugin information to file"""
        plugin_data = {
            "total_plugins": len(self.plugins),
            "loaded_plugins": list(self.plugins.keys()),
            "plugin_commands": self.plugin_commands,
            "load_order": self.load_order,
            "last_updated": time.time()
        }
        
        with open(self.plugin_info_file, 'w') as f:
            json.dump(plugin_data, f, indent=2)
    
    def load_plugin_info(self) -> Dict:
        """Load plugin information from file"""
        if os.path.exists(self.plugin_info_file):
            try:
                with open(self.plugin_info_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load plugin info: {e}")
        return {}
    
    def get_plugin_hash(self, plugin_path: Path) -> str:
        """Get hash of plugin file for change detection"""
        try:
            with open(plugin_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    async def load_plugin(self, plugin_file: Path) -> bool:
        """Load a single plugin"""
        try:
            # Import vzoel_client here to avoid circular import
            global vzoel_client
            
            plugin_name = plugin_file.stem
            
            # Skip if already loaded and not changed
            if plugin_name in self.plugins:
                return True
            
            # Import plugin module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
            if not spec or not spec.loader:
                logger.error(f"❌ Failed to load spec for {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Register plugin
            self.plugins[plugin_name] = module
            self.load_order.append(plugin_name)
            
            # Register event handlers if available
            handlers_registered = 0
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '__call__') and callable(obj):
                    # Skip built-in functions and non-handler functions
                    if name.startswith('_') or name in ['vzoel_init']:
                        continue
                    
                    handler_registered = False
                    
                    # Method 1: Try to register as @events.register decorated function first
                    if name.endswith('_handler') or name.endswith('handler'):
                        try:
                            self.client.add_event_handler(obj)
                            handlers_registered += 1
                            handler_registered = True
                            
                            # Track commands if available
                            if hasattr(obj, 'command'):
                                self.plugin_commands[obj.command] = plugin_name
                                
                            logger.debug(f"Registered {name} via decorator method")
                        except Exception as e:
                            logger.debug(f"Could not register {name} as decorated handler: {e}")
                    
                    # Method 2: Check for explicit handler attribute (fallback)
                    if not handler_registered and hasattr(obj, 'handler') and obj.handler is not None:
                        try:
                            self.client.add_event_handler(obj, obj.handler)
                            handlers_registered += 1
                            handler_registered = True
                            
                            # Track commands
                            if hasattr(obj, 'command'):
                                self.plugin_commands[obj.command] = plugin_name
                                
                            logger.debug(f"Registered {name} via handler attribute")
                        except Exception as e:
                            logger.debug(f"Could not register {name} with handler attribute: {e}")
                    
                    # Method 3: Check for alternative _handler attribute
                    if not handler_registered and hasattr(obj, '_handler'):
                        try:
                            self.client.add_event_handler(obj, obj._handler)
                            handlers_registered += 1
                            handler_registered = True
                            logger.debug(f"Registered {name} via _handler attribute")
                        except Exception as e:
                            logger.debug(f"Could not register {name} with _handler: {e}")
            
            # Call plugin initialization if available  
            if hasattr(module, 'vzoel_init'):
                await module.vzoel_init(self.vzoel_client, vzoel_emoji)
            
            logger.info(f"🤩 Loaded plugin: {plugin_name} ({handlers_registered} handlers)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_file.name}: {e}")
            return False
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        try:
            if plugin_name in self.plugins:
                # Remove old handlers (if possible)
                logger.info(f"⚙️ Reloading plugin: {plugin_name}")
                
                # Remove from loaded plugins
                del self.plugins[plugin_name]
                
                # Reload
                plugin_file = self.plugins_dir / f"{plugin_name}.py"
                if plugin_file.exists():
                    return await self.load_plugin(plugin_file)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to reload plugin {plugin_name}: {e}")
            return False
    
    async def load_all_plugins(self) -> Dict[str, bool]:
        """Load all plugins from plugins directory"""
        self.create_plugins_directory()
        
        results = {}
        plugin_files = list(self.plugins_dir.glob("*.py"))
        
        if not plugin_files:
            logger.info("⛈ No plugins found in plugins/ directory")
            return results
        
        logger.info(f"🎚 Found {len(plugin_files)} plugin(s) to load...")
        
        for plugin_file in plugin_files:
            if plugin_file.name.startswith('_'):
                continue  # Skip private files
            
            plugin_name = plugin_file.stem
            success = await self.load_plugin(plugin_file)
            results[plugin_name] = success
        
        # Save plugin info
        self.save_plugin_info()
        
        loaded_count = sum(results.values())
        total_count = len(results)
        
        signature = vzoel_emoji.get_vzoel_signature()
        logger.info(f"{signature} Loaded {loaded_count}/{total_count} plugins successfully")
        
        return results
    
    def get_plugin_list(self) -> List[Dict]:
        """Get list of loaded plugins"""
        plugin_list = []
        for name, module in self.plugins.items():
            info = {
                'name': name,
                'file': f"{name}.py",
                'description': getattr(module, '__doc__', 'No description'),
                'commands': [cmd for cmd, plugin in self.plugin_commands.items() if plugin == name]
            }
            plugin_list.append(info)
        return plugin_list

class AutoUpdater:
    """VzoelFox's Auto-Update System"""
    
    def __init__(self, client):
        self.client = client
        self.repo_url = "https://github.com/VanZoel112/vzl2.git"
        self.update_branch = "main"
        self.last_check = 0
        self.check_interval = 3600  # 1 hour
        
    async def check_for_updates(self) -> Dict:
        """Check if updates are available"""
        try:
            # Get current commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'], 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                return {"error": "Not a git repository"}
            
            current_commit = result.stdout.strip()
            
            # Fetch latest changes
            subprocess.run(
                ['git', 'fetch', 'origin', self.update_branch], 
                capture_output=True, 
                cwd=os.getcwd()
            )
            
            # Get remote commit hash
            result = subprocess.run(
                ['git', 'rev-parse', f'origin/{self.update_branch}'], 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                return {"error": "Failed to get remote commit"}
            
            remote_commit = result.stdout.strip()
            
            # Check if update is needed
            needs_update = current_commit != remote_commit
            
            return {
                "needs_update": needs_update,
                "current_commit": current_commit[:7],
                "remote_commit": remote_commit[:7],
                "current_full": current_commit,
                "remote_full": remote_commit
            }
            
        except Exception as e:
            logger.error(f"❌ Update check failed: {e}")
            return {"error": str(e)}
    
    async def perform_update(self, force: bool = False) -> Dict:
        """Perform git pull update"""
        try:
            signature = vzoel_emoji.get_vzoel_signature()
            
            if not force:
                # Check for updates first
                update_info = await self.check_for_updates()
                if "error" in update_info:
                    return update_info
                
                if not update_info["needs_update"]:
                    return {"status": "already_updated", "message": "Already up to date"}
            
            logger.info(f"⚙️ Starting VzoelFox's Assistant update...")
            
            # Stash local changes if any
            subprocess.run(['git', 'stash'], cwd=os.getcwd())
            
            # Pull latest changes
            result = subprocess.run(
                ['git', 'pull', 'origin', self.update_branch],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                return {
                    "status": "failed",
                    "error": result.stderr,
                    "message": "Git pull failed"
                }
            
            # Get new commit info
            commit_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%h - %s'],
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            new_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "Unknown"
            
            logger.info(f"{signature} Update completed successfully!")
            logger.info(f"🤩 Latest commit: {new_commit}")
            
            return {
                "status": "success",
                "new_commit": new_commit,
                "message": f"Updated to: {new_commit}",
                "restart_required": True
            }
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def auto_check_updates(self):
        """Automatically check for updates periodically"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                
                current_time = time.time()
                if current_time - self.last_check >= self.check_interval:
                    update_info = await self.check_for_updates()
                    
                    if "needs_update" in update_info and update_info["needs_update"]:
                        signature = vzoel_emoji.get_vzoel_signature()
                        logger.info(f"{signature} New update available! Use .update to install")
                        
                        # Notify via log chat if configured
                        if hasattr(self.client, 'config') and self.client.config.VZOEL_LOG_CHAT:
                            try:
                                update_msg = vzoel_emoji.format_emoji_response(
                                    ['biru', 'utama'], 
                                    f"**Update Available!**\n"
                                    f"Current: `{update_info['current_commit']}`\n"
                                    f"Latest: `{update_info['remote_commit']}`\n"
                                    f"Use `.update` to install"
                                )
                                await self.client.send_message(self.client.config.VZOEL_LOG_CHAT, update_msg)
                            except Exception as e:
                                logger.debug(f"Failed to send update notification: {e}")
                    
                    self.last_check = current_time
                    
            except Exception as e:
                logger.error(f"Auto update check error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

class VzoelFoxClient:
    """VzoelFox's Advanced Assistant Client"""
    
    def __init__(self):
        self.client: Optional[TelegramClient] = None
        self.config = Config()
        self.plugin_manager: Optional[PluginManager] = None
        self.auto_updater: Optional[AutoUpdater] = None
        self.is_running = False
        self.start_time = time.time()
        self.stats = {
            'commands_executed': 0,
            'plugins_loaded': 0,
            'uptime_start': self.start_time
        }
        
    async def initialize_client(self) -> bool:
        """Initialize the client with session"""
        try:
            if self.config.STRING_SESSION:
                logger.info("🤩 Using string session...")
                self.client = TelegramClient(
                    StringSession(self.config.STRING_SESSION),
                    self.config.API_ID,
                    self.config.API_HASH
                )
            else:
                logger.info("⚙️ Using file session...")
                self.client = TelegramClient(
                    'vzl2_session',
                    self.config.API_ID,
                    self.config.API_HASH
                )
            
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                logger.error("❌ Client not authorized!")
                logger.error("🔑 STRING_SESSION tidak ditemukan atau tidak valid")
                logger.error("📱 Jalankan generate_session.py untuk membuat session baru:")
                logger.error("   python generate_session.py")
                return False
            
            # Get user info
            me = await self.client.get_me()
            signature = vzoel_emoji.get_vzoel_signature()
            
            logger.info(f"{signature} Connected as: {me.first_name} (@{me.username or 'No username'})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            if "STRING_SESSION" in str(e) or "unauthorized" in str(e).lower():
                logger.error("🔑 Session tidak valid atau tidak ditemukan")
                logger.error("📱 Jalankan generate_session.py untuk membuat session baru:")
                logger.error("   python generate_session.py")
            return False
    
    async def setup_components(self):
        """Setup plugin manager and auto-updater"""
        try:
            # Initialize plugin manager
            self.plugin_manager = PluginManager(self.client, self)
            
            # Initialize auto-updater
            self.auto_updater = AutoUpdater(self.client)
            
            # Load plugins
            plugin_results = await self.plugin_manager.load_all_plugins()
            self.stats['plugins_loaded'] = len([r for r in plugin_results.values() if r])
            
            # Start auto-update checker in background
            asyncio.create_task(self.auto_updater.auto_check_updates())
            
            logger.info("🎚 All components initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup components: {e}")
    
    async def start(self) -> bool:
        """Start the VzoelFox's Assistant client"""
        try:
            signature = vzoel_emoji.get_vzoel_signature()
            logger.info(f"{signature} Starting VzoelFox's Assistant v2...")
            
            # Initialize client
            if not await self.initialize_client():
                return False
            
            # Setup components
            await self.setup_components()
            
            # Mark as running
            self.is_running = True
            
            # Startup message
            startup_msg = vzoel_emoji.format_emoji_response(
                ['utama', 'petir', 'aktif'],
                f"VzoelFox's Assistant v2 is now ACTIVE!\n"
                f"🤩 Plugins loaded: {self.stats['plugins_loaded']}\n"
                f"⚙️ Auto-updater: Active"
            )
            
            logger.info(f"{signature} {startup_msg}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start client: {e}")
            return False
    
    async def stop(self):
        """Stop the client gracefully"""
        try:
            if self.client and self.is_running:
                logger.info("⛈ Stopping VzoelFox's Assistant...")
                await self.client.disconnect()
                self.is_running = False
                
                signature = vzoel_emoji.get_vzoel_signature()
                logger.info(f"{signature} VzoelFox's Assistant stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping client: {e}")
    
    def get_stats(self) -> Dict:
        """Get client statistics"""
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': int(uptime),
            'uptime_formatted': f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
            'commands_executed': self.stats['commands_executed'],
            'plugins_loaded': self.stats['plugins_loaded'],
            'is_running': self.is_running
        }
    
    def increment_command_count(self):
        """Increment command execution counter"""
        self.stats['commands_executed'] += 1

# Global client instance
vzoel_client = VzoelFoxClient()