"""Optional Termux:API speech helpers; silently unavailable elsewhere."""

from __future__ import annotations

import shutil
import subprocess


def available() -> bool:
    return bool(shutil.which("termux-speech-to-text") or shutil.which("termux-tts-speak"))


def speech_to_text() -> str:
    if not shutil.which("termux-speech-to-text"):
        return ""
    try:
        return subprocess.run(["termux-speech-to-text"], capture_output=True, text=True, timeout=120).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def text_to_speech(text: str) -> bool:
    if not shutil.which("termux-tts-speak"):
        return False
    try:
        subprocess.run(["termux-tts-speak", text], check=False, timeout=120)
        return True
    except (OSError, subprocess.SubprocessError):
        return False
