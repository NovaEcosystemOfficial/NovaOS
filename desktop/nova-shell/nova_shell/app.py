"""Nova Shell GTK experience — Horizon Bar, Launcher, Widgets, Dock API UI stub."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk  # noqa: E402

from nova_shell import api  # noqa: E402
from nova_shell.backend import search as search_backend  # noqa: E402
from nova_shell.prefs import TopBarMode  # noqa: E402
from nova_shell.settings_ui import TopBarSettingsDialog  # noqa: E402
from nova_shell.topbar_manager import TopBarManager  # noqa: E402

BAR_HEIGHT = 42
DOCK_HEIGHT = 48
TOTAL_HEIGHT = BAR_HEIGHT + DOCK_HEIGHT
POLL_MS = 3000

CSS = b"""
window.horizon-bar {
  background-color: rgba(15, 39, 68, 0.92);
}
.horizon-label {
  color: #e8eef5;
  font-size: 10pt;
}
.horizon-brand {
  color: #ffffff;
  font-weight: bold;
  font-size: 11pt;
}
.horizon-chip {
  color: #c5d0dc;
  font-size: 9pt;
  padding: 2px 6px;
}
.horizon-chip-warn { color: #f0c14a; font-weight: bold; }
.horizon-chip-ok { color: #6dcea0; }
.horizon-logo-btn {
  padding: 2px 8px;
  border-radius: 8px;
  transition: background-color 180ms ease;
}
.horizon-logo-btn:hover {
  background-color: rgba(255, 255, 255, 0.12);
}
window.launcher-window {
  background-color: rgba(238, 242, 246, 0.97);
  border-radius: 16px;
  border: 1px solid #cfd8e3;
}
.launcher-title {
  font-weight: bold;
  font-size: 16pt;
  color: #0f2744;
}
.launcher-hint {
  color: #64748b;
  font-size: 9pt;
}
.launcher-row-title {
  font-weight: bold;
  color: #0f2744;
}
.launcher-row-sub {
  color: #64748b;
  font-size: 9pt;
}
.widget-card {
  background-color: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 4px 8px;
}
.widget-label {
  color: #9db0c4;
  font-size: 8pt;
}
.widget-value {
  color: #ffffff;
  font-weight: bold;
  font-size: 10pt;
}
.dock-strip {
  background-color: rgba(15, 39, 68, 0.88);
  border-radius: 14px;
}
.dock-btn {
  padding: 6px 10px;
  border-radius: 10px;
  transition: background-color 160ms ease, opacity 160ms ease;
  color: #e8eef5;
}
.dock-btn:hover {
  background-color: rgba(255, 255, 255, 0.14);
}
entry.search-entry {
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 12pt;
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


def _pct(value) -> str:
    if value is None:
        return "—"
    try:
        if isinstance(value, str):
            return value if value.endswith("%") else f"{float(value.rstrip('%')):.0f}%"
        return f"{float(value):.0f}%"
    except (TypeError, ValueError):
        return str(value)


class LauncherWindow(Gtk.Window):
    def __init__(self, on_open=None, on_close=None) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Nova Launcher")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_default_size(640, 480)
        self.get_style_context().add_class("launcher-window")
        self._on_open = on_open
        self._on_close = on_close
        self._opacity = 0.0
        self.set_opacity(0.0)

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        outer.set_border_width(20)
        self.add(outer)

        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title = Gtk.Label(label="Nova Launcher", xalign=0)
        title.get_style_context().add_class("launcher-title")
        head.pack_start(title, True, True, 0)
        close_btn = Gtk.Button(label="Esc")
        close_btn.connect("clicked", lambda *_: self.hide_animated())
        head.pack_end(close_btn, False, False, 0)
        outer.pack_start(head, False, False, 0)

        hint = Gtk.Label(
            label="Ricerca istantanea · App · Documenti · Comandi · Impostazioni",
            xalign=0,
        )
        hint.get_style_context().add_class("launcher-hint")
        outer.pack_start(hint, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Cerca in NovaOS…")
        self.entry.get_style_context().add_class("search-entry")
        self.entry.connect("changed", self._on_query)
        self.entry.connect("activate", self._on_activate)
        outer.pack_start(self.entry, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        outer.pack_start(scroll, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self._on_row)
        scroll.add(self.listbox)

        self.connect("key-press-event", self._on_key)
        self._render("")

    def _on_key(self, _w, event) -> bool:
        if event.keyval == Gdk.KEY_Escape:
            self.hide_animated()
            return True
        return False

    def show_animated(self) -> None:
        if self._on_open:
            self._on_open()
        screen = self.get_screen()
        monitor = screen.get_primary_monitor()
        geo = screen.get_monitor_geometry(monitor)
        self.resize(min(640, geo.width - 80), min(520, geo.height - 120))
        self.move(geo.x + (geo.width - self.get_size()[0]) // 2, geo.y + 72)
        self.show_all()
        self.present()
        self.entry.grab_focus()
        self._opacity = 0.0
        self.set_opacity(0.0)
        GLib.timeout_add(16, self._fade_in)

    def hide_animated(self) -> None:
        GLib.timeout_add(16, self._fade_out)

    def _fade_in(self) -> bool:
        self._opacity = min(1.0, self._opacity + 0.12)
        self.set_opacity(self._opacity)
        return self._opacity < 1.0

    def _fade_out(self) -> bool:
        self._opacity = max(0.0, self._opacity - 0.15)
        self.set_opacity(self._opacity)
        if self._opacity <= 0.0:
            self.hide()
            if self._on_close:
                self._on_close()
            return False
        return True

    def _on_query(self, entry: Gtk.Entry) -> None:
        self._render(entry.get_text())

    def _render(self, text: str) -> None:
        for child in list(self.listbox.get_children()):
            self.listbox.remove(child)
        hits = api.search_query(text).get("hits") or []
        if not hits:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label="Nessun risultato", xalign=0)
            lbl.get_style_context().add_class("launcher-row-sub")
            lbl.set_margin_start(8)
            lbl.set_margin_top(10)
            lbl.set_margin_bottom(10)
            row.add(lbl)
            self.listbox.add(row)
        else:
            for hit in hits:
                row = Gtk.ListBoxRow()
                row._action = hit.get("action")  # type: ignore[attr-defined]
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                box.set_margin_start(10)
                box.set_margin_end(10)
                box.set_margin_top(8)
                box.set_margin_bottom(8)
                t = Gtk.Label(label=str(hit.get("title") or ""), xalign=0)
                t.get_style_context().add_class("launcher-row-title")
                s = Gtk.Label(
                    label=f"{hit.get('category')} · {hit.get('subtitle') or ''}",
                    xalign=0,
                )
                s.get_style_context().add_class("launcher-row-sub")
                box.pack_start(t, False, False, 0)
                box.pack_start(s, False, False, 0)
                row.add(box)
                self.listbox.add(row)
        self.listbox.show_all()

    def _on_row(self, _lb, row) -> None:
        action = getattr(row, "_action", None)
        if action:
            api.search_execute(str(action))
            self.hide_animated()

    def _on_activate(self, *_a) -> None:
        row = self.listbox.get_selected_row()
        if row is None:
            children = self.listbox.get_children()
            row = children[0] if children else None
        if row is not None:
            self._on_row(self.listbox, row)


class HorizonBar(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Nova Shell")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_accept_focus(False)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.get_style_context().add_class("horizon-bar")
        self._launcher: LauncherWindow | None = None
        self._settings: TopBarSettingsDialog | None = None
        self._refreshing = False
        self._chips: dict[str, Gtk.Label] = {}
        self._widgets: dict[str, Gtk.Label] = {}
        self._manager: TopBarManager | None = None

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(root)

        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bar.set_margin_start(10)
        bar.set_margin_end(12)
        bar.set_margin_top(4)
        bar.set_margin_bottom(4)
        bar.set_size_request(-1, BAR_HEIGHT)
        root.pack_start(bar, False, False, 0)

        # Logo → launcher
        logo_btn = Gtk.Button()
        logo_btn.get_style_context().add_class("horizon-logo-btn")
        logo_btn.set_relief(Gtk.ReliefStyle.NONE)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        logo = _logo_path()
        if logo:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 22, 22, True)
                logo_box.pack_start(Gtk.Image.new_from_pixbuf(pix), False, False, 0)
            except Exception:
                pass
        brand = Gtk.Label(label="Nova")
        brand.get_style_context().add_class("horizon-brand")
        logo_box.pack_start(brand, False, False, 0)
        logo_btn.add(logo_box)
        logo_btn.connect("clicked", lambda *_: self.toggle_launcher())
        bar.pack_start(logo_btn, False, False, 0)

        # Widgets strip
        widgets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for key, title in (
            ("cpu", "CPU"),
            ("ram", "RAM"),
            ("disk", "Disco"),
            ("net", "Rete"),
            ("upd", "Update"),
        ):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            card.get_style_context().add_class("widget-card")
            t = Gtk.Label(label=title, xalign=0)
            t.get_style_context().add_class("widget-label")
            v = Gtk.Label(label="—", xalign=0)
            v.get_style_context().add_class("widget-value")
            self._widgets[key] = v
            card.pack_start(t, False, False, 0)
            card.pack_start(v, False, False, 0)
            widgets.pack_start(card, False, False, 0)
        bar.pack_start(widgets, False, False, 8)

        spacer = Gtk.Label(label="")
        bar.pack_start(spacer, True, True, 0)

        # Status chips
        for key in ("time", "date", "battery", "network", "volume", "updates", "ryuk"):
            lbl = Gtk.Label(label="—")
            lbl.get_style_context().add_class("horizon-chip")
            self._chips[key] = lbl
            bar.pack_start(lbl, False, False, 0)

        settings_btn = Gtk.Button(label="⚙")
        settings_btn.set_relief(Gtk.ReliefStyle.NONE)
        settings_btn.set_tooltip_text("Impostazioni Nova — Barra superiore")
        settings_btn.get_style_context().add_class("horizon-logo-btn")
        settings_btn.connect("clicked", lambda *_: self.open_settings())
        bar.pack_end(settings_btn, False, False, 0)

        # Dock strip (API-backed favorites: Hub, Center, Update, File, Terminal)
        self.dock_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.dock_box.get_style_context().add_class("dock-strip")
        self.dock_box.set_halign(Gtk.Align.CENTER)
        self.dock_box.set_margin_top(6)
        self.dock_box.set_margin_bottom(8)
        self.dock_box.set_margin_start(12)
        self.dock_box.set_margin_end(12)
        root.pack_start(self.dock_box, False, False, 0)
        self._rebuild_dock()

        self.connect("destroy", self._on_destroy)
        self.show_all()

        self._manager = TopBarManager(
            self,
            bar_height=TOTAL_HEIGHT,
            on_mode_changed=lambda _m: None,
        )
        # Default auto-hide: start tucked away
        if self._manager.mode == TopBarMode.AUTO_HIDE:
            self._manager.recompute(force=True)
        self.refresh()
        GLib.timeout_add(POLL_MS, self._poll)

    def _on_destroy(self, *_a) -> None:
        if self._manager:
            self._manager.destroy()
        Gtk.main_quit()

    def open_settings(self) -> None:
        if not self._manager:
            return
        self._manager.notify_menu_open()
        dlg = TopBarSettingsDialog(self, self._manager)
        dlg.connect("response", self._on_settings_done)
        dlg.connect("destroy", self._on_settings_done)
        dlg.present()
        self._settings = dlg

    def _on_settings_done(self, *args) -> None:
        dlg = args[0] if args else None
        if isinstance(dlg, Gtk.Dialog):
            dlg.destroy()
        self._settings = None
        if self._manager:
            self._manager.notify_menu_close()

    def toggle_launcher(self) -> None:
        # Prefer official nova-launcher when installed (Sprint 22).
        import shutil
        import subprocess

        cmd = shutil.which("nova-launcher")
        if cmd:
            if self._manager:
                self._manager.notify_menu_open()
            try:
                subprocess.Popen([cmd], start_new_session=True)  # noqa: S603
            except OSError:
                pass
            if self._manager:
                GLib.timeout_add(600, self._menu_release)
            return
        if self._launcher and self._launcher.get_visible():
            self._launcher.hide_animated()
            return
        if self._launcher is None:
            self._launcher = LauncherWindow(
                on_open=lambda: self._manager and self._manager.notify_menu_open(),
                on_close=lambda: self._manager and self._manager.notify_menu_close(),
            )
        self._launcher.show_animated()

    def _rebuild_dock(self) -> None:
        for child in list(self.dock_box.get_children()):
            self.dock_box.remove(child)
        snap = api.dock_snapshot()
        for item in snap.get("favorites") or []:
            btn = Gtk.Button(label=str(item.get("title") or item.get("id")))
            btn.get_style_context().add_class("dock-btn")
            btn.set_relief(Gtk.ReliefStyle.NONE)
            action = str(item.get("action") or "")

            def _launch(_b, a=action) -> None:
                if self._manager:
                    self._manager.notify_menu_open()
                api.search_execute(a)
                # App leave focus — allow hide again shortly
                if self._manager:
                    GLib.timeout_add(400, self._menu_release)

            btn.connect("clicked", _launch)
            self.dock_box.pack_start(btn, False, False, 0)
        self.dock_box.show_all()

    def _menu_release(self) -> bool:
        if self._manager and not (self._launcher and self._launcher.get_visible()):
            self._manager.notify_menu_close()
        return False

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
            self._chips["ryuk"].set_text("Platform ?")
            return False
        clock = data.get("clock") or {}
        self._chips["time"].set_text(str(clock.get("time") or "—"))
        self._chips["date"].set_text(str(clock.get("date") or "—"))
        bat = data.get("battery") or {}
        self._chips["battery"].set_text(f"bat {bat.get('label') or '—'}")
        net = data.get("network") or {}
        self._chips["network"].set_text(f"net {net.get('label') or '—'}")
        vol = data.get("volume") or {}
        self._chips["volume"].set_text(f"vol {vol.get('label') or 'n/d'}")
        upd = data.get("updates") or {}
        upd_lbl = self._chips["updates"]
        upd_lbl.set_text(f"upd {upd.get('label') or '—'}")
        ctx = upd_lbl.get_style_context()
        ctx.remove_class("horizon-chip-warn")
        ctx.remove_class("horizon-chip-ok")
        if int(upd.get("pending_count") or 0) > 0:
            ctx.add_class("horizon-chip-warn")
        else:
            ctx.add_class("horizon-chip-ok")
        ryuk = data.get("ryuk") or {}
        ryuk_lbl = self._chips["ryuk"]
        state = ryuk.get("state") or "—"
        ryuk_lbl.set_text(f"Ryuk {state}")
        rctx = ryuk_lbl.get_style_context()
        rctx.remove_class("horizon-chip-ok")
        if ryuk.get("ok"):
            rctx.add_class("horizon-chip-ok")

        w = data.get("widgets") or {}
        self._widgets["cpu"].set_text(_pct(w.get("cpu_percent")))
        self._widgets["ram"].set_text(_pct(w.get("memory_percent")))
        disk = w.get("disk_percent")
        self._widgets["disk"].set_text(str(disk) if disk is not None else "—")
        self._widgets["net"].set_text(str(w.get("network_label") or "—"))
        self._widgets["upd"].set_text(str(w.get("updates_label") or "—"))
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
    win = HorizonBar()
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
