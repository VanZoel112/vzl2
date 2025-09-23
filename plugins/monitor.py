#!/usr/bin/env python3
"""
VZL2 User Monitor Plugin - Group Activity Tracking & Statistics
Advanced user activity monitoring with message and media statistics
Real-time user behavior analysis in groups
Created by: VanZoel112
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from telethon import events
from telethon.tl.types import (
    MessageEntityCustomEmoji, User, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeSticker, DocumentAttributeVideo, DocumentAttributeAudio,
    MessageMediaWebPage, DocumentAttributeAnimated
)
from telethon.errors import (
    UsernameNotOccupiedError, UsernameInvalidError, PeerIdInvalidError
)

# Import from VZL2 utils
try:
    from utils.font_helper import convert_font
except ImportError:
    def convert_font(text, style):
        return text

# ===== Plugin Info =====
PLUGIN_INFO = {
    "name": "monitor",
    "version": "1.0.0",
    "description": "Advanced user activity monitoring and statistics in groups",
    "author": "VanZoel112",
    "commands": [".monitor <user>", ".stats <user>", ".activity <user>"],
    "features": ["user tracking", "message statistics", "media analysis", "activity patterns", "group monitoring"]
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
        print(f"[Monitor] Premium emoji error: {e}")
        return await event.reply(text)

class UserMonitorSystem:
    """Advanced User Activity Monitoring System"""

    def __init__(self):
        self.monitoring_data = defaultdict(lambda: {
            'messages': defaultdict(list),
            'media_stats': defaultdict(int),
            'activity_patterns': defaultdict(int),
            'daily_stats': defaultdict(int),
            'user_info': {},
            'last_seen': None,
            'total_messages': 0,
            'message_types': defaultdict(int)
        })

    def get_media_type(self, message) -> str:
        """Determine media type from message"""
        if not message.media:
            return "text"

        if isinstance(message.media, MessageMediaPhoto):
            return "photo"
        elif isinstance(message.media, MessageMediaDocument):
            document = message.media.document

            # Check document attributes for specific types
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

    def get_time_period(self, timestamp: datetime) -> str:
        """Get time period classification"""
        hour = timestamp.hour

        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def analyze_message_content(self, message) -> Dict:
        """Analyze message content for patterns"""
        content_analysis = {
            'text_length': len(message.text) if message.text else 0,
            'has_emojis': bool(message.entities and any(
                isinstance(e, MessageEntityCustomEmoji) for e in message.entities
            )),
            'word_count': len(message.text.split()) if message.text else 0,
            'has_links': bool(message.entities and any(
                'url' in str(type(e)).lower() for e in message.entities
            )),
            'has_mentions': bool(message.entities and any(
                'mention' in str(type(e)).lower() for e in message.entities
            )),
            'is_forwarded': bool(message.forward),
            'is_reply': bool(message.reply_to_msg_id),
            'language_detected': 'unknown'  # Could be enhanced with language detection
        }

        # Simple language detection based on characters
        if message.text:
            if any('\u0600' <= c <= '\u06FF' for c in message.text):
                content_analysis['language_detected'] = 'arabic'
            elif any('\u4e00' <= c <= '\u9fff' for c in message.text):
                content_analysis['language_detected'] = 'chinese'
            elif any('\u0400' <= c <= '\u04FF' for c in message.text):
                content_analysis['language_detected'] = 'cyrillic'
            elif message.text.isascii():
                content_analysis['language_detected'] = 'latin'

        return content_analysis

    async def track_user_activity(self, user_id: int, chat_id: int, message) -> None:
        """Track user activity from message"""
        user_key = f"{user_id}_{chat_id}"
        timestamp = message.date

        # Update user info
        if message.sender:
            self.monitoring_data[user_key]['user_info'] = {
                'id': user_id,
                'username': message.sender.username,
                'first_name': message.sender.first_name,
                'last_name': message.sender.last_name,
                'is_bot': getattr(message.sender, 'bot', False),
                'is_premium': getattr(message.sender, 'premium', False)
            }

        # Track message
        media_type = self.get_media_type(message)
        time_period = self.get_time_period(timestamp)
        content_analysis = self.analyze_message_content(message)

        # Update statistics
        self.monitoring_data[user_key]['total_messages'] += 1
        self.monitoring_data[user_key]['media_stats'][media_type] += 1
        self.monitoring_data[user_key]['activity_patterns'][time_period] += 1
        self.monitoring_data[user_key]['message_types'][media_type] += 1
        self.monitoring_data[user_key]['last_seen'] = timestamp.isoformat()

        # Daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        self.monitoring_data[user_key]['daily_stats'][date_key] += 1

        # Store recent messages (last 50)
        message_data = {
            'id': message.id,
            'timestamp': timestamp.isoformat(),
            'media_type': media_type,
            'content_length': content_analysis['text_length'],
            'word_count': content_analysis['word_count'],
            'has_media': bool(message.media),
            'is_forwarded': content_analysis['is_forwarded'],
            'is_reply': content_analysis['is_reply'],
            'text_preview': (message.text[:50] + '...') if message.text and len(message.text) > 50 else (message.text or '')
        }

        self.monitoring_data[user_key]['messages']['recent'].append(message_data)

        # Keep only last 50 messages
        if len(self.monitoring_data[user_key]['messages']['recent']) > 50:
            self.monitoring_data[user_key]['messages']['recent'] = \
                self.monitoring_data[user_key]['messages']['recent'][-50:]

    def get_user_statistics(self, user_id: int, chat_id: int) -> Dict:
        """Get comprehensive user statistics"""
        user_key = f"{user_id}_{chat_id}"
        data = self.monitoring_data[user_key]

        if not data['user_info']:
            return None

        # Calculate activity metrics
        total_messages = data['total_messages']
        media_stats = dict(data['media_stats'])
        activity_patterns = dict(data['activity_patterns'])
        daily_stats = dict(data['daily_stats'])

        # Recent activity (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_activity = sum(
            count for date_str, count in daily_stats.items()
            if datetime.fromisoformat(date_str + 'T00:00:00') >= recent_date
        )

        # Most active time
        most_active_time = max(activity_patterns.items(), key=lambda x: x[1])[0] if activity_patterns else "unknown"

        # Media breakdown percentage
        media_percentages = {}
        if total_messages > 0:
            for media_type, count in media_stats.items():
                media_percentages[media_type] = round((count / total_messages) * 100, 1)

        # Activity score (messages per day average)
        days_tracked = len(daily_stats) if daily_stats else 1
        avg_messages_per_day = round(total_messages / days_tracked, 1)

        return {
            'user_info': data['user_info'],
            'total_messages': total_messages,
            'recent_activity_7d': recent_activity,
            'avg_messages_per_day': avg_messages_per_day,
            'most_active_time': most_active_time,
            'media_stats': media_stats,
            'media_percentages': media_percentages,
            'activity_patterns': activity_patterns,
            'daily_stats': daily_stats,
            'last_seen': data['last_seen'],
            'recent_messages': data['messages']['recent'][-10:],  # Last 10 messages
            'days_tracked': days_tracked
        }

    async def resolve_target_user(self, client, event, args: str):
        """Resolve target user from argument or reply"""
        # Check reply first
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender:
                return reply_msg.sender

        # Check username argument
        if args:
            # Clean username
            username = args.strip().lstrip('@')

            try:
                user = await client.get_entity(username)
                return user
            except (UsernameNotOccupiedError, UsernameInvalidError, PeerIdInvalidError):
                return None

        return None

# Initialize monitor system
monitor_system = UserMonitorSystem()

async def is_owner_check(client, event):
    """Check if user is bot owner"""
    try:
        # Get sender ID from event properly
        sender_id = None
        if hasattr(event, 'sender_id') and event.sender_id:
            sender_id = event.sender_id
        elif hasattr(event, 'from_id') and event.from_id:
            sender_id = event.from_id.user_id if hasattr(event.from_id, 'user_id') else event.from_id
        elif event.sender:
            sender_id = event.sender.id

        if not sender_id:
            return False

        owner_id = os.getenv("OWNER_ID")
        if owner_id:
            return sender_id == int(owner_id)
        me = await client.get_me()
        return sender_id == me.id
    except Exception:
        return False

# Global client reference
client = None

# Background message tracker
async def message_tracker(event):
    """Background message tracking for all messages"""
    global client

    # Only track in groups
    if not (event.is_group or event.is_channel):
        return

    # Skip bot messages
    if not event.sender or getattr(event.sender, 'bot', False):
        return

    try:
        # Get sender ID properly
        sender_id = None
        if hasattr(event, 'sender_id') and event.sender_id:
            sender_id = event.sender_id
        elif hasattr(event, 'from_id') and event.from_id:
            sender_id = event.from_id.user_id if hasattr(event.from_id, 'user_id') else event.from_id
        elif event.sender:
            sender_id = event.sender.id

        if sender_id:
            # Track user activity
            await monitor_system.track_user_activity(sender_id, event.chat_id, event)
    except Exception as e:
        print(f"[Monitor] Tracking error: {e}")

async def monitor_handler(event):
    """User monitoring handler (.monitor)"""
    global client
    if not await is_owner_check(client, event):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Monitor commands only work in groups."
        )
        return

    # Get arguments
    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""

    # Resolve target user
    target_user = await monitor_system.resolve_target_user(client, event, args)

    if not target_user:
        usage_text = f"""{get_emoji('main')} {convert_font('USER ACTIVITY MONITOR', 'bold')}

{get_emoji('adder5')} {convert_font('No target specified!', 'bold')}

{get_emoji('main')} {convert_font('Usage:', 'bold')}
  • {convert_font('.monitor @username', 'mono')} - Monitor by username
  • Reply to user + {convert_font('.monitor', 'mono')} - Monitor by reply

{get_emoji('check')} {convert_font('Examples:', 'bold')}
  • {convert_font('.monitor @johndoe', 'mono')}
  • Reply to message + {convert_font('.monitor', 'mono')}

{get_emoji('adder1')} {convert_font('Note:', 'bold')} Tracking starts after first command use

{get_emoji('adder6')} VZL2 User Monitor System"""

        await safe_send_premium(event, usage_text)
        return

    # Show monitoring status
    monitoring_msg = await safe_send_premium(event,
        f"{get_emoji('check')} {convert_font('Analyzing User Activity...', 'bold')}\n\n"
        f"{get_emoji('adder4')} {convert_font('Target:', 'bold')} {convert_font(target_user.first_name, 'bold')}\n"
        f"{get_emoji('adder1')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}\n"
        f"{get_emoji('adder3')} {convert_font('Processing statistics...', 'bold')}"
    )

    # Get user statistics
    stats = monitor_system.get_user_statistics(target_user.id, event.chat_id)

    if not stats:
        await monitoring_msg.edit(
            f"{get_emoji('adder5')} {convert_font('No Activity Data!', 'bold')}\n\n"
            f"{get_emoji('adder3')} User has not sent any tracked messages yet\n"
            f"{get_emoji('adder1')} Monitoring will start from now on\n\n"
            f"{get_emoji('adder4')} {convert_font('Target User:', 'bold')} {convert_font(target_user.first_name, 'bold')}\n"
            f"{get_emoji('adder2')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}\n\n"
            f"{get_emoji('adder6')} VZL2 User Monitor System"
        )
        return

    # Format statistics
    user_info = stats['user_info']

    # Media stats breakdown
    media_breakdown = []
    for media_type, percentage in stats['media_percentages'].items():
        if percentage > 0:
            media_breakdown.append(f"{convert_font(media_type.title(), 'mono')}: {convert_font(f'{percentage}%', 'bold')}")

    media_text = " • ".join(media_breakdown[:5])  # Show top 5
    if len(media_breakdown) > 5:
        media_text += f" + {len(media_breakdown)-5} more"

    # Recent messages preview
    recent_preview = []
    for msg in stats['recent_messages'][-5:]:  # Last 5 messages
        msg_time = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
        msg_type = msg['media_type']
        preview = f"{msg_time} {convert_font(msg_type, 'mono')}"
        if msg['text_preview']:
            preview += f": {msg['text_preview'][:30]}..."
        recent_preview.append(preview)

    stats_text = f"""{get_emoji('main')} {convert_font('USER ACTIVITY STATISTICS', 'bold')}

{get_emoji('adder2')} {convert_font('User Info:', 'bold')}
  • Name: {convert_font(user_info.get('first_name', 'Unknown'), 'bold')}
  • Username: {convert_font(f"@{user_info.get('username')}" if user_info.get('username') else 'No username', 'mono')}
  • Premium: {convert_font('Yes' if user_info.get('is_premium') else 'No', 'mono')}

{get_emoji('check')} {convert_font('Activity Summary:', 'bold')}
  • Total Messages: {convert_font(str(stats['total_messages']), 'bold')}
  • Recent 7 Days: {convert_font(str(stats['recent_activity_7d']), 'bold')} messages
  • Daily Average: {convert_font(str(stats['avg_messages_per_day']), 'bold')} messages
  • Days Tracked: {convert_font(str(stats['days_tracked']), 'bold')} days

{get_emoji('adder4')} {convert_font('Activity Pattern:', 'bold')}
  • Most Active: {convert_font(stats['most_active_time'].title(), 'bold')} time
  • Last Seen: {convert_font(datetime.fromisoformat(stats['last_seen']).strftime('%Y-%m-%d %H:%M'), 'mono')}

{get_emoji('adder1')} {convert_font('Content Breakdown:', 'bold')}
  {media_text}

{get_emoji('adder3')} {convert_font('Recent Messages (Last 5):', 'bold')}"""

    for preview in recent_preview:
        stats_text += f"\n  • {preview}"

    stats_text += f"""

{get_emoji('adder6')} VZL2 User Monitor System
{get_emoji('adder5')} Use {convert_font('.stats @user', 'mono')} for detailed breakdown"""

    await monitoring_msg.edit(stats_text)
    print(f"[Monitor] Generated stats for user {target_user.id} - {stats['total_messages']} messages tracked")

async def stats_handler(event):
    """Detailed statistics handler (.stats)"""
    global client
    if not await is_owner_check(client, event):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Stats commands only work in groups."
        )
        return

    # Get arguments
    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""

    # Resolve target user
    target_user = await monitor_system.resolve_target_user(client, event, args)

    if not target_user:
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('No target specified!', 'bold')}\n\n"
            f"{get_emoji('adder1')} Use {convert_font('.stats @username', 'mono')} or reply + {convert_font('.stats', 'mono')}"
        )
        return

    # Get detailed statistics
    stats = monitor_system.get_user_statistics(target_user.id, event.chat_id)

    if not stats:
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('No Data Available!', 'bold')}\n\n"
            f"{get_emoji('adder3')} User has not sent any tracked messages"
        )
        return

    # Format detailed stats
    media_details = []
    for media_type, count in stats['media_stats'].items():
        if count > 0:
            percentage = stats['media_percentages'].get(media_type, 0)
            media_details.append(f"  • {convert_font(media_type.title(), 'bold')}: {convert_font(str(count), 'mono')} ({convert_font(f'{percentage}%', 'italic')})")

    activity_details = []
    for time_period, count in stats['activity_patterns'].items():
        if count > 0:
            percentage = round((count / stats['total_messages']) * 100, 1)
            activity_details.append(f"  • {convert_font(time_period.title(), 'bold')}: {convert_font(str(count), 'mono')} ({convert_font(f'{percentage}%', 'italic')})")

    detailed_text = f"""{get_emoji('main')} {convert_font('DETAILED USER STATISTICS', 'bold')}

{get_emoji('adder2')} {convert_font('Target User:', 'bold')} {convert_font(stats['user_info']['first_name'], 'bold')}

{get_emoji('check')} {convert_font('Media Breakdown:', 'bold')}
{chr(10).join(media_details)}

{get_emoji('adder4')} {convert_font('Time Patterns:', 'bold')}
{chr(10).join(activity_details)}

{get_emoji('adder1')} {convert_font('Daily Activity (Last 7 Days):', 'bold')}"""

    # Add recent daily stats
    recent_days = sorted(stats['daily_stats'].items(), key=lambda x: x[0])[-7:]
    for date_str, count in recent_days:
        date_obj = datetime.fromisoformat(date_str + 'T00:00:00')
        day_name = date_obj.strftime('%a')
        detailed_text += f"\n  • {convert_font(day_name, 'bold')} {convert_font(date_str[-5:], 'mono')}: {convert_font(str(count), 'bold')} messages"

    detailed_text += f"""

{get_emoji('adder3')} {convert_font('Summary Metrics:', 'bold')}
  • Average per day: {convert_font(str(stats['avg_messages_per_day']), 'bold')}
  • Peak activity: {convert_font(stats['most_active_time'].title(), 'bold')}
  • Tracking period: {convert_font(str(stats['days_tracked']), 'bold')} days

{get_emoji('adder6')} VZL2 Detailed Statistics"""

    await safe_send_premium(event, detailed_text)

def get_plugin_info():
    return PLUGIN_INFO

def setup(client_instance):
    """Setup function untuk register event handlers"""
    global client
    client = client_instance

    # Register monitoring commands
    client.add_event_handler(monitor_handler, events.NewMessage(pattern=r'\.monitor(?:\s+(.+))?$'))
    client.add_event_handler(stats_handler, events.NewMessage(pattern=r'\.stats(?:\s+(.+))?$'))

    # Register background message tracker
    client.add_event_handler(message_tracker, events.NewMessage())

    print(f"✅ [Monitor] User activity monitor loaded v{PLUGIN_INFO['version']} - .monitor/.stats commands + background tracking active")

def cleanup_plugin():
    """Cleanup plugin resources"""
    global client
    try:
        print("[Monitor] Plugin cleanup initiated")
        client = None
        print("[Monitor] Plugin cleanup completed")
    except Exception as e:
        print(f"[Monitor] Cleanup error: {e}")

# Export functions
__all__ = ['setup', 'cleanup_plugin', 'get_plugin_info', 'monitor_handler', 'stats_handler', 'message_tracker']