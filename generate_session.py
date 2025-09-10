"""
Vzoel Fox's's Session Generator
Interactive session generator for Vzoel Fox's's Assistant v2
Created by: Vzoel Fox's
"""

import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, PhoneCodeInvalidError

def get_vzoel_banner():
    """Get Vzoel Fox's's signature banner"""
    return """
╔══════════════════════════════════════════════════════════╗
║          🦊 Vzoel Fox's's Session Generator v2              ║
║        Interactive Telegram Session Generator            ║
║            Created by: Vzoel Fox's                       ║
╚══════════════════════════════════════════════════════════╝
"""

def get_api_credentials():
    """Get API ID and API Hash from user"""
    print("📱 Masukkan kredensial API Telegram Anda:")
    print("   Dapatkan dari: https://my.telegram.org/apps\n")
    
    while True:
        try:
            api_id = input("🔑 API ID: ").strip()
            if not api_id:
                print("❌ API ID tidak boleh kosong!")
                continue
            api_id = int(api_id)
            break
        except ValueError:
            print("❌ API ID harus berupa angka!")
    
    while True:
        api_hash = input("🔐 API Hash: ").strip()
        if api_hash:
            break
        print("❌ API Hash tidak boleh kosong!")
    
    return api_id, api_hash

def get_phone_number():
    """Get phone number from user"""
    print("\n📞 Masukkan nomor telepon Anda:")
    print("   Format: +62xxxxxxxxx (dengan kode negara)")
    
    while True:
        phone = input("📱 Nomor telepon: ").strip()
        if phone:
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone
        print("❌ Nomor telepon tidak boleh kosong!")

async def generate_string_session():
    """Generate string session interactively"""
    try:
        print(get_vzoel_banner())
        print("🚀 Memulai proses generate session...")
        print("⚠️  Pastikan Anda memiliki akses ke nomor telepon yang akan didaftarkan\n")
        
        # Get API credentials
        api_id, api_hash = get_api_credentials()
        
        print(f"\n✅ API ID: {api_id}")
        print(f"✅ API Hash: {api_hash[:8]}...")
        
        # Create client with string session
        print("\n🔄 Membuat koneksi ke Telegram...")
        client = TelegramClient(StringSession(), api_id, api_hash)
        
        await client.connect()
        
        # Get phone number
        phone = get_phone_number()
        print(f"\n📞 Mengirim kode verifikasi ke: {phone}")
        
        # Send code request
        try:
            await client.send_code_request(phone)
        except PhoneNumberInvalidError:
            print(f"❌ Nomor telepon tidak valid: {phone}")
            print("   Pastikan format nomor benar (contoh: +628123456789)")
            return None
        except Exception as e:
            print(f"❌ Gagal mengirim kode verifikasi: {e}")
            return None
        
        print("✅ Kode verifikasi telah dikirim!")
        print("📨 Periksa aplikasi Telegram Anda untuk kode verifikasi\n")
        
        # Get verification code
        while True:
            try:
                code = input("🔢 Masukkan kode verifikasi: ").strip()
                if not code:
                    print("❌ Kode verifikasi tidak boleh kosong!")
                    continue
                
                print("🔄 Memverifikasi kode...")
                await client.sign_in(phone, code)
                break
                
            except PhoneCodeInvalidError:
                print("❌ Kode verifikasi salah! Coba lagi.")
                continue
            except SessionPasswordNeededError:
                # 2FA is enabled
                print("\n🔐 Akun Anda menggunakan 2FA (Two-Factor Authentication)")
                while True:
                    password = input("🔒 Masukkan password 2FA: ")
                    try:
                        await client.sign_in(password=password)
                        break
                    except Exception as e:
                        print(f"❌ Password 2FA salah: {e}")
                break
            except Exception as e:
                print(f"❌ Error saat sign in: {e}")
                continue
        
        # Get user info
        me = await client.get_me()
        
        # Generate string session
        string_session = client.session.save()
        
        print(f"\n🎉 Session berhasil dibuat!")
        print(f"👤 Nama: {me.first_name}")
        print(f"📞 Username: @{me.username or 'Tidak ada'}")
        print(f"🆔 User ID: {me.id}")
        
        print("\n" + "="*60)
        print("🔑 STRING SESSION ANDA:")
        print("="*60)
        print(f"{string_session}")
        print("="*60)
        
        print("\n📝 LANGKAH SELANJUTNYA:")
        print("1. Copy string session di atas")
        print("2. Buat file .env di folder vzl2")
        print("3. Tambahkan baris berikut ke file .env:")
        print(f"   STRING_SESSION={string_session}")
        print("4. Jalankan client.py dengan: python client.py")
        
        print("\n⚠️  PENTING:")
        print("   - Jangan share string session dengan siapapun!")
        print("   - String session sama seperti password akun Anda")
        print("   - Simpan dengan aman!")
        
        await client.disconnect()
        return string_session
        
    except KeyboardInterrupt:
        print("\n\n❌ Proses dibatalkan oleh user")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def save_to_env_file(string_session, api_id, api_hash):
    """Save session to .env file"""
    try:
        env_content = f"""# Vzoel Fox's's Assistant v2 Configuration
# Generated automatically by session generator

# API Configuration (Required)
API_ID={api_id}
API_HASH={api_hash}

# Session
STRING_SESSION={string_session}

# Optional Settings
VZOEL_PREFIX=.
# VZOEL_OWNER_ID=123456789
# VZOEL_LOG_CHAT=-1001234567890

# Premium Features
PREMIUM_EMOJIS_ENABLED=true
EMOJI_MAPPING_FILE=emoji_mapping.json

# Advanced Settings
WORKERS=4
LOAD_UNOFFICIAL_PLUGINS=false

# Database
DATABASE_URL=sqlite:///vzl2.db
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ File .env berhasil dibuat!")
        print("📁 Lokasi: ./env")
        return True
        
    except Exception as e:
        print(f"❌ Gagal membuat file .env: {e}")
        return False

async def main():
    """Main function"""
    try:
        string_session = await generate_string_session()
        
        if string_session:
            print(f"\n🎯 Apakah Anda ingin menyimpan konfigurasi ke file .env? (y/n): ", end="")
            choice = input().strip().lower()
            
            if choice in ['y', 'yes', 'ya']:
                # We need to get API credentials again for .env file
                print("\n📋 Untuk file .env, masukkan kembali API credentials:")
                api_id, api_hash = get_api_credentials()
                save_to_env_file(string_session, api_id, api_hash)
        
        print("\n🦊 Terima kasih telah menggunakan Vzoel Fox's's Session Generator!")
        print("🚀 Sekarang Anda dapat menjalankan Vzoel Fox's's Assistant v2")
        
    except Exception as e:
        print(f"❌ Error dalam main function: {e}")

if __name__ == "__main__":
    print("🔄 Memulai Vzoel Fox's's Session Generator...")
    
    # Check if telethon is installed
    try:
        import telethon
    except ImportError:
        print("❌ Telethon tidak terinstall!")
        print("📦 Install dengan: pip install telethon")
        sys.exit(1)
    
    # Run the session generator
    asyncio.run(main())