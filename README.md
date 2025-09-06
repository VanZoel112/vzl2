# 🦊 VzoelFox's Assistant v2

**Enhanced userbot with premium emoji support**

Created by **Vzoel Fox's** • Enhanced by **Vzoel Fox's Ltpn**

---

## ✨ Features

🤩 **Premium Emoji Collection**
- 12 exclusive VzoelFox premium emojis
- Smart emoji mapping system  
- Category-based organization
- Quick access patterns

⛈ **Advanced Integration**
- Modern async/await syntax
- Optimized performance
- Robust error handling
- Session management

🎚 **VzoelFox Signature Commands**
- `.ping` - Speed test with emojis
- `.alive` - Status with signature
- `.vzoel` - Special VzoelFox mode
- `.emojis` - List all premium emojis

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/VanZoel112/vzl2.git
cd vzl2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file:
```env
API_ID=your_api_id
API_HASH=your_api_hash
VZOEL_PREFIX=.
PREMIUM_EMOJIS_ENABLED=true
```

### 4. Run Userbot
```bash
python main.py
```

---

## 🤖 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.ping` | 🤩 Check bot response time | `.ping` |
| `.alive` | ⛈ Show bot status | `.alive` |
| `.vzoel` | 😈 VzoelFox special mode | `.vzoel` |
| `.emo <name>` | 🎚 Get emoji info | `.emo utama` |
| `.emojis` | 📱 List all emojis | `.emojis` |
| `.help` | 🤪 Show help menu | `.help` |

---

## 🎭 Premium Emoji Collection

### Primary Emojis
- 🤩 `utama` - VzoelFox main emoji
- 👍 `centang` - Approval emoji
- ⛈ `petir` - Power emoji

### System Emojis  
- ⚙️ `loading` - Processing indicator
- 👽 `proses` - Special operations
- 🎚 `aktif` - Active status

### Fun Emojis
- 🍿 `kuning` - Entertainment
- 🤪 `merah` - Playful mode
- 🎅 `biru` - Special events

### Special Emojis
- 😈 `adder1` - Mischief mode
- 💟 `adder2` - Premium features
- ✉️ `telegram` - Messages

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | Yes | API ID |
| `API_HASH` | Yes | API Hash |
| `VZOEL_PREFIX` | No | Command prefix (default: `.`) |
| `PREMIUM_EMOJIS_ENABLED` | No | Enable emoji features |
| `VZOEL_OWNER_ID` | No | Bot owner user ID |

### Emoji Mapping

The assistant uses `emoji_mapping.json` for premium emoji management:
- Custom emoji IDs for premium features
- Category-based organization
- Usage patterns for smart responses
- Quick access combinations

---

## 🔧 Development

### Project Structure
```
vzl2/
├── main.py              # Main assistant application
├── config.py            # Configuration management
├── emoji_handler.py     # Premium emoji handler
├── emoji_mapping.json   # Emoji definitions
├── requirements.txt     # Dependencies
└── README.md           # This file
```

### Adding New Features
1. Create new command handlers in `main.py`
2. Use `vzoel_emoji.get_emoji()` for emoji integration
3. Follow VzoelFox naming conventions
4. Test with premium emoji responses

---

## 🛡️ Security

- Never share your API credentials
- Use environment variables for sensitive data
- Enable 2FA on your account
- Monitor assistant activity regularly

---

## 📄 License

This project is licensed under the MIT License.

**© 2025 Vzoel Fox's - All Rights Reserved**

Enhanced by **Vzoel Fox's Ltpn**

---

## 🤝 Support

- **Creator:** Vzoel Fox's
- **Version:** v2.0.0-vzoel
- **Telegram:** [@YourTelegramHandle]

**Made with 🦊 by VzoelFox Team**