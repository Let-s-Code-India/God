"""Safe, side-effect-free host detection for SDK and prompt generation."""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class SystemSnapshot:
    os_name: str
    architecture: str
    kernel: str
    environment: str
    package_manager: str
    shell: str
    cpu_count: int
    termux_api_available: bool

    @property
    def is_termux(self) -> bool:
        return self.environment == "Termux"

    @property
    def is_ish(self) -> bool:
        return self.environment == "iSH"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def prompt_constraints(self) -> str:
        constraints = [f"Detected {self.os_name} on {self.architecture}; shell={self.shell}; package manager={self.package_manager}."]
        if self.is_termux:
            constraints.append("Use Termux pkg; avoid sudo, systemd, desktop GUI packages, and privileged paths.")
        if self.is_ish:
            constraints.append("Use Alpine apk and portable POSIX shell; avoid systemd and GNU-only flags.")
        if self.os_name == "Windows":
            constraints.append("Use PowerShell-compatible commands and Windows paths.")
        return "Platform constraints:\n- " + "\n- ".join(constraints)


def detect() -> SystemSnapshot:
    os_name = platform.system() or "Unknown"
    if os.getenv("ANDROID_ROOT") or os.getenv("TERMUX_VERSION"):
        environment, package_manager = "Termux", "pkg"
    elif os.getenv("ISH_VERSION") or (os_name == "Linux" and "alpine" in platform.platform().lower()):
        environment, package_manager = "iSH", "apk"
    elif os_name == "Darwin":
        environment, package_manager = "Desktop", "brew" if shutil.which("brew") else "installer"
    elif os_name == "Windows":
        environment, package_manager = "Desktop", "winget" if shutil.which("winget") else "choco"
    else:
        environment, package_manager = "Desktop", "apt" if shutil.which("apt") else ("apk" if shutil.which("apk") else "unknown")
    shell = os.getenv("COMSPEC", "cmd.exe") if os_name == "Windows" else (os.getenv("SHELL") or "/bin/sh")
    return SystemSnapshot(os_name, platform.machine(), platform.release(), environment, package_manager, shell, os.cpu_count() or 1, bool(shutil.which("termux-api")))


system = detect()


def system_prompt() -> str:
    return system.prompt_constraints()