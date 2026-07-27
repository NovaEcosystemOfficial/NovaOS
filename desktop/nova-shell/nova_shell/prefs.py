"""Nova Shell top-bar preferences (Impostazioni Nova)."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path


class TopBarMode(str, Enum):
    ALWAYS_VISIBLE = "always_visible"
    AUTO_HIDE = "auto_hide"  # default
    HIDE_MAXIMIZED = "hide_maximized"


_LABELS = {
    TopBarMode.ALWAYS_VISIBLE: "Sempre visibile",
    TopBarMode.AUTO_HIDE: "Nascondi automaticamente",
    TopBarMode.HIDE_MAXIMIZED: "Nascondi con finestre massimizzate",
}


def prefs_path() -> Path:
    return Path.home() / ".config" / "nova" / "shell-topbar.json"


def mode_label(mode: TopBarMode) -> str:
    return _LABELS[mode]


def load_mode() -> TopBarMode:
    path = prefs_path()
    if not path.is_file():
        return TopBarMode.AUTO_HIDE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return TopBarMode.AUTO_HIDE
    raw = str(data.get("mode") or TopBarMode.AUTO_HIDE.value)
    try:
        return TopBarMode(raw)
    except ValueError:
        return TopBarMode.AUTO_HIDE


def save_mode(mode: TopBarMode) -> None:
    path = prefs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "api": "shell.topbar.v1",
        "mode": mode.value,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
