"""
Template Premium Emoji untuk Semua Plugin VZL2 ASSISTANT
Sistem mapping yang sama persis dengan Vzoel Fox's
Author: Vzoel Fox's (Enhanced by Morgan)
Version: 1.0.0
"""

import asyncio
from telethon.tl.types import MessageEntityCustomEmoji

# ===== PREMIUM EMOJI CONFIGURATION (STANDALONE) =====
PREMIUM_EMOJIS = {
    'utama': {'id': '6156784006194009426', 'char': '🤩'},
    'centang': {'id': '4947455506382849110', 'char': '👍'},
    'petir': {'id': '5794407002566300853', 'char': '⛈'},
    'loading': {'id': '5794353925360457382', 'char': '⚙️'},
    'kuning': {'id': '5260648752149970801', 'char': '🍿'},
    'biru': {'id': '5260687265121712272', 'char': '🎅'},
    'merah': {'id': '5262927296725007707', 'char': '🤪'},
    'proses': {'id': '5321023901998801538', 'char': '👽'},
    'aktif': {'id': '5794128499706958658', 'char': '🎚'},
    'adder1': {'id': '5357404860566235955', 'char': '😈'},
    'adder2': {'id': '5427157414375881061', 'char': '💟'},
    'telegram': {'id': '5350291836378307462', 'char': '✉️'}
}

def get_emoji(emoji_type):
    """Get premium emoji character"""
    return PREMIUM_EMOJIS.get(emoji_type, {}).get('char', '🤩')

def create_premium_entities(text):
    """Create premium emoji entities for text with proper offset calculation"""
    try:
        entities = []
        used_positions = set()

        # Sort emojis by length (longest first) to prevent partial matches
        sorted_emojis = sorted(PREMIUM_EMOJIS.items(),
                             key=lambda x: len(x[1]['char']),
                             reverse=True)

        for emoji_type, emoji_data in sorted_emojis:
            emoji_char = emoji_data['char']
            emoji_id = emoji_data['id']

            # Find all occurrences of this emoji
            start_pos = 0
            while True:
                pos = text.find(emoji_char, start_pos)
                if pos == -1:
                    break

                # Check if this position is already used
                if not any(p in used_positions for p in range(pos, pos + len(emoji_char))):
                    # Calculate UTF-16 offset
                    text_before = text[:pos]
                    utf16_offset = len(text_before.encode('utf-16-le')) // 2

                    # Calculate UTF-16 length
                    emoji_utf16_length = len(emoji_char.encode('utf-16-le')) // 2

                    entities.append(MessageEntityCustomEmoji(
                        offset=utf16_offset,
                        length=emoji_utf16_length,
                        document_id=int(emoji_id)
                    ))

                    # Mark positions as used
                    for p in range(pos, pos + len(emoji_char)):
                        used_positions.add(p)

                start_pos = pos + 1

        # Sort entities by offset for proper order
        entities.sort(key=lambda x: x.offset)
        return entities
    except Exception as e:
        print(f"DEBUG: Premium entities error: {e}")
        return []

async def safe_send_premium(event, text, buttons=None):
    """Send message with premium entities (standalone version)"""
    try:
        entities = create_premium_entities(text)
        
        if entities:
            if buttons:
                return await event.reply(text, formatting_entities=entities, buttons=buttons)
            else:
                return await event.reply(text, formatting_entities=entities)
        else:
            # No premium emojis found, send normally
            if buttons:
                return await event.reply(text, buttons=buttons)
            else:
                return await event.reply(text)
    except Exception:
        # Fallback to simple reply
        try:
            if buttons:
                return await event.reply(text, buttons=buttons)
            else:
                return await event.reply(text)
        except Exception:
            return None

async def safe_edit_premium(message_or_event, text, buttons=None):
    """Edit message with premium entities (standalone version)"""
    try:
        entities = create_premium_entities(text)

        # Force retry mechanism for premium entities
        for attempt in range(3):
            try:
                if entities:
                    if buttons:
                        return await message_or_event.edit(text, formatting_entities=entities, buttons=buttons)
                    else:
                        return await message_or_event.edit(text, formatting_entities=entities)
                else:
                    # Try with empty entities to force premium rendering
                    if buttons:
                        return await message_or_event.edit(text, formatting_entities=[], buttons=buttons)
                    else:
                        return await message_or_event.edit(text, formatting_entities=[])
                break
            except Exception as e:
                print(f"DEBUG: Edit attempt {attempt + 1} failed: {e}")
                if attempt == 2:  # Last attempt
                    # Final fallback to simple edit
                    if buttons:
                        return await message_or_event.edit(text, buttons=buttons)
                    else:
                        return await message_or_event.edit(text)
                await asyncio.sleep(0.5)  # Brief pause before retry

    except Exception as e:
        print(f"DEBUG: Safe edit error: {e}")
        # Ultimate fallback
        try:
            if hasattr(message_or_event, 'edit'):
                if buttons:
                    return await message_or_event.edit(text, buttons=buttons)
                else:
                    return await message_or_event.edit(text)
            elif hasattr(message_or_event, 'reply'):
                if buttons:
                    return await message_or_event.reply(text, buttons=buttons)
                else:
                    return await message_or_event.reply(text)
        except Exception:
            return None

# ===== OWNER CHECK (STANDALONE) =====
async def is_owner(client, user_id):
    """Check if user is bot owner (standalone version)"""
    try:
        me = await client.get_me()
        return user_id == me.id
    except Exception:
        return False