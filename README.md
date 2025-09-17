# 🦊 VzoelFox's Assistant v2

**Advanced Telegram Userbot with Premium Emoji Support**

Created by: **Vzoel Fox's**  
Enhanced by: **Vzoel Fox's Ltpn**

---

## 🚀 Quick Start (Recommended)

Cara termudah untuk memulai:

```bash
python start.py
```

Script ini akan:
- ✅ Mengecek apakah session sudah ada
- 🔧 Otomatis menjalankan setup jika belum ada session
- 🚀 Langsung menjalankan bot jika session sudah ada

---

## 🔧 Session Recovery System

### Automatic Session Recovery
VzoelFox's Assistant v2 dilengkapi dengan sistem recovery otomatis untuk session yang kadaluwarsa:

**Features:**
- ✅ **Auto-detection** session kadaluwarsa
- ✅ **Auto-backup** session lama sebelum recovery  
- ✅ **Auto-cleanup** file session yang expired
- ✅ **Interactive recovery** dengan guided setup
- ✅ **Session validation** otomatis saat startup

### Quick Recovery Commands

**1. One-click Recovery:**
```bash
python quick_recovery.py
```
Script all-in-one untuk recovery session dengan test otomatis.

**2. Manual Recovery:**
```bash
python session_recovery.py
```
Recovery interaktif dengan control penuh.

**3. In-Bot Commands:**
```
.session          # Status session lengkap
.sessioncheck     # Check validitas session
.sessionbackup    # Backup session manual  
.sessionrecovery  # Guide recovery lengkap
```

### When Recovery is Needed

Recovery diperlukan ketika muncul error:
- 🚨 `SessionRevokedError` - Session dibatalkan Telegram
- 🚨 `AUTH_KEY_UNREGISTERED` - Key tidak terdaftar
- 🚨 `AUTH_KEY_DUPLICATED` - Parallel session terdeteksi
- 🚨 `UnauthorizedError` - Session tidak valid

### Recovery Process

1. **Backup Otomatis**: Session lama di-backup ke `session_backups/`
2. **Cleanup**: File session expired dihapus otomatis
3. **Interactive Setup**: Guided setup session baru
4. **Auto-Update**: File `.env` diupdate otomatis
5. **Validation**: Test session baru sebelum selesai

---

## 📱 Manual Setup

### 1️⃣ Generate Session

Jika ingin setup manual:

```bash
python main.py --generate-session
```

Script akan meminta:
- **API ID** dan **API Hash** (dari https://my.telegram.org/apps)
- **Nomor telepon** (dengan kode negara, contoh: +628123456789)
- **Kode verifikasi** (yang dikirim ke Telegram)
- **Password 2FA** (jika diaktifkan)

### 2️⃣ Jalankan Bot

Setelah session dibuat:

```bash
python main.py
```

Atau gunakan:

```bash
python start.py
```

---

## 🔧 Konfigurasi

### File `.env`

Bot akan membuat file `.env` secara otomatis, tapi Anda bisa edit manual:

```env
# API Configuration (Required)
API_ID=your_api_id
API_HASH=your_api_hash

# Session (Auto-generated)
STRING_SESSION=your_generated_session_string

# Optional Settings
VZOEL_PREFIX=.
VZOEL_OWNER_ID=your_telegram_user_id
VZOEL_LOG_CHAT=your_log_chat_id

# Premium Features
PREMIUM_EMOJIS_ENABLED=true
EMOJI_MAPPING_FILE=emoji_mapping.json

# Advanced Settings
WORKERS=4
LOAD_UNOFFICIAL_PLUGINS=false

# Database
DATABASE_URL=sqlite:///vzl2.db
```

---

## 🤖 Commands

### Basic Commands

- `.ping` - Cek kecepatan bot
- `.alive` - Status bot
- `.vzoel` - Special VzoelFox command
- `.help` - Bantuan

### Emoji Commands

- `.emo <name>` - Info emoji spesifik
- `.emojis` - List semua emoji
- `.emoprev` - Preview emoji

### Plugin System

Bot secara otomatis memuat plugin dari folder `plugins/`:

```
vzl2/
├── plugins/
│   ├── ping.py
│   ├── alive.py
│   └── your_custom_plugin.py
└── main.py
```

---

## 🔐 Keamanan

### ⚠️ PENTING:

1. **Jangan share `STRING_SESSION`** dengan siapapun
2. **Backup file `.env`** secara aman
3. **Jangan commit `.env`** ke repository public
4. **String session = password akun Anda**

### Session Management:

- Session tersimpan di `.env` sebagai `STRING_SESSION`
- Jika session rusak, generate ulang dengan `python main.py --generate-session`
- Bot juga mendukung file session (`.session`) sebagai backup

---

## 🎭 Premium Emoji Features

VzoelFox's Assistant v2 mendukung:

- ✨ Custom Premium Emoji dari Telegram
- 🎨 Emoji mapping system
- 🦊 VzoelFox signature emojis
- 📱 Dynamic emoji responses

### Emoji Categories:

- **Main**: Emoji utama VzoelFox
- **Status**: Status indicators
- **Actions**: Action emojis
- **UI**: Interface emojis

---

## 📁 Project Structure

```
vzl2/
├── start.py              # Easy launcher (recommended)
├── main.py               # Main bot file
├── client.py             # Advanced client with plugins
├── generate_session.py   # Standalone session generator
├── config.py             # Configuration management
├── emoji_handler.py      # Premium emoji system
├── .env                  # Environment config (auto-generated)
├── plugins/              # Plugin directory
└── README.md             # This file
```

---

## 🔄 Update System

Bot memiliki auto-update system:

```bash
# Manual update
git pull origin main

# Auto-update akan memberitahu di log
# Gunakan command .update (jika tersedia di plugin)
```

---

## 🛠️ Troubleshooting

### Session Error:

```bash
# Regenerate session
python main.py --generate-session

# Atau hapus session lama
rm vzl2_session.session
rm .env
python start.py
```

### API Errors:

1. Pastikan API_ID dan API_HASH benar
2. Cek https://my.telegram.org/apps
3. API_ID harus angka, bukan string

### Plugin Errors:

1. Cek folder `plugins/` ada
2. Plugin harus format Python valid
3. Restart bot setelah update plugin

---

## 📞 Support

- **Repository**: https://github.com/VanZoel112/vzl2
- **Creator**: Vzoel Fox's
- **Enhanced by**: Vzoel Fox's Ltpn

---

## 📜 License

This project is created for educational and personal use.

**© 2024 Vzoel Fox's - VzoelFox's Assistant v2**

---

*Selamat menggunakan VzoelFox's Assistant v2! 🦊*