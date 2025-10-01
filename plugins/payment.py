"""
Vzoel Fox's Lutpan - Payment Plugin
Payment gateway and QR code management

Commands:
- .getfileid - Extract file_id from image (reply to image)
- .setgetqr - Store QR code for quick display
- .getqr - Display stored payment QR code
- .setget <info> - Set payment information
- .get - Show payment information

Author: Vzoel Fox's
Contact: @VZLfxs
"""

from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium
from core.payment import PaymentManager

# Plugin info
PLUGIN_INFO = {
    "name": "payment",
    "version": "2.0.0",
    "description": "Payment gateway and QR code management",
    "author": "Vzoel Fox's",
    "commands": [".getfileid", ".setgetqr", ".getqr", ".setget", ".get"],
    "features": ["File ID extraction", "QR storage", "Payment info", "Database persistence"]
}

# Global references
vzoel_client = None
vzoel_emoji = None
payment_manager = None


async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji, payment_manager

    vzoel_client = client
    vzoel_emoji = emoji_handler

    # Initialize payment manager
    try:
        payment_manager = PaymentManager()
        print(f"{get_emoji('utama')} Vzoel Fox's Lutpan Payment System loaded")
    except Exception as e:
        print(f"{get_emoji('merah')} Payment manager init error: {e}")


@events.register(events.NewMessage(pattern=r'\.getfileid'))
async def get_file_id_handler(event):
    """Extract file_id from replied image"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client

        # Check if replying to message
        if not event.is_reply:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Reply to an image to get file_id\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} **Extracting file_id**

{get_emoji('proses')} Reading message
{get_emoji('telegram')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Get replied message
        reply_msg = await event.get_reply_message()

        # Extract file_id
        file_id = None
        file_type = "Unknown"

        if reply_msg.photo:
            file_id = reply_msg.photo.id
            file_type = "Photo"
        elif reply_msg.document:
            file_id = reply_msg.document.id
            file_type = "Document"

        if file_id:
            response = f"""{get_emoji('centang')} **File ID extracted**

{get_emoji('aktif')} Type: {file_type}
{get_emoji('proses')} File ID: `{file_id}`

{get_emoji('telegram')} **Usage:**
Copy the file_id above or use .setgetqr to store as QR code

{get_emoji('biru')} **Tips:**
Reply to this message with .setgetqr to save automatically

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} **No file found**

{get_emoji('kuning')} Please reply to a message containing:
• Photo
• Image document

{get_emoji('telegram')} Then use .getfileid again

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.setgetqr(?: (.+))?'))
async def set_qr_handler(event):
    """Store QR code file_id"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Get description if provided
        description = None
        match = event.pattern_match.group(1)
        if match:
            description = match.strip()

        # Check if replying to message
        if not event.is_reply:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Reply to QR image with .setgetqr\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} **Storing QR code**

{get_emoji('proses')} Extracting file_id
{get_emoji('telegram')} Saving to database

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Get replied message
        reply_msg = await event.get_reply_message()

        # Extract file_id
        file_id = None
        if reply_msg.photo:
            file_id = reply_msg.photo.id
        elif reply_msg.document:
            file_id = reply_msg.document.id

        if file_id:
            # Save QR code
            success = payment_manager.set_qr_code(file_id, description)

            if success:
                qr_count = payment_manager.get_stats()['qr_codes_count']
                response = f"""{get_emoji('centang')} **QR code saved**

{get_emoji('aktif')} File ID: `{file_id}`
{get_emoji('proses')} Description: {description or 'Payment QR Code'}
{get_emoji('telegram')} Total QR codes: {qr_count}

{get_emoji('biru')} **Quick Access:**
Use .getqr to display this QR code instantly

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""
            else:
                response = f"""{get_emoji('merah')} **Save failed**

{get_emoji('kuning')} Please try again

**Vzoel Fox's Lutpan**"""
        else:
            response = f"""{get_emoji('merah')} **No image found**

{get_emoji('kuning')} Reply to QR code image
{get_emoji('telegram')} Then use .setgetqr

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.getqr'))
async def get_qr_handler(event):
    """Display stored QR code"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} **Loading QR code**

{get_emoji('proses')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Get primary QR
        qr = payment_manager.get_primary_qr()

        if qr:
            file_id = qr['file_id']
            description = qr.get('description', 'Payment QR Code')

            # Delete processing message
            await event.delete()

            # Send QR code
            try:
                await event.client.send_file(
                    event.chat_id,
                    file_id,
                    caption=f"""{get_emoji('utama')} **{description}**

{get_emoji('centang')} Scan QR code to pay
{get_emoji('telegram')} Quick payment access

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""
                )
            except Exception as e:
                await event.respond(f"{get_emoji('merah')} Failed to send QR: {e}\n\n**Vzoel Fox's Lutpan**")

        else:
            response = f"""{get_emoji('kuning')} **No QR code stored**

{get_emoji('telegram')} Use .setgetqr to store QR code first

{get_emoji('aktif')} **Steps:**
1. Find your payment QR image
2. Reply to it with .getfileid
3. Reply to it with .setgetqr

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""

            await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.setget (.+)'))
async def set_payment_info_handler(event):
    """Set payment gateway information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        info_text = event.pattern_match.group(1).strip()

        # Processing
        processing_msg = f"""{get_emoji('loading')} **Storing payment info**

{get_emoji('proses')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Parse info (simple key:value format)
        payment_info = {'raw_text': info_text}

        # Try to parse structured format
        if '\n' in info_text:
            for line in info_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    payment_info[key.strip().lower()] = value.strip()

        # Save info
        success = payment_manager.set_payment_info(payment_info)

        if success:
            response = f"""{get_emoji('centang')} **Payment info saved**

{get_emoji('aktif')} Information stored successfully
{get_emoji('telegram')} Use .get to display payment info

{get_emoji('biru')} **Stored data:**
{info_text[:200]}{'...' if len(info_text) > 200 else ''}

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} **Save failed**

{get_emoji('kuning')} Please try again

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.get'))
async def get_payment_info_handler(event):
    """Display payment information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\n**Vzoel Fox's Lutpan**")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} **Loading payment info**

{get_emoji('proses')} Please wait

**Vzoel Fox's Lutpan**"""

        await safe_edit_premium(event, processing_msg)

        # Get payment info
        info = payment_manager.get_payment_info()
        stats = payment_manager.get_stats()

        if info:
            # Build response
            response = f"""{get_emoji('utama')} **Payment Information**

"""
            # Show structured data if available
            raw_text = info.get('raw_text', '')
            if raw_text:
                response += f"{raw_text}\n\n"

            response += f"""{get_emoji('telegram')} **Quick Actions:**
• .getqr - Show QR code ({stats['qr_codes_count']} stored)
• .setget - Update payment info
• .setgetqr - Add QR code

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""

        else:
            response = f"""{get_emoji('kuning')} **No payment info set**

{get_emoji('telegram')} Use .setget to configure payment details

{get_emoji('aktif')} **Example:**
.setget Bank: BCA
Account: 1234567890
Name: Vzoel Fox's

{get_emoji('biru')} **Or multiline:**
.setget Payment Gateway: Dana/Gopay/OVO
Number: 081234567890

**Vzoel Fox's Lutpan** Payment System
**Contact:** @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
