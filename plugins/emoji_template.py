"""
Template Premium Emoji untuk Semua Plugin VZL2 ASSISTANT
Sistem mapping yang sama persis dengan VzoelFox
Author: Vzoel Fox's (Enhanced by Morgan) 
Version: 1.0.0
"""

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
    """Create premium emoji entities for text (standalone version)"""
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
                        # Calculate UTF-16 length
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

async def safe_send_premium(event, text, buttons=None):
    """Send message with premium entities (standalone version)"""
    try:
        entities = create_premium_entities(text)
        if entities and buttons:
            await event.reply(text, formatting_entities=entities, buttons=buttons)
        elif entities:
            await event.reply(text, formatting_entities=entities)
        elif buttons:
            await event.reply(text, buttons=buttons)
        else:
            await event.reply(text)
    except Exception:
        # Fallback to simple reply
        if buttons:
            await event.reply(text, buttons=buttons)
        else:
            await event.reply(text)

async def safe_edit_premium(event, text, buttons=None):
    """Edit message with premium entities (standalone version)"""
    try:
        entities = create_premium_entities(text)
        if entities and buttons:
            await event.edit(text, formatting_entities=entities, buttons=buttons)
        elif entities:
            await event.edit(text, formatting_entities=entities)
        elif buttons:
            await event.edit(text, buttons=buttons)
        else:
            await event.edit(text)
    except Exception:
        # Fallback to simple edit
        if buttons:
            await event.edit(text, buttons=buttons)
        else:
            await event.edit(text)

# ===== OWNER CHECK (STANDALONE) =====
async def is_owner(client, user_id):
    """Check if user is bot owner (standalone version)"""
    try:
        me = await client.get_me()
        return user_id == me.id
    except Exception:
        return False