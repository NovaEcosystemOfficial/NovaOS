"""Quick Search engine — future Ryuk will call this API (shell.search.v1)."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SearchHit:
    id: str
    title: str
    subtitle: str
    category: str  # apps | documents | commands | settings
    score: float
    action: str  # command name or special action id
    icon: str = "application-x-executable"


_CATALOG_CANDIDATES = (
    Path("/usr/share/nova/shell/data/catalog.json"),
    Path(__file__).resolve().parents[2] / "data" / "catalog.json",
)


def _load_catalog() -> list[dict[str, Any]]:
    path = next((p for p in _CATALOG_CANDIDATES if p.is_file()), None)
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = data.get("items") if isinstance(data, dict) else data
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


def _score(query: str, title: str, keywords: list[str]) -> float:
    q = query.strip().lower()
    if not q:
        return 0.5
    t = title.lower()
    if t.startswith(q):
        return 1.0
    if q in t:
        return 0.85
    for kw in keywords:
        if q in kw.lower():
            return 0.7
    # token overlap
    tokens = q.split()
    hits = sum(1 for tok in tokens if tok in t or any(tok in k.lower() for k in keywords))
    if hits:
        return 0.4 + 0.1 * hits
    return 0.0


class QuickSearch:
    """In-process search index over packaged catalog + built-in commands."""

    def __init__(self) -> None:
        self._items = _load_catalog()

    def reload(self) -> None:
        self._items = _load_catalog()

    def query(self, text: str, limit: int = 24) -> list[SearchHit]:
        q = (text or "").strip()
        hits: list[SearchHit] = []
        for item in self._items:
            title = str(item.get("title") or item.get("name") or "")
            if not title:
                continue
            keywords = [str(k) for k in (item.get("keywords") or [])]
            keywords.append(str(item.get("category") or ""))
            sc = _score(q, title, keywords)
            if q and sc <= 0:
                continue
            hits.append(
                SearchHit(
                    id=str(item.get("id") or title),
                    title=title,
                    subtitle=str(item.get("subtitle") or item.get("tagline") or ""),
                    category=str(item.get("category") or "apps"),
                    score=sc,
                    action=str(item.get("action") or item.get("command") or ""),
                    icon=str(item.get("icon") or "application-x-executable"),
                )
            )
        hits.sort(key=lambda h: (-h.score, h.title.lower()))
        return hits[:limit]

    def query_dict(self, text: str, limit: int = 24) -> list[dict[str, Any]]:
        return [asdict(h) for h in self.query(text, limit=limit)]

    def execute(self, action: str) -> bool:
        if not action:
            return False
        # Special actions
        special = {
            "nova-hub": "nova-hub",
            "nova-center": "nova-center",
            "nova-update": "nova-update-gui",
            "nova-shell-settings": "systemsettings",
        }
        cmd = special.get(action, action)
        path = shutil.which(cmd)
        if not path and cmd == "systemsettings":
            path = shutil.which("systemsettings5")
        if not path:
            return False
        try:
            subprocess.Popen([path], start_new_session=True)  # noqa: S603
            return True
        except OSError:
            return False


# Module-level singleton for Ryuk / shell.api consumers
_ENGINE: QuickSearch | None = None


def get_engine() -> QuickSearch:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = QuickSearch()
    return _ENGINE


def search(text: str, limit: int = 24) -> list[dict[str, Any]]:
    """Public Quick Search API entry (shell.search.v1)."""
    return get_engine().query_dict(text, limit=limit)
