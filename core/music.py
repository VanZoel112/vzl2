"""
Vzoel Fox's Lutpan - Music Manager
Pure userbot music system with yt-dlp integration

Features:
- Local MP3 playback to OS audio
- YouTube download via yt-dlp
- Voice chat streaming (optional)
- Cookie support for YouTube bypass

Author: Vzoel Fox's
Contact: @VZLfxs
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
    logger.warning("yt-dlp not installed")

try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality, GroupCallConfig
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    logger.warning("py-tgcalls not installed - voice chat disabled")
    MediaStream = None
    AudioQuality = None
    GroupCallConfig = None


class MusicManager:
    """
    Music manager for Vzoel Fox's Lutpan
    Supports both local playback and voice chat streaming
    """

    def __init__(self, userbot_client):
        self.client = userbot_client
        self.download_path = Path("downloads/musik")
        self.download_path.mkdir(parents=True, exist_ok=True)

        # PyTgCalls for VC streaming (pure userbot mode)
        self.pytgcalls = None
        self.streaming_available = PYTGCALLS_AVAILABLE

        # Music state
        self.queues: Dict[int, List[Dict]] = {}
        self.current_song: Dict[int, Dict] = {}
        self.active_calls: Dict[int, bool] = {}
        self.last_request: Dict[int, float] = {}

        # Voice chat configuration
        self._join_as_cache = None
        self._join_as_resolved = False

        # Initialize PyTgCalls for pure userbot
        if self.streaming_available:
            try:
                self.pytgcalls = PyTgCalls(self.client)
                logger.info("Vzoel Fox's Lutpan Music System initialized")
            except Exception as e:
                logger.error(f"PyTgCalls initialization failed: {e}")
                self.streaming_available = False

        # Cooldown configuration
        self.cooldown_seconds = 3

    async def start(self):
        """Start music system"""
        if self.pytgcalls and self.streaming_available:
            try:
                await self.pytgcalls.start()
                logger.info("Voice chat streaming ready")
            except Exception as e:
                logger.error(f"Voice chat start failed: {e}")
                self.streaming_available = False

        if not self.streaming_available:
            logger.info("Music system ready (download mode only)")

    async def stop(self):
        """Stop music system and cleanup"""
        if self.pytgcalls:
            try:
                for chat_id in list(self.active_calls.keys()):
                    await self.leave_voice_chat(chat_id)
                logger.info("Music system stopped")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    async def search_song(self, query: str) -> Optional[Dict]:
        """
        Search for song on YouTube

        Returns:
            Dict with song info or None if not found
        """
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

            # Check for cookies (YouTube bypass)
            cookies_file = Path("cookies.txt")
            if cookies_file.exists():
                ydl_opts['cookiefile'] = str(cookies_file)

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
        """
        Download audio as MP3 (high quality)

        Args:
            url: YouTube URL or direct URL
            title: File title for saving

        Returns:
            Path to downloaded file or None
        """
        if not YTDLP_AVAILABLE:
            return None

        try:
            # Clean title for filename
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

            # Add cookies if available
            cookies_file = Path("cookies.txt")
            if cookies_file.exists():
                ydl_opts['cookiefile'] = str(cookies_file)

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
        Play music - streams to voice chat or downloads locally

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

            # VOICE CHAT STREAMING MODE (if available)
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
                    # Stream directly from YouTube
                    youtube_url = song_info.get('webpage_url')

                    # Build cookie parameters for streaming
                    ytdlp_params = []
                    cookies_file = Path("cookies.txt")
                    if cookies_file.exists():
                        ytdlp_params.append(f'--cookies {str(cookies_file)}')

                    ytdlp_parameters = ' '.join(ytdlp_params) if ytdlp_params else None

                    # Create media stream
                    media_stream = MediaStream(
                        youtube_url,
                        AudioQuality.HIGH,
                        ytdlp_parameters=ytdlp_parameters
                    )

                    # Build voice chat config
                    group_config = GroupCallConfig(auto_start=True)

                    # Play in voice chat
                    await self.pytgcalls.play(
                        chat_id,
                        media_stream,
                        config=group_config
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
                    # Fallback to download mode
                    self.streaming_available = False

            # DOWNLOAD MODE (fallback or primary)
            logger.info("Using download mode")

            # Download audio
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
            logger.error(f"Play error: {e}")
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
            logger.error(f"Stop error: {e}")
            return False

    async def join_voice_chat(self, chat_id: int) -> bool:
        """Join voice chat (ready for streaming)"""
        try:
            if not self.streaming_available or not self.pytgcalls:
                return False

            if chat_id in self.active_calls and self.active_calls[chat_id]:
                return True

            logger.info(f"Voice chat ready for {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Join error: {e}")
            return False

    async def leave_voice_chat(self, chat_id: int) -> bool:
        """Leave voice chat"""
        try:
            if self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.leave_call(chat_id)
                self.active_calls.pop(chat_id, None)
                logger.info(f"Left voice chat {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Leave error: {e}")
            return False

    async def pause_stream(self, chat_id: int) -> bool:
        """Pause current stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.pause_stream(chat_id)
                logger.info(f"Paused stream {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Pause error: {e}")
        return False

    async def resume_stream(self, chat_id: int) -> bool:
        """Resume paused stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.resume_stream(chat_id)
                logger.info(f"Resumed stream {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Resume error: {e}")
        return False

    def get_current_song(self, chat_id: int) -> Optional[Dict]:
        """Get currently playing song info"""
        return self.current_song.get(chat_id)

    def get_queue(self, chat_id: int) -> List[Dict]:
        """Get music queue for chat"""
        return self.queues.get(chat_id, [])

    def get_stats(self) -> Dict:
        """Get music system statistics"""
        return {
            'active_songs': len(self.current_song),
            'active_calls': len(self.active_calls),
            'total_queued': sum(len(q) for q in self.queues.values()),
            'mode': 'streaming' if self.streaming_available else 'download',
            'streaming_available': self.streaming_available,
            'yt_dlp_available': YTDLP_AVAILABLE
        }
