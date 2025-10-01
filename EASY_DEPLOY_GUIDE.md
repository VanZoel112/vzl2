# 🚀 VZL2 Easy Deploy - Panduan Lengkap

## ✨ Deploy Tanpa Ribet!

Tidak perlu bikin API_ID/API_HASH di my.telegram.org!
Cukup nomor HP dan kode OTP, userbot langsung jalan.

---

## 📋 Persyaratan

- ✅ Python 3.8+ terinstall
- ✅ Nomor HP Telegram aktif
- ✅ Akses ke Telegram untuk terima kode OTP
- ✅ Password 2FA (jika aktif di akun Telegram)

---

## 🎯 Cara Deploy (Super Mudah!)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/VanZoel112/vzl2.git
cd vzl2
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Jalankan Easy Deploy

```bash
python easy_deploy.py
```

### 4️⃣ Ikuti Instruksi di Layar

```
📱 Masukkan Nomor HP:
   Format: +628123456789 (dengan kode negara +)
   Nomor HP: +628123456789

📨 Mengirim kode OTP ke +628123456789...

🔢 Masukkan Kode OTP:
   Cek Telegram Anda untuk kode verifikasi
   Kode OTP: 12345
```

### 5️⃣ Jika Ada 2FA (Two-Factor Authentication)

```
🔒 2FA terdeteksi!
   Password 2FA: [masukkan password Anda]
```

### 6️⃣ Selesai! 🎉

```
✅ LOGIN BERHASIL!
==================================================
👤 Nama: Vzoel Fox
🆔 User ID: 123456789
📱 Username: @VZLfxs
==================================================

💾 Menyimpan session ke .env...
✅ File .env berhasil diupdate!

🎉 DEPLOY SELESAI!
==================================================

🚀 Cara menjalankan userbot:
   python main.py
   atau
   ./start.sh

✅ Userbot siap digunakan!
```

---

## 🔧 Menjalankan Userbot

Setelah deploy selesai, jalankan userbot dengan:

```bash
# Cara 1: Langsung dengan Python
python main.py

# Cara 2: Dengan start script
./start.sh

# Cara 3: Dengan PM2 (untuk production)
pm2 start ecosystem.config.js
```

---

## 🛠️ Troubleshooting

### ❌ Error: Nomor HP tidak valid
**Solusi:** Pastikan format nomor dengan kode negara (+62 untuk Indonesia)

### ❌ Error: Kode OTP salah
**Solusi:** Cek lagi kode di Telegram, jangan sampai typo

### ❌ Error: Terlalu banyak percobaan
**Solusi:** Tunggu beberapa menit, Telegram membatasi percobaan login

### ❌ Error: 2FA password salah
**Solusi:** Cek password 2FA di Settings → Privacy and Security → Two-Step Verification

---

## 🔐 Keamanan

### API Credentials
Script ini menggunakan API_ID dan API_HASH default dari VZL2 config:
- **API_ID:** 29919905
- **API_HASH:** 717957f0e3ae20a7db004d08b66bfd30

Ini aman digunakan karena:
- ✅ API credentials hanya untuk autentikasi awal
- ✅ Session string yang dihasilkan unique per user
- ✅ Tidak ada data user yang tersimpan di server

### String Session
- String session disimpan di file `.env` lokal
- **JANGAN SHARE** string session ke orang lain
- Session = akses penuh ke akun Telegram Anda

---

## 📱 Untuk Pengguna Baru

### Apa itu Userbot?
Userbot adalah bot Telegram yang berjalan dengan akun user biasa (bukan bot account). Bisa melakukan semua yang user bisa lakukan, termasuk:
- ✅ Join voice chat & streaming musik
- ✅ Kirim pesan otomatis
- ✅ Download media
- ✅ Auto-reply
- ✅ Dan banyak lagi!

### Bedanya dengan Bot Biasa?
| Fitur | Bot Biasa | Userbot |
|-------|-----------|---------|
| Akun | @BotFather | Nomor HP |
| Voice Chat | ❌ Tidak bisa | ✅ Bisa |
| Privacy Mode | ❌ Dibatasi | ✅ Penuh |
| Command | `/start` | `.help` |

---

## 🎯 Fitur VZL2 Userbot

Setelah deploy, Anda bisa gunakan:

### 🎵 Musik & Voice Chat
- `.play <judul>` - Play musik dari YouTube
- `.jvc` - Join voice chat
- `.lvc` - Leave voice chat
- `.pause` / `.resume` / `.stop`

### 💬 Messaging
- `.gcast <pesan>` - Broadcast ke semua grup
- `.tagall` - Tag semua member
- `.lock <user_id>` - Lock user (auto-delete)

### 🛠️ Tools
- `.ping` - Cek ping
- `.help` - List semua command
- `.restart` - Restart userbot

---

## 📞 Support

- 📧 GitHub Issues: [vzl2/issues](https://github.com/VanZoel112/vzl2/issues)
- 💬 Telegram: [@VZLfxs](https://t.me/VZLfxs)
- 📖 Documentation: [README.md](README.md)

---

## ⚠️ Disclaimer

- Gunakan dengan bijak dan ikuti TOS Telegram
- Jangan spam atau abuse fitur
- Creator tidak bertanggung jawab atas penyalahgunaan
- Userbot dapat di-ban jika melanggar aturan Telegram

---

## 📝 License

MIT License - Free to use and modify

---

**🦊 VZL2 Userbot - by VanZoel112**
*Deploy sekali, jalan selamanya!*
