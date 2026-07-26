"""Local NovaOS news feed (JSON). Future: remote servers."""

from __future__ import annotations

import json
from pathlib import Path

_NEWS_CANDIDATES = (
    Path("/usr/share/nova/hub/data/news.json"),
    Path(__file__).resolve().parents[2] / "data" / "news.json",
)


def load_news(limit: int = 10) -> list[dict]:
    path = next((p for p in _NEWS_CANDIDATES if p.is_file()), None)
    if path is None:
        return [
            {
                "id": "fallback-1",
                "title": "Benvenuto in Nova Hub",
                "summary": "La home ufficiale di NovaOS. Le novità arriveranno qui.",
                "date": "2026-07-26",
            }
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = data.get("items") if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for item in items[:limit]:
        if isinstance(item, dict) and item.get("title"):
            out.append(item)
    return out
