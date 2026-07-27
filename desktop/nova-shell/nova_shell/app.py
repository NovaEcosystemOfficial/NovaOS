"""Nova Shell GTK — Vision 2.0 Top Bar (strut panel, minimal chrome)."""

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
from nova_shell.topbar_manager import TopBarManager  # noqa: E402

BAR_HEIGHT = 32
POLL_MS = 3000

CSS = b"""
window.horizon-bar {
  background-color: #0f2744;
}
.horizon-clock {
  color: #e8eef5;
  font-size: 10.5pt;
  font-weight: 600;
  letter-spacing: 0.3px;
  padding: 0 10px;
}
.horizon-icon-btn {
  padding: 2px 8px;
  border-radius: 6px;
  transition: background-color 140ms ease;
  color: #d7e2ee;
}
.horizon-icon-btn:hover {
  background-color: rgba(255, 255, 255, 0.10);
}
.horizon-logo-btn {
  padding: 2px 10px;
  border-radius: 6px;
  transition: background-color 140ms ease;
}
.horizon-logo-btn:hover {
  background-color: rgba(255, 255, 255, 0.10);
}
.horizon-muted {
  color: #8fa3b8;
  font-size: 9pt;
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


class HorizonBar(Gtk.Window):
    """Vision 2.0 top bar: logo | (empty) | notifications · wifi · audio · battery · clock."""

    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Nova Shell")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.get_style_context().add_class("horizon-bar")
        self._refreshing = False
        self._manager: TopBarManager | None = None
        self._battery_btn: Gtk.Button | None = None

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        root.set_margin_start(8)
        root.set_margin_end(8)
        self.add(root)

        # —— Left: Nova logo ——
        logo_btn = Gtk.Button()
        logo_btn.set_relief(Gtk.ReliefStyle.NONE)
        logo_btn.get_style_context().add_class("horizon-logo-btn")
        logo_btn.set_tooltip_text("Nova Launcher")
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        logo = _logo_path()
        if logo:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 18, 18, True)
                logo_box.pack_start(Gtk.Image.new_from_pixbuf(pix), False, False, 0)
            except Exception:  # noqa: BLE001
                pass
        logo_btn.add(logo_box)
        logo_btn.connect("clicked", lambda *_: self._open_launcher())
        root.pack_start(logo_btn, False, False, 0)

        # —— Center: reserved empty ——
        center = Gtk.Label(label="")
        center.set_hexpand(True)
        root.pack_start(center, True, True, 0)

        # —— Right: status cluster ——
        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        root.pack_end(right, False, False, 0)

        self.btn_notify = self._tray_btn(
            "preferences-system-notifications-symbolic",
            "Notifiche — Control Center (prossimamente)",
            "notifications-symbolic",
        )
        self.btn_wifi = self._tray_btn(
            "network-wireless-symbolic",
            "Wi‑Fi — Control Center (prossimamente)",
            "network-wireless",
        )
        self.btn_audio = self._tray_btn(
            "audio-volume-high-symbolic",
            "Audio — Control Center (prossimamente)",
            "audio-volume-high",
        )
        self.btn_battery = self._tray_btn(
            "battery-good-symbolic",
            "Batteria",
            "battery",
        )
        self._battery_btn = self.btn_battery
        self.btn_battery.set_no_show_all(True)
        self.btn_battery.hide()

        for b in (self.btn_notify, self.btn_wifi, self.btn_audio, self.btn_battery):
            right.pack_start(b, False, False, 0)

        self.clock = Gtk.Label(label="—")
        self.clock.get_style_context().add_class("horizon-clock")
        self.clock.set_tooltip_text("Ora")
        right.pack_start(self.clock, False, False, 0)

        self.connect("destroy", self._on_destroy)
        self.show_all()
        self.btn_battery.hide()

        self._manager = TopBarManager(self, bar_height=BAR_HEIGHT)
        GLib.idle_add(self._manager.apply)
        self.refresh()
        GLib.timeout_add(POLL_MS, self._poll)

    def _tray_btn(self, icon: str, tip: str, fallback: str) -> Gtk.Button:
        btn = Gtk.Button()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.get_style_context().add_class("horizon-icon-btn")
        btn.set_tooltip_text(tip)
        img = _icon_image(icon)
        if img.get_storage_type() == Gtk.ImageType.EMPTY:
            img = _icon_image(fallback)
        btn.add(img)
        btn.connect("clicked", self._on_tray_click)
        return btn

    def _on_tray_click(self, *_a) -> None:
        # Control Center lands in a later sprint — keep click quiet.
        return

    def _open_launcher(self) -> None:
        cmd = shutil.which("nova-launcher")
        if cmd:
            try:
                subprocess.Popen([cmd], start_new_session=True)  # noqa: S603
            except OSError:
                pass
            return
        # Fallback: embedded minimal open of hub/center not required for Vision bar.
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
        self.clock.set_text(str(clock.get("time") or "—"))

        net = data.get("network") or {}
        label = str(net.get("label") or "—")
        self.btn_wifi.set_tooltip_text(f"Wi‑Fi · {label}")

        vol = data.get("volume") or {}
        self.btn_audio.set_tooltip_text(f"Audio · {vol.get('label') or 'n/d'}")

        bat = data.get("battery") or {}
        if bat.get("present") and bat.get("percent") is not None:
            pct = bat.get("percent")
            status = bat.get("status") or ""
            self.btn_battery.set_tooltip_text(f"Batteria {pct}% · {status}")
            self.btn_battery.show()
        else:
            self.btn_battery.hide()

        # Re-assert strut after status paints (WM sometimes forgets on theme change)
        if self._manager:
            self._manager.apply()
        return False


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
    search_backend.get_engine()
    HorizonBar()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
