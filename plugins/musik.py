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
    "commands": [".play", ".download", ".search", ".minfo", ".pause", ".resume", ".stop"],
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

# Music playback state
music_state = {
    'current_track': None,
    'is_playing': False,
    'is_paused': False,
    'volume': 50,
    'playlist': [],
    'current_index': 0,
    'process': None,
    'last_played_url': None
}

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
    """Search YouTube using PyTube with yt-dlp fallback"""
    # Try PyTube first
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
                print(f"Error processing video with PyTube: {e}")
                continue
        
        if results:
            return results
            
    except Exception as e:
        print(f"PyTube search failed: {e}")
    
    # Fallback to yt-dlp
    print(f"Falling back to yt-dlp for search: {query}")
    return await search_youtube_ytdlp(query, limit)

async def search_youtube_ytdlp(query, limit=5):
    """Fallback search using yt-dlp"""
    try:
        # Simplified approach for reliability
        cmd = [
            'yt-dlp',
            '--quiet',
            '--no-warnings', 
            '--flat-playlist',
            '--print', 'title:%(title)s id:%(id)s uploader:%(uploader)s duration:%(duration)s',
            f'ytsearch{limit}:{query}'
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if process.returncode == 0 and process.stdout.strip():
            results = []
            lines = process.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    # Parse formatted output
                    try:
                        # Extract info from formatted line
                        title_match = re.search(r'title:([^]+?) id:', line)
                        id_match = re.search(r'id:([^\s]+)', line)
                        uploader_match = re.search(r'uploader:([^]+?) duration:', line)
                        duration_match = re.search(r'duration:(\d+)', line)
                        
                        if title_match and id_match:
                            title = title_match.group(1).strip()
                            video_id = id_match.group(1).strip()
                            uploader = uploader_match.group(1).strip() if uploader_match else 'YouTube'
                            duration = int(duration_match.group(1)) if duration_match else 180
                            
                            results.append({
                                'title': title[:60] + "..." if len(title) > 60 else title,
                                'uploader': uploader[:20] + "..." if len(uploader) > 20 else uploader,
                                'duration': duration,
                                'url': f'https://www.youtube.com/watch?v={video_id}',
                                'video_id': video_id,
                                'views': 0  # yt-dlp flat mode doesn't provide views easily
                            })
                    except Exception as parse_err:
                        print(f"Error parsing yt-dlp output: {parse_err}")
                        continue
            
            return results
        
        print(f"yt-dlp search failed. Return code: {process.returncode}")
        if process.stderr:
            print(f"yt-dlp stderr: {process.stderr}")
        return []
        
    except subprocess.TimeoutExpired:
        print("yt-dlp search timeout after 20 seconds")
        return []
    except Exception as e:
        print(f"yt-dlp search error: {e}")
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
        
        # Try to download and play the first result
        first_result = results[0]
        duration_str = format_duration(first_result['duration'])
        
        # Update music state
        music_state['last_played_url'] = first_result['url']
        
        # Show downloading message
        download_msg = f"""{get_emoji('loading')} Mendownload dan memutar...
        
{get_emoji('proses')} {first_result['title']}
{get_emoji('aktif')} Channel: {first_result['uploader']}
{get_emoji('telegram')} Durasi: {duration_str}
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Player"""
        
        await safe_edit_premium(event, download_msg)
        
        # Try to download the audio
        file_path, download_status = await download_music_file(first_result['url'], MUSIC_DIR)
        
        if file_path and os.path.exists(file_path):
            # Try to play the downloaded file
            play_success, play_status = await play_audio_file(file_path)
            
            if play_success:
                playing_msg = f"""{get_emoji('utama')} SEDANG MEMUTAR ▶️
        
{get_emoji('proses')} {first_result['title']}
{get_emoji('telegram')} Channel: {first_result['uploader']}
{get_emoji('aktif')} Durasi: {duration_str}
{get_emoji('centang')} Status: PLAYING (Audio Active)
{get_emoji('kuning')} Player: {play_status}
        
{get_emoji('adder1')} Controls: .pause .stop
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
            else:
                playing_msg = f"""{get_emoji('kuning')} DOWNLOAD BERHASIL, AUDIO TIDAK BISA DIPUTAR
        
{get_emoji('proses')} {first_result['title']}
{get_emoji('telegram')} Channel: {first_result['uploader']}
{get_emoji('aktif')} Durasi: {duration_str}
{get_emoji('merah')} Audio Error: {play_status}
        
{get_emoji('adder1')} URL: {first_result['url']}
{get_emoji('centang')} File: {os.path.basename(file_path)}
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        else:
            playing_msg = f"""{get_emoji('merah')} DOWNLOAD GAGAL
        
{get_emoji('kuning')} Error: {download_status}
{get_emoji('proses')} {first_result['title']}
{get_emoji('aktif')} URL: {first_result['url']}
        
{get_emoji('telegram')} Showing as streaming mode instead:
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, playing_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.pause'))
async def pause_music_handler(event):
    """Pause music playback command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not is_playback_active():
            no_music_msg = f"""{get_emoji('kuning')} Tidak ada musik yang sedang diputar
            
{get_emoji('aktif')} Status musik saat ini:
• Track: {music_state['current_track'] or 'Tidak ada'}
• Status: Idle
• Volume: {music_state['volume']}%

{get_emoji('telegram')} Gunakan .play [nama lagu] untuk mulai memutar musik
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
            await safe_edit_premium(event, no_music_msg)
            return
        
        if music_state['is_paused']:
            already_paused_msg = f"""{get_emoji('kuning')} Musik sudah dalam keadaan pause
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('aktif')} Status: PAUSED ⏸️
{get_emoji('adder1')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Gunakan .resume untuk melanjutkan
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
            await safe_edit_premium(event, already_paused_msg)
            return
        
        success = pause_playback()
        
        if success:
            paused_msg = f"""{get_emoji('centang')} MUSIK DIPAUSE ⏸️
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('kuning')} Status: PAUSED
{get_emoji('aktif')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Commands:
• .resume - Lanjutkan pemutaran
• .stop - Hentikan musik  

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        else:
            paused_msg = f"""{get_emoji('merah')} Gagal pause musik
            
{get_emoji('kuning')} Kemungkinan masalah:
• Player tidak mendukung pause
• Process sudah berhenti
• System audio error

{get_emoji('aktif')} Solusi:
• Gunakan .stop dan .play ulang
• Restart musik system

{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
        
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

{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
            await safe_edit_premium(event, not_paused_msg)
            return
        
        success = resume_playback()
        
        if success:
            resumed_msg = f"""{get_emoji('centang')} MUSIK DILANJUTKAN ▶️
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('aktif')} Status: PLAYING
{get_emoji('adder1')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Music Controls:
• .pause - Pause pemutaran
• .stop - Hentikan musik

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        else:
            resumed_msg = f"""{get_emoji('merah')} Gagal resume musik
            
{get_emoji('kuning')} Kemungkinan masalah:
• Process musik sudah mati
• Audio device error
• Player crashed

{get_emoji('aktif')} Solusi:
• Gunakan .play untuk mulai ulang
• Check audio system

{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
        
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
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
            await safe_edit_premium(event, no_music_msg)
            return
        
        current_track = music_state['current_track']
        success = stop_playback()
        
        if success or current_track:  # Show success even if stop fails but we had a track
            stopped_msg = f"""{get_emoji('centang')} MUSIK DIHENTIKAN ⏹️
            
{get_emoji('proses')} Last Track: {current_track or 'Unknown'}
{get_emoji('kuning')} Status: STOPPED
{get_emoji('aktif')} Volume: {music_state['volume']}%

{get_emoji('telegram')} Ready untuk track baru:
• .play [nama lagu] - Putar musik
• .download [lagu] - Download MP3

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        else:
            stopped_msg = f"""{get_emoji('centang')} MUSIK SYSTEM RESET
            
{get_emoji('kuning')} Musik telah dihentikan
{get_emoji('aktif')} System telah direset

{get_emoji('telegram')} Music system ready
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Player"""
        
        await safe_edit_premium(event, stopped_msg)
        
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
        
        # Get playback status info
        is_active = is_playback_active()
        status_emoji = "▶️" if music_state['is_playing'] else "⏸️" if music_state['is_paused'] else "⏹️"
        status_text = "PLAYING" if music_state['is_playing'] else "PAUSED" if music_state['is_paused'] else "STOPPED"
        
        info_msg = f"""{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 MUSIC INFO
        
{get_emoji('centang')} SYSTEM STATUS:
• Engine: PyTube (Stable)
• Status: {'✅ Ready' if PYTUBE_AVAILABLE else '❌ Not Available'}
• Version: {__version__}

{get_emoji('proses')} PLAYBACK STATUS:
• Current Track: {music_state['current_track'] or 'None'}
• Status: {status_text} {status_emoji}
• Active Process: {'Yes' if is_active else 'No'}
• Volume: {music_state['volume']}%
        
{get_emoji('kuning')} DOWNLOAD STATISTICS:
• MP3 Files: {len(mp3_files)}
• MP4 Files: {len(mp4_files)}
• Total Files: {total_files}
• Total Size: {total_size_mb:.1f} MB
        
{get_emoji('aktif')} AVAILABLE COMMANDS:
• .play [song] - Search, download and play music
• .download [song/url] - Download audio only
• .search [song] - Search without download
• .pause - Pause current playback
• .resume - Resume paused playback
• .stop - Stop playback completely
• .minfo - Show this info
        
{get_emoji('telegram')} DIRECTORY INFO:
• Location: {MUSIC_DIR}
• Free Space: Available
• Supported: MP3, MP4
        
{get_emoji('adder1')} FEATURES:
• Real audio playback (mpv/ffplay)
• Proper pause/resume/stop controls
• No cookies required
• Stable downloads with PyTube
• High quality audio with MP3 conversion
• Success/failure status tracking
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, info_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()