"""Quick actions: Center, Update, Terminal, Files, Settings, Reboot, PowerOff."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class QuickAction:
    id: str
    title: str
    icon: str
    kind: str  # app | system


ACTIONS: tuple[QuickAction, ...] = (
    QuickAction("center", "Nova Center", "novaos", "app"),
    QuickAction("update", "Nova Update", "system-software-update", "app"),
    QuickAction("terminal", "Terminale", "utilities-terminal", "app"),
    QuickAction("files", "File", "system-file-manager", "app"),
    QuickAction("settings", "Impostazioni", "preferences-system", "app"),
    QuickAction("reboot", "Riavvia", "system-reboot", "system"),
    QuickAction("poweroff", "Spegni", "system-shutdown", "system"),
)


def _which(*names: str) -> str | None:
    for n in names:
        hit = shutil.which(n)
        if hit:
            return hit
    return None


def _popen(argv: list[str]) -> bool:
    try:
        subprocess.Popen(argv, start_new_session=True)  # noqa: S603
        return True
    except OSError:
        return False


def run_action(action_id: str) -> bool:
    if action_id == "center":
        cmd = _which("nova-center")
        return _popen([cmd]) if cmd else False
    if action_id == "update":
        cmd = _which("nova-update-gui", "nova-updater")
        return _popen([cmd]) if cmd else False
    if action_id == "terminal":
        cmd = _which("konsole", "gnome-terminal", "kgx", "xterm")
        return _popen([cmd]) if cmd else False
    if action_id == "files":
        cmd = _which("dolphin", "nautilus", "nemo", "thunar")
        return _popen([cmd]) if cmd else False
    if action_id == "settings":
        cmd = _which("systemsettings", "systemsettings5", "gnome-control-center")
        return _popen([cmd]) if cmd else False
    if action_id == "reboot":
        return _popen(["systemctl", "reboot"])
    if action_id == "poweroff":
        return _popen(["systemctl", "poweroff"])
    return False
