"""
VZL2 Event Icon Plugin - Custom Seasonal Profile Icons
Advanced event-based profile decoration dengan seasonal templates
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 1.0.0 - Premium Event Icon System
"""

from telethon import events, functions
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
import asyncio
import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VZL2 style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, PREMIUM_EMOJIS

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Plugin Info
PLUGIN_INFO = {
    "name": "eventicon",
    "version": "1.0.0",
    "description": "Custom seasonal profile icons untuk Halloween, Christmas, dll",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".eventicon", ".setevent", ".removeevent", ".eventlist", ".autoevent"],
    "features": ["seasonal icons", "auto profile change", "event templates", "custom overlays", "premium branding"]
}

__version__ = "1.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Event icon directory
EVENT_DIR = Path("downloads/eventicons")
EVENT_DIR.mkdir(parents=True, exist_ok=True)

# Storage untuk backup profile original
BACKUP_DIR = Path("downloads/eventicons/backup")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Event templates dengan tanggal otomatis
EVENT_TEMPLATES = {
    "halloween": {
        "name": "Halloween 2025",
        "dates": ["2025-10-25", "2025-11-05"],  # Active period
        "colors": ["#FF4500", "#000000", "#8B0000"],
        "overlay_type": "pumpkin",
        "emoji": "🎃",
        "description": "Spooky Halloween decoration dengan pumpkin overlay"
    },
    "christmas": {
        "name": "Christmas 2025",
        "dates": ["2025-12-20", "2025-12-26"],
        "colors": ["#DC143C", "#228B22", "#FFD700"],
        "overlay_type": "santa_hat",
        "emoji": "🎅",
        "description": "Festive Christmas dengan Santa hat decoration"
    },
    "newyear": {
        "name": "New Year 2026",
        "dates": ["2025-12-30", "2026-01-05"],
        "colors": ["#FFD700", "#FF69B4", "#00CED1"],
        "overlay_type": "fireworks",
        "emoji": "🎊",
        "description": "New Year celebration dengan fireworks effect"
    },
    "valentine": {
        "name": "Valentine's Day 2026",
        "dates": ["2026-02-10", "2026-02-16"],
        "colors": ["#FF1493", "#FFB6C1", "#DC143C"],
        "overlay_type": "hearts",
        "emoji": "💖",
        "description": "Romantic Valentine dengan hearts decoration"
    },
    "independence": {
        "name": "Indonesian Independence Day",
        "dates": ["2025-08-15", "2025-08-19"],
        "colors": ["#FF0000", "#FFFFFF"],
        "overlay_type": "flag",
        "emoji": "🇮🇩",
        "description": "Indonesian flag themed decoration"
    },
    "ramadan": {
        "name": "Ramadan 2026",
        "dates": ["2026-02-28", "2026-03-30"],  # Approximate
        "colors": ["#00CED1", "#FFD700", "#228B22"],
        "overlay_type": "crescent",
        "emoji": "🌙",
        "description": "Islamic Ramadan dengan crescent moon"
    },
    "birthday": {
        "name": "Custom Birthday",
        "dates": ["manual"],  # User sets manually
        "colors": ["#FF69B4", "#FFD700", "#32CD32"],
        "overlay_type": "cake",
        "emoji": "🎂",
        "description": "Birthday celebration dengan cake decoration"
    }
}

# Auto event settings storage
AUTO_EVENT_SETTINGS = {
    "enabled": False,
    "user_events": [],  # User subscribed events
    "check_interval": 3600,  # Check every hour
    "backup_original": True
}

class EventIconSystem:
    """Premium Event Icon Management System"""

    def __init__(self):
        self.settings_file = EVENT_DIR / "settings.json"
        self.load_settings()

    def load_settings(self):
        """Load auto event settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    AUTO_EVENT_SETTINGS.update(loaded)
        except Exception as e:
            print(f"[EventIcon] Error loading settings: {e}")

    def save_settings(self):
        """Save auto event settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(AUTO_EVENT_SETTINGS, f, indent=2)
        except Exception as e:
            print(f"[EventIcon] Error saving settings: {e}")

    def is_event_active(self, event_key: str) -> bool:
        """Check if event is currently active based on dates"""
        template = EVENT_TEMPLATES.get(event_key)
        if not template or template["dates"] == ["manual"]:
            return False

        today = datetime.now().strftime("%Y-%m-%d")
        start_date, end_date = template["dates"]
        return start_date <= today <= end_date

    def get_active_events(self) -> list:
        """Get list of currently active events"""
        active = []
        for key, template in EVENT_TEMPLATES.items():
            if self.is_event_active(key):
                active.append({
                    "key": key,
                    "name": template["name"],
                    "emoji": template["emoji"],
                    "description": template["description"]
                })
        return active

    async def backup_current_profile(self, client) -> str:
        """Backup current profile photo before changing"""
        try:
            me = await client.get_me()
            if me.photo:
                backup_path = BACKUP_DIR / f"original_profile_{me.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                await client.download_profile_photo(me, file=backup_path)
                return str(backup_path)
        except Exception as e:
            print(f"[EventIcon] Backup error: {e}")
        return None

    def create_overlay_decoration(self, overlay_type: str, size: tuple = (400, 400)):
        """Create overlay decoration based on type"""
        if not PIL_AVAILABLE:
            raise Exception("PIL/Pillow is required for overlay creation")

        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if overlay_type == "pumpkin":
            # Halloween pumpkin in corner
            x, y = size[0] - 80, 20
            draw.ellipse([x, y, x+60, y+60], fill=(255, 165, 0, 200))
            # Simple jack-o'-lantern face
            draw.ellipse([x+15, y+15, x+25, y+25], fill=(0, 0, 0, 255))  # Eye
            draw.ellipse([x+35, y+15, x+45, y+25], fill=(0, 0, 0, 255))  # Eye
            draw.arc([x+20, y+35, x+40, y+45], 0, 180, fill=(0, 0, 0, 255))  # Smile

        elif overlay_type == "santa_hat":
            # Christmas Santa hat
            x, y = size[0] - 100, 0
            # Hat triangle
            draw.polygon([(x+20, y), (x+80, y+60), (x+50, y+20)], fill=(220, 20, 60, 200))
            # Hat brim
            draw.ellipse([x+10, y+50, x+70, y+70], fill=(255, 255, 255, 200))
            # Pom pom
            draw.ellipse([x+15, y-5, x+35, y+15], fill=(255, 255, 255, 200))

        elif overlay_type == "fireworks":
            # New Year fireworks sparkles
            for _ in range(15):
                x = random.randint(0, size[0])
                y = random.randint(0, size[1]//2)
                color = random.choice([(255, 215, 0), (255, 105, 180), (0, 206, 209)])
                draw.ellipse([x-2, y-2, x+2, y+2], fill=color + (180,))
                # Sparkle lines
                draw.line([x-8, y, x+8, y], fill=color + (150,), width=1)
                draw.line([x, y-8, x, y+8], fill=color + (150,), width=1)

        elif overlay_type == "hearts":
            # Valentine hearts
            for _ in range(8):
                x = random.randint(20, size[0]-40)
                y = random.randint(20, size[1]-40)
                self.draw_heart(draw, x, y, random.randint(15, 25), (255, 20, 147, 150))

        elif overlay_type == "flag":
            # Indonesian flag corner
            x, y = 20, 20
            # Red stripe
            draw.rectangle([x, y, x+60, y+20], fill=(255, 0, 0, 200))
            # White stripe
            draw.rectangle([x, y+20, x+60, y+40], fill=(255, 255, 255, 200))

        elif overlay_type == "crescent":
            # Ramadan crescent moon
            x, y = size[0] - 80, 20
            # Main circle
            draw.ellipse([x, y, x+50, y+50], fill=(0, 206, 209, 200))
            # Cut out for crescent
            draw.ellipse([x+10, y+5, x+45, y+45], fill=(0, 0, 0, 0))

        elif overlay_type == "cake":
            # Birthday cake
            x, y = size[0] - 80, size[1] - 80
            # Cake base
            draw.rectangle([x+10, y+30, x+60, y+60], fill=(255, 192, 203, 200))
            # Candles
            for i in range(3):
                cx = x + 20 + (i * 15)
                draw.line([cx, y+20, cx, y+30], fill=(255, 215, 0, 255), width=3)
                # Flame
                draw.ellipse([cx-2, y+15, cx+2, y+23], fill=(255, 69, 0, 200))

        return overlay

    def draw_heart(self, draw, x, y, size, color):
        """Draw heart shape"""
        # Simple heart using circles and triangle
        r = size // 3
        draw.ellipse([x-r, y, x+r, y+2*r], fill=color)
        draw.ellipse([x, y, x+2*r, y+2*r], fill=color)
        draw.polygon([x-r, y+r, x+r, y+2*r, x+3*r, y+r], fill=color)

    async def create_event_profile(self, original_path: str, event_key: str) -> str:
        """Create event-themed profile photo"""
        if not PIL_AVAILABLE:
            raise Exception("PIL/Pillow is required for event icon creation")

        template = EVENT_TEMPLATES[event_key]

        # Load original photo
        original = Image.open(original_path).convert('RGBA')

        # Resize to standard size
        size = (400, 400)
        try:
            original = original.resize(size, Image.Resampling.LANCZOS)
        except AttributeError:
            # Fallback for older PIL versions
            original = original.resize(size, Image.LANCZOS)

        # Apply color filter for theme
        color_overlay = Image.new('RGBA', size, template["colors"][0] + (30,))
        original = Image.alpha_composite(original, color_overlay)

        # Add decoration overlay
        decoration = self.create_overlay_decoration(template["overlay_type"], size)
        final = Image.alpha_composite(original, decoration)

        # Add subtle border in theme colors
        border_color = template["colors"][0]
        border = ImageDraw.Draw(final)
        border.rectangle([0, 0, size[0]-1, size[1]-1], outline=border_color, width=3)

        # Save result
        result_path = EVENT_DIR / f"event_{event_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        final.convert('RGB').save(result_path, 'PNG', optimize=True)

        return str(result_path)

# Initialize event system
event_system = EventIconSystem()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('petir')}{get_emoji('adder1')}"
    print(f"✅ [EventIcon] Premium event icon system loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [EventIcon] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} EVENT ICON SYSTEM")

    # Check for active events on startup
    active_events = event_system.get_active_events()
    if active_events:
        print(f"🎉 [EventIcon] {len(active_events)} active events detected:")
        for event in active_events:
            print(f"   {event['emoji']} {event['name']}")

@events.register(events.NewMessage(pattern=r'\.eventlist'))
async def event_list_handler(event):
    """Show available events and their status"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        active_events = event_system.get_active_events()

        result_text = f"{get_emoji('utama')} AVAILABLE EVENT ICONS\n\n"

        if active_events:
            result_text += f"{get_emoji('centang')} Currently Active Events:\n"
            for evt in active_events:
                result_text += f"{evt['emoji']} {evt['name']}\n"
                result_text += f"   └ {evt['description']}\n\n"

        result_text += f"{get_emoji('telegram')} All Available Events:\n\n"

        for key, template in EVENT_TEMPLATES.items():
            status = "🟢 ACTIVE" if event_system.is_event_active(key) else "⚪ Inactive"
            result_text += f"{template['emoji']} {template['name']}\n"
            result_text += f"   └ Status: {status}\n"
            result_text += f"   └ {template['description']}\n"
            if template['dates'] != ['manual']:
                result_text += f"   └ Period: {template['dates'][0]} to {template['dates'][1]}\n"
            result_text += "\n"

        result_text += f"{get_emoji('aktif')} Commands:\n"
        result_text += f".setevent <event> - Set event icon\n"
        result_text += f".removeevent - Remove event icon\n"
        result_text += f".autoevent on/off - Toggle auto events\n\n"
        result_text += f"{get_emoji('adder1')} VZL2 Event Icon System"

        await safe_send_premium(event, result_text)

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.setevent(?:\s+(.+))?'))
async def set_event_handler(event):
    """Set event icon for profile"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        if not PIL_AVAILABLE:
            error_msg = f"{get_emoji('merah')} PIL/Pillow required!\n\n"
            error_msg += f"{get_emoji('kuning')} Install: pip install pillow\n\n"
            error_msg += f"{get_emoji('telegram')} VZL2 Event Icon System"
            await safe_send_premium(event, error_msg)
            return

        event_key = event.pattern_match.group(1)
        if not event_key:
            await safe_send_premium(event, f"{get_emoji('kuning')} Usage: .setevent <event_name>\n\nUse .eventlist to see available events")
            return

        event_key = event_key.strip().lower()
        if event_key not in EVENT_TEMPLATES:
            await safe_send_premium(event, f"{get_emoji('merah')} Event '{event_key}' not found!\n\nUse .eventlist to see available events")
            return

        template = EVENT_TEMPLATES[event_key]

        processing_msg = await safe_send_premium(event, f"{get_emoji('loading')} Setting {template['name']} icon...")

        try:
            # Backup current profile
            await safe_edit_premium(processing_msg, f"{get_emoji('proses')} Backing up current profile...")
            backup_path = await event_system.backup_current_profile(event.client)

            # Download current profile for processing
            me = await event.client.get_me()
            if not me.photo:
                await safe_edit_premium(processing_msg, f"{get_emoji('merah')} No profile photo to decorate!\n\nSet a profile photo first, then use this command.")
                return

            temp_path = EVENT_DIR / f"temp_current_{me.id}.jpg"
            await event.client.download_profile_photo(me, file=temp_path)

            # Create event-themed version
            await safe_edit_premium(processing_msg, f"{get_emoji('loading')} Creating {template['name']} decoration...")
            event_photo_path = await event_system.create_event_profile(str(temp_path), event_key)

            # Upload new profile photo
            await safe_edit_premium(processing_msg, f"{get_emoji('petir')} Uploading new profile...")

            with open(event_photo_path, 'rb') as f:
                uploaded_file = await event.client.upload_file(f, file_name=f"event_{event_key}.png")
                await event.client(UploadProfilePhotoRequest(file=uploaded_file))

            success_msg = f"{get_emoji('centang')} Event Icon Set Successfully!\n\n"
            success_msg += f"{template['emoji']} Event: {template['name']}\n"
            success_msg += f"{get_emoji('aktif')} Style: {template['overlay_type'].title()}\n"
            success_msg += f"{get_emoji('proses')} Theme: {', '.join(template['colors'][:2])}\n\n"
            if backup_path:
                success_msg += f"{get_emoji('kuning')} Original backed up\n"
            success_msg += f"{get_emoji('telegram')} Use .removeevent to restore\n\n"
            success_msg += f"{get_emoji('adder1')} VZL2 Event Icon System"

            await safe_edit_premium(processing_msg, success_msg)

            # Cleanup temp files
            try:
                os.remove(temp_path)
                # Keep event photo for reference
            except:
                pass

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Failed to set event icon!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Event Icon System"
            )

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.removeevent'))
async def remove_event_handler(event):
    """Remove event icon and restore backup if available"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        processing_msg = await safe_send_premium(event, f"{get_emoji('loading')} Removing event icon...")

        try:
            # Find most recent backup
            me = await event.client.get_me()
            backup_files = list(BACKUP_DIR.glob(f"original_profile_{me.id}_*.jpg"))

            if backup_files:
                # Get most recent backup
                latest_backup = max(backup_files, key=os.path.getctime)

                await safe_edit_premium(processing_msg, f"{get_emoji('proses')} Restoring original profile...")

                # Upload backup as new profile
                with open(latest_backup, 'rb') as f:
                    uploaded_file = await event.client.upload_file(f, file_name="restored_profile.jpg")
                    await event.client(UploadProfilePhotoRequest(file=uploaded_file))

                success_msg = f"{get_emoji('centang')} Event Icon Removed!\n\n"
                success_msg += f"{get_emoji('aktif')} Original profile restored\n"
                success_msg += f"{get_emoji('kuning')} Backup used: {latest_backup.name}\n\n"
                success_msg += f"{get_emoji('telegram')} VZL2 Event Icon System"

                await safe_edit_premium(processing_msg, success_msg)

                # Clean up old backups (keep only 3 most recent)
                backup_files = sorted(BACKUP_DIR.glob(f"original_profile_{me.id}_*.jpg"),
                                    key=os.path.getctime, reverse=True)
                for old_backup in backup_files[3:]:
                    try:
                        os.remove(old_backup)
                    except:
                        pass

            else:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('kuning')} No backup found!\n\n"
                    f"{get_emoji('telegram')} Manual profile change needed\n\n"
                    f"{get_emoji('adder1')} VZL2 Event Icon System"
                )

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Failed to remove event icon!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Event Icon System"
            )

        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator