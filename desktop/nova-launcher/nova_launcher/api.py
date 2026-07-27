"""Public API facade for Nova Launcher / future Ryuk (launcher.v1)."""

from __future__ import annotations

from typing import Any

from . import API_VERSION, __version__, actions, apps, favorites, prefs, recent, search


def get_apps() -> dict[str, Any]:
    items = [a.to_dict() for a in apps.list_applications()]
    return {"api": API_VERSION, "count": len(items), "apps": items}


def get_favorites() -> dict[str, Any]:
    ids = favorites.load_favorites()
    by_id = {a.desktop_id: a.to_dict() for a in apps.list_applications()}
    resolved = [by_id[i] for i in ids if i in by_id]
    return {"api": "launcher.favorites.v1", "favorites": resolved, "ids": ids}


def get_recent() -> dict[str, Any]:
    docs = [d.to_dict() for d in recent.list_recent()]
    return {"api": "launcher.recent.v1", "documents": docs}


def get_actions() -> dict[str, Any]:
    return {
        "api": "launcher.actions.v1",
        "actions": [
            {"id": a.id, "title": a.title, "icon": a.icon, "kind": a.kind}
            for a in actions.ACTIONS
        ],
    }


def search_query(text: str, limit: int = 40) -> dict[str, Any]:
    hits = search.search(text, limit=limit)
    return {
        "api": "launcher.search.v1",
        "query": text,
        "count": len(hits),
        "hits": hits,
    }


def search_execute(hit: dict[str, Any]) -> dict[str, Any]:
    ok = search.get_engine().execute(hit)
    return {"api": "launcher.search.v1", "ok": ok, "hit": hit}


def get_shortcut() -> dict[str, Any]:
    return {"api": "launcher.prefs.v1", "shortcut": prefs.load_shortcut()}


def snapshot() -> dict[str, Any]:
    return {
        "api": API_VERSION,
        "launcher_version": __version__,
        "apps": get_apps(),
        "favorites": get_favorites(),
        "recent": get_recent(),
        "actions": get_actions(),
        "shortcut": get_shortcut(),
        "search": search_query(""),
    }
