import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced Profile Card Plugin for VzoelFox Userbot - Premium Edition
Fitur: Generate profile card seperti cardd.co dengan template random
Founder Userbot: Vzoel Fox's Ltpn
Version: 1.0.0 - Profile Card Generator
"""

from telethon import events, functions
import asyncio
import random
import json
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import io
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
from pathlib import Path

# Plugin Info
PLUGIN_INFO = {
    "name": "profil",
    "version": "1.0.0",
    "description": "Generate profile card seperti cardd.co dengan template random",
    "author": "Founder Userbot: Vzoel Fox's Ltpn",
    "commands": [".card", ".pinfo"],
    "features": ["Profile card generation", "Random border templates", "cardd.co style", "Premium emoji", "VzoelFox branding"]
}

__version__ = "1.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Profile card directory
PROFILE_DIR = Path("downloads/profil")
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Border templates - berbagai style border untuk random selection
BORDER_TEMPLATES = [
    # Gradient borders
    {
        "name": "Gradient Sunset",
        "colors": ["#FF6B35", "#F7931E", "#FFD23F"],
        "style": "gradient",
        "width": 8
    },
    {
        "name": "Ocean Wave", 
        "colors": ["#00B4DB", "#0083B0", "#00A8CC"],
        "style": "gradient",
        "width": 10
    },
    {
        "name": "Purple Dream",
        "colors": ["#667eea", "#764ba2", "#f093fb"],
        "style": "gradient", 
        "width": 12
    },
    {
        "name": "Forest Green",
        "colors": ["#56ab2f", "#a8e6cf", "#2F7D32"],
        "style": "gradient",
        "width": 8
    },
    # Solid borders
    {
        "name": "Electric Blue",
        "colors": ["#00D4FF"],
        "style": "solid",
        "width": 6
    },
    {
        "name": "Hot Pink",
        "colors": ["#FF1493"],
        "style": "solid", 
        "width": 5
    },
    {
        "name": "Golden",
        "colors": ["#FFD700"],
        "style": "solid",
        "width": 7
    },
    # Neon borders
    {
        "name": "Neon Green",
        "colors": ["#39FF14"],
        "style": "neon",
        "width": 4
    },
    {
        "name": "Neon Pink", 
        "colors": ["#FF10F0"],
        "style": "neon",
        "width": 4
    },
    {
        "name": "Cyber Blue",
        "colors": ["#00FFFF"],
        "style": "neon",
        "width": 5
    },
    # Pastel borders
    {
        "name": "Soft Peach",
        "colors": ["#FFB3BA", "#FFDFBA", "#FFFFBA"],
        "style": "gradient",
        "width": 6
    },
    {
        "name": "Mint Fresh",
        "colors": ["#B3FFB3", "#BAE1FF", "#BFFCC6"],
        "style": "gradient",
        "width": 6
    },
    # Dark themed
    {
        "name": "Dark Matter",
        "colors": ["#2C3E50", "#34495E", "#1ABC9C"],
        "style": "gradient",
        "width": 10
    },
    {
        "name": "Shadow",
        "colors": ["#1A1A1A"],
        "style": "solid",
        "width": 8
    }
]

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} Profile Card Plugin loaded - Profile card generator ready")

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_gradient(width, height, colors):
    """Create gradient image from colors"""
    if len(colors) == 1:
        img = Image.new('RGB', (width, height), hex_to_rgb(colors[0]))
        return img
    
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    if len(colors) == 2:
        # Simple gradient
        color1 = hex_to_rgb(colors[0])
        color2 = hex_to_rgb(colors[1])
        
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        # Multi-color gradient
        sections = len(colors) - 1
        section_height = height // sections
        
        for i in range(sections):
            color1 = hex_to_rgb(colors[i])
            color2 = hex_to_rgb(colors[i + 1])
            start_y = i * section_height
            end_y = start_y + section_height
            
            for y in range(start_y, min(end_y, height)):
                ratio = (y - start_y) / section_height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def apply_border(image, border_template):
    """Apply border to image based on template"""
    width, height = image.size
    border_width = border_template["width"]
    
    # Create new image with border
    new_width = width + (border_width * 2)
    new_height = height + (border_width * 2)
    
    if border_template["style"] == "gradient":
        # Create gradient border
        border_img = create_gradient(new_width, new_height, border_template["colors"])
        # Paste original image in center
        border_img.paste(image, (border_width, border_width))
        return border_img
    
    elif border_template["style"] == "solid":
        # Create solid color border
        color = hex_to_rgb(border_template["colors"][0])
        border_img = Image.new('RGB', (new_width, new_height), color)
        border_img.paste(image, (border_width, border_width))
        return border_img
    
    elif border_template["style"] == "neon":
        # Create neon glow effect
        color = hex_to_rgb(border_template["colors"][0])
        border_img = Image.new('RGB', (new_width, new_height), (0, 0, 0))
        
        # Create glow effect
        glow = Image.new('RGB', (new_width, new_height), color)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=border_width//2))
        
        # Composite images
        border_img.paste(glow, (0, 0))
        border_img.paste(image, (border_width, border_width))
        return border_img
    
    return image

async def get_profile_photo(client, user_id):
    """Download profile photo"""
    try:
        user = await client.get_entity(user_id)
        if user.photo:
            photo_path = await client.download_profile_photo(user, file=PROFILE_DIR / f"temp_photo_{user_id}.jpg")
            return photo_path
        else:
            return None
    except Exception as e:
        print(f"Error downloading profile photo: {e}")
        return None

def create_default_avatar(name):
    """Create default avatar with initials"""
    size = (200, 200)
    img = Image.new('RGB', size, (64, 64, 64))
    draw = ImageDraw.Draw(img)
    
    # Get initials
    words = name.split()
    initials = ""
    for word in words[:2]:
        if word:
            initials += word[0].upper()
    
    if not initials:
        initials = "?"
    
    # Try to load font
    try:
        font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 80)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Draw initials
    if font:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        draw.text((x, y), initials, fill=(255, 255, 255), font=font)
    
    return img

async def create_profile_card(user_info, photo_path=None, border_template=None):
    """Create profile card like cardd.co"""
    
    # Card dimensions
    card_width = 400
    card_height = 600
    
    # Create base card
    card = Image.new('RGB', (card_width, card_height), (255, 255, 255))
    draw = ImageDraw.Draw(card)
    
    # Load or create profile photo
    if photo_path and os.path.exists(photo_path):
        try:
            profile_img = Image.open(photo_path)
            # Resize and crop to circle
            profile_img = profile_img.resize((150, 150))
            
            # Create circular mask
            mask = Image.new('L', (150, 150), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 150, 150), fill=255)
            
            # Apply mask
            profile_img.putalpha(mask)
            
            # Create new image with circle
            circle_img = Image.new('RGBA', (150, 150), (255, 255, 255, 0))
            circle_img.paste(profile_img, (0, 0), profile_img)
            
            # Convert to RGB for pasting
            temp_img = Image.new('RGB', (150, 150), (255, 255, 255))
            temp_img.paste(circle_img, (0, 0), circle_img)
            profile_img = temp_img
            
        except Exception as e:
            print(f"Error processing profile photo: {e}")
            profile_img = create_default_avatar(user_info.get('first_name', 'User'))
    else:
        profile_img = create_default_avatar(user_info.get('first_name', 'User'))
    
    # Paste profile photo
    photo_x = (card_width - 150) // 2
    photo_y = 50
    card.paste(profile_img, (photo_x, photo_y))
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 28)
        subtitle_font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 18)
        text_font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", 14)
    except:
        try:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        except:
            title_font = subtitle_font = text_font = None
    
    # Draw name
    name = user_info.get('first_name', '')
    if user_info.get('last_name'):
        name += f" {user_info['last_name']}"
    
    if title_font:
        name_bbox = draw.textbbox((0, 0), name, font=title_font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (card_width - name_width) // 2
        draw.text((name_x, 220), name, fill=(33, 37, 41), font=title_font)
    
    # Draw username
    username = user_info.get('username', '')
    if username:
        username_text = f"@{username}"
        if subtitle_font:
            username_bbox = draw.textbbox((0, 0), username_text, font=subtitle_font)
            username_width = username_bbox[2] - username_bbox[0]
            username_x = (card_width - username_width) // 2
            draw.text((username_x, 260), username_text, fill=(108, 117, 125), font=subtitle_font)
    
    # Draw bio
    bio = user_info.get('about', '')
    if bio:
        # Word wrap bio
        max_width = card_width - 40
        if text_font:
            words = bio.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=text_font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Limit to 4 lines
            lines = lines[:4]
            
            # Draw bio lines
            bio_y = 300
            for i, line in enumerate(lines):
                if i >= 4:
                    break
                line_bbox = draw.textbbox((0, 0), line, font=text_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (card_width - line_width) // 2
                draw.text((line_x, bio_y + (i * 20)), line, fill=(73, 80, 87), font=text_font)
    
    # Draw user ID
    user_id = user_info.get('id', '')
    if user_id:
        id_text = f"ID: {user_id}"
        if text_font:
            id_bbox = draw.textbbox((0, 0), id_text, font=text_font)
            id_width = id_bbox[2] - id_bbox[0]
            id_x = (card_width - id_width) // 2
            draw.text((id_x, 450), id_text, fill=(108, 117, 125), font=text_font)
    
    # Draw watermark
    watermark = "VzoelFox Card Generator"
    if text_font:
        watermark_bbox = draw.textbbox((0, 0), watermark, font=text_font)
        watermark_width = watermark_bbox[2] - watermark_bbox[0]
        watermark_x = (card_width - watermark_width) // 2
        draw.text((watermark_x, 520), watermark, fill=(206, 212, 218), font=text_font)
    
    # Add decorative elements
    draw.rectangle([50, 480, card_width-50, 482], fill=(0, 123, 255))
    
    # Apply border if provided
    if border_template:
        card = apply_border(card, border_template)
    
    return card

@events.register(events.NewMessage(pattern=r'\.card(?:\s+@?(.+))?'))
async def card_handler(event):
    """Generate profile card command"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        # Check dependencies
        if not PIL_AVAILABLE:
            error_msg = f"""{get_emoji('merah')} PIL/Pillow tidak terinstall
            
{get_emoji('kuning')} Instalasi diperlukan:
• pip install pillow
• pkg install pillow (Termux)

{get_emoji('aktif')} Fitur yang membutuhkan PIL:
• Image processing
• Profile card generation
• Border effects
• Font rendering

{get_emoji('telegram')} Install PIL untuk menggunakan fitur ini

{get_emoji('utama')} VzoelFox Card Generator"""
            await safe_edit_premium(event, error_msg)
            return
        
        target_user = None
        
        # Check if replying to a message
        if event.is_reply:
            reply = await event.get_reply_message()
            target_user = reply.sender
        else:
            # Check for username argument
            username = event.pattern_match.group(1)
            if username:
                username = username.strip().lstrip('@')
                try:
                    target_user = await event.client.get_entity(username)
                except Exception as e:
                    error_msg = f"""{get_emoji('merah')} User tidak ditemukan: @{username}
                    
{get_emoji('kuning')} Kemungkinan masalah:
• Username salah atau tidak ada
• User belum pernah berinteraksi dengan bot
• User memiliki privacy setting ketat
• Username baru diubah

{get_emoji('aktif')} Cara penggunaan:
.card @username - Generate card untuk user
.card (reply) - Generate card untuk user yang direply

{get_emoji('telegram')} Contoh:
.card @vzoel_fox
.card (balas pesan user)

{get_emoji('utama')} VzoelFox Card Generator"""
                    await safe_edit_premium(event, error_msg)
                    return
            else:
                # Use message sender
                target_user = await event.get_sender()
        
        if not target_user:
            error_msg = f"""{get_emoji('merah')} Tidak ada target user
            
{get_emoji('aktif')} Gunakan salah satu cara:
• .card @username
• .card (reply ke pesan user)
• .card (untuk profile sendiri)

{get_emoji('utama')} VzoelFox Card Generator"""
            await safe_edit_premium(event, error_msg)
            return
        
        # Show processing message
        processing_msg = f"{get_emoji('loading')} Generating profile card untuk {target_user.first_name}..."
        await safe_edit_premium(event, processing_msg)
        
        try:
            # Get user info
            user_info = {
                'id': target_user.id,
                'first_name': target_user.first_name or '',
                'last_name': target_user.last_name or '',
                'username': target_user.username or '',
                'about': ''
            }
            
            # Get full user info including bio
            try:
                full_user = await event.client(functions.users.GetFullUserRequest(target_user.id))
                if full_user.full_user.about:
                    user_info['about'] = full_user.full_user.about
            except Exception as e:
                print(f"Could not get full user info: {e}")
            
            # Download profile photo
            photo_path = await get_profile_photo(event.client, target_user.id)
            
            # Select random border template
            border_template = random.choice(BORDER_TEMPLATES)
            
            # Update processing message
            update_msg = f"{get_emoji('loading')} Creating card dengan {border_template['name']} border..."
            await safe_edit_premium(event, update_msg)
            
            # Create profile card
            card_img = await create_profile_card(user_info, photo_path, border_template)
            
            # Save card
            card_path = PROFILE_DIR / f"card_{target_user.id}_{random.randint(1000, 9999)}.png"
            card_img.save(card_path, 'PNG', optimize=True)
            
            # Prepare caption
            caption = f"""{get_emoji('utama')} PROFILE CARD GENERATED
            
{get_emoji('centang')} User: {user_info['first_name']} {user_info['last_name']}
{get_emoji('telegram')} Username: @{user_info['username'] if user_info['username'] else 'None'}
{get_emoji('aktif')} User ID: {user_info['id']}
{get_emoji('adder1')} Border: {border_template['name']}
{get_emoji('proses')} Style: {border_template['style'].title()}

{get_emoji('petir')} Generated by VzoelFox Card System"""
            
            # Send the card
            await event.client.send_file(
                event.chat_id,
                card_path,
                caption=caption,
                reply_to=event.id
            )
            
            # Delete processing message
            await event.delete()
            
            # Clean up temporary files
            if photo_path and os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except:
                    pass
            
            # Clean up card file after delay
            async def cleanup_card():
                await asyncio.sleep(300)  # Wait 5 minutes
                try:
                    if os.path.exists(card_path):
                        os.remove(card_path)
                except:
                    pass
            
            asyncio.create_task(cleanup_card())
            
        except Exception as e:
            error_msg = f"""{get_emoji('merah')} Error generating profile card
            
{get_emoji('kuning')} Error details: {str(e)}

{get_emoji('aktif')} Kemungkinan masalah:
• User profile tidak dapat diakses
• Foto profil bermasalah
• Error processing gambar
• Storage penuh

{get_emoji('telegram')} Solusi:
• Coba dengan user lain
• Restart bot
• Check storage space
• Try again in a few minutes

{get_emoji('utama')} VzoelFox Card Generator"""
            await safe_edit_premium(event, error_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.pinfo'))
async def profile_info_handler(event):
    """Show profile plugin information"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        # Count available border templates
        total_borders = len(BORDER_TEMPLATES)
        gradient_borders = len([b for b in BORDER_TEMPLATES if b['style'] == 'gradient'])
        solid_borders = len([b for b in BORDER_TEMPLATES if b['style'] == 'solid'])
        neon_borders = len([b for b in BORDER_TEMPLATES if b['style'] == 'neon'])
        
        # List some border names
        border_examples = [b['name'] for b in BORDER_TEMPLATES[:5]]
        border_list = ', '.join(border_examples)
        
        profile_info = f"""{signature} VzoelFox Profile Card Generator
        
{get_emoji('utama')} Features:
• Generate profile cards seperti cardd.co
• Random border templates
• Auto foto profil download
• Bio dan info lengkap
• Premium design quality
• Watermark VzoelFox branding

{get_emoji('centang')} Commands:
.card @username - Generate card untuk user
.card (reply) - Generate card dari reply
.pinfo - Info sistem profil

{get_emoji('telegram')} Border Templates ({total_borders} total):
• Gradient: {gradient_borders} styles
• Solid: {solid_borders} styles  
• Neon: {neon_borders} styles
• Examples: {border_list}

{get_emoji('aktif')} Card Info:
• Resolution: 400x600 (dengan border)
• Format: PNG optimized
• Style: cardd.co inspired
• Auto cleanup: 5 minutes

{get_emoji('proses')} Usage Examples:
.card @vzoel_fox - Card untuk user
.card @username - Target specific user
.card (reply pesan) - Card dari reply
.card - Card untuk diri sendiri

{get_emoji('adder2')} Technical:
• PIL/Pillow image processing
• Circular profile photos
• Font rendering dengan fallback
• Random template selection
• Automatic file cleanup

{get_emoji('kuning')} Output Location: {PROFILE_DIR}

{get_emoji('biru')} Powered by VzoelFox Technology

By VzoelFox Assistant"""
        
        await safe_edit_premium(event, profile_info)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

# Handler automatically registered via @events.register decorator