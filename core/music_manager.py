#!/usr/bin/env python3
"""
Music Manager for Pure Userbot
Uses py-tgcalls for voice chat streaming (userbot mode only)

Author: Vzoel Fox's Lutpan
Version: 3.0.0 (Pure Userbot)
"""

import asyncio
import logging
import os
import time
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    logger.warning("yt-dlp not available")

try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    logger.warning("py-tgcalls not available")
    MediaStream = None
    AudioQuality = None


class MusicManager:
    """Music manager for pure userbot with voice chat streaming"""

    def __init__(self, userbot_client):
        """
        Initialize music manager

        Args:
            userbot_client: Telethon client (userbot)
        """
        self.client = userbot_client
        self.download_path = Path("downloads/musik")
        self.download_path.mkdir(parents=True, exist_ok=True)

        # PyTgCalls instance (untuk userbot)
        self.pytgcalls = None
        self.streaming_available = PYTGCALLS_AVAILABLE

        # Queue per chat
        self.queues: Dict[int, List[Dict]] = {}

        # Currently playing
        self.current_song: Dict[int, Dict] = {}

        # Active voice chats
        self.active_calls: Dict[int, bool] = {}

        # Rate limiting
        self.last_request: Dict[int, float] = {}
        self.cooldown_seconds = 3

        # Initialize PyTgCalls untuk userbot
        if self.streaming_available:
            try:
                self.pytgcalls = PyTgCalls(self.client)
                logger.info("PyTgCalls initialized for userbot")
            except Exception as e:
                logger.error(f"Failed to initialize PyTgCalls: {e}")
                self.streaming_available = False

    async def start(self):
        """Start music manager"""
        if self.pytgcalls and self.streaming_available:
            try:
                await self.pytgcalls.start()
                logger.info("🎵 Music streaming ready (userbot mode)")
            except Exception as e:
                logger.error(f"Failed to start PyTgCalls: {e}")
                self.streaming_available = False

        if not self.streaming_available:
            logger.info("🎵 Music system ready (download mode only)")

    async def stop(self):
        """Stop music manager"""
        if self.pytgcalls:
            try:
                for chat_id in list(self.active_calls.keys()):
                    await self.leave_voice_chat(chat_id)
                logger.info("Music manager stopped")
            except Exception as e:
                logger.error(f"Error stopping: {e}")

    async def search_song(self, query: str) -> Optional[Dict]:
        """Search song on YouTube"""
        if not YTDLP_AVAILABLE:
            return None

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch:{query}" if not query.startswith('http') else query
                info = ydl.extract_info(search_query, download=False)

                if 'entries' in info:
                    info = info['entries'][0]

                return {
                    'title': info.get('title', 'Unknown'),
                    'url': info.get('url'),
                    'webpage_url': info.get('webpage_url'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return None

    async def download_audio(self, url: str, title: str) -> Optional[str]:
        """Download audio as MP3"""
        if not YTDLP_AVAILABLE:
            return None

        try:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            output_template = str(self.download_path / f"{safe_title}.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Find downloaded file
            for ext in ['mp3', 'm4a', 'webm', 'opus']:
                file_path = self.download_path / f"{safe_title}.{ext}"
                if file_path.exists():
                    return str(file_path)

            return None

        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    async def play_stream(self, chat_id: int, query: str, requester_id: int) -> Dict:
        """
        Play music - stream to VC or download

        Args:
            chat_id: Target chat ID
            query: Search query or URL
            requester_id: User who requested

        Returns:
            Dict with status and info
        """
        # Rate limiting
        current_time = time.time()
        if requester_id in self.last_request:
            if current_time - self.last_request[requester_id] < self.cooldown_seconds:
                return {
                    'success': False,
                    'error': f'Please wait {self.cooldown_seconds} seconds between requests'
                }

        self.last_request[requester_id] = current_time

        try:
            # Search song
            song_info = await self.search_song(query)
            if not song_info:
                return {'success': False, 'error': 'Song not found'}

            # STREAMING MODE (if available)
            if self.streaming_available and self.pytgcalls:
                # Check if already playing
                if chat_id in self.active_calls and self.active_calls[chat_id]:
                    # Add to queue
                    if chat_id not in self.queues:
                        self.queues[chat_id] = []
                    self.queues[chat_id].append(song_info)
                    return {
                        'success': True,
                        'queued': True,
                        'position': len(self.queues[chat_id]),
                        'song': song_info,
                        'streaming': True
                    }

                try:
                    # Stream from YouTube URL
                    youtube_url = song_info.get('webpage_url')

                    # Create media stream
                    media_stream = MediaStream(
                        youtube_url,
                        AudioQuality.HIGH
                    )

                    # Play in voice chat
                    await self.pytgcalls.play(
                        chat_id,
                        media_stream
                    )

                    self.active_calls[chat_id] = True
                    self.current_song[chat_id] = song_info

                    logger.info(f"Streaming in chat {chat_id}: {song_info['title']}")

                    return {
                        'success': True,
                        'song': song_info,
                        'streaming': True,
                        'joined_vc': True
                    }

                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    # Fallback to download
                    self.streaming_available = False

            # DOWNLOAD MODE (fallback)
            logger.info("Using download mode")

            file_path = await self.download_audio(song_info['url'], song_info['title'][:50])

            if not file_path:
                return {'success': False, 'error': 'Download failed'}

            self.current_song[chat_id] = {
                **song_info,
                'file_path': file_path
            }

            return {
                'success': True,
                'song': song_info,
                'file_path': file_path,
                'streaming': False
            }

        except Exception as e:
            logger.error(f"Error in play_stream: {e}")
            return {'success': False, 'error': str(e)}

    async def stop_stream(self, chat_id: int) -> bool:
        """Stop stream and clear queue"""
        try:
            if self.streaming_available and chat_id in self.active_calls:
                await self.leave_voice_chat(chat_id)

            if chat_id in self.queues:
                self.queues[chat_id].clear()
            if chat_id in self.current_song:
                del self.current_song[chat_id]

            return True
        except Exception as e:
            logger.error(f"Error stopping: {e}")
            return False

    async def pause_stream(self, chat_id: int) -> bool:
        """Pause stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.pause_stream(chat_id)
                logger.info(f"Paused stream in {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Error pausing: {e}")
        return False

    async def resume_stream(self, chat_id: int) -> bool:
        """Resume stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.resume_stream(chat_id)
                logger.info(f"Resumed stream in {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Error resuming: {e}")
        return False

    async def join_voice_chat(self, chat_id: int) -> bool:
        """Join voice chat (auto joins on play)"""
        try:
            if not self.streaming_available or not self.pytgcalls:
                return False

            if chat_id in self.active_calls and self.active_calls[chat_id]:
                return True

            # PyTgCalls joins automatically when play() is called
            logger.info(f"VC ready for {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error preparing VC: {e}")
            return False

    async def leave_voice_chat(self, chat_id: int) -> bool:
        """Leave voice chat"""
        try:
            if self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.leave_call(chat_id)
                self.active_calls.pop(chat_id, None)
                logger.info(f"Left VC {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error leaving VC: {e}")
            return False

    def get_current_song(self, chat_id: int) -> Optional[Dict]:
        """Get current song"""
        return self.current_song.get(chat_id)

    def get_queue(self, chat_id: int) -> List[Dict]:
        """Get queue"""
        return self.queues.get(chat_id, [])

    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'active_songs': len(self.current_song),
            'active_calls': len(self.active_calls),
            'total_queued': sum(len(q) for q in self.queues.values()),
            'mode': 'streaming' if self.streaming_available else 'download',
            'streaming_available': self.streaming_available
        }
