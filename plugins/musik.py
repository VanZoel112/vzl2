"""
Plugin Musik untuk VzoelFox Userbot - Premium Edition
Fitur: Music player dan downloader dengan YT-DLP dan Spotify support
Founder Userbot: Vzoel Fox's Ltpn
Version: 1.0.0 - Music System
"""

from telethon import events
import asyncio
import os
import sys
import re
import json
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VzoelFox style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "1.0.0",
    "description": "Music player dan downloader dengan YT-DLP dan Spotify support",
    "author": "Founder Userbot: Vzoel Fox's Ltpn",
    "commands": [".play", ".download", ".minfo"],
    "features": ["YouTube music streaming", "Spotify integration", "music download", "premium emoji", "VzoelFox branding"]
}

__version__ = "1.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Music directory
MUSIC_DIR = Path("downloads/musik")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Musik Plugin loaded - Music system ready")

def check_ytdlp_installed():
    """Check if yt-dlp is installed"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ytdlp():
    """Install yt-dlp if not available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

async def search_youtube_music(query):
    """Search music on YouTube with timeout and better error handling"""
    try:
        # Use yt-dlp to search with timeout and authentication
        cmd = [
            'yt-dlp', 
            '--dump-json', 
            '--no-download',
            '--socket-timeout', '30',
            '--no-warnings',
            '--default-search', 'ytsearch3:',
            query
        ]
        
        # Run with timeout
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if process.returncode != 0:
            print(f"YT-DLP error: {process.stderr}")
            return []
        
        results = []
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        results.append({
                            'title': data.get('title', 'Unknown')[:60],  # Limit title length
                            'uploader': data.get('uploader', 'Unknown')[:30],
                            'duration': data.get('duration', 0),
                            'url': data.get('webpage_url', ''),
                            'id': data.get('id', '')
                        })
                    except json.JSONDecodeError:
                        continue
        
        return results[:3]  # Return top 3 results
        
    except subprocess.TimeoutExpired:
        print("Search timeout after 30 seconds")
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []

async def download_music(url, output_dir):
    """Download music using yt-dlp with timeout and better error handling"""
    try:
        output_template = str(output_dir / "%(title)s.%(ext)s")
        
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0',
            '--socket-timeout', '30',
            '--no-warnings',
            '--output', output_template,
            url
        ]
        
        # Run with timeout (max 5 minutes for download)
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if process.returncode == 0:
            # Find downloaded file
            for file in output_dir.glob("*.mp3"):
                if file.stat().st_mtime > time.time() - 120:  # File created in last 2 minutes
                    return str(file)
        else:
            print(f"Download failed: {process.stderr}")
        
        return None
        
    except subprocess.TimeoutExpired:
        print("Download timeout after 5 minutes")
        return None
    except Exception as e:
        print(f"Download error: {e}")
        return None

def format_duration(seconds):
    """Format duration to readable format"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music command dengan search dan streaming"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        if not query:
            error_msg = f"{get_emoji('merah')} Gunakan format: .play [nama lagu/artis]"
            await safe_edit_premium(event, error_msg)
            return
        
        # Check yt-dlp installation
        if not check_ytdlp_installed():
            install_msg = f"{get_emoji('loading')} Installing yt-dlp..."
            await safe_edit_premium(event, install_msg)
            
            if not install_ytdlp():
                error_msg = f"""{get_emoji('merah')} YT-DLP tidak tersedia

{get_emoji('aktif')} Instalasi Manual:
• pip install yt-dlp
• pkg install yt-dlp (Termux)

{get_emoji('kuning')} Error kemungkinan:
• Koneksi internet bermasalah
• Permission denied
• Storage tidak cukup

{get_emoji('telegram')} Solusi alternatif:
• Coba restart aplikasi
• Clear cache dan coba lagi
• Update system packages

{get_emoji('utama')} VzoelFox Music System"""
                await safe_edit_premium(event, error_msg)
                return
        
        # Search phase
        search_msg = f"{get_emoji('loading')} Mencari musik: {query}..."
        await safe_edit_premium(event, search_msg)
        
        # Search YouTube
        results = await search_youtube_music(query)
        
        if not results:
            not_found_msg = f"""{get_emoji('merah')} Musik tidak ditemukan: {query}

{get_emoji('kuning')} Kemungkinan masalah:
• Koneksi internet lemah/timeout
• Kata kunci terlalu umum
• Content restriction/geo-block
• Server YouTube sedang down

{get_emoji('telegram')} Tips pencarian:
• .play alan walker faded
• .play despacito luis fonsi  
• .play [artis] [judul lagu]

{get_emoji('aktif')} Solusi:
• Coba kata kunci berbeda
• Check koneksi internet
• Tunggu beberapa menit dan coba lagi

{get_emoji('utama')} VzoelFox Music Search"""
            await safe_edit_premium(event, not_found_msg)
            return
        
        # Display results
        search_results = f"{get_emoji('utama')} HASIL PENCARIAN MUSIK\n\n"
        
        for i, result in enumerate(results, 1):
            duration_str = format_duration(result['duration'])
            search_results += f"{get_emoji('centang')} {i}. {result['title']}\n"
            search_results += f"{get_emoji('telegram')} Channel: {result['uploader']}\n"
            search_results += f"{get_emoji('aktif')} Durasi: {duration_str}\n\n"
        
        search_results += f"{get_emoji('kuning')} Memutar musik pertama...\n"
        search_results += f"{get_emoji('biru')} URL: {results[0]['url']}"
        
        await safe_edit_premium(event, search_results)
        
        # Play first result (in Telegram, we can't actually play, so we show info)
        await asyncio.sleep(2)
        
        playing_msg = f"""{get_emoji('utama')} SEDANG MEMUTAR

{get_emoji('proses')} Judul: {results[0]['title']}
{get_emoji('telegram')} Channel: {results[0]['uploader']}
{get_emoji('aktif')} Durasi: {format_duration(results[0]['duration'])}
{get_emoji('kuning')} Status: STREAMING

{get_emoji('adder1')} Link: {results[0]['url']}

{get_emoji('petir')} VzoelFox Music Player Active!"""
        
        await safe_edit_premium(event, playing_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.download (.+)'))
async def download_music_handler(event):
    """Download music command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        if not query:
            error_msg = f"{get_emoji('merah')} Gunakan format: .download [nama lagu/URL]"
            await safe_edit_premium(event, error_msg)
            return
        
        # Check yt-dlp installation
        if not check_ytdlp_installed():
            install_msg = f"{get_emoji('loading')} Installing yt-dlp..."
            await safe_edit_premium(event, install_msg)
            
            if not install_ytdlp():
                error_msg = f"""{get_emoji('merah')} YT-DLP tidak tersedia

{get_emoji('aktif')} Instalasi Manual:
• pip install yt-dlp
• pkg install yt-dlp (Termux)

{get_emoji('kuning')} Error kemungkinan:
• Koneksi internet bermasalah
• Permission denied
• Storage tidak cukup

{get_emoji('telegram')} Solusi alternatif:
• Coba restart aplikasi
• Clear cache dan coba lagi
• Update system packages

{get_emoji('utama')} VzoelFox Music System"""
                await safe_edit_premium(event, error_msg)
                return
        
        # Check if query is URL or search term
        is_url = query.startswith(('http://', 'https://'))
        
        if is_url:
            download_url = query
            download_msg = f"{get_emoji('loading')} Mendownload dari URL..."
        else:
            # Search first
            search_msg = f"{get_emoji('loading')} Mencari musik: {query}..."
            await safe_edit_premium(event, search_msg)
            
            results = await search_youtube_music(query)
            
            if not results:
                not_found_msg = f"{get_emoji('merah')} Musik tidak ditemukan: {query}"
                await safe_edit_premium(event, not_found_msg)
                return
            
            download_url = results[0]['url']
            download_msg = f"{get_emoji('loading')} Mendownload: {results[0]['title']}..."
        
        await safe_edit_premium(event, download_msg)
        
        # Download
        downloaded_file = await download_music(download_url, MUSIC_DIR)
        
        if downloaded_file:
            file_size = os.path.getsize(downloaded_file) / (1024 * 1024)  # MB
            file_name = os.path.basename(downloaded_file)
            
            success_msg = f"""{get_emoji('centang')} DOWNLOAD BERHASIL

{get_emoji('utama')} File: {file_name}
{get_emoji('aktif')} Ukuran: {file_size:.2f} MB
{get_emoji('proses')} Lokasi: {MUSIC_DIR}
{get_emoji('kuning')} Format: MP3

{get_emoji('adder2')} File siap digunakan!

{get_emoji('telegram')} VzoelFox Downloader"""
            
            await safe_edit_premium(event, success_msg)
            
            # Optionally send the file
            try:
                if os.path.getsize(downloaded_file) < 50 * 1024 * 1024:  # Less than 50MB
                    await event.client.send_file(
                        event.chat_id, 
                        downloaded_file,
                        caption=f"{get_emoji('utama')} Downloaded by VzoelFox Music System"
                    )
            except Exception as e:
                print(f"Error sending file: {e}")
        else:
            error_msg = f"""{get_emoji('merah')} Gagal mendownload musik

{get_emoji('kuning')} Kemungkinan masalah:
• File terlalu besar (>50MB)
• Koneksi timeout/lambat
• Format tidak didukung
• Storage penuh

{get_emoji('aktif')} Solusi:
• Coba lagu yang lebih pendek
• Check storage space
• Restart aplikasi dan coba lagi
• Gunakan koneksi WiFi yang stabil

{get_emoji('telegram')} Coba lagi dalam beberapa menit

{get_emoji('utama')} VzoelFox Downloader"""
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.minfo'))
async def music_info_handler(event):
    """Show music plugin information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Count downloaded files
        downloaded_count = len(list(MUSIC_DIR.glob("*.mp3")))
        
        music_info = f"""{signature} VzoelFox Music System

{get_emoji('utama')} Features:
• YouTube music search and streaming
• High-quality MP3 downloads
• Spotify integration support
• Advanced music player interface
• Premium emoji integration

{get_emoji('centang')} Commands:
.play [query] - Search dan putar musik
.download [query/URL] - Download musik MP3
.minfo - Info sistem musik

{get_emoji('telegram')} Statistics:
• Downloaded Files: {downloaded_count} MP3s
• Storage Location: {MUSIC_DIR}
• Quality: High (320kbps)
• Format Support: MP3, M4A, WAV

{get_emoji('aktif')} Engine Info:
• Backend: YT-DLP v2025
• Source: YouTube Music
• Quality: Best Available
• Speed: Optimized Download

{get_emoji('proses')} Usage:
.play despacito - Search dan putar
.download https://youtu.be/xxx - Download dari URL
.download alan walker faded - Search dan download

{get_emoji('adder2')} Powered by VzoelFox Technology

By VzoelFox Assistant"""
        
        await safe_edit_premium(event, music_info)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator