"""
Vzoel Fox's Lutpan - Payment Plugin
Payment gateway and QR code management with multi-method support

Commands:
- .getfileid - Extract file_id from image (reply to image)
- .setgetqr - Store QR code for quick display
- .getqr - Display stored payment QR code
- .setget <info> - Set payment information (supports multiple methods)
- .get - Show all payment methods with checklist mapping

Multi-Method Examples:
1. Double newline separator:
   .setget Bank: BCA
   Account: 123

   E-Wallet: Dana
   Number: 081234567890

2. Pipe separator:
   .setget Bank: BCA | E-Wallet: Dana | Crypto: USDT

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
            await safe_edit_premium(event, f"{get_emoji('kuning')} Reply to an image to get file_id\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing message
        processing_msg = f"""{get_emoji('loading')} EXTRACTING FILE_ID

{get_emoji('proses')} Reading message
{get_emoji('telegram')} Please wait

VZOEL FOX'S LUTPAN"""

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
            response = f"""{get_emoji('centang')} FILE ID EXTRACTED

{get_emoji('aktif')} Type: {file_type}
{get_emoji('proses')} File ID: `{file_id}`

{get_emoji('telegram')} USAGE:
Copy the file_id above or use .setgetqr to store as QR code

{get_emoji('biru')} TIPS:
Reply to this message with .setgetqr to save automatically

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} NO FILE FOUND

{get_emoji('kuning')} Please reply to a message containing:
• Photo
• Image document

{get_emoji('telegram')} Then use .getfileid again

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.setgetqr(?: (.+))?'))
async def set_qr_handler(event):
    """Store QR code file_id"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Get description if provided
        description = None
        match = event.pattern_match.group(1)
        if match:
            description = match.strip()

        # Check if replying to message
        if not event.is_reply:
            await safe_edit_premium(event, f"{get_emoji('kuning')} Reply to QR image with .setgetqr\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} STORING QR CODE

{get_emoji('proses')} Extracting file_id
{get_emoji('telegram')} Saving to database

VZOEL FOX'S LUTPAN"""

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
                response = f"""{get_emoji('centang')} QR CODE SAVED

{get_emoji('aktif')} File ID: `{file_id}`
{get_emoji('proses')} Description: {description or 'Payment QR Code'}
{get_emoji('telegram')} Total QR codes: {qr_count}

{get_emoji('biru')} QUICK ACCESS:
Use .getqr to display this QR code instantly

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""
            else:
                response = f"""{get_emoji('merah')} SAVE FAILED

{get_emoji('kuning')} Please try again

VZOEL FOX'S LUTPAN"""
        else:
            response = f"""{get_emoji('merah')} NO IMAGE FOUND

{get_emoji('kuning')} Reply to QR code image
{get_emoji('telegram')} Then use .setgetqr

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.getqr'))
async def get_qr_handler(event):
    """Display stored QR code"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} LOADING QR CODE

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

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
                    caption=f"""{get_emoji('utama')} {description}

{get_emoji('centang')} Scan QR code to pay
{get_emoji('telegram')} Quick payment access

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""
                )
            except Exception as e:
                await event.respond(f"{get_emoji('merah')} Failed to send QR: {e}\n\nVZOEL FOX'S LUTPAN")

        else:
            response = f"""{get_emoji('kuning')} NO QR CODE STORED

{get_emoji('telegram')} Use .setgetqr to store QR code first

{get_emoji('aktif')} STEPS:
1. Find your payment QR image
2. Reply to it with .getfileid
3. Reply to it with .setgetqr

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""

            await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.setget (.+)'))
async def set_payment_info_handler(event):
    """Set payment gateway information (supports multiple methods)"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        info_text = event.pattern_match.group(1).strip()

        # Processing
        processing_msg = f"""{get_emoji('loading')} STORING PAYMENT INFO

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Parse payment methods (support multiple methods separated by newlines or |)
        payment_methods = []

        # Split by newline or pipe separator
        if '\n\n' in info_text:
            # Multiple methods separated by double newline
            raw_methods = info_text.split('\n\n')
        elif '|' in info_text:
            # Multiple methods separated by pipe
            raw_methods = info_text.split('|')
        else:
            # Single method
            raw_methods = [info_text]

        for method_text in raw_methods:
            method_text = method_text.strip()
            if not method_text:
                continue

            method_info = {'raw_text': method_text}

            # Parse key:value pairs
            for line in method_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key_clean = key.strip().lower()
                    method_info[key_clean] = value.strip()

                    # Detect payment type
                    if key_clean in ['bank', 'e-wallet', 'ewallet', 'payment', 'type']:
                        method_info['payment_type'] = value.strip()

            payment_methods.append(method_info)

        # Save all methods
        payment_info = {
            'methods': payment_methods,
            'count': len(payment_methods),
            'raw_text': info_text
        }

        success = payment_manager.set_payment_info(payment_info)

        if success:
            # Build checklist display
            checklist = ""
            for i, method in enumerate(payment_methods, 1):
                payment_type = method.get('payment_type', method.get('bank', method.get('e-wallet', 'Payment Method')))
                checklist += f"{get_emoji('centang')} {i}. {payment_type}\n"

            response = f"""{get_emoji('centang')} PAYMENT METHODS SAVED

{get_emoji('aktif')} Total Methods: {len(payment_methods)}

{get_emoji('biru')} SAVED METHODS:
{checklist}
{get_emoji('telegram')} Use .get to display all payment info

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""
        else:
            response = f"""{get_emoji('merah')} SAVE FAILED

{get_emoji('kuning')} Please try again

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r'\.get'))
async def get_payment_info_handler(event):
    """Display payment information with checklist mapping"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, payment_manager

        if not payment_manager:
            await safe_edit_premium(event, f"{get_emoji('merah')} Payment manager not initialized\n\nVZOEL FOX'S LUTPAN")
            return

        # Processing
        processing_msg = f"""{get_emoji('loading')} LOADING PAYMENT INFO

{get_emoji('proses')} Please wait

VZOEL FOX'S LUTPAN"""

        await safe_edit_premium(event, processing_msg)

        # Get payment info
        info = payment_manager.get_payment_info()
        stats = payment_manager.get_stats()

        if info:
            # Build response with checklist mapping
            response = f"""{get_emoji('utama')} PAYMENT INFORMATION

"""
            # Show multiple methods if available
            methods = info.get('methods', [])

            if methods:
                # Checklist mapping header
                response += f"{get_emoji('biru')} AVAILABLE PAYMENT METHODS:\n\n"

                # Display each method with checklist
                for i, method in enumerate(methods, 1):
                    payment_type = method.get('payment_type', method.get('bank', method.get('e-wallet', f'Method {i}')))
                    response += f"{get_emoji('centang')} {i}. {payment_type}\n"

                    # Show details for each method
                    raw_text = method.get('raw_text', '')
                    if raw_text:
                        # Indent method details
                        for line in raw_text.split('\n'):
                            if line.strip():
                                response += f"   {line}\n"
                    response += "\n"

            else:
                # Fallback to raw text if no structured methods
                raw_text = info.get('raw_text', '')
                if raw_text:
                    response += f"{raw_text}\n\n"

            response += f"""{get_emoji('telegram')} QUICK ACTIONS:
• .getqr - Show QR code ({stats['qr_codes_count']} stored)
• .setget - Update payment info
• .setgetqr - Add QR code

{get_emoji('aktif')} Total Payment Methods: {len(methods) if methods else 1}

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""

        else:
            response = f"""{get_emoji('kuning')} NO PAYMENT INFO SET

{get_emoji('telegram')} Use .setget to configure payment details

{get_emoji('aktif')} SINGLE METHOD EXAMPLE:
.setget Bank: BCA
Account: 1234567890
Name: Vzoel Fox's

{get_emoji('biru')} MULTIPLE METHODS EXAMPLE:
.setget Bank: BCA
Account: 1234567890
Name: Vzoel Fox's

E-Wallet: Dana
Number: 081234567890
Name: Vzoel Fox's

{get_emoji('centang')} OR USE PIPE SEPARATOR:
.setget Bank: BCA | E-Wallet: Dana | Crypto: USDT

VZOEL FOX'S LUTPAN Payment System
CONTACT: @VZLfxs"""

        await safe_edit_premium(event, response)

        if vzoel_client:
            vzoel_client.increment_command_count()
