"""Dock API foundation — favorites / recent / open apps (shell.dock.v1).

Persistence uses Nova config under ~/.config/nova (user prefs), not system
metrics paths. Live window lists arrive later via Platform/compositor.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class DockItem:
    id: str
    title: str
    action: str
    icon: str = "application-x-executable"
    pinned: bool = False


def _state_path() -> Path:
    return Path.home() / ".config" / "nova" / "shell-dock.json"


def _default_favorites() -> list[DockItem]:
    return [
        DockItem("hub", "Nova Hub", "nova-hub", "novaos", True),
        DockItem("center", "Nova Center", "nova-center", "novaos", True),
        DockItem("update", "Nova Update", "nova-update-gui", "system-software-update", True),
        DockItem("files", "File", "dolphin", "system-file-manager", True),
        DockItem("terminal", "Terminale", "konsole", "utilities-terminal", True),
    ]


class DockAPI:
    """Intelligent dock model — API ready for future open-apps / recents."""

    def __init__(self) -> None:
        self._favorites: list[DockItem] = []
        self._recent: list[DockItem] = []
        self._open: list[DockItem] = []  # filled when compositor bridge exists
        self.load()

    def load(self) -> None:
        path = _state_path()
        if not path.is_file():
            self._favorites = _default_favorites()
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._favorites = _default_favorites()
            return
        favs = []
        for item in data.get("favorites") or []:
            if isinstance(item, dict) and item.get("id"):
                favs.append(
                    DockItem(
                        id=str(item["id"]),
                        title=str(item.get("title") or item["id"]),
                        action=str(item.get("action") or ""),
                        icon=str(item.get("icon") or "application-x-executable"),
                        pinned=bool(item.get("pinned", True)),
                    )
                )
        self._favorites = favs or _default_favorites()
        recent = []
        for item in data.get("recent") or []:
            if isinstance(item, dict) and item.get("id"):
                recent.append(
                    DockItem(
                        id=str(item["id"]),
                        title=str(item.get("title") or item["id"]),
                        action=str(item.get("action") or ""),
                        icon=str(item.get("icon") or "application-x-executable"),
                        pinned=False,
                    )
                )
        self._recent = recent

    def save(self) -> None:
        path = _state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "api": "shell.dock.v1",
            "favorites": [asdict(i) for i in self._favorites],
            "recent": [asdict(i) for i in self._recent[:20]],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def favorites(self) -> list[dict[str, Any]]:
        return [asdict(i) for i in self._favorites]

    def recent(self) -> list[dict[str, Any]]:
        return [asdict(i) for i in self._recent]

    def open_apps(self) -> list[dict[str, Any]]:
        """Placeholder until Platform/compositor exposes open windows."""
        return [asdict(i) for i in self._open]

    def pin(self, item: DockItem) -> None:
        self._favorites = [f for f in self._favorites if f.id != item.id]
        item.pinned = True
        self._favorites.append(item)
        self.save()

    def unpin(self, item_id: str) -> None:
        self._favorites = [f for f in self._favorites if f.id != item_id]
        self.save()

    def push_recent(self, item: DockItem) -> None:
        self._recent = [r for r in self._recent if r.id != item.id]
        self._recent.insert(0, item)
        self._recent = self._recent[:20]
        self.save()

    def snapshot(self) -> dict[str, Any]:
        return {
            "api": "shell.dock.v1",
            "favorites": self.favorites(),
            "recent": self.recent(),
            "open": self.open_apps(),
        }


_DOCK: DockAPI | None = None


def get_dock() -> DockAPI:
    global _DOCK
    if _DOCK is None:
        _DOCK = DockAPI()
    return _DOCK
