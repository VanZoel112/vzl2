"""
VZOEL USERBOT – Voice Chat Controller

This plugin provides reliable join/leave helpers for Telegram voice chats
using the official PyTgCalls API. It mirrors the behaviour from the
vzoelupgrade reference while staying compatible with both the current
PyTgCalls 2.x releases and the legacy 1.x stream helpers.

Commands
--------
.jvc / .joinvc          Join the current voice chat silently
.leavevc / .stopvc      Leave the current voice chat session
.vcstatus               Show PyTgCalls diagnostics and active sessions

All responses preserve VZOEL USERBOT branding and premium emoji styling.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from telethon import events
from telethon.utils import get_display_name

# Ensure the project root is available for shared helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.emoji_template import get_emoji, safe_edit_premium

# --- PyTgCalls runtime detection -------------------------------------------------
try:  # pragma: no cover - optional dependency at runtime
    import pytgcalls
    from pytgcalls import PyTgCalls
    from pytgcalls.exceptions import (
        NoActiveGroupCall,
        NotInCallError,
        PyTgCallsAlreadyRunning,
    )
    from pytgcalls.types import GroupCallConfig, MediaStream

    PYTGCALLS_AVAILABLE = True
    PYTGCALLS_VERSION = getattr(pytgcalls, "__version__", "unknown")
except ImportError:  # pragma: no cover - optional dependency
    class NoActiveGroupCall(Exception):
        """Placeholder when PyTgCalls is missing."""

    class NotInCallError(Exception):
        """Placeholder when PyTgCalls is missing."""

    class PyTgCallsAlreadyRunning(Exception):
        """Placeholder when PyTgCalls is missing."""

    PyTgCalls = None  # type: ignore
    GroupCallConfig = None  # type: ignore
    MediaStream = None  # type: ignore
    pytgcalls = None  # type: ignore
    PYTGCALLS_AVAILABLE = False
    PYTGCALLS_VERSION = "not-installed"

# Legacy imports for PyTgCalls 1.x fallbacks
LegacyInputStream = None
LegacyStreamType = None
LegacyAudioPiped = None
if PYTGCALLS_AVAILABLE:
    try:  # pragma: no cover - dependent on library version
        from pytgcalls.types import InputStream as _LegacyInputStream  # type: ignore[attr-defined]
        LegacyInputStream = _LegacyInputStream
    except ImportError:
        try:
            from pytgcalls.types.input_stream import InputStream as _LegacyInputStream  # type: ignore[attr-defined]
            LegacyInputStream = _LegacyInputStream
        except ImportError:
            LegacyInputStream = None

    try:  # pragma: no cover - dependent on library version
        from pytgcalls.types import StreamType as _LegacyStreamType  # type: ignore[attr-defined]
        LegacyStreamType = _LegacyStreamType
    except ImportError:
        try:
            from pytgcalls import StreamType as _LegacyStreamType  # type: ignore[attr-defined]
            LegacyStreamType = _LegacyStreamType
        except Exception:
            LegacyStreamType = None

    try:  # pragma: no cover - dependent on library version
        from pytgcalls.types import AudioPiped as _LegacyAudioPiped  # type: ignore[attr-defined]
        LegacyAudioPiped = _LegacyAudioPiped
    except ImportError:
        try:
            from pytgcalls.types.input_stream import AudioPiped as _LegacyAudioPiped  # type: ignore[attr-defined]
            LegacyAudioPiped = _LegacyAudioPiped
        except ImportError:
            LegacyAudioPiped = None


@dataclass
class AttemptError:
    """Container for join/leave attempt failures."""

    method: str
    error: str


class VoiceJoinError(Exception):
    """Raised when every join strategy has failed."""

    def __init__(self, attempts: List[AttemptError]):
        super().__init__("All join methods failed")
        self.attempts = attempts


class VoiceLeaveError(Exception):
    """Raised when every leave strategy has failed."""

    def __init__(self, attempts: List[AttemptError]):
        super().__init__("All leave methods failed")
        self.attempts = attempts


# --- Global runtime state --------------------------------------------------------
vzoel_client = None
vzoel_emoji = None
_voice_client: Optional["PyTgCalls"] = None
_voice_client_lock: Optional[asyncio.Lock] = None
_state_lock: Optional[asyncio.Lock] = None
_active_calls: Dict[int, Dict[str, object]] = {}
_capabilities: Optional[Dict[str, object]] = None
_silence_file: Optional[Path] = None


# --- Helpers --------------------------------------------------------------------
def _clean_error_text(raw: BaseException) -> str:
    text = str(raw).strip() or raw.__class__.__name__
    return text.splitlines()[0][:160]


def _format_method_label(method: str) -> str:
    mapping = {
        "modern-mediastream": "MediaStream Silent Join",
        "modern-direct": "Direct Play (No Stream)",
        "legacy-input-stream": "Legacy InputStream",
        "legacy-audio-piped": "Legacy AudioPiped",
        "leave-call": "leave_call",
        "leave-legacy": "leave_group_call",
    }
    return mapping.get(method, method.replace("-", " ").title())


def _ensure_silence_track() -> Optional[Path]:
    global _silence_file
    if _silence_file and _silence_file.exists():
        return _silence_file

    try:
        temp_dir = Path(tempfile.gettempdir())
        candidate = temp_dir / "vzoel_voice_silence.wav"
        if not candidate.exists():
            with wave.open(candidate.as_posix(), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(48000)
                handle.writeframes(b"\x00\x00" * 48000)
        _silence_file = candidate
        return candidate
    except Exception:
        return None


def _detect_capabilities() -> Dict[str, object]:
    global _capabilities
    if _capabilities is not None:
        return _capabilities

    capabilities: Dict[str, object] = {
        "available": PYTGCALLS_AVAILABLE,
        "version": PYTGCALLS_VERSION,
        "has_media_stream": bool(MediaStream),
        "media_stream_cls": MediaStream,
        "input_stream_cls": LegacyInputStream,
        "audio_piped_cls": LegacyAudioPiped,
        "stream_type_cls": LegacyStreamType,
        "has_play": bool(PyTgCalls and hasattr(PyTgCalls, "play")),
        "has_leave_call": bool(PyTgCalls and hasattr(PyTgCalls, "leave_call")),
        "has_legacy_leave": bool(PyTgCalls and hasattr(PyTgCalls, "leave_group_call")),
    }

    _capabilities = capabilities
    return capabilities


async def _ensure_runtime_state() -> None:
    global _voice_client_lock, _state_lock
    if _voice_client_lock is None:
        _voice_client_lock = asyncio.Lock()
    if _state_lock is None:
        _state_lock = asyncio.Lock()


async def _ensure_voice_client(telethon_client) -> Optional["PyTgCalls"]:
    await _ensure_runtime_state()

    capabilities = _detect_capabilities()
    if not capabilities["available"] or PyTgCalls is None:
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


async def _attempt_join(chat_id: int, voice_client: "PyTgCalls") -> str:
    attempts: List[AttemptError] = []
    capabilities = _detect_capabilities()
    config = GroupCallConfig(auto_start=False) if GroupCallConfig else None

    # Method 1 – use MediaStream to provide a silent join on PyTgCalls 2.x
    if capabilities["has_media_stream"] and capabilities["media_stream_cls"]:
        silence_path = _ensure_silence_track()
        if silence_path is not None:
            try:
                media_stream = capabilities["media_stream_cls"](  # type: ignore[misc]
                    silence_path.as_posix(),
                    audio_flags=capabilities["media_stream_cls"].Flags.IGNORE,  # type: ignore[attr-defined]
                    video_flags=capabilities["media_stream_cls"].Flags.IGNORE,  # type: ignore[attr-defined]
                )
                await voice_client.play(chat_id, media_stream, config=config)
                return "modern-mediastream"
            except NoActiveGroupCall:
                raise
            except Exception as exc:
                attempts.append(AttemptError("modern-mediastream", _clean_error_text(exc)))

    # Method 2 – direct play with no stream (PyTgCalls >=2.0)
    if capabilities["has_play"]:
        try:
            await voice_client.play(chat_id, stream=None, config=config)
            return "modern-direct"
        except NoActiveGroupCall:
            raise
        except Exception as exc:
            attempts.append(AttemptError("modern-direct", _clean_error_text(exc)))

    # Method 3 – legacy InputStream join (PyTgCalls 1.x)
    legacy_stream_cls = capabilities.get("input_stream_cls")
    if legacy_stream_cls and hasattr(voice_client, "join_group_call"):
        kwargs: Dict[str, object] = {}
        stream_type_cls = capabilities.get("stream_type_cls")
        if stream_type_cls:
            try:
                kwargs["stream_type"] = stream_type_cls().local_stream  # type: ignore[attr-defined]
            except Exception:
                pass
        try:
            legacy_stream = legacy_stream_cls()  # type: ignore[call-arg]
            await voice_client.join_group_call(chat_id, legacy_stream, **kwargs)  # type: ignore[attr-defined]
            return "legacy-input-stream"
        except NoActiveGroupCall:
            raise
        except Exception as exc:
            attempts.append(AttemptError("legacy-input-stream", _clean_error_text(exc)))

    # Method 4 – legacy AudioPiped join with silent track
    audio_piped_cls = capabilities.get("audio_piped_cls")
    if audio_piped_cls and hasattr(voice_client, "join_group_call"):
        silence_path = _ensure_silence_track()
        if silence_path is not None:
            try:
                silent_pipe = audio_piped_cls(silence_path.as_posix())  # type: ignore[call-arg]
                kwargs: Dict[str, object] = {}
                stream_type_cls = capabilities.get("stream_type_cls")
                if stream_type_cls:
                    try:
                        kwargs["stream_type"] = stream_type_cls().local_stream  # type: ignore[attr-defined]
                    except Exception:
                        pass
                await voice_client.join_group_call(chat_id, silent_pipe, **kwargs)  # type: ignore[attr-defined]
                return "legacy-audio-piped"
            except NoActiveGroupCall:
                raise
            except Exception as exc:
                attempts.append(AttemptError("legacy-audio-piped", _clean_error_text(exc)))

    raise VoiceJoinError(attempts)


async def _attempt_leave(chat_id: int, voice_client: "PyTgCalls") -> str:
    attempts: List[AttemptError] = []
    capabilities = _detect_capabilities()

    if capabilities["has_leave_call"]:
        try:
            await voice_client.leave_call(chat_id)
            return "leave-call"
        except (NotInCallError, NoActiveGroupCall):
            raise
        except Exception as exc:
            attempts.append(AttemptError("leave-call", _clean_error_text(exc)))

    if capabilities["has_legacy_leave"] and hasattr(voice_client, "leave_group_call"):
        try:
            await voice_client.leave_group_call(chat_id)  # type: ignore[attr-defined]
            return "leave-legacy"
        except (NotInCallError, NoActiveGroupCall):
            raise
        except Exception as exc:
            attempts.append(AttemptError("leave-legacy", _clean_error_text(exc)))

    raise VoiceLeaveError(attempts or [AttemptError("leave", "No leave method available")])


# --- Plugin bootstrap ------------------------------------------------------------
async def vzoel_init(client, emoji_handler):
    global vzoel_client, vzoel_emoji
    vzoel_client = client
    vzoel_emoji = emoji_handler
    await _ensure_runtime_state()


# --- Command handlers ------------------------------------------------------------
@events.register(events.NewMessage(pattern=r"\.(?:jvc|joinvc|vcjoin)(?:\s|$)"))
async def join_voice_chat_handler(event):
    if not event.out:
        return

    if event.is_private:
        await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL USERBOT")
        return

    capabilities = _detect_capabilities()

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception as exc:
        message = (
            f"{get_emoji('merah')} PyTgCalls init failed\n\n"
            f"{get_emoji('kuning')} Error: {_clean_error_text(exc)}\n\n"
            f"VZOEL USERBOT"
        )
        await safe_edit_premium(event, message)
        return

    if voice_client is None:
        await safe_edit_premium(
            event,
            "".join(
                [
                    f"{get_emoji('merah')} PyTgCalls not installed\n\n",
                    f"{get_emoji('telegram')} Install: pip install py-tgcalls -U\n\n",
                    "VZOEL USERBOT",
                ]
            ),
        )
        return

    await _ensure_runtime_state()
    async with _state_lock:  # type: ignore[arg-type]
        if event.chat_id in _active_calls:
            await safe_edit_premium(
                event,
                f"{get_emoji('kuning')} Already connected\n\nVZOEL USERBOT",
            )
            return

    processing_msg = (
        f"{get_emoji('loading')} CONNECTING VOICE CHAT\n\n"
        f"{get_emoji('proses')} PyTgCalls v{capabilities['version']}\n"
        f"{get_emoji('telegram')} Trying silent clone mode\n\n"
        f"VZOEL USERBOT"
    )
    await safe_edit_premium(event, processing_msg)

    try:
        method_used = await _attempt_join(event.chat_id, voice_client)
        try:
            await voice_client.mute(event.chat_id)
        except NotInCallError:
            pass

        title = await _format_group_title(event)
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls[event.chat_id] = {
                "title": title,
                "joined_at": time.time(),
                "method": method_used,
                "version": capabilities["version"],
            }

        response = (
            f"{get_emoji('centang')} VOICE CHAT CONNECTED\n\n"
            f"{get_emoji('aktif')} Group: {title}\n"
            f"{get_emoji('proses')} Method: {_format_method_label(method_used)}\n"
            f"{get_emoji('telegram')} PyTgCalls v{capabilities['version']}\n\n"
            f"VZOEL USERBOT\n"
            f"~2025 by Vzoel Fox's Lutpan"
        )
    except NoActiveGroupCall:
        response = (
            f"{get_emoji('merah')} JOIN FAILED\n\n"
            f"{get_emoji('kuning')} Start the voice chat first\n\n"
            f"VZOEL USERBOT"
        )
    except VoiceJoinError as exc:
        detail_lines = [
            f"{get_emoji('merah')} JOIN FAILED\n",
            f"{get_emoji('kuning')} PyTgCalls v{capabilities['version']}",
        ]
        if exc.attempts:
            detail_lines.append("")
            detail_lines.append(f"{get_emoji('proses')} Methods tried:")
            for attempt in exc.attempts:
                detail_lines.append(
                    f"• {_format_method_label(attempt.method)} — {attempt.error}"
                )
        detail_lines.extend(["", "VZOEL USERBOT"])
        response = "\n".join(detail_lines)
    except Exception as exc:
        response = (
            f"{get_emoji('merah')} JOIN FAILED\n\n"
            f"{get_emoji('kuning')} Error: {_clean_error_text(exc)}\n\n"
            f"VZOEL USERBOT"
        )

    await safe_edit_premium(event, response)

    if vzoel_client:
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r"\.(?:lvc|leavevc|stopvc)(?:\s|$)"))
async def leave_voice_chat_handler(event):
    if not event.out:
        return

    if event.is_private:
        await safe_edit_premium(event, f"{get_emoji('kuning')} Only works in groups\n\nVZOEL USERBOT")
        return

    capabilities = _detect_capabilities()

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception as exc:
        await safe_edit_premium(
            event,
            f"{get_emoji('merah')} PyTgCalls init failed\n\n{get_emoji('kuning')} Error: {_clean_error_text(exc)}\n\nVZOEL USERBOT",
        )
        return

    if voice_client is None:
        await safe_edit_premium(
            event,
            f"{get_emoji('merah')} PyTgCalls not installed\n\nVZOEL USERBOT",
        )
        return

    await _ensure_runtime_state()
    async with _state_lock:  # type: ignore[arg-type]
        if event.chat_id not in _active_calls:
            await safe_edit_premium(
                event,
                f"{get_emoji('kuning')} Not connected to VC\n\nVZOEL USERBOT",
            )
            return

    processing_msg = (
        f"{get_emoji('loading')} DISCONNECTING VOICE CHAT\n\n"
        f"{get_emoji('proses')} Cleaning session\n"
        f"{get_emoji('telegram')} PyTgCalls v{capabilities['version']}\n\n"
        f"VZOEL USERBOT"
    )
    await safe_edit_premium(event, processing_msg)

    try:
        method_used = await _attempt_leave(event.chat_id, voice_client)
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls.pop(event.chat_id, None)

        response = (
            f"{get_emoji('centang')} LEFT VOICE CHAT\n\n"
            f"{get_emoji('aktif')} Method: {_format_method_label(method_used)}\n"
            f"{get_emoji('telegram')} PyTgCalls v{capabilities['version']}\n\n"
            f"VZOEL USERBOT\n"
            f"~2025 by Vzoel Fox's Lutpan"
        )
    except NotInCallError:
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls.pop(event.chat_id, None)
        response = f"{get_emoji('kuning')} Not in voice chat\n\nVZOEL USERBOT"
    except NoActiveGroupCall:
        async with _state_lock:  # type: ignore[arg-type]
            _active_calls.pop(event.chat_id, None)
        response = f"{get_emoji('kuning')} Voice chat already closed\n\nVZOEL USERBOT"
    except VoiceLeaveError as exc:
        detail_lines = [
            f"{get_emoji('merah')} LEAVE FAILED\n",
            f"{get_emoji('kuning')} PyTgCalls v{capabilities['version']}",
        ]
        if exc.attempts:
            detail_lines.append("")
            detail_lines.append(f"{get_emoji('proses')} Methods tried:")
            for attempt in exc.attempts:
                detail_lines.append(
                    f"• {_format_method_label(attempt.method)} — {attempt.error}"
                )
        detail_lines.extend(["", "VZOEL USERBOT"])
        response = "\n".join(detail_lines)
    except Exception as exc:
        response = (
            f"{get_emoji('merah')} LEAVE FAILED\n\n"
            f"{get_emoji('kuning')} Error: {_clean_error_text(exc)}\n\n"
            f"VZOEL USERBOT"
        )

    await safe_edit_premium(event, response)

    if vzoel_client:
        vzoel_client.increment_command_count()


@events.register(events.NewMessage(pattern=r"\.vcstatus(?:\s|$)"))
async def voice_chat_status_handler(event):
    if not event.out:
        return

    capabilities = _detect_capabilities()
    await _ensure_runtime_state()

    async with _state_lock:  # type: ignore[arg-type]
        active_copy = dict(_active_calls)

    status_lines: List[str] = [
        f"{get_emoji('utama')} VOICE CHAT STATUS",
        "",
        f"{get_emoji('aktif')} PyTgCalls: {'Ready' if capabilities['available'] else 'Missing'}",
        f"{get_emoji('proses')} Version: {capabilities['version']}",
        f"{get_emoji('loading')} Client started: {'Yes' if _voice_client else 'No'}",
        f"{get_emoji('telegram')} MediaStream: {'Yes' if capabilities['has_media_stream'] else 'No'}",
        f"{get_emoji('telegram')} Legacy InputStream: {'Yes' if capabilities['input_stream_cls'] else 'No'}",
        "",
        f"{get_emoji('loading')} Active calls: {len(active_copy)}",
    ]

    if not capabilities['available']:
        status_lines.extend(
            [
                "",
                f"{get_emoji('kuning')} Install with: pip install py-tgcalls -U",
            ]
        )

    if active_copy:
        status_lines.append("")
        status_lines.append(f"{get_emoji('telegram')} Sessions:")
        now = time.time()
        for chat_id, info in active_copy.items():
            title = info.get("title", str(chat_id))
            joined_at = info.get("joined_at")
            method = _format_method_label(str(info.get("method", "")))
            version = info.get("version", capabilities["version"])
            if isinstance(joined_at, (int, float)):
                duration = int(now - joined_at)
                minutes, seconds = divmod(duration, 60)
                hours, minutes = divmod(minutes, 60)
                uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime = "--:--"
            status_lines.append(
                f"• {title} ({chat_id}) — {uptime} — {method} — v{version}"
            )

    status_lines.append("")
    status_lines.append("VZOEL USERBOT")

    await safe_edit_premium(event, "\n".join(status_lines))

    if vzoel_client:
        vzoel_client.increment_command_count()
