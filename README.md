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

🎚 **VzoelFox Enhanced Features**
- **Plugin System** - Dynamic plugin loading from `plugins/` directory
- **Auto-Update** - Manual update system with `.update` and `.update force`
- **Advanced Client** - Enhanced client with statistics and management
- **Premium Emojis** - 12 exclusive VzoelFox emojis integrated throughout
- **Gcast System** - Advanced broadcast with blacklist management and animations
- **Blacklist Management** - Automatic config.py integration for persistent storage

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

### 3. Generate Session String (First Time)
```bash
python main.py --generate-session
```
Follow the prompts:
- Enter phone number with country code
- Enter verification code
- Enter 2FA password (if enabled)
- Session will be automatically saved to `.env`

### 4. Run Assistant
```bash
python main.py
```

---

## 🚀 Usage

### Session Generation
```bash
# Generate new session (first time setup)
python main.py --generate-session

# Start assistant
python main.py

# Show help
python main.py --help
```

### 🤩 Features:
- **Automatic API validation** - Checks credentials before proceeding
- **Smart session management** - Automatically saves to `.env` file
- **VzoelFox premium emojis** - Enhanced visual feedback
- **Error handling** - Guides you through common issues

---

## 🤖 Commands

### 🤩 Core Commands
| Command | Description | Example |
|---------|-------------|---------|
| `.vzoel` | VzoelFox special domain mode | `.vzoel` |
| `.help` | Show help menu | `.help` |

### 🦊 Alive Commands (Plugin)
| Command | Description | Example |
|---------|-------------|---------|
| `.alive` | 12-phase animated alive display | `.alive` |
| `.ainfo` | Show alive system information | `.ainfo` |

### 🎚 System Commands  
| Command | Description | Example |
|---------|-------------|---------|
| `.update` | Check and install updates | `.update` |
| `.update force` | Force update (manual) | `.update force` |
| `.stats` | Show assistant statistics | `.stats` |
| `.plugins` | List loaded plugins | `.plugins` |
| `.restart` | Restart the assistant | `.restart` |

### 💟 Emoji Commands
| Command | Description | Example |
|---------|-------------|---------|
| `.emo <name>` | Get emoji information | `.emo utama` |
| `.emojis` | List all premium emojis | `.emojis` |

### 🦊 Fun Commands (Plugin)
| Command | Description | Example |
|---------|-------------|---------|
| `.dice` | Roll a dice | `.dice` |
| `.flip` | Flip a coin | `.flip` |
| `.quote` | Random VzoelFox quote | `.quote` |

### ⚙️ Ping Commands (Plugin)
| Command | Description | Example |
|---------|-------------|---------|
| `.ping` | PONG!!!! Anti-delay message | `.ping` |
| `.pink` | PONG!!!! with latency display | `.pink` |
| `.pong` | PONG + @spambot trigger for limits | `.pong` |
| `.ponk` | PONGGGGGG + triggers .alive | `.ponk` |
| `.pings` | Show all ping command info | `.pings` |

### 🎚 ID Checker Commands (Plugin)
| Command | Description | Example |
|---------|-------------|---------|
| `.id @username` | Check user ID by username | `.id @telegram` |
| `.id` (reply) | Check user ID from reply | Reply then `.id` |
| `.stopid` | Stop ID animation loop | `.stopid` |
| `.idinfo` | Show ID checker information | `.idinfo` |

### ⛈ Gcast & Blacklist Commands (Plugin)
| Command | Description | Example |
|---------|-------------|---------|
| `.gcast <text>` | Broadcast message to all groups | `.gcast Hello!` |
| `.gcast` (reply) | Broadcast replied message | Reply then `.gcast` |
| `.ginfo` | Show gcast information | `.ginfo` |
| `.addbl <id>` | Add chat to blacklist | `.addbl -1001234567` |
| `.addbl` (reply) | Add forwarded chat to blacklist | Reply then `.addbl` |
| `.rembl <id>` | Remove chat from blacklist | `.rembl -1001234567` |
| `.listbl` | List all blacklisted chats | `.listbl` |

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
| `API_ID` | Auto | API ID (29919905) |
| `API_HASH` | Auto | API Hash (pre-configured) |
| `STRING_SESSION` | Auto | Generated automatically |
| `VZOEL_PREFIX` | No | Command prefix (default: `.`) |
| `PREMIUM_EMOJIS_ENABLED` | No | Enable emoji features |

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

### Plugin Development
1. Create `.py` files in `plugins/` directory
2. Use `@events.register()` for command handlers
3. Add `vzoel_init()` function for initialization
4. Import `vzoel_emoji` for emoji integration

#### Example Plugin:
```python
from telethon import events

async def vzoel_init(client, vzoel_emoji):
    print("Plugin loaded!")

@events.register(events.NewMessage(pattern=r'\.test'))
async def test_handler(event):
    await event.edit("Test successful!")

test_handler.handler = test_handler.handler
test_handler.command = ".test"
```

### System Features
- **Auto-reload** plugins on file changes
- **Plugin management** with `.plugins` command  
- **Update system** with git integration
- **Statistics tracking** with `.stats` command

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