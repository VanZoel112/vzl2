"""
Voice Chat Manager for VzoelFox
Handles voice chat connections and audio streaming
Compatible with premium emoji mapping and markdown
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from telethon import TelegramClient

# Safe PyTgCalls import dengan fallback
try:
    from pytgcalls import PyTgCalls
    try:
        # Try new API first
        from pytgcalls.types.input_stream import AudioPiped, VideoPiped
    except ImportError:
        try:
            # Try old API
            from pytgcalls.types import AudioPiped, VideoPiped
        except ImportError:
            # Fallback for newer versions
            from pytgcalls.types.input_stream.audio_piped import AudioPiped
            from pytgcalls.types.input_stream.video_piped import VideoPiped
    
    from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound
    PYTGCALLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PyTgCalls not available: {e}")
    PYTGCALLS_AVAILABLE = False

# Import VzoelFox emoji mappings
try:
    from config import EMOJI_MAPPING
    from utils import get_emoji
except ImportError:
    EMOJI_MAPPING = {}
    def get_emoji(key: str) -> str:
        return "🎵"

class VoiceChatManager:
    """Voice chat manager dengan premium emoji support"""
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.app = None
        self.active_calls: Dict[int, Dict[str, Any]] = {}
        self.music_queue: Dict[int, list] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize PyTgCalls jika available
        if PYTGCALLS_AVAILABLE:
            try:
                self.app = PyTgCalls(client)
            except Exception as e:
                self.logger.error(f"Failed to initialize PyTgCalls: {e}")
                self.app = None
        else:
            self.logger.warning("PyTgCalls not available - voice chat disabled")
        
    async def start(self):
        """Start voice chat manager"""
        if not self.app or not PYTGCALLS_AVAILABLE:
            self.logger.warning("PyTgCalls not available - voice chat disabled")
            return False
            
        try:
            await self.app.start()
            self.logger.info(f"{get_emoji('success')} Voice chat manager started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start voice manager: {e}")
            return False
    
    async def stop(self):
        """Stop voice chat manager"""
        try:
            await self.app.stop()
            self.logger.info(f"{get_emoji('stop')} Voice chat manager stopped")
        except Exception as e:
            self.logger.error(f"Error stopping voice manager: {e}")
    
    async def join_voice_chat(self, chat_id: int) -> bool:
        """Join voice chat dengan premium emoji feedback"""
        try:
            if chat_id in self.active_calls:
                return True

            # Use correct PyTgCalls API based on documentation
            from pytgcalls.types.input_stream import InputStream, InputAudioStream
            from pytgcalls import StreamType

            # Create proper input stream (RAW audio format required)
            input_stream = InputStream(
                InputAudioStream("http://duramecho.com/Misc/SilentCd/Silence01s.wav")
            )

            await self.app.join_group_call(
                chat_id,
                input_stream,
                stream_type=StreamType().local_stream
            )

            self.active_calls[chat_id] = {
                'status': 'connected',
                'current_track': None,
                'volume': 100
            }

            self.logger.info(f"{get_emoji('join')} Joined voice chat: {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to join voice chat {chat_id}: {e}")
            return False
    
    async def leave_voice_chat(self, chat_id: int) -> bool:
        """Leave voice chat"""
        try:
            if chat_id not in self.active_calls:
                return True

            # Use correct PyTgCalls API - leave_current_group_call method
            await self.app.leave_current_group_call()

            if chat_id in self.active_calls:
                del self.active_calls[chat_id]
            if chat_id in self.music_queue:
                del self.music_queue[chat_id]

            self.logger.info(f"{get_emoji('leave')} Left voice chat: {chat_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to leave voice chat {chat_id}: {e}")
            return False
    
    async def play_audio(self, chat_id: int, source: str, title: str = "Unknown") -> bool:
        """Play audio in voice chat"""
        try:
            if chat_id not in self.active_calls:
                if not await self.join_voice_chat(chat_id):
                    return False
            
            # Try new API first (PyTgCalls 2.x)
            try:
                await self.app.play(
                    chat_id,
                    AudioPiped(source)
                )
            except AttributeError:
                # Fallback to old API (PyTgCalls 1.x)
                await self.app.change_stream(
                    chat_id,
                    AudioPiped(source)
                )
            
            self.active_calls[chat_id]['current_track'] = title
            self.active_calls[chat_id]['status'] = 'playing'
            
            self.logger.info(f"{get_emoji('play')} Playing: {title} in {chat_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to play audio in {chat_id}: {e}")
            return False
    
    async def pause_audio(self, chat_id: int) -> bool:
        """Pause audio"""
        try:
            # Try new API first (PyTgCalls 2.x)
            try:
                await self.app.pause(chat_id)
            except AttributeError:
                # Fallback to old API (PyTgCalls 1.x)
                await self.app.pause_stream(chat_id)

            self.active_calls[chat_id]['status'] = 'paused'
            self.logger.info(f"{get_emoji('pause')} Paused audio in {chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pause audio in {chat_id}: {e}")
            return False
    
    async def resume_audio(self, chat_id: int) -> bool:
        """Resume audio"""
        try:
            # Try new API first (PyTgCalls 2.x)
            try:
                await self.app.resume(chat_id)
            except AttributeError:
                # Fallback to old API (PyTgCalls 1.x)
                await self.app.resume_stream(chat_id)

            self.active_calls[chat_id]['status'] = 'playing'
            self.logger.info(f"{get_emoji('play')} Resumed audio in {chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to resume audio in {chat_id}: {e}")
            return False
    
    async def stop_audio(self, chat_id: int) -> bool:
        """Stop audio"""
        try:
            # Try new API first (PyTgCalls 2.x)
            try:
                await self.app.play(
                    chat_id,
                    AudioPiped("http://duramecho.com/Misc/SilentCd/Silence01s.wav")
                )
            except AttributeError:
                # Fallback to old API (PyTgCalls 1.x)
                await self.app.change_stream(
                    chat_id,
                    AudioPiped("http://duramecho.com/Misc/SilentCd/Silence01s.wav")
                )

            self.active_calls[chat_id]['status'] = 'stopped'
            self.active_calls[chat_id]['current_track'] = None
            self.logger.info(f"{get_emoji('stop')} Stopped audio in {chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop audio in {chat_id}: {e}")
            return False
    
    async def set_volume(self, chat_id: int, volume: int) -> bool:
        """Set volume (0-200)"""
        try:
            volume = max(0, min(200, volume))

            # Try new API first (PyTgCalls 2.x)
            try:
                await self.app.set_volume(chat_id, volume)
            except AttributeError:
                # Fallback to old API (PyTgCalls 1.x)
                await self.app.change_volume(chat_id, volume)

            self.active_calls[chat_id]['volume'] = volume
            self.logger.info(f"{get_emoji('volume')} Volume set to {volume}% in {chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set volume in {chat_id}: {e}")
            return False
    
    def add_to_queue(self, chat_id: int, source: str, title: str):
        """Add track to queue"""
        if chat_id not in self.music_queue:
            self.music_queue[chat_id] = []
        
        self.music_queue[chat_id].append({
            'source': source,
            'title': title
        })
        
        self.logger.info(f"{get_emoji('queue')} Added to queue: {title}")
    
    def get_queue(self, chat_id: int) -> list:
        """Get current queue"""
        return self.music_queue.get(chat_id, [])
    
    async def play_next(self, chat_id: int) -> bool:
        """Play next track in queue"""
        try:
            if chat_id not in self.music_queue or not self.music_queue[chat_id]:
                return False
            
            next_track = self.music_queue[chat_id].pop(0)
            return await self.play_audio(
                chat_id, 
                next_track['source'], 
                next_track['title']
            )
        except Exception as e:
            self.logger.error(f"Failed to play next track: {e}")
            return False
    
    def get_voice_chat_info(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get voice chat status info"""
        return self.active_calls.get(chat_id)
    
    def is_connected(self, chat_id: int) -> bool:
        """Check if connected to voice chat"""
        return chat_id in self.active_calls
    
    def get_all_active_calls(self) -> Dict[int, Dict[str, Any]]:
        """Get all active voice chat calls"""
        return self.active_calls.copy()

# Global voice manager instance
voice_manager: Optional[VoiceChatManager] = None

def get_voice_manager() -> Optional[VoiceChatManager]:
    """Get voice manager instance"""
    return voice_manager

async def initialize_voice_manager(client: TelegramClient) -> bool:
    """Initialize voice manager"""
    global voice_manager
    try:
        voice_manager = VoiceChatManager(client)
        if not PYTGCALLS_AVAILABLE:
            logging.info("Voice chat disabled - PyTgCalls not available")
            return False
        return await voice_manager.start()
    except Exception as e:
        logging.error(f"Failed to initialize voice manager: {e}")
        return False

async def cleanup_voice_manager():
    """Cleanup voice manager"""
    global voice_manager
    if voice_manager:
        await voice_manager.stop()
        voice_manager = None