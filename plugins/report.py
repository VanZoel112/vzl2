"""
Vzoel Fox's Lutpan - Report Plugin
Report spam users and messages

Commands:
- .report [username/reply] - Report spam user
- .reports - View all reported users
- .unreport <user_id> - Remove from report list

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events, Button
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam, InputPeerUser
from telethon.errors import UserIdInvalidError, UserNotParticipantError
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from config import Config

# Plugin info
PLUGIN_INFO = {
    "name": "report",
    "version": "1.0.0",
    "description": "Report spam users and track reports",
    "author": "Vzoel Fox's",
    "commands": [".report", ".reports", ".unreport"],
    "features": ["Spam reporting", "Report tracking", "Database storage"]
}

# Global references
vzoel_client = None
vzoel_emoji = None

# Report storage file
REPORTS_FILE = "reported_users.json"


def load_reports():
    """Load reported users from file"""
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_reports(reports):
    """Save reported users to file"""
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler

    print(f"{get_emoji('utama')} Vzoel Fox's Lutpan Report System loaded")


@events.register(events.NewMessage(pattern=r'\.report(?: (.+))?'))
async def report_spam_handler(event):
    """Report spam user"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        # Processing message
        processing_msg = f"""{get_emoji('loading')} PROCESSING REPORT

{get_emoji('proses')} Analyzing target
{get_emoji('telegram')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        target_user = None
        target_username = None
        reason = "Spam"

        # Get target user
        if event.is_reply:
            # Report replied message
            reply_msg = await event.get_reply_message()
            target_user = await event.client.get_entity(reply_msg.sender_id)
            target_username = f"@{target_user.username}" if target_user.username else f"User {target_user.id}"
        else:
            # Report by username
            match = event.pattern_match.group(1)
            if not match:
                await safe_edit_premium(event, f"""{get_emoji('kuning')} INVALID USAGE

{get_emoji('telegram')} Reply to spam message with .report
{get_emoji('aktif')} Or use: .report @username

VZOEL FOX'S LUTPAN""")
                return

            try:
                target_user = await event.client.get_entity(match.strip())
                target_username = f"@{target_user.username}" if target_user.username else f"User {target_user.id}"
            except Exception as e:
                await safe_edit_premium(event, f"""{get_emoji('merah')} USER NOT FOUND

{get_emoji('kuning')} Error: {str(e)}
{get_emoji('telegram')} Check username and try again

VZOEL FOX'S LUTPAN""")
                return

        # Report to Telegram
        try:
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                await event.client(ReportRequest(
                    peer=await event.client.get_input_entity(event.chat_id),
                    id=[reply_msg.id],
                    reason=InputReportReasonSpam(),
                    message="Spam report from Vzoel Fox's Lutpan"
                ))
        except Exception as e:
            print(f"Telegram report error: {e}")

        # Save to local database
        reports = load_reports()
        user_id = str(target_user.id)

        if user_id not in reports:
            reports[user_id] = {
                'username': target_username,
                'first_name': target_user.first_name or 'Unknown',
                'last_name': target_user.last_name or '',
                'reports': []
            }

        reports[user_id]['reports'].append({
            'timestamp': datetime.now().isoformat(),
            'chat_id': event.chat_id,
            'reason': reason
        })

        save_reports(reports)

        # Response with inline buttons
        total_reports = len(reports[user_id]['reports'])

        response = f"""{get_emoji('centang')} USER REPORTED

{get_emoji('aktif')} Target: {target_username}
{get_emoji('proses')} User ID: `{target_user.id}`
{get_emoji('telegram')} Total Reports: {total_reports}

{get_emoji('biru')} ACTIONS TAKEN:
• Reported to Telegram
• Saved to local database
• Added to spam tracker

{get_emoji('kuning')} QUICK ACTIONS:
Use .reports to view all reported users

VZOEL FOX'S LUTPAN Anti-Spam System
CONTACT: @VZLfxs"""

        # Inline buttons
        buttons = [
            [Button.inline(f"{get_emoji('centang')} View Reports", b"view_reports")],
            [Button.inline(f"{get_emoji('merah')} Unreport User", f"unreport_{user_id}")]
        ]

        await safe_edit_premium(event, response, buttons=buttons)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.reports'))
async def view_reports_handler(event):
    """View all reported users"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        # Processing
        processing_msg = f"""{get_emoji('loading')} LOADING REPORTS

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Load reports
        reports = load_reports()

        if not reports:
            await safe_edit_premium(event, f"""{get_emoji('kuning')} NO REPORTS FOUND

{get_emoji('telegram')} No users have been reported yet
{get_emoji('aktif')} Use .report to report spam users

VZOEL FOX'S LUTPAN""")
            return

        # Build report list
        response = f"""{get_emoji('utama')} REPORTED USERS

{get_emoji('biru')} Total Reported: {len(reports)}

"""

        for i, (user_id, data) in enumerate(reports.items(), 1):
            username = data.get('username', 'Unknown')
            report_count = len(data.get('reports', []))
            latest_report = data['reports'][-1] if data['reports'] else {}
            timestamp = latest_report.get('timestamp', 'Unknown')

            response += f"""{get_emoji('centang')} {i}. {username}
   ID: `{user_id}`
   Reports: {report_count}
   Last: {timestamp[:10] if timestamp != 'Unknown' else 'N/A'}

"""

        response += f"""{get_emoji('telegram')} MANAGEMENT:
• .unreport <user_id> - Remove from list
• .report @username - Report new user

VZOEL FOX'S LUTPAN Anti-Spam System
CONTACT: @VZLfxs"""

        # Inline buttons for pagination (if many reports)
        buttons = []
        if len(reports) > 5:
            buttons.append([Button.inline(f"{get_emoji('proses')} Show More", b"show_more_reports")])

        await safe_edit_premium(event, response, buttons=buttons if buttons else None)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.unreport (\d+)'))
async def unreport_handler(event):
    """Remove user from report list"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        user_id = event.pattern_match.group(1).strip()

        # Processing
        processing_msg = f"""{get_emoji('loading')} REMOVING REPORT

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Load reports
        reports = load_reports()

        if user_id not in reports:
            await safe_edit_premium(event, f"""{get_emoji('kuning')} USER NOT FOUND

{get_emoji('merah')} User ID {user_id} not in report list
{get_emoji('telegram')} Use .reports to view all

VZOEL FOX'S LUTPAN""")
            return

        # Remove user
        user_data = reports.pop(user_id)
        save_reports(reports)

        response = f"""{get_emoji('centang')} REPORT REMOVED

{get_emoji('aktif')} User: {user_data.get('username', 'Unknown')}
{get_emoji('proses')} User ID: `{user_id}`
{get_emoji('telegram')} Total Reports Cleared: {len(user_data.get('reports', []))}

{get_emoji('biru')} User removed from report database

VZOEL FOX'S LUTPAN Anti-Spam System
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.CallbackQuery(pattern=b"view_reports"))
async def view_reports_callback(event):
    """Callback for viewing reports"""
    await view_reports_handler(event)


@events.register(events.CallbackQuery(pattern=b"unreport_(.+)"))
async def unreport_callback(event):
    """Callback for unreporting user"""
    user_id = event.data.decode().split('_')[1]

    # Load reports
    reports = load_reports()

    if user_id not in reports:
        await event.answer(f"{get_emoji('merah')} User not found", alert=True)
        return

    # Remove user
    user_data = reports.pop(user_id)
    save_reports(reports)

    # Update message
    response = f"""{get_emoji('centang')} REPORT REMOVED

{get_emoji('aktif')} User: {user_data.get('username', 'Unknown')}
{get_emoji('proses')} User ID: `{user_id}`
{get_emoji('telegram')} Cleared from database

VZOEL FOX'S LUTPAN Anti-Spam System
CONTACT: @VZLfxs"""

    await event.edit(response)
    await event.answer(f"{get_emoji('centang')} User unreported successfully")
