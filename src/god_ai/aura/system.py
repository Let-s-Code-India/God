"""Aura system detection facade."""

from ..system import SystemSnapshot, detect

system = detect()

__all__ = ["SystemSnapshot", "system"]