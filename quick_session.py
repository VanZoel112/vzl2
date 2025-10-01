#!/usr/bin/env python3
"""
Quick Session Generator for Vzoel Fox's Lutpan
Generate STRING_SESSION and save to .env
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import os

async def main():
    print("🦊 Vzoel Fox's Lutpan - Quick Session Generator\n")

    # Get credentials from .env or ask
    api_id = os.getenv("API_ID", "29919905")
    api_hash = os.getenv("API_HASH", "717957f0e3ae20a7db004d08b66bfd30")

    print(f"📱 API ID: {api_id}")
    print(f"🔑 API Hash: {api_hash[:10]}...")
    print()

    # Ask for phone number
    phone = input("📞 Masukkan nomor telepon (format: +62xxx): ").strip()

    if not phone.startswith('+'):
        phone = '+' + phone

    print("\n🔄 Connecting to Telegram...")

    # Create client with empty string session
    client = TelegramClient(StringSession(), int(api_id), api_hash)

    try:
        await client.connect()

        # Send code request
        print("📨 Sending code...")
        await client.send_code_request(phone)

        # Ask for code
        code = input("🔢 Masukkan kode OTP: ").strip()

        # Sign in
        try:
            await client.sign_in(phone, code)
        except Exception as e:
            if "password" in str(e).lower() or "2fa" in str(e).lower():
                password = input("🔐 Masukkan 2FA password: ").strip()
                await client.sign_in(password=password)
            else:
                raise

        # Get string session
        string_session = client.session.save()

        print("\n✅ Login berhasil!")
        print(f"\n📝 STRING_SESSION:\n{string_session}\n")

        # Update .env file
        env_path = ".env"

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Update STRING_SESSION line
            found = False
            for i, line in enumerate(lines):
                if line.startswith("STRING_SESSION="):
                    lines[i] = f"STRING_SESSION={string_session}\n"
                    found = True
                    break

            if not found:
                lines.append(f"\nSTRING_SESSION={string_session}\n")

            with open(env_path, 'w') as f:
                f.writelines(lines)

            print("✅ .env file updated!")
        else:
            print("⚠️ .env file not found, creating new one...")
            with open(env_path, 'w') as f:
                f.write(f"""# Vzoel Fox's Lutpan Configuration
API_ID={api_id}
API_HASH={api_hash}
STRING_SESSION={string_session}

VZOEL_PREFIX=.
PREMIUM_EMOJIS_ENABLED=true
WORKERS=4
""")
            print("✅ .env file created!")

        print("\n🚀 Sekarang Anda bisa jalankan bot dengan:")
        print("   ./start.sh")
        print("   atau: pm2 start ecosystem.config.js")

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
