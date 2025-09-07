"""
VzoelFox Premium Emoji Handler - Working Implementation
Based on successful VanZoel112/vzoelfox structure but adapted for vzl2
Maintains existing premium emoji IDs while using proven implementation approach
Created by: Vzoel Fox's
Enhanced with working mapping structure
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

# Import Telethon components for premium emoji
try:
    from telethon.tl.types import MessageEntityCustomEmoji
    from telethon.tl.functions import messages
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logging.warning("Telethon not available - premium emoji features limited")

class VzoelEmojiHandler:
    """Working premium emoji handler for VzoelFox's Assistant"""
    
    def __init__(self, mapping_file: str = "emoji_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.emojis = {}
        self.quick_emojis = {}  # Simple format like VzoelFox
        self.client = None
        self.load_mapping()
        self._create_quick_mapping()
        
    def load_mapping(self) -> bool:
        """Load emoji mapping from JSON file"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.emojis = data.get('emojis', {})
            logging.info(f"Loaded {len(self.emojis)} VzoelFox premium emojis")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load emoji mapping: {e}")
            return False
    
    def _create_quick_mapping(self):
        """Create simple mapping format like VzoelFox"""
        for name, data in self.emojis.items():
            self.quick_emojis[name] = {
                'id': data.get('custom_emoji_id'),
                'char': data.get('emoji_char')
            }
    
    def set_client(self, client):
        """Set Telegram client for premium emoji functionality"""
        self.client = client
    
    def get_emoji(self, name: str, premium: bool = True) -> str:
        """Get emoji with working implementation like VzoelFox"""
        if name not in self.quick_emojis:
            return "🔸"  # Fallback
        
        emoji_data = self.quick_emojis[name]
        
        if premium and emoji_data.get('id'):
            # Return markdown format for premium emojis
            char = emoji_data.get('char', '🔸')
            emoji_id = emoji_data.get('id')
            return f"[{char}](emoji/{emoji_id})"
        
        # Return standard emoji
        return emoji_data.get('char', '🔸')
    
    def getemoji(self, name: str, premium: bool = True) -> str:
        """Legacy method name support"""
        return self.get_emoji(name, premium)
    
    async def create_premium_entity(self, name: str, offset: int) -> Optional[MessageEntityCustomEmoji]:
        """Create MessageEntityCustomEmoji for API compliance"""
        if not TELETHON_AVAILABLE or name not in self.quick_emojis:
            return None
        
        emoji_data = self.quick_emojis[name]
        emoji_id = emoji_data.get('id')
        char = emoji_data.get('char')
        
        if emoji_id and char:
            # Calculate proper UTF-16 length for the emoji character
            utf16_length = len(char.encode('utf-16le')) // 2
            
            return MessageEntityCustomEmoji(
                offset=offset,
                length=utf16_length,
                document_id=int(emoji_id)
            )
        
        return None
    
    def format_message_with_premium(self, text: str, emoji_replacements: Dict[str, str]) -> str:
        """Format message with premium emoji like VzoelFox"""
        formatted_text = text
        
        for placeholder, emoji_name in emoji_replacements.items():
            premium_emoji = self.get_emoji(emoji_name, premium=True)
            formatted_text = formatted_text.replace(placeholder, premium_emoji)
        
        return formatted_text
    
    async def send_premium_message(self, client, chat_id: Union[str, int], message: str, 
                                  emoji_names: List[str] = None) -> Any:
        """Send message with premium emojis using working approach"""
        if not client:
            return None
        
        if emoji_names:
            # Create replacements dict
            emoji_replacements = {}
            for i, emoji_name in enumerate(emoji_names):
                placeholder = f"{{{emoji_name}}}"
                emoji_replacements[placeholder] = emoji_name
            
            # Format message with premium emojis
            formatted_message = self.format_message_with_premium(message, emoji_replacements)
            
            try:
                # Send with markdown parsing
                return await client.send_message(chat_id, formatted_message, parse_mode='markdown')
            except Exception as e:
                logging.warning(f"Premium emoji send failed: {e}")
                # Fallback to standard emojis
                fallback_message = message
                for placeholder, emoji_name in emoji_replacements.items():
                    standard_emoji = self.get_emoji(emoji_name, premium=False)
                    fallback_message = fallback_message.replace(placeholder, standard_emoji)
                
                return await client.send_message(chat_id, fallback_message)
        
        return await client.send_message(chat_id, message)
    
    def get_vzoel_signature(self, premium: bool = True) -> str:
        """Get Vzoel signature with working approach"""
        # Use signature emojis: utama, adder1, petir
        signature_emojis = ['utama', 'adder1', 'petir']
        result = ''
        
        for emoji_name in signature_emojis:
            result += self.get_emoji(emoji_name, premium)
        
        return result
    
    def get_all_emoji_names(self) -> List[str]:
        """Get all available emoji names"""
        return list(self.quick_emojis.keys())
    
    def is_valid_emoji(self, name: str) -> bool:
        """Check if emoji name exists"""
        return name in self.quick_emojis
    
    def get_emoji_info(self, name: str) -> Optional[Dict]:
        """Get emoji information"""
        if name not in self.quick_emojis:
            return None
        
        quick_data = self.quick_emojis[name]
        full_data = self.emojis.get(name, {})
        
        return {
            'name': name,
            'char': quick_data.get('char'),
            'id': quick_data.get('id'),
            'premium_format': self.get_emoji(name, premium=True),
            'category': full_data.get('category', 'unknown'),
            'description': full_data.get('description', '')
        }
    
    # Compatibility methods for existing code
    def get_premium_emoji_markdown(self, name: str) -> Optional[str]:
        """Get premium emoji in markdown format"""
        return self.get_emoji(name, premium=True) if self.is_valid_emoji(name) else None
    
    def get_custom_emoji_id(self, name: str) -> Optional[str]:
        """Get custom emoji ID"""
        if name in self.quick_emojis:
            return self.quick_emojis[name].get('id')
        return None
    
    def format_premium_message(self, text: str, emoji_replacements: Dict[str, str]) -> str:
        """Format message with premium emoji replacements"""
        return self.format_message_with_premium(text, emoji_replacements)
    
    def format_emoji_response(self, emoji_names: List[str], text: str = "", use_premium: bool = True) -> str:
        """Format response with emojis (premium or standard) - compatibility method"""
        if use_premium:
            # Use premium markdown format
            emoji_chars = []
            for name in emoji_names:
                premium_emoji = self.get_premium_emoji_markdown(name)
                if premium_emoji:
                    emoji_chars.append(premium_emoji)
                else:
                    # Fallback to standard
                    emoji = self.get_emoji(name)
                    if emoji:
                        emoji_chars.append(emoji)
        else:
            # Use standard emojis
            emoji_chars = []
            for name in emoji_names:
                emoji = self.get_emoji(name)
                if emoji:
                    emoji_chars.append(emoji)
        
        if text:
            return f"{''.join(emoji_chars)} {text}"
        return ''.join(emoji_chars)
    
    def get_command_emojis(self, command: str) -> List[str]:
        """Get recommended emojis for a command - compatibility method"""
        # Return emojis based on command
        command_mappings = {
            'alive': ['utama', 'aktif', 'petir'],
            'ping': ['loading', 'centang', 'aktif'],
            'vzoel': ['utama', 'petir', 'adder1'],
            'gcast': ['telegram', 'loading', 'centang'],
            'pizol': ['kuning', 'merah', 'adder2']
        }
        return command_mappings.get(command, ['utama'])

# Global emoji handler instance using working implementation
vzoel_emoji = VzoelEmojiHandler()