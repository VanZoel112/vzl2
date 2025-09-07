"""
VzoelFox's Assistant Comments Plugin
Centralized comment system for easy customization of process and command responses
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Plugin info
__version__ = "1.0.0"
__author__ = "Vzoel Fox's"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

class VzoelComments:
    """Centralized comment system untuk VzoelFox Assistant"""
    
    def __init__(self):
        self.comments = self.load_comments()
    
    def load_comments(self):
        """Load semua comment yang bisa di-customize"""
        return {
            # ==== PROCESS COMMENTS ====
            "process": {
                "loading": "⚙️ Sedang memproses...",
                "calculating": "🔄 Menghitung...",
                "connecting": "🌐 Menghubungkan...",
                "generating": "⚡ Menghasilkan...",
                "scanning": "🔍 Memindai...",
                "checking": "✅ Memeriksa...",
                "validating": "🔐 Memvalidasi...",
                "finalizing": "🎯 Menyelesaikan...",
                "initializing": "🚀 Memulai sistem...",
                "preparing": "📋 Mempersiapkan...",
                "testing": "🧪 Menguji koneksi...",
                "uploading": "📤 Mengupload...",
                "downloading": "📥 Mendownload...",
                "processing": "⚙️ Memproses data..."
            },
            
            # ==== SUCCESS COMMENTS ====
            "success": {
                "completed": "✅ Berhasil diselesaikan!",
                "done": "🎉 Selesai!",
                "sent": "📤 Berhasil dikirim!",
                "saved": "💾 Berhasil disimpan!",
                "updated": "🔄 Berhasil diperbarui!",
                "connected": "🌐 Terhubung dengan sukses!",
                "uploaded": "📤 Upload berhasil!",
                "downloaded": "📥 Download selesai!",
                "activated": "⚡ Berhasil diaktifkan!",
                "configured": "⚙️ Konfigurasi berhasil!"
            },
            
            # ==== ERROR COMMENTS ====
            "error": {
                "failed": "❌ Gagal diproses!",
                "timeout": "⏱️ Waktu habis!",
                "connection_error": "🌐 Error koneksi!",
                "permission_denied": "🚫 Akses ditolak!",
                "not_found": "🔍 Tidak ditemukan!",
                "invalid_input": "📝 Input tidak valid!",
                "server_error": "🛠️ Error server!",
                "rate_limit": "⏳ Terkena rate limit!",
                "unknown_error": "❓ Error tidak diketahui!"
            },
            
            # ==== COMMAND RESPONSES ====
            "commands": {
                "ping": {
                    "testing": "📡 Testing latency...",
                    "result": "🏓 PONG!!!! VzoelFox Assistant Anti Delay",
                    "with_latency": "🏓 PONG!!!! Latency {latency}ms"
                },
                "alive": {
                    "phases": [
                        "🔧 Initializing VzoelFox Assistant...",
                        "💎 Loading premium components...",
                        "🌐 Connecting to VzoelFox servers...",
                        "🎭 Validating premium emojis...",
                        "🔌 Scanning installed plugins...",
                        "🛡️ Checking system integrity...",
                        "🔐 Verifying VzoelFox credentials...",
                        "👤 Loading assistant profile...",
                        "🎨 Preparing display interface...",
                        "📊 Finalizing system status...",
                        "✨ VzoelFox Assistant ready!",
                        "📱 Generating status display..."
                    ]
                },
                "help": {
                    "loading": "📚 Memuat daftar bantuan...",
                    "generating": "📋 Menyusun informasi bantuan..."
                },
                "gcast": {
                    "preparing": "📢 Mempersiapkan global cast...",
                    "sending": "📤 Mengirim ke {count} grup...",
                    "completed": "✅ Global cast selesai!"
                }
            },
            
            # ==== STATUS INDICATORS ====
            "status": {
                "online": "🟢 Online",
                "offline": "🔴 Offline", 
                "busy": "🟡 Sibuk",
                "away": "🟠 Away",
                "dnd": "⛔ Jangan Diganggu",
                "invisible": "👻 Tidak Terlihat"
            },
            
            # ==== CUSTOM VZOEL MESSAGES ====
            "vzoel": {
                "signature": "🦊 VzoelFox's Assistant",
                "tagline": "Enhanced by Vzoel Fox's Ltpn",
                "copyright": "©2025 ~ Vzoel Fox's (LTPN)",
                "creator": "Created by: Vzoel Fox's",
                "repo_notice": "Userbot ini dibuat dengan repo murni oleh Vzoel Fox's..\nBukan hasil fork maupun beli dari seller manapun!!!\nHak cipta sepenuhnya milik Vzoel..",
                "zone": "Zone: ID 🇮🇩",
                "ig": "IG: vzoel.fox_s"
            },
            
            # ==== SYSTEM MESSAGES ====
            "system": {
                "restarting": "🔄 Restarting VzoelFox Assistant...",
                "updating": "⬆️ Updating system...",
                "maintenance": "🔧 System maintenance...",
                "backup": "💾 Creating backup...",
                "restore": "📁 Restoring from backup..."
            }
        }
    
    def get(self, category: str, key: str, **kwargs) -> str:
        """Get comment with optional formatting"""
        try:
            comment = self.comments[category][key]
            if kwargs:
                return comment.format(**kwargs)
            return comment
        except KeyError:
            return f"❓ Comment tidak ditemukan: {category}.{key}"
    
    def get_process(self, key: str) -> str:
        """Get process comment"""
        return self.get("process", key)
    
    def get_success(self, key: str) -> str:
        """Get success comment"""
        return self.get("success", key)
    
    def get_error(self, key: str) -> str:
        """Get error comment"""
        return self.get("error", key)
    
    def get_command(self, command: str, key: str, **kwargs) -> str:
        """Get command-specific comment"""
        try:
            comment = self.comments["commands"][command][key]
            if kwargs:
                return comment.format(**kwargs)
            return comment
        except KeyError:
            return f"❓ Command comment tidak ditemukan: {command}.{key}"
    
    def get_status(self, key: str) -> str:
        """Get status indicator"""
        return self.get("status", key)
    
    def get_vzoel(self, key: str) -> str:
        """Get VzoelFox specific message"""
        return self.get("vzoel", key)
    
    def get_system(self, key: str) -> str:
        """Get system message"""
        return self.get("system", key)
    
    def customize_comment(self, category: str, key: str, new_comment: str):
        """Customize a comment (runtime only)"""
        if category not in self.comments:
            self.comments[category] = {}
        self.comments[category][key] = new_comment
    
    def get_alive_phases(self) -> list:
        """Get alive animation phases"""
        return self.comments["commands"]["alive"]["phases"]

# Global comment instance
vzoel_comments = VzoelComments()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji
    
    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler
    
    signature = vzoel_emoji.get_vzoel_signature()
    print(f"{signature} Comments Plugin loaded - Centralized comment system ready")

@events.register(events.NewMessage(pattern=r'\.comments'))
async def comments_info_handler(event):
    """Show available comment categories"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        signature = vzoel_emoji.get_vzoel_signature()
        
        comments_info = f"""**{signature} VzoelFox Comments System**

{vzoel_emoji.get_emoji('utama')} **Available Categories:**

{vzoel_emoji.get_emoji('loading')} **process** - Loading, calculating, connecting
{vzoel_emoji.get_emoji('centang')} **success** - Completed, done, sent
{vzoel_emoji.get_emoji('merah')} **error** - Failed, timeout, connection errors
{vzoel_emoji.get_emoji('telegram')} **commands** - Command-specific responses
{vzoel_emoji.get_emoji('aktif')} **status** - Online, offline, busy indicators
{vzoel_emoji.get_emoji('petir')} **vzoel** - VzoelFox branded messages
{vzoel_emoji.get_emoji('proses')} **system** - System maintenance messages

{vzoel_emoji.get_emoji('adder1')} **Usage Examples:**
• `vzoel_comments.get_process("loading")` 
• `vzoel_comments.get_success("completed")`
• `vzoel_comments.get_vzoel("signature")`

**Easy Customization Available!**"""
        
        await event.edit(comments_info)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.customize (\w+) (\w+) (.+)'))
async def customize_comment_handler(event):
    """Customize a comment: .customize category key new_message"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        category = event.pattern_match.group(1)
        key = event.pattern_match.group(2)
        new_comment = event.pattern_match.group(3)
        
        # Customize the comment
        vzoel_comments.customize_comment(category, key, new_comment)
        
        success_msg = f"""{vzoel_emoji.get_emoji('centang')} **Comment Updated!**

**Category:** {category}
**Key:** {key}
**New Message:** {new_comment}

{vzoel_emoji.get_emoji('proses')} Comment berhasil di-customize untuk session ini."""
        
        await event.edit(success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.showcomment (\w+) (\w+)'))
async def show_comment_handler(event):
    """Show specific comment: .showcomment category key"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        category = event.pattern_match.group(1)
        key = event.pattern_match.group(2)
        
        comment = vzoel_comments.get(category, key)
        
        display_msg = f"""{vzoel_emoji.get_emoji('utama')} **Comment Display**

**Category:** {category}
**Key:** {key}
**Message:** {comment}

{vzoel_emoji.get_emoji('telegram')} Use `.customize {category} {key} new_message` to change"""
        
        await event.edit(display_msg)
        vzoel_client.increment_command_count()