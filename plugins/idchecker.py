import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced ID Checker Plugin for 𝗩𝗭𝗢𝗘𝗟 𝗔𝗦𝗦𝗜𝗦𝗧𝗔𝗡𝗧 - Premium Edition
Fitur: Advanced ID checking dengan premium display
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 0.0.0.𝟼𝟿 - Premium ID Checker System
"""

from telethon import events
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import asyncio
import random

# Plugin info
__version__ = "0.0.0.𝟼𝟿"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} ID Checker Plugin loaded - Animated ID detection ready")

@events.register(events.NewMessage(pattern=r'\.id(?: (.+))?'))
async def id_checker_handler(event):
    """ID checker sesuai template dengan emoji premium"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        target_user = None
        args = event.pattern_match.group(1)
        
        # Phase 1: Determine target from arguments or reply
        if event.reply_to_msg_id:
            # Get user from reply
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg.sender:
                    target_user = reply_msg.sender
                else:
                    error_msg = f"{get_emoji('merah')} Cannot get user from reply"
                    await safe_edit_premium(event, error_msg)
                    return
            except Exception as e:
                error_msg = f"{get_emoji('merah')} Error getting reply: {str(e)}"
                await safe_edit_premium(event, error_msg)
                return
                
        elif args:
            # Get user from username/mention
            username = args.strip().replace('@', '')
            try:
                target_user = await event.client.get_entity(username)
            except (UsernameNotOccupiedError, UsernameInvalidError):
                error_msg = f"{get_emoji('merah')} Username @{username} not found"
                await safe_edit_premium(event, error_msg)
                return
            except Exception as e:
                error_msg = f"{get_emoji('merah')} Error finding user: {str(e)}"
                await safe_edit_premium(event, error_msg)
                return
        else:
            # No target specified - get current user
            target_user = await event.client.get_me()
        
        # Respon awal sesuai template
        initial_msg = f"{get_emoji('utama')} sebentar....."
        message = await safe_edit_premium(event, initial_msg)
        
        # Phase 1: Proses sesuai template
        await asyncio.sleep(1.5)
        edit1 = f"{get_emoji('utama')} menginisialisasi user"
        await safe_edit_premium(message, edit1)
        
        await asyncio.sleep(1.5)
        edit2 = f"{get_emoji('proses')} mencari angka user"
        await safe_edit_premium(message, edit2)
        
        await asyncio.sleep(1.5)
        edit3 = f"{get_emoji('loading')} menemukan informasi"
        await safe_edit_premium(message, edit3)
        
        # Delay sebelum hasil
        await asyncio.sleep(2)
        
        # Extract user information
        user_id = target_user.id
        username = target_user.username or "No Username"
        first_name = target_user.first_name or ""
        last_name = target_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "No Name"
        
        # Hasil Phase 1
        hasil1 = f"ID : {user_id} {get_emoji('kuning')}"
        await safe_edit_premium(message, hasil1)
        
        await asyncio.sleep(1.5)
        # Hasil Phase 2
        hasil2 = f"""ID : {user_id} {get_emoji('kuning')}
Nama User : {full_name} {get_emoji('biru')}"""
        await safe_edit_premium(message, hasil2)
        
        await asyncio.sleep(1.5)
        # Hasil Phase 3
        username_display = f"@{username}" if username != "No Username" else "No Username"
        hasil3 = f"""ID : {user_id} {get_emoji('kuning')}
Nama User : {full_name} {get_emoji('biru')}
Username : {username_display} {get_emoji('merah')}"""
        await safe_edit_premium(message, hasil3)
        
        await asyncio.sleep(1.5)
        # Hasil Final
        hasil_final = f"""ID : {user_id} {get_emoji('kuning')}
Nama User : {full_name} {get_emoji('biru')}
Username : {username_display} {get_emoji('merah')}
Info by. Vzoel Assistant {get_emoji('utama')}"""
        await safe_edit_premium(message, hasil_final)
        
        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.idinfo'))
async def id_info_handler(event):
    """Show information about ID checker system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        id_info = f"""{signature} Vzoel Fox's ID Checker

{get_emoji('utama')} Usage Methods:
• .id @username - Check by username
• .id (reply to message) - Check replied user
• .id (no args) - Check your own ID

{get_emoji('centang')} Process Animation:
1. {get_emoji('utama')} sebentar..... (loading)
2. {get_emoji('utama')} menginisialisasi user
3. {get_emoji('proses')} mencari angka user
4. {get_emoji('loading')} menemukan informasi

{get_emoji('aktif')} Display Results:
1. ID : [user_id] {get_emoji('kuning')}
2. Nama User : [full_name] {get_emoji('biru')}
3. Username : [@username] {get_emoji('merah')}
4. Info by. Vzoel Assistant {get_emoji('utama')}

{get_emoji('telegram')} Features:
• Premium emoji integration
• Step-by-step animation
• Clean information display
• Vzoel Fox's branding

By Vzoel Fox's Assistant"""
        
        await safe_edit_premium(event, id_info)
        if vzoel_client:
            vzoel_client.increment_command_count()
