"""Recent documents via GTK RecentManager (FreeDesktop)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import unquote, urlparse

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


@dataclass(frozen=True)
class RecentDoc:
    uri: str
    name: str
    mime: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def list_recent(limit: int = 12) -> list[RecentDoc]:
    mgr = Gtk.RecentManager.get_default()
    items = []
    try:
        raw = mgr.get_items() or []
    except Exception:  # noqa: BLE001
        return []
    for it in raw:
        try:
            if hasattr(it, "get_private_hint") and it.get_private_hint():
                continue
            uri = it.get_uri() or ""
            if not uri:
                continue
            name = it.get_display_name() or unquote(urlparse(uri).path.split("/")[-1])
            mime = ""
            try:
                mime = it.get_mime_type() or ""
            except Exception:  # noqa: BLE001
                mime = ""
            items.append(RecentDoc(uri=uri, name=name, mime=mime))
        except Exception:  # noqa: BLE001
            continue
        if len(items) >= limit:
            break
    return items


def open_uri(uri: str) -> bool:
    try:
        return bool(Gtk.show_uri_on_window(None, uri, Gtk.get_current_event_time()))
    except Exception:  # noqa: BLE001
        import subprocess

        try:
            subprocess.Popen(["xdg-open", uri], start_new_session=True)  # noqa: S603
            return True
        except OSError:
            return False
