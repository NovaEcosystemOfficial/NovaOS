"""Desktop notifications via org.freedesktop.Notifications (notify-send fallback)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def notify(
    summary: str,
    body: str = "",
    *,
    app_name: str = "NovaOS",
    icon: str = "novaos",
    urgency: str = "normal",
    replace_id: int = 0,
) -> None:
    """Post a user-session notification. Best-effort; never raises to callers."""
    try:
        _notify_gio(summary, body, app_name=app_name, icon=icon, urgency=urgency)
        return
    except Exception:
        pass
    try:
        _notify_send(summary, body, icon=icon, urgency=urgency, replace_id=replace_id)
    except Exception as exc:  # pragma: no cover
        print(f"nova-notify: {exc}", file=sys.stderr)


def _notify_gio(summary: str, body: str, *, app_name: str, icon: str, urgency: str) -> None:
    import gi

    gi.require_version("Gio", "2.0")
    from gi.repository import Gio, GLib

    # Gio.Notification is for GApplication; use D-Bus Notifications portal-style via subprocess gio?
    # Prefer Notify D-Bus directly.
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    urgency_map = {"low": 0, "normal": 1, "critical": 2}
    hints = {"urgency": GLib.Variant("y", urgency_map.get(urgency, 1))}
    bus.call_sync(
        "org.freedesktop.Notifications",
        "/org/freedesktop/Notifications",
        "org.freedesktop.Notifications",
        "Notify",
        GLib.Variant(
            "(susssasa{sv}i)",
            (
                app_name,
                0,
                icon,
                summary,
                body,
                [],
                hints,
                8000,
            ),
        ),
        None,
        Gio.DBusCallFlags.NONE,
        5000,
        None,
    )


def _notify_send(
    summary: str,
    body: str,
    *,
    icon: str,
    urgency: str,
    replace_id: int,
) -> None:
    cmd = shutil.which("notify-send")
    if not cmd:
        raise RuntimeError("notify-send missing")
    args = [
        cmd,
        f"--urgency={urgency}",
        f"--icon={icon}",
        "--app-name=NovaOS",
        summary,
    ]
    if body:
        args.append(body)
    if replace_id:
        args.insert(1, f"--replace-id={replace_id}")
    subprocess.run(args, check=False, timeout=5)  # noqa: S603
