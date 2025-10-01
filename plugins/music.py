"""
Vzoel Fox's Lutpan - Music Plugin
Pure userbot music system with yt-dlp

Commands:
- .play <query> - Stream to voice chat or download MP3
- .song <query> - Download song to device
- .pause - Pause current playback
- .resume - Resume paused playback
- .stop - Stop playback and clear queue
- .queue - Show music queue

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.music import MusicManager

# Plugin info
PLUGIN_INFO = {
    "name": "music",
    "version": "2.0.0",
    "description": "Pure userbot music system with yt-dlp",
    "author": "Vzoel Fox's",
    "commands": [".play", ".song", ".pause", ".resume", ".stop", ".queue"],
    "features": ["YouTube download", "Voice chat streaming", "MP3 high quality", "Cookie support"]
}

# Global references
vzoel_client = None
vzoel_emoji = None
music_manager = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, music_manager

    vzoel_client = client
    vzoel_emoji = emoji_handler

    # Initialize music manager
    try:
        music_manager = MusicManager(client.client)
        await music_manager.start()
        print(f"{get_emoji('utama')} Vzoel Fox's Lutpan Music System loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Music system init error: {e}")


def format_duration(seconds):
    """Format duration to MM:SS"""
    try:
        if not seconds:
            return "00:00"
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    except:
        return "00:00"


@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Music system not initialized")
            return

        query = event.pattern_match.group(1).strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Processing music request**

{get_emoji('proses')} Searching YouTube
{get_emoji('telegram')} Query: {query}

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Play music
        result = await music_manager.play_stream(
            event.chat_id,
            query,
            event.sender_id
        )

        if result['success']:
            song = result['song']
            duration = format_duration(song.get('duration', 0))

            if result.get('streaming'):
                # Streaming to voice chat
                if result.get('queued'):
                    response = f"""{get_emoji('centang')} **Added to queue**

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('kuning')} Position: #{result['position']}

{get_emoji('telegram')} Playing next after current song

**Vzoel Fox's Lutpan** Music System
**Contact:** @VZLfxs"""
                else:
                    response = f"""{get_emoji('utama')} **Now streaming**

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('centang')} Mode: Voice chat streaming

{get_emoji('telegram')} Controls: .pause .resume .stop

**Vzoel Fox's Lutpan** Music System
**Contact:** @VZLfxs"""
            else:
                # Downloaded locally
                file_path = result.get('file_path', '')
                file_name = Path(file_path).name if file_path else 'Unknown'

                response = f"""{get_emoji('centang')} **Download complete**

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}

{get_emoji('telegram')} Saved to: downloads/musik/

**Vzoel Fox's Lutpan** Music System
**Contact:** @VZLfxs"""

                # Send file if downloaded
                if file_path and os.path.exists(file_path):
                    try:
                        await event.client.send_file(
                            event.chat_id,
                            file_path,
                            caption=f"**{song['title']}**\n\n**Vzoel Fox's Lutpan**\n**Contact:** @VZLfxs",
                            reply_to=event.id
                        )
                    except Exception as e:
                        print(f"Send file error: {e}")

        else:
            # Error
            error_msg = result.get('error', 'Unknown error')
            response = f"""{get_emoji('merah')} **Request failed**

{get_emoji('kuning')} Error: {error_msg}

{get_emoji('aktif')} Please try again or check query

**Vzoel Fox's Lutpan** Music System
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.song (.+)'))
async def download_song_handler(event):
    """Download song command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Music system not initialized")
            return

        query = event.pattern_match.group(1).strip()

        # Processing
        processing_msg = f"""{get_emoji('loading')} **Downloading song**

{get_emoji('proses')} Searching YouTube
{get_emoji('telegram')} Query: {query}
{get_emoji('aktif')} Preparing download

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Search song
        song_info = await music_manager.search_song(query)

        if not song_info:
            await safe_edit_premium(event, f"{get_emoji('merah')} Song not found\n\n**Vzoel Fox's Lutpan**")
            return

        # Update status
        downloading_msg = f"""{get_emoji('loading')} **Downloading**

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Extracting MP3 (192kbps)
{get_emoji('telegram')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, downloading_msg)

        # Download
        file_path = await music_manager.download_audio(song_info['url'], song_info['title'])

        if file_path and os.path.exists(file_path):
            duration = format_duration(song_info.get('duration', 0))
            file_name = Path(file_path).name

            response = f"""{get_emoji('centang')} **Download complete**

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}
{get_emoji('kuning')} Quality: MP3 192kbps

**Vzoel Fox's Lutpan** Music System
**Contact:** @VZLfxs"""

            await safe_edit_premium(event, response)

            # Send file
            try:
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"**{song_info['title']}**\n\n**Vzoel Fox's Lutpan**\n**Contact:** @VZLfxs",
                    attributes=[],
                    reply_to=event.id
                )
            except Exception as e:
                print(f"Send file error: {e}")

        else:
            await safe_edit_premium(event, f"{get_emoji('merah')} Download failed\n\n**Vzoel Fox's Lutpan**")

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.pause'))
async def pause_handler(event):
    """Pause playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            return

        success = await music_manager.pause_stream(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} **Playback paused**

{get_emoji('aktif')} Use .resume to continue

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('kuning')} **Not playing**

{get_emoji('telegram')} No active playback to pause

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.resume'))
async def resume_handler(event):
    """Resume playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            return

        success = await music_manager.resume_stream(event.chat_id)

        if success:
            response = f"""{get_emoji('centang')} **Playback resumed**

{get_emoji('aktif')} Now playing

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('kuning')} **Not paused**

{get_emoji('telegram')} No paused playback to resume

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.stop'))
async def stop_handler(event):
    """Stop playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            return

        current = music_manager.get_current_song(event.chat_id)
        success = await music_manager.stop_stream(event.chat_id)

        if success or current:
            track_name = current.get('title', 'Unknown') if current else 'Unknown'
            response = f"""{get_emoji('centang')} **Playback stopped**

{get_emoji('proses')} Last track: {track_name}
{get_emoji('aktif')} Queue cleared

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('kuning')} **Not playing**

{get_emoji('telegram')} No active playback

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.queue'))
async def queue_handler(event):
    """Show music queue"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            return

        current = music_manager.get_current_song(event.chat_id)
        queue = music_manager.get_queue(event.chat_id)

        if not current and not queue:
            response = f"""{get_emoji('kuning')} **Queue empty**

{get_emoji('telegram')} Use .play to add songs

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('utama')} **Music Queue**\n\n"""

            if current:
                duration = format_duration(current.get('duration', 0))
                response += f"""{get_emoji('proses')} **Now playing:**
{current.get('title', 'Unknown')} ({duration})\n\n"""

            if queue:
                response += f"""{get_emoji('aktif')} **Queue ({len(queue)} songs):**\n"""
                for i, song in enumerate(queue[:5], 1):
                    duration = format_duration(song.get('duration', 0))
                    response += f"{i}. {song.get('title', 'Unknown')} ({duration})\n"

                if len(queue) > 5:
                    response += f"\n{get_emoji('telegram')} +{len(queue) - 5} more songs\n"

            response += f"\n**Vzoel Fox's Lutpan** Music System\n**Contact:** @VZLfxs"

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
