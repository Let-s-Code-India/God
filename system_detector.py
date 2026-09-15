"""Compatibility imports for older integrations."""

from god_ai.system import SystemSnapshot as SystemInfo
from god_ai.system import detect, system_prompt


def detect_system():
    return detect()
