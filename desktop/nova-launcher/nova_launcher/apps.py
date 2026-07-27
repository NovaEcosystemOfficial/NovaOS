"""Discover installed applications via FreeDesktop .desktop / Gio AppInfo."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa: E402


@dataclass(frozen=True)
class AppEntry:
    id: str
    name: str
    comment: str
    exec_key: str
    icon: str
    desktop_id: str
    keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _keywords(info: Gio.AppInfo) -> tuple[str, ...]:
    kws: list[str] = []
    try:
        if hasattr(info, "get_keywords"):
            raw = info.get_keywords() or []
            kws.extend(str(k) for k in raw)
    except Exception:  # noqa: BLE001
        pass
    name = info.get_name() or ""
    if name:
        kws.append(name)
    generic = info.get_generic_name() or ""
    if generic:
        kws.append(generic)
    return tuple(dict.fromkeys(kws))


def list_applications(*, include_hidden: bool = False) -> list[AppEntry]:
    """Return launchable desktop applications (compatible with .desktop files)."""
    out: list[AppEntry] = []
    seen: set[str] = set()
    for info in Gio.AppInfo.get_all():
        try:
            if not include_hidden and not info.should_show():
                continue
            if not info.should_show() and not include_hidden:
                continue
            desktop_id = info.get_id() or ""
            if not desktop_id or desktop_id in seen:
                continue
            # Skip pure KDE menu chrome if marked NoDisplay already handled by should_show
            name = (info.get_name() or "").strip()
            if not name:
                continue
            seen.add(desktop_id)
            icon = ""
            gicon = info.get_icon()
            if gicon is not None:
                try:
                    icon = gicon.to_string() or ""
                except Exception:  # noqa: BLE001
                    icon = ""
            out.append(
                AppEntry(
                    id=desktop_id,
                    name=name,
                    comment=(info.get_description() or info.get_generic_name() or "").strip(),
                    exec_key=(info.get_executable() or "").strip(),
                    icon=icon or "application-x-executable",
                    desktop_id=desktop_id,
                    keywords=_keywords(info),
                )
            )
        except Exception:  # noqa: BLE001
            continue
    out.sort(key=lambda a: a.name.casefold())
    return out


def launch_desktop_id(desktop_id: str) -> bool:
    for info in Gio.AppInfo.get_all():
        if info.get_id() == desktop_id:
            try:
                return bool(info.launch([], None))
            except Exception:  # noqa: BLE001
                return False
    return False


def find_by_executable(names: tuple[str, ...]) -> AppEntry | None:
    want = {n.casefold() for n in names}
    for app in list_applications():
        exe = Path_name(app.exec_key)
        if exe.casefold() in want or app.desktop_id.casefold() in want:
            return app
    return None


def Path_name(exec_key: str) -> str:
    if not exec_key:
        return ""
    return exec_key.split("/")[-1].split()[0]
