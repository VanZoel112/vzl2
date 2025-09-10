"""
Vzoel Fox's Premium Emoji Handler
Enhanced emoji management for Vzoel Fox's's Assistant v2
"""

import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

class VzoelEmojiHandler:
    """Premium emoji handler for Vzoel Fox's's Assistant"""
    
    def __init__(self, mapping_file: str = "emoji_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.emojis = {}
        self.categories = {}
        self.usage_patterns = {}
        self.quick_access = {}
        self.load_mapping()
        
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
        """Get emoji character by name"""
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
    
    def format_emoji_response(self, emoji_names: List[str], text: str = "") -> str:
        """Format response with emojis"""
        emoji_chars = []
        for name in emoji_names:
            emoji = self.get_emoji(name)
            if emoji:
                emoji_chars.append(emoji)
        
        if text:
            return f"{''.join(emoji_chars)} {text}"
        return ''.join(emoji_chars)
    
    def getemoji(self, name: str) -> str:
        """Get emoji with fallback - alternative method name"""
        emoji = self.get_emoji(name)
        return emoji if emoji else "🔸"  # Fallback emoji
    
    def get_vzoel_signature(self) -> str:
        """Get Vzoel Fox's signature emoji combination"""
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
        return self.emojis.get(name)

# Global emoji handler instance
vzoel_emoji = VzoelEmojiHandler()