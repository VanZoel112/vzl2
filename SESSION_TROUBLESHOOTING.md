# 🔧 Session Troubleshooting Guide

## 🚨 Common Session Errors

### 1. SessionRevokedError
```
The authorization has been invalidated, because of the user terminating all sessions
```

**Penyebab:**
- User manually terminated all sessions in Telegram
- Multiple concurrent sessions detected
- Telegram spam protection triggered

**Solusi:**
```bash
python quick_recovery.py
# atau
python session_recovery.py
```

### 2. AUTH_KEY_UNREGISTERED
```
AUTH_KEY_UNREGISTERED (401): The key is not registered in the system
```

**Penyebab:**
- Session file corrupted
- Telegram server issues
- Long inactivity period

**Solusi:**
```bash
# Remove old session files
rm *.session*
python session_recovery.py
```

### 3. AUTH_KEY_DUPLICATED
```
AUTH_KEY_DUPLICATED: Multiple sessions detected
```

**Penyebab:**
- Same session used from multiple devices/scripts
- Parallel connections with same auth key

**Solusi:**
```bash
# Stop all other instances first
python session_recovery.py
# Use different session for each instance
```

### 4. UnauthorizedError
```
UnauthorizedError: User not authorized
```

**Penyebab:**
- STRING_SESSION not set or invalid
- .env file corrupted
- API credentials invalid

**Solusi:**
```bash
# Check .env file
cat .env | grep STRING_SESSION
# If empty/invalid, recover:
python session_recovery.py
```

## 🔍 Diagnostic Commands

### Check Session Status
```bash
# In bot (if accessible)
.session

# From command line
python -c "
import asyncio
from session_recovery import SessionRecoveryManager
from config import Config

async def check():
    recovery = SessionRecoveryManager(Config())
    result = await recovery.check_session_validity()
    print(f'Valid: {result[\"valid\"]}')
    if not result['valid']:
        print(f'Error: {result[\"error_type\"]}')

asyncio.run(check())
"
```

### List Session Files
```bash
ls -la *.session*
ls -la session_backups/
```

### Check Configuration
```bash
# Check .env file
cat .env | grep -E "(API_ID|API_HASH|STRING_SESSION|VZOEL_OWNER_ID)"

# Check Python dependencies
python -c "import telethon; print('Telethon:', telethon.__version__)"
```

## 🛠️ Recovery Methods

### Method 1: Quick Recovery (Recommended)
```bash
python quick_recovery.py
```
- ✅ All-in-one solution
- ✅ Pre-flight checks
- ✅ Automatic testing
- ✅ Guided process

### Method 2: Manual Recovery
```bash
python session_recovery.py
```
- ✅ Full control
- ✅ Interactive setup
- ✅ Manual verification
- ✅ Advanced options

### Method 3: Legacy Generate Session
```bash
python generate_session.py
```
- ⚠️ Manual .env update required
- ⚠️ No automatic backup
- ✅ Classic method

### Method 4: In-Bot Recovery (if bot running)
```
.sessioncheck     # Check validity
.sessionbackup    # Backup current
.sessionrecovery  # Show guide
```

## 🔄 Recovery Process Flow

```
1. [ERROR DETECTED] 
   ↓
2. [AUTO BACKUP] Current session saved to session_backups/
   ↓ 
3. [CLEANUP] Remove expired session files
   ↓
4. [INTERACTIVE] Phone → Code → 2FA → New session
   ↓
5. [UPDATE] .env file updated with new STRING_SESSION
   ↓
6. [TEST] Validate new session works
   ↓
7. [COMPLETE] Bot ready to restart
```

## 📁 File Structure

```
vzl2/
├── session_recovery.py          # Main recovery tool
├── quick_recovery.py           # One-click recovery
├── plugins/session_manager.py  # In-bot commands
├── session_backups/            # Auto-backup directory
│   ├── backup_20240917_143022/ 
│   │   ├── .env.backup
│   │   └── vzl2_session.session
│   └── backup_20240917_144533/
├── .session_info.json         # Recovery statistics
└── .env                       # Current configuration
```

## ⚡ Quick Fixes

### Bot Won't Start
```bash
# 1. Check session validity
python -c "from session_recovery import *; import asyncio; asyncio.run(SessionRecoveryManager(Config()).check_session_validity())"

# 2. If invalid, recover
python quick_recovery.py

# 3. Restart bot
python main.py
```

### Session Keeps Expiring
```bash
# 1. Check for multiple instances
ps aux | grep python | grep vzl2

# 2. Stop all instances
pkill -f vzl2

# 3. Create fresh session
python session_recovery.py

# 4. Start single instance only
python main.py
```

### Backup Recovery
```bash
# List available backups
ls -la session_backups/

# Restore from backup (manual)
cp session_backups/backup_YYYYMMDD_HHMMSS/.env.backup .env
cp session_backups/backup_YYYYMMDD_HHMMSS/*.session .

# Test restored session
python -c "from client import vzoel_client; import asyncio; asyncio.run(vzoel_client.initialize_client())"
```

## 🚨 Emergency Recovery

If all else fails:

```bash
# 1. Complete clean slate
rm -rf *.session*
rm -rf __pycache__
rm .env

# 2. Fresh setup
python generate_session.py

# 3. Manual .env configuration
nano .env
# Add your new STRING_SESSION

# 4. Test
python main.py
```

## 📞 Support Commands

### Get Recovery Status
```bash
python -c "
from session_recovery import SessionRecoveryManager
from config import Config
import json

recovery = SessionRecoveryManager(Config())
status = recovery.get_recovery_status()
print(json.dumps(status, indent=2, default=str))
"
```

### Validate Current Session
```bash
python -c "
import asyncio
from client import vzoel_client

async def test():
    try:
        success = await vzoel_client.initialize_client()
        print('✅ Session is valid' if success else '❌ Session is invalid')
        if success:
            await vzoel_client.stop()
    except Exception as e:
        print(f'❌ Session error: {e}')

asyncio.run(test())
"
```

## 🔐 Security Notes

- ⚠️ **Never share your STRING_SESSION** - it's like your account password
- ⚠️ **Backup files contain sensitive data** - secure them properly  
- ⚠️ **Recovery requires phone access** - ensure you can receive SMS/calls
- ⚠️ **2FA password required** - have it ready if enabled
- ⚠️ **Single session per account** - avoid multiple concurrent sessions

## 📊 Session Statistics

Track your session health:
```bash
# Recovery count and backup info
cat .session_info.json | python -m json.tool

# Backup directory size
du -sh session_backups/

# Last session check time
python -c "
import json
try:
    with open('.session_info.json') as f:
        info = json.load(f)
    print(f'Last check: {info.get(\"last_check\", \"Never\")}')
    print(f'Recovery count: {info.get(\"recovery_count\", 0)}')
    print(f'Backup count: {info.get(\"backup_count\", 0)}')
except:
    print('No session info available')
"
```