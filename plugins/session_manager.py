"""
Session Manager Plugin
Manual session management and recovery commands
Created by: Vzoel Fox's
Enhanced by: Claude Code Assistant
"""

from telethon import events
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@events.register(events.NewMessage(pattern=r'^\.session$', outgoing=True))
async def session_status_handler(event):
    """Display current session status and recovery info"""
    try:
        # Get recovery manager from client
        vzoel_client = event.client._vzoel_client_instance
        if not hasattr(vzoel_client, 'recovery_manager') or not vzoel_client.recovery_manager:
            await event.edit("❌ Recovery manager not initialized")
            return
        
        recovery_manager = vzoel_client.recovery_manager
        
        # Check session validity
        check_result = await recovery_manager.check_session_validity()
        
        # Get recovery status
        recovery_status = recovery_manager.get_recovery_status()
        
        # Build status message
        status_msg = "🔍 SESSION STATUS REPORT\n\n"
        
        if check_result["valid"]:
            user_info = check_result.get("user_info", {})
            status_msg += f"✅ SESSION: Valid\n"
            status_msg += f"👤 USER: {user_info.get('first_name', 'Unknown')}\n"
            status_msg += f"🆔 ID: `{user_info.get('id', 'Unknown')}`\n"
            status_msg += f"📞 USERNAME: @{user_info.get('username') or 'None'}\n"
        else:
            status_msg += f"❌ SESSION: Invalid\n"
            status_msg += f"🔧 ERROR TYPE: {check_result.get('error_type', 'Unknown')}\n"
            status_msg += f"📝 ERROR: {check_result.get('error', 'Unknown')}\n"
            if check_result.get('needs_recovery'):
                status_msg += f"⚠️ RECOVERY NEEDED: Yes\n"
        
        status_msg += f"\n📊 RECOVERY STATISTICS:\n"
        status_msg += f"🔄 TOTAL RECOVERIES: {recovery_status.get('total_recoveries', 0)}\n"
        status_msg += f"📁 BACKUP COUNT: {recovery_status.get('backup_count', 0)}\n"
        
        last_check = recovery_status.get('last_check')
        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check)
                status_msg += f"🕐 LAST CHECK: {check_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            except:
                status_msg += f"🕐 LAST CHECK: {last_check}\n"
        
        last_recovery = recovery_status.get('last_recovery')
        if last_recovery:
            try:
                recovery_time = datetime.fromisoformat(last_recovery)
                status_msg += f"🔧 LAST RECOVERY: {recovery_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            except:
                status_msg += f"🔧 LAST RECOVERY: {last_recovery}\n"
        
        status_msg += f"\n📂 BACKUP DIRECTORY: `{recovery_status.get('backup_dir', 'Unknown')}`\n"
        
        if not check_result["valid"] and check_result.get('needs_recovery'):
            status_msg += f"\n🚨 ACTION REQUIRED:\n"
            status_msg += f"Run: `python session_recovery.py`"
        
        await event.edit(status_msg)
        
    except Exception as e:
        logger.error(f"Session status error: {e}")
        await event.edit(f"❌ Failed to get session status: {e}")

@events.register(events.NewMessage(pattern=r'^\.sessioncheck$', outgoing=True))
async def session_check_handler(event):
    """Force session validity check"""
    try:
        await event.edit("🔍 Checking session validity...")
        
        # Get recovery manager from client
        vzoel_client = event.client._vzoel_client_instance
        if not hasattr(vzoel_client, 'recovery_manager') or not vzoel_client.recovery_manager:
            await event.edit("❌ Recovery manager not initialized")
            return
        
        recovery_manager = vzoel_client.recovery_manager
        
        # Perform check
        check_result = await recovery_manager.check_session_validity()
        
        if check_result["valid"]:
            user_info = check_result.get("user_info", {})
            msg = f"✅ SESSION VALID\n\n"
            msg += f"👤 USER: {user_info.get('first_name', 'Unknown')}\n"
            msg += f"🆔 ID: `{user_info.get('id', 'Unknown')}`\n"
            msg += f"📞 USERNAME: @{user_info.get('username') or 'None'}\n"
            msg += f"🕐 CHECKED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            msg = f"❌ SESSION INVALID\n\n"
            msg += f"🔧 ERROR TYPE: {check_result.get('error_type', 'Unknown')}\n"
            msg += f"📝 ERROR: {check_result.get('error', 'Unknown')}\n"
            if check_result.get('needs_recovery'):
                msg += f"\n⚠️ RECOVERY NEEDED!\n"
                msg += f"Run: `python session_recovery.py`"
        
        await event.edit(msg)
        
    except Exception as e:
        logger.error(f"Session check error: {e}")
        await event.edit(f"❌ Session check failed: {e}")

@events.register(events.NewMessage(pattern=r'^\.sessionbackup$', outgoing=True))
async def session_backup_handler(event):
    """Manually backup current session"""
    try:
        await event.edit("📁 Creating session backup...")
        
        # Get recovery manager from client
        vzoel_client = event.client._vzoel_client_instance
        if not hasattr(vzoel_client, 'recovery_manager') or not vzoel_client.recovery_manager:
            await event.edit("❌ Recovery manager not initialized")
            return
        
        recovery_manager = vzoel_client.recovery_manager
        
        # Create backup
        success = recovery_manager.backup_current_session()
        
        if success:
            # Get backup info
            recovery_status = recovery_manager.get_recovery_status()
            msg = f"✅ SESSION BACKUP CREATED\n\n"
            msg += f"📁 BACKUP COUNT: {recovery_status.get('backup_count', 0)}\n"
            msg += f"📂 BACKUP DIRECTORY: `{recovery_status.get('backup_dir', 'Unknown')}`\n"
            msg += f"🕐 CREATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            msg = f"❌ BACKUP FAILED\n\nNo session files found to backup"
        
        await event.edit(msg)
        
    except Exception as e:
        logger.error(f"Session backup error: {e}")
        await event.edit(f"❌ Backup failed: {e}")

@events.register(events.NewMessage(pattern=r'^\.sessionrecovery$', outgoing=True))
async def session_recovery_info_handler(event):
    """Show session recovery information and instructions"""
    try:
        msg = f"🔧 SESSION RECOVERY GUIDE\n\n"
        msg += f"WHEN TO USE RECOVERY:\n"
        msg += f"• Session expired/revoked errors\n"
        msg += f"• AUTH_KEY_UNREGISTERED errors\n"
        msg += f"• Unauthorized access errors\n"
        msg += f"• Bot fails to start due to session issues\n\n"
        
        msg += f"RECOVERY METHODS:\n"
        msg += f"1. INTERACTIVE RECOVERY:\n"
        msg += f"   `python session_recovery.py`\n\n"
        
        msg += f"2. CHECK SESSION STATUS:\n"
        msg += f"   `.session` - Full status report\n"
        msg += f"   `.sessioncheck` - Quick validity check\n\n"
        
        msg += f"3. MANUAL BACKUP:\n"
        msg += f"   `.sessionbackup` - Create session backup\n\n"
        
        msg += f"WHAT RECOVERY DOES:\n"
        msg += f"• ✅ Backs up current session\n"
        msg += f"• ✅ Removes expired session files\n"
        msg += f"• ✅ Creates new session interactively\n"
        msg += f"• ✅ Updates .env file automatically\n"
        msg += f"• ✅ Maintains session history\n\n"
        
        msg += f"RECOVERY PROCESS:\n"
        msg += f"1. Run `python session_recovery.py`\n"
        msg += f"2. Enter phone number with country code\n"
        msg += f"3. Enter verification code from Telegram\n"
        msg += f"4. Enter 2FA password (if enabled)\n"
        msg += f"5. New session saved to .env automatically\n"
        msg += f"6. Restart bot: `python main.py`\n\n"
        
        msg += f"SECURITY NOTES:\n"
        msg += f"⚠️ Never share your string session\n"
        msg += f"⚠️ Backup files contain sensitive data\n"
        msg += f"⚠️ Recovery requires phone access"
        
        await event.edit(msg)
        
    except Exception as e:
        logger.error(f"Session recovery info error: {e}")
        await event.edit(f"❌ Failed to show recovery info: {e}")

# Plugin commands info
commands = {
    ".session": "Show detailed session status and recovery info",
    ".sessioncheck": "Force check session validity",
    ".sessionbackup": "Create manual session backup", 
    ".sessionrecovery": "Show session recovery guide and instructions"
}

# Plugin info
__doc__ = """
Session Manager Plugin

Commands:
• .session - Show detailed session status
• .sessioncheck - Force session validity check  
• .sessionbackup - Create manual session backup
• .sessionrecovery - Show recovery guide

Features:
• Automatic session validity checking
• Session backup management
• Recovery guidance and instructions
• Integration with session recovery system
"""