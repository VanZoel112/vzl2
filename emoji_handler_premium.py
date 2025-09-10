"""
Vzoel Fox's Premium Emoji Handler - Telegram API Compliant
Enhanced emoji management with proper Telegram Premium emoji support
Created by: Vzoel Fox's
Enhanced with proper Telegram API integration
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
    """Premium emoji handler for Vzoel Fox's's Assistant with Telegram API compliance"""
    
    def __init__(self, mapping_file: str = "emoji_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.emojis = {}
        self.categories = {}
        self.usage_patterns = {}
        self.quick_access = {}
        self.client = None  # Will be set by client when available
        self.load_mapping()
        
    def set_client(self, client):
        """Set Telegram client for premium emoji functionality"""
        self.client = client
        
    def load_mapping(self) -> bool:
        """Load emoji mapping from JSON file"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.emojis = data.get('emojis', {})
            self.categories = data.get('categories', {})
            self.usage_patterns = data.get('usage_patterns', {})
            self.quick_access = data.get('quick_access', {})
            
            logging.info(f"Loaded {len(self.emojis)} Vzoel Fox's premium emojis")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load emoji mapping: {e}")
            return False
    
    def get_emoji(self, name: str) -> Optional[str]:
        """Get emoji character by name (standard fallback)"""
        emoji_data = self.emojis.get(name)
        if emoji_data:
            return emoji_data.get('emoji_char')
        return None
    
    def get_custom_emoji_id(self, name: str) -> Optional[str]:
        """Get custom emoji ID by name"""
        emoji_data = self.emojis.get(name)
        if emoji_data:
            return emoji_data.get('custom_emoji_id')
        return None
    
    def get_premium_emoji_markdown(self, name: str) -> Optional[str]:
        """Get premium emoji in Telegram markdown format for sending"""
        emoji_data = self.emojis.get(name)
        if emoji_data:
            emoji_char = emoji_data.get('emoji_char')
            custom_id = emoji_data.get('custom_emoji_id')
            if emoji_char and custom_id:
                # Format: [standard_emoji](emoji/custom_id)
                return f"[{emoji_char}](emoji/{custom_id})"
        return None
    
    def get_premium_emoji_html(self, name: str) -> Optional[str]:
        """Get premium emoji in HTML format"""
        emoji_data = self.emojis.get(name)
        if emoji_data:
            emoji_char = emoji_data.get('emoji_char')
            custom_id = emoji_data.get('custom_emoji_id')
            if emoji_char and custom_id:
                # Format: <tg-emoji emoji-id="custom_id">standard_emoji</tg-emoji>
                return f'<tg-emoji emoji-id="{custom_id}">{emoji_char}</tg-emoji>'
        return None
    
    async def get_premium_emoji_entity(self, name: str, offset: int = 0) -> Optional[MessageEntityCustomEmoji]:
        """Create MessageEntityCustomEmoji for proper API usage"""
        if not TELETHON_AVAILABLE:
            return None
            
        emoji_data = self.emojis.get(name)
        if emoji_data:
            custom_id = emoji_data.get('custom_emoji_id')
            emoji_char = emoji_data.get('emoji_char')
            if custom_id and emoji_char:
                # Length should be the actual length of the emoji character
                length = len(emoji_char)
                return MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=int(custom_id)
                )
        return None
    
    def format_premium_message(self, text: str, emoji_replacements: Dict[str, str]) -> str:
        """Format message with premium emoji markdown replacements"""
        formatted_text = text
        for placeholder, emoji_name in emoji_replacements.items():
            premium_emoji = self.get_premium_emoji_markdown(emoji_name)
            if premium_emoji:
                formatted_text = formatted_text.replace(placeholder, premium_emoji)
            else:
                # Fallback to standard emoji
                standard_emoji = self.get_emoji(emoji_name)
                if standard_emoji:
                    formatted_text = formatted_text.replace(placeholder, standard_emoji)
        return formatted_text
    
    def create_premium_signature(self) -> str:
        """Create premium signature with proper markdown format"""
        signature_ids = self.quick_access.get('vzoel_signature', [])
        premium_emojis = []
        
        for emoji_name, emoji_data in self.emojis.items():
            if emoji_data.get('custom_emoji_id') in signature_ids:
                premium_emoji = self.get_premium_emoji_markdown(emoji_name)
                if premium_emoji:
                    premium_emojis.append(premium_emoji)
                else:
                    # Fallback to standard
                    premium_emojis.append(emoji_data.get('emoji_char', ''))
        
        return ''.join(premium_emojis)
    
    async def send_premium_message(self, client, chat_id: Union[str, int], message: str, 
                                   emoji_names: List[str] = None) -> Any:
        """Send message with premium emojis using proper Telegram API"""
        if not TELETHON_AVAILABLE or not client:
            # Fallback to standard message
            return await client.send_message(chat_id, message)
        
        if emoji_names:
            # Replace emoji placeholders with markdown format
            emoji_replacements = {}
            for i, emoji_name in enumerate(emoji_names):
                placeholder = f"{{{emoji_name}}}"
                emoji_replacements[placeholder] = emoji_name
            
            formatted_message = self.format_premium_message(message, emoji_replacements)
            
            # Send with markdown parsing
            try:
                return await client.send_message(chat_id, formatted_message, parse_mode='markdown')
            except Exception as e:
                logging.warning(f"Failed to send premium emoji message: {e}")
                # Fallback to standard emojis
                fallback_message = message
                for placeholder, emoji_name in emoji_replacements.items():
                    standard_emoji = self.get_emoji(emoji_name)
                    if standard_emoji:
                        fallback_message = fallback_message.replace(placeholder, standard_emoji)
                
                return await client.send_message(chat_id, fallback_message)
        else:
            return await client.send_message(chat_id, message)
    
    # Keep all existing methods for backward compatibility
    def get_emoji_by_category(self, category: str) -> List[str]:
        """Get all emoji names in a category"""
        category_data = self.categories.get(category, {})
        return category_data.get('emojis', [])
    
    def get_command_emojis(self, command: str) -> List[str]:
        """Get recommended emojis for a command"""
        command_patterns = self.usage_patterns.get('command_responses', {})
        return command_patterns.get(command, [])
    
    def get_status_emojis(self, status: str) -> List[str]:
        """Get emojis for status indicators"""
        status_patterns = self.usage_patterns.get('status_indicators', {})
        return status_patterns.get(status, [])
    
    def get_theme_emojis(self, theme: str) -> List[str]:
        """Get emojis for a specific theme"""
        themes = self.usage_patterns.get('themes', {})
        return themes.get(theme, [])
    
    def format_emoji_response(self, emoji_names: List[str], text: str = "", use_premium: bool = True) -> str:
        """Format response with emojis (premium or standard)"""
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
    
    def getemoji(self, name: str, premium: bool = False) -> str:
        """Get emoji with fallback - supports premium format"""
        if premium:
            premium_emoji = self.get_premium_emoji_markdown(name)
            if premium_emoji:
                return premium_emoji
        
        emoji = self.get_emoji(name)
        return emoji if emoji else "🔸"  # Fallback emoji
    
    def get_vzoel_signature(self, premium: bool = False) -> str:
        """Get Vzoel Fox's signature emoji combination"""
        if premium:
            return self.create_premium_signature()
        
        # Standard signature
        signature_ids = self.quick_access.get('vzoel_signature', [])
        signature_emojis = []
        
        for emoji_name, emoji_data in self.emojis.items():
            if emoji_data.get('custom_emoji_id') in signature_ids:
                signature_emojis.append(emoji_data.get('emoji_char'))
        
        return ''.join(signature_emojis)
    
    def get_most_used(self) -> List[str]:
        """Get most used emoji IDs"""
        return self.quick_access.get('most_used', [])
    
    def search_emoji(self, query: str) -> List[Dict]:
        """Search emojis by name, description, or usage"""
        results = []
        query_lower = query.lower()
        
        for name, data in self.emojis.items():
            if (query_lower in name.lower() or 
                query_lower in data.get('description', '').lower() or
                query_lower in data.get('usage', '').lower()):
                
                results.append({
                    'name': name,
                    'emoji': data.get('emoji_char'),
                    'premium_markdown': self.get_premium_emoji_markdown(name),
                    'custom_id': data.get('custom_emoji_id'),
                    'description': data.get('description'),
                    'category': data.get('category')
                })
        
        return results
    
    def get_all_emojis(self) -> Dict:
        """Get all available emojis"""
        return self.emojis
    
    def is_valid_emoji(self, name: str) -> bool:
        """Check if emoji name is valid"""
        return name in self.emojis
    
    def get_emoji_info(self, name: str) -> Optional[Dict]:
        """Get complete information about an emoji"""
        emoji_data = self.emojis.get(name)
        if emoji_data:
            # Add premium formats to the info
            info = emoji_data.copy()
            info['premium_markdown'] = self.get_premium_emoji_markdown(name)
            info['premium_html'] = self.get_premium_emoji_html(name)
            return info
        return None
    
    def validate_emoji_mapping(self) -> Dict[str, List[str]]:
        """Validate emoji mapping against Telegram API requirements"""
        validation_results = {
            'valid': [],
            'invalid_id': [],
            'missing_char': [],
            'missing_id': []
        }
        
        for name, data in self.emojis.items():
            emoji_char = data.get('emoji_char')
            custom_id = data.get('custom_emoji_id')
            
            if not emoji_char:
                validation_results['missing_char'].append(name)
            elif not custom_id:
                validation_results['missing_id'].append(name)
            else:
                # Check if custom_id is valid format (should be numeric string)
                try:
                    int(custom_id)
                    validation_results['valid'].append(name)
                except ValueError:
                    validation_results['invalid_id'].append(name)
        
        return validation_results

# Global emoji handler instance
vzoel_emoji = VzoelEmojiHandler()