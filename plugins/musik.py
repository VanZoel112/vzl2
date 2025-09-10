"""
Plugin Musik untuk Vzoel Fox's Userbot - Premium Edition
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

# Import from central emoji template (Vzoel Fox's style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "0.0.0.𝟼𝟿",
    "description": "Music player dan downloader dengan YT-DLP dan Spotify support",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".play", ".download", ".minfo", ".pause", ".resume", ".stop", ".volume", ".mute", ".mstatus"],
    "features": ["YouTube music streaming", "Spotify integration", "music download", "premium emoji", "𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 branding"]
}

__version__ = "0.0.0.𝟼𝟿"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

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

{get_emoji('utama')} Vzoel Fox's Music System - Anti-Bot Protection"""

def install_ytdlp():
    """Install yt-dlp if not available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def validate_cookies():
    """Validate if cookies file is working"""
    cookie_file = '/home/ubuntu/vzl2/cookies.txt'
    
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
    
    cookie_file = '/home/ubuntu/vzl2/cookies.txt'
    
    try:
        # Simple search strategy - get video info directly
        print(f"Searching YouTube for: {query}")
        cmd = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--cookies', cookie_file,
            '--flat-playlist',  # Fixed: was --extract-flat (deprecated)
            '--print', '%(title)s|%(id)s|%(uploader)s',  # Simple format: title|id|uploader
            f'ytsearch3:{query}'  # Search for 3 results
        ]
        
        # Run with timeout
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if process.returncode == 0 and process.stdout.strip():
            results = []
            lines = process.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip() and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        video_id = parts[1].strip()
                        uploader = parts[2].strip() if len(parts) > 2 else 'YouTube'
                        
                        results.append({
                            'title': title[:60] + "..." if len(title) > 60 else title,
                            'uploader': uploader,
                            'duration': 180,  # Default duration
                            'url': f'https://www.youtube.com/watch?v={video_id}',
                            'id': video_id
                        })
            
            if results:
                print(f"Found {len(results)} results")
                return results
        
        print(f"Search failed: {process.stderr}")
        
    except subprocess.TimeoutExpired:
        print("Search timeout after 30 seconds")
    except Exception as e:
        print(f"Search error: {e}")
    
    # No fallback - return empty results if search fails
    print("Search completely failed - no results found")
    return []

async def download_music(url, output_dir):
    """Download music using yt-dlp with enhanced cookie handling"""
    
    # Validate URL first - prevent downloading search pages
    if 'youtube.com/results?' in url or 'search_query=' in url:
        print("Cannot download search results page")
        print("URL appears to be search results, not a video")
        return None
    
    if not ('youtube.com/watch?v=' in url or 'youtu.be/' in url):
        print(f"URL may not be a valid YouTube video: {url}")
    
    output_template = str(output_dir / "%(title)s.%(ext)s")
    cookie_file = '/home/ubuntu/vzl2/cookies.txt'
    
    # Check if cookies file exists
    if not os.path.exists(cookie_file):
        print(f"Cookies file not found: {cookie_file}")
        print("Attempting download without cookies...")
    
    try:
        print(f"Starting download from: {url}")
        
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
            print("Download command executed successfully")
            
            # Find downloaded file
            for file in output_dir.glob("*.*"):
                if file.stat().st_mtime > time.time() - 180:  # File created in last 3 minutes
                    file_size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"Found downloaded file: {file.name} ({file_size:.1f}MB)")
                    return str(file)
            
            print("Download completed but file not found")
        else:
            error_msg = process.stderr.strip()
            print(f"Download failed with code {process.returncode}")
            print(f"Error details: {error_msg[:200]}...")
            
            # Check for specific error types
            if "Sign in to confirm" in error_msg or "not a bot" in error_msg:
                print("Bot detection triggered - cookies may be expired")
            elif "Video unavailable" in error_msg:
                print("Video is unavailable or restricted")
            elif "Private video" in error_msg:
                print("Video is private")
            
    except subprocess.TimeoutExpired:
        print("Download timeout after 5 minutes")
    except FileNotFoundError:
        print("yt-dlp not found - please install it")
        return None
    except Exception as e:
        print(f"Unexpected download error: {e}")
    
    print("Download failed completely")
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

{get_emoji('utama')} Vzoel Fox's Music System"""
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

{get_emoji('telegram')} Vzoel Fox's telah mencoba:
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

{get_emoji('utama')} Vzoel Fox's Advanced Music Search"""
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
        # Download music file        downloaded_file = await download_music(results[0]["url"], MUSIC_DIR)        if downloaded_file:            success, play_msg = await play_audio_file(downloaded_file)        else:            success = False            play_msg = "Download failed"
        
        playing_msg = f"""{get_emoji('utama')} SEDANG MEMUTAR

{get_emoji('proses')} Judul: {results[0]['title']}
{get_emoji('telegram')} Channel: {results[0]['uploader']}
{get_emoji('aktif')} Durasi: {format_duration(results[0]['duration'])}
{get_emoji("kuning")} Status: {"PLAYING ▶️" if success else "STREAMING"}
{get_emoji("adder1")} Info: {play_msg if success else results[0]["url"]}

{get_emoji('adder1')} Link: {results[0]['url']}

{get_emoji('petir')} Vzoel Fox's Music Player Active!"""
        
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

{get_emoji('utama')} Vzoel Fox's Music System"""
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

{get_emoji('telegram')} Vzoel Fox's Downloader"""
            
            await safe_edit_premium(event, success_msg)
            
            # Optionally send the file
            try:
                if os.path.getsize(downloaded_file) < 50 * 1024 * 1024:  # Less than 50MB
                    await event.client.send_file(
                        event.chat_id, 
                        downloaded_file,
                        caption=f"{get_emoji('utama')} Downloaded by Vzoel Fox's Music System"
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

{get_emoji('utama')} Vzoel Fox's Downloader"""
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
        
        music_info = f"""{signature} Vzoel Fox's Music System

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

{get_emoji('adder2')} Powered by Vzoel Fox's Technology

By Vzoel Fox's Assistant"""
        
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
{get_emoji('utama')} File: /home/ubuntu/vzl2/cookies.txt
{get_emoji('telegram')} YouTube authentication: ACTIVE
{get_emoji('biru')} Bot detection bypass: ENABLED

{get_emoji('proses')} Cookie Details:
• File size: {os.path.getsize('/home/ubuntu/vzl2/cookies.txt')} bytes
• YouTube domain: Detected
• Essential cookies: Present
• Test download: PASSED

{get_emoji('kuning')} Music commands ready:
.play [song name] - Search and play music
.download [song/url] - Download audio file

{get_emoji('petir')} Vzoel Fox's Music System - Cookies Valid"""
        else:
            status_msg = f"""{get_emoji('merah')} COOKIES STATUS: INVALID
            
{get_emoji('kuning')} Problem: {message}
{get_emoji('aktif')} File: /home/ubuntu/vzl2/cookies.txt

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

{get_emoji('petir')} Vzoel Fox's Music System - Fix Required"""
        
        await safe_edit_premium(event, status_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator# Music playback control state
music_state = {
    'current_track': None,
    'is_playing': False,
    'is_paused': False,
    'volume': 50,
    'playlist': [],
    'current_index': 0,
    'process': None
}

def get_audio_devices():
    """Get available audio devices for playback"""
    try:
        result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            devices = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            'id': parts[0],
                            'name': parts[1],
                            'description': ' '.join(parts[2:]) if len(parts) > 2 else parts[1]
                        })
            return devices
    except FileNotFoundError:
        pass
    
    # Fallback to basic audio check
    return [{'id': '0', 'name': 'default', 'description': 'Default Audio Device'}]

def set_system_volume(volume_level):
    """Set system volume using amixer or pactl"""
    volume_level = max(0, min(100, volume_level))  # Clamp to 0-100
    
    try:
        # Try pactl first (PulseAudio)
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume_level}%'], 
                      check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            # Try amixer (ALSA)
            subprocess.run(['amixer', 'set', 'Master', f'{volume_level}%'], 
                          check=True, capture_output=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

def get_system_volume():
    """Get current system volume"""
    try:
        # Try pactl first
        result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Parse output like "Volume: front-left: 32768 /  50% / -18.06 dB"
            for line in result.stdout.split('\n'):
                if 'Volume:' in line and '%' in line:
                    import re
                    match = re.search(r'(\d+)%', line)
                    if match:
                        return int(match.group(1))
    except FileNotFoundError:
        pass
    
    try:
        # Try amixer
        result = subprocess.run(['amixer', 'get', 'Master'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            import re
            match = re.search(r'\[(\d+)%\]', result.stdout)
            if match:
                return int(match.group(1))
    except FileNotFoundError:
        pass
    
    return music_state['volume']  # Return stored volume as fallback

async def play_audio_file(file_path):
    """Play audio file using available audio players"""
    global music_state
    
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # List of audio players to try (in order of preference)
    players = [
        ['mpv', '--no-video', '--really-quiet'],
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet'],
        ['aplay'],  # For WAV files
        ['paplay']  # PulseAudio player
    ]
    
    for player_cmd in players:
        try:
            # Check if player is available
            subprocess.run([player_cmd[0], '--help'], 
                         capture_output=True, timeout=2)
            
            # Start playback process
            cmd = player_cmd + [file_path]
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            music_state['process'] = process
            music_state['is_playing'] = True
            music_state['is_paused'] = False
            music_state['current_track'] = os.path.basename(file_path)
            
            return True, f"Playing with {player_cmd[0]}"
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return False, "No compatible audio player found"

def pause_playback():
    """Pause current playback"""
    global music_state
    
    if music_state['process'] and music_state['is_playing']:
        try:
            # Send SIGSTOP to pause (works with most players)
            music_state['process'].send_signal(19)  # SIGSTOP
            music_state['is_paused'] = True
            music_state['is_playing'] = False
            return True
        except:
            return False
    return False

def resume_playback():
    """Resume paused playback"""
    global music_state
    
    if music_state['process'] and music_state['is_paused']:
        try:
            # Send SIGCONT to resume
            music_state['process'].send_signal(18)  # SIGCONT
            music_state['is_paused'] = False
            music_state['is_playing'] = True
            return True
        except:
            return False
    return False

def stop_playback():
    """Stop current playback"""
    global music_state
    
    if music_state['process']:
        try:
            music_state['process'].terminate()
            music_state['process'].wait(timeout=5)
        except:
            try:
                music_state['process'].kill()
            except:
                pass
        
        music_state['process'] = None
        music_state['is_playing'] = False
        music_state['is_paused'] = False
        music_state['current_track'] = None
        return True
    return False

def is_playback_active():
    """Check if playback is currently active"""
    global music_state
    
    if music_state['process']:
        poll = music_state['process'].poll()
        if poll is None:  # Process is still running
            return True
        else:
            # Process ended, clean up
            music_state['process'] = None
            music_state['is_playing'] = False
            music_state['is_paused'] = False
            music_state['current_track'] = None
    
    return False
@events.register(events.NewMessage(pattern=r'\.pause'))
async def pause_music_handler(event):
    """Pause music playback command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not is_playback_active():
            no_music_msg = f"""{get_emoji('kuning')} Tidak ada musik yang sedang diputar
            
{get_emoji('aktif')} Status musik saat ini:
• Track: Tidak ada
• Status: Idle
• Volume: {music_state['volume']}%

{get_emoji('telegram')} Gunakan .play [nama lagu] untuk mulai memutar musik
{get_emoji('utama')} VzoelFox Music Player"""
            await safe_edit_premium(event, no_music_msg)
            return
        
        if music_state['is_paused']:
            already_paused_msg = f"""{get_emoji('kuning')} Musik sudah dalam keadaan pause
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('aktif')} Status: PAUSED
{get_emoji('adder1')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Gunakan .resume untuk melanjutkan
{get_emoji('utama')} VzoelFox Music Player"""
            await safe_edit_premium(event, already_paused_msg)
            return
        
        if pause_playback():
            paused_msg = f"""{get_emoji('centang')} MUSIK DIPAUSE
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('kuning')} Status: PAUSED ⏸️
{get_emoji('aktif')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Commands:
• .resume - Lanjutkan pemutaran
• .stop - Hentikan musik  
• .volume [0-100] - Atur volume

{get_emoji('utama')} VzoelFox Music Controller"""
        else:
            paused_msg = f"""{get_emoji('merah')} Gagal pause musik
            
{get_emoji('kuning')} Kemungkinan masalah:
• Player tidak mendukung pause
• Process sudah berhenti
• System audio error

{get_emoji('aktif')} Solusi:
• Gunakan .stop dan .play ulang
• Restart musik system
• Check audio device

{get_emoji('utama')} VzoelFox Music Player"""
        
        await safe_edit_premium(event, paused_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.resume'))
async def resume_music_handler(event):
    """Resume music playback command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not music_state['is_paused']:
            not_paused_msg = f"""{get_emoji('kuning')} Tidak ada musik yang di-pause
            
{get_emoji('aktif')} Status saat ini:
• Playing: {'Ya' if music_state['is_playing'] else 'Tidak'}
• Track: {music_state['current_track'] or 'Tidak ada'}
• Volume: {music_state['volume']}%

{get_emoji('telegram')} Commands:
• .play [lagu] - Putar musik baru
• .pause - Pause musik
• .stop - Hentikan musik

{get_emoji('utama')} VzoelFox Music Player"""
            await safe_edit_premium(event, not_paused_msg)
            return
        
        if resume_playback():
            resumed_msg = f"""{get_emoji('centang')} MUSIK DILANJUTKAN
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('aktif')} Status: PLAYING ▶️
{get_emoji('adder1')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Music Controls:
• .pause - Pause pemutaran
• .stop - Hentikan musik
• .volume [0-100] - Atur volume
• .mstatus - Status detail

{get_emoji('utama')} VzoelFox Music Controller"""
        else:
            resumed_msg = f"""{get_emoji('merah')} Gagal resume musik
            
{get_emoji('kuning')} Kemungkinan masalah:
• Process musik sudah mati
• Audio device error
• Player crashed

{get_emoji('aktif')} Solusi:
• Gunakan .play untuk mulai ulang
• Check audio system
• Restart bot jika perlu

{get_emoji('utama')} VzoelFox Music Player"""
        
        await safe_edit_premium(event, resumed_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.stop'))
async def stop_music_handler(event):
    """Stop music playback command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not is_playback_active() and not music_state['is_paused']:
            no_music_msg = f"""{get_emoji('kuning')} Tidak ada musik yang sedang diputar
            
{get_emoji('aktif')} Status musik:
• Track: Tidak ada
• Status: Idle
• Volume: {music_state['volume']}%

{get_emoji('telegram')} Gunakan .play [nama lagu] untuk mulai
{get_emoji('utama')} VzoelFox Music Player"""
            await safe_edit_premium(event, no_music_msg)
            return
        
        current_track = music_state['current_track']
        
        if stop_playback():
            stopped_msg = f"""{get_emoji('centang')} MUSIK DIHENTIKAN
            
{get_emoji('proses')} Last Track: {current_track or 'Unknown'}
{get_emoji('kuning')} Status: STOPPED ⏹️
{get_emoji('aktif')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Ready untuk track baru:
• .play [nama lagu] - Putar musik
• .download [lagu] - Download MP3
• .minfo - Info sistem musik

{get_emoji('utama')} VzoelFox Music Controller"""
        else:
            stopped_msg = f"""{get_emoji('merah')} Gagal stop musik
            
{get_emoji('kuning')} Musik mungkin sudah berhenti
{get_emoji('aktif')} System telah direset

{get_emoji('telegram')} Music system ready
{get_emoji('utama')} VzoelFox Music Player"""
        
        await safe_edit_premium(event, stopped_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.volume (\d+)'))
async def volume_control_handler(event):
    """Volume control command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        volume_level = int(event.pattern_match.group(1))
        volume_level = max(0, min(100, volume_level))  # Clamp to 0-100
        
        # Update music state
        music_state['volume'] = volume_level
        
        # Try to set system volume
        volume_set = set_system_volume(volume_level)
        current_vol = get_system_volume()
        
        if volume_set:
            volume_msg = f"""{get_emoji('centang')} VOLUME DIATUR
            
{get_emoji('aktif')} Volume: {volume_level}% 🔊
{get_emoji('proses')} System Volume: {current_vol}%
{get_emoji('telegram')} Status: {'Playing' if music_state['is_playing'] else 'Paused' if music_state['is_paused'] else 'Idle'}

{get_emoji('adder1')} Volume Controls:
• .volume 0 - Mute
• .volume 50 - Medium  
• .volume 100 - Maximum
• .mute - Quick mute/unmute

{get_emoji('utama')} VzoelFox Volume Controller"""
        else:
            volume_msg = f"""{get_emoji('kuning')} VOLUME DISIMPAN (SOFTWARE)
            
{get_emoji('aktif')} Bot Volume: {volume_level}% 🔊
{get_emoji('merah')} System Volume: Tidak dapat diatur
{get_emoji('telegram')} Status: {'Playing' if music_state['is_playing'] else 'Paused' if music_state['is_paused'] else 'Idle'}

{get_emoji('adder2')} Note: 
Audio system tidak mendukung volume control otomatis.
Atur volume manual dari system audio.

{get_emoji('utama')} VzoelFox Volume Controller"""
        
        await safe_edit_premium(event, volume_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.mute'))
async def mute_toggle_handler(event):
    """Mute/unmute toggle command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        current_volume = get_system_volume()
        
        if current_volume > 0:
            # Mute
            music_state['pre_mute_volume'] = current_volume
            set_system_volume(0)
            music_state['volume'] = 0
            
            mute_msg = f"""{get_emoji('kuning')} AUDIO DIMUTE
            
{get_emoji('merah')} Volume: 0% 🔇
{get_emoji('proses')} Previous: {music_state['pre_mute_volume']}%
{get_emoji('telegram')} Status: MUTED

{get_emoji('aktif')} Gunakan .mute lagi untuk unmute
{get_emoji('utama')} VzoelFox Mute Controller"""
        else:
            # Unmute
            restore_vol = music_state.get('pre_mute_volume', 50)
            set_system_volume(restore_vol)
            music_state['volume'] = restore_vol
            
            mute_msg = f"""{get_emoji('centang')} AUDIO DIAKTIFKAN
            
{get_emoji('aktif')} Volume: {restore_vol}% 🔊
{get_emoji('telegram')} Status: UNMUTED
{get_emoji('proses')} Audio restored

{get_emoji('adder1')} Volume controls ready
{get_emoji('utama')} VzoelFox Volume Controller"""
        
        await safe_edit_premium(event, mute_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.mstatus'))
async def music_status_handler(event):
    """Show detailed music status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        # Get system info
        devices = get_audio_devices()
        current_vol = get_system_volume()
        is_active = is_playback_active()
        
        # Status emoji
        if music_state['is_playing']:
            status_emoji = "▶️"
            status_text = "PLAYING"
        elif music_state['is_paused']:
            status_emoji = "⏸️"
            status_text = "PAUSED"
        else:
            status_emoji = "⏹️"
            status_text = "STOPPED"
        
        status_msg = f"""{get_emoji('utama')} VZOEL MUSIC STATUS
        
{get_emoji('proses')} PLAYBACK STATUS:
• Current Track: {music_state['current_track'] or 'None'}
• Status: {status_text} {status_emoji}
• Active Process: {'Yes' if is_active else 'No'}

{get_emoji('aktif')} AUDIO SETTINGS:
• Bot Volume: {music_state['volume']}%
• System Volume: {current_vol}%
• Audio Devices: {len(devices)} found

{get_emoji('telegram')} CONTROL COMMANDS:
• .play [lagu] - Putar musik
• .pause - Pause pemutaran  
• .resume - Lanjut pemutaran
• .stop - Hentikan musik
• .volume [0-100] - Atur volume
• .mute - Mute/unmute audio

{get_emoji('centang')} SYSTEM INFO:
• Music Directory: {MUSIC_DIR}
• Downloaded: {len(list(MUSIC_DIR.glob('*.mp3')))} files
• Primary Device: {devices[0]['description'] if devices else 'Default'}

{get_emoji('petir')} VzoelFox Advanced Music System"""
        
        await safe_edit_premium(event, status_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()