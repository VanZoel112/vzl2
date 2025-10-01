# 🤖 PM2 Management - Vzoel Bots

Panduan lengkap mengelola **VZL2 Userbot** dan **Vzoelmenfess Bot** menggunakan PM2.

---

## 📦 Setup Awal

### 1. Install PM2 (jika belum)

```bash
npm install -g pm2
```

### 2. Cek PM2 terinstall

```bash
pm2 --version
```

---

## 🚀 Quick Start

### Cara Termudah - Pakai Scripts

```bash
# Start semua bots
~/start_bots.sh

# Stop semua bots
~/stop_bots.sh

# Restart semua bots
~/restart_bots.sh

# Cek status bots
~/status_bots.sh
```

### Cara Manual - Pakai PM2 Langsung

```bash
# Start semua bots
pm2 start ~/ecosystem.config.js

# Stop semua bots
pm2 stop all

# Restart semua bots
pm2 restart all

# Delete semua bots dari PM2
pm2 delete all
```

---

## 📊 Monitoring & Logs

### Cek Status Bots

```bash
# List semua process
pm2 list

# Detail lengkap
pm2 show vzl2
pm2 show vzoelmenfess

# Real-time monitoring
pm2 monit
```

### Lihat Logs

```bash
# Logs semua bots
pm2 logs

# Logs VZL2 only
pm2 logs vzl2

# Logs Vzoelmenfess only
pm2 logs vzoelmenfess

# Logs dengan filter error
pm2 logs --err

# Clear logs
pm2 flush
```

---

## 🔧 Management Commands

### Start/Stop Individual Bot

```bash
# Start VZL2 only
pm2 start vzl2

# Start Vzoelmenfess only
pm2 start vzoelmenfess

# Stop VZL2 only
pm2 stop vzl2

# Stop Vzoelmenfess only
pm2 stop vzoelmenfess

# Restart VZL2 only
pm2 restart vzl2

# Restart Vzoelmenfess only
pm2 restart vzoelmenfess
```

### Auto-Start on Boot (Termux)

```bash
# Generate startup script
pm2 startup

# Save current process list
pm2 save

# Disable auto-start
pm2 unstartup
```

---

## 📁 File Locations

```
/data/data/com.termux/files/home/
├── ecosystem.config.js          # PM2 config file
├── start_bots.sh               # Quick start script
├── stop_bots.sh                # Quick stop script
├── restart_bots.sh             # Quick restart script
├── status_bots.sh              # Status checker script
├── logs/                       # Log directory
│   ├── vzl2-error.log         # VZL2 error logs
│   ├── vzl2-out.log           # VZL2 output logs
│   ├── vzoelmenfess-error.log # Menfess error logs
│   └── vzoelmenfess-out.log   # Menfess output logs
├── vzl2/                       # VZL2 userbot
│   └── main.py
└── vzoelmenfess/               # Vzoelmenfess bot
    └── bot.js
```

---

## 🔍 Troubleshooting

### Bot Crash Terus

```bash
# Cek logs error
pm2 logs vzl2 --err
pm2 logs vzoelmenfess --err

# Restart dengan fresh start
pm2 delete all
pm2 start ~/ecosystem.config.js
```

### Memory Usage Tinggi

```bash
# Cek memory
pm2 list

# Restart bot yang memory tinggi
pm2 restart vzl2
pm2 restart vzoelmenfess
```

### Logs Terlalu Besar

```bash
# Clear semua logs
pm2 flush

# Install PM2 log rotate
pm2 install pm2-logrotate

# Configure log rotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

### Bot Tidak Auto-Restart

Cek `ecosystem.config.js`:
```javascript
autorestart: true,        // Harus true
max_restarts: 10,         // Max restart attempts
min_uptime: '10s',        // Min uptime sebelum dianggap stable
restart_delay: 4000,      # Delay antara restart (ms)
```

---

## 💡 Tips & Tricks

### 1. Watch Mode (Auto-Restart on File Change)

Edit `ecosystem.config.js`:
```javascript
watch: true,
watch_delay: 1000,
ignore_watch: ['node_modules', 'logs', '*.log'],
```

**⚠️ WARNING**: Jangan aktifkan watch di production!

### 2. Cron Restart (Restart Otomatis Tiap Hari)

```bash
# Restart tiap hari jam 3 pagi
pm2 start vzl2 --cron-restart="0 3 * * *"
```

### 3. Cluster Mode (Multiple Instances)

Hanya untuk bot yang support multi-instance:
```javascript
instances: 2,              // Jalankan 2 instance
exec_mode: 'cluster'       // Cluster mode
```

### 4. Max Memory Restart

Bot auto-restart kalau memory melebihi limit:
```javascript
max_memory_restart: '300M'  // VZL2
max_memory_restart: '200M'  // Vzoelmenfess
```

---

## 🆘 Emergency Commands

```bash
# Kill semua PM2 process
pm2 kill

# Hard restart (force kill + start)
pm2 delete all && pm2 start ~/ecosystem.config.js

# Reset PM2 saved config
rm -rf ~/.pm2

# Reinstall PM2
npm uninstall -g pm2 && npm install -g pm2
```

---

## 📈 Performance Monitoring

### Real-Time Dashboard

```bash
# PM2 monitoring
pm2 monit

# Web dashboard (install dulu)
pm2 install pm2-server-monit
```

### Export Metrics

```bash
# JSON format
pm2 jlist

# Pretty print
pm2 prettylist

# Dump to file
pm2 jlist > /data/data/com.termux/files/home/pm2_metrics.json
```

---

## 🔐 Best Practices

1. **Selalu save setelah start**
   ```bash
   pm2 start ~/ecosystem.config.js
   pm2 save
   ```

2. **Cek logs regularly**
   ```bash
   pm2 logs --lines 50
   ```

3. **Monitor memory usage**
   ```bash
   pm2 list
   ```

4. **Backup ecosystem config**
   ```bash
   cp ~/ecosystem.config.js ~/ecosystem.config.js.backup
   ```

5. **Use log rotation**
   ```bash
   pm2 install pm2-logrotate
   ```

---

## 📞 Support

- **PM2 Docs**: https://pm2.keymetrics.io/docs/
- **Bot Issues**: @VZLfxs
- **GitHub**: https://github.com/VanZoel112/vzl2

---

**🦊 Vzoel Fox's Lutpan - 2025**
*Keep your bots running 24/7!*
