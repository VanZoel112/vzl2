"""
VZL2 User Monitor Plugin - Group Activity Tracking & Statistics
Advanced user activity monitoring with message and media statistics
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 1.0.0 - Premium Monitor System
"""

from telethon import events
from telethon.tl.types import (
    MessageEntityCustomEmoji, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeSticker, DocumentAttributeVideo, DocumentAttributeAudio,
    MessageMediaWebPage, DocumentAttributeAnimated
)
from telethon.errors import (
    UsernameNotOccupiedError, UsernameInvalidError, PeerIdInvalidError
)
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VZL2 style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "monitor",
    "version": "1.0.0",
    "description": "Premium user activity monitoring dan statistics in groups",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".monitor", ".stats"],
    "features": ["user tracking", "message statistics", "media analysis", "activity patterns"]
}

__version__ = "1.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

class MonitorSystem:
    """Premium User Activity Monitoring System"""

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

        # Update statistics
        self.monitoring_data[user_key]['total_messages'] += 1
        self.monitoring_data[user_key]['media_stats'][media_type] += 1
        self.monitoring_data[user_key]['activity_patterns'][time_period] += 1
        self.monitoring_data[user_key]['message_types'][media_type] += 1
        self.monitoring_data[user_key]['last_seen'] = timestamp.isoformat()

        # Daily stats
        date_key = timestamp.strftime('%Y-%m-%d')
        self.monitoring_data[user_key]['daily_stats'][date_key] += 1

        # Store recent messages (last 20)
        message_data = {
            'id': message.id,
            'timestamp': timestamp.isoformat(),
            'media_type': media_type,
            'content_length': len(message.text) if message.text else 0,
            'has_media': bool(message.media),
            'is_forwarded': bool(message.forward),
            'is_reply': bool(message.reply_to_msg_id),
            'text_preview': (message.text[:30] + '...') if message.text and len(message.text) > 30 else (message.text or '')
        }

        self.monitoring_data[user_key]['messages']['recent'].append(message_data)

        # Keep only last 20 messages
        if len(self.monitoring_data[user_key]['messages']['recent']) > 20:
            self.monitoring_data[user_key]['messages']['recent'] = \
                self.monitoring_data[user_key]['messages']['recent'][-20:]

    def get_user_statistics(self, user_id: int, chat_id: int) -> dict:
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
            'recent_messages': data['messages']['recent'][-5:],  # Last 5 messages
            'days_tracked': days_tracked
        }

    async def resolve_user(self, client, event, args: str):
        """Resolve target user dari argument atau reply"""
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender:
                return reply_msg.sender

        if args:
            username = args.strip().lstrip('@')
            try:
                user = await client.get_entity(username)
                return user
            except:
                return None
        return None

# Initialize monitor system
monitor_system = MonitorSystem()

# Background message tracker - register as NewMessage without pattern to catch all
@events.register(events.NewMessage())
async def message_tracker(event):
    """Background message tracking for all messages"""

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
        # Silent tracking - don't spam logs
        pass

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('proses')}{get_emoji('aktif')}"
    print(f"✅ [Monitor] Premium user monitor loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [Monitor] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} MONITOR SYSTEM")

@events.register(events.NewMessage(pattern=r'\.monitor'))
async def monitor_handler(event):
    """User monitoring handler (.monitor)"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Monitor commands only work in groups.\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
    target_user = await monitor_system.resolve_user(vzoel_client, event, args)

    if not target_user:
        await safe_send_premium(event,
            f"{get_emoji('utama')} **USER ACTIVITY MONITOR**\n\n"
            f"{get_emoji('merah')} **No target specified!**\n\n"
            f"{get_emoji('utama')} **Usage:**\n"
            f"  • `.monitor @username` - Monitor by username\n"
            f"  • Reply to user + `.monitor` - Monitor by reply\n\n"
            f"{get_emoji('centang')} **Examples:**\n"
            f"  • `.monitor @johndoe`\n"
            f"  • Reply to message + `.monitor`\n\n"
            f"{get_emoji('loading')} **Note:** Tracking starts after first command use\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    monitoring_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Analyzing User Activity...**\n\n"
        f"{get_emoji('proses')} **Target:** {target_user.first_name}\n"
        f"{get_emoji('loading')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n"
        f"{get_emoji('kuning')} **Processing statistics...**"
    )

    stats = monitor_system.get_user_statistics(target_user.id, event.chat_id)

    if not stats:
        await safe_edit_premium(monitoring_msg,
            f"{get_emoji('merah')} **No Activity Data!**\n\n"
            f"{get_emoji('kuning')} User has not sent any tracked messages yet\n"
            f"{get_emoji('loading')} Monitoring will start from now on\n\n"
            f"{get_emoji('proses')} **Target User:** {target_user.first_name}\n"
            f"{get_emoji('aktif')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    user_info = stats['user_info']

    # Media breakdown
    media_breakdown = []
    for media_type, percentage in stats['media_percentages'].items():
        if percentage > 0:
            media_breakdown.append(f"`{media_type.title()}`: **{percentage}%**")

    media_text = " • ".join(media_breakdown[:4])  # Show top 4
    if len(media_breakdown) > 4:
        media_text += f" + {len(media_breakdown)-4} more"

    # Recent messages preview
    recent_preview = []
    for msg in stats['recent_messages'][-3:]:  # Last 3 messages
        msg_time = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
        msg_type = msg['media_type']
        preview = f"`{msg_time}` *{msg_type}*"
        if msg['text_preview']:
            preview += f": {msg['text_preview'][:25]}..."
        recent_preview.append(preview)

    stats_text = f"{get_emoji('utama')} **USER ACTIVITY STATISTICS**\n\n"
    stats_text += f"{get_emoji('aktif')} **User Info:**\n"
    stats_text += f"  • Name: **{user_info.get('first_name', 'Unknown')}**\n"
    stats_text += f"  • Username: `@{user_info.get('username')}` " if user_info.get('username') else "  • Username: `No username`\n"
    stats_text += f"  • Premium: `{'Yes' if user_info.get('is_premium') else 'No'}`\n\n"

    stats_text += f"{get_emoji('centang')} **Activity Summary:**\n"
    stats_text += f"  • Total Messages: **{stats['total_messages']}**\n"
    stats_text += f"  • Recent 7 Days: **{stats['recent_activity_7d']}** messages\n"
    stats_text += f"  • Daily Average: **{stats['avg_messages_per_day']}** messages\n"
    stats_text += f"  • Days Tracked: **{stats['days_tracked']}** days\n\n"

    stats_text += f"{get_emoji('proses')} **Activity Pattern:**\n"
    stats_text += f"  • Most Active: **{stats['most_active_time'].title()}** time\n"
    stats_text += f"  • Last Seen: `{datetime.fromisoformat(stats['last_seen']).strftime('%Y-%m-%d %H:%M')}`\n\n"

    stats_text += f"{get_emoji('loading')} **Content Breakdown:**\n"
    stats_text += f"  {media_text}\n\n"

    stats_text += f"{get_emoji('kuning')} **Recent Messages (Last 3):**\n"
    for preview in recent_preview:
        stats_text += f"  • {preview}\n"

    stats_text += f"\n{get_emoji('telegram')} VZL2 Monitor System\n"
    stats_text += f"{get_emoji('merah')} Use `.stats @user` for detailed breakdown"

    await safe_edit_premium(monitoring_msg, stats_text)

@events.register(events.NewMessage(pattern=r'\.stats'))
async def stats_handler(event):
    """Detailed statistics handler (.stats)"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Stats commands only work in groups.\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
    target_user = await monitor_system.resolve_user(vzoel_client, event, args)

    if not target_user:
        await safe_send_premium(event,
            f"{get_emoji('merah')} **No target specified!**\n\n"
            f"{get_emoji('loading')} Use `.stats @username` or reply + `.stats`\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    stats = monitor_system.get_user_statistics(target_user.id, event.chat_id)

    if not stats:
        await safe_send_premium(event,
            f"{get_emoji('merah')} **No Data Available!**\n\n"
            f"{get_emoji('kuning')} User has not sent any tracked messages\n\n"
            f"{get_emoji('telegram')} VZL2 Monitor System"
        )
        return

    # Format detailed stats
    media_details = []
    for media_type, count in stats['media_stats'].items():
        if count > 0:
            percentage = stats['media_percentages'].get(media_type, 0)
            media_details.append(f"  • **{media_type.title()}:** `{count}` (**{percentage}%**)")

    activity_details = []
    for time_period, count in stats['activity_patterns'].items():
        if count > 0:
            percentage = round((count / stats['total_messages']) * 100, 1)
            activity_details.append(f"  • **{time_period.title()}:** `{count}` (**{percentage}%**)")

    detailed_text = f"{get_emoji('utama')} **DETAILED USER STATISTICS**\n\n"
    detailed_text += f"{get_emoji('aktif')} **Target User:** **{stats['user_info']['first_name']}**\n\n"

    detailed_text += f"{get_emoji('centang')} **Media Breakdown:**\n"
    detailed_text += "\n".join(media_details[:6])  # Show max 6 types
    detailed_text += "\n\n"

    detailed_text += f"{get_emoji('proses')} **Time Patterns:**\n"
    detailed_text += "\n".join(activity_details)
    detailed_text += "\n\n"

    detailed_text += f"{get_emoji('loading')} **Daily Activity (Last 7 Days):**\n"
    recent_days = sorted(stats['daily_stats'].items(), key=lambda x: x[0])[-7:]
    for date_str, count in recent_days:
        date_obj = datetime.fromisoformat(date_str + 'T00:00:00')
        day_name = date_obj.strftime('%a')
        detailed_text += f"  • **{day_name}** `{date_str[-5:]}`: **{count}** messages\n"

    detailed_text += f"\n{get_emoji('kuning')} **Summary Metrics:**\n"
    detailed_text += f"  • Average per day: **{stats['avg_messages_per_day']}**\n"
    detailed_text += f"  • Peak activity: **{stats['most_active_time'].title()}**\n"
    detailed_text += f"  • Tracking period: **{stats['days_tracked']}** days\n\n"

    detailed_text += f"{get_emoji('telegram')} VZL2 Detailed Statistics"

    await safe_send_premium(event, detailed_text)