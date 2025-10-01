"""
VZOEL ASSISTANT - Music Plugin  
Pure userbot music with VC streaming

Commands:
- .play <query> - Play/stream music
- .song <query> - Download song
- .pause - Pause stream
- .resume - Resume stream
- .stop - Stop and clear
- .queue - Show queue

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.music_manager import MusicManager

# Global references
vzoel_client = None
vzoel_emoji = None
music_manager = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, music_manager

    vzoel_client = client
    vzoel_emoji = emoji_handler

    try:
        music_manager = MusicManager(client.client)
        await music_manager.start()
        print(f"{get_emoji('utama')} Music Plugin loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Music init error: {e}")


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
async def play_handler(event):
    """Play music"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager

        if not music_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Music system not initialized\n\nVZOEL ASSISTANT")
            return

        query = event.pattern_match.group(1).strip()

        processing_msg = f"""{get_emoji('loading')} PROCESSING

{get_emoji('proses')} Searching: {query}

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        result = await music_manager.play_stream(event.chat_id, query, event.sender_id)

        if result['success']:
            song = result['song']
            duration = format_duration(song.get('duration', 0))

            if result.get('streaming'):
                if result.get('queued'):
                    response = f"""{get_emoji('centang')} QUEUED

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('kuning')} Position: #{result['position']}

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
                else:
                    response = f"""{get_emoji('utama')} NOW STREAMING

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('centang')} Mode: Voice chat

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
            else:
                file_path = result.get('file_path', '')
                file_name = Path(file_path).name if file_path else 'Unknown'
                response = f"""{get_emoji('centang')} DOWNLOADED

{get_emoji('proses')} {song['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
                await safe_edit_premium(event, response)
                if file_path and os.path.exists(file_path):
                    try:
                        await event.client.send_file(event.chat_id, file_path, caption=f"{song['title']}\n\nVZOEL ASSISTANT", reply_to=event.id)
                    except:
                        pass
                return

            await safe_edit_premium(event, response)
        else:
            error = result.get('error', 'Unknown error')
            response = f"""{get_emoji('merah')} FAILED

{get_emoji('kuning')} Error: {error}

VZOEL ASSISTANT"""
            await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.song (.+)'))
async def song_handler(event):
    """Download song"""
    await play_handler(event)


@events.register(events.NewMessage(pattern=r'\.pause'))
async def pause_handler(event):
    """Pause playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, music_manager
        if not music_manager:
            return
        success = await music_manager.pause_stream(event.chat_id)
        if success:
            response = f"""{get_emoji('centang')} PAUSED

{get_emoji('aktif')} Use .resume to continue

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PLAYING

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
            response = f"""{get_emoji('centang')} RESUMED

{get_emoji('aktif')} Now playing

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PAUSED

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
            track = current.get('title', 'Unknown') if current else 'Unknown'
            response = f"""{get_emoji('centang')} STOPPED

{get_emoji('proses')} Last: {track}
{get_emoji('aktif')} Queue cleared

VZOEL ASSISTANT"""
        else:
            response = f"""{get_emoji('kuning')} NOT PLAYING

VZOEL ASSISTANT"""
        await safe_edit_premium(event, response)
        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.queue'))
async def queue_handler(event):
    """Show queue"""
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
                response += f"""{get_emoji('aktif')} QUEUE ({len(queue)}):\n"""
                for i, song in enumerate(queue[:5], 1):
                    duration = format_duration(song.get('duration', 0))
                    response += f"{i}. {song.get('title', 'Unknown')} ({duration})\n"
                if len(queue) > 5:
                    response += f"\n{get_emoji('telegram')} +{len(queue) - 5} more\n"
            response += f"\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan"
        await safe_edit_premium(event, response)
        if vzoel_client:
            vzoel_client.increment_command_count()
