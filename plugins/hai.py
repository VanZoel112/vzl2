"""
Plugin Hai untuk VzoelFox Userbot - Premium Edition  
Fitur: Interactive greeting dengan edit looping dan premium emoji
Founder Userbot: Vzoel Fox's Ltpn
Version: 1.0.0 - Interactive Hai System
"""

from telethon import events
import asyncio
import random
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VzoelFox style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "hai",
    "version": "1.0.0",
    "description": "Interactive greeting dengan edit looping dan premium emoji",
    "author": "Founder Userbot: Vzoel Fox's Ltpn",
    "commands": [".hai"],
    "features": ["interactive greeting", "edit looping", "premium emoji", "VzoelFox branding"]
}

__version__ = "1.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Hai Plugin loaded - Interactive greeting ready")

@events.register(events.NewMessage(pattern=r'\.hai'))
async def hai_handler(event):
    """Interactive hai command dengan edit looping dan premium emoji"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        # Respon awal
        initial_response = f"hai..... {get_emoji('telegram')}"
        message = await safe_send_premium(event, initial_response)
        
        # Edit phase 1
        await asyncio.sleep(1.5)
        edit1 = f"aku Vzoel Fox's {get_emoji('merah')}"
        await safe_edit_premium(message, edit1)
        
        # Edit phase 2  
        await asyncio.sleep(1.5)
        edit2 = f"kamu lagi ngapain nih {get_emoji('biru')}"
        await safe_edit_premium(message, edit2)
        
        # Edit phase 3
        await asyncio.sleep(1.5)
        edit3 = f"aku cuma gabut doang {get_emoji('kuning')}"
        await safe_edit_premium(message, edit3)
        
        # Edit phase 4
        await asyncio.sleep(1.5)
        edit4 = f"mau ngobrolin apa nih {get_emoji('adder1')}"
        await safe_edit_premium(message, edit4)
        
        # Final delay before hasil
        await asyncio.sleep(2)
        
        # Persiapan emoji looping unlimited - hanya untuk emoji paling atas
        all_premium_emojis = ['utama', 'centang', 'petir', 'loading', 'kuning', 'biru', 'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram']
        
        # Hasil akhir dengan emoji FLAT (tidak berubah) - hanya emoji atas yang berubah
        hasil_flat = f"""Profil by Vzoel Assistant
{get_emoji('biru')} Nama : Vzoel Fox's
{get_emoji('merah')} Zodiac sign : Cancer
{get_emoji('kuning')} Hobby : Ngegame,Berenang,dan Belajar hal baru.
{get_emoji('biru')} Umur : yg jelas bukan om²

{get_emoji('utama')} Developer Assistant : Vzoel Fox's"""
        
        # Looping unlimited untuk emoji di bagian paling atas SAJA
        for i in range(20):  # Loop 20 kali untuk efek unlimited
            await asyncio.sleep(1.5)
            
            # Generate emoji baru HANYA untuk bagian paling atas
            new_emoji_top = get_emoji(random.choice(all_premium_emojis))
            
            # Update hasil dengan emoji baru HANYA di baris pertama
            updated_hasil = f"""{new_emoji_top} {hasil_flat}"""
            
            await safe_edit_premium(message, updated_hasil)
        
        # Final display dengan signature VzoelFox
        await asyncio.sleep(1)
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        final_hasil = f"""{signature} Profil by Vzoel Assistant
{get_emoji('biru')} Nama : Vzoel Fox's
{get_emoji('merah')} Zodiac sign : Cancer
{get_emoji('kuning')} Hobby : Ngegame,Berenang,dan Belajar hal baru.
{get_emoji('biru')} Umur : yg jelas bukan om²

{get_emoji('utama')} Developer Assistant : Vzoel Fox's

{get_emoji('telegram')} ©2025 ~ VZOEL FOX'S PREMIUM SYSTEM"""
        
        await safe_edit_premium(message, final_hasil)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator