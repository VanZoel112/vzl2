"""
Enhanced Musik Plugin untuk 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Spotify Edition
Fitur: Spotify API integration untuk musik search dan streaming preview
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟽𝟷 - Spotify Music System
"""

from telethon import events
import asyncio
import os
import sys
import re
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Try importing spotipy
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False

# Plugin Info
PLUGIN_INFO = {
    "name": "musik",
    "version": "0.0.0.𝟽𝟷",
    "description": "Spotify API integration untuk musik search dan streaming preview",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".play", ".search", ".minfo", ".pause", ".resume", ".stop", ".trending"],
    "features": ["Spotify API integration", "Music search", "Track preview", "Artist info", "premium emoji", "𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 branding"]
}

__version__ = "0.0.0.𝟽𝟷"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Spotify credentials
SPOTIFY_CLIENT_ID = "2dedf745c9154e2b8053a1c51a4c7412"
SPOTIFY_CLIENT_SECRET = "93257603bc9a4683b7be6c78f0e2500e"

# Global references
vzoel_client = None
vzoel_emoji = None
spotify = None

# Music directories
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
    'current_url': None,
    'track_info': None
}

def init_spotify():
    """Initialize Spotify client"""
    global spotify
    
    if not SPOTIFY_AVAILABLE:
        return False
    
    try:
        # Client credentials flow for accessing public data
        client_credentials_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test connection
        spotify.search('test', limit=1, type='track')
        return True
        
    except Exception as e:
        print(f"Spotify initialization failed: {e}")
        return False

def format_duration_ms(ms):
    """Format duration from milliseconds to MM:SS"""
    try:
        if ms is None:
            return "00:00"
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    except:
        return "00:00"

def get_artist_names(artists):
    """Get formatted artist names from Spotify artists array"""
    try:
        if not artists:
            return "Unknown Artist"
        return ", ".join([artist['name'] for artist in artists])
    except:
        return "Unknown Artist"

async def search_spotify_music(query, limit=5):
    """Search music using Spotify API"""
    global spotify
    
    if not spotify:
        return []
    
    try:
        # Search for tracks
        results = spotify.search(q=query, limit=limit, type='track', market='US')
        
        tracks = []
        for track in results['tracks']['items']:
            track_info = {
                'name': track['name'],
                'artist': get_artist_names(track['artists']),
                'album': track['album']['name'],
                'duration': track['duration_ms'],
                'popularity': track['popularity'],
                'preview_url': track['preview_url'],
                'external_url': track['external_urls']['spotify'],
                'spotify_id': track['id'],
                'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'release_date': track['album']['release_date']
            }
            tracks.append(track_info)
        
        return tracks
        
    except Exception as e:
        print(f"Spotify search error: {e}")
        return []

async def get_track_audio_url(track_info):
    """Get audio URL for playback (using preview or yt-dlp as fallback)"""
    
    # First try preview URL from Spotify
    if track_info.get('preview_url'):
        return track_info['preview_url'], "Spotify preview (30s)"
    
    # Fallback to yt-dlp search
    search_query = f"{track_info['artist']} - {track_info['name']}"
    
    try:
        cmd = [
            'yt-dlp',
            '--quiet',
            '--no-warnings',
            '--get-url',
            '--format', 'bestaudio/best',
            f'ytsearch1:{search_query}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "YouTube audio"
        
    except Exception as e:
        print(f"yt-dlp fallback failed: {e}")
    
    return None, "No audio source available"

async def play_audio_stream(audio_url):
    """Play audio stream using available players"""
    global music_state
    
    # Stop current playback first
    stop_playback()
    
    # List of audio players to try
    players = [
        ['mpv', '--no-video', '--really-quiet'],
        ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet'],
        ['vlc', '--intf', 'dummy', '--play-and-exit'],
        ['mplayer', '-really-quiet']
    ]
    
    for player_cmd in players:
        try:
            # Check if player is available
            subprocess.run([player_cmd[0], '--help'], 
                         capture_output=True, timeout=2)
            
            # Start playback process
            cmd = player_cmd + [audio_url]
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            music_state['process'] = process
            music_state['is_playing'] = True
            music_state['is_paused'] = False
            music_state['current_url'] = audio_url
            
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
        music_state['current_url'] = None
        music_state['track_info'] = None
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
            music_state['current_url'] = None
            music_state['track_info'] = None
    
    return False

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    
    # Initialize Spotify
    if init_spotify():
        print(f"{signature} Spotify Music Plugin loaded - API ready")
    else:
        print(f"{signature} Spotify Music Plugin loaded - API not available")

@events.register(events.NewMessage(pattern=r'\.play (.+)'))
async def play_music_handler(event):
    """Play music using Spotify search"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, spotify
        
        query = event.pattern_match.group(1).strip()
        
        if not SPOTIFY_AVAILABLE or not spotify:
            install_msg = f"""{get_emoji('merah')} Spotify tidak tersedia
            
{get_emoji('kuning')} Error: Spotify API tidak terkoneksi
{get_emoji('aktif')} Check credentials dan koneksi internet
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music System"""
            
            await safe_edit_premium(event, install_msg)
            return
        
        # Show searching message
        searching_msg = f"""{get_emoji('loading')} Mencari musik di Spotify...
        
{get_emoji('proses')} Query: {query}
{get_emoji('aktif')} Engine: Spotify API
{get_emoji('telegram')} Searching tracks...
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Music Search"""
        
        await safe_edit_premium(event, searching_msg)
        
        # Search for music
        results = await search_spotify_music(query, limit=3)
        
        if not results:
            no_results_msg = f"""{get_emoji('kuning')} Tidak ada hasil ditemukan
            
{get_emoji('merah')} Query: {query}
{get_emoji('aktif')} Coba dengan keyword yang berbeda
{get_emoji('telegram')} Atau cek ejaan nama artis/lagu
            
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Spotify Search"""
            
            await safe_edit_premium(event, no_results_msg)
            return
        
        # Display results
        search_results = f"""{get_emoji('utama')} HASIL PENCARIAN SPOTIFY
        
{get_emoji('centang')} Ditemukan {len(results)} hasil untuk: {query}

"""
        
        for i, track in enumerate(results, 1):
            duration_str = format_duration_ms(track['duration'])
            popularity = track['popularity']
            
            search_results += f"""{get_emoji('proses')} {i}. {track['name']}
{get_emoji('aktif')} Artist: {track['artist']}
{get_emoji('kuning')} Album: {track['album']}
{get_emoji('biru')} Duration: {duration_str} | Popularity: {popularity}/100

"""
        
        search_results += f"""{get_emoji('telegram')} Memutar track pertama...
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        
        await safe_edit_premium(event, search_results)
        
        # Try to play the first result
        first_track = results[0]
        duration_str = format_duration_ms(first_track['duration'])
        
        # Update music state
        music_state['track_info'] = first_track
        music_state['current_track'] = f"{first_track['artist']} - {first_track['name']}"
        
        # Show getting audio message
        audio_msg = f"""{get_emoji('loading')} Mencari audio stream...
        
{get_emoji('proses')} {first_track['name']}
{get_emoji('aktif')} Artist: {first_track['artist']}
{get_emoji('telegram')} Getting audio URL...
        
{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 Player"""
        
        await safe_edit_premium(event, audio_msg)
        
        # Get audio URL
        audio_url, audio_source = await get_track_audio_url(first_track)
        
        if audio_url:
            # Try to play the audio
            play_success, play_status = await play_audio_stream(audio_url)
            
            if play_success:
                playing_msg = f"""{get_emoji('utama')} SEDANG MEMUTAR ▶️
        
{get_emoji('proses')} {first_track['name']}
{get_emoji('telegram')} Artist: {first_track['artist']}
{get_emoji('aktif')} Album: {first_track['album']}
{get_emoji('kuning')} Duration: {duration_str}
{get_emoji('centang')} Source: {audio_source}
{get_emoji('biru')} Player: {play_status}
        
{get_emoji('adder1')} Controls: .pause .resume .stop
        
{get_emoji('petir')} Spotify Link: {first_track['external_url']}
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
            else:
                playing_msg = f"""{get_emoji('kuning')} AUDIO DITEMUKAN TAPI TIDAK BISA DIPUTAR
        
{get_emoji('proses')} {first_track['name']}
{get_emoji('telegram')} Artist: {first_track['artist']}
{get_emoji('aktif')} Album: {first_track['album']}
{get_emoji('merah')} Audio Error: {play_status}
{get_emoji('biru')} Source: {audio_source}
        
{get_emoji('adder1')} Spotify Link: {first_track['external_url']}
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        else:
            playing_msg = f"""{get_emoji('merah')} TIDAK ADA AUDIO YANG TERSEDIA
        
{get_emoji('kuning')} Track ditemukan di Spotify tapi tidak ada preview
{get_emoji('proses')} {first_track['name']}
{get_emoji('aktif')} Artist: {first_track['artist']}
        
{get_emoji('telegram')} Solusi:
• Buka langsung di Spotify
• Coba track lain yang ada preview
        
{get_emoji('adder1')} Spotify Link: {first_track['external_url']}
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, playing_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.search (.+)'))
async def search_music_handler(event):
    """Search music on Spotify without playing"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, spotify
        
        query = event.pattern_match.group(1).strip()
        
        if not SPOTIFY_AVAILABLE or not spotify:
            await safe_edit_premium(event, f"{get_emoji('merah')} Spotify API tidak tersedia")
            return
        
        await safe_edit_premium(event, f"{get_emoji('loading')} Mencari di Spotify: {query}...")
        
        results = await search_spotify_music(query, limit=8)
        
        if not results:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ada hasil untuk: {query}")
            return
        
        search_results = f"""{get_emoji('utama')} HASIL PENCARIAN SPOTIFY
        
{get_emoji('centang')} Query: {query}
{get_emoji('proses')} Ditemukan: {len(results)} tracks

"""
        
        for i, track in enumerate(results, 1):
            duration_str = format_duration_ms(track['duration'])
            popularity = track['popularity']
            
            search_results += f"""{i}. {track['name']}
   {get_emoji('aktif')} {track['artist']} | {duration_str} | {popularity}/100
   {get_emoji('biru')} Album: {track['album']} ({track.get('release_date', 'Unknown')})

"""
        
        search_results += f"""{get_emoji('telegram')} Gunakan .play [nama lagu] untuk memutar

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        
        await safe_edit_premium(event, search_results)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.pause'))
async def pause_handler(event):
    """Pause music playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not is_playback_active():
            await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ada musik yang sedang diputar")
            return
        
        if music_state['is_paused']:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Musik sudah dalam keadaan pause")
            return
        
        success = pause_playback()
        
        if success:
            paused_msg = f"""{get_emoji('centang')} MUSIK DIPAUSE ⏸️
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('kuning')} Status: PAUSED
            
{get_emoji('telegram')} Gunakan .resume untuk melanjutkan
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        else:
            paused_msg = f"{get_emoji('merah')} Gagal pause musik"
        
        await safe_edit_premium(event, paused_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.resume'))
async def resume_handler(event):
    """Resume music playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not music_state['is_paused']:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ada musik yang di-pause")
            return
        
        success = resume_playback()
        
        if success:
            resumed_msg = f"""{get_emoji('centang')} MUSIK DILANJUTKAN ▶️
            
{get_emoji('proses')} Track: {music_state['current_track']}
{get_emoji('aktif')} Status: PLAYING
            
{get_emoji('telegram')} Gunakan .pause untuk pause lagi
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        else:
            resumed_msg = f"{get_emoji('merah')} Gagal resume musik"
        
        await safe_edit_premium(event, resumed_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.stop'))
async def stop_handler(event):
    """Stop music playback"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, music_state
        
        if not is_playback_active() and not music_state['is_paused']:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak ada musik yang sedang diputar")
            return
        
        current_track = music_state['current_track']
        success = stop_playback()
        
        if success or current_track:
            stopped_msg = f"""{get_emoji('centang')} MUSIK DIHENTIKAN ⏹️
            
{get_emoji('proses')} Last Track: {current_track or 'Unknown'}
{get_emoji('kuning')} Status: STOPPED
            
{get_emoji('telegram')} Gunakan .play [nama lagu] untuk putar lagi
            
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
        else:
            stopped_msg = f"{get_emoji('centang')} MUSIK SYSTEM RESET"
        
        await safe_edit_premium(event, stopped_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.trending'))
async def trending_handler(event):
    """Get trending music from Spotify"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, spotify
        
        if not SPOTIFY_AVAILABLE or not spotify:
            await safe_edit_premium(event, f"{get_emoji('merah')} Spotify API tidak tersedia")
            return
        
        await safe_edit_premium(event, f"{get_emoji('loading')} Mengambil musik trending...")
        
        try:
            # Search for popular tracks (using generic popular terms)
            trending_queries = ["pop 2024", "viral", "trending", "top hits"]
            all_tracks = []
            
            for query in trending_queries:
                tracks = await search_spotify_music(query, limit=3)
                all_tracks.extend(tracks)
            
            # Sort by popularity and remove duplicates
            unique_tracks = {}
            for track in all_tracks:
                if track['spotify_id'] not in unique_tracks:
                    unique_tracks[track['spotify_id']] = track
            
            sorted_tracks = sorted(unique_tracks.values(), key=lambda x: x['popularity'], reverse=True)[:8]
            
            if not sorted_tracks:
                await safe_edit_premium(event, f"{get_emoji('kuning')} Tidak dapat mengambil trending music")
                return
            
            trending_msg = f"""{get_emoji('utama')} MUSIK TRENDING SPOTIFY
            
{get_emoji('centang')} Top trending tracks:

"""
            
            for i, track in enumerate(sorted_tracks, 1):
                duration_str = format_duration_ms(track['duration'])
                popularity = track['popularity']
                
                trending_msg += f"""{i}. {track['name']}
   {get_emoji('aktif')} {track['artist']} | {duration_str} | {popularity}/100
   {get_emoji('biru')} {track['album']}

"""
            
            trending_msg += f"""{get_emoji('telegram')} Gunakan .play [nama lagu] untuk memutar

𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"""
            
            await safe_edit_premium(event, trending_msg)
            
        except Exception as e:
            await safe_edit_premium(event, f"{get_emoji('merah')} Error mengambil trending: {str(e)}")
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.minfo'))
async def minfo_handler(event):
    """Show music system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji, spotify
        
        # Get playback status
        is_active = is_playback_active()
        status_emoji = "▶️" if music_state['is_playing'] else "⏸️" if music_state['is_paused'] else "⏹️"
        status_text = "PLAYING" if music_state['is_playing'] else "PAUSED" if music_state['is_paused'] else "STOPPED"
        
        spotify_status = "✅ Connected" if (SPOTIFY_AVAILABLE and spotify) else "❌ Not Available"
        
        info_msg = f"""{get_emoji('utama')} 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 SPOTIFY INFO
        
{get_emoji('centang')} SYSTEM STATUS:
• Engine: Spotify Web API
• Status: {spotify_status}
• Version: {__version__}
• Client ID: {SPOTIFY_CLIENT_ID[:8]}...

{get_emoji('proses')} PLAYBACK STATUS:
• Current Track: {music_state['current_track'] or 'None'}
• Status: {status_text} {status_emoji}
• Active Process: {'Yes' if is_active else 'No'}
• Audio Source: {music_state.get('current_url', 'None')[:50] + '...' if music_state.get('current_url') else 'None'}
        
{get_emoji('aktif')} AVAILABLE COMMANDS:
• .play [song] - Search dan putar musik dari Spotify
• .search [song] - Search musik tanpa memutar
• .trending - Tampilkan musik trending
• .pause - Pause current playback
• .resume - Resume paused playback
• .stop - Stop playback completely
• .minfo - Show this info
        
{get_emoji('kuning')} AUDIO SOURCES:
• Spotify Preview (30s clips)
• YouTube fallback via yt-dlp
• Direct stream playback
        
{get_emoji('telegram')} FEATURES:
• Rich metadata from Spotify
• Artist, album, popularity info
• High-quality search results
• Direct Spotify links
• No rate limiting issues
• Global music catalog
        
{get_emoji('adder1')} SPOTIFY INTEGRATION:
• Client Credentials Flow
• Public data access
• Track search & info
• Preview URL access
• Album artwork & metadata
        
𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝

©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"""
        
        await safe_edit_premium(event, info_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()