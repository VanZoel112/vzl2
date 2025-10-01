# PM2 Commands - Quick Reference

## 🚀 Start/Stop

```bash
# Start semua bots
pm2 start ecosystem.config.js

# Stop semua
pm2 stop all

# Restart semua
pm2 restart all

# Delete semua dari PM2
pm2 delete all
```

## 🎯 Individual Bot

```bash
# Start
pm2 start vzl2
pm2 start vzoelmenfess

# Stop
pm2 stop vzl2
pm2 stop vzoelmenfess

# Restart
pm2 restart vzl2
pm2 restart vzoelmenfess

# Delete
pm2 delete vzl2
pm2 delete vzoelmenfess
```

## 📊 Monitoring

```bash
# List semua process
pm2 list

# Detail bot tertentu
pm2 show vzl2
pm2 show vzoelmenfess

# Real-time monitor
pm2 monit

# Logs semua bots
pm2 logs

# Logs bot tertentu
pm2 logs vzl2
pm2 logs vzoelmenfess

# Logs error only
pm2 logs --err

# Clear logs
pm2 flush
```

## 💾 Save/Startup

```bash
# Save current process list
pm2 save

# Generate startup script
pm2 startup

# Disable startup
pm2 unstartup
```

## 🔧 Maintenance

```bash
# Kill PM2 daemon
pm2 kill

# Update PM2
pm2 update

# Reload ecosystem
pm2 reload ecosystem.config.js
```

## 📈 Info

```bash
# PM2 version
pm2 --version

# Process info (JSON)
pm2 jlist

# Pretty list
pm2 prettylist
```

---

**🦊 Vzoel Fox's Lutpan**
