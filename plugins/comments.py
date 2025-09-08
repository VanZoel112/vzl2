"""
Enhanced Comments Plugin for VzoelFox Userbot - Premium Edition
Fitur: Comment system dengan custom responses
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium Comments System
"""

from telethon import events
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin info
__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global references (will be set by vzoel_init)
vzoel_client = None

class VzoelComments:
    """Centralized comment system untuk VzoelFox Assistant"""
    
    def __init__(self):
        self.comments = self.load_comments()
    
    def load_comments(self):
        """Load semua comment yang bisa di-customize"""
        return {
            # ==== PROCESS COMMENTS ====
            "process": {
                "loading": f"{get_emoji('loading')} Sedang memproses...",
                "calculating": f"{get_emoji('loading')} Menghitung...",
                "connecting": f"{get_emoji('telegram')} Menghubungkan...",
                "generating": f"{get_emoji('petir')} Menghasilkan...",
                "scanning": f"{get_emoji('proses')} Memindai...",
                "checking": f"{get_emoji('centang')} Memeriksa...",
                "validating": f"{get_emoji('aktif')} Memvalidasi...",
                "finalizing": f"{get_emoji('utama')} Menyelesaikan...",
                "initializing": f"{get_emoji('petir')} Memulai sistem...",
                "preparing": f"{get_emoji('aktif')} Mempersiapkan...",
                "testing": f"{get_emoji('kuning')} Menguji koneksi...",
                "uploading": f"{get_emoji('telegram')} Mengupload...",
                "downloading": f"{get_emoji('telegram')} Mendownload...",
                "processing": f"{get_emoji('loading')} Memproses data..."
            },
            # ==== SUCCESS COMMENTS ====
            "success": {
                "completed": f"{get_emoji('centang')} Berhasil diselesaikan!",
                "done": f"{get_emoji('utama')} Selesai!",
                "sent": f"{get_emoji('telegram')} Berhasil dikirim!",
                "saved": f"{get_emoji('adder2')} Berhasil disimpan!",
                "updated": f"{get_emoji('loading')} Berhasil diperbarui!",
                "connected": f"{get_emoji('telegram')} Terhubung dengan sukses!",
                "uploaded": f"{get_emoji('telegram')} Upload berhasil!",
                "downloaded": f"{get_emoji('telegram')} Download selesai!",
                "activated": f"{get_emoji('petir')} Berhasil diaktifkan!",
                "configured": f"{get_emoji('loading')} Konfigurasi berhasil!"
            },
            # ==== ERROR COMMENTS ====
            "error": {
                "failed": f"{get_emoji('merah')} Gagal diproses!",
                "timeout": f"{get_emoji('loading')} Waktu habis!",
                "connection_error": f"{get_emoji('telegram')} Error koneksi!",
                "permission_denied": f"{get_emoji('merah')} Akses ditolak!",
                "not_found": f"{get_emoji('proses')} Tidak ditemukan!",
                "invalid_input": f"{get_emoji('kuning')} Input tidak valid!",
                "server_error": f"{get_emoji('loading')} Error server!",
                "rate_limit": f"{get_emoji('loading')} Terkena rate limit!",
                "unknown_error": f"{get_emoji('kuning')} Error tidak diketahui!"
            },
            # ==== COMMAND RESPONSES ====
            "commands": {
                "ping": {
                    "testing": f"{get_emoji('telegram')} Testing latency...",
                    "result": f"{get_emoji('kuning')} PONG!!!! VzoelFox Assistant Anti Delay",
                    "with_latency": f"{get_emoji('kuning')} PONG!!!! Latency {{latency}}ms"
                },
                "alive": {
                    "phases": [
                        f"{get_emoji('loading')} Initializing VzoelFox Assistant...",
                        f"{get_emoji('adder2')} Loading premium components...",
                        f"{get_emoji('telegram')} Connecting to VzoelFox servers...",
                        f"{get_emoji('biru')} Validating premium emojis...",
                        f"{get_emoji('aktif')} Scanning installed plugins...",
                        f"{get_emoji('utama')} Checking system integrity...",
                        f"{get_emoji('aktif')} Verifying VzoelFox credentials...",
                        f"{get_emoji('utama')} Loading assistant profile...",
                        f"{get_emoji('biru')} Preparing display interface...",
                        f"{get_emoji('aktif')} Finalizing system status...",
                        f"{get_emoji('utama')} VzoelFox Assistant ready!",
                        f"{get_emoji('telegram')} Generating status display..."
                    ]
                },
                "help": {
                    "loading": f"{get_emoji('kuning')} Memuat daftar bantuan...",
                    "generating": f"{get_emoji('aktif')} Menyusun informasi bantuan..."
                },
                "gcast": {
                    "preparing": f"{get_emoji('telegram')} Mempersiapkan global cast...",
                    "sending": f"{get_emoji('telegram')} Mengirim ke {{count}} grup...",
                    "completed": f"{get_emoji('centang')} Global cast selesai!"
                }
            },
            # ==== STATUS INDICATORS ====
            "status": {
                "online": f"{get_emoji('centang')} Online",
                "offline": f"{get_emoji('merah')} Offline", 
                "busy": f"{get_emoji('kuning')} Sibuk",
                "away": f"{get_emoji('kuning')} Away",
                "dnd": f"{get_emoji('merah')} Jangan Diganggu",
                "invisible": f"{get_emoji('proses')} Tidak Terlihat"
            },
            # ==== CUSTOM VZOEL MESSAGES ====
            "vzoel": {
                "signature": f"{get_emoji('adder1')} VzoelFox's Assistant",
                "tagline": "Enhanced by Vzoel Fox's Ltpn",
                "copyright": "©2025 ~ Vzoel Fox's (LTPN)",
                "creator": "Created by: Vzoel Fox's",
                "repo_notice": "VzoelFox Userbot",
                "info": "Created by Vzoel Fox's"
Hak cipta sepenuhnya milik Vzoel..",
                "zone": "Zone: ID 🇮🇩",
                "ig": "IG: vzoel.fox_s"
            },
            # ==== SYSTEM MESSAGES ====
            "system": {
                "restarting": f"{get_emoji('loading')} Restarting VzoelFox Assistant...",
                "updating": f"{get_emoji('petir')} Updating system...",
                "maintenance": f"{get_emoji('loading')} System maintenance...",
                "backup": f"{get_emoji('adder2')} Creating backup...",
                "restore": f"{get_emoji('aktif')} Restoring from backup..."
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

async def vzoel_init(client, emoji_handler=None):
    """Plugin initialization"""
    global vzoel_client
    
    # Set global references
    vzoel_client = client
    
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Comments Plugin loaded - Centralized comment system ready")

@events.register(events.NewMessage(pattern=r'\.comments'))
async def comments_info_handler(event):
    """Show available comment categories"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        comments_info = f"""**{signature} VzoelFox Comments System**

{get_emoji('utama')} **Available Categories:**

{get_emoji('loading')} **process** - Loading, calculating, connecting
{get_emoji('centang')} **success** - Completed, done, sent
{get_emoji('merah')} **error** - Failed, timeout, connection errors
{get_emoji('telegram')} **commands** - Command-specific responses
{get_emoji('aktif')} **status** - Online, offline, busy indicators
{get_emoji('petir')} **vzoel** - VzoelFox branded messages
{get_emoji('proses')} **system** - System maintenance messages

{get_emoji('adder1')} **Usage Examples:**
• `vzoel_comments.get_process("loading")` 
• `vzoel_comments.get_success("completed")`
• `vzoel_comments.get_vzoel("signature")`

**Easy Customization Available!**"""
        
        
        msg = await event.edit(comments_info)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.customize (\w+) (\w+) (.+)'))
async def customize_comment_handler(event):
    """Customize a comment: .customize category key new_message"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client
        
        category = event.pattern_match.group(1)
        key = event.pattern_match.group(2)
        new_comment = event.pattern_match.group(3)
        
        # Customize the comment
        vzoel_comments.customize_comment(category, key, new_comment)
        
        success_msg = f"""{get_emoji('centang')} **Comment Updated!**

**Category:** {category}
**Key:** {key}
**New Message:** {new_comment}

{get_emoji('proses')} Comment berhasil di-customize untuk session ini."""
        
        
        msg = await event.edit(success_msg)
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.showcomment (\w+) (\w+)'))
async def show_comment_handler(event):
    """Show specific comment: .showcomment category key"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client
        
        category = event.pattern_match.group(1)
        key = event.pattern_match.group(2)
        
        comment = vzoel_comments.get(category, key)
        
        display_msg = f"""{get_emoji('utama')} **Comment Display**

**Category:** {category}
**Key:** {key}
**Message:** {comment}

{get_emoji('telegram')} Use `.customize {category} {key} new_message` to change"""
        
        
        msg = await event.edit(display_msg)
        vzoel_client.increment_command_count()