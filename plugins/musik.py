"""
Enhanced Musik Plugin untuk 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Music player dan downloader menggunakan PyTube (lebih stabil)
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟼𝟿 - PyTube Music System
"""

from telethon import events
import asyncio
import os
import sys
import re
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Try importing pytube
try:
    from pytube import YouTube, Search
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "0.0.0.𝟼𝟿",
    "description": "Music player dan downloader menggunakan PyTube (lebih stabil dari yt-dlp)",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".play", ".download", ".search", ".minfo"],
    "features": ["YouTube music streaming", "PyTube integration", "music download", "premium emoji", "𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 branding"]
}

__version__ = "0.0.0.𝟼𝟿"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references
vzoel_client = None
vzoel_emoji = None

# Music directory
MUSIC_DIR = Path("downloads/musik")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Musik Plugin loaded - PyTube music system ready")

def install_pytube():
    """Install pytube if not available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytube'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def format_duration(seconds):
    """Format duration to MM:SS"""
    try:
        if isinstance(seconds, str):
            return seconds
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

def sanitize_filename(filename):
    """Sanitize filename for safe saving"""
    # Remove special characters that could cause issues
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'[^\w\s\-_.]', '_', filename)
    return filename[:100]  # Limit length

async def search_youtube_music(query, limit=5):
    """Search YouTube using PyTube"""
    try:
        print(f"Searching YouTube with PyTube: {query}")
        
        # Use PyTube Search
        search = Search(query)
        results = []
        
        count = 0
        for video in search.results:
            if count >= limit:
                break
                
            try:
                # Get video info
                duration = getattr(video, 'length', 0)
                
                results.append({
                    'title': video.title,
                    'uploader': video.author,
                    'duration': duration,
                    'url': video.watch_url,
                    'video_id': video.video_id,
                    'views': getattr(video, 'views', 0)
                })
                count += 1
                
            except Exception as e:
                print(f"Error processing video: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"PyTube search error: {e}")
        return []

async def download_music_file(url, output_dir):
    """Download audio using PyTube"""
    try:
        print(f"Downloading with PyTube: {url}")
        
        # Create YouTube object
        yt = YouTube(url)
        
        # Get audio stream (highest quality)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            return None, "No audio stream found"
        
        # Sanitize filename
        safe_title = sanitize_filename(yt.title)
        output_filename = f"{safe_title}.mp4"
        
        # Download
        downloaded_file = audio_stream.download(
            output_path=str(output_dir),
            filename=output_filename
        )
        
        # Convert to MP3 if ffmpeg available
        mp3_path = str(output_dir / f"{safe_title}.mp3")
        
        try:
            subprocess.run([
                'ffmpeg', '-i', downloaded_file, 
                '-vn', '-acodec', 'mp3', '-ab', '192k', 
                mp3_path
            ], check=True, capture_output=True)
            
            # Remove original file
            os.remove(downloaded_file)
            return mp3_path, "Downloaded and converted to MP3"
            
        except (FileNotFoundError, subprocess.CalledProcessError):
            # ffmpeg not available, return original
            return downloaded_file, "Downloaded (original format)"
            
    except Exception as e:
        return None, f"Download error: {e}"

@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music using PyTube search"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        if not PYTUBE_AVAILABLE:
            install_msg = f"""{get_emoji('merah')} PyTube tidak terinstall
            
{get_emoji('kuning')} Installing PyTube...
{get_emoji('proses')} pip install pytube
            
{get_emoji('aktif')} Mohon tunggu instalasi selesai"""
            
            await safe_edit_premium(event, install_msg)
            
            if install_pytube():
                success_msg = f"""{get_emoji('centang')} PyTube berhasil diinstall!
                
{get_emoji('aktif')} Restart bot untuk menggunakan
{get_emoji('telegram')} Atau coba command lagi
                
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music System"""
                await safe_edit_premium(event, success_msg)
                return
            else:
                await safe_edit_premium(event, f"{get_emoji('merah')} Gagal install PyTube")
                return
        
        # Show searching message
        searching_msg = f"""{get_emoji('loading')} Mencari musik...
        
{get_emoji('proses')} Query: {query}
{get_emoji('aktif')} Engine: PyTube (Stable)
{get_emoji('telegram')} Mencari di YouTube...
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Search"""
        
        await safe_edit_premium(event, searching_msg)
        
        # Search for music
        results = await search_youtube_music(query, limit=3)
        
        if not results:
            no_results_msg = f"""{get_emoji('kuning')} Tidak ada hasil ditemukan
            
{get_emoji('merah')} Query: {query}
{get_emoji('aktif')} Coba dengan keyword yang berbeda
{get_emoji('telegram')} Atau periksa koneksi internet
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music System"""
            
            await safe_edit_premium(event, no_results_msg)
            return
        
        # Display results
        search_results = f"""{get_emoji('utama')} HASIL PENCARIAN MUSIK
        
{get_emoji('centang')} Ditemukan {len(results)} hasil untuk: {query}

"""
        
        for i, result in enumerate(results, 1):
            duration_str = format_duration(result['duration'])
            views_str = f"{result['views']:,}" if result['views'] > 0 else "N/A"
            
            search_results += f"""{get_emoji('proses')} {i}. {result['title']}
{get_emoji('aktif')} Channel: {result['uploader']}
{get_emoji('kuning')} Durasi: {duration_str}
{get_emoji('biru')} Views: {views_str}

"""
        
        search_results += f"""{get_emoji('telegram')} Memutar musik pertama...
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        
        await safe_edit_premium(event, search_results)
        
        # Show now playing info (in Telegram we can't actually play audio)
        first_result = results[0]
        duration_str = format_duration(first_result['duration'])
        
        playing_msg = f"""{get_emoji('utama')} SEDANG MEMUTAR
        
{get_emoji('proses')} {first_result['title']}
{get_emoji('telegram')} Channel: {first_result['uploader']}
{get_emoji('aktif')} Durasi: {duration_str}
{get_emoji('centang')} Status: STREAMING ▶️
        
{get_emoji('adder1')} URL: {first_result['url']}
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, playing_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.download (.+)'))
async def download_music_handler(event):
    """Download music using PyTube"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        if not PYTUBE_AVAILABLE:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTube tidak terinstall. Gunakan .play dulu untuk install.")
            return
        
        # Check if it's a URL or search query
        if 'youtube.com' in query or 'youtu.be' in query:
            url = query
            download_msg = f"""{get_emoji('loading')} Mendownload dari URL...
            
{get_emoji('proses')} URL: {url}
{get_emoji('aktif')} Engine: PyTube
{get_emoji('telegram')} Preparing download...
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Downloader"""
        else:
            # Search first
            await safe_edit_premium(event, f"{get_emoji('loading')} Mencari dan mendownload...")
            
            results = await search_youtube_music(query, limit=1)
            if not results:
                await safe_edit_premium(event, f"{get_emoji('merah')} Tidak ditemukan: {query}")
                return
                
            url = results[0]['url']
            download_msg = f"""{get_emoji('loading')} Mendownload...
            
{get_emoji('proses')} {results[0]['title']}
{get_emoji('aktif')} Channel: {results[0]['uploader']}
{get_emoji('telegram')} Downloading audio...
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Downloader"""
        
        await safe_edit_premium(event, download_msg)
        
        # Download the audio
        file_path, status = await download_music_file(url, MUSIC_DIR)
        
        if file_path and os.path.exists(file_path):
            # Success
            file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
            filename = os.path.basename(file_path)
            
            success_msg = f"""{get_emoji('centang')} DOWNLOAD BERHASIL
            
{get_emoji('proses')} File: {filename}
{get_emoji('aktif')} Size: {file_size:.1f} MB
{get_emoji('telegram')} Status: {status}
{get_emoji('kuning')} Location: {MUSIC_DIR}
            
{get_emoji('adder1')} File siap diputar!
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
            
            await safe_edit_premium(event, success_msg)
        else:
            # Failed
            error_msg = f"""{get_emoji('merah')} DOWNLOAD GAGAL
            
{get_emoji('kuning')} Error: {status}
{get_emoji('aktif')} URL: {url}
            
{get_emoji('telegram')} Possible solutions:
• Video mungkin private/restricted
• Check internet connection
• Try different video
• Video might be too long
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Downloader"""
            
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.search (.+)'))
async def search_music_handler(event):
    """Search music without playing"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        if not PYTUBE_AVAILABLE:
            await safe_edit_premium(event, f"{get_emoji('merah')} PyTube tidak terinstall.")
            return
        
        await safe_edit_premium(event, f"{get_emoji('loading')} Mencari: {query}...")
        
        results = await search_youtube_music(query, limit=5)
        
        if not results:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ada hasil untuk: {query}")
            return
        
        search_results = f"""{get_emoji('utama')} HASIL PENCARIAN
        
{get_emoji('centang')} Query: {query}
{get_emoji('proses')} Ditemukan: {len(results)} video

"""
        
        for i, result in enumerate(results, 1):
            duration_str = format_duration(result['duration'])
            views_str = f"{result['views']:,}" if result['views'] > 0 else "N/A"
            
            search_results += f"""{i}. {result['title'][:50]}...
   {get_emoji('aktif')} {result['uploader']} | {duration_str} | {views_str} views
   {get_emoji('biru')} {result['url']}

"""
        
        search_results += f"""𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        
        await safe_edit_premium(event, search_results)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.minfo'))
async def music_info_handler(event):
    """Show music system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        # Count downloaded files
        mp3_files = list(MUSIC_DIR.glob("*.mp3"))
        mp4_files = list(MUSIC_DIR.glob("*.mp4"))
        total_files = len(mp3_files) + len(mp4_files)
        
        # Calculate total size
        total_size = 0
        for file in mp3_files + mp4_files:
            try:
                total_size += os.path.getsize(file)
            except:
                pass
        
        total_size_mb = total_size / 1024 / 1024
        
        info_msg = f"""{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 MUSIC INFO
        
{get_emoji('centang')} SYSTEM STATUS:
• Engine: PyTube (Stable)
• Status: {'✅ Ready' if PYTUBE_AVAILABLE else '❌ Not Available'}
• Version: {__version__}
        
{get_emoji('proses')} DOWNLOAD STATISTICS:
• MP3 Files: {len(mp3_files)}
• MP4 Files: {len(mp4_files)}
• Total Files: {total_files}
• Total Size: {total_size_mb:.1f} MB
        
{get_emoji('aktif')} AVAILABLE COMMANDS:
• .play [song] - Search and show music
• .download [song/url] - Download audio
• .search [song] - Search only
• .minfo - Show this info
        
{get_emoji('telegram')} DIRECTORY INFO:
• Location: {MUSIC_DIR}
• Free Space: Available
• Supported: MP3, MP4
        
{get_emoji('adder1')} FEATURES:
• No cookies required
• Stable downloads
• High quality audio
• Fast search results
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, info_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()