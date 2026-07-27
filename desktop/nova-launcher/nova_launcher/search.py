"""Instant search engine — apps, files, settings, recent docs (launcher.search.v1)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from . import actions, apps, favorites, recent


@dataclass(frozen=True)
class SearchHit:
    id: str
    title: str
    subtitle: str
    category: str  # apps | favorites | documents | settings | actions
    score: float
    payload: str  # desktop_id | uri | action_id
    icon: str = "application-x-executable"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _score(query: str, title: str, keywords: tuple[str, ...] | list[str] = ()) -> float:
    q = query.strip().casefold()
    if not q:
        return 0.35
    t = title.casefold()
    if t.startswith(q):
        return 1.0
    if q in t:
        return 0.85
    for kw in keywords:
        if q in str(kw).casefold():
            return 0.7
    tokens = q.split()
    hits = sum(1 for tok in tokens if tok in t)
    return 0.4 + 0.1 * hits if hits else 0.0


class NovaSearch:
    """Public search API for UI and future Ryuk."""

    def __init__(self) -> None:
        self._apps = apps.list_applications()

    def reload(self) -> None:
        self._apps = apps.list_applications()

    def query(self, text: str, limit: int = 40) -> list[SearchHit]:
        q = (text or "").strip()
        hits: list[SearchHit] = []

        fav_ids = set(favorites.load_favorites())
        for app in self._apps:
            sc = _score(q, app.name, app.keywords)
            if q and sc <= 0:
                continue
            cat = "favorites" if app.desktop_id in fav_ids else "apps"
            # boost favorites slightly when browsing
            if not q and app.desktop_id in fav_ids:
                sc = 0.55
            hits.append(
                SearchHit(
                    id=f"app:{app.desktop_id}",
                    title=app.name,
                    subtitle=app.comment or app.desktop_id,
                    category=cat,
                    score=sc + (0.05 if app.desktop_id in fav_ids else 0),
                    payload=app.desktop_id,
                    icon=app.icon,
                )
            )

        for doc in recent.list_recent(limit=20):
            sc = _score(q, doc.name, (doc.mime,))
            if q and sc <= 0:
                continue
            hits.append(
                SearchHit(
                    id=f"doc:{doc.uri}",
                    title=doc.name,
                    subtitle=doc.uri,
                    category="documents",
                    score=sc,
                    payload=doc.uri,
                    icon="text-x-generic",
                )
            )

        for act in actions.ACTIONS:
            sc = _score(q, act.title, (act.id, act.kind))
            if q and sc <= 0:
                continue
            cat = "settings" if act.id == "settings" else "actions"
            hits.append(
                SearchHit(
                    id=f"act:{act.id}",
                    title=act.title,
                    subtitle="Azione rapida",
                    category=cat,
                    score=max(sc, 0.4 if not q else sc),
                    payload=act.id,
                    icon=act.icon,
                )
            )

        hits.sort(key=lambda h: (-h.score, h.title.casefold()))
        return hits[:limit]

    def execute(self, hit: SearchHit | dict[str, Any]) -> bool:
        if isinstance(hit, dict):
            category = str(hit.get("category") or "")
            payload = str(hit.get("payload") or "")
        else:
            category = hit.category
            payload = hit.payload
        if category in ("apps", "favorites"):
            return apps.launch_desktop_id(payload)
        if category == "documents":
            return recent.open_uri(payload)
        if category in ("actions", "settings"):
            return actions.run_action(payload)
        return False


_ENGINE: NovaSearch | None = None


def get_engine() -> NovaSearch:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = NovaSearch()
    return _ENGINE


def search(text: str, limit: int = 40) -> list[dict[str, Any]]:
    return [h.to_dict() for h in get_engine().query(text, limit=limit)]
