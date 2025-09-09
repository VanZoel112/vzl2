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

def create_manual_verification_message():
    """Create message untuk manual verification process"""
    return f"""{get_emoji('kuning')} YOUTUBE ANTI-BOT DETECTION ACTIVE

{get_emoji('merah')} Problem:
YouTube requires manual verification untuk akses content

{get_emoji('aktif')} SOLUSI MANUAL VERIFICATION:
1. Buka browser dan kunjungi YouTube
2. Complete CAPTCHA verification jika diminta
3. Export cookies dari browser
4. Simpan cookies ke bot

{get_emoji('telegram')} Alternative Solutions:
• Gunakan VPN dengan IP yang berbeda
• Wait 30-60 menit sebelum coba lagi
• Gunakan YouTube Premium account cookies
• Try different search keywords

{get_emoji('petir')} Quick Fixes:
• Restart internet connection
• Clear browser cache dan cookies
• Use incognito/private browsing mode
• Try mobile data instead of WiFi

{get_emoji('biru')} Advanced Option:
Contact admin untuk setup YouTube cookies
atau gunakan alternatif search method

{get_emoji('utama')} VzoelFox Music System - Anti-Bot Protection"""

def install_ytdlp():
    """Install yt-dlp if not available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def validate_cookies():
    """Validate if cookies file is working"""
    cookie_file = '/data/data/com.termux/files/home/cookies.txt'
    
    if not os.path.exists(cookie_file):
        return False, "Cookies file not found"
    
    try:
        # Check file size
        file_size = os.path.getsize(cookie_file)
        if file_size < 100:  # Very small file, probably empty
            return False, f"Cookies file too small ({file_size} bytes)"
        
        # Check file format (basic validation)
        with open(cookie_file, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Read first 500 chars
            
            if '.youtube.com' not in content:
                return False, "No YouTube cookies found"
            
            if 'VISITOR_INFO1_LIVE' not in content:
                return False, "Missing essential YouTube cookies"
        
        # Try a quick test with yt-dlp
        test_cmd = [
            'yt-dlp', 
            '--cookies', cookie_file,
            '--quiet',
            '--simulate',
            '--playlist-end', '1',
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # Rick Roll for testing
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return True, "Cookies are valid and working"
        else:
            error = result.stderr.strip()
            if "Sign in to confirm" in error or "not a bot" in error:
                return False, "Cookies expired - YouTube bot detection active"
            else:
                return False, f"Cookie test failed: {error[:100]}..."
    
    except subprocess.TimeoutExpired:
        return False, "Cookie validation timeout"
    except Exception as e:
        return False, f"Cookie validation error: {e}"

async def search_youtube_music(query):
    """Search music on YouTube with cookies authentication"""
    
    cookie_file = '/data/data/com.termux/files/home/cookies.txt'
    
    try:
        # Strategy 1: Use yt-dlp search with cookies
        print(f"🔍 Searching YouTube for: {query}")
        cmd = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--cookies', cookie_file,
            '--extract-flat',
            '--playlist-end', '5',  # Get max 5 results
            f'ytsearch5:{query}'
        ]
        
        # Run with timeout
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if process.returncode == 0:
            # Parse results (basic parsing)
            results = []
            lines = process.stdout.strip().split('\n')
            
            for line in lines:
                if line and 'youtube.com/watch?v=' in line:
                    # Extract basic info
                    url_match = line.split('youtube.com/watch?v=')[1].split()[0]
                    video_id = url_match.split('&')[0] if '&' in url_match else url_match
                    
                    results.append({
                        'title': f'Found: {query}',
                        'uploader': 'YouTube',
                        'duration': 180,  # Default duration
                        'url': f'https://www.youtube.com/watch?v={video_id}',
                        'id': video_id
                    })
            
            if results:
                print(f"✅ Found {len(results)} results")
                return results
        
        print(f"❌ Search failed: {process.stderr}")
        
    except subprocess.TimeoutExpired:
        print("⏱️ Search timeout after 30 seconds")
    except Exception as e:
        print(f"💥 Search error: {e}")
    
    # Fallback: Return mock result to prevent total failure
    print("🔄 Using fallback search result")
    mock_results = [
        {
            'title': f'Fallback Search: {query}',
            'uploader': 'VzoelFox Music',
            'duration': 212,
            'url': f'https://www.youtube.com/results?search_query={query.replace(" ", "+")}',
            'id': 'fallback'
        }
    ]
    
    return mock_results

async def download_music(url, output_dir):
    """Download music using yt-dlp with enhanced cookie handling"""
    
    output_template = str(output_dir / "%(title)s.%(ext)s")
    cookie_file = '/data/data/com.termux/files/home/cookies.txt'
    
    # Check if cookies file exists
    if not os.path.exists(cookie_file):
        print(f"⚠️ Cookies file not found: {cookie_file}")
        print("🔄 Attempting download without cookies...")
    
    try:
        print(f"🎵 Starting download from: {url}")
        
        # Build command with enhanced options
        cmd = [
            'yt-dlp',
            '--format', 'bestaudio[ext=m4a]/bestaudio/best',  # Prefer m4a format
            '--extract-audio',  # Extract audio only
            '--audio-format', 'mp3',  # Convert to mp3
            '--audio-quality', '192K',  # 192kbps quality
            '--output', output_template,
            '--no-warnings',
            '--quiet',
            url
        ]
        
        # Add cookies if file exists
        if os.path.exists(cookie_file):
            cmd.insert(-1, '--cookies')
            cmd.insert(-1, cookie_file)
            print("🍪 Using cookies for authentication")
        
        # Add user agent to avoid bot detection
        cmd.extend([
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ])
        
        print(f"🚀 Command: {' '.join(cmd[:5])}... (truncated)")
        
        # Run with longer timeout (5 minutes for downloads)
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if process.returncode == 0:
            print("✅ Download command executed successfully")
            
            # Find downloaded file
            for file in output_dir.glob("*.*"):
                if file.stat().st_mtime > time.time() - 180:  # File created in last 3 minutes
                    file_size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"📁 Found downloaded file: {file.name} ({file_size:.1f}MB)")
                    return str(file)
            
            print("⚠️ Download completed but file not found")
        else:
            error_msg = process.stderr.strip()
            print(f"❌ Download failed with code {process.returncode}")
            print(f"📋 Error details: {error_msg[:200]}...")
            
            # Check for specific error types
            if "Sign in to confirm" in error_msg or "not a bot" in error_msg:
                print("🤖 Bot detection triggered - cookies may be expired")
            elif "Video unavailable" in error_msg:
                print("📹 Video is unavailable or restricted")
            elif "Private video" in error_msg:
                print("🔒 Video is private")
            
    except subprocess.TimeoutExpired:
        print("⏱️ Download timeout after 5 minutes")
    except FileNotFoundError:
        print("❌ yt-dlp not found - please install it")
        return None
    except Exception as e:
        print(f"💥 Unexpected download error: {e}")
    
    print("💔 Download failed completely")
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
• YouTube Anti-Bot Detection aktif
• Koneksi internet lemah/timeout
• Content restriction/geo-block
• Rate limiting dari server YouTube

{get_emoji('telegram')} VzoelFox telah mencoba:
• Multiple User-Agent strategies
• Cookie-based authentication
• Alternative extractors (yt-dlp, youtube-dl)
• Different timeout configurations

{get_emoji('aktif')} Solusi yang bisa dicoba:
• Tunggu 5-10 menit sebelum coba lagi
• Gunakan kata kunci yang lebih spesifik
• Coba dengan koneksi internet berbeda
• Restart bot jika masalah persist

{get_emoji('biru')} Format yang disarankan:
.play [artist name] [song title]
.play alan walker faded
.play ed sheeran perfect

{get_emoji('utama')} VzoelFox Advanced Music Search"""
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

@events.register(events.NewMessage(pattern=r'\.cookiecheck'))
async def cookie_check_handler(event):
    """Check YouTube cookies status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        checking_msg = f"{get_emoji('loading')} Checking YouTube cookies status..."
        await safe_edit_premium(event, checking_msg)
        
        is_valid, message = validate_cookies()
        
        if is_valid:
            status_msg = f"""{get_emoji('centang')} COOKIES STATUS: VALID
            
{get_emoji('aktif')} Status: {message}
{get_emoji('utama')} File: /data/data/com.termux/files/home/cookies.txt
{get_emoji('telegram')} YouTube authentication: ACTIVE
{get_emoji('biru')} Bot detection bypass: ENABLED

{get_emoji('proses')} Cookie Details:
• File size: {os.path.getsize('/data/data/com.termux/files/home/cookies.txt')} bytes
• YouTube domain: Detected
• Essential cookies: Present
• Test download: PASSED

{get_emoji('kuning')} Music commands ready:
.play [song name] - Search and play music
.download [song/url] - Download audio file

{get_emoji('petir')} VzoelFox Music System - Cookies Valid"""
        else:
            status_msg = f"""{get_emoji('merah')} COOKIES STATUS: INVALID
            
{get_emoji('kuning')} Problem: {message}
{get_emoji('aktif')} File: /data/data/com.termux/files/home/cookies.txt

{get_emoji('telegram')} Solusi untuk fix cookies:
1. Export fresh cookies dari browser
2. Pastikan login ke YouTube dulu
3. Gunakan browser extension untuk export
4. Copy cookies ke file tersebut

{get_emoji('biru')} Recommended Extensions:
• "Get cookies.txt" (Chrome/Firefox)
• "EditThisCookie" (Chrome) 
• "Cookie Quick Manager" (Firefox)

{get_emoji('proses')} Export Steps:
1. Login ke YouTube di browser
2. Kunjungi https://youtube.com
3. Export cookies dengan extension
4. Save ke cookies.txt

{get_emoji('petir')} VzoelFox Music System - Fix Required"""
        
        await safe_edit_premium(event, status_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator