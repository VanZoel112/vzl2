#!/usr/bin/env python3
"""
VZL2 Staff Management Plugin - Admin Promotion & Staff List
Advanced admin promotion and staff listing with premium emoji mapping
Adapted for VZL2 architecture by VanZoel112
"""

import asyncio
import os
from typing import List, Optional, Dict, Any
from telethon import events
from telethon.tl.types import MessageEntityCustomEmoji, User, Channel
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
from telethon.errors import (
    ChatAdminRequiredError, UserAdminInvalidError, RightForbiddenError,
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
    "name": "staff",
    "version": "1.0.0",
    "description": "Advanced staff management with admin promotion and listing",
    "author": "VanZoel112",
    "commands": [".staff", ".admin <user>", ".unadmin <user>", ".reloadmin"],
    "features": ["admin promotion", "admin demotion", "admin reload", "staff listing", "premium emoji support", "hierarchy display"]
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
        print(f"[Staff] Premium emoji error: {e}")
        return await event.reply(text)

class StaffManagementSystem:
    """Premium Staff Management System"""

    def __init__(self):
        # Admin hierarchy mapping
        self.admin_hierarchy = {
            "creator": {"name": "Pendiri", "priority": 1, "emoji": "main"},
            "administrator": {"name": "Admin", "priority": 3, "emoji": "check"}
        }

        # Special admin titles detection
        self.special_titles = {
            "founder": "Pendiri",
            "co-founder": "Wakil Pendiri",
            "co founder": "Wakil Pendiri",
            "wakil pendiri": "Wakil Pendiri",
            "deputy": "Wakil Pendiri",
            "vice": "Wakil Pendiri",
            "admin": "Admin",
            "administrator": "Admin",
            "moderator": "Admin",
            "mod": "Admin"
        }

    def get_admin_title(self, participant) -> str:
        """Get admin title dengan hierarchy detection"""

        # Owner always gets Pendiri
        if hasattr(participant, 'admin_rights') and participant.creator:
            return "Pendiri"

        # Check custom title first
        if hasattr(participant, 'rank') and participant.rank:
            title_lower = participant.rank.lower()

            # Check for special titles
            for key, display_name in self.special_titles.items():
                if key in title_lower:
                    return display_name

            # Return custom title if not special
            return participant.rank

        # Default admin title
        return "Admin"

    def format_admin_entry(self, index: int, user, admin_title: str) -> str:
        """Format single admin entry untuk display"""

        if not user:
            return ""

        # Select emoji based on title
        if admin_title == "Pendiri":
            title_emoji = get_emoji("main")
        elif admin_title == "Wakil Pendiri":
            title_emoji = get_emoji("adder2")
        else:
            title_emoji = get_emoji("check")

        # Format name
        full_name = user.first_name or "Unknown"
        if hasattr(user, 'last_name') and user.last_name:
            full_name += f" {user.last_name}"

        # Format username
        username_text = f"@{user.username}" if user.username else "No username"

        # Create entry lines
        entry_lines = [
            f"{convert_font(f'{index}.', 'bold')} {title_emoji} {convert_font(full_name, 'bold')}",
            f"   {get_emoji('adder4')} {convert_font(username_text, 'mono')}",
            f"   {get_emoji('adder1')} {convert_font(admin_title, 'italic')}"
        ]

        return "\n".join(entry_lines)

    async def get_chat_admins(self, client, chat_id):
        """Get all chat administrators"""
        try:
            admins = []

            # Get chat participants
            async for participant in client.iter_participants(chat_id, filter="administrators"):
                if not participant.bot:
                    # Get participant info from chat
                    participant_info = await client.get_participants(chat_id, filter="administrators")
                    for p in participant_info:
                        if p.id == participant.id and hasattr(p, 'participant'):
                            admin_title = self.get_admin_title(p.participant)
                            admins.append({
                                'user': participant,
                                'title': admin_title,
                                'is_creator': hasattr(p.participant, 'admin_rights') and getattr(p.participant, 'creator', False)
                            })
                            break

            # Sort by hierarchy (owner first, then admins)
            admins.sort(key=lambda x: (
                0 if x['is_creator'] else 1,
                x['user'].first_name or "Unknown"
            ))

            return admins

        except Exception as e:
            print(f"[Staff] Error getting chat admins: {e}")
            return []

    async def promote_user_to_admin(self, client, chat_id: int, target_user) -> bool:
        """Promote user to administrator"""
        try:
            # Create admin rights
            admin_rights = ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False  # Cannot promote others
            )

            # Promote user
            await client(EditAdminRequest(
                channel=chat_id,
                user_id=target_user.id,
                admin_rights=admin_rights,
                rank="Admin"
            ))

            return True

        except ChatAdminRequiredError:
            print("[Staff] Chat admin privileges required to promote")
            return False
        except UserAdminInvalidError:
            print("[Staff] Cannot promote this user")
            return False
        except RightForbiddenError:
            print("[Staff] Insufficient rights to promote users")
            return False
        except Exception as e:
            print(f"[Staff] Error promoting user: {e}")
            return False

    async def demote_user_from_admin(self, client, chat_id: int, target_user) -> bool:
        """Demote user from administrator"""
        try:
            # Create empty admin rights (removes all admin privileges)
            no_admin_rights = ChatAdminRights(
                change_info=False,
                post_messages=False,
                edit_messages=False,
                delete_messages=False,
                ban_users=False,
                invite_users=False,
                pin_messages=False,
                add_admins=False
            )

            # Demote user by removing admin rights
            await client(EditAdminRequest(
                channel=chat_id,
                user_id=target_user.id,
                admin_rights=no_admin_rights,
                rank=""
            ))

            return True

        except ChatAdminRequiredError:
            print("[Staff] Chat admin privileges required to demote")
            return False
        except UserAdminInvalidError:
            print("[Staff] Cannot demote this user")
            return False
        except RightForbiddenError:
            print("[Staff] Insufficient rights to demote users")
            return False
        except Exception as e:
            print(f"[Staff] Error demoting user: {e}")
            return False

    async def resolve_target_user(self, client, event, args: str):
        """Resolve target user dari argument atau reply"""

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

# Initialize staff system
staff_system = StaffManagementSystem()

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

async def admin_handler(event):
    """Admin promotion handler"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Admin commands only work in groups."
        )
        return

    # Get arguments
    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""

    # Resolve target user
    target_user = await staff_system.resolve_target_user(client, event, args)

    if not target_user:
        usage_text = f"""{get_emoji('main')} {convert_font('PREMIUM ADMIN PROMOTION', 'bold')}

{get_emoji('adder5')} {convert_font('No target specified!', 'bold')}

{get_emoji('main')} {convert_font('Usage:', 'bold')}
  • {convert_font('.admin @username', 'mono')} - Promote by username
  • Reply to user + {convert_font('.admin', 'mono')} - Promote by reply

{get_emoji('check')} {convert_font('Examples:', 'bold')}
  • {convert_font('.admin @johndoe', 'mono')}
  • Reply to message + {convert_font('.admin', 'mono')}

{get_emoji('adder1')} {convert_font('Requirements:', 'bold')} Admin with promote rights

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await safe_send_premium(event, usage_text)
        return

    # Show promoting status
    promoting_msg = await safe_send_premium(event,
        f"{get_emoji('check')} {convert_font('Promoting User...', 'bold')}\n\n"
        f"{get_emoji('adder4')} {convert_font('Target:', 'bold')} {convert_font(target_user.first_name, 'bold')}\n"
        f"{get_emoji('adder1')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}\n"
        f"{get_emoji('adder3')} {convert_font('Processing promotion...', 'bold')}"
    )

    # Attempt promotion
    success = await staff_system.promote_user_to_admin(client, event.chat_id, target_user)

    if success:
        success_text = f"""{get_emoji('adder2')} {convert_font('User Promoted Successfully!', 'bold')}

{get_emoji('main')} {convert_font('New Admin:', 'bold')} {convert_font(target_user.first_name, 'bold')}
{get_emoji('adder4')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}
{get_emoji('check')} {convert_font('Rank:', 'bold')} {convert_font('Administrator', 'bold')}
{get_emoji('adder2')} {convert_font('Privileges:', 'bold')} Standard admin rights granted

{get_emoji('adder3')} {convert_font('View all staff:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await promoting_msg.edit(success_text)
        print(f"[Staff] Successfully promoted {target_user.username or target_user.id} to admin")

    else:
        error_text = f"""{get_emoji('adder5')} {convert_font('Promotion Failed!', 'bold')}

{get_emoji('adder5')} Unable to promote user to admin
{get_emoji('adder3')} {convert_font('Possible Issues:', 'bold')}
  • Insufficient admin privileges
  • User is already an admin
  • Cannot promote this user type
  • Group restrictions

{get_emoji('adder3')} {convert_font('Current staff:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await promoting_msg.edit(error_text)

async def unadmin_handler(event):
    """Admin demotion handler"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Unadmin commands only work in groups."
        )
        return

    # Get arguments
    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""

    # Resolve target user
    target_user = await staff_system.resolve_target_user(client, event, args)

    if not target_user:
        usage_text = f"""{get_emoji('main')} {convert_font('PREMIUM ADMIN DEMOTION', 'bold')}

{get_emoji('adder5')} {convert_font('No target specified!', 'bold')}

{get_emoji('main')} {convert_font('Usage:', 'bold')}
  • {convert_font('.unadmin @username', 'mono')} - Demote by username
  • Reply to user + {convert_font('.unadmin', 'mono')} - Demote by reply

{get_emoji('check')} {convert_font('Examples:', 'bold')}
  • {convert_font('.unadmin @johndoe', 'mono')}
  • Reply to message + {convert_font('.unadmin', 'mono')}

{get_emoji('adder1')} {convert_font('Requirements:', 'bold')} Admin with demote rights

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await safe_send_premium(event, usage_text)
        return

    # Show demoting status
    demoting_msg = await safe_send_premium(event,
        f"{get_emoji('check')} {convert_font('Demoting Admin...', 'bold')}\n\n"
        f"{get_emoji('adder4')} {convert_font('Target:', 'bold')} {convert_font(target_user.first_name, 'bold')}\n"
        f"{get_emoji('adder1')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}\n"
        f"{get_emoji('adder3')} {convert_font('Processing demotion...', 'bold')}"
    )

    # Attempt demotion
    success = await staff_system.demote_user_from_admin(client, event.chat_id, target_user)

    if success:
        success_text = f"""{get_emoji('adder2')} {convert_font('Admin Demoted Successfully!', 'bold')}

{get_emoji('adder4')} {convert_font('Demoted User:', 'bold')} {convert_font(target_user.first_name, 'bold')}
{get_emoji('adder1')} {convert_font('Username:', 'bold')} {convert_font(f'@{target_user.username}' if target_user.username else 'No username', 'mono')}
{get_emoji('adder3')} {convert_font('Status:', 'bold')} {convert_font('Regular Member', 'bold')}
{get_emoji('adder2')} {convert_font('Admin Rights:', 'bold')} All privileges removed

{get_emoji('adder3')} {convert_font('View current staff:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await demoting_msg.edit(success_text)
        print(f"[Staff] Successfully demoted {target_user.username or target_user.id} from admin")

    else:
        error_text = f"""{get_emoji('adder5')} {convert_font('Demotion Failed!', 'bold')}

{get_emoji('adder5')} Unable to demote user from admin
{get_emoji('adder3')} {convert_font('Possible Issues:', 'bold')}
  • Insufficient admin privileges
  • User is not an admin
  • Cannot demote this user type
  • User has higher privileges
  • Group restrictions

{get_emoji('adder3')} {convert_font('Current staff:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await demoting_msg.edit(error_text)

async def reloadmin_handler(event):
    """Admin reload/refresh handler"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Reload commands only work in groups."
        )
        return

    # Show reloading status
    reload_msg = await safe_send_premium(event,
        f"{get_emoji('check')} {convert_font('Reloading Admin Cache...', 'bold')}\n\n"
        f"{get_emoji('adder1')} Refreshing administrator list..."
    )

    try:
        # Force reload admin cache by getting fresh admin list
        admins = await staff_system.get_chat_admins(client, event.chat_id)

        # Get chat info
        chat = await client.get_entity(event.chat_id)
        chat_title = chat.title if hasattr(chat, 'title') else "Group"

        if admins:
            reload_text = f"""{get_emoji('adder2')} {convert_font('Admin Cache Reloaded!', 'bold')}

{get_emoji('main')} {convert_font('Group:', 'bold')} {convert_font(chat_title, 'bold')}
{get_emoji('adder2')} {convert_font('Total Admins:', 'bold')} {convert_font(str(len(admins)), 'bold')}
{get_emoji('adder1')} {convert_font('Cache Status:', 'bold')} {convert_font('Fresh', 'bold')}

{get_emoji('adder4')} {convert_font('Admin List:', 'bold')}"""

            # Add first 5 admins for preview
            for i, admin in enumerate(admins[:5], 1):
                admin_name = admin['user'].first_name or "Unknown"
                admin_title = admin['title']
                reload_text += f"\n  {get_emoji('check')} {convert_font(f'{i}. {admin_name}', 'mono')} - {convert_font(admin_title, 'italic')}"

            if len(admins) > 5:
                reload_text += f"\n  {get_emoji('adder3')} {convert_font(f'... and {len(admins)-5} more', 'italic')}"

            reload_text += f"""

{get_emoji('adder3')} {convert_font('Full list:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

            await reload_msg.edit(reload_text)
            print(f"[Staff] Admin cache reloaded for chat {event.chat_id} - {len(admins)} admins")

        else:
            error_text = f"""{get_emoji('adder5')} {convert_font('Reload Failed!', 'bold')}

{get_emoji('adder5')} Unable to refresh admin cache
{get_emoji('adder3')} This may be due to:
  • Privacy restrictions
  • Network issues
  • Insufficient permissions

{get_emoji('adder1')} {convert_font('Try again later or use:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

            await reload_msg.edit(error_text)

    except Exception as e:
        error_text = f"""{get_emoji('adder5')} {convert_font('Reload Error!', 'bold')}

{get_emoji('adder5')} {convert_font('Error:', 'bold')} {str(e)}

{get_emoji('adder1')} {convert_font('Try again with:', 'bold')} {convert_font('.staff', 'mono')}

{get_emoji('adder6')} VZL2 Premium Staff System"""

        await reload_msg.edit(error_text)
        print(f"[Staff] Admin reload error: {e}")

async def staff_handler(event):
    """Staff listing handler"""
    global client
    if not await is_owner_check(client, event.sender_id):
        return

    # Check if in group
    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('adder5')} {convert_font('Group Only!', 'bold')}\n\n"
            f"{get_emoji('adder3')} Staff commands only work in groups."
        )
        return

    # Show loading message
    loading_msg = await safe_send_premium(event,
        f"{get_emoji('adder3')} {convert_font('Loading Staff List...', 'bold')}\n\n"
        f"{get_emoji('check')} Collecting administrators..."
    )

    # Get chat admins
    admins = await staff_system.get_chat_admins(client, event.chat_id)

    if not admins:
        await loading_msg.edit(
            f"{get_emoji('adder5')} {convert_font('Unable to Load Staff!', 'bold')}\n\n"
            f"{get_emoji('adder5')} Cannot access administrator list\n"
            f"{get_emoji('adder3')} This may be due to privacy settings"
        )
        return

    # Format staff list
    chat = await client.get_entity(event.chat_id)
    chat_title = chat.title if hasattr(chat, 'title') else "Group"

    staff_lines = [
        f"{get_emoji('adder3')} {convert_font(f'STAFF LIST - {chat_title.upper()}', 'bold')}",
        "",
        f"{get_emoji('adder2')} {convert_font('Total Administrators:', 'bold')} {convert_font(str(len(admins)), 'bold')}",
        ""
    ]

    # Add each admin
    for index, admin in enumerate(admins, 1):
        admin_entry = staff_system.format_admin_entry(index, admin['user'], admin['title'])
        if admin_entry:
            staff_lines.append(admin_entry)
            staff_lines.append("")  # Empty line between entries

    # Add footer
    staff_lines.extend([
        f"{get_emoji('main')} {convert_font('Promote new admin:', 'bold')} {convert_font('.admin @username', 'mono')}",
        "",
        f"{get_emoji('adder6')} VZL2 Premium Staff System"
    ])

    # Update message dengan staff list
    await loading_msg.edit("\n".join(staff_lines))
    print(f"[Staff] Displayed staff list for chat {event.chat_id} - {len(admins)} admins")

def get_plugin_info():
    return PLUGIN_INFO

def setup(client_instance):
    """Setup function untuk register event handlers"""
    global client
    client = client_instance

    client.add_event_handler(admin_handler, events.NewMessage(pattern=r'\.admin(?:\s+(.+))?$'))
    client.add_event_handler(unadmin_handler, events.NewMessage(pattern=r'\.unadmin(?:\s+(.+))?$'))
    client.add_event_handler(staff_handler, events.NewMessage(pattern=r'\.staff$'))
    client.add_event_handler(reloadmin_handler, events.NewMessage(pattern=r'\.reloadmin$'))

    print(f"✅ [Staff] Premium staff management loaded v{PLUGIN_INFO['version']} - admin/unadmin/staff/reloadmin commands ready")

def cleanup_plugin():
    """Cleanup plugin resources"""
    global client
    try:
        print("[Staff] Plugin cleanup initiated")
        client = None
        print("[Staff] Plugin cleanup completed")
    except Exception as e:
        print(f"[Staff] Cleanup error: {e}")

# Export functions
__all__ = ['setup', 'cleanup_plugin', 'get_plugin_info', 'admin_handler', 'unadmin_handler', 'staff_handler', 'reloadmin_handler']