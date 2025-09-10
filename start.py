#!/usr/bin/env python3
"""
Vzoel Fox's's Assistant v2 - Easy Starter
User-friendly launcher with automatic session handling
Created by: Vzoel Fox's
"""

import asyncio
import os
import sys
import subprocess

def show_banner():
    """Show startup banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          🦊 Vzoel Fox's's Assistant v2 Easy Starter        ║
║        Automatic Session Management & Easy Setup        ║
║            Created by: Vzoel Fox's                       ║
╚══════════════════════════════════════════════════════════╝
""")

def check_session():
    """Check if session exists"""
    # Check for .env file with STRING_SESSION
    if os.path.exists('.env'):
        try:
            with open('.env', 'r') as f:
                content = f.read()
                if 'STRING_SESSION=' in content:
                    # Check if not empty
                    for line in content.split('\n'):
                        if line.startswith('STRING_SESSION=') and '=' in line:
                            session_value = line.split('=', 1)[1].strip()
                            if session_value and session_value != 'your_string_session_if_available':
                                return True
        except Exception:
            pass
    
    # Check for session file
    if os.path.exists('vzl2_session.session'):
        return True
    
    return False

def main():
    """Main launcher function"""
    show_banner()
    
    if check_session():
        print("✅ Session ditemukan!")
        print("🚀 Memulai Vzoel Fox's's Assistant v2...")
        
        # Start the main bot
        try:
            result = subprocess.run([sys.executable, 'main.py'], cwd=os.getcwd())
            return result.returncode
        except KeyboardInterrupt:
            print("\n👋 Bot dihentikan oleh user")
            return 0
        except Exception as e:
            print(f"❌ Error menjalankan bot: {e}")
            return 1
    
    else:
        print("❌ Session tidak ditemukan!")
        print("📱 Anda perlu membuat session Telegram terlebih dahulu")
        print("\n🔧 CARA SETUP:")
        print("1. Siapkan API_ID dan API_HASH dari https://my.telegram.org/apps")
        print("2. Pastikan nomor telepon aktif untuk menerima kode verifikasi")
        print("3. Ikuti instruksi yang akan muncul")
        
        while True:
            try:
                choice = input("\n🎯 Generate session sekarang? (y/n): ").lower().strip()
                
                if choice in ['y', 'yes', 'ya']:
                    print("\n🔄 Menjalankan session generator...")
                    try:
                        result = subprocess.run([sys.executable, 'main.py', '--generate-session'], 
                                               cwd=os.getcwd())
                        
                        if result.returncode == 0:
                            print("\n✅ Session berhasil dibuat!")
                            choice2 = input("🚀 Jalankan bot sekarang? (y/n): ").lower().strip()
                            
                            if choice2 in ['y', 'yes', 'ya']:
                                print("🔄 Memulai Vzoel Fox's's Assistant v2...")
                                result2 = subprocess.run([sys.executable, 'main.py'], 
                                                        cwd=os.getcwd())
                                return result2.returncode
                            else:
                                print("👍 Session siap! Jalankan 'python start.py' kapan saja")
                                return 0
                        else:
                            print("❌ Gagal membuat session!")
                            return 1
                            
                    except KeyboardInterrupt:
                        print("\n👋 Setup dibatalkan")
                        return 0
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        return 1
                
                elif choice in ['n', 'no', 'tidak']:
                    print("\n📋 Manual Setup:")
                    print("   python main.py --generate-session")
                    print("   python main.py")
                    print("\n👋 Sampai jumpa!")
                    return 0
                
                else:
                    print("❌ Pilihan tidak valid! Masukkan 'y' atau 'n'")
                    
            except KeyboardInterrupt:
                print("\n👋 Sampai jumpa!")
                return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)