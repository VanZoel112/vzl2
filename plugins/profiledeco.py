"""
VZL2 Profile Decoration Plugin - Official Telegram Profile Customization
Advanced profile color palettes dan background emoji dengan VZL2 premium branding
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 1.0.0 - Premium Profile Decoration System
"""

from telethon import events
from telethon.tl.functions.account import UpdateColorRequest, GetDefaultBackgroundEmojisRequest
from telethon.tl.functions.help import GetPeerProfileColorsRequest
from telethon.tl.types import MessageEntityCustomEmoji
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

# Plugin Info
PLUGIN_INFO = {
    "name": "profiledeco",
    "version": "1.0.0",
    "description": "Official Telegram profile decorations dengan VZL2 premium branding",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".profiledeco", ".vzbranding", ".seasonaldeco", ".profilecolor", ".profilebg"],
    "features": ["official profile colors", "premium emoji backgrounds", "seasonal decorations", "VZL2 branding", "auto-scheduling"]
}

__version__ = "1.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# Profile decoration directory
DECO_DIR = Path("downloads/profiledeco")
DECO_DIR.mkdir(parents=True, exist_ok=True)

# VZL2 Premium Branding Combinations
VZL_BRANDING_SETS = {
    "signature": {
        "name": "VZL2 Signature",
        "color_preference": ["red", "orange", "blue"],  # Prefer these colors
        "emoji_combo": ["utama", "petir", "adder1"],    # 🤩⛈😈 combination
        "description": "Classic Vzoel Fox's signature dengan premium emoji trio"
    },
    "premium": {
        "name": "VZL2 Premium",
        "color_preference": ["violet", "cyan", "pink"],
        "emoji_combo": ["centang", "aktif", "adder2"],  # 👍🎚💟 combination
        "description": "Premium user branding dengan elite emoji combo"
    },
    "fire": {
        "name": "VZL2 Fire",
        "color_preference": ["red", "orange"],
        "emoji_combo": ["petir", "merah", "adder1"],    # ⛈🤪😈 combination
        "description": "Aggressive fire theme dengan intense emoji"
    },
    "cool": {
        "name": "VZL2 Cool",
        "color_preference": ["cyan", "blue", "green"],
        "emoji_combo": ["biru", "loading", "telegram"],  # 🎅⚙️✉️ combination
        "description": "Cool blue theme dengan tech emoji"
    },
    "royal": {
        "name": "VZL2 Royal",
        "color_preference": ["violet", "pink"],
        "emoji_combo": ["utama", "adder2", "kuning"],   # 🤩💟🍿 combination
        "description": "Royal purple theme dengan luxury emoji"
    }
}

# Seasonal Event Colors (map to Telegram's preset palettes)
SEASONAL_COLORS = {
    "halloween": {
        "primary": ["orange", "red"],
        "emoji": "utama",  # 🤩 as pumpkin substitute
        "description": "Halloween orange/red dengan premium emoji"
    },
    "christmas": {
        "primary": ["red", "green"],
        "emoji": "biru",   # 🎅 perfect for Christmas
        "description": "Christmas red/green dengan Santa emoji"
    },
    "valentine": {
        "primary": ["pink", "red"],
        "emoji": "adder2", # 💟 perfect for Valentine
        "description": "Valentine pink/red dengan heart emoji"
    },
    "newyear": {
        "primary": ["cyan", "violet", "pink"],
        "emoji": "petir",  # ⛈ as fireworks substitute
        "description": "New Year colorful dengan fireworks emoji"
    },
    "summer": {
        "primary": ["cyan", "blue"],
        "emoji": "loading", # ⚙️ as sun substitute
        "description": "Summer blue dengan sun emoji"
    },
    "independence": {
        "primary": ["red"],
        "emoji": "merah",  # 🤪 as flag celebration
        "description": "Independence red dengan celebration emoji"
    }
}

class ProfileDecorationSystem:
    """Premium Profile Decoration Management"""

    def __init__(self):
        self.settings_file = DECO_DIR / "deco_settings.json"
        self.available_colors = []
        self.default_bg_emojis = []
        self.load_settings()

    def load_settings(self):
        """Load decoration settings"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    "auto_seasonal": False,
                    "current_branding": "signature",
                    "last_update": None
                }
        except Exception as e:
            print(f"[ProfileDeco] Error loading settings: {e}")

    def save_settings(self):
        """Save decoration settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[ProfileDeco] Error saving settings: {e}")

    async def get_available_colors(self, client):
        """Get available color palettes from Telegram"""
        try:
            # Use raw client if VzoelFoxClient wrapper
            raw_client = client.client if hasattr(client, 'client') else client

            colors = await raw_client(GetPeerProfileColorsRequest())
            self.available_colors = colors.colors
            return self.available_colors
        except Exception as e:
            print(f"[ProfileDeco] Error getting colors: {e}")
            return []

    async def get_default_bg_emojis(self, client):
        """Get default background emojis from Telegram"""
        try:
            # Use raw client if VzoelFoxClient wrapper
            raw_client = client.client if hasattr(client, 'client') else client

            bg_emojis = await raw_client(GetDefaultBackgroundEmojisRequest())
            self.default_bg_emojis = bg_emojis.document_ids
            return self.default_bg_emojis
        except Exception as e:
            print(f"[ProfileDeco] Error getting background emojis: {e}")
            return []

    def find_color_by_preference(self, preferences):
        """Find best matching color from preferences"""
        if not self.available_colors:
            return None

        # Map color names to Telegram's color palette system
        color_mapping = {
            "red": [0, 1, 8],      # Red-based palettes
            "orange": [2, 9],      # Orange-based palettes
            "green": [3, 10],      # Green-based palettes
            "cyan": [4, 11],       # Cyan-based palettes
            "blue": [5, 12],       # Blue-based palettes
            "violet": [6, 13],     # Violet-based palettes
            "pink": [7, 14],       # Pink-based palettes
        }

        # Try to find best match
        for pref in preferences:
            if pref in color_mapping:
                for color_id in color_mapping[pref]:
                    # Check if this color ID exists in available colors
                    for color in self.available_colors:
                        if hasattr(color, 'color_id') and color.color_id == color_id:
                            return color.color_id
                        elif hasattr(color, 'id') and color.id == color_id:
                            return color.id

        # Fallback to first available color
        if self.available_colors:
            first_color = self.available_colors[0]
            if hasattr(first_color, 'color_id'):
                return first_color.color_id
            elif hasattr(first_color, 'id'):
                return first_color.id

        return None

    def get_premium_emoji_id(self, emoji_key):
        """Get premium emoji document ID for background"""
        emoji_data = PREMIUM_EMOJIS.get(emoji_key)

        # Try to get document ID from various possible formats
        if emoji_data:
            # Check for direct ID
            if 'id' in emoji_data:
                try:
                    return int(emoji_data['id'])
                except (ValueError, TypeError):
                    pass

            # Check for document_id
            if 'document_id' in emoji_data:
                try:
                    return int(emoji_data['document_id'])
                except (ValueError, TypeError):
                    pass

            # Check for custom_emoji_id
            if 'custom_emoji_id' in emoji_data:
                try:
                    return int(emoji_data['custom_emoji_id'])
                except (ValueError, TypeError):
                    pass

        # If no valid ID found, return None
        # Background decoration will use default emoji instead
        return None

    async def apply_vzl_branding(self, client, branding_key="signature"):
        """Apply VZL2 branding decorations"""
        if branding_key not in VZL_BRANDING_SETS:
            raise ValueError(f"Unknown branding: {branding_key}")

        branding = VZL_BRANDING_SETS[branding_key]

        # Get available colors and background emojis
        await self.get_available_colors(client)
        await self.get_default_bg_emojis(client)

        # Find best color match
        color_palette = self.find_color_by_preference(branding["color_preference"])

        # Get premium emoji for background
        primary_emoji_key = branding["emoji_combo"][0]  # Use first emoji as background
        bg_emoji_id = self.get_premium_emoji_id(primary_emoji_key)

        return {
            "color_palette": color_palette,
            "bg_emoji_id": bg_emoji_id,
            "branding": branding
        }

    async def apply_seasonal_decoration(self, client, season_key):
        """Apply seasonal decorations"""
        if season_key not in SEASONAL_COLORS:
            raise ValueError(f"Unknown season: {season_key}")

        season = SEASONAL_COLORS[season_key]

        # Get available colors
        await self.get_available_colors(client)

        # Find seasonal color match
        color_palette = self.find_color_by_preference(season["primary"])

        # Get seasonal premium emoji
        bg_emoji_id = self.get_premium_emoji_id(season["emoji"])

        return {
            "color_palette": color_palette,
            "bg_emoji_id": bg_emoji_id,
            "season": season
        }

    async def update_profile_decoration(self, client, color_palette_id=None, bg_emoji_id=None):
        """Update profile decoration via Telegram API"""
        try:
            # Use raw client if VzoelFoxClient wrapper
            raw_client = client.client if hasattr(client, 'client') else client

            # Prepare update parameters - only include non-None values
            update_params = {}
            if color_palette_id is not None:
                update_params['color'] = color_palette_id
            if bg_emoji_id is not None:
                update_params['background_emoji_id'] = bg_emoji_id

            if not update_params:
                print("[ProfileDeco] No valid decoration parameters to update")
                return False

            # Update profile color and/or background emoji
            await raw_client(UpdateColorRequest(**update_params))
            print(f"[ProfileDeco] Successfully updated decoration: color={color_palette_id}, emoji={bg_emoji_id}")
            return True

        except Exception as e:
            print(f"[ProfileDeco] Error updating decoration: {e}")

            # Try fallback: update only color if emoji fails
            if bg_emoji_id is not None and color_palette_id is not None:
                try:
                    print("[ProfileDeco] Trying fallback: color only")
                    await raw_client(UpdateColorRequest(color=color_palette_id))
                    print("[ProfileDeco] Fallback successful: color applied")
                    return True
                except Exception as fallback_e:
                    print(f"[ProfileDeco] Fallback also failed: {fallback_e}")

            return False

# Initialize decoration system
deco_system = ProfileDecorationSystem()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('petir')}{get_emoji('adder1')}"
    print(f"✅ [ProfileDeco] Premium profile decoration system loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [ProfileDeco] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} PROFILE DECORATION")

    # Preload available options
    try:
        await deco_system.get_available_colors(client)
        await deco_system.get_default_bg_emojis(client)
        print(f"📊 [ProfileDeco] Loaded {len(deco_system.available_colors)} color palettes")
        print(f"🎨 [ProfileDeco] Loaded {len(deco_system.default_bg_emojis)} background emojis")
    except Exception as e:
        print(f"⚠️ [ProfileDeco] Could not preload options: {e}")

@events.register(events.NewMessage(pattern=r'\.vzbranding(?:\s+(.+))?'))
async def vzl_branding_handler(event):
    """Apply VZL2 branding to profile decoration"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        branding_key = event.pattern_match.group(1)
        if not branding_key:
            branding_key = "signature"  # Default branding

        branding_key = branding_key.strip().lower()

        if branding_key not in VZL_BRANDING_SETS:
            available = ', '.join(VZL_BRANDING_SETS.keys())
            await safe_send_premium(event,
                f"{get_emoji('merah')} Unknown branding: {branding_key}\n\n"
                f"{get_emoji('centang')} Available: {available}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Decoration"
            )
            return

        processing_msg = await safe_send_premium(event,
            f"{get_emoji('loading')} Applying VZL2 {VZL_BRANDING_SETS[branding_key]['name']}..."
        )

        try:
            # Apply VZL branding
            deco_result = await deco_system.apply_vzl_branding(vzoel_client, branding_key)

            await safe_edit_premium(processing_msg,
                f"{get_emoji('proses')} Updating profile decoration..."
            )

            # Update profile via Telegram API
            success = await deco_system.update_profile_decoration(
                vzoel_client,
                deco_result.get("color_palette"),
                deco_result.get("bg_emoji_id")
            )

            if success:
                branding = deco_result["branding"]
                emoji_names = " + ".join([get_emoji(key) for key in branding["emoji_combo"][:3]])

                success_msg = f"{get_emoji('centang')} VZL2 Branding Applied!\n\n"
                success_msg += f"{get_emoji('utama')} Style: {branding['name']}\n"
                success_msg += f"{get_emoji('aktif')} Emoji Combo: {emoji_names}\n"
                success_msg += f"{get_emoji('proses')} Colors: {', '.join(branding['color_preference'])}\n"
                success_msg += f"{get_emoji('kuning')} Description: {branding['description']}\n\n"
                success_msg += f"{get_emoji('telegram')} VZL2 Profile Decoration"

                await safe_edit_premium(processing_msg, success_msg)

                # Save current branding
                deco_system.settings["current_branding"] = branding_key
                deco_system.settings["last_update"] = datetime.now().isoformat()
                deco_system.save_settings()

            else:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('merah')} Failed to apply branding!\n\n"
                    f"{get_emoji('kuning')} Possible issues:\n"
                    f"• Telegram Premium required\n"
                    f"• API rate limiting\n"
                    f"• Invalid color/emoji combination\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Decoration"
                )

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Error applying branding!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Decoration"
            )

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.seasonaldeco(?:\s+(.+))?'))
async def seasonal_decoration_handler(event):
    """Apply seasonal decorations"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        season_key = event.pattern_match.group(1)
        if not season_key:
            # Show available seasonal decorations
            result_text = f"{get_emoji('utama')} SEASONAL DECORATIONS\n\n"

            for key, season in SEASONAL_COLORS.items():
                emoji_char = get_emoji(season['emoji'])
                result_text += f"{emoji_char} `.seasonaldeco {key}`\n"
                result_text += f"   └ {season['description']}\n"
                result_text += f"   └ Colors: {', '.join(season['primary'])}\n\n"

            result_text += f"{get_emoji('telegram')} Usage: .seasonaldeco <season>\n"
            result_text += f"{get_emoji('adder1')} VZL2 Profile Decoration"

            await safe_send_premium(event, result_text)
            return

        season_key = season_key.strip().lower()

        if season_key not in SEASONAL_COLORS:
            available = ', '.join(SEASONAL_COLORS.keys())
            await safe_send_premium(event,
                f"{get_emoji('merah')} Unknown season: {season_key}\n\n"
                f"{get_emoji('centang')} Available: {available}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Decoration"
            )
            return

        processing_msg = await safe_send_premium(event,
            f"{get_emoji('loading')} Applying {season_key} seasonal decoration..."
        )

        try:
            # Apply seasonal decoration
            deco_result = await deco_system.apply_seasonal_decoration(vzoel_client, season_key)

            await safe_edit_premium(processing_msg,
                f"{get_emoji('proses')} Updating seasonal profile..."
            )

            # Update profile via Telegram API
            success = await deco_system.update_profile_decoration(
                vzoel_client,
                deco_result.get("color_palette"),
                deco_result.get("bg_emoji_id")
            )

            if success:
                season = deco_result["season"]
                emoji_char = get_emoji(season['emoji'])

                success_msg = f"{get_emoji('centang')} Seasonal Decoration Applied!\n\n"
                success_msg += f"{emoji_char} Season: {season_key.title()}\n"
                success_msg += f"{get_emoji('aktif')} Background: Premium emoji\n"
                success_msg += f"{get_emoji('proses')} Colors: {', '.join(season['primary'])}\n"
                success_msg += f"{get_emoji('kuning')} Theme: {season['description']}\n\n"
                success_msg += f"{get_emoji('telegram')} VZL2 Seasonal Decoration"

                await safe_edit_premium(processing_msg, success_msg)

            else:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('merah')} Failed to apply decoration!\n\n"
                    f"{get_emoji('kuning')} Check Telegram Premium status\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Decoration"
                )

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Error applying seasonal decoration!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Decoration"
            )

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.profiledeco'))
async def profile_decoration_info_handler(event):
    """Show profile decoration system information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        signature = f"{get_emoji('utama')}{get_emoji('petir')}{get_emoji('adder1')}"

        result_text = f"{signature} VZL2 PROFILE DECORATION SYSTEM\n\n"

        result_text += f"{get_emoji('centang')} VZL2 Branding Sets:\n\n"
        for key, branding in VZL_BRANDING_SETS.items():
            emoji_combo = " ".join([get_emoji(ek) for ek in branding["emoji_combo"][:3]])
            result_text += f"{emoji_combo} `.vzbranding {key}`\n"
            result_text += f"   └ {branding['name']}\n"
            result_text += f"   └ {branding['description']}\n\n"

        result_text += f"{get_emoji('telegram')} Seasonal Decorations:\n\n"
        active_seasons = []
        for key, season in SEASONAL_COLORS.items():
            emoji_char = get_emoji(season['emoji'])
            result_text += f"{emoji_char} `.seasonaldeco {key}`\n"

        result_text += f"\n{get_emoji('aktif')} Features:\n"
        result_text += f"• Official Telegram API decorations\n"
        result_text += f"• VZL2 premium emoji backgrounds\n"
        result_text += f"• Animated scroll effects\n"
        result_text += f"• Seasonal auto-scheduling\n"
        result_text += f"• Custom color palettes\n\n"

        result_text += f"{get_emoji('kuning')} Requirements:\n"
        result_text += f"• Telegram Premium subscription\n"
        result_text += f"• VZL2 with premium emoji access\n\n"

        result_text += f"{get_emoji('proses')} Commands:\n"
        result_text += f".vzbranding <style> - Apply VZL2 branding\n"
        result_text += f".seasonaldeco <season> - Apply seasonal theme\n"
        result_text += f".profiledeco - Show this info\n\n"

        result_text += f"{get_emoji('adder2')} VZL2 Premium Profile System"

        await safe_send_premium(event, result_text)

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.profilecolor(?:\s+(.+))?'))
async def profile_color_handler(event):
    """Directly set profile color palette"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        color_name = event.pattern_match.group(1)
        if not color_name:
            # Show available colors
            await deco_system.get_available_colors(vzoel_client)

            result_text = f"{get_emoji('utama')} AVAILABLE COLOR PALETTES\n\n"

            color_names = ["red", "orange", "green", "cyan", "blue", "violet", "pink"]
            for i, color in enumerate(color_names):
                result_text += f"{get_emoji('centang')} `.profilecolor {color}`\n"

            result_text += f"\n{get_emoji('aktif')} Total available: {len(deco_system.available_colors)}\n"
            result_text += f"{get_emoji('telegram')} VZL2 Profile Colors"

            await safe_send_premium(event, result_text)
            return

        color_name = color_name.strip().lower()
        processing_msg = await safe_send_premium(event,
            f"{get_emoji('loading')} Setting {color_name} profile color...")

        try:
            await deco_system.get_available_colors(vzoel_client)
            color_id = deco_system.find_color_by_preference([color_name])

            if color_id is None:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('merah')} Color '{color_name}' not available\n\n"
                    f"{get_emoji('kuning')} Try: red, orange, green, cyan, blue, violet, pink\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Colors")
                return

            success = await deco_system.update_profile_decoration(vzoel_client, color_palette_id=color_id)

            if success:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('centang')} Profile color updated!\n\n"
                    f"{get_emoji('aktif')} Color: {color_name.title()}\n"
                    f"{get_emoji('proses')} ID: {color_id}\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Colors")
            else:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('merah')} Failed to update color!\n\n"
                    f"{get_emoji('kuning')} Check Telegram Premium status\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Colors")

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Error setting color!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Colors")

        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.profilebg(?:\s+(.+))?'))
async def profile_background_handler(event):
    """Set profile background emoji from VZL2 premium collection"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji

        emoji_key = event.pattern_match.group(1)
        if not emoji_key:
            # Show available premium emojis
            result_text = f"{get_emoji('utama')} VZL2 PREMIUM BACKGROUND EMOJIS\n\n"

            for key, emoji_data in PREMIUM_EMOJIS.items():
                emoji_char = emoji_data.get('char', '❓')
                result_text += f"{emoji_char} `.profilebg {key}`\n"

            result_text += f"\n{get_emoji('aktif')} Total premium emojis: {len(PREMIUM_EMOJIS)}\n"
            result_text += f"{get_emoji('kuning')} Note: Not all emojis may work as backgrounds\n"
            result_text += f"{get_emoji('telegram')} VZL2 Profile Backgrounds"

            await safe_send_premium(event, result_text)
            return

        emoji_key = emoji_key.strip().lower()

        if emoji_key not in PREMIUM_EMOJIS:
            await safe_send_premium(event,
                f"{get_emoji('merah')} Unknown emoji: {emoji_key}\n\n"
                f"{get_emoji('centang')} Use `.profilebg` to see available emojis\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Backgrounds")
            return

        processing_msg = await safe_send_premium(event,
            f"{get_emoji('loading')} Setting {get_emoji(emoji_key)} background...")

        try:
            emoji_id = deco_system.get_premium_emoji_id(emoji_key)

            if emoji_id is None:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('kuning')} Premium emoji '{emoji_key}' not compatible as background\n\n"
                    f"{get_emoji('centang')} Emoji: {get_emoji(emoji_key)}\n"
                    f"{get_emoji('proses')} Status: No valid document ID found\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Backgrounds")
                return

            success = await deco_system.update_profile_decoration(vzoel_client, bg_emoji_id=emoji_id)

            if success:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('centang')} Background emoji updated!\n\n"
                    f"{get_emoji('aktif')} Emoji: {get_emoji(emoji_key)}\n"
                    f"{get_emoji('proses')} Key: {emoji_key}\n"
                    f"{get_emoji('kuning')} ID: {emoji_id}\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Backgrounds")
            else:
                await safe_edit_premium(processing_msg,
                    f"{get_emoji('merah')} Failed to set background!\n\n"
                    f"{get_emoji('kuning')} Possible issues:\n"
                    f"• Premium emoji not supported as background\n"
                    f"• Telegram Premium required\n"
                    f"• API rate limiting\n\n"
                    f"{get_emoji('telegram')} VZL2 Profile Backgrounds")

        except Exception as e:
            await safe_edit_premium(processing_msg,
                f"{get_emoji('merah')} Error setting background!\n\n"
                f"{get_emoji('kuning')} Error: {str(e)[:100]}\n\n"
                f"{get_emoji('telegram')} VZL2 Profile Backgrounds")

        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator