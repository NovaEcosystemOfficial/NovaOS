"""Launch helpers for Hub quick actions."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _popen(argv: list[str]) -> bool:
    try:
        subprocess.Popen(argv, start_new_session=True)  # noqa: S603
        return True
    except OSError:
        return False


def which_or(*names: str) -> str | None:
    for name in names:
        hit = shutil.which(name)
        if hit:
            return hit
    return None


def open_center() -> bool:
    cmd = which_or("nova-center")
    return _popen([cmd]) if cmd else False


def open_update() -> bool:
    cmd = which_or("nova-update-gui", "nova-updater")
    return _popen([cmd]) if cmd else False


def open_terminal() -> bool:
    cmd = which_or("konsole", "gnome-terminal", "kgx", "xterm")
    return _popen([cmd]) if cmd else False


def open_settings() -> bool:
    cmd = which_or("systemsettings", "systemsettings5", "gnome-control-center")
    return _popen([cmd]) if cmd else False


def open_files() -> bool:
    cmd = which_or("dolphin", "nautilus", "nemo", "thunar", "xdg-open")
    if not cmd:
        return False
    if Path(cmd).name == "xdg-open":
        return _popen([cmd, str(Path.home())])
    return _popen([cmd])


def open_command(command: str | None) -> bool:
    if not command:
        return False
    cmd = which_or(command)
    return _popen([cmd]) if cmd else False
