"""
VZL2 Staff Management Plugin - Admin Promotion & Staff List
Advanced admin promotion and staff listing with premium emoji mapping
𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠
Version: 1.0.0 - Premium Staff System
"""

from telethon import events
from telethon.tl.types import ChatAdminRights
from telethon.tl.functions.channels import EditAdminRequest
from telethon.errors import (
    ChatAdminRequiredError, UserAdminInvalidError, RightForbiddenError,
    UsernameNotOccupiedError, UsernameInvalidError, PeerIdInvalidError
)
import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from central emoji template (VZL2 style)
from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

# Plugin Info
PLUGIN_INFO = {
    "name": "staff",
    "version": "1.0.0",
    "description": "Premium staff management dengan admin promotion dan listing",
    "author": "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠",
    "commands": [".staff", ".admin", ".unadmin", ".reloadmin"],
    "features": ["admin promotion", "admin demotion", "staff listing", "premium emoji"]
}

__version__ = "1.0.0"
__author__ = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

class StaffSystem:
    """Premium Staff Management System"""

    def __init__(self):
        self.admin_hierarchy = {
            "creator": {"name": "Pendiri", "emoji": "utama"},
            "administrator": {"name": "Admin", "emoji": "centang"}
        }

    def get_admin_title(self, participant) -> str:
        """Get admin title dengan hierarchy detection"""
        if hasattr(participant, 'admin_rights') and participant.creator:
            return "Pendiri"

        if hasattr(participant, 'rank') and participant.rank:
            return participant.rank

        return "Admin"

    async def get_chat_admins(self, client, chat_id):
        """Get all chat administrators"""
        try:
            admins = []
            async for participant in client.iter_participants(chat_id, filter="administrators"):
                if not participant.bot:
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

            admins.sort(key=lambda x: (0 if x['is_creator'] else 1, x['user'].first_name or "Unknown"))
            return admins
        except Exception as e:
            print(f"[Staff] Error getting admins: {e}")
            return []

    async def promote_user(self, client, chat_id: int, user) -> bool:
        """Promote user to administrator"""
        try:
            admin_rights = ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False
            )

            await client(EditAdminRequest(
                channel=chat_id,
                user_id=user.id,
                admin_rights=admin_rights,
                rank="Admin"
            ))
            return True
        except Exception as e:
            print(f"[Staff] Promote error: {e}")
            return False

    async def demote_user(self, client, chat_id: int, user) -> bool:
        """Demote user from administrator"""
        try:
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

            await client(EditAdminRequest(
                channel=chat_id,
                user_id=user.id,
                admin_rights=no_admin_rights,
                rank=""
            ))
            return True
        except Exception as e:
            print(f"[Staff] Demote error: {e}")
            return False

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

# Initialize staff system
staff_system = StaffSystem()

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    signature = f"{get_emoji('utama')}{get_emoji('centang')}{get_emoji('adder1')}"
    print(f"✅ [Staff] Premium staff management loaded v{PLUGIN_INFO['version']}")
    print(f"✅ [Staff] 𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠 branding: {signature} STAFF SYSTEM")

@events.register(events.NewMessage(pattern=r'\.admin'))
async def admin_handler(event):
    """Admin promotion handler"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Admin commands only work in groups."
        )
        return

    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
    target_user = await staff_system.resolve_user(vzoel_client, event, args)

    if not target_user:
        await safe_send_premium(event,
            f"{get_emoji('utama')} **PREMIUM ADMIN PROMOTION**\n\n"
            f"{get_emoji('merah')} **No target specified!**\n\n"
            f"{get_emoji('utama')} **Usage:**\n"
            f"  • `.admin @username` - Promote by username\n"
            f"  • Reply to user + `.admin` - Promote by reply\n\n"
            f"{get_emoji('adder1')} **Requirements:** Admin with promote rights\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )
        return

    promoting_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Promoting User...**\n\n"
        f"{get_emoji('proses')} **Target:** {target_user.first_name}\n"
        f"{get_emoji('loading')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n"
        f"{get_emoji('kuning')} **Processing promotion...**"
    )

    success = await staff_system.promote_user(vzoel_client, event.chat_id, target_user)

    if success:
        await safe_edit_premium(promoting_msg,
            f"{get_emoji('aktif')} **User Promoted Successfully!**\n\n"
            f"{get_emoji('utama')} **New Admin:** {target_user.first_name}\n"
            f"{get_emoji('proses')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n"
            f"{get_emoji('centang')} **Rank:** Administrator\n"
            f"{get_emoji('aktif')} **Privileges:** Standard admin rights granted\n\n"
            f"{get_emoji('telegram')} **View all staff:** `.staff`\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )
    else:
        await safe_edit_premium(promoting_msg,
            f"{get_emoji('merah')} **Promotion Failed!**\n\n"
            f"{get_emoji('merah')} Unable to promote user to admin\n"
            f"{get_emoji('kuning')} **Possible Issues:**\n"
            f"  • Insufficient admin privileges\n"
            f"  • User is already an admin\n"
            f"  • Cannot promote this user type\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )

@events.register(events.NewMessage(pattern=r'\.unadmin'))
async def unadmin_handler(event):
    """Admin demotion handler"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Unadmin commands only work in groups."
        )
        return

    args = event.text.split(maxsplit=1)[1] if len(event.text.split()) > 1 else ""
    target_user = await staff_system.resolve_user(vzoel_client, event, args)

    if not target_user:
        await safe_send_premium(event,
            f"{get_emoji('utama')} **PREMIUM ADMIN DEMOTION**\n\n"
            f"{get_emoji('merah')} **No target specified!**\n\n"
            f"{get_emoji('utama')} **Usage:**\n"
            f"  • `.unadmin @username` - Demote by username\n"
            f"  • Reply to user + `.unadmin` - Demote by reply\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )
        return

    demoting_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Demoting Admin...**\n\n"
        f"{get_emoji('proses')} **Target:** {target_user.first_name}\n"
        f"{get_emoji('loading')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n"
        f"{get_emoji('kuning')} **Processing demotion...**"
    )

    success = await staff_system.demote_user(vzoel_client, event.chat_id, target_user)

    if success:
        await safe_edit_premium(demoting_msg,
            f"{get_emoji('aktif')} **Admin Demoted Successfully!**\n\n"
            f"{get_emoji('proses')} **Demoted User:** {target_user.first_name}\n"
            f"{get_emoji('loading')} **Username:** `@{target_user.username if target_user.username else 'No username'}`\n"
            f"{get_emoji('kuning')} **Status:** Regular Member\n"
            f"{get_emoji('aktif')} **Admin Rights:** All privileges removed\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )
    else:
        await safe_edit_premium(demoting_msg,
            f"{get_emoji('merah')} **Demotion Failed!**\n\n"
            f"{get_emoji('merah')} Unable to demote user from admin\n"
            f"{get_emoji('kuning')} **Possible Issues:**\n"
            f"  • Insufficient admin privileges\n"
            f"  • User is not an admin\n"
            f"  • User has higher privileges\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )

@events.register(events.NewMessage(pattern=r'\.staff'))
async def staff_handler(event):
    """Staff listing handler"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Staff commands only work in groups."
        )
        return

    loading_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Loading Staff List...**\n\n"
        f"{get_emoji('loading')} Collecting administrators..."
    )

    admins = await staff_system.get_chat_admins(vzoel_client, event.chat_id)

    if not admins:
        await safe_edit_premium(loading_msg,
            f"{get_emoji('merah')} **Unable to Load Staff!**\n\n"
            f"{get_emoji('merah')} Cannot access administrator list\n"
            f"{get_emoji('kuning')} This may be due to privacy settings\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )
        return

    chat = await vzoel_client.get_entity(event.chat_id)
    chat_title = chat.title if hasattr(chat, 'title') else "Group"

    staff_text = f"{get_emoji('telegram')} **STAFF LIST - {chat_title.upper()}**\n\n"
    staff_text += f"{get_emoji('aktif')} **Total Administrators:** {len(admins)}\n\n"

    for index, admin in enumerate(admins[:15], 1):  # Limit to 15 admins
        user = admin['user']
        title = admin['title']

        if title == "Pendiri":
            title_emoji = get_emoji('utama')
        else:
            title_emoji = get_emoji('centang')

        full_name = user.first_name or "Unknown"
        if hasattr(user, 'last_name') and user.last_name:
            full_name += f" {user.last_name}"

        username_text = f"@{user.username}" if user.username else "No username"

        staff_text += f"{title_emoji} **{index}. {full_name}**\n"
        staff_text += f"   {get_emoji('proses')} `{username_text}`\n"
        staff_text += f"   {get_emoji('loading')} *{title}*\n\n"

    if len(admins) > 15:
        staff_text += f"{get_emoji('kuning')} *... and {len(admins)-15} more admins*\n\n"

    staff_text += f"{get_emoji('utama')} **Promote new admin:** `.admin @username`\n\n"
    staff_text += f"{get_emoji('telegram')} VZL2 Premium Staff System"

    await safe_edit_premium(loading_msg, staff_text)

@events.register(events.NewMessage(pattern=r'\.reloadmin'))
async def reloadmin_handler(event):
    """Admin reload/refresh handler"""
    if not await is_owner(event):
        return

    if not (event.is_group or event.is_channel):
        await safe_send_premium(event,
            f"{get_emoji('merah')} **Group Only!**\n\n"
            f"{get_emoji('kuning')} Reload commands only work in groups."
        )
        return

    reload_msg = await safe_send_premium(event,
        f"{get_emoji('loading')} **Reloading Admin Cache...**\n\n"
        f"{get_emoji('loading')} Refreshing administrator list..."
    )

    try:
        admins = await staff_system.get_chat_admins(vzoel_client, event.chat_id)
        chat = await vzoel_client.get_entity(event.chat_id)
        chat_title = chat.title if hasattr(chat, 'title') else "Group"

        if admins:
            reload_text = f"{get_emoji('aktif')} **Admin Cache Reloaded!**\n\n"
            reload_text += f"{get_emoji('utama')} **Group:** {chat_title}\n"
            reload_text += f"{get_emoji('aktif')} **Total Admins:** {len(admins)}\n"
            reload_text += f"{get_emoji('loading')} **Cache Status:** Fresh\n\n"
            reload_text += f"{get_emoji('proses')} **Admin Preview:**\n"

            for i, admin in enumerate(admins[:5], 1):
                admin_name = admin['user'].first_name or "Unknown"
                admin_title = admin['title']
                reload_text += f"  {get_emoji('centang')} `{i}. {admin_name}` - *{admin_title}*\n"

            if len(admins) > 5:
                reload_text += f"  {get_emoji('kuning')} *... and {len(admins)-5} more*\n"

            reload_text += f"\n{get_emoji('telegram')} **Full list:** `.staff`\n\n"
            reload_text += f"{get_emoji('telegram')} VZL2 Premium Staff System"

            await safe_edit_premium(reload_msg, reload_text)
        else:
            await safe_edit_premium(reload_msg,
                f"{get_emoji('merah')} **Reload Failed!**\n\n"
                f"{get_emoji('merah')} Unable to refresh admin cache\n"
                f"{get_emoji('kuning')} This may be due to privacy restrictions\n\n"
                f"{get_emoji('telegram')} VZL2 Premium Staff System"
            )
    except Exception as e:
        await safe_edit_premium(reload_msg,
            f"{get_emoji('merah')} **Reload Error!**\n\n"
            f"{get_emoji('merah')} **Error:** {str(e)[:100]}\n\n"
            f"{get_emoji('telegram')} VZL2 Premium Staff System"
        )