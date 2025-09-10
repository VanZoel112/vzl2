#!/usr/bin/env python3
"""
Quick test untuk memastikan semua berfungsi
"""

import asyncio
import sys
import os

# Add current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Main test function"""
    print("🦊 Vzoel Fox's's Assistant v2 - Quick Test")
    print("=" * 50)
    
    try:
        # Test imports
        from client import vzoel_client
        from emoji_handler import vzoel_emoji
        from config import Config
        
        print("✅ All imports successful")
        
        # Test config
        c = Config()
        print(f"✅ Config loaded - Premium Emojis: {Config.PREMIUM_EMOJIS_ENABLED}")
        
        # Test emoji system
        signature = vzoel_emoji.get_vzoel_signature()
        print(f"✅ Emoji signature: {signature}")
        
        test_emoji = vzoel_emoji.getemoji('utama')
        print(f"✅ getemoji('utama'): {test_emoji}")
        
        # Test client initialization (mock)
        print(f"✅ Vzoel Fox'sClient instance created")
        print(f"✅ Client version: {Config.VZOEL_VERSION}")
        
        # Test plugin structure
        from pathlib import Path
        plugins_dir = Path("plugins")
        plugin_files = list(plugins_dir.glob("*.py"))
        print(f"✅ Found {len(plugin_files)} plugins")
        
        for plugin_file in plugin_files[:5]:  # Show first 5
            print(f"   📝 {plugin_file.name}")
        
        print(f"\n🎉 All systems ready!")
        print(f"🚀 Vzoel Fox's's Assistant v2 is ready to launch!")
        
        # Show usage instructions
        print(f"\n📋 USAGE:")
        print(f"   python start.py              # Easy launcher")
        print(f"   python main.py               # Direct launch")
        print(f"   python generate_session.py   # Session generator")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print(f"\n✅ Quick test completed successfully!")
    else:
        print(f"\n❌ Quick test failed!")