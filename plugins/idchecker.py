"""
VzoelFox's Assistant ID Checker Plugin
Advanced ID checker with animated process and unlimited loop display
Created by: Vzoel Fox's
Enhanced by: Vzoel Fox's Ltpn
"""

from telethon import events
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
import asyncio
import random

# Plugin info
__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

# Global variable to control animation loops
animation_tasks = {}

async def vzoel_init(client, vzoel_emoji):
    """Plugin initialization"""
    signature = vzoel_emoji.get_vzoel_signature(premium=True)
    print(f"{signature} ID Checker Plugin loaded - Animated ID detection ready")

@events.register(events.NewMessage(pattern=r'\.id(?: (.+))?'))
async def id_checker_handler(event):
    """ID checker with animated process and unlimited loop results"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        # Stop any existing animation for this chat
        chat_id = event.chat_id
        if chat_id in animation_tasks:
            animation_tasks[chat_id].cancel()
            del animation_tasks[chat_id]
        
        target_user = None
        args = event.pattern_match.group(1)
        
        # Phase 1: Determine target from arguments or reply
        if event.reply_to_msg_id:
            # Get user from reply
            process_msg = vzoel_emoji.format_emoji_response(
                ['loading'], "Analyzing replied message..."
            )
            msg = await event.edit(process_msg)
            await asyncio.sleep(0.8)
            
            try:
                reply_msg = await event.get_reply_message()
                if reply_msg.sender:
                    target_user = reply_msg.sender
                else:
                    error_msg = vzoel_emoji.format_emoji_response(
                        ['merah'], "Cannot get user from reply"
                    )
                    await msg.edit(error_msg)
                    return
            except Exception as e:
                error_msg = vzoel_emoji.format_emoji_response(
                    ['merah'], f"Error getting reply: {str(e)}"
                )
                await msg.edit(error_msg)
                return
                
        elif args:
            # Get user from username/mention
            username = args.strip().replace('@', '')
            
            process_msg = vzoel_emoji.format_emoji_response(
                ['proses'], f"Searching for user: @{username}..."
            )
            msg = await event.edit(process_msg)
            await asyncio.sleep(0.8)
            
            try:
                target_user = await event.client.get_entity(username)
            except (UsernameNotOccupiedError, UsernameInvalidError):
                error_msg = vzoel_emoji.format_emoji_response(
                    ['merah'], f"Username @{username} not found"
                )
                await msg.edit(error_msg)
                return
            except Exception as e:
                error_msg = vzoel_emoji.format_emoji_response(
                    ['merah'], f"Error finding user: {str(e)}"
                )
                await msg.edit(error_msg)
                return
        else:
            # No target specified
            help_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "Usage: .id @username or .id (reply to message)"
            )
            await event.edit(help_msg)
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
            process_msg = vzoel_emoji.format_emoji_response(
                ['aktif'], phase
            )
            await msg.edit(process_msg)
            await asyncio.sleep(0.7)
        
        # Final processing message
        final_process = vzoel_emoji.format_emoji_response(
            ['centang'], "User found! Generating display..."
        )
        await msg.edit(final_process)
        await asyncio.sleep(1)
        
        # Extract user information
        user_id = target_user.id
        username = target_user.username or "No Username"
        first_name = target_user.first_name or ""
        last_name = target_user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "No Name"
        
        # Start unlimited loop animation
        animation_task = asyncio.create_task(
            animate_id_display(msg, user_id, username, full_name, vzoel_emoji)
        )
        animation_tasks[chat_id] = animation_task
        
        vzoel_client.increment_command_count()

async def animate_id_display(msg, user_id, username, full_name, vzoel_emoji):
    """Unlimited loop animation for ID display"""
    display_states = [
        f"""**1. ID:** `{user_id}`
**2. Username:** @{username}  
**3. Nama User:** {full_name}
**4. By VzoelFox Assistant**""",
        
        f"""**1. ID:** `{user_id}`
**2. Username:** @{username}
**3. Nama User:** {full_name}
**4. By VzoelFox Assistant**""",
        
        f"""**1. ID:** `{user_id}`
**2. Username:** @{username}
**3. Nama User:** {full_name}
**4. By VzoelFox Assistant**""",
        
        f"""**1. ID:** `{user_id}`
**2. Username:** @{username}
**3. Nama User:** {full_name}
**4. By VzoelFox Assistant**"""
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
                formatted_display = vzoel_emoji.format_emoji_response([random_emoji], state)
                
                # Edit message
                await msg.edit(formatted_display)
                
                # Wait before next animation frame
                await asyncio.sleep(1.5)
                
    except asyncio.CancelledError:
        # Animation was cancelled (user ran another command)
        pass
    except Exception as e:
        # Handle any errors during animation
        try:
            error_msg = vzoel_emoji.format_emoji_response(
                ['merah'], f"Animation error: {str(e)}"
            )
            await msg.edit(error_msg)
        except:
            pass

@events.register(events.NewMessage(pattern=r'\.stopid'))
async def stop_id_animation_handler(event):
    """Stop ID animation loop"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
        
        chat_id = event.chat_id
        
        if chat_id in animation_tasks:
            animation_tasks[chat_id].cancel()
            del animation_tasks[chat_id]
            
            stop_msg = vzoel_emoji.format_emoji_response(
                ['centang'], "ID animation stopped"
            )
            await event.edit(stop_msg)
        else:
            no_animation_msg = vzoel_emoji.format_emoji_response(
                ['kuning'], "No ID animation running"
            )
            await event.edit(no_animation_msg)
        
        vzoel_client.increment_command_count()

@events.register(events.NewMessage(pattern=r'\.idinfo'))
async def id_info_handler(event):
    """Show information about ID checker system"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        from client import vzoel_client
        from emoji_handler_premium import vzoel_emoji
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import comment system
from plugins.comments import vzoel_comments
        
        signature = vzoel_emoji.get_vzoel_signature(premium=True)
        
        id_info = f"""**{signature} VzoelFox ID Checker**

{vzoel_emoji.getemoji('utama', premium=True)} **Usage Methods:**
• `.id @username` - Check by username
• `.id` (reply) - Check replied user
• `.stopid` - Stop animation loop

{vzoel_emoji.getemoji('centang', premium=True)} **Process Animation:**
1. Connecting to VzoelFox servers
2. Validating user credentials  
3. Scanning user database
4. Retrieving user information
5. Processing user data
6. Finalizing ID lookup

{vzoel_emoji.getemoji('aktif', premium=True)} **Display Features:**
• Unlimited loop animation
• Random emoji rotation
• User ID display
• Username detection
• Full name resolution
• VzoelFox branding

{vzoel_emoji.getemoji('telegram', premium=True)} **Information Shown:**
1. User ID (numeric)
2. Username (@handle)
3. Full name (first + last)
4. VzoelFox Assistant credit

**By VzoelFox Assistant**"""
        
        await event.edit(id_info)
        vzoel_client.increment_command_count()
