#!/usr/bin/env python3
"""
🤖 VZL2 Auto-Deploy Bot Assistant
Bot yang handle deployment otomatis untuk user

User tinggal chat dengan bot:
1. /start - Mulai deployment
2. Kirim nomor HP
3. Kirim kode OTP
4. Bot auto-deploy ke VPS

Author: VanZoel112
Version: 1.0.0
"""

import os
import asyncio
import paramiko
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment
load_dotenv()

# Bot credentials (dari BotFather)
BOT_TOKEN = os.getenv("DEPLOY_BOT_TOKEN", "8235912270:AAFYAKRTXnw5nxEGn7HkYoRIahc0zQygqwI")
API_ID = int(os.getenv("API_ID", "29919905"))
API_HASH = os.getenv("API_HASH", "717957f0e3ae20a7db004d08b66bfd30")

# Deployment mode
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "user")  # "user" or "developer"

# VPS credentials
VPS_HOST = os.getenv("VPS_HOST")  # IP VPS
VPS_USER = os.getenv("VPS_USER", "ubuntu")
VPS_PORT = int(os.getenv("VPS_PORT", "22"))
VPS_PASSWORD = os.getenv("VPS_PASSWORD")  # atau gunakan SSH key

# Admin yang bisa pakai bot
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Deploy storage
DEPLOY_DIR = "deployments"
os.makedirs(DEPLOY_DIR, exist_ok=True)

# User state untuk conversation
user_states = {}

# Bot client
bot = TelegramClient('deploy_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


class DeployState:
    """State untuk tracking deployment progress"""
    IDLE = "idle"
    WAITING_PHONE = "waiting_phone"
    WAITING_CODE = "waiting_code"
    WAITING_2FA = "waiting_2fa"
    DEPLOYING = "deploying"
    COMPLETED = "completed"


async def is_admin(user_id):
    """Check if user is admin"""
    if not ADMIN_IDS:
        return True  # Jika tidak ada admin list, semua bisa pakai
    return user_id in ADMIN_IDS


async def create_session(phone, code, password=None):
    """Generate string session dari phone + code"""
    try:
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()

        # Send code request
        await client.send_code_request(phone)

        # Sign in
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            if password:
                await client.sign_in(password=password)
            else:
                await client.disconnect()
                return None, "2FA password required"

        # Get session string
        session_string = client.session.save()

        # Get user info
        me = await client.get_me()
        user_info = {
            'id': me.id,
            'first_name': me.first_name,
            'username': me.username,
            'phone': phone
        }

        await client.disconnect()
        return session_string, user_info

    except PhoneCodeInvalidError:
        return None, "Invalid OTP code"
    except Exception as e:
        return None, str(e)


async def deploy_to_vps(session_string, user_info, owner_id, deployment_mode="user"):
    """Deploy userbot ke VPS via SSH with plugin filtering"""
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to VPS
        if VPS_PASSWORD:
            ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASSWORD)
        else:
            # Gunakan SSH key
            key_path = os.path.expanduser("~/.ssh/id_rsa")
            ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, key_filename=key_path)

        # Generate deployment folder name
        username = user_info.get('username', f"user_{user_info['id']}")
        deploy_name = f"vzl2_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Plugin filtering for user mode
        plugin_filter_cmd = ""
        if deployment_mode == "user":
            # Allowed plugins for user deployment
            allowed_plugins = [
                "gcast.py", "blacklist.py", "lock.py", "tagall.py",
                "vc.py", "id.py", "ping.py", "alive.py", "limit.py",
                "help.py",  # Help command
                "emoji_template.py", "__init__.py"  # Required
            ]

            # Create command to remove blocked plugins
            plugin_filter_cmd = f"""
            cd {deploy_name}/plugins
            for plugin in *.py; do
                if [[ ! "$plugin" =~ ^({'|'.join(allowed_plugins)})$ ]]; then
                    rm -f "$plugin"
                    echo "Removed: $plugin"
                fi
            done
            cd ..
            """

        # Commands untuk deploy
        commands = [
            f"cd ~",
            f"git clone https://github.com/VanZoel112/vzl2.git {deploy_name}",
            f"cd {deploy_name}",
        ]

        # Add plugin filtering if user mode
        if plugin_filter_cmd:
            commands.append(plugin_filter_cmd)

        commands.extend([
            f"python3 -m venv venv",
            f"source venv/bin/activate && pip install -r requirements.txt",
            # Update .env dengan session
            f"""cat > .env << 'EOL'
API_ID={API_ID}
API_HASH={API_HASH}
STRING_SESSION={session_string}
VZOEL_OWNER_ID={owner_id}
VZOEL_PREFIX=.
PREMIUM_EMOJIS_ENABLED=true
DEPLOYMENT_MODE={deployment_mode}
EOL""",
            # Create info file
            f"""cat > deployment_info.txt << 'EOL'
Deployment Type: {deployment_mode.upper()}
Owner: {user_info.get('first_name', 'User')} (@{user_info.get('username', 'N/A')})
User ID: {owner_id}
Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Allowed Features ({deployment_mode} mode):
✅ .help - View all commands
✅ .gcast - Broadcast messages
✅ .addbl/.delbl - Blacklist management
✅ .lock/.unlock - User locking
✅ .tagall/.stoptagall - Tag all members
✅ .joinvc/.leavevc - Voice chat
✅ .id - Get user/chat ID
✅ .ping/.pink/.pong/.ponk - Ping variations
✅ .alive - Check bot status
✅ .limit - Check Telegram limits

Contact: @VZLfxs
EOL""",
            # Start dengan PM2
            f"pm2 start main.py --name {deploy_name} --interpreter python3",
            f"pm2 save"
        ])

        # Execute commands
        full_command = " && ".join(commands)
        stdin, stdout, stderr = ssh.exec_command(full_command, timeout=600)

        # Get output
        output = stdout.read().decode()
        error = stderr.read().decode()

        ssh.close()

        # Check for critical errors
        if error and any(err in error.lower() for err in ['fatal', 'cannot', 'failed', 'error:']):
            return False, f"Deployment error:\n{error[:500]}"

        return True, {
            'deploy_name': deploy_name,
            'output': output[:500],
            'vps_host': VPS_HOST,
            'deployment_mode': deployment_mode
        }

    except Exception as e:
        return False, str(e)


@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command"""
    user_id = event.sender_id

    if not await is_admin(user_id):
        await event.respond("❌ Unauthorized. Contact admin for access.")
        return

    user_states[user_id] = {
        'state': DeployState.IDLE,
        'data': {}
    }

    welcome = f"""🤖 **VZL2 Auto-Deploy Bot**

Halo! Saya akan membantu deploy userbot VZL2 ke VPS secara otomatis.

**📋 Yang Anda Butuhkan:**
✅ Nomor HP Telegram (dengan kode negara)
✅ Kode OTP dari Telegram
✅ Password 2FA (jika aktif)

**🎯 Fitur yang Tersedia:**
✅ `.help` - Lihat semua command
✅ `.gcast` - Broadcast pesan ke semua grup
✅ `.addbl` / `.delbl` - Blacklist grup
✅ `.lock` / `.unlock` - Lock/unlock user
✅ `.tagall` / `.stoptagall` - Tag semua member
✅ `.joinvc` / `.leavevc` - Join/leave voice chat
✅ `.id` - Get user/chat ID
✅ `.ping` / `.pink` / `.pong` / `.ponk` - Ping bot
✅ `.alive` - Cek status bot
✅ `.limit` - Cek Telegram limits

**🚀 Proses Deploy:**
1. Kirim nomor HP Anda
2. Terima kode OTP di Telegram
3. Kirim kode OTP ke bot
4. Bot auto-deploy ke VPS
5. Selesai! Userbot langsung jalan

**💡 Keuntungan:**
• Tidak perlu akses SSH
• Tidak perlu setup manual
• Deploy dalam 2-3 menit
• Auto-start dengan PM2
• Limited features (aman untuk pemula)

**📝 Mode:** USER (Limited Features)
Klik tombol di bawah untuk mulai!"""

    buttons = [
        [Button.inline("🚀 Mulai Deploy", b"start_deploy")],
        [Button.inline("❓ Help", b"help"), Button.inline("📊 Status", b"status")]
    ]

    await event.respond(welcome, buttons=buttons)


@bot.on(events.CallbackQuery(pattern=b"start_deploy"))
async def start_deploy_callback(event):
    """Handle start deploy button"""
    user_id = event.sender_id

    user_states[user_id] = {
        'state': DeployState.WAITING_PHONE,
        'data': {}
    }

    await event.edit("""📱 **STEP 1: Nomor HP**

Kirim nomor HP Telegram Anda dengan format:
`+628123456789`

**⚠️ Penting:**
• Gunakan kode negara (+62 untuk Indonesia)
• Nomor harus aktif di Telegram
• Jangan pakai spasi atau tanda hubung

**Contoh:**
✅ +628123456789
✅ +6281234567890
❌ 08123456789 (tanpa +62)
❌ +62 812 345 6789 (ada spasi)

Kirim nomor HP Anda sekarang:""")

    await event.answer()


@bot.on(events.NewMessage)
async def message_handler(event):
    """Handle user messages based on state"""
    user_id = event.sender_id

    # Ignore if no state or not admin
    if user_id not in user_states or not await is_admin(user_id):
        return

    # Ignore commands
    if event.message.text.startswith('/'):
        return

    state_data = user_states[user_id]
    current_state = state_data['state']
    message = event.message.text.strip()

    # State: Waiting for phone number
    if current_state == DeployState.WAITING_PHONE:
        # Validate phone format
        if not message.startswith('+'):
            await event.respond("❌ Format salah! Nomor harus diawali dengan + dan kode negara.\n\nContoh: `+628123456789`")
            return

        # Save phone and generate session client
        state_data['data']['phone'] = message

        # Send code request
        try:
            temp_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await temp_client.connect()
            await temp_client.send_code_request(message)
            await temp_client.disconnect()

            # Update state
            state_data['state'] = DeployState.WAITING_CODE

            await event.respond(f"""✅ **Kode OTP Terkirim!**

📱 Nomor: `{message}`
📨 Kode OTP telah dikirim ke Telegram Anda

**📝 STEP 2: Kode OTP**

Cek aplikasi Telegram Anda dan kirimkan kode 5 digit yang Anda terima.

**Contoh:**
`12345`

Kirim kode OTP sekarang:""")

        except Exception as e:
            await event.respond(f"❌ Error mengirim kode:\n`{str(e)}`\n\nCoba lagi dengan /start")
            user_states[user_id]['state'] = DeployState.IDLE

    # State: Waiting for OTP code
    elif current_state == DeployState.WAITING_CODE:
        phone = state_data['data']['phone']

        # Processing message
        processing = await event.respond("""⚙️ **Memproses OTP...**

🔐 Verifying code
🔗 Connecting to Telegram
📦 Generating session

Please wait...""")

        # Try to create session
        session_string, result = await create_session(phone, message)

        if session_string:
            # Success! Save session
            state_data['data']['session'] = session_string
            state_data['data']['user_info'] = result
            state_data['state'] = DeployState.DEPLOYING

            await processing.edit(f"""✅ **Session Generated!**

👤 Nama: {result['first_name']}
🆔 User ID: `{result['id']}`
📱 Username: @{result.get('username', 'N/A')}

**🚀 STEP 3: Deploy ke VPS**

Bot sedang deploy userbot Anda ke VPS...

⏳ Proses ini memakan waktu 2-3 menit
📦 Cloning repository
📥 Installing dependencies
🔧 Configuring environment
🚀 Starting with PM2

Please wait...""")

            # Deploy to VPS
            success, deploy_result = await deploy_to_vps(
                session_string,
                result,
                result['id']  # Set owner_id = user_id
            )

            if success:
                state_data['state'] = DeployState.COMPLETED

                # Save deployment info
                deploy_info = {
                    'user_id': user_id,
                    'deploy_name': deploy_result['deploy_name'],
                    'timestamp': datetime.now().isoformat(),
                    'user_info': result,
                    'vps_host': deploy_result['vps_host']
                }

                with open(f"{DEPLOY_DIR}/{user_id}_{result['id']}.json", 'w') as f:
                    json.dump(deploy_info, f, indent=2)

                await processing.edit(f"""🎉 **DEPLOY BERHASIL!**

✅ Userbot berhasil di-deploy ke VPS
🚀 Bot sudah otomatis berjalan

**📊 Deployment Info:**
🏷️ Name: `{deploy_result['deploy_name']}`
🖥️ VPS: `{deploy_result['vps_host']}`
👤 Owner: {result['first_name']} (`{result['id']}`)
📝 Mode: **USER** (Limited Features)

**🎮 Cara Menggunakan:**
1. Buka Telegram Anda
2. Kirim pesan `.alive` di Saved Messages
3. Bot akan merespon jika aktif

**🎯 Available Commands:**
• `.help` - Lihat semua command & plugin info
• `.gcast <text>` - Broadcast ke semua grup
• `.addbl` / `.delbl` - Manage blacklist
• `.lock <user_id>` / `.unlock <user_id>` - Lock user
• `.tagall` / `.stoptagall` - Tag semua member
• `.joinvc` / `.leavevc` - Voice chat control
• `.id` - Get user/chat ID
• `.ping` / `.pink` / `.pong` / `.ponk` - Check latency
• `.alive` - Check bot status
• `.limit` - Check Telegram limits

**📝 Notes:**
• Bot berjalan 24/7 di VPS
• Auto-restart jika crash
• Limited features untuk keamanan
• Gunakan dengan bijak

**💬 Butuh bantuan?**
Contact: @VZLfxs

Terima kasih telah menggunakan VZL2 Auto-Deploy! 🦊""")

            else:
                await processing.edit(f"""❌ **Deploy Gagal**

Error: `{deploy_result}`

Silakan hubungi admin atau coba lagi dengan /start""")
                state_data['state'] = DeployState.IDLE

        elif result == "2FA password required":
            state_data['state'] = DeployState.WAITING_2FA
            await processing.edit("""🔒 **2FA Detected**

Akun Anda menggunakan Two-Factor Authentication.

Kirim password 2FA Anda sekarang:

⚠️ **Privacy:** Password akan langsung dihapus setelah digunakan.""")

        else:
            await processing.edit(f"""❌ **OTP Tidak Valid**

Error: `{result}`

Coba lagi dengan /start atau hubungi admin.""")
            state_data['state'] = DeployState.IDLE

    # State: Waiting for 2FA password
    elif current_state == DeployState.WAITING_2FA:
        phone = state_data['data']['phone']
        code = message  # Assuming code was saved previously

        # Processing
        processing = await event.respond("⚙️ Processing with 2FA password...")

        # Try to create session with 2FA
        session_string, result = await create_session(phone, code, message)

        if session_string:
            # Continue with deployment (same as WAITING_CODE success)
            state_data['data']['session'] = session_string
            state_data['data']['user_info'] = result
            state_data['state'] = DeployState.DEPLOYING

            await processing.edit("✅ 2FA verified! Deploying...")

            # Deploy to VPS (sama seperti di atas)
            success, deploy_result = await deploy_to_vps(session_string, result, result['id'])

            if success:
                # ... (sama seperti success message di atas)
                await processing.edit(f"🎉 Deploy berhasil!\n\nName: {deploy_result['deploy_name']}")
            else:
                await processing.edit(f"❌ Deploy gagal: {deploy_result}")

        else:
            await processing.edit(f"❌ 2FA password salah: {result}")
            state_data['state'] = DeployState.IDLE


@bot.on(events.CallbackQuery(pattern=b"status"))
async def status_callback(event):
    """Show deployment status"""
    user_id = event.sender_id

    # Find user deployments
    deploy_files = [f for f in os.listdir(DEPLOY_DIR) if f.startswith(str(user_id))]

    if not deploy_files:
        await event.answer("❌ Belum ada deployment", alert=True)
        return

    status_text = "📊 **Your Deployments**\n\n"

    for file in deploy_files:
        with open(f"{DEPLOY_DIR}/{file}", 'r') as f:
            data = json.load(f)

        status_text += f"""🏷️ {data['deploy_name']}
🖥️ VPS: {data['vps_host']}
📅 Deployed: {data['timestamp'][:10]}

"""

    await event.answer(status_text, alert=True)


@bot.on(events.CallbackQuery(pattern=b"help"))
async def help_callback(event):
    """Show help"""
    help_text = """❓ **VZL2 Auto-Deploy Help**

**📋 Requirements:**
• Nomor HP Telegram aktif
• Kode OTP dari Telegram
• Password 2FA (jika aktif)

**🔧 Process:**
1. /start - Mulai deployment
2. Kirim nomor HP
3. Kirim kode OTP
4. Bot auto-deploy

**💡 Tips:**
• Pastikan nomor HP benar
• Kode OTP berlaku 5 menit
• Jangan share session string

**📞 Support:**
@VZLfxs"""

    await event.answer(help_text, alert=True)


async def main():
    """Main function"""
    print("🤖 VZL2 Auto-Deploy Bot Started!")
    print(f"📡 Bot ready to deploy userbot to VPS: {VPS_HOST}")

    if not VPS_HOST:
        print("⚠️ WARNING: VPS_HOST not configured in .env")

    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
