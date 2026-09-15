"""Detect host capabilities and provide command-generation constraints."""

from __future__ import annotations

import os
import platform
import shutil
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class SystemInfo:
    os_name: str
    kernel: str
    architecture: str
    environment: str
    package_manager: str
    shell: str
    cpu_count: int
    termux_api_available: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def prompt_constraints(self) -> str:
        limitations = []
        if self.environment == "Termux":
            limitations.append("Use Termux pkg commands and avoid systemd, sudo, and GUI-only packages.")
        if self.environment == "iSH":
            limitations.append("Use Alpine apk commands; avoid bash-only syntax, systemd, and GNU-only flags.")
        if self.os_name == "Windows":
            limitations.append("Use PowerShell-compatible commands and Windows paths when shell commands are needed.")
        limitations.append(f"Detected {self.os_name} ({self.architecture}), shell {self.shell}, package manager {self.package_manager}.")
        return "Platform constraints:\n- " + "\n- ".join(limitations)


def detect_system() -> SystemInfo:
    os_name = platform.system() or "Unknown"
    environment = "Desktop"
    if os.getenv("ANDROID_ROOT") or os.getenv("TERMUX_VERSION"):
        environment = "Termux"
    elif os.getenv("ISH_VERSION") or (os_name == "Linux" and "alpine" in platform.platform().lower()):
        environment = "iSH"
    if environment == "Termux":
        package_manager = "pkg"
    elif environment == "iSH":
        package_manager = "apk"
    elif os_name == "Darwin":
        package_manager = "brew" if shutil.which("brew") else "installer"
    elif os_name == "Windows":
        package_manager = "winget" if shutil.which("winget") else "choco"
    else:
        package_manager = "apt" if shutil.which("apt") else ("apk" if shutil.which("apk") else "package-manager")
    shell = os.getenv("COMSPEC", "cmd.exe") if os_name == "Windows" else (os.getenv("SHELL") or "/bin/sh")
    return SystemInfo(os_name, platform.release(), platform.machine(), environment, package_manager, shell, os.cpu_count() or 1, bool(shutil.which("termux-api")))


def system_prompt() -> str:
    """Return concise platform facts for an LLM-generated command plan."""
    return detect_system().prompt_constraints()
