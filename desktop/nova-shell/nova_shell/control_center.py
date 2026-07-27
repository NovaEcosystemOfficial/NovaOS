"""Nova Control Center entry point (Top Bar 3.0).

The full Control Center arrives in a later sprint. Tray icons open this
stub so the UX contract is already wired: section-aware, glass flyout,
ready to swap to the real surface without changing the Top Bar.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Literal

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

Section = Literal[
    "overview",
    "notifications",
    "network",
    "audio",
    "battery",
    "system",
]

_SECTION_COPY: dict[str, tuple[str, str]] = {
    "overview": (
        "Nova Control Center",
        "Prossimamente: Wi‑Fi, Bluetooth, audio, luminosità, Focus e stato sistema.",
    ),
    "notifications": (
        "Notifiche",
        "Il centro notifiche Nova arriverà con Control Center.",
    ),
    "network": (
        "Rete",
        "Gestione Wi‑Fi e connessioni — Control Center.",
    ),
    "audio": (
        "Audio",
        "Volume e uscite — Control Center.",
    ),
    "battery": (
        "Batteria",
        "Energia e autonomia — Control Center.",
    ),
    "system": (
        "Sistema",
        "CPU, RAM, disco e aggiornamenti vivranno qui — non più nella Top Bar.",
    ),
}


class ControlCenterFlyout(Gtk.Window):
    """Lightweight glass flyout anchored near the Top Bar (placeholder UI)."""

    def __init__(self, *, section: Section = "overview", parent: Gtk.Window | None = None) -> None:
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        if parent is not None:
            self.set_transient_for(parent)
        self.set_default_size(320, 220)
        self.get_style_context().add_class("nova-cc-flyout")

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)
        self.set_app_paintable(True)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(16)
        root.set_margin_bottom(16)
        root.set_margin_start(18)
        root.set_margin_end(18)
        self.add(root)

        title_text, body_text = _SECTION_COPY.get(section, _SECTION_COPY["overview"])
        title = Gtk.Label(label=title_text, xalign=0)
        title.get_style_context().add_class("nova-cc-title")
        root.pack_start(title, False, False, 0)

        body = Gtk.Label(label=body_text, xalign=0)
        body.set_line_wrap(True)
        body.get_style_context().add_class("nova-cc-body")
        root.pack_start(body, True, True, 0)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        root.pack_end(row, False, False, 0)

        open_center = Gtk.Button(label="Apri Nova Center")
        open_center.get_style_context().add_class("nova-cc-btn")
        open_center.connect("clicked", self._open_center)
        row.pack_start(open_center, False, False, 0)

        close_btn = Gtk.Button(label="Chiudi")
        close_btn.get_style_context().add_class("nova-cc-btn-ghost")
        close_btn.connect("clicked", lambda *_: self.destroy())
        row.pack_end(close_btn, False, False, 0)

        self.connect("focus-out-event", lambda *_: self.destroy() or False)
        self.show_all()

    def _open_center(self, *_a) -> None:
        for cmd in ("nova-center", "nova-hub"):
            path = shutil.which(cmd)
            if path:
                try:
                    subprocess.Popen([path], start_new_session=True)  # noqa: S603
                except OSError:
                    pass
                break
        self.destroy()

    def place_near(self, anchor: Gtk.Widget) -> None:
        alloc = anchor.get_allocation()
        win = anchor.get_window()
        if win is None:
            return
        origin = win.get_origin()
        # Gdk.Window.get_origin returns (bool, x, y) on some bindings
        if isinstance(origin, tuple) and len(origin) == 3:
            _, ox, oy = origin
        elif isinstance(origin, tuple) and len(origin) == 2:
            ox, oy = origin
        else:
            ox, oy = 0, 0
        x = int(ox + alloc.x + alloc.width - 320)
        y = int(oy + alloc.y + alloc.height + 6)
        self.move(max(8, x), max(8, y))


_open: ControlCenterFlyout | None = None


def open_control_center(
    *,
    section: Section = "overview",
    anchor: Gtk.Widget | None = None,
    parent: Gtk.Window | None = None,
) -> None:
    """Public Top Bar → Control Center hook."""
    global _open
    if _open is not None:
        try:
            _open.destroy()
        except Exception:  # noqa: BLE001
            pass
        _open = None
    fly = ControlCenterFlyout(section=section, parent=parent)
    if anchor is not None:
        fly.place_near(anchor)
    _open = fly
    fly.connect("destroy", lambda *_: _clear())


def _clear() -> None:
    global _open
    _open = None
