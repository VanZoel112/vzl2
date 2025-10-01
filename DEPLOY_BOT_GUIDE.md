# 🤖 VZL2 Auto-Deploy Bot - Panduan Lengkap

## ✨ Konsep

Bot Assistant Telegram yang membantu user deploy VZL2 userbot ke VPS **tanpa perlu akses SSH atau technical knowledge**.

### 🎯 Alur Kerja:

```
User → Chat Bot → Kasih HP → Kasih OTP → Bot Deploy ke VPS → Done!
```

**User hanya perlu:**
1. Nomor HP Telegram
2. Kode OTP
3. Password 2FA (jika ada)

**Bot yang handle:**
- Generate session string
- Clone repository ke VPS
- Install dependencies
- Setup environment
- Start dengan PM2
- Monitoring

---

## 🚀 Setup Deploy Bot

### **1. Buat Bot di BotFather**

```
1. Buka Telegram, cari @BotFather
2. Ketik /newbot
3. Kasih nama bot: "VZL2 Deploy Assistant"
4. Kasih username: "vzl2_deploy_bot" (atau yang lain)
5. Copy token yang diberikan
```

**Contoh Token:**
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
```

### **2. Setup Environment**

```bash
# Copy example config
cp .env.deploy_bot.example .env.deploy_bot

# Edit config
nano .env.deploy_bot
```

**Isi dengan:**
```env
DEPLOY_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
VPS_HOST=13.215.215.63
VPS_USER=ubuntu
VPS_PASSWORD=your_password  # atau kosongkan jika pakai SSH key
ADMIN_IDS=8024282347  # User ID Anda
```

### **3. Install Dependencies**

```bash
pip install paramiko python-dotenv
```

### **4. Jalankan Deploy Bot**

```bash
python deploy_bot.py
```

**Output:**
```
🤖 VZL2 Auto-Deploy Bot Started!
📡 Bot ready to deploy userbot to VPS: 13.215.215.63
```

---

## 👥 Cara User Menggunakan Bot

### **Step 1: Start Chat**

User cari bot di Telegram: `@vzl2_deploy_bot`

Ketik: `/start`

**Bot Response:**
```
🤖 VZL2 Auto-Deploy Bot

Halo! Saya akan membantu deploy userbot VZL2 ke VPS.

Yang Anda Butuhkan:
✅ Nomor HP Telegram
✅ Kode OTP dari Telegram
✅ Password 2FA (jika aktif)

[🚀 Mulai Deploy] [❓ Help] [📊 Status]
```

### **Step 2: Klik "Mulai Deploy"**

**Bot Response:**
```
📱 STEP 1: Nomor HP

Kirim nomor HP Telegram Anda:
Contoh: +628123456789
```

**User kirim:**
```
+628123456789
```

### **Step 3: Terima Kode OTP**

**Bot Response:**
```
✅ Kode OTP Terkirim!

📱 Nomor: +628123456789
📨 Kode OTP telah dikirim ke Telegram Anda

Kirim kode OTP sekarang:
```

**User cek Telegram, dapat kode 12345, kirim:**
```
12345
```

### **Step 4: Auto Deploy**

**Bot Response:**
```
⚙️ Memproses OTP...

🔐 Verifying code
🔗 Connecting to Telegram
📦 Generating session

✅ Session Generated!

👤 Nama: Vzoel Fox
🆔 User ID: 123456789

🚀 STEP 3: Deploy ke VPS

Bot sedang deploy userbot Anda...

⏳ Proses 2-3 menit
📦 Cloning repository
📥 Installing dependencies
🔧 Configuring environment
🚀 Starting with PM2
```

### **Step 5: Done!**

**Bot Response:**
```
🎉 DEPLOY BERHASIL!

✅ Userbot berhasil di-deploy
🚀 Bot sudah otomatis berjalan

📊 Deployment Info:
🏷️ Name: vzl2_username_20250102
🖥️ VPS: 13.215.215.63
👤 Owner: Vzoel Fox (123456789)

🎮 Cara Menggunakan:
1. Buka Telegram
2. Kirim .alive di Saved Messages
3. Bot akan merespon

Terima kasih! 🦊
```

---

## 🔧 Advanced Configuration

### **SSH Key (Tanpa Password)**

Jika VPS pakai SSH key authentication:

```bash
# Generate SSH key di server bot
ssh-keygen -t rsa -b 4096

# Copy public key ke VPS
ssh-copy-id ubuntu@13.215.215.63

# Update .env.deploy_bot
VPS_PASSWORD=  # Kosongkan
```

Bot akan otomatis pakai `~/.ssh/id_rsa`

### **Multiple VPS Support**

Bisa deploy ke multiple VPS dengan load balancing:

```env
VPS_HOSTS=13.215.215.63,54.169.123.45,18.142.200.100
```

Bot akan pilih VPS dengan load terendah.

### **Custom Deploy Location**

```env
DEPLOY_BASE_DIR=/home/userbots
```

Semua userbot akan di-deploy ke `/home/userbots/vzl2_username_xxx`

---

## 📊 Monitoring & Management

### **Check Active Deployments**

```bash
# Di VPS
pm2 list

# Output:
# vzl2_user1_20250102  │ online
# vzl2_user2_20250102  │ online
# vzl2_user3_20250103  │ online
```

### **View Logs**

```bash
pm2 logs vzl2_user1_20250102
```

### **Stop/Restart User**

```bash
pm2 restart vzl2_user1_20250102
pm2 stop vzl2_user1_20250102
pm2 delete vzl2_user1_20250102
```

### **Deployment Database**

Bot menyimpan info deployment di `deployments/`:

```json
{
  "user_id": 123456789,
  "deploy_name": "vzl2_username_20250102",
  "timestamp": "2025-01-02T14:30:00",
  "user_info": {
    "id": 123456789,
    "first_name": "Vzoel Fox",
    "username": "VZLfxs",
    "phone": "+628123456789"
  },
  "vps_host": "13.215.215.63"
}
```

---

## 🔒 Security Best Practices

### **1. Limit Admin Access**

```env
ADMIN_IDS=123456789  # Hanya user ID ini yang bisa deploy
```

### **2. Session String Protection**

Bot **TIDAK** menyimpan session string di file. Session langsung dikirim ke VPS via SSH dan disimpan di `.env` VPS.

### **3. SSH Key Rotation**

Rotate SSH keys secara berkala:

```bash
# Generate new key
ssh-keygen -t ed25519 -f ~/.ssh/vzl2_deploy_new

# Update VPS
ssh-copy-id -i ~/.ssh/vzl2_deploy_new.pub ubuntu@vps

# Update bot config
SSH_KEY_PATH=~/.ssh/vzl2_deploy_new
```

### **4. VPS Firewall**

```bash
# Allow hanya SSH dari IP bot
sudo ufw allow from BOT_IP to any port 22
```

---

## ⚠️ Troubleshooting

### **Error: Bot Token Invalid**

```
telegram.error.InvalidToken: Invalid token
```

**Fix:** Cek token dari @BotFather, pastikan tidak ada spasi.

### **Error: SSH Connection Failed**

```
paramiko.ssh_exception.AuthenticationException
```

**Fix:**
1. Cek VPS_HOST, VPS_USER, VPS_PASSWORD
2. Test manual: `ssh ubuntu@13.215.215.63`
3. Pastikan VPS accept password auth atau SSH key sudah ter-copy

### **Error: Deploy Timeout**

```
Deployment timeout after 300 seconds
```

**Fix:**
1. Increase timeout: `DEPLOY_TIMEOUT=600`
2. Cek VPS resources (RAM/CPU)
3. Cek internet connection VPS

### **Error: PM2 Not Found**

```
pm2: command not found
```

**Fix:**
Install PM2 di VPS:
```bash
npm install -g pm2
```

---

## 📈 Scaling Tips

### **1. Resource Monitoring**

```bash
# Check VPS usage
htop

# Check userbot count
pm2 list | grep vzl2 | wc -l
```

### **2. Auto-Cleanup**

Hapus inactive deployments:

```bash
# Cron job untuk cleanup
0 0 * * * /path/to/cleanup_inactive.sh
```

### **3. Load Balancing**

Deploy ke multiple VPS berdasarkan load:

```python
# Di deploy_bot.py
def get_least_loaded_vps():
    # Check PM2 process count di each VPS
    # Return VPS dengan load terendah
    pass
```

---

## 🆘 Support

- **Bot Issues:** @VZLfxs
- **GitHub Issues:** https://github.com/VanZoel112/vzl2/issues
- **Documentation:** README.md

---

**🦊 VZL2 Auto-Deploy Bot - by VanZoel112**
*Deploy once, run forever!*
