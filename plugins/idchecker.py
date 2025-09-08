import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, create_premium_entities, safe_send_premium, safe_edit_premium, is_owner, PREMIUM_EMOJIS

"""
Enhanced ID Checker Plugin for VzoelFox Userbot - Premium Edition
Fitur: Advanced ID checking dengan premium display
Founder Userbot: Vzoel Fox's Ltpn
Version: 3.0.0 - Premium ID Checker System
"""

from telethon import events
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import asyncio
import random

# Plugin info
__version__ = "3.0.0"
__author__ = "Founder Userbot: Vzoel Fox's Ltpn"

# Global variable to control animation loops
animation_tasks = {}

async def vzoel_init(client, vzoel_emoji=None):
    """Plugin initialization"""
    signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
    print(f"{signature} ID Checker Plugin loaded - Animated ID detection ready")

@events.register(events.NewMessage(pattern=r'\.id(?: (.+))?'))
async def id_checker_handler(event):
    """ID checker with animated process and unlimited loop results"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        # Get chat ID for animation management
        chat_id = event.chat_id
        # Don't cancel existing animations - let them run permanently
        # Users can only stop by using .stop command or restarting bot
        
        target_user = None
        args = event.pattern_match.group(1)
        
        # Phase 1: Determine target from arguments or reply
        if event.reply_to_msg_id:
            # Get user from reply
            process_msg = f"{get_emoji('loading')} Analyzing replied message..."
            msg = await event.edit(process_msg)
            await asyncio.sleep(0.8)
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg.sender:
                    target_user = reply_msg.sender
                else:
                    error_msg = f"{get_emoji('merah')} Cannot get user from reply"
                    await safe_edit_premium(msg, error_msg)
                    return
            except Exception as e:
                error_msg = f"{get_emoji('merah')} Error getting reply: {str(e)}"
                await safe_edit_premium(msg, error_msg)
                return
                
        elif args:
            # Get user from username/mention
            username = args.strip().replace('@', '')
            process_msg = f"{get_emoji('proses')} Searching for user: @{username}..."
            msg = await event.edit(process_msg)
            await asyncio.sleep(0.8)
            try:
                target_user = await event.client.get_entity(username)
            except (UsernameNotOccupiedError, UsernameInvalidError):
                error_msg = f"{get_emoji('merah')} Username @{username} not found"
                await safe_edit_premium(msg, error_msg)
                return
            except Exception as e:
                error_msg = f"{get_emoji('merah')} Error finding user: {str(e)}"
                await safe_edit_premium(msg, error_msg)
                return
        else:
            # No target specified
            help_msg = f"{get_emoji('kuning')} Usage: .id @username or .id (reply to message)"
            msg = await event.edit(help_msg)
            await safe_edit_premium(msg, help_msg)
            return
        
        # Phase 2: Processing animation sequence
        processing_phases = [
            "Connecting to VzoelFox servers...",
            "Validating user credentials...", 
            "Scanning user database...",
            "Retrieving user information...",
            "Processing user data...",
            "Finalizing ID lookup..."
        ]
        
        for phase in processing_phases:
            process_msg = f"{get_emoji('aktif')} {phase}"
            await safe_edit_premium(msg, process_msg)
            await asyncio.sleep(0.7)
        
        # Final processing message
        final_process = f"{get_emoji('centang')} User found! Generating display..."
        await safe_edit_premium(msg, final_process)
        await asyncio.sleep(1)
        
        # Extract user information
        user_id = target_user.id
        username = target_user.username or "No Username"
        first_name = target_user.first_name or ""
        last_name = target_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "No Name"
        
        # Start unlimited loop animation
        animation_task = asyncio.create_task(
            animate_id_display(msg, user_id, username, full_name)
        )
        animation_tasks[chat_id] = animation_task
        
        if vzoel_client:
            vzoel_client.increment_command_count()

async def animate_id_display(msg, user_id, username, full_name):
    """Unlimited loop animation for ID display"""
    display_states = [
        f"""1. ID: {user_id}
2. Username: @{username}  
3. Nama User: {full_name}
4. By VzoelFox Assistant""",
        
        f"""1. ID: {user_id}
2. Username: @{username}
3. Nama User: {full_name}
4. By VzoelFox Assistant""",
        
        f"""1. ID: {user_id}
2. Username: @{username}
3. Nama User: {full_name}
4. By VzoelFox Assistant""",
        
        f"""1. ID: {user_id}
2. Username: @{username}
3. Nama User: {full_name}
4. By VzoelFox Assistant"""
    ]
    
    # Available emojis for rotation (only mapped ones)
    available_emojis = [
        'utama', 'centang', 'petir', 'loading', 'kuning', 'biru', 
        'merah', 'proses', 'aktif', 'adder1', 'adder2', 'telegram'
    ]
    
    try:
        while True:
            for state in display_states:
                # Select random emoji for this iteration
                random_emoji = random.choice(available_emojis)
                
                # Format with random emoji
                formatted_display = f"{get_emoji(random_emoji)} {state}"
                
                # Edit message
                await safe_edit_premium(msg, formatted_display)
                
                # Wait before next animation frame
                await asyncio.sleep(1.5)
                
    except asyncio.CancelledError:
        # Animation was cancelled (user ran another command)
        pass
    except Exception as e:
        # Handle any errors during animation
        try:
            error_msg = f"{get_emoji('merah')} Animation error: {str(e)}"
            await safe_edit_premium(msg, error_msg)
        except:
            pass

@events.register(events.NewMessage(pattern=r'\.stopid'))
async def stop_id_animation_handler(event):
    """Stop ID animation loop"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        
        chat_id = event.chat_id
        
        if chat_id in animation_tasks:
            animation_tasks[chat_id].cancel()
            del animation_tasks[chat_id]
            stop_msg = f"{get_emoji('centang')} ID animation stopped"
            await safe_edit_premium(event, stop_msg)
        else:
            no_animation_msg = f"{get_emoji('kuning')} No ID animation running"
            await safe_edit_premium(event, no_animation_msg)
        
        if vzoel_client:
            vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.idinfo'))
async def id_info_handler(event):
    """Show information about ID checker system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client

        
        signature = f"{get_emoji('utama')}{get_emoji('adder1')}{get_emoji('petir')}"
        
        id_info = f"""**{signature} VzoelFox ID Checker**

{get_emoji('utama')} **Usage Methods:**
• `.id @username` - Check by username
• `.id` (reply) - Check replied user
• `.stopid` - Stop animation loop

{get_emoji('centang')} **Process Animation:**
1. Connecting to VzoelFox servers
2. Validating user credentials  
3. Scanning user database
4. Retrieving user information
5. Processing user data
6. Finalizing ID lookup

{get_emoji('aktif')} **Display Features:**
• Unlimited loop animation
• Random emoji rotation
• User ID display
• Username detection
• Full name resolution
• VzoelFox branding

{get_emoji('telegram')} **Information Shown:**
1. User ID (numeric)
2. Username (@handle)
3. Full name (first + last)
4. VzoelFox Assistant credit

**By VzoelFox Assistant**"""
        
        msg = await event.edit(id_info)
        await safe_edit_premium(msg, id_info)
        if vzoel_client:
            vzoel_client.increment_command_count()
