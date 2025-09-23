"""
VZL2 Show JSON Plugin - Message to JSON Converter
Converts messages, emojis, stickers, media to detailed JSON metadata
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 1.0.0 - Premium JSON Analyzer
"""

from telethon import events
from telethon.tl.types import (
    MessageEntityCustomEmoji, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeSticker, DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeAnimated, MessageMediaWebPage
)
import json
import re
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VZL2 style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "showjson",
    "version": "1.0.0",
    "description": "Premium message to JSON converter dengan emoji/sticker/media analysis",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".sj", ".showjson"],
    "features": ["message analysis", "emoji detection", "media metadata", "JSON export"]
}

__version__ = "1.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

class JSONAnalyzer:
    """Premium Message to JSON Converter"""

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

    def detect_emojis(self, text: str) -> list:
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
                "category": "standard_emoji"
            })

        return emojis

    def analyze_custom_emojis(self, message) -> list:
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

    def get_media_type(self, message) -> str:
        """Determine media type from message"""
        if not message.media:
            return "text"

        if isinstance(message.media, MessageMediaPhoto):
            return "photo"
        elif isinstance(message.media, MessageMediaDocument):
            document = message.media.document

            for attr in document.attributes:
                if isinstance(attr, DocumentAttributeSticker):
                    return "sticker"
                elif isinstance(attr, DocumentAttributeVideo):
                    if hasattr(attr, 'round_message') and attr.round_message:
                        return "video_note"
                    return "video"
                elif isinstance(attr, DocumentAttributeAudio):
                    if hasattr(attr, 'voice') and attr.voice:
                        return "voice"
                    return "audio"
                elif isinstance(attr, DocumentAttributeAnimated):
                    return "gif"

            return "document"
        elif isinstance(message.media, MessageMediaWebPage):
            return "webpage"

        return "other"

    def analyze_photo(self, photo) -> dict:
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
            "dc_id": photo.dc_id
        }

    def analyze_document(self, document) -> dict:
        """Analyze document media"""
        doc_info = {
            "type": "document",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": []
        }

        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                doc_info["sticker_info"] = {
                    "alt": attr.alt,
                    "stickerset_id": str(attr.stickerset.id) if attr.stickerset else None,
                    "mask": attr.mask
                }
            elif isinstance(attr, DocumentAttributeVideo):
                doc_info["video_info"] = {
                    "duration": attr.duration,
                    "width": attr.w,
                    "height": attr.h,
                    "round_message": getattr(attr, 'round_message', False)
                }
            elif isinstance(attr, DocumentAttributeAudio):
                doc_info["audio_info"] = {
                    "duration": attr.duration,
                    "title": attr.title,
                    "performer": attr.performer,
                    "voice": getattr(attr, 'voice', False)
                }

        return doc_info

    async def analyze_message(self, message) -> dict:
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
            "edit_date": message.edit_date.isoformat() if message.edit_date else None,
            "pinned": message.pinned,
            "views": message.views
        }

        # Get sender info if available
        if message.sender:
            sender = message.sender
            message_data["from_user"].update({
                "username": sender.username,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "is_bot": getattr(sender, 'bot', False),
                "is_verified": getattr(sender, 'verified', False),
                "is_premium": getattr(sender, 'premium', False)
            })

        # Analyze emojis
        message_data["emojis"] = {
            "standard_emojis": self.detect_emojis(message.text),
            "custom_emojis": self.analyze_custom_emojis(message)
        }

        # Analyze media
        message_data["media"] = None
        media_type = self.get_media_type(message)
        message_data["media_type"] = media_type

        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                message_data["media"] = self.analyze_photo(message.media.photo)
            elif isinstance(message.media, MessageMediaDocument):
                message_data["media"] = self.analyze_document(message.media.document)
            elif isinstance(message.media, MessageMediaWebPage):
                message_data["media"] = {
                    "type": "webpage",
                    "url": getattr(message.media.webpage, 'url', None),
                    "title": getattr(message.media.webpage, 'title', None),
                    "description": getattr(message.media.webpage, 'description', None)
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
analyzer = JSONAnalyzer()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('telegram')}{get_emoji('proses')}"
    print(f"✅ [ShowJSON] Premium JSON analyzer loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [ShowJSON] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} JSON ANALYZER")

@events.register(events.NewMessage(pattern=r'\.sj'))
async def sj_handler(event):
    """Show JSON handler (.sj)"""
    if not await is_owner(event):
        return

    processing_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Analyzing Message...**\n\n"
        f"{get_emoji('proses')} Processing message data to JSON..."
    )

    try:
        target_message = None

        if event.reply_to_msg_id:
            target_message = await event.get_reply_message()
        else:
            target_message = event

        if not target_message:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} **No Message to Analyze!**\n\n"
                f"{get_emoji('kuning')} Reply to a message to analyze it\n\n"
                f"{get_emoji('telegram')} VZL2 JSON Analyzer"
            )
            return

        # Analyze message
        json_data = await analyzer.analyze_message(target_message)
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        # Check if JSON is too long
        if len(json_str) > 3500:
            # Split into chunks
            chunks = []
            chunk_size = 3500
            for i in range(0, len(json_str), chunk_size):
                chunks.append(json_str[i:i + chunk_size])

            # Send first chunk with header
            header_text = f"{get_emoji('utama')} **MESSAGE JSON ANALYSIS**\n\n"
            header_text += f"{get_emoji('aktif')} **Message ID:** `{json_data['message_id']}`\n"
            header_text += f"{get_emoji('proses')} **Total Size:** `{len(json_str)} chars`\n"
            header_text += f"{get_emoji('loading')} **Parts:** `{len(chunks)} chunks`\n\n"
            header_text += f"{get_emoji('centang')} **Part 1/{len(chunks)}:**\n\n"
            header_text += f"```json\n{chunks[0]}\n```"

            await safe_edit_premium(processing_msg, header_text)

            # Send remaining chunks
            for i, chunk in enumerate(chunks[1:], 2):
                chunk_text = f"{get_emoji('kuning')} **Part {i}/{len(chunks)}:**\n\n"
                chunk_text += f"```json\n{chunk}\n```"
                await event.reply(chunk_text)

        else:
            # Single message output
            analytics = json_data['analytics']

            result_text = f"{get_emoji('utama')} **MESSAGE JSON ANALYSIS**\n\n"
            result_text += f"{get_emoji('aktif')} **Message ID:** `{json_data['message_id']}`\n"
            result_text += f"{get_emoji('proses')} **Chat ID:** `{json_data['chat_id']}`\n"
            result_text += f"{get_emoji('loading')} **Date:** `{json_data['date'][:19] if json_data['date'] else 'N/A'}`\n\n"

            result_text += f"{get_emoji('centang')} **Analytics:**\n"
            result_text += f"  • Text: `{'Yes' if analytics['has_text'] else 'No'}` (`{json_data['text_length']}` chars)\n"
            result_text += f"  • Media: `{'Yes' if analytics['has_media'] else 'No'}` (`{json_data['media_type']}`)\n"
            result_text += f"  • Emojis: `{analytics['total_emojis']}` total\n"
            result_text += f"  • Entities: `{analytics['total_entities']}` total\n\n"

            result_text += f"{get_emoji('kuning')} **Full JSON Data:**\n\n"
            result_text += f"```json\n{json_str}\n```\n\n"
            result_text += f"{get_emoji('telegram')} VZL2 JSON Analyzer"

            await safe_edit_premium(processing_msg, result_text)

    except Exception as e:
        await safe_edit_premium(processing_msg,
            f"{get_emoji('merah')} **Analysis Failed!**\n\n"
            f"{get_emoji('merah')} **Error:** `{str(e)[:100]}`\n\n"
            f"{get_emoji('kuning')} **Possible Issues:**\n"
            f"  • Message too complex to analyze\n"
            f"  • Media access restrictions\n"
            f"  • Network connectivity issues\n\n"
            f"{get_emoji('telegram')} VZL2 JSON Analyzer"
        )

@events.register(events.NewMessage(pattern=r'\.showjson'))
async def showjson_handler(event):
    """Show JSON handler (.showjson) - alias for .sj"""
    await sj_handler(event)