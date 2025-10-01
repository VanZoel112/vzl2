"""
Vzoel Fox's Lutpan - Voice Chat Manager
Pure userbot voice chat control system

Commands:
- .jlvc - Join/Leave voice chat toggle
- .startvc - Create new voice chat in group

Author: Vzoel Fox's
Contact: @VZLfxs
"""

import asyncio
import logging
from typing import Dict, Optional
from telethon import TelegramClient
from telethon.tl.functions.phone import CreateGroupCallRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import ChatAdminRequiredError

logger = logging.getLogger(__name__)

try:
    from pytgcalls import PyTgCalls
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    logger.warning("py-tgcalls not available")


class VoiceChatManager:
    """
    Voice chat manager for pure userbot
    Handles VC creation and connection
    """

    def __init__(self, client: TelegramClient):
        self.client = client
        self.pytgcalls = None
        self.active_chats: Dict[int, Dict] = {}

        # Initialize PyTgCalls
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
                logger.info("Voice chat manager started")
                return True
            except Exception as e:
                logger.error(f"Start error: {e}")
                return False
        return False

    async def stop(self):
        """Stop voice chat manager"""
        if self.pytgcalls:
            try:
                await self.pytgcalls.stop()
                logger.info("Voice chat manager stopped")
            except Exception as e:
                logger.error(f"Stop error: {e}")

    async def create_voice_chat(self, chat_id: int) -> bool:
        """
        Create new voice chat in group

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

    async def join_voice_chat(self, chat_id: int) -> bool:
        """
        Join voice chat in group

        Args:
            chat_id: Target chat ID

        Returns:
            True if joined successfully
        """
        try:
            if not self.pytgcalls or not PYTGCALLS_AVAILABLE:
                logger.error("PyTgCalls not available")
                return False

            # Check if already in voice chat
            if chat_id in self.active_chats:
                return True

            # Note: Actual joining happens when play() is called
            # This marks the chat as ready for streaming
            self.active_chats[chat_id] = {
                'status': 'ready',
                'joined_at': asyncio.get_event_loop().time()
            }

            logger.info(f"Voice chat ready in {chat_id}")
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
                    await self.pytgcalls.leave_call(chat_id)
                except Exception as e:
                    logger.warning(f"Leave call error: {e}")

                self.active_chats.pop(chat_id, None)
                logger.info(f"Left voice chat {chat_id}")
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
                success = await self.join_voice_chat(chat_id)
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
            'initialized': self.pytgcalls is not None
        }
