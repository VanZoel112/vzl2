"""
VZOEL ASSISTANT - Voice Chat Plugin (PyTgCalls 2.x Compatible)
Stealth join/leave helpers for Telegram voice chats with premium emoji output.

Commands:
- .jvc / .joinvc     - Join voice chat silently
- .lvc / .leavevc    - Leave voice chat
- .stopvc            - Alias for leave
- .vcstatus          - Show runtime status

~2025 by Vzoel Fox's Lutpan
"""

import asyncio
import os
import sys
import time
from typing import Dict, Optional

from telethon import events
from telethon.utils import get_display_name

# Ensure project root is on sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# A tiny silent audio file to perform a 'stealth join'
SILENCE_URL = os.getenv(
    'VC_SILENCE_URL',
    'https://raw.githubusercontent.com/anars/blank-audio/master/1-second-of-silence.mp3'
)

# ===== PyTgCalls Runtime Detection =====
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import GroupCallConfig
    from pytgcalls.exceptions import (
        NoActiveGroupCall,
        NotInCallError,
        PyTgCallsAlreadyRunning,
    )

    PYTGCALLS_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    class NoActiveGroupCall(Exception):
        """Placeholder when PyTgCalls is not installed."""

    class NotInCallError(Exception):
        """Placeholder when PyTgCalls is not installed."""

    class PyTgCallsAlreadyRunning(Exception):
        """Placeholder when PyTgCalls is not installed."""

    PyTgCalls = None  # type: ignore
    GroupCallConfig = None  # type: ignore
    PYTGCALLS_AVAILABLE = False

# ===== Global Runtime State =====
vzoel_client = None
vzoel_emoji = None
_voice_client: Optional["PyTgCalls"] = None
_voice_client_lock: Optional[asyncio.Lock] = None
_state_lock: Optional[asyncio.Lock] = None
_active_calls: Dict[int, Dict[str, object]] = {}


async def _ensure_runtime_state() -> None:
    """Lazily create locks once the event loop is running."""
    global _voice_client_lock, _state_lock

    if _voice_client_lock is None:
        _voice_client_lock = asyncio.Lock()
    if _state_lock is None:
        _state_lock = asyncio.Lock()


async def _ensure_voice_client(telethon_client) -> Optional["PyTgCalls"]:
    """Ensure PyTgCalls client is available and started."""
    await _ensure_runtime_state()

    if not PYTGCALLS_AVAILABLE or PyTgCalls is None:
        return None

    global _voice_client
    async with _voice_client_lock:  # type: ignore[arg-type]
        if _voice_client is None:
            _voice_client = PyTgCalls(telethon_client)
            try:
                await _voice_client.start()
            except PyTgCallsAlreadyRunning:  # type: ignore[attr-defined]
                pass
            except Exception:
                _voice_client = None
                raise

    return _voice_client


async def _format_group_title(event) -> str:
    try:
        chat = await event.get_chat()
        title = get_display_name(chat)
        return title or str(event.chat_id)
    except Exception:
        return str(event.chat_id)


async def vzoel_init(client, emoji_handler):
    """Plugin initialization from plugin loader."""
    global vzoel_client, vzoel_emoji

    vzoel_client = client
    vzoel_emoji = emoji_handler
    await _ensure_runtime_state()


@events.register(events.NewMessage(pattern=r"\.(?:jvc|joinvc)(?:\s|$)"))
async def join_voice_chat_handler(event):
    if not event.out:
        return

    if event.is_private:
        await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
        return

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception as exc:
        message = (
            f"{get_emoji('merah')} PyTgCalls failed\n\n"
            f"{get_emoji('kuning')} Error: {str(exc)[:80]}\n\n"
            f"VZOEL ASSISTANT"
        )
        await safe_edit_premium(event, message)
        return

    if voice_client is None:
        await safe_edit_premium(
            event,
            f"{get_emoji('merah')} PyTgCalls not installed\n\n"
            f"{get_emoji('telegram')} Install: pip install py-tgcalls\n\n"
            f"VZOEL ASSISTANT",
        )
        return

    await _ensure_runtime_state()
    async with _state_lock:  # type: ignore[arg-type]
        if event.chat_id in _active_calls:
            await safe_edit_premium(
                event,
                f"{get_emoji('kuning')} Already connected\n\nVZOEL ASSISTANT",
            )
            return

    processing_msg = (
        f"{get_emoji('loading')} JOINING VOICE CHAT\n\n"
        f"{get_emoji('proses')} Preparing silent session\n"
        f"{get_emoji('telegram')} Please wait\n\n"
        f"VZOEL ASSISTANT"
    )
    await safe_edit_premium(event, processing_msg)

    try:
        config = GroupCallConfig(auto_start=False) if GroupCallConfig else None
        await voice_client.play(event.chat_id, SILENCE_URL, config=config)
        try:
            await voice_client.mute(event.chat_id)
        except NotInCallError:  # type: ignore[attr-defined]
            pass

        title = await _format_group_title(event)
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls[event.chat_id] = {
                "title": title,
                "joined_at": time.time(),
            }

        response = (
            f"{get_emoji('centang')} JOINED VOICE CHAT\n\n"
            f"{get_emoji('aktif')} Connected to: {title}\n"
            f"{get_emoji('telegram')} Muted for stealth\n\n"
            f"VZOEL ASSISTANT\n"
            f"~2025 by Vzoel Fox's Lutpan"
        )
    except NoActiveGroupCall:  # type: ignore[attr-defined]
        response = (
            f"{get_emoji('merah')} JOIN FAILED\n\n"
            f"{get_emoji('kuning')} Start the voice chat first\n\n"
            f"VZOEL ASSISTANT"
        )
    except Exception as exc:
        response = (
            f"{get_emoji('merah')} JOIN FAILED\n\n"
            f"{get_emoji('kuning')} Error: {str(exc)[:80]}\n\n"
            f"VZOEL ASSISTANT"
        )

    await safe_edit_premium(event, response)

    if vzoel_client:
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r"\.(?:lvc|leavevc|stopvc)(?:\s|$)"))
async def leave_voice_chat_handler(event):
    if not event.out:
        return

    if event.is_private:
        await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL ASSISTANT")
        return

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception as exc:
        await safe_edit_premium(
            event,
            f"{get_emoji('merah')} PyTgCalls failed\n\n{get_emoji('kuning')} Error: {str(exc)[:80]}\n\nVZOEL ASSISTANT",
        )
        return

    if voice_client is None:
        await safe_edit_premium(
            event,
            f"{get_emoji('merah')} PyTgCalls not installed\n\nVZOEL ASSISTANT",
        )
        return

    await _ensure_runtime_state()
    async with _state_lock:  # type: ignore[arg-type]
        if event.chat_id not in _active_calls:
            await safe_edit_premium(
                event,
                f"{get_emoji('kuning')} Not connected to VC\n\nVZOEL ASSISTANT",
            )
            return

    processing_msg = (
        f"{get_emoji('loading')} LEAVING VOICE CHAT\n\n"
        f"{get_emoji('proses')} Disconnecting\n\n"
        f"VZOEL ASSISTANT"
    )
    await safe_edit_premium(event, processing_msg)

    try:
        await voice_client.leave_call(event.chat_id)
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls.pop(event.chat_id, None)

        response = (
            f"{get_emoji('centang')} LEFT VOICE CHAT\n\n"
            f"{get_emoji('aktif')} Successfully disconnected\n\n"
            f"VZOEL ASSISTANT\n"
            f"~2025 by Vzoel Fox's Lutpan"
        )
    except NotInCallError:  # type: ignore[attr-defined]
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls.pop(event.chat_id, None)
        response = (
            f"{get_emoji('kuning')} Not in voice chat\n\nVZOEL ASSISTANT"
        )
    except NoActiveGroupCall:  # type: ignore[attr-defined]
        response = (
            f"{get_emoji('kuning')} Voice chat already closed\n\nVZOEL ASSISTANT"
        )
    except Exception as exc:
        response = (
            f"{get_emoji('merah')} LEAVE FAILED\n\n"
            f"{get_emoji('kuning')} Error: {str(exc)[:80]}\n\n"
            f"VZOEL ASSISTANT"
        )

    await safe_edit_premium(event, response)

    if vzoel_client:
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r"\.vcstatus(?:\s|$)"))
async def voice_chat_status_handler(event):
    if not event.out:
        return

    await _ensure_runtime_state()

    async with _state_lock:  # type: ignore[arg-type]
        active_copy = dict(_active_calls)

    status_lines = [
        f"{get_emoji('utama')} VOICE CHAT STATUS",
        "",
        f"{get_emoji('aktif')} PyTgCalls: {'Ready' if PYTGCALLS_AVAILABLE else 'Missing'}",
        f"{get_emoji('proses')} Client started: {'Yes' if _voice_client else 'No'}",
        f"{get_emoji('loading')} Active calls: {len(active_copy)}",
    ]

    if active_copy:
        status_lines.append("")
        status_lines.append(f"{get_emoji('telegram')} Sessions:")
        now = time.time()
        for chat_id, info in active_copy.items():
            title = info.get("title", str(chat_id))
            joined_at = info.get("joined_at")
            if isinstance(joined_at, (int, float)):
                duration = int(now - joined_at)
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime = "--:--"
            status_lines.append(f"• {title} ({chat_id}) — {uptime}")

    status_lines.append("")
    status_lines.append("VZOEL ASSISTANT")

    await safe_edit_premium(event, "\n".join(status_lines))

    if vzoel_client:
        vzoel_client.increment_command_count()
