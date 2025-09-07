# 🦊 VzoelFox's Emoji Usage Guide

## Cara Menggunakan Emoji Premium di Plugin

### 1. Format Standar (Recommended)

```python
# Di plugin handler:
async def my_handler(event):
    global vzoel_client, vzoel_emoji
    
    # Menggunakan single emoji
    emoji = vzoel_emoji.get_emoji('utama')  # 🤩
    await event.edit(f"{emoji} Hello VzoelFox!")
    
    # Menggunakan multiple emojis
    response = vzoel_emoji.format_emoji_response(['utama', 'petir'], "Power activated!")
    await event.edit(response)  # 🤩⛈ Power activated!
```

### 2. Format getemoji() - Lebih Mudah

```python
# Di plugin handler:
async def my_handler(event):
    global vzoel_client, vzoel_emoji
    
    # Cara yang lebih mudah dengan fallback otomatis
    emoji1 = vzoel_emoji.getemoji('utama')    # 🤩
    emoji2 = vzoel_emoji.getemoji('petir')    # ⛈
    emoji3 = vzoel_emoji.getemoji('unknown')  # 🔸 (fallback)
    
    message = f"{emoji1} VzoelFox {emoji2} Assistant is active!"
    await event.edit(message)
```

### 3. Format f-string Template (Paling Mudah)

```python
# Di plugin handler:
async def my_handler(event):
    global vzoel_client, vzoel_emoji
    
    # Template yang mudah dibaca
    message = f"""
{vzoel_emoji.getemoji('utama')} **VzoelFox Status**

{vzoel_emoji.getemoji('centang')} System: Online
{vzoel_emoji.getemoji('aktif')} Plugins: {vzoel_client.stats['plugins_loaded']}
{vzoel_emoji.getemoji('petir')} Commands: {vzoel_client.stats['commands_executed']}

{vzoel_emoji.get_vzoel_signature()} **Ready to serve!**
    """.strip()
    
    await event.edit(message)
```

## Available Emojis

| Nama | Emoji | Kategori | Deskripsi |
|------|-------|----------|-----------|
| `utama` | 🤩 | primary | Emoji utama VzoelFox |
| `centang` | 👍 | reaction | Persetujuan/sukses |
| `petir` | ⛈ | power | Kekuatan/energi |
| `loading` | ⚙️ | system | Loading/proses |
| `kuning` | 🍿 | fun | Hiburan |
| `biru` | 🎅 | special | Spesial event |
| `merah` | 🤪 | fun | Fun/crazy |
| `proses` | 👽 | system | Proses khusus |
| `aktif` | 🎚 | status | Status aktif |
| `adder1` | 😈 | special | Tambahan 1 |
| `adder2` | 💟 | special | Tambahan 2 |
| `telegram` | ✉️ | communication | Komunikasi |

## Command Emoji Patterns

```python
# Pre-defined patterns untuk commands
alive_emojis = vzoel_emoji.get_command_emojis('alive')    # ['utama', 'aktif', 'petir']
ping_emojis = vzoel_emoji.get_command_emojis('ping')      # ['loading', 'centang', 'aktif']
vzoel_emojis = vzoel_emoji.get_command_emojis('vzoel')    # ['utama', 'petir', 'adder1']
```

## Status Emoji Indicators

```python
# Pre-defined status patterns
success_emojis = vzoel_emoji.get_status_emojis('success') # ['centang', 'utama']
loading_emojis = vzoel_emoji.get_status_emojis('loading') # ['loading', 'proses']
error_emojis = vzoel_emoji.get_status_emojis('error')     # ['merah', 'petir']
```

## VzoelFox Signature

```python
# Signature emoji combination
signature = vzoel_emoji.get_vzoel_signature()  # 🤩⛈😈

# Menggunakan dalam message
message = f"{signature} VzoelFox's Territory {signature}"
```

## Custom Emoji Support

VzoelFox's Assistant mendukung custom emoji Telegram Premium:

```python
# Get custom emoji ID
custom_id = vzoel_emoji.get_custom_emoji_id('utama')  # "6156784006194009426"

# Untuk advanced usage dengan Telethon DocumentAttributeCustomEmoji
from telethon.tl.types import DocumentAttributeCustomEmoji

# Note: Implementasi custom emoji memerlukan Telegram Premium
```

## Best Practices

1. **Selalu gunakan `getemoji()`** untuk single emoji dengan fallback
2. **Gunakan `format_emoji_response()`** untuk multiple emoji
3. **Gunakan signature** di awal/akhir message penting
4. **Konsisten** dengan tema emoji per command
5. **Test fallback** untuk user non-premium

## Example Plugin

```python
@events.register(events.NewMessage(pattern=r'\.mystatus'))
async def my_status_handler(event):
    """Status command with VzoelFox emojis"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vzoel_client, vzoel_emoji
        
        # Animated loading
        msg = await event.edit(f"{vzoel_emoji.getemoji('loading')} Checking status...")
        await asyncio.sleep(1)
        
        # Final status
        signature = vzoel_emoji.get_vzoel_signature()
        status_msg = f"""
**{signature} My VzoelFox Status**

{vzoel_emoji.getemoji('utama')} **User:** {(await event.client.get_me()).first_name}
{vzoel_emoji.getemoji('aktif')} **Plugins:** {len(vzoel_client.plugin_manager.plugins)}
{vzoel_emoji.getemoji('centang')} **Status:** Active & Running
{vzoel_emoji.getemoji('telegram')} **Engine:** VzoelFox v2.0.0

**{vzoel_emoji.getemoji('petir')} Ready to dominate!**
        """.strip()
        
        await msg.edit(status_msg)
        vzoel_client.increment_command_count()
```

---

**🦊 Created by VzoelFox's Team**