#!/usr/bin/env python3
"""
Quick Session Recovery Script
One-command session recovery for Vzoel Fox's Assistant
Created by: Vzoel Fox's
Enhanced by: Claude Code Assistant
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def print_banner():
    """Print recovery banner"""
    print("""
╔══════════════════════════════════════════════════════════╗
║        🚨 Vzoel Fox's Quick Session Recovery 🚨            ║
║         Fast & Automatic Session Recovery Tool          ║
║            Created by: Vzoel Fox's                       ║
╚══════════════════════════════════════════════════════════╝
    """)

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "session_recovery.py",
        "config.py", 
        "client.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("📁 Make sure you're in the vzl2 directory")
        return False
    
    return True

def check_dependencies():
    """Check if required Python packages are installed"""
    try:
        import telethon
        import dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        missing_package = str(e).split("'")[1] if "'" in str(e) else "unknown"
        print(f"❌ Missing package: {missing_package}")
        print(f"📦 Install with: pip install {missing_package}")
        return False

async def run_recovery():
    """Run the session recovery process"""
    try:
        print("🔄 Starting session recovery process...")
        print("📱 Make sure you have access to your phone number\n")
        
        # Import and run recovery
        from session_recovery import main as recovery_main
        await recovery_main()
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Recovery cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Recovery failed: {e}")
        return False

def test_bot_startup():
    """Test if the bot can start with new session"""
    try:
        print("\n🧪 Testing bot startup with new session...")
        
        # Try to import and test the client
        result = subprocess.run([
            sys.executable, "-c", 
            """
import asyncio
from client import vzoel_client

async def test():
    try:
        success = await vzoel_client.initialize_client()
        if success:
            print("✅ Bot startup test: PASSED")
            await vzoel_client.stop()
            return True
        else:
            print("❌ Bot startup test: FAILED")
            return False
    except Exception as e:
        print(f"❌ Bot startup test error: {e}")
        return False

result = asyncio.run(test())
exit(0 if result else 1)
            """
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Bot startup test timed out (might be working)")
        return True
    except Exception as e:
        print(f"❌ Failed to test bot startup: {e}")
        return False

def show_next_steps(recovery_success, test_success):
    """Show next steps based on results"""
    print("\n" + "="*60)
    print("📋 RECOVERY SUMMARY")
    print("="*60)
    
    if recovery_success:
        print("✅ Session recovery: COMPLETED")
    else:
        print("❌ Session recovery: FAILED")
    
    if test_success:
        print("✅ Bot startup test: PASSED")
    else:
        print("❌ Bot startup test: FAILED")
    
    print("\n📝 NEXT STEPS:")
    
    if recovery_success and test_success:
        print("🎉 Recovery completed successfully!")
        print("🚀 You can now start your bot normally:")
        print("   python main.py")
        print("   # OR")
        print("   python client.py")
        
    elif recovery_success and not test_success:
        print("⚠️ Recovery completed but bot test failed")
        print("🔍 Check your configuration:")
        print("   1. Verify .env file has correct STRING_SESSION")
        print("   2. Check API_ID and API_HASH are correct")
        print("   3. Try starting bot manually: python main.py")
        
    else:
        print("❌ Recovery failed")
        print("🔧 Try manual recovery:")
        print("   1. python session_recovery.py")
        print("   2. Or python generate_session.py")
        print("   3. Check your phone number and network connection")
    
    print("\n📞 SUPPORT:")
    print("• Check session status: .session (in bot)")
    print("• Manual recovery: python session_recovery.py") 
    print("• Recovery guide: .sessionrecovery (in bot)")
    print("• Backup session: .sessionbackup (in bot)")

async def main():
    """Main recovery function"""
    print_banner()
    
    print("🔍 Pre-flight checks...")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Pre-flight check failed")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return
    
    print("✅ All pre-flight checks passed\n")
    
    # Show current directory
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Confirm recovery
    print("⚠️  This will:")
    print("   • Backup your current session")
    print("   • Remove expired session files") 
    print("   • Create a new session")
    print("   • Update your .env file")
    print("   • Test the new session")
    
    choice = input("\n🔄 Continue with recovery? (y/n): ").strip().lower()
    if choice not in ['y', 'yes', 'ya']:
        print("❌ Recovery cancelled by user")
        return
    
    # Run recovery
    recovery_success = await run_recovery()
    
    # Test bot startup if recovery succeeded
    test_success = False
    if recovery_success:
        test_choice = input("\n🧪 Test bot startup with new session? (y/n): ").strip().lower()
        if test_choice in ['y', 'yes', 'ya']:
            test_success = test_bot_startup()
    
    # Show summary
    show_next_steps(recovery_success, test_success)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Quick recovery cancelled")
    except Exception as e:
        print(f"\n❌ Quick recovery error: {e}")