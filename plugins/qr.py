import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
QR Code Generator Plugin for Vzoel Fox's Userbot
Fitur: Generate QR code untuk link t.me dengan Vzoel Fox's branding
Founder Userbot: Vzoel Fox's Lutpan
Version: 1.0.0 - QR Code Generator System
"""

from telethon import events
import asyncio
import random
import json
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
import io
import base64
from pathlib import Path

# Plugin Info
PLUGIN_INFO = {
    "name": "qr",
    "version": "1.0.0",
    "description": "Generate QR code untuk link t.me dengan Vzoel Fox's branding",
    "author": "Founder Userbot: Vzoel Fox's Lutpan",
    "commands": [".qr", ".qrinfo"],
    "features": ["QR code generation", "t.me link support", "Vzoel Fox's branding", "Custom styling"]
}

__version__ = "1.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Lutpan"

# Global references (will be set by vzoel_init)
vzoel_client = None
vzoel_emoji = None

# QR code directory
QR_DIR = Path("downloads/qr")
QR_DIR.mkdir(parents=True, exist_ok=True)

# QR Code styling templates
QR_STYLES = [
    {
        "name": "Vzoel Fox's Classic",
        "fill_color": "#1a1a1a",
        "back_color": "#ffffff",
        "border": 4,
        "box_size": 10
    },
    {
        "name": "Telegram Blue",
        "fill_color": "#0088cc", 
        "back_color": "#ffffff",
        "border": 4,
        "box_size": 10
    },
    {
        "name": "Dark Mode",
        "fill_color": "#ffffff",
        "back_color": "#1a1a1a", 
        "border": 4,
        "box_size": 10
    },
    {
        "name": "Premium Gold",
        "fill_color": "#FFD700",
        "back_color": "#000000",
        "border": 5,
        "box_size": 12
    },
    {
        "name": "Neon Green",
        "fill_color": "#39FF14",
        "back_color": "#000000",
        "border": 4,
        "box_size": 10
    },
    {
        "name": "Electric Blue",
        "fill_color": "#00D4FF",
        "back_color": "#ffffff",
        "border": 4,
        "box_size": 10
    }
]

async def vzoel_init(client, emoji_handler):
    """Plugin initialization"""
    global vzoel_client, vzoel_emoji

    # Set global references
    vzoel_client = client
    vzoel_emoji = emoji_handler
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} QR Code Plugin loaded - QR generator ready")

def validate_telegram_link(url):
    """Validate if URL is a valid Telegram link"""
    telegram_domains = [
        "t.me/",
        "telegram.me/",
        "telegram.org/",
        "telegram.dog/"
    ]
    
    url_lower = url.lower()
    for domain in telegram_domains:
        if domain in url_lower:
            return True
    return False

def add_vzoel_branding(qr_img, style, url):
    """Add Vzoel Fox's branding to QR code"""
    try:
        # Convert to RGB if needed
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')
        
        # Create larger canvas for branding
        canvas_width = qr_img.width + 100
        canvas_height = qr_img.height + 150
        
        canvas = Image.new('RGB', (canvas_width, canvas_height), style['back_color'])
        
        # Paste QR code in center
        qr_x = (canvas_width - qr_img.width) // 2
        qr_y = 50
        canvas.paste(qr_img, (qr_x, qr_y))
        
        draw = ImageDraw.Draw(canvas)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 24)
            subtitle_font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 16)
            small_font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 12)
        except:
            try:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            except:
                title_font = subtitle_font = small_font = None
        
        # Text color (opposite of background)
        text_color = "#000000" if style['back_color'] == "#ffffff" else "#ffffff"
        accent_color = style['fill_color']
        
        # Draw title
        title = "Vzoel Fox's QR Generator"
        if title_font:
            try:
                # Try modern textbbox method first
                title_bbox = draw.textbbox((0, 0), title, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
            except:
                # Fallback to textsize for older PIL versions
                try:
                    title_width, _ = draw.textsize(title, font=title_font)
                except:
                    title_width = len(title) * 12  # Rough estimate
            title_x = (canvas_width - title_width) // 2
            draw.text((title_x, 10), title, fill=accent_color, font=title_font)
        
        # Draw URL info
        if len(url) > 40:
            display_url = url[:37] + "..."
        else:
            display_url = url
            
        url_text = f"Link: {display_url}"
        if subtitle_font:
            try:
                url_bbox = draw.textbbox((0, 0), url_text, font=subtitle_font)
                url_width = url_bbox[2] - url_bbox[0]
            except:
                try:
                    url_width, _ = draw.textsize(url_text, font=subtitle_font)
                except:
                    url_width = len(url_text) * 10
            url_x = (canvas_width - url_width) // 2
            draw.text((url_x, qr_y + qr_img.height + 20), url_text, fill=text_color, font=subtitle_font)
        
        # Draw style info
        style_text = f"Style: {style['name']}"
        if small_font:
            try:
                style_bbox = draw.textbbox((0, 0), style_text, font=small_font)
                style_width = style_bbox[2] - style_bbox[0]
            except:
                try:
                    style_width, _ = draw.textsize(style_text, font=small_font)
                except:
                    style_width = len(style_text) * 8
            style_x = (canvas_width - style_width) // 2
            draw.text((style_x, qr_y + qr_img.height + 50), style_text, fill=text_color, font=small_font)
        
        # Draw footer branding
        footer = "Vzoel Fox's Userbot"
        author = "Founder: Vzoel Fox's Lutpan"
        
        if small_font:
            try:
                try:
                    footer_bbox = draw.textbbox((0, 0), footer, font=small_font)
                except:
                    footer_width = len(footer) * 8
            except:
                try:
                    footer_width, _ = draw.textsize(footer, font=small_font)
                except:
                    footer_width = len(footer) * 8
            footer_x = (canvas_width - footer_width) // 2
            draw.text((footer_x, canvas_height - 35), footer, fill=accent_color, font=small_font)
            
            try:
                author_bbox = draw.textbbox((0, 0), author, font=small_font)
                author_width = author_bbox[2] - author_bbox[0]
            except:
                try:
                    author_width, _ = draw.textsize(author, font=small_font)
                except:
                    author_width = len(author) * 8
            author_x = (canvas_width - author_width) // 2
            draw.text((author_x, canvas_height - 20), author, fill=text_color, font=small_font)
        
        # Draw decorative border
        border_width = 3
        draw.rectangle([0, 0, canvas_width, border_width], fill=accent_color)
        draw.rectangle([0, 0, border_width, canvas_height], fill=accent_color)
        draw.rectangle([canvas_width-border_width, 0, canvas_width, canvas_height], fill=accent_color)
        draw.rectangle([0, canvas_height-border_width, canvas_width, canvas_height], fill=accent_color)
        
        return canvas
        
    except Exception as e:
        print(f"Error adding branding: {e}")
        return qr_img

def generate_qr_code(url, style):
    """Generate QR code with specified style"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=style['box_size'],
            border=style['border'],
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color=style['fill_color'], back_color=style['back_color'])
        
        # Add Vzoel Fox's branding
        branded_img = add_vzoel_branding(qr_img, style, url)
        
        return branded_img
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

@events.register(events.NewMessage(pattern=r'\.qr(?:\s+(.+))?'))
async def qr_handler(event):
    """Generate QR code command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client
        
        # Check dependencies
        if not QR_AVAILABLE:
            error_msg = f"""{get_emoji('merah')} QR dependencies tidak terinstall
            
{get_emoji('kuning')} Instalasi diperlukan:
• pip install qrcode[pil]
• pip install pillow

{get_emoji('aktif')} Fitur yang membutuhkan QR:
• QR code generation
• Image processing
• Custom styling
• Branding overlay

{get_emoji('telegram')} Install dependencies untuk menggunakan fitur ini

{get_emoji('utama')} Vzoel Fox's QR Generator"""
            await safe_edit_premium(event, error_msg)
            return
        
        url = event.pattern_match.group(1)
        
        if not url:
            help_msg = f"""{get_emoji('kuning')} Gunakan format: .qr [link]
            
{get_emoji('aktif')} Contoh penggunaan:
.qr https://t.me/vzoel_fox
.qr https://t.me/joinchat/xxxxx  
.qr https://telegram.me/channel

{get_emoji('centang')} Supported links:
• t.me/username
• t.me/joinchat/xxxxx
• telegram.me/xxxxx
• telegram.org/xxxxx

{get_emoji('biru')} Features:
• 6+ QR styles (random)
• Vzoel Fox's branding
• High quality output
• Auto file cleanup

{get_emoji('utama')} Vzoel Fox's QR Generator"""
            await safe_edit_premium(event, help_msg)
            return
        
        # Validate URL
        if not validate_telegram_link(url):
            warning_msg = f"""{get_emoji('kuning')} Link bukan Telegram link
            
{get_emoji('merah')} Link: {url}
            
{get_emoji('aktif')} Supported domains:
• t.me/
• telegram.me/  
• telegram.org/
• telegram.dog/

{get_emoji('centang')} Akan tetap generate QR code...

{get_emoji('utama')} Vzoel Fox's QR Generator"""
            await safe_edit_premium(event, warning_msg)
            await asyncio.sleep(3)
        
        # Show processing message
        style = random.choice(QR_STYLES)
        processing_msg = f"{get_emoji('loading')} Generating QR code dengan {style['name']} style..."
        await safe_edit_premium(event, processing_msg)
        
        try:
            # Generate QR code
            qr_img = generate_qr_code(url, style)
            
            if qr_img:
                # Save QR code
                qr_filename = f"qr_{random.randint(10000, 99999)}.png"
                qr_path = QR_DIR / qr_filename
                qr_img.save(qr_path, 'PNG', optimize=True, quality=95)
                
                # Prepare caption
                caption = f"""{get_emoji('utama')} QR CODE GENERATED
                
{get_emoji('centang')} Link: {url}
{get_emoji('adder1')} Style: {style['name']}
{get_emoji('aktif')} Colors: {style['fill_color']} on {style['back_color']}
{get_emoji('proses')} Size: {qr_img.size[0]}x{qr_img.size[1]}px
{get_emoji('kuning')} Quality: High (95%)

{get_emoji('telegram')} Scan dengan kamera atau Telegram
{get_emoji('biru')} Branding by Vzoel Fox's

{get_emoji('adder2')} Generated by Vzoel Fox's Userbot
{get_emoji('petir')} Founder: Vzoel Fox's Lutpan"""
                
                # Send the QR code
                await event.client.send_file(
                    event.chat_id,
                    qr_path,
                    caption=caption,
                    formatting_entities=create_premium_entities(caption),
                    reply_to=event.id
                )
                
                # Delete processing message
                await event.delete()
                
                # Clean up file after delay
                async def cleanup_qr():
                    await asyncio.sleep(300)  # Wait 5 minutes
                    try:
                        if qr_path.exists():
                            qr_path.unlink()
                    except:
                        pass
                
                asyncio.create_task(cleanup_qr())
                
            else:
                error_msg = f"""{get_emoji('merah')} Gagal generate QR code
                
{get_emoji('kuning')} Kemungkinan masalah:
• URL terlalu panjang
• Format URL tidak valid
• Error processing image
• Memory insufficient

{get_emoji('aktif')} Solusi:
• Coba URL yang lebih pendek
• Check format URL
• Restart aplikasi
• Free up memory

{get_emoji('utama')} Vzoel Fox's QR Generator"""
                await safe_edit_premium(event, error_msg)
                
        except Exception as e:
            error_msg = f"""{get_emoji('merah')} Error generating QR code
            
{get_emoji('kuning')} Error: {str(e)[:100]}...

{get_emoji('aktif')} Troubleshooting:
• Check URL validity
• Ensure dependencies installed
• Try different style
• Restart application

{get_emoji('telegram')} Contact support jika masalah persist

{get_emoji('utama')} Vzoel Fox's QR Generator"""
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.qrinfo'))
async def qr_info_handler(event):
    """Show QR plugin information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Count generated files
        qr_count = len(list(QR_DIR.glob("*.png")))
        
        # List available styles
        style_names = [style['name'] for style in QR_STYLES]
        style_list = ', '.join(style_names[:3]) + f' dan {len(QR_STYLES)-3} lainnya'
        
        qr_info = f"""{signature} Vzoel Fox's QR Code Generator
        
{get_emoji('utama')} Features:
• Generate QR untuk link t.me
• 6+ premium QR styles
• Vzoel Fox's branding otomatis
• High quality PNG output
• Auto file cleanup system
• Premium emoji integration

{get_emoji('centang')} Commands:
.qr [link] - Generate QR code
.qrinfo - Info sistem QR

{get_emoji('telegram')} QR Styles ({len(QR_STYLES)} total):
{style_list}

{get_emoji('aktif')} Supported Links:
• t.me/username
• t.me/joinchat/xxxxx
• telegram.me/channel
• telegram.org/group
• telegram.dog/bot

{get_emoji('proses')} Technical Specs:
• Format: PNG optimized
• Quality: 95% compression
• Branding: Vzoel Fox's watermark
• Colors: Custom per style
• Auto cleanup: 5 minutes

{get_emoji('kuning')} Statistics:
• Generated QRs: {qr_count} files
• Storage: {QR_DIR}
• Dependencies: qrcode, PIL

{get_emoji('biru')} Usage Examples:
.qr https://t.me/vzoel_fox
.qr https://t.me/joinchat/xxxxx
.qr https://telegram.me/channel

{get_emoji('adder2')} Premium QR Generator
{get_emoji('adder1')} By Vzoel Fox's Userbot
{get_emoji('petir')} Founder: Vzoel Fox's Lutpan"""
        
        await safe_edit_premium(event, qr_info)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator