"""Nova Shell GTK — Top Bar 3.0 (glass strut panel, non-KDE chrome)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk  # noqa: E402

from nova_shell import api  # noqa: E402
from nova_shell.backend import search as search_backend  # noqa: E402
from nova_shell.control_center import open_control_center  # noqa: E402
from nova_shell.plasma_panels import hide_plasma_panels  # noqa: E402
from nova_shell.topbar_manager import TopBarManager  # noqa: E402

BAR_HEIGHT = 36
POLL_MS = 3000

# Distinct from stock Plasma / previous solid navy bar: light glass + cool edge.
CSS = b"""
window.nova-topbar3 {
  background-color: rgba(10, 22, 38, 0.52);
  border-bottom: 1px solid rgba(61, 214, 198, 0.28);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.10);
}
.nova-tb-brand {
  color: #E9EEF6;
  font-family: "Noto Sans", "Source Sans 3", sans-serif;
  font-weight: 700;
  font-size: 11pt;
  letter-spacing: 0.8px;
  padding: 0 2px 0 4px;
}
.nova-tb-brand-accent {
  color: #3DD6C6;
}
.nova-tb-clock {
  color: #E9EEF6;
  font-family: "Noto Sans", "Source Sans 3", sans-serif;
  font-size: 10.5pt;
  font-weight: 600;
  letter-spacing: 0.6px;
  padding: 0 12px 0 8px;
}
.nova-tb-chip {
  padding: 4px 9px;
  border-radius: 999px;
  background-color: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: background-color 160ms ease, border-color 160ms ease;
  color: #D7E2EE;
  min-height: 26px;
}
.nova-tb-chip:hover {
  background-color: rgba(61, 214, 198, 0.16);
  border-color: rgba(61, 214, 198, 0.35);
}
.nova-tb-logo {
  padding: 2px 8px;
  border-radius: 10px;
  transition: background-color 160ms ease;
}
.nova-tb-logo:hover {
  background-color: rgba(255, 255, 255, 0.08);
}
.nova-tb-sep {
  color: rgba(233, 238, 246, 0.22);
  padding: 0 4px;
  font-size: 11pt;
}
window.nova-cc-flyout {
  background-color: rgba(12, 26, 44, 0.88);
  border: 1px solid rgba(61, 214, 198, 0.28);
  border-radius: 14px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.nova-cc-title {
  color: #E9EEF6;
  font-weight: 700;
  font-size: 12pt;
}
.nova-cc-body {
  color: #A8B8C9;
  font-size: 9.5pt;
}
.nova-cc-btn {
  padding: 6px 12px;
  border-radius: 8px;
  background-color: rgba(61, 214, 198, 0.22);
  color: #E9EEF6;
  border: 1px solid rgba(61, 214, 198, 0.4);
}
.nova-cc-btn:hover {
  background-color: rgba(61, 214, 198, 0.34);
}
.nova-cc-btn-ghost {
  padding: 6px 12px;
  border-radius: 8px;
  background-color: transparent;
  color: #A8B8C9;
  border: 1px solid rgba(255, 255, 255, 0.12);
}
"""


def _logo_path() -> Path | None:
    for p in (
        Path("/usr/share/nova/assets/logo/novaos.png"),
        Path("/usr/share/pixmaps/novaos.png"),
    ):
        if p.is_file():
            return p
    return None


def _icon_image(name: str, size: int = 16) -> Gtk.Image:
    theme = Gtk.IconTheme.get_default()
    try:
        if theme.has_icon(name):
            pix = theme.load_icon(name, size, 0)
            return Gtk.Image.new_from_pixbuf(pix)
    except Exception:  # noqa: BLE001
        pass
    return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.MENU)


def _enable_rgba(window: Gtk.Window) -> None:
    screen = window.get_screen()
    visual = screen.get_rgba_visual()
    if visual is not None:
        window.set_visual(visual)
    window.set_app_paintable(True)


class TopBar(Gtk.Window):
    """Top Bar 3.0 — glass strut panel: logo | empty | tray · clock."""

    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Nova Top Bar")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.get_style_context().add_class("nova-topbar3")
        _enable_rgba(self)

        self._refreshing = False
        self._manager: TopBarManager | None = None
        self._tray: dict[str, Gtk.Button] = {}

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        root.set_margin_start(10)
        root.set_margin_end(6)
        self.add(root)

        # —— Left: mark + wordmark ——
        logo_btn = Gtk.Button()
        logo_btn.set_relief(Gtk.ReliefStyle.NONE)
        logo_btn.get_style_context().add_class("nova-tb-logo")
        logo_btn.set_tooltip_text("Nova Launcher")
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        logo = _logo_path()
        if logo:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 20, 20, True)
                logo_box.pack_start(Gtk.Image.new_from_pixbuf(pix), False, False, 0)
            except Exception:  # noqa: BLE001
                pass
        brand = Gtk.Label()
        brand.set_markup(
            '<span class="nova-tb-brand">Nova</span>'
        )
        # Markup class not applied via span class — use style on label
        brand.set_text("Nova")
        brand.get_style_context().add_class("nova-tb-brand")
        logo_box.pack_start(brand, False, False, 0)
        logo_btn.add(logo_box)
        logo_btn.connect("clicked", lambda *_: self._open_launcher())
        root.pack_start(logo_btn, False, False, 0)

        # —— Center: reserved ——
        center = Gtk.Label(label="")
        center.set_hexpand(True)
        root.pack_start(center, True, True, 0)

        # —— Right: status glass chips ——
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        root.pack_end(right, False, False, 0)

        specs = (
            ("notifications", "preferences-system-notifications-symbolic", "notifications-symbolic", "notifications"),
            ("network", "network-wireless-symbolic", "network-wireless", "network"),
            ("audio", "audio-volume-high-symbolic", "audio-volume-high", "audio"),
            ("battery", "battery-good-symbolic", "battery", "battery"),
        )
        for key, icon, fallback, section in specs:
            btn = self._chip(icon, fallback, section)
            self._tray[key] = btn
            right.pack_start(btn, False, False, 0)

        self._tray["battery"].set_no_show_all(True)
        self._tray["battery"].hide()

        sep = Gtk.Label(label="·")
        sep.get_style_context().add_class("nova-tb-sep")
        right.pack_start(sep, False, False, 0)

        self.clock = Gtk.Label(label="—:—")
        self.clock.get_style_context().add_class("nova-tb-clock")
        self.clock.set_tooltip_text("Ora")
        # Clock opens overview Control Center
        clock_evt = Gtk.EventBox()
        clock_evt.add(self.clock)
        clock_evt.set_visible_window(False)
        clock_evt.connect(
            "button-press-event",
            lambda *_: open_control_center(section="overview", anchor=self.clock, parent=self) or True,
        )
        right.pack_start(clock_evt, False, False, 0)

        self.connect("destroy", self._on_destroy)
        self.connect("realize", self._on_realize)
        self.show_all()
        self._tray["battery"].hide()

        # Strip KDE panels so this bar is the visible chrome
        GLib.timeout_add(800, self._kick_plasma)
        GLib.timeout_add(2500, self._kick_plasma)

        self._manager = TopBarManager(self, bar_height=BAR_HEIGHT)
        GLib.idle_add(self._manager.apply)
        self.refresh()
        GLib.timeout_add(POLL_MS, self._poll)

    def _chip(self, icon: str, fallback: str, section: str) -> Gtk.Button:
        btn = Gtk.Button()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.get_style_context().add_class("nova-tb-chip")
        img = _icon_image(icon)
        if img.get_storage_type() == Gtk.ImageType.EMPTY:
            img = _icon_image(fallback)
        btn.add(img)
        btn.connect(
            "clicked",
            lambda *_a, s=section, b=btn: open_control_center(
                section=s,  # type: ignore[arg-type]
                anchor=b,
                parent=self,
            ),
        )
        return btn

    def _kick_plasma(self) -> bool:
        hide_plasma_panels()
        if self._manager:
            self._manager.apply()
        return False

    def _on_realize(self, *_a) -> None:
        GLib.idle_add(self._apply_kwin_blur)

    def _apply_kwin_blur(self) -> bool:
        """Ask KWin to blur behind this glass panel."""
        if self._manager is not None:
            self._manager.set_blur_behind()
        return False

    def _open_launcher(self) -> None:
        cmd = shutil.which("nova-launcher")
        if cmd:
            try:
                subprocess.Popen([cmd], start_new_session=True)  # noqa: S603
            except OSError:
                pass
            return
        hub = shutil.which("nova-hub")
        if hub:
            try:
                subprocess.Popen([hub], start_new_session=True)  # noqa: S603
            except OSError:
                pass

    def _on_destroy(self, *_a) -> None:
        if self._manager:
            self._manager.destroy()
        Gtk.main_quit()

    def _poll(self) -> bool:
        if not self._refreshing:
            self.refresh()
        return True

    def refresh(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True

        def work() -> None:
            try:
                data = api.get_status()
                GLib.idle_add(self._apply, data, None)
            except Exception as exc:  # noqa: BLE001
                GLib.idle_add(self._apply, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _apply(self, data, error) -> bool:
        self._refreshing = False
        if error or not data:
            return False
        clock = data.get("clock") or {}
        self.clock.set_text(str(clock.get("time") or "—:—"))

        net = data.get("network") or {}
        self._tray["network"].set_tooltip_text(f"Rete · {net.get('label') or '—'}")

        vol = data.get("volume") or {}
        self._tray["audio"].set_tooltip_text(f"Audio · {vol.get('label') or 'n/d'}")

        self._tray["notifications"].set_tooltip_text("Notifiche")

        bat = data.get("battery") or {}
        if bat.get("present") and bat.get("percent") is not None:
            pct = bat.get("percent")
            status = bat.get("status") or ""
            self._tray["battery"].set_tooltip_text(f"Batteria {pct}% · {status}")
            self._tray["battery"].show()
        else:
            self._tray["battery"].hide()

        if self._manager:
            self._manager.apply()
        return False


# Back-compat alias
HorizonBar = TopBar


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--snapshot" in argv or "--json" in argv:
        print(json.dumps(api.snapshot(), indent=2, ensure_ascii=False))
        return 0
    if "--search" in argv:
        idx = argv.index("--search")
        q = argv[idx + 1] if idx + 1 < len(argv) else ""
        print(json.dumps(api.search_query(q), indent=2, ensure_ascii=False))
        return 0
    if "--hide-plasma-panels" in argv:
        return 0 if hide_plasma_panels() else 1
    search_backend.get_engine()
    TopBar()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
