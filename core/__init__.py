"""
Vzoel Fox's Lutpan - Core Systems
Pure userbot architecture with essential components
"""

__version__ = "2.0.0"
__author__ = "Vzoel Fox's"

from .music import MusicManager
from .voice_chat import VoiceChatManager

__all__ = ['MusicManager', 'VoiceChatManager']
