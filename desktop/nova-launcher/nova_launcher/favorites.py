"""Favorites persistence for Nova Launcher."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_FAVORITES = [
    "org.novaos.Hub.desktop",
    "org.novaos.Center.desktop",
    "org.novaos.Update.desktop",
    "org.kde.dolphin.desktop",
    "org.kde.konsole.desktop",
]


def _path() -> Path:
    return Path.home() / ".config" / "nova" / "launcher-favorites.json"


def load_favorites() -> list[str]:
    path = _path()
    if not path.is_file():
        return list(DEFAULT_FAVORITES)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return list(DEFAULT_FAVORITES)
    items = data.get("favorites") if isinstance(data, dict) else data
    if not isinstance(items, list):
        return list(DEFAULT_FAVORITES)
    out = [str(i) for i in items if i]
    return out or list(DEFAULT_FAVORITES)


def save_favorites(ids: list[str]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"api": "launcher.favorites.v1", "favorites": ids}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def toggle_favorite(desktop_id: str) -> list[str]:
    favs = load_favorites()
    if desktop_id in favs:
        favs = [f for f in favs if f != desktop_id]
    else:
        favs.insert(0, desktop_id)
    save_favorites(favs)
    return favs
