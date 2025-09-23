#!/usr/bin/env python3
"""
VZL2 Show JSON Plugin - Message to JSON Converter
Converts messages, emojis, stickers, media to detailed JSON metadata
Advanced message analysis with premium emoji mapping
Created by: VanZoel112
"""

import asyncio
import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from telethon import events
from telethon.tl.types import (
    MessageEntityCustomEmoji, User, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeSticker, DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeAnimated, MessageMediaWebPage
)

# Import from VZL2 utils
try:
    from utils.font_helper import convert_font
except ImportError:
    def convert_font(text, style):
        return text

# ===== Plugin Info =====
PLUGIN_INFO = {
    "name": "showjson",
    "version": "1.0.0",
    "description": "Advanced message to JSON converter with emoji/sticker/media analysis",
    "author": "VanZoel112",
    "commands": [".sj", ".showjson"],
    "features": ["message analysis", "emoji detection", "sticker metadata", "media info", "JSON export"]
}

# ===== PREMIUM EMOJI CONFIGURATION (VZL2 Format) =====
PREMIUM_EMOJIS = {
    'main': {'id': '6156784006194009426', 'char': '🤩'},
    'check': {'id': '5794353925360457382', 'char': '⚙️'},
    'adder1': {'id': '5794407002566300853', 'char': '⛈'},
    'adder2': {'id': '5793913811471700779', 'char': '✅'},
    'adder3': {'id': '5321412209992033736', 'char': '👽'},
    'adder4': {'id': '5793973133559993740', 'char': '✈️'},
    'adder5': {'id': '5357404860566235955', 'char': '😈'},
    'adder6': {'id': '5794323465452394551', 'char': '🎚️'}
}

def get_emoji(emoji_type):
    """Get premium emoji character"""
    return PREMIUM_EMOJIS.get(emoji_type, {}).get('char', '🤩')

def create_premium_entities(text):
    """Create premium emoji entities for text with UTF-16 support"""
    try:
        entities = []
        current_offset = 0
        i = 0

        while i < len(text):
            found_emoji = False

            for emoji_type, emoji_data in PREMIUM_EMOJIS.items():
                emoji_char = emoji_data['char']
                emoji_id = emoji_data['id']

                if text[i:].startswith(emoji_char):
                    try:
                        emoji_bytes = emoji_char.encode('utf-16-le')
                        utf16_length = len(emoji_bytes) // 2

                        entities.append(MessageEntityCustomEmoji(
                            offset=current_offset,
                            length=utf16_length,
                            document_id=int(emoji_id)
                        ))

                        i += len(emoji_char)
                        current_offset += utf16_length
                        found_emoji = True
                        break

                    except Exception:
                        break

            if not found_emoji:
                char = text[i]
                char_bytes = char.encode('utf-16-le')
                char_utf16_length = len(char_bytes) // 2
                current_offset += char_utf16_length
                i += 1

        return entities
    except Exception:
        return []

async def safe_send_premium(event, text):
    """Send message with premium entities"""
    try:
        entities = create_premium_entities(text)
        if entities:
            return await event.reply(text, formatting_entities=entities)
        else:
            return await event.reply(text)
    except Exception as e:
        print(f"[ShowJSON] Premium emoji error: {e}")
        return await event.reply(text)

class MessageJSONAnalyzer:
    """Advanced Message to JSON Converter with Media Analysis"""

    def __init__(self):
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F'  # emoticons
            r'\U0001F300-\U0001F5FF'   # symbols & pictographs
            r'\U0001F680-\U0001F6FF'   # transport & map
            r'\U0001F1E0-\U0001F1FF'   # flags
            r'\U00002700-\U000027BF'   # dingbats
            r'\U0001F900-\U0001F9FF'   # supplemental symbols
            r'\U00002600-\U000026FF'   # miscellaneous symbols
            r'\U0001F100-\U0001F1FF]+' # enclosed characters
        )

    def detect_emojis(self, text: str) -> List[Dict]:
        """Detect and analyze emojis in text"""
        emojis = []
        if not text:
            return emojis

        for match in self.emoji_pattern.finditer(text):
            emoji_char = match.group()
            emojis.append({
                "character": emoji_char,
                "position": match.start(),
                "end_position": match.end(),
                "unicode_codepoint": [f"U+{ord(c):04X}" for c in emoji_char],
                "name": f"EMOJI_{ord(emoji_char[0]):04X}",
                "category": "standard_emoji"
            })

        return emojis

    def analyze_custom_emojis(self, message) -> List[Dict]:
        """Analyze custom/premium emojis from message entities"""
        custom_emojis = []

        if not message.entities:
            return custom_emojis

        for entity in message.entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                custom_emojis.append({
                    "document_id": str(entity.document_id),
                    "offset": entity.offset,
                    "length": entity.length,
                    "type": "custom_emoji",
                    "is_premium": True
                })

        return custom_emojis

    def analyze_sticker(self, document) -> Dict:
        """Analyze sticker document"""
        sticker_info = {
            "type": "sticker",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": {}
        }

        # Analyze attributes
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                sticker_info["attributes"]["sticker"] = {
                    "alt": attr.alt,
                    "stickerset": {
                        "id": str(attr.stickerset.id) if attr.stickerset else None,
                        "access_hash": str(attr.stickerset.access_hash) if attr.stickerset else None
                    } if attr.stickerset else None,
                    "mask": attr.mask,
                    "mask_coords": str(attr.mask_coords) if hasattr(attr, 'mask_coords') and attr.mask_coords else None
                }
            elif isinstance(attr, DocumentAttributeAnimated):
                sticker_info["attributes"]["animated"] = True

        return sticker_info

    def analyze_photo(self, photo) -> Dict:
        """Analyze photo media"""
        return {
            "type": "photo",
            "id": str(photo.id),
            "access_hash": str(photo.access_hash),
            "file_reference": photo.file_reference.hex() if photo.file_reference else None,
            "date": photo.date.isoformat() if photo.date else None,
            "sizes": [
                {
                    "type": size.type,
                    "width": getattr(size, 'w', None),
                    "height": getattr(size, 'h', None),
                    "size": getattr(size, 'size', None)
                }
                for size in photo.sizes
            ],
            "dc_id": photo.dc_id,
            "has_stickers": photo.has_stickers if hasattr(photo, 'has_stickers') else False
        }

    def analyze_video(self, document) -> Dict:
        """Analyze video document"""
        video_info = {
            "type": "video",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": {}
        }

        # Analyze video attributes
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                video_info["attributes"]["video"] = {
                    "duration": attr.duration,
                    "width": attr.w,
                    "height": attr.h,
                    "round_message": attr.round_message if hasattr(attr, 'round_message') else False,
                    "supports_streaming": attr.supports_streaming if hasattr(attr, 'supports_streaming') else False
                }
            elif isinstance(attr, DocumentAttributeAnimated):
                video_info["attributes"]["animated"] = True

        return video_info

    def analyze_audio(self, document) -> Dict:
        """Analyze audio document"""
        audio_info = {
            "type": "audio",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": {}
        }

        # Analyze audio attributes
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeAudio):
                audio_info["attributes"]["audio"] = {
                    "duration": attr.duration,
                    "title": attr.title,
                    "performer": attr.performer,
                    "voice": attr.voice if hasattr(attr, 'voice') else False,
                    "waveform": attr.waveform.hex() if hasattr(attr, 'waveform') and attr.waveform else None
                }

        return audio_info

    def analyze_document(self, document) -> Dict:
        """Analyze generic document"""
        doc_info = {
            "type": "document",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": []
        }

        # Add attribute info
        for attr in document.attributes:
            doc_info["attributes"].append({
                "type": type(attr).__name__,
                "data": str(attr)
            })

        return doc_info

    async def analyze_message(self, message) -> Dict:
        """Comprehensive message analysis to JSON"""

        # Basic message info
        message_data = {
            "message_id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "chat_id": message.chat_id,
            "from_user": {
                "id": message.sender_id,
                "is_self": message.out,
                "username": None,
                "first_name": None,
                "last_name": None
            } if message.sender_id else None,
            "text": message.text or "",
            "text_length": len(message.text) if message.text else 0,
            "reply_to": message.reply_to_msg_id if message.reply_to_msg_id else None,
            "forward_from": None,
            "edit_date": message.edit_date.isoformat() if message.edit_date else None,
            "pinned": message.pinned,
            "views": message.views,
            "reactions": None
        }

        # Get sender info if available
        if message.sender:
            sender = message.sender
            message_data["from_user"].update({
                "username": sender.username,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "is_bot": sender.bot if hasattr(sender, 'bot') else False,
                "is_verified": sender.verified if hasattr(sender, 'verified') else False,
                "is_premium": sender.premium if hasattr(sender, 'premium') else False
            })

        # Analyze text emojis
        message_data["emojis"] = {
            "standard_emojis": self.detect_emojis(message.text),
            "custom_emojis": self.analyze_custom_emojis(message)
        }

        # Analyze media
        message_data["media"] = None
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                message_data["media"] = self.analyze_photo(message.media.photo)

            elif isinstance(message.media, MessageMediaDocument):
                document = message.media.document

                # Check document type
                is_sticker = any(isinstance(attr, DocumentAttributeSticker) for attr in document.attributes)
                is_video = any(isinstance(attr, DocumentAttributeVideo) for attr in document.attributes)
                is_audio = any(isinstance(attr, DocumentAttributeAudio) for attr in document.attributes)

                if is_sticker:
                    message_data["media"] = self.analyze_sticker(document)
                elif is_video:
                    message_data["media"] = self.analyze_video(document)
                elif is_audio:
                    message_data["media"] = self.analyze_audio(document)
                else:
                    message_data["media"] = self.analyze_document(document)

            elif isinstance(message.media, MessageMediaWebPage):
                message_data["media"] = {
                    "type": "webpage",
                    "webpage": {
                        "id": str(message.media.webpage.id) if hasattr(message.media.webpage, 'id') else None,
                        "url": message.media.webpage.url if hasattr(message.media.webpage, 'url') else None,
                        "title": message.media.webpage.title if hasattr(message.media.webpage, 'title') else None,
                        "description": message.media.webpage.description if hasattr(message.media.webpage, 'description') else None
                    }
                }

        # Message entities analysis
        message_data["entities"] = []
        if message.entities:
            for entity in message.entities:
                entity_data = {
                    "type": type(entity).__name__,
                    "offset": entity.offset,
                    "length": entity.length
                }

                # Add specific entity data
                if hasattr(entity, 'url'):
                    entity_data["url"] = entity.url
                if hasattr(entity, 'user_id'):
                    entity_data["user_id"] = entity.user_id
                if hasattr(entity, 'document_id'):
                    entity_data["document_id"] = str(entity.document_id)

                message_data["entities"].append(entity_data)

        # Analytics summary
        message_data["analytics"] = {
            "has_text": bool(message.text),
            "has_media": bool(message.media),
            "has_emojis": bool(message_data["emojis"]["standard_emojis"] or message_data["emojis"]["custom_emojis"]),
            "total_emojis": len(message_data["emojis"]["standard_emojis"]) + len(message_data["emojis"]["custom_emojis"]),
            "has_entities": bool(message.entities),
            "total_entities": len(message.entities) if message.entities else 0,
            "is_forwarded": bool(message.forward),
            "is_reply": bool(message.reply_to_msg_id),
            "is_edited": bool(message.edit_date)
        }

        return message_data

# Initialize analyzer
analyzer = MessageJSONAnalyzer()

async def is_owner_check(client, user_id):
    """Check if user is bot owner"""
    try:
        owner_id = os.getenv("OWNER_ID")
        if owner_id:
            return user_id == int(owner_id)
        me = await client.get_me()
        return user_id == me.id
    except Exception:
        return False

# Global client reference
client = None

async def showjson_handler(event):
    """Show JSON handler (.sj or .showjson)"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    # Show processing status
    processing_msg = await safe_send_premium(event,
        f"{get_emoji('check')} {convert_font('Analyzing Message...', 'bold')}\n\n"
        f"{get_emoji('adder1')} Processing message data to JSON..."
    )

    try:
        # Get target message
        target_message = None

        if event.reply_to_msg_id:
            # Analyze replied message
            target_message = await event.get_reply_message()
        else:
            # Analyze the command message itself
            target_message = event

        if not target_message:
            await processing_msg.edit(
                f"{get_emoji('adder5')} {convert_font('No Message to Analyze!', 'bold')}\n\n"
                f"{get_emoji('adder3')} Reply to a message to analyze it, or use the command to analyze itself."
            )
            return

        # Analyze message
        json_data = await analyzer.analyze_message(target_message)

        # Format JSON output
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        # Check if JSON is too long for single message
        if len(json_str) > 3500:  # Leave room for formatting
            # Split into chunks
            chunks = []
            chunk_size = 3500
            for i in range(0, len(json_str), chunk_size):
                chunks.append(json_str[i:i + chunk_size])

            # Send first chunk with header
            header_text = f"""{get_emoji('main')} {convert_font('MESSAGE JSON ANALYSIS', 'bold')}

{get_emoji('adder2')} {convert_font('Message ID:', 'bold')} {convert_font(str(json_data['message_id']), 'mono')}
{get_emoji('adder4')} {convert_font('Total Size:', 'bold')} {convert_font(f'{len(json_str)} chars', 'mono')}
{get_emoji('adder1')} {convert_font('Parts:', 'bold')} {convert_font(f'{len(chunks)} chunks', 'mono')}

{get_emoji('check')} {convert_font('Part 1/' + str(len(chunks)) + ':', 'bold')}

{convert_font('```json', 'mono')}
{chunks[0]}
{convert_font('```', 'mono')}"""

            await processing_msg.edit(header_text)

            # Send remaining chunks
            for i, chunk in enumerate(chunks[1:], 2):
                chunk_text = f"""{get_emoji('adder3')} {convert_font(f'Part {i}/{len(chunks)}:', 'bold')}

{convert_font('```json', 'mono')}
{chunk}
{convert_font('```', 'mono')}"""

                await event.reply(chunk_text)

        else:
            # Single message output
            analytics = json_data['analytics']

            result_text = f"""{get_emoji('main')} {convert_font('MESSAGE JSON ANALYSIS', 'bold')}

{get_emoji('adder2')} {convert_font('Message ID:', 'bold')} {convert_font(str(json_data['message_id']), 'mono')}
{get_emoji('adder4')} {convert_font('Chat ID:', 'bold')} {convert_font(str(json_data['chat_id']), 'mono')}
{get_emoji('adder1')} {convert_font('Date:', 'bold')} {convert_font(json_data['date'][:19] if json_data['date'] else 'N/A', 'mono')}

{get_emoji('check')} {convert_font('Analytics:', 'bold')}
  • Text: {convert_font('Yes' if analytics['has_text'] else 'No', 'mono')} ({convert_font(str(json_data['text_length']), 'mono')} chars)
  • Media: {convert_font('Yes' if analytics['has_media'] else 'No', 'mono')} ({convert_font(json_data['media']['type'] if json_data['media'] else 'None', 'mono')})
  • Emojis: {convert_font(str(analytics['total_emojis']), 'mono')} total
  • Entities: {convert_font(str(analytics['total_entities']), 'mono')} total

{get_emoji('adder3')} {convert_font('Full JSON Data:', 'bold')}

{convert_font('```json', 'mono')}
{json_str}
{convert_font('```', 'mono')}

{get_emoji('adder6')} VZL2 Message JSON Analyzer"""

            await processing_msg.edit(result_text)

        print(f"[ShowJSON] Analyzed message {json_data['message_id']} - {analytics['total_emojis']} emojis, {analytics['total_entities']} entities")

    except Exception as e:
        error_text = f"""{get_emoji('adder5')} {convert_font('Analysis Failed!', 'bold')}

{get_emoji('adder5')} {convert_font('Error:', 'bold')} {str(e)[:100]}...

{get_emoji('adder3')} {convert_font('Possible Issues:', 'bold')}
  • Message too complex to analyze
  • Media access restrictions
  • Network connectivity issues

{get_emoji('adder1')} {convert_font('Try again with simpler message', 'bold')}

{get_emoji('adder6')} VZL2 Message JSON Analyzer"""

        await processing_msg.edit(error_text)
        print(f"[ShowJSON] Analysis error: {e}")

def get_plugin_info():
    return PLUGIN_INFO

def setup(client_instance):
    """Setup function untuk register event handlers"""
    global client
    client = client_instance

    client.add_event_handler(showjson_handler, events.NewMessage(pattern=r'\.sj$'))
    client.add_event_handler(showjson_handler, events.NewMessage(pattern=r'\.showjson$'))

    print(f"✅ [ShowJSON] Message JSON analyzer loaded v{PLUGIN_INFO['version']} - .sj/.showjson commands ready")

def cleanup_plugin():
    """Cleanup plugin resources"""
    global client
    try:
        print("[ShowJSON] Plugin cleanup initiated")
        client = None
        print("[ShowJSON] Plugin cleanup completed")
    except Exception as e:
        print(f"[ShowJSON] Cleanup error: {e}")

# Export functions
__all__ = ['setup', 'cleanup_plugin', 'get_plugin_info', 'showjson_handler']