"""
Enhanced Musik Plugin untuk 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Local Music Edition
Fitur: Local music player dengan SQL database untuk metadata
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟽𝟶 - Local SQL Music System
"""

from telethon import events
import asyncio
import os
import sys
import re
import subprocess
import time
import sqlite3
import hashlib
import json
import mimetypes
from pathlib import Path
from datetime import datetime
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.ogg import OggVorbis

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "0.0.0.𝟽𝟶",
    "description": "Local music player dengan SQL database dan file management",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".play", ".add", ".search", ".minfo", ".pause", ".resume", ".stop", ".playlist", ".delete", ".upload"],
    "features": ["Local music storage", "SQL database", "metadata extraction", "playlist management", "𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 branding"]
}

__version__ = "0.0.0.𝟽𝟶"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references
vzoel_client = None
vzoel_emoji = None

# Music directory
MUSIC_DIR = Path("downloads/musik")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Database file
DB_FILE = MUSIC_DIR / "music_library.db"

# Music playback state
music_state = {
    'current_track': None,
    'current_track_id': None,
    'is_playing': False,
    'is_paused': False,
    'volume': 50,
    'playlist': [],
    'current_index': 0,
    'process': None,
    'repeat_mode': 'none',  # none, one, all
    'shuffle': False
}

# Initialize database
def init_database():
    """Initialize SQLite database for music library"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create music table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS music (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            title TEXT,
            artist TEXT,
            album TEXT,
            duration INTEGER,
            bitrate INTEGER,
            file_size INTEGER,
            file_path TEXT NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            play_count INTEGER DEFAULT 0,
            last_played TIMESTAMP,
            tags TEXT,
            user_added TEXT,
            metadata TEXT
        )
    ''')
    
    # Create playlists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            track_ids TEXT,
            user_created TEXT
        )
    ''')
    
    # Create play history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS play_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            played_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,
            FOREIGN KEY (track_id) REFERENCES music (id)
        )
    ''')
    
    # Create indexes for faster search
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON music(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_artist ON music(artist)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_album ON music(album)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags ON music(tags)')
    
    conn.commit()
    conn.close()

# Initialize database on module load
init_database()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Musik Plugin loaded - Local SQL music system ready")
    
    # Check database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM music')
    track_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"{signature} Database loaded with {track_count} tracks")

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file to prevent duplicates"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_audio_metadata(file_path):
    """Extract metadata from audio file using mutagen"""
    metadata = {
        'title': None,
        'artist': None,
        'album': None,
        'duration': 0,
        'bitrate': 0,
        'extra': {}
    }
    
    try:
        audio = MutagenFile(file_path)
        if audio is not None:
            # Duration
            if hasattr(audio.info, 'length'):
                metadata['duration'] = int(audio.info.length)
            
            # Bitrate
            if hasattr(audio.info, 'bitrate'):
                metadata['bitrate'] = audio.info.bitrate
            
            # Tags
            if audio.tags:
                # Title
                if 'TIT2' in audio.tags:  # ID3
                    metadata['title'] = str(audio.tags['TIT2'])
                elif 'title' in audio.tags:
                    metadata['title'] = str(audio.tags['title'][0])
                
                # Artist
                if 'TPE1' in audio.tags:  # ID3
                    metadata['artist'] = str(audio.tags['TPE1'])
                elif 'artist' in audio.tags:
                    metadata['artist'] = str(audio.tags['artist'][0])
                
                # Album
                if 'TALB' in audio.tags:  # ID3
                    metadata['album'] = str(audio.tags['TALB'])
                elif 'album' in audio.tags:
                    metadata['album'] = str(audio.tags['album'][0])
                
                # Additional metadata
                for key in audio.tags:
                    metadata['extra'][str(key)] = str(audio.tags[key])
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    
    return metadata

def add_music_to_database(file_path, user_id=None, tags=None):
    """Add music file to database"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    try:
        # Calculate file hash
        file_hash = calculate_file_hash(file_path)
        
        # Check if file already exists
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename FROM music WHERE file_hash = ?', (file_hash,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return False, f"File already exists as: {existing[1]}"
        
        # Extract metadata
        metadata = extract_audio_metadata(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        # Use filename as title if no metadata
        if not metadata['title']:
            metadata['title'] = os.path.splitext(filename)[0]
        
        # Insert into database
        cursor.execute('''
            INSERT INTO music (file_hash, filename, title, artist, album, 
                             duration, bitrate, file_size, file_path, tags, 
                             user_added, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_hash,
            filename,
            metadata['title'],
            metadata['artist'],
            metadata['album'],
            metadata['duration'],
            metadata['bitrate'],
            file_size,
            file_path,
            tags,
            user_id,
            json.dumps(metadata['extra'])
        ))
        
        conn.commit()
        track_id = cursor.lastrowid
        conn.close()
        
        return True, track_id
        
    except Exception as e:
        return False, f"Database error: {e}"

def search_music_database(query, limit=10):
    """Search music in database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Search in title, artist, album, and tags
    search_query = f"%{query}%"
    cursor.execute('''
        SELECT id, title, artist, album, duration, file_size, play_count, filename
        FROM music
        WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR tags LIKE ? OR filename LIKE ?
        ORDER BY play_count DESC, date_added DESC
        LIMIT ?
    ''', (search_query, search_query, search_query, search_query, search_query, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_track_by_id(track_id):
    """Get track info by ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, artist, album, duration, file_path, filename, play_count
        FROM music WHERE id = ?
    ''', (track_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_play_count(track_id, user_id=None):
    """Update play count and history"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update play count and last played
    cursor.execute('''
        UPDATE music 
        SET play_count = play_count + 1, 
            last_played = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (track_id,))
    
    # Add to play history
    cursor.execute('''
        INSERT INTO play_history (track_id, user_id)
        VALUES (?, ?)
    ''', (track_id, user_id))
    
    conn.commit()
    conn.close()

def get_all_tracks(limit=50, offset=0):
    """Get all tracks from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, artist, album, duration, play_count, date_added
        FROM music
        ORDER BY date_added DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    results = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM music')
    total = cursor.fetchone()[0]
    
    conn.close()
    return results, total

def delete_track(track_id):
    """Delete track from database and file system"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get file path first
    cursor.execute('SELECT file_path, title FROM music WHERE id = ?', (track_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "Track not found"
    
    file_path, title = result
    
    # Delete from database
    cursor.execute('DELETE FROM music WHERE id = ?', (track_id,))
    cursor.execute('DELETE FROM play_history WHERE track_id = ?', (track_id,))
    conn.commit()
    conn.close()
    
    # Delete file if exists
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    return True, title

def format_duration(seconds):
    """Format duration to MM:SS"""
    try:
        if seconds is None:
            return "00:00"
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

def format_file_size(size_bytes):
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

async def play_audio_file(file_path):
    """Play audio file using available audio players"""
    global music_state
    
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # Stop current playback if any
    if music_state['process']:
        stop_playback()
    
    # List of audio players to try
    players = [
        ['mpv', '--no-video', '--really-quiet'],
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet'],
        ['mplayer', '-really-quiet'],
        ['cvlc', '--intf', 'dummy', '--play-and-exit'],
        ['aplay'],
        ['paplay']
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
        music_state['current_track_id'] = None
        return True
    return False

@events.register(events.NewMessage(pattern=r'\.add'))
async def add_music_handler(event):
    """Add music files to library from replied message"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        if not event.is_reply:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Reply ke file audio untuk menambahkan ke library")
            return
        
        replied = await event.get_reply_message()
        if not replied.file:
            await safe_edit_premium(event, f"{get_emoji('merah')} Reply message tidak memiliki file")
            return
        
        # Check if audio file
        mime_type = replied.file.mime_type
        if not mime_type or not mime_type.startswith('audio/'):
            await safe_edit_premium(event, f"{get_emoji('kuning')} File bukan audio. MIME: {mime_type}")
            return
        
        # Download file
        downloading_msg = f"""{get_emoji('loading')} Mendownload file audio...
        
{get_emoji('proses')} Filename: {replied.file.name}
{get_emoji('aktif')} Size: {format_file_size(replied.file.size)}
{get_emoji('telegram')} Processing...
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Library"""
        
        await safe_edit_premium(event, downloading_msg)
        
        # Download to music directory
        file_path = await replied.download_media(file=str(MUSIC_DIR))
        
        if not file_path:
            await safe_edit_premium(event, f"{get_emoji('merah')} Gagal download file")
            return
        
        # Add to database
        user_id = str(event.sender_id)
        success, result = add_music_to_database(file_path, user_id)
        
        if success:
            track_id = result
            track_info = get_track_by_id(track_id)
            
            success_msg = f"""{get_emoji('centang')} FILE BERHASIL DITAMBAHKAN
            
{get_emoji('proses')} ID: #{track_id}
{get_emoji('aktif')} Title: {track_info[1]}
{get_emoji('telegram')} Artist: {track_info[2] or 'Unknown'}
{get_emoji('kuning')} Album: {track_info[3] or 'Unknown'}
{get_emoji('biru')} Duration: {format_duration(track_info[4])}
            
{get_emoji('adder1')} File saved to library
{get_emoji('utama')} Use .play {track_id} to play
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
            
            await safe_edit_premium(event, success_msg)
        else:
            error_msg = f"""{get_emoji('merah')} GAGAL MENAMBAHKAN FILE
            
{get_emoji('kuning')} Error: {result}
{get_emoji('telegram')} File mungkin sudah ada di library
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Library"""
            
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.play(?:\s+(.+))?'))
async def play_music_handler(event):
    """Play music from library"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        query = event.pattern_match.group(1)
        
        if not query:
            # Play random or continue playlist
            tracks, total = get_all_tracks(limit=1)
            if not tracks:
                await safe_edit_premium(event, f"{get_emoji('kuning')} Library kosong. Gunakan .add untuk menambahkan musik")
                return
            
            track = tracks[0]
            track_id = track[0]
        else:
            # Check if query is track ID
            if query.isdigit():
                track = get_track_by_id(int(query))
                if not track:
                    await safe_edit_premium(event, f"{get_emoji('merah')} Track ID #{query} tidak ditemukan")
                    return
                track_id = track[0]
            else:
                # Search by name
                results = search_music_database(query, limit=1)
                if not results:
                    await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ditemukan: {query}")
                    return
                
                track = get_track_by_id(results[0][0])
                track_id = track[0]
        
        # Show playing message
        playing_msg = f"""{get_emoji('loading')} Memulai pemutaran...
        
{get_emoji('proses')} {track[1]}
{get_emoji('aktif')} Artist: {track[2] or 'Unknown'}
{get_emoji('telegram')} Album: {track[3] or 'Unknown'}
{get_emoji('kuning')} Duration: {format_duration(track[4])}
{get_emoji('biru')} Play Count: {track[7]}
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Player"""
        
        await safe_edit_premium(event, playing_msg)
        
        # Play the file
        file_path = track[5]
        success, status = await play_audio_file(file_path)
        
        if success:
            # Update state
            music_state['current_track_id'] = track_id
            music_sta
