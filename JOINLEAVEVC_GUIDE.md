# JoinLeaveVC Plugin - Voice Chat Clone Mode

Plugin canggih untuk otomatis bergabung/keluar dari voice chat menggunakan mode clone yang tidak terdeteksi.

## 🚀 Fitur Utama

### Clone Mode Features
- **Stealth Join**: Bergabung ke voice chat tanpa notifikasi
- **Silent Mode**: Otomatis muted saat bergabung (tidak ada suara)
- **Background Operation**: Berjalan di background tanpa mengganggu user
- **Auto Timer**: Otomatis keluar setelah waktu tertentu

### Auto Management
- **Group-Specific**: Pengaturan per group yang berbeda
- **Smart Detection**: Otomatis join saat voice chat dimulai
- **Auto Leave**: Keluar otomatis saat voice chat kosong
- **Session Recovery**: Mempertahankan koneksi saat restart

## 📋 Command List

### Basic Commands
```
.joinvc          - Join voice chat dalam mode clone
.leavevc         - Keluar dari voice chat
.vcstatus        - Tampilkan status lengkap voice chat
```

### Auto Management
```
.autovc on       - Aktifkan sistem auto voice chat
.autovc off      - Matikan sistem auto voice chat
.autovc delay 300 - Set auto leave delay (detik)

.autojoin on     - Aktifkan auto join untuk group ini
.autojoin off    - Matikan auto join untuk group ini
.autojoin        - Cek status auto join group
```

## 🛠️ Setup & Installation

### 1. Install Dependencies
```bash
pip install py-tgcalls -U
pkg install ffmpeg  # Untuk Termux
```

### 2. Restart Bot
```
.restart
```

### 3. Enable Auto VC
```
.autovc on
```

### 4. Enable untuk Group Tertentu
```
.autojoin on
```

## ⚙️ Pengaturan Lanjutan

### Auto Leave Timer
- Default: 300 detik (5 menit)
- Minimum: 60 detik
- Maximum: 3600 detik (1 jam)

```
.autovc delay 600  # 10 menit
```

### Mode Stealth
- **Selalu muted** saat join
- **Tidak ada notifikasi** ke member lain
- **Background mode** - tidak mengganggu aktivitas user
- **Clone session** - menggunakan session terpisah

## 🎯 Use Cases

### 1. Monitor Voice Chat
Bergabung secara diam-diam untuk memantau voice chat grup tanpa ketahuan.

### 2. Auto Presence
Otomatis hadir di voice chat grup penting untuk menunjukkan keaktifan.

### 3. Silent Recorder
Bergabung untuk recording atau monitoring (sesuai kebijakan grup).

### 4. Background Presence
Hadir di voice chat sambil melakukan aktivitas lain.

## 🔧 Troubleshooting

### PyTgCalls Error
```bash
pip uninstall py-tgcalls
pip install py-tgcalls==0.9.7
```

### FFmpeg Missing
```bash
# Termux
pkg install ffmpeg

# Ubuntu/Debian
apt install ffmpeg
```

### Connection Issues
1. Restart bot: `.restart`
2. Check status: `.vcstatus`
3. Disable/enable: `.autovc off` → `.autovc on`

## 📊 Status Monitoring

### Cek Status System
```
.vcstatus
```

Output:
- PyTgCalls status
- System enable/disable
- Active connections
- Auto join groups
- Current group status

### Database Files
- `database/joinleavevc_settings.json` - Pengaturan auto join
- Session otomatis tersimpan dan recovery

## 🛡️ Security & Privacy

### Clone Mode Safety
- Menggunakan session terpisah
- Tidak menggunakan akun utama
- Mode stealth (tidak terdeteksi)
- Auto muted untuk privacy

### Recommendations
- Gunakan hanya di grup yang diizinkan
- Respect privacy member lain
- Set auto leave timer yang wajar
- Monitor penggunaan secara berkala

## 🔄 Update & Maintenance

### Update Plugin
Plugin akan auto-update saat restart bot jika ada perubahan.

### Backup Settings
```bash
cp database/joinleavevc_settings.json backup/
```

### Reset Settings
```bash
rm database/joinleavevc_settings.json
.restart
```

---

**Created by Vzoel Fox's Assistant**
Version 4.0.0 - Advanced Auto Voice Chat System