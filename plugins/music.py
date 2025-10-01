"""
VZOEL ASSISTANT - Music Plugin
Pure userbot music system with yt-dlp and inline controls

Commands:
- .play <query> - Play music to voice chat or download
- .song <query> - Download song as MP3
- .pause - Pause current playback
- .resume - Resume playback
- .stop - Stop and clear queue
- .queue - Show music queue

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events, Button
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium, safe_send_premium
from core.music import MusicManager

# Plugin info
PLUGIN_INFO = {
    "name": "music",
    "version": "3.0.0",
    "description": "Pure userbot music system with inline controls",
    "author": "Vzoel Fox's",
    "commands": [".play", ".song", ".pause", ".resume", ".stop", ".queue"],
    "features": ["YouTube download", "Voice chat streaming", "Inline buttons", "Queue system"]
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
        print(f"{get_emoji('utama')} VZOEL ASSISTANT Music System loaded")
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


def create_music_buttons(chat_id):
    """Create inline control buttons for music player"""
    return [
        [
            Button.inline(f"{get_emoji('proses')} Pause", f"music_pause_{chat_id}"),
            Button.inline(f"{get_emoji('centang')} Resume", f"music_resume_{chat_id}"),
            Button.inline(f"{get_emoji('merah')} Stop", f"music_stop_{chat_id}")
        ],
        [
            Button.inline(f"{get_emoji('aktif')} Queue", f"music_queue_{chat_id}"),
            Button.inline(f"{get_emoji('kuning')} Download", f"music_download_{chat_id}")
        ]
    ]


@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Music system not initialized\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan")
            return

        query = event.pattern_match.group(1).strip()

        # Processing message
        processing_msg = f"""{get_emoji('loading')} PROCESSING MUSIC REQUEST

{get_emoji('proses')} Searching YouTube
{get_emoji('telegram')} Query: {query}

VZOEL ASSISTANT"""

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
                    response = f"""{get_emoji('centang')} ADDED TO QUEUE

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('kuning')} Position: #{result['position']}

{get_emoji('telegram')} Playing next after current song

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
                else:
                    response = f"""{get_emoji('utama')} NOW STREAMING

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('centang')} Mode: Voice chat streaming

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

                # Send with inline buttons
                buttons = create_music_buttons(event.chat_id)
                await safe_edit_premium(event, response, buttons=buttons)
            else:
                # Downloaded locally
                file_path = result.get('file_path', '')
                file_name = Path(file_path).name if file_path else 'Unknown'

                response = f"""{get_emoji('centang')} DOWNLOAD COMPLETE

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}

{get_emoji('telegram')} Saved to: downloads/musik/

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

                await safe_edit_premium(event, response)

                # Send file if downloaded
                if file_path and os.path.exists(file_path):
                    try:
                        await event.client.send_file(
                            event.chat_id,
                            file_path,
                            caption=f"{song['title']}\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan",
                            reply_to=event.id
                        )
                    except Exception as e:
                        print(f"Send file error: {e}")

        else:
            # Error
            error_msg = result.get('error', 'Unknown error')
            response = f"""{get_emoji('merah')} REQUEST FAILED

{get_emoji('kuning')} Error: {error_msg}

{get_emoji('aktif')} Please try again or check query

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

            await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.song (.+)'))
async def download_song_handler(event):
    """Download song command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Music system not initialized\n\nVZOEL ASSISTANT")
            return

        query = event.pattern_match.group(1).strip()

        # Processing
        processing_msg = f"""{get_emoji('loading')} DOWNLOADING SONG

{get_emoji('proses')} Searching YouTube
{get_emoji('telegram')} Query: {query}
{get_emoji('aktif')} Preparing download

VZOEL ASSISTANT"""

        await safe_edit_premium(event, processing_msg)

        # Search song
        song_info = await music_manager.search_song(query)

        if not song_info:
            await safe_edit_premium(event, f"{get_emoji('merah')} Song not found\n\nVZOEL ASSISTANT")
            return

        # Update status
        downloading_msg = f"""{get_emoji('loading')} DOWNLOADING

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Extracting MP3 (192kbps)
{get_emoji('telegram')} Please wait

VZOEL ASSISTANT"""

        await safe_edit_premium(event, downloading_msg)

        # Download
        file_path = await music_manager.download_audio(song_info['url'], song_info['title'])

        if file_path and os.path.exists(file_path):
            duration = format_duration(song_info.get('duration', 0))
            file_name = Path(file_path).name

            response = f"""{get_emoji('centang')} DOWNLOAD COMPLETE

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}
{get_emoji('kuning')} Quality: MP3 192kbps

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

            await safe_edit_premium(event, response)

            # Send file
            try:
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"{song_info['title']}\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan",
                    attributes=[],
                    reply_to=event.id
                )
            except Exception as e:
                print(f"Send file error: {e}")

        else:
            await safe_edit_premium(event, f"{get_emoji('merah')} Download failed\n\nVZOEL ASSISTANT")

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
            response = f"""{get_emoji('centang')} PLAYBACK PAUSED

{get_emoji('aktif')} Use .resume to continue

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PLAYING

{get_emoji('telegram')} No active playback to pause

VZOEL ASSISTANT"""

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
            response = f"""{get_emoji('centang')} PLAYBACK RESUMED

{get_emoji('aktif')} Now playing

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PAUSED

{get_emoji('telegram')} No paused playback to resume

VZOEL ASSISTANT"""

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
            response = f"""{get_emoji('centang')} PLAYBACK STOPPED

{get_emoji('proses')} Last track: {track_name}
{get_emoji('aktif')} Queue cleared

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PLAYING

{get_emoji('telegram')} No active playback

VZOEL ASSISTANT"""

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
            response = f"""{get_emoji('kuning')} QUEUE EMPTY

{get_emoji('telegram')} Use .play to add songs

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('utama')} MUSIC QUEUE\n\n"""

            if current:
                duration = format_duration(current.get('duration', 0))
                response += f"""{get_emoji('proses')} NOW PLAYING:
{current.get('title', 'Unknown')} ({duration})\n\n"""

            if queue:
                response += f"""{get_emoji('aktif')} QUEUE ({len(queue)} SONGS):\n"""
                for i, song in enumerate(queue[:5], 1):
                    duration = format_duration(song.get('duration', 0))
                    response += f"{i}. {song.get('title', 'Unknown')} ({duration})\n"

                if len(queue) > 5:
                    response += f"\n{get_emoji('telegram')} +{len(queue) - 5} more songs\n"

            response += f"\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan"

        # Add buttons if music is playing
        buttons = None
        if current:
            buttons = create_music_buttons(event.chat_id)

        await safe_edit_premium(event, response, buttons=buttons)

        if vzoel_client:
            vzoel_client.increment_command_count()


# Inline button callbacks
@events.register(events.CallbackQuery(pattern=r'music_pause_(\d+)'))
async def music_pause_callback(event):
    """Handle pause button"""
    chat_id = int(event.pattern_match.group(1))

    if music_manager:
        success = await music_manager.pause_stream(chat_id)
        if success:
            await event.answer(f"{get_emoji('centang')} Paused", alert=False)
        else:
            await event.answer(f"{get_emoji('kuning')} Not playing", alert=True)


@events.register(events.CallbackQuery(pattern=r'music_resume_(\d+)'))
async def music_resume_callback(event):
    """Handle resume button"""
    chat_id = int(event.pattern_match.group(1))

    if music_manager:
        success = await music_manager.resume_stream(chat_id)
        if success:
            await event.answer(f"{get_emoji('centang')} Resumed", alert=False)
        else:
            await event.answer(f"{get_emoji('kuning')} Not paused", alert=True)


@events.register(events.CallbackQuery(pattern=r'music_stop_(\d+)'))
async def music_stop_callback(event):
    """Handle stop button"""
    chat_id = int(event.pattern_match.group(1))

    if music_manager:
        await music_manager.stop_stream(chat_id)
        await event.answer(f"{get_emoji('centang')} Stopped", alert=False)

        # Update message
        try:
            await event.edit(f"{get_emoji('centang')} PLAYBACK STOPPED\n\nVZOEL ASSISTANT")
        except:
            pass


@events.register(events.CallbackQuery(pattern=r'music_queue_(\d+)'))
async def music_queue_callback(event):
    """Handle queue button"""
    chat_id = int(event.pattern_match.group(1))

    if music_manager:
        current = music_manager.get_current_song(chat_id)
        queue = music_manager.get_queue(chat_id)

        if not current and not queue:
            await event.answer(f"{get_emoji('kuning')} Queue empty", alert=True)
        else:
            queue_text = f"{get_emoji('utama')} QUEUE\n\n"
            if current:
                queue_text += f"Now: {current.get('title', 'Unknown')}\n"
            if queue:
                queue_text += f"Next: {len(queue)} songs"
            await event.answer(queue_text, alert=True)


@events.register(events.CallbackQuery(pattern=r'music_download_(\d+)'))
async def music_download_callback(event):
    """Handle download button"""
    chat_id = int(event.pattern_match.group(1))

    if music_manager:
        current = music_manager.get_current_song(chat_id)
        if current:
            await event.answer(f"{get_emoji('loading')} Use .song command to download", alert=True)
        else:
            await event.answer(f"{get_emoji('kuning')} Nothing playing", alert=True)
