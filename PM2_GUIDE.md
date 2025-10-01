# Vzoel Fox's Lutpan - PM2 Setup Guide

## 🚀 Quick Start

### 1. Generate Session (First Time Only)
```bash
cd ~/vzl2
python quick_session.py
```
- Masukkan nomor HP (format: +62xxx)
- Masukkan kode OTP dari Telegram
- Jika ada 2FA, masukkan password

### 2. Start Bot with PM2
```bash
cd ~/vzl2
./start.sh
```

## 📋 PM2 Commands

### Basic Commands
```bash
pm2 status              # Check bot status
pm2 logs vzl2           # View real-time logs
pm2 logs vzl2 --lines 50  # View last 50 lines
pm2 restart vzl2        # Restart bot
pm2 stop vzl2           # Stop bot
pm2 start vzl2          # Start bot
pm2 delete vzl2         # Remove from PM2
```

### Monitoring
```bash
pm2 monit               # Interactive monitoring
pm2 info vzl2           # Detailed bot info
```

### Advanced
```bash
pm2 save                # Save process list
pm2 startup             # Setup auto-start on boot
pm2 resurrect           # Restore saved processes
pm2 flush vzl2          # Clear logs
```

## 📁 File Structure

```
vzl2/
├── ecosystem.config.js    # PM2 configuration
├── start.sh               # Start script
├── quick_session.py       # Session generator
├── main.py                # Main bot file
├── logs/                  # PM2 logs
│   ├── vzl2-error.log
│   └── vzl2-out.log
└── .env                   # Configuration (STRING_SESSION here)
```

## 🔧 Troubleshooting

### Bot keeps restarting
```bash
pm2 logs vzl2 --err      # Check error logs
```

### Session expired
```bash
pm2 stop vzl2
python quick_session.py   # Regenerate session
pm2 start vzl2
```

### Clear everything and restart
```bash
pm2 delete vzl2
rm -rf logs/*
./start.sh
```

## 🎯 Features

- ✅ Auto-restart on crash
- ✅ Log rotation
- ✅ Resource monitoring
- ✅ Easy start/stop/restart
- ✅ Persistent across reboots (with pm2 startup)

## 📞 Support

Contact: @VZLfxs
Created by: Vzoel Fox's Lutpan
