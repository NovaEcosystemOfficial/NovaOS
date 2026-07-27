"""Configurable launcher shortcut prefs."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_SHORTCUT = "Meta+Space"


def prefs_path() -> Path:
    return Path.home() / ".config" / "nova" / "launcher.json"


def load_shortcut() -> str:
    path = prefs_path()
    if not path.is_file():
        return DEFAULT_SHORTCUT
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SHORTCUT
    return str(data.get("shortcut") or DEFAULT_SHORTCUT)


def save_shortcut(shortcut: str) -> None:
    path = prefs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "api": "launcher.prefs.v1",
        "shortcut": shortcut.strip() or DEFAULT_SHORTCUT,
        "note": "Plasma: Impostazioni → Scorciatoie → aggiungi Nova Launcher. "
        "Meta da sola resta al menu KDE finché non la riassegni.",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
