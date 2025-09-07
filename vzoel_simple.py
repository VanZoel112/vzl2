"""
VzoelFox Simple Internal Mapping
Simple internal mapping approach like VzoelFox
No external complexity, pure internal handling
Created by: Vzoel Fox's
"""

class VzoelSimpleEmoji:
    """Simple emoji mapping like VzoelFox"""
    
    def __init__(self):
        # Simple internal mapping like VzoelFox  
        self.emojis = {
            'utama': {'id': '6156784006194009426', 'char': '🤩'},
            'centang': {'id': '4947455506382849110', 'char': '👍'},
            'petir': {'id': '5794407002566300853', 'char': '⛈'},
            'loading': {'id': '5794353925360457382', 'char': '⚙️'},
            'kuning': {'id': '5260648752149970801', 'char': '🍿'},
            'biru': {'id': '5260687265121712272', 'char': '🎅'},
            'merah': {'id': '5262927296725007707', 'char': '🤪'},
            'proses': {'id': '5321023901998801538', 'char': '👽'},
            'aktif': {'id': '5794128499706958658', 'char': '🎚'},
            'adder1': {'id': '5357404860566235955', 'char': '😈'},
            'adder2': {'id': '5427157414375881061', 'char': '💟'},
            'telegram': {'id': '5350291836378307462', 'char': '✉️'}
        }
    
    def get_emoji(self, name, premium=True):
        """Get emoji simple method"""
        if name not in self.emojis:
            return "🔸"
        
        emoji_data = self.emojis[name]
        
        if premium:
            # Premium format
            return f"[{emoji_data['char']}](emoji/{emoji_data['id']})"
        
        # Standard emoji
        return emoji_data['char']
    
    def getemoji(self, name, premium=True):
        """Legacy method support"""
        return self.get_emoji(name, premium)
    
    def get_vzoel_signature(self, premium=True):
        """VzoelFox signature"""
        # utama + adder1 + petir
        sig_parts = [
            self.get_emoji('utama', premium),
            self.get_emoji('adder1', premium),
            self.get_emoji('petir', premium)
        ]
        return ''.join(sig_parts)
    
    def format_emoji_response(self, emoji_names, text="", use_premium=True):
        """Format response with emojis"""
        emoji_chars = []
        for name in emoji_names:
            emoji_chars.append(self.get_emoji(name, use_premium))
        
        if text:
            return f"{''.join(emoji_chars)} {text}"
        return ''.join(emoji_chars)
    
    def get_command_emojis(self, command):
        """Get command emojis"""
        mappings = {
            'alive': ['utama', 'aktif', 'petir'],
            'ping': ['loading', 'centang', 'aktif'],
            'vzoel': ['utama', 'petir', 'adder1'],
            'gcast': ['telegram', 'loading', 'centang'],
            'pizol': ['kuning', 'merah', 'adder2']
        }
        return mappings.get(command, ['utama'])

class VzoelSimpleComments:
    """Simple comment system"""
    
    def __init__(self):
        # Simple internal comments - adopted VzoelFox branding for vzl2
        self.comments = {
            "ping": "🏓 PONG!!!! VzoelFox Assistant Anti Delay",
            "ping_testing": "📡 Testing latency...", 
            "ping_latency": "🏓 PONG!!!! Latency {latency}ms",
            "loading": "⚙️ Sedang memproses...",
            "calculating": "🔄 Menghitung...",
            "connecting": "🌐 Menghubungkan...",
            "generating": "⚡ Menghasilkan...",
            "scanning": "🔍 Memindai...",
            "checking": "✅ Memeriksa...",
            "completed": "✅ Berhasil diselesaikan!",
            "done": "🎉 Selesai!",
            "success": "💯 Sukses!",
            "failed": "❌ Gagal diproses!",
            "timeout": "⏱️ Waktu habis!",
            "connection_error": "🌐 Error koneksi!",
            "signature": "🦊 VzoelFox's Assistant",
            "creator": "Created by: Vzoel Fox's",
            "enhanced": "Enhanced by Vzoel Fox's Ltpn",
            "copyright": "©2025 ~ Vzoel Fox's (LTPN)",
            "repo_notice": "Userbot ini dibuat dengan repo murni oleh Vzoel Fox's..\nBukan hasil fork maupun beli dari seller manapun!!!\nHak cipta sepenuhnya milik Vzoel..",
            "zone": "Zone: ID 🇮🇩",
            "ig": "IG: vzoel.fox_s",
            "alive_start": "🔧 Initializing VzoelFox Assistant...",
            "alive_ready": "✨ VzoelFox Assistant ready!",
            "help": "📚 VzoelFox Help System",
            "gcast_start": "📢 Mempersiapkan global cast...",
            "gcast_done": "✅ Global cast selesai!"
        }
    
    def get(self, key, **kwargs):
        """Get comment"""
        comment = self.comments.get(key, f"❓ Not found: {key}")
        if kwargs:
            try:
                return comment.format(**kwargs)
            except:
                return comment
        return comment
    
    def process(self, key):
        """Process comments"""
        return self.get(key)
    
    def result(self, key):
        """Result comments"""
        return self.get(key)
    
    def error(self, key):
        """Error comments"""
        return self.get(key)
    
    def response(self, key, subkey=None, **kwargs):
        """Response comments"""
        if subkey:
            combined_key = f"{key}_{subkey}"
            comment = self.comments.get(combined_key)
            if not comment:
                # Fallback untuk backward compatibility
                comment = self.comments.get(key, f"❓ Not found: {key}")
            if kwargs:
                try:
                    return comment.format(**kwargs)
                except:
                    return comment
            return comment
        return self.get(key, **kwargs)
    
    def vzoel(self, key):
        """VzoelFox branding"""
        return self.get(key)

# Global simple instances
vzoel_emoji = VzoelSimpleEmoji()
vzoel_comments = VzoelSimpleComments()