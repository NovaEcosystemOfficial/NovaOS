"""Nova Shell public API facade (shell.v1) — for GUI and future Ryuk."""

from __future__ import annotations

from typing import Any

from . import API_VERSION, __version__
from .backend import dock, search, status


def get_status() -> dict[str, Any]:
    return {
        "api": API_VERSION,
        "shell_version": __version__,
        **status.collect(),
    }


def search_query(text: str, limit: int = 24) -> dict[str, Any]:
    hits = search.search(text, limit=limit)
    return {"api": "shell.search.v1", "query": text, "hits": hits, "count": len(hits)}


def search_execute(action: str) -> dict[str, Any]:
    ok = search.get_engine().execute(action)
    if ok:
        search.get_engine()  # ensure loaded
        dock.get_dock().push_recent(
            dock.DockItem(
                id=action,
                title=action,
                action=action,
            )
        )
    return {"api": "shell.search.v1", "action": action, "ok": ok}


def dock_snapshot() -> dict[str, Any]:
    return dock.get_dock().snapshot()


def snapshot() -> dict[str, Any]:
    return {
        "api": API_VERSION,
        "shell_version": __version__,
        "status": get_status(),
        "search": search_query(""),
        "dock": dock_snapshot(),
    }
