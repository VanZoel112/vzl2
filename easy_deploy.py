#!/usr/bin/env python3
"""
🚀 VZL2 Easy Deploy - No API ID/Hash Required!
Deploy userbot hanya dengan nomor HP dan kode OTP

Author: VanZoel112
Version: 1.0.0
"""

import os
import sys
import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    FloodWaitError
)

# Default API credentials (dari config VZL2)
DEFAULT_API_ID = 29919905
DEFAULT_API_HASH = "717957f0e3ae20a7db004d08b66bfd30"

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Print welcome banner"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════╗
║  🚀 VZL2 USERBOT - EASY DEPLOY SYSTEM 🚀    ║
║  Deploy tanpa ribet - cuma perlu HP & OTP!   ║
╚══════════════════════════════════════════════╝{Colors.END}

{Colors.YELLOW}📱 Yang Anda Butuhkan:{Colors.END}
  ✅ Nomor HP Telegram (dengan kode negara, contoh: +628123456789)
  ✅ Kode OTP yang akan dikirim ke Telegram
  ✅ Password 2FA (jika aktif)

{Colors.GREEN}Proses deploy akan dimulai...{Colors.END}
"""
    print(banner)

def get_phone_number():
    """Get phone number from user"""
    while True:
        print(f"\n{Colors.BOLD}📱 Masukkan Nomor HP:{Colors.END}")
        print(f"{Colors.CYAN}   Format: +628123456789 (dengan kode negara +){Colors.END}")
        phone = input(f"{Colors.GREEN}   Nomor HP: {Colors.END}").strip()

        if not phone:
            print(f"{Colors.RED}❌ Nomor HP tidak boleh kosong!{Colors.END}")
            continue

        if not phone.startswith('+'):
            print(f"{Colors.YELLOW}⚠️  Menambahkan '+' di depan nomor...{Colors.END}")
            phone = '+' + phone

        confirm = input(f"{Colors.YELLOW}   Nomor: {phone} - Benar? (y/n): {Colors.END}").lower()
        if confirm in ['y', 'yes', 'ya']:
            return phone

def update_env_file(session_string: str, phone: str):
    """Update .env file with new session"""
    env_path = Path('.env')

    if not env_path.exists():
        print(f"{Colors.RED}❌ File .env tidak ditemukan!{Colors.END}")
        return False

    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update STRING_SESSION
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('STRING_SESSION='):
            lines[i] = f'STRING_SESSION={session_string}\n'
            updated = True
            break

    # If not found, add it
    if not updated:
        lines.append(f'\nSTRING_SESSION={session_string}\n')

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)

    print(f"{Colors.GREEN}✅ File .env berhasil diupdate!{Colors.END}")
    return True

async def generate_session():
    """Generate string session with phone number only"""
    print_banner()

    # Get phone number
    phone = get_phone_number()

    print(f"\n{Colors.CYAN}🔐 Menggunakan API credentials default VZL2...{Colors.END}")
    print(f"{Colors.CYAN}📡 Menghubungkan ke Telegram...{Colors.END}\n")

    # Create client with StringSession
    client = TelegramClient(
        StringSession(),
        DEFAULT_API_ID,
        DEFAULT_API_HASH
    )

    try:
        await client.connect()

        # Send code request
        print(f"{Colors.YELLOW}📨 Mengirim kode OTP ke {phone}...{Colors.END}")
        await client.send_code_request(phone)

        # Get OTP code
        print(f"\n{Colors.BOLD}🔢 Masukkan Kode OTP:{Colors.END}")
        print(f"{Colors.CYAN}   Cek Telegram Anda untuk kode verifikasi{Colors.END}")
        code = input(f"{Colors.GREEN}   Kode OTP: {Colors.END}").strip()

        try:
            # Sign in with code
            await client.sign_in(phone, code)

        except SessionPasswordNeededError:
            # 2FA is enabled
            print(f"\n{Colors.YELLOW}🔒 2FA terdeteksi!{Colors.END}")
            password = input(f"{Colors.GREEN}   Password 2FA: {Colors.END}").strip()
            await client.sign_in(password=password)

        except PhoneCodeInvalidError:
            print(f"{Colors.RED}❌ Kode OTP salah! Coba lagi.{Colors.END}")
            await client.disconnect()
            return False

        # Get string session
        session_string = client.session.save()

        # Get user info
        me = await client.get_me()

        print(f"\n{Colors.GREEN}{'='*50}{Colors.END}")
        print(f"{Colors.GREEN}✅ LOGIN BERHASIL!{Colors.END}")
        print(f"{Colors.GREEN}{'='*50}{Colors.END}")
        print(f"{Colors.CYAN}👤 Nama: {me.first_name or ''} {me.last_name or ''}{Colors.END}")
        print(f"{Colors.CYAN}🆔 User ID: {me.id}{Colors.END}")
        print(f"{Colors.CYAN}📱 Username: @{me.username or 'tidak ada'}{Colors.END}")
        print(f"{Colors.GREEN}{'='*50}{Colors.END}\n")

        # Update .env file
        print(f"{Colors.YELLOW}💾 Menyimpan session ke .env...{Colors.END}")
        if update_env_file(session_string, phone):
            print(f"\n{Colors.GREEN}{'='*50}{Colors.END}")
            print(f"{Colors.GREEN}🎉 DEPLOY SELESAI!{Colors.END}")
            print(f"{Colors.GREEN}{'='*50}{Colors.END}")
            print(f"\n{Colors.CYAN}📋 String Session Anda:{Colors.END}")
            print(f"{Colors.YELLOW}{session_string}{Colors.END}\n")
            print(f"{Colors.CYAN}🚀 Cara menjalankan userbot:{Colors.END}")
            print(f"{Colors.YELLOW}   python main.py{Colors.END}")
            print(f"{Colors.CYAN}   atau{Colors.END}")
            print(f"{Colors.YELLOW}   ./start.sh{Colors.END}\n")
            print(f"{Colors.GREEN}✅ Userbot siap digunakan!{Colors.END}\n")

        await client.disconnect()
        return True

    except PhoneNumberInvalidError:
        print(f"{Colors.RED}❌ Nomor HP tidak valid!{Colors.END}")
        await client.disconnect()
        return False

    except FloodWaitError as e:
        print(f"{Colors.RED}❌ Terlalu banyak percobaan! Tunggu {e.seconds} detik.{Colors.END}")
        await client.disconnect()
        return False

    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        await client.disconnect()
        return False

async def main():
    """Main function"""
    try:
        success = await generate_session()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Deploy dibatalkan oleh user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error tidak terduga: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"{Colors.CYAN}Starting VZL2 Easy Deploy System...{Colors.END}\n")
    asyncio.run(main())
