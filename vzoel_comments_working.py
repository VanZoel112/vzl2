"""
VzoelFox Working Comment System
Based on successful VanZoel112/vzoelfox comment structure
Simplified and working approach for process, results and responses
Created by: Vzoel Fox's
"""

class VzoelWorkingComments:
    """Working comment system based on VzoelFox structure"""
    
    def __init__(self):
        self.comments = {
            # Process messages
            "process": {
                "loading": "⚙️ Processing...",
                "connecting": "🌐 Connecting...", 
                "calculating": "🔄 Calculating...",
                "generating": "⚡ Generating...",
                "scanning": "🔍 Scanning...",
                "checking": "✅ Checking...",
                "preparing": "📋 Preparing...",
                "initializing": "🚀 Initializing...",
                "uploading": "📤 Uploading...",
                "downloading": "📥 Downloading..."
            },
            
            # Success/Result messages
            "result": {
                "completed": "✅ Completed successfully!",
                "done": "🎉 Done!",
                "success": "💯 Success!",
                "finished": "🏁 Finished!",
                "sent": "📤 Sent successfully!",
                "saved": "💾 Saved!",
                "updated": "🔄 Updated!",
                "connected": "🌐 Connected!",
                "ready": "✨ Ready!"
            },
            
            # Error messages  
            "error": {
                "failed": "❌ Failed!",
                "timeout": "⏱️ Timeout!",
                "connection_error": "🌐 Connection error!",
                "not_found": "🔍 Not found!",
                "permission_denied": "🚫 Permission denied!",
                "invalid": "📝 Invalid input!",
                "server_error": "🛠️ Server error!",
                "rate_limit": "⏳ Rate limited!"
            },
            
            # Response messages
            "response": {
                "ping": "🏓 PONG!!!! VzoelFox Assistant Active",
                "alive_start": "🔧 Starting VzoelFox Assistant...",
                "alive_ready": "✨ VzoelFox Assistant Ready!",
                "help": "📚 VzoelFox Help System",
                "gcast_start": "📢 Starting global cast...",
                "gcast_done": "✅ Global cast completed!",
                "system_info": "💻 System Information"
            },
            
            # Vzoel branding
            "vzoel": {
                "signature": "🦊 VzoelFox's Assistant",
                "creator": "Created by: Vzoel Fox's",
                "enhanced": "Enhanced by Vzoel Fox's Ltpn",
                "copyright": "©2025 ~ Vzoel Fox's (LTPN)",
                "repo": "Vzoel Fox's Original Repository"
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
            return f"❓ Comment not found: {category}.{key}"
    
    def process(self, key: str) -> str:
        """Get process comment"""
        return self.get("process", key)
    
    def result(self, key: str) -> str:
        """Get result comment"""  
        return self.get("result", key)
    
    def error(self, key: str) -> str:
        """Get error comment"""
        return self.get("error", key)
    
    def response(self, key: str, subkey: str = None, **kwargs) -> str:
        """Get response comment with optional subkey"""
        if subkey:
            # Handle nested response like response("ping", "result")
            try:
                if key == "ping":
                    ping_responses = {
                        "result": "🏓 PONG!!!! VzoelFox Assistant Active",
                        "testing": "📡 Testing latency...",
                        "with_latency": "🏓 PONG!!!! Latency {latency}ms"
                    }
                    comment = ping_responses.get(subkey, f"❓ Subkey not found: {key}.{subkey}")
                else:
                    comment = f"❓ Nested response not found: {key}.{subkey}"
                
                if kwargs:
                    return comment.format(**kwargs)
                return comment
            except:
                return f"❓ Response error: {key}.{subkey}"
        else:
            return self.get("response", key, **kwargs)
    
    def vzoel(self, key: str) -> str:
        """Get vzoel branding comment"""
        return self.get("vzoel", key)
    
    def customize(self, category: str, key: str, new_comment: str):
        """Customize comment at runtime"""
        if category not in self.comments:
            self.comments[category] = {}
        self.comments[category][key] = new_comment
    
    def get_all_categories(self) -> list:
        """Get all comment categories"""
        return list(self.comments.keys())
    
    def get_category_keys(self, category: str) -> list:
        """Get all keys in a category"""
        return list(self.comments.get(category, {}).keys())

# Global working comment instance
vzoel_comments = VzoelWorkingComments()