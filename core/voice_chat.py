"""
Vzoel Fox's Lutpan - Voice Chat Manager
Pure userbot voice chat control with PyTgCalls

Features:
- Direct VC join/leave as userbot
- Silent audio stream for idle connection
- PyTgCalls integration for pure userbot mode
- No bot assistant required

Author: Vzoel Fox's
Contact: @VZLfxs
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, Optional
from telethon import TelegramClient
from telethon.tl.functions.phone import CreateGroupCallRequest
from telethon.errors import ChatAdminRequiredError

logger = logging.getLogger(__name__)

try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    logger.warning("py-tgcalls not available")
    MediaStream = None
    AudioQuality = None


class VoiceChatManager:
    """
    Voice chat manager for pure userbot
    Handles VC join/leave with PyTgCalls as userbot (not bot)
    """

    def __init__(self, client: TelegramClient):
        self.client = client
        self.pytgcalls = None
        self.active_chats: Dict[int, Dict] = {}
        self.silence_file = None

        # Initialize PyTgCalls for USERBOT mode
        if PYTGCALLS_AVAILABLE:
            try:
                self.pytgcalls = PyTgCalls(self.client)
            except Exception as e:
                logger.error(f"PyTgCalls init error: {e}")
                self.pytgcalls = None

    async def start(self) -> bool:
        """Start voice chat manager"""
        if self.pytgcalls and PYTGCALLS_AVAILABLE:
            try:
                await self.pytgcalls.start()

                # Create silent audio file for idle VC connection
                self.silence_file = await self._create_silence_file()

                logger.info("Voice chat manager started (pure userbot mode)")
                return True
            except Exception as e:
                logger.error(f"Start error: {e}")
                return False
        return False

    async def stop(self):
        """Stop voice chat manager"""
        if self.pytgcalls:
            try:
                # Leave all active VCs
                for chat_id in list(self.active_chats.keys()):
                    await self.leave_voice_chat(chat_id)

                await self.pytgcalls.stop()

                # Cleanup silence file
                if self.silence_file and os.path.exists(self.silence_file):
                    os.remove(self.silence_file)

                logger.info("Voice chat manager stopped")
            except Exception as e:
                logger.error(f"Stop error: {e}")

    async def _create_silence_file(self) -> Optional[str]:
        """
        Create silent audio file for idle VC presence
        Returns path to silence file
        """
        try:
            temp_dir = tempfile.gettempdir()
            silence_file = os.path.join(temp_dir, 'vzl2_silence.raw')

            if not os.path.exists(silence_file):
                # Create 1-second silent audio (48kHz, 16-bit, stereo)
                # This allows userbot to stay in VC without playing anything
                silent_data = b'\x00' * (48000 * 2 * 2)  # 48kHz * 2 channels * 2 bytes
                with open(silence_file, 'wb') as f:
                    f.write(silent_data)

                logger.info(f"Silent audio created at {silence_file}")

            return silence_file
        except Exception as e:
            logger.error(f"Failed to create silence file: {e}")
            return None

    async def create_voice_chat(self, chat_id: int) -> bool:
        """
        Create new voice chat in group (requires admin rights)

        Args:
            chat_id: Target chat ID

        Returns:
            True if created successfully
        """
        try:
            # Get chat entity
            chat = await self.client.get_entity(chat_id)

            # Create voice chat using Telegram API
            result = await self.client(CreateGroupCallRequest(
                peer=chat,
                random_id=self.client._get_client_id()
            ))

            logger.info(f"Voice chat created in {chat_id}")
            return True

        except ChatAdminRequiredError:
            logger.error(f"Admin rights required to create VC in {chat_id}")
            return False
        except Exception as e:
            logger.error(f"Create VC error: {e}")
            return False

    async def join_voice_chat(self, chat_id: int, silent: bool = True) -> bool:
        """
        Join voice chat as userbot with PyTgCalls

        Args:
            chat_id: Target chat ID
            silent: If True, join with silent audio stream (idle presence)

        Returns:
            True if joined successfully
        """
        try:
            if not self.pytgcalls or not PYTGCALLS_AVAILABLE:
                logger.error("PyTgCalls not available")
                return False

            # Check if already in voice chat
            if chat_id in self.active_chats:
                logger.info(f"Already in VC {chat_id}")
                return True

            # Join with silent stream (userbot idle presence)
            if silent and self.silence_file:
                try:
                    # Create media stream from silent audio
                    media_stream = MediaStream(
                        self.silence_file,
                        audio_parameters=AudioQuality.HIGH
                    )

                    # Join VC by playing silent stream
                    await self.pytgcalls.play(
                        chat_id,
                        media_stream
                    )

                    self.active_chats[chat_id] = {
                        'status': 'connected',
                        'mode': 'silent',
                        'joined_at': asyncio.get_event_loop().time()
                    }

                    logger.info(f"Joined VC {chat_id} in silent mode (pure userbot)")
                    return True

                except Exception as e:
                    logger.error(f"Failed to join with silent stream: {e}")
                    return False
            else:
                # Mark as ready (will join when music plays)
                self.active_chats[chat_id] = {
                    'status': 'ready',
                    'mode': 'waiting',
                    'joined_at': asyncio.get_event_loop().time()
                }
                logger.info(f"VC {chat_id} marked as ready")
                return True

        except Exception as e:
            logger.error(f"Join VC error: {e}")
            return False

    async def leave_voice_chat(self, chat_id: int) -> bool:
        """
        Leave voice chat

        Args:
            chat_id: Target chat ID

        Returns:
            True if left successfully
        """
        try:
            if self.pytgcalls and chat_id in self.active_chats:
                try:
                    # Leave the group call
                    await self.pytgcalls.leave_call(chat_id)
                    logger.info(f"Left VC call {chat_id}")
                except Exception as e:
                    logger.warning(f"Leave call error: {e}")

                # Remove from active chats
                self.active_chats.pop(chat_id, None)
                logger.info(f"Removed {chat_id} from active chats")
                return True

            return False

        except Exception as e:
            logger.error(f"Leave VC error: {e}")
            return False

    async def toggle_voice_chat(self, chat_id: int) -> tuple:
        """
        Toggle join/leave voice chat

        Args:
            chat_id: Target chat ID

        Returns:
            Tuple of (success: bool, action: str)
            action is either 'joined' or 'left'
        """
        try:
            if chat_id in self.active_chats:
                # Already in VC, leave
                success = await self.leave_voice_chat(chat_id)
                return (success, 'left')
            else:
                # Not in VC, join
                success = await self.join_voice_chat(chat_id, silent=True)
                return (success, 'joined')

        except Exception as e:
            logger.error(f"Toggle VC error: {e}")
            return (False, 'error')

    def is_in_voice_chat(self, chat_id: int) -> bool:
        """Check if currently in voice chat"""
        return chat_id in self.active_chats

    def get_active_chats(self) -> Dict[int, Dict]:
        """Get all active voice chats"""
        return self.active_chats.copy()

    def get_stats(self) -> Dict:
        """Get voice chat statistics"""
        return {
            'active_chats': len(self.active_chats),
            'available': PYTGCALLS_AVAILABLE,
            'initialized': self.pytgcalls is not None,
            'mode': 'pure_userbot'
        }
