"""
VzoelFox's Assistant Limit Checker Plugin
Advanced spam protection and account restriction checker via @spambot
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
from telethon.errors import FloodWaitError, UserNotMutualContactError, UserPrivacyRestrictedError
import asyncio
import re
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variables for limit checking
limit_active = {}
limit_tasks = {}

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Limit Checker Plugin loaded - Anti-flood ready")

@events.register(events.NewMessage(pattern=r'\.limit'))
async def limit_checker_handler(event):
    """Check account limits and restrictions via @spambot"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        chat_id = event.chat_id if not event.is_private else event.sender_id
        
        # Stop any existing limit check
        if chat_id in limit_tasks and not limit_tasks[chat_id].done():
            limit_tasks[chat_id].cancel()
        
        limit_active[chat_id] = True
        
        # Initial process message
        process_msg = f"{get_emoji('loading')} Memulai pengecekan limit akun..."
        msg = await event.edit(process_msg)
        
        # Start limit checking task
        limit_tasks[chat_id] = asyncio.create_task(
            perform_limit_check(event, msg)
        )
        try:
            await limit_tasks[chat_id]
        except asyncio.CancelledError:
            cancel_msg = f"{get_emoji('kuning')} Pengecekan limit dibatalkan"
            await safe_edit_premium(msg, cancel_msg)
        finally:
            limit_active[chat_id] = False
        
        vzoel_client.increment_command_count()

async def perform_limit_check(event, msg):
    """Perform the actual limit checking process"""
    from emoji_handler_premium import vzoel_emoji
    
    try:
        # Phase 1: Connecting to @spambot
        await safe_edit_premium(msg, f"{get_emoji('proses')} Menghubungi @spambot untuk cek status...")
        await asyncio.sleep(1)
        
        # Phase 2: Sending multiple /start commands
        await safe_edit_premium(msg, f"{get_emoji('loading')} Mengirim perintah /start ke @spambot...")
        
        # Send /start command multiple times for thorough check
        responses = []
        for i in range(3):
            try:
                # Send /start to @spambot
                await event.client.send_message('@spambot', '/start')
                await asyncio.sleep(2)
                
                # Get recent messages from @spambot
                async for message in event.client.iter_messages('@spambot', limit=5):
                    if message.message and message.date:
                        responses.append(message.message.lower())
                        break
                
                # Update progress
                await safe_edit_premium(msg, f"{get_emoji('aktif')} Mengirim perintah ke @spambot ({i+1}/3)...")
                
            except FloodWaitError as e:
                # Handle flood wait from spambot
                await safe_edit_premium(msg, f"{get_emoji('kuning')} Menunggu {e.seconds} detik (flood protection)...")
                await asyncio.sleep(e.seconds + 1)
            except (UserNotMutualContactError, UserPrivacyRestrictedError):
                # Handle privacy/contact issues
                await safe_edit_premium(msg, f"{get_emoji('merah')} Tidak dapat mengakses @spambot. Coba lagi nanti.")
                return
        
        # Phase 3: Analyzing responses
        await safe_edit_premium(msg, f"{get_emoji('proses')} Menganalisis respons dari @spambot...")
        await asyncio.sleep(2)
        
        # Analyze spambot responses
        account_status = analyze_spambot_responses(responses)
        
        # Phase 4: Final result
        if account_status['restricted']:
            # Account is restricted - use red emoji
            restriction_msg = f"""**{get_emoji('merah')} AKUN DIBATASI**

{get_emoji('merah')} **Status:** Account Restricted
{get_emoji('petir')} **Tipe:** {account_status['restriction_type']}
{get_emoji('telegram')} **Durasi:** {account_status['duration']}
{get_emoji('proses')} **Pesan Bot:** {account_status['bot_message']}

{get_emoji('kuning')} **Saran:**
• Tunggu hingga pembatasan berakhir
• Kurangi aktivitas spam
• Gunakan delay lebih lama antar pesan
• Hindari broadcast massal

**VzoelFox Limit Checker**"""
            await safe_edit_premium(msg, restriction_msg)
        elif account_status['good_news']:
            # Good news from spambot - account is safe
            safe_msg = f"""**{get_emoji('centang')} VZOEL FOX'S AMAN**

{get_emoji('utama')} **Status:** Account Clear
{get_emoji('aktif')} **Anti-Flood:** Active
{get_emoji('telegram')} **Spam Protection:** Enabled
{get_emoji('petir')} **Limit Status:** No Restrictions

{get_emoji('centang')} **VzoelFox Features:**
• Flood protection aktif
• Spam detection enabled
• Account dalam kondisi baik
• Siap untuk broadcast/gcast

{get_emoji('proses')} **Bot Message:** {account_status['bot_message']}

**Vzoel Fox's Aman!**"""
            await safe_edit_premium(msg, safe_msg)
        else:
            # Unclear response or other status
            unclear_msg = f"""**{get_emoji('kuning')} STATUS TIDAK JELAS**

{get_emoji('loading')} **Status:** Unknown
{get_emoji('proses')} **Respons Bot:** {account_status['bot_message']}
{get_emoji('telegram')} **Saran:** Coba lagi dalam beberapa menit

{get_emoji('utama')} **Kemungkinan:**
• @spambot sedang maintenance
• Koneksi tidak stabil
• Respons bot tidak standar

**VzoelFox Limit Checker**"""
            await safe_edit_premium(msg, unclear_msg)
    
    except Exception as e:
        error_msg = f"{get_emoji('merah')} Error saat cek limit: {str(e)}"
        await safe_edit_premium(msg, error_msg)

def analyze_spambot_responses(responses):
    """Analyze spambot responses to determine account status"""
    result = {
        'restricted': False,
        'good_news': False,
        'restriction_type': 'Unknown',
        'duration': 'Unknown',
        'bot_message': 'No response received'
    }
    
    if not responses:
        return result
    
    # Combine all responses
    combined_response = ' '.join(responses)
    result['bot_message'] = combined_response[:200] + '...' if len(combined_response) > 200 else combined_response
    
    # Check for restrictions
    restriction_keywords = [
        'restricted', 'limited', 'spam', 'flood', 'banned', 
        'temporarily', 'violated', 'terms', 'blocked'
    ]
    
    # Check for good news
    good_news_keywords = [
        'good news', 'kabar baik', 'no restrictions', 'clear', 
        'safe', 'aman', 'normal', 'unrestricted'
    ]
    
    # Analyze for restrictions
    for keyword in restriction_keywords:
        if keyword in combined_response:
            result['restricted'] = True
            # Try to extract restriction type
            if 'flood' in combined_response:
                result['restriction_type'] = 'Flood Wait'
            elif 'spam' in combined_response:
                result['restriction_type'] = 'Spam Detection'
            elif 'banned' in combined_response:
                result['restriction_type'] = 'Account Banned'
            else:
                result['restriction_type'] = 'General Restriction'
            # Try to extract duration
            duration_match = re.search(r'(\d+)\s*(hour|day|minute)', combined_response)
            if duration_match:
                result['duration'] = f"{duration_match.group(1)} {duration_match.group(2)}(s)"
            break
    
    # Check for good news (only if not restricted)
    if not result['restricted']:
        for keyword in good_news_keywords:
            if keyword in combined_response:
                result['good_news'] = True
                break
    
    return result

@events.register(events.NewMessage(pattern=r'\.limitinfo'))
async def limit_info_handler(event):
    """Show information about limit checker system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        limit_info = f"""**{signature} Limit Checker Information**

{get_emoji('utama')} **Apa itu Limit Checker?**
Sistem untuk memeriksa status akun dan pembatasan melalui @spambot dengan mengirim perintah /start berulang.

{get_emoji('centang')} **Cara Kerja:**
• Mengirim /start ke @spambot 3x berturut-turut
• Menganalisis respons untuk deteksi pembatasan
• Memberikan feedback dengan emoji sesuai status
• Anti-flood protection dengan delay otomatis

{get_emoji('aktif')} **Status Response:**
• {get_emoji('merah')} **Merah** - Akun dibatasi/restricted
• {get_emoji('centang')} **Hijau** - "Vzoel Fox's Aman" (kabar baik)
• {get_emoji('kuning')} **Kuning** - Status tidak jelas

{get_emoji('telegram')} **Deteksi Pembatasan:**
• Flood wait restrictions
• Spam detection alerts  
• Account temporary bans
• General limitations

{get_emoji('proses')} **Anti-Flood Features:**
• 2 detik delay antar perintah
• Flood wait error handling
• Privacy restriction handling
• Multiple attempt system

{get_emoji('petir')} **Usage:**
Simply type `.limit` to start comprehensive account restriction check via @spambot interaction.

**By VzoelFox Assistant**"""
        
        
        msg = await event.edit(limit_info)
        vzoel_client.increment_command_count()
