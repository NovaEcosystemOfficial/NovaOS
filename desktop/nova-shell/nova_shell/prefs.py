"""Top bar preferences — Vision 2.0: fixed strut panel only.

Legacy auto-hide modes are ignored; kept only for reading old config files.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path


class TopBarMode(str, Enum):
    """Deprecated enum — shell always uses a reserved strut panel."""

    ALWAYS_VISIBLE = "always_visible"
    AUTO_HIDE = "auto_hide"
    HIDE_MAXIMIZED = "hide_maximized"


_LABELS = {
    TopBarMode.ALWAYS_VISIBLE: "Sempre visibile (strut)",
    TopBarMode.AUTO_HIDE: "Nascondi automaticamente (rimosso)",
    TopBarMode.HIDE_MAXIMIZED: "Nascondi con massimizzate (rimosso)",
}


def prefs_path() -> Path:
    return Path.home() / ".config" / "nova" / "shell-topbar.json"


def mode_label(mode: TopBarMode) -> str:
    return _LABELS.get(mode, mode.value)


def load_mode() -> TopBarMode:
    return TopBarMode.ALWAYS_VISIBLE


def save_mode(mode: TopBarMode) -> None:
    path = prefs_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "api": "shell.topbar.v1",
                "mode": TopBarMode.ALWAYS_VISIBLE.value,
                "vision": "2.0",
                "note": "auto-hide removed; strut panel only",
                "requested": mode.value,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
