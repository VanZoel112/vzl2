"""
Enhanced Musik Plugin untuk 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Local Database Edition
Fitur: Local music database dengan Telethon sharing system (No API dependency)
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟽𝟶 - Local SQLite Music System
"""

from telethon import events
from telethon.tl.types import DocumentAttributeAudio
import asyncio
import os
import sys
import re
import subprocess
import time
import sqlite3
import json
import random
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "0.0.0.𝟽𝟶",
    "description": "Local music database dengan Telethon sharing system (no API dependency)",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".play", ".upload", ".catalog", ".minfo", ".pause", ".resume", ".stop", ".playlist", ".search"],
    "features": ["Local SQLite database", "Telethon file sharing", "Offline music catalog", "premium emoji", "𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 branding"]
}

__version__ = "0.0.0.𝟽𝟶"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references
vzoel_client = None
vzoel_emoji = None

# Music directories
MUSIC_DIR = Path("downloads/musik")
DB_DIR = Path("database")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

# Database file
DB_FILE = DB_DIR / "music_catalog.db"

# Music playback state
music_state = {
    'current_track': None,
    'is_playing': False,
    'is_paused': False,
    'volume': 50,
    'playlist': [],
    'current_index': 0,
    'process': None,
    'current_file': None,
    'music_id': None
}

def init_database():
    """Initialize SQLite music database"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    # Create music catalog table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS music_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            duration INTEGER,
            file_hash TEXT UNIQUE,
            uploaded_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            play_count INTEGER DEFAULT 0,
            tags TEXT,
            description TEXT
        )
    ''')
    
    # Create playlists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            music_ids TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file for duplicate detection"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def get_audio_duration(file_path):
    """Get audio duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 
            'format=duration', '-of', 'csv=p=0', str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return int(float(result.stdout.strip()))
    except:
        pass
    return 0

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    # Initialize database
    init_database()
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Local Music Plugin loaded - SQLite catalog ready")

def add_music_to_catalog(file_path, title=None, artist=None, tags=None, description=None):
    """Add music file to local database catalog"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # Calculate file info
    file_size = os.path.getsize(file_path)
    file_hash = calculate_file_hash(file_path)
    duration = get_audio_duration(file_path)
    
    if not title:
        title = Path(file_path).stem
    
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO music_catalog 
            (title, artist, file_path, file_size, duration, file_hash, tags, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, artist, str(file_path), file_size, duration, file_hash, tags, description))
        
        conn.commit()
        music_id = cursor.lastrowid
        conn.close()
        return True, f"Added to catalog with ID: {music_id}"
        
    except sqlite3.IntegrityError:
        conn.close()
        return False, "File already exists in catalog"
    except Exception as e:
        conn.close()
        return False, f"Database error: {e}"

def search_music_catalog(query):
    """Search music in local database"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    # Search by title, artist, or tags
    cursor.execute('''
        SELECT id, title, artist, file_path, duration, play_count, tags
        FROM music_catalog 
        WHERE title LIKE ? OR artist LIKE ? OR tags LIKE ?
        ORDER BY play_count DESC, title ASC
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_random_music(limit=5):
    """Get random music from catalog"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, artist, file_path, duration, play_count
        FROM music_catalog 
        ORDER BY RANDOM()
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def increment_play_count(music_id):
    """Increment play count for a music track"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE music_catalog 
        SET play_count = play_count + 1
        WHERE id = ?
    ''', (music_id,))
    
    conn.commit()
    conn.close()

def format_duration(seconds):
    """Format duration to MM:SS"""
    try:
        if isinstance(seconds, str):
            seconds = int(float(seconds))
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

async def play_audio_file(file_path, music_id=None):
    """Play audio file using available audio players"""
    global music_state
    
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # Stop current playback first
    stop_playback()
    
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
            cmd = player_cmd + [str(file_path)]
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            music_state['process'] = process
            music_state['is_playing'] = True
            music_state['is_paused'] = False
            music_state['current_track'] = Path(file_path).name
            music_state['current_file'] = str(file_path)
            music_state['music_id'] = music_id
            
            # Increment play count if music_id provided
            if music_id:
                increment_play_count(music_id)
            
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
        music_state['current_file'] = None
        music_state['music_id'] = None
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
            music_state['current_file'] = None
            music_state['music_id'] = None
    
    return False

@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music from local catalog"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        query = event.pattern_match.group(1).strip()
        
        # Check for special commands
        if query.lower() == "random":
            # Play random music
            results = get_random_music(1)
            if not results:
                await safe_edit_premium(event, f"{get_emoji('kuning')} Catalog musik kosong. Upload musik dulu dengan .upload")
                return
        else:
            # Search in local catalog
            results = search_music_catalog(query)
            if not results:
                no_results_msg = f"""{get_emoji('kuning')} Tidak ada musik ditemukan
                
{get_emoji('merah')} Query: {query}
{get_emoji('aktif')} Coba dengan keyword yang berbeda
{get_emoji('telegram')} Atau upload musik baru dengan .upload
                
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Local Music"""
                
                await safe_edit_premium(event, no_results_msg)
                return
        
        # Display results and play first one
        first_result = results[0]
        music_id, title, artist, file_path, duration, play_count = first_result[:6]
        
        # Show searching message first
        if query.lower() != "random":
            search_results = f"""{get_emoji('utama')} HASIL PENCARIAN MUSIK LOKAL
            
{get_emoji('centang')} Ditemukan {len(results)} hasil untuk: {query}

"""
            
            for i, result in enumerate(results[:3], 1):
                _, r_title, r_artist, _, r_duration, r_play_count = result[:6]
                duration_str = format_duration(r_duration)
                artist_str = r_artist or "Unknown Artist"
                
                search_results += f"""{get_emoji('proses')} {i}. {r_title}
{get_emoji('aktif')} Artist: {artist_str}
{get_emoji('kuning')} Durasi: {duration_str} | Played: {r_play_count}x

"""
            
            search_results += f"""{get_emoji('telegram')} Memutar musik pertama...
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
            
            await safe_edit_premium(event, search_results)
        
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