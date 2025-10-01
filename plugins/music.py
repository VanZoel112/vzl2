"""
VZOEL ASSISTANT - Music Plugin
Simple music download with yt-dlp

Commands:
- .play <query> - Download and send MP3
- .song <query> - Download song

~2025 by Vzoel Fox's Lutpan
"""

from telethon import events
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# Try import yt-dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

# Global references
vzoel_client = None
vzoel_emoji = None

# Download path
DOWNLOAD_PATH = Path("downloads/musik")
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    if YTDLP_AVAILABLE:
        print(f"{get_emoji('utama')} Music Plugin loaded - yt-dlp ready")
    else:
        print(f"{get_emoji('kuning')} yt-dlp not installed")


def search_song(query):
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
            }

    except Exception as e:
        print(f"Search error: {e}")
        return None


def download_audio(url, title):
    """Download audio as MP3"""
    if not YTDLP_AVAILABLE:
        return None

    try:
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
        output_template = str(DOWNLOAD_PATH / f"{safe_title}.%(ext)s")

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
            file_path = DOWNLOAD_PATH / f"{safe_title}.{ext}"
            if file_path.exists():
                return str(file_path)

        return None

    except Exception as e:
        print(f"Download error: {e}")
        return None


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
    """Play/download music"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        if not YTDLP_AVAILABLE:
            await safe_edit_premium(event, f"{get_emoji('merah')} yt-dlp not installed\n\n{get_emoji('telegram')} Install: pip install yt-dlp\n\nVZOEL ASSISTANT")
            return

        query = event.pattern_match.group(1).strip()

        processing_msg = f"""{get_emoji('loading')} PROCESSING REQUEST

{get_emoji('proses')} Searching YouTube
{get_emoji('telegram')} Query: {query}

VZOEL ASSISTANT"""
        await safe_edit_premium(event, processing_msg)

        # Search song
        song_info = search_song(query)

        if not song_info:
            await safe_edit_premium(event, f"{get_emoji('merah')} Song not found\n\nVZOEL ASSISTANT")
            return

        # Download
        downloading_msg = f"""{get_emoji('loading')} DOWNLOADING

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Extracting MP3

VZOEL ASSISTANT"""
        await safe_edit_premium(event, downloading_msg)

        file_path = download_audio(song_info['url'], song_info['title'])

        if file_path and os.path.exists(file_path):
            duration = format_duration(song_info.get('duration', 0))
            file_name = Path(file_path).name

            response = f"""{get_emoji('centang')} DOWNLOAD COMPLETE

{get_emoji('proses')} {song_info['title']}
{get_emoji('aktif')} Duration: {duration}
{get_emoji('biru')} File: {file_name}

VZOEL ASSISTANT
~2025 by Vzoel Fox's Lutpan"""

            await safe_edit_premium(event, response)

            # Send file
            try:
                await event.client.send_file(
                    event.chat_id,
                    file_path,
                    caption=f"{song_info['title']}\n\nVZOEL ASSISTANT\n~2025 by Vzoel Fox's Lutpan",
                    reply_to=event.id
                )
            except Exception as e:
                print(f"Send file error: {e}")

        else:
            await safe_edit_premium(event, f"{get_emoji('merah')} Download failed\n\nVZOEL ASSISTANT")

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.song (.+)'))
async def song_handler(event):
    """Download song"""
    # Same as play handler
    await play_handler(event)
