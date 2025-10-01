"""
VZOEL ASSISTANT - Voice Chat Plugin (PyTgCalls 2.x Compatible)
Ultra-silent join like a regular user (no audio stream, no disturbance)

Commands:
- .jvc / .joinvc     - Join voice chat silently (no audio, pure presence)
- .lvc / .leavevc    - Leave voice chat
- .stopvc            - Alias for leave
- .vcstatus          - Show runtime status

Features:
- Silent join (tidak ganggu yang lagi di VC)
- No audio streaming (seperti user biasa naik VC)
- Instant mute on join
- Stealth mode optimized

~2025 by Vzoel Fox's Lutpan
"""

import asyncio
import os
import sys
import time
from typing import Dict, Optional

from telethon import events
from telethon.utils import get_display_name
from telethon.tl.functions.phone import JoinGroupCallRequest, LeaveGroupCallRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import DataJSON

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


async def _join_vc_silent(client, chat_id) -> bool:
    """
    Join voice chat silently using raw Telethon (no PyTgCalls streaming).
    This joins as a listener only, like a regular user - no audio disturbance.
    """
    try:
        # Get full chat info to find the active group call
        chat = await client.get_entity(chat_id)
        full_chat = await client(GetFullChannelRequest(chat))

        if not full_chat.full_chat.call:
            raise NoActiveGroupCall("No active voice chat in this group")

        # Join as listener only with muted audio
        # params: empty JSON means listen-only mode (no audio/video streaming)
        await client(JoinGroupCallRequest(
            call=full_chat.full_chat.call,
            join_as=await client.get_me(),
            params=DataJSON(data='{"ufrag":"","pwd":"","fingerprints":[],"ssrc":0}'),
            muted=True,
            video_stopped=True
        ))
        return True
    except Exception:
        # Fallback: if raw join fails, return False to use PyTgCalls method
        return False


async def _leave_vc_silent(client, chat_id) -> bool:
    """
    Leave voice chat using raw Telethon.
    """
    try:
        chat = await client.get_entity(chat_id)
        full_chat = await client(GetFullChannelRequest(chat))

        if not full_chat.full_chat.call:
            return False

        await client(LeaveGroupCallRequest(
            call=full_chat.full_chat.call
        ))
        return True
    except Exception:
        return False


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
        f"{get_emoji('proses')} Pure listener mode\n"
        f"{get_emoji('telegram')} Please wait\n\n"
        f"VZOEL ASSISTANT"
    )
    await safe_edit_premium(event, processing_msg)

    try:
        # Method 1: Try raw Telethon join (pure listener, ZERO audio streaming)
        silent_join_success = await _join_vc_silent(event.client, event.chat_id)

        if not silent_join_success:
            # Method 2: Fallback to PyTgCalls with instant mute
            config = GroupCallConfig(auto_start=False) if GroupCallConfig else None
            await voice_client.play(event.chat_id, SILENCE_URL, config=config)
            try:
                await voice_client.mute(event.chat_id)
            except NotInCallError:  # type: ignore[attr-defined]
                pass
            await asyncio.sleep(0.1)

        title = await _format_group_title(event)
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls[event.chat_id] = {
                "title": title,
                "joined_at": time.time(),
                "method": "silent" if silent_join_success else "pytgcalls"
            }

        join_method = "Pure Listener" if silent_join_success else "Muted Stream"
        response = (
            f"{get_emoji('centang')} JOINED VOICE CHAT\n\n"
            f"{get_emoji('aktif')} Connected to: {title}\n"
            f"{get_emoji('telegram')} Mode: {join_method}\n"
            f"{get_emoji('kuning')} Zero audio disturbance\n\n"
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
        # Check which method was used to join
        async with _state_lock:  # type: ignore[arg-type]
            call_info = _active_calls.get(event.chat_id, {})
            join_method = call_info.get("method", "pytgcalls")

        # Try appropriate leave method
        if join_method == "silent":
            leave_success = await _leave_vc_silent(event.client, event.chat_id)
            if not leave_success and voice_client:
                # Fallback to PyTgCalls leave
                await voice_client.leave_call(event.chat_id)
        else:
            # Use PyTgCalls leave
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
            method = info.get("method", "unknown")
            method_label = "🎧 Listener" if method == "silent" else "🔇 Muted"

            if isinstance(joined_at, (int, float)):
                duration = int(now - joined_at)
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime = "--:--"
            status_lines.append(f"• {title} — {uptime} ({method_label})")

    status_lines.append("")
    status_lines.append("VZOEL ASSISTANT")

    await safe_edit_premium(event, "\n".join(status_lines))

    if vzoel_client:
        vzoel_client.increment_command_count()
