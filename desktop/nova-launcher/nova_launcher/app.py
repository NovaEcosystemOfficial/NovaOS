"""Nova Launcher GTK UI — official NovaOS launcher window."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango  # noqa: E402

from nova_launcher import api  # noqa: E402
from nova_launcher import apps as apps_mod  # noqa: E402
from nova_launcher import favorites as fav_mod  # noqa: E402
from nova_launcher import prefs  # noqa: E402
from nova_launcher import recent as recent_mod  # noqa: E402
from nova_launcher import search as search_mod  # noqa: E402
from nova_launcher.actions import ACTIONS, run_action  # noqa: E402

CSS = b"""
window.nova-launcher {
  background-color: #f3f6fa;
  border-radius: 18px;
  border: 1px solid #c5d0dc;
}
.nova-launcher-chrome {
  background-color: #f3f6fa;
  border-radius: 18px;
}
.launcher-brand {
  font-weight: bold;
  font-size: 18pt;
  color: #0f2744;
}
.launcher-sub {
  color: #64748b;
  font-size: 9pt;
}
.section-title {
  font-weight: bold;
  font-size: 11pt;
  color: #0f2744;
  margin-top: 4px;
}
entry.search-entry {
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 12pt;
  background-color: #ffffff;
  border: 1px solid #d0dae6;
  box-shadow: 0 1px 2px rgba(15, 39, 68, 0.06);
}
.tile {
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #e1e8f0;
  padding: 8px;
  transition: background-color 140ms ease, border-color 140ms ease;
}
.tile:hover {
  background-color: #eaf1fb;
  border-color: #9bb6de;
}
.tile-title {
  font-weight: bold;
  color: #0f2744;
  font-size: 9.5pt;
}
.tile-sub {
  color: #64748b;
  font-size: 8pt;
}
.action-btn {
  border-radius: 12px;
  padding: 10px 8px;
  background-color: #ffffff;
  border: 1px solid #e1e8f0;
  transition: background-color 140ms ease;
  color: #0f2744;
  font-weight: bold;
}
.action-btn:hover {
  background-color: #e8f0fc;
}
.action-danger:hover {
  background-color: #fde8e8;
}
.row-title { font-weight: bold; color: #0f2744; }
.row-sub { color: #64748b; font-size: 9pt; }
"""


def _logo_path() -> Path | None:
    for p in (
        Path("/usr/share/nova/assets/logo/novaos.png"),
        Path("/usr/share/pixmaps/novaos.png"),
    ):
        if p.is_file():
            return p
    return None


def _load_icon(name: str, size: int = 32) -> Gtk.Image:
    theme = Gtk.IconTheme.get_default()
    try:
        if name and theme.has_icon(name):
            pix = theme.load_icon(name, size, 0)
            return Gtk.Image.new_from_pixbuf(pix)
    except Exception:  # noqa: BLE001
        pass
    # gicon string sometimes is path
    if name and Path(name).is_file():
        try:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(name, size, size, True)
            return Gtk.Image.new_from_pixbuf(pix)
        except Exception:  # noqa: BLE001
            pass
    return Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DND)


class NovaLauncher(Gtk.Window):
    """Official Nova Launcher window."""

    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Nova Launcher")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(False)
        self.set_skip_pager_hint(False)
        self.set_keep_above(True)
        self.set_accept_focus(True)
        self.set_default_size(760, 620)
        self.get_style_context().add_class("nova-launcher")
        self._opacity = 0.0
        self.set_opacity(0.0)
        self._engine = search_mod.get_engine()
        self._closing = False

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Soft shadow via frame + margin
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_border_width(10)
        outer.get_style_context().add_class("nova-launcher-chrome")
        self.add(outer)

        chrome = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        chrome.set_border_width(16)
        outer.pack_start(chrome, True, True, 0)

        # Header
        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        logo = _logo_path()
        if logo:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 40, 40, True)
                head.pack_start(Gtk.Image.new_from_pixbuf(pix), False, False, 0)
            except Exception:  # noqa: BLE001
                pass
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        brand = Gtk.Label(label="Nova Launcher", xalign=0)
        brand.get_style_context().add_class("launcher-brand")
        sub = Gtk.Label(
            label=f"Scorciatoia: {prefs.load_shortcut()} · parallelo al menu KDE",
            xalign=0,
        )
        sub.get_style_context().add_class("launcher-sub")
        titles.pack_start(brand, False, False, 0)
        titles.pack_start(sub, False, False, 0)
        head.pack_start(titles, True, True, 0)
        close_btn = Gtk.Button(label="Esc")
        close_btn.connect("clicked", lambda *_: self.close_animated())
        head.pack_end(close_btn, False, False, 0)
        chrome.pack_start(head, False, False, 0)

        # Search
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Cerca applicazioni, file, impostazioni…")
        self.entry.get_style_context().add_class("search-entry")
        self.entry.connect("changed", self._on_query)
        self.entry.connect("activate", self._on_activate_search)
        chrome.pack_start(self.entry, False, False, 0)

        # Body scroll
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        chrome.pack_start(scroll, True, True, 0)

        self.body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        scroll.add(self.body)

        self._browse_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self._results = Gtk.ListBox()
        self._results.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._results.connect("row-activated", self._on_result_row)
        self.body.pack_start(self._browse_box, False, False, 0)

        self._build_browse()
        self.connect("key-press-event", self._on_key)
        self.connect("focus-out-event", self._on_focus_out)
        self.connect("delete-event", self._on_delete)

    def _section(self, title: str) -> Gtk.Label:
        lbl = Gtk.Label(label=title, xalign=0)
        lbl.get_style_context().add_class("section-title")
        return lbl

    def _build_browse(self) -> None:
        for child in list(self._browse_box.get_children()):
            self._browse_box.remove(child)

        # Quick actions
        self._browse_box.pack_start(self._section("Azioni rapide"), False, False, 0)
        actions_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions_row.set_homogeneous(True)
        for act in ACTIONS:
            btn = Gtk.Button(label=act.title)
            btn.get_style_context().add_class("action-btn")
            if act.kind == "system":
                btn.get_style_context().add_class("action-danger")
            btn.connect("clicked", self._on_action, act.id)
            actions_row.pack_start(btn, True, True, 0)
        self._browse_box.pack_start(actions_row, False, False, 0)

        # Favorites
        self._browse_box.pack_start(self._section("Applicazioni preferite"), False, False, 0)
        fav_flow = Gtk.FlowBox()
        fav_flow.set_max_children_per_line(4)
        fav_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        fav_flow.set_homogeneous(True)
        fav_flow.set_column_spacing(8)
        fav_flow.set_row_spacing(8)
        by_id = {a.desktop_id: a for a in apps_mod.list_applications()}
        for fid in fav_mod.load_favorites():
            app = by_id.get(fid)
            if app:
                fav_flow.add(self._app_tile(app, favorite=True))
        if not fav_flow.get_children():
            empty = Gtk.Label(label="Nessun preferito ancora.", xalign=0)
            empty.get_style_context().add_class("launcher-sub")
            self._browse_box.pack_start(empty, False, False, 0)
        else:
            self._browse_box.pack_start(fav_flow, False, False, 0)

        # All apps
        self._browse_box.pack_start(self._section("Tutte le applicazioni"), False, False, 0)
        apps_flow = Gtk.FlowBox()
        apps_flow.set_max_children_per_line(4)
        apps_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        apps_flow.set_homogeneous(True)
        apps_flow.set_column_spacing(8)
        apps_flow.set_row_spacing(8)
        for app in apps_mod.list_applications():
            apps_flow.add(self._app_tile(app))
        self._browse_box.pack_start(apps_flow, False, False, 0)

        # Recent docs
        self._browse_box.pack_start(self._section("Documenti recenti"), False, False, 0)
        docs = recent_mod.list_recent(limit=10)
        if not docs:
            empty = Gtk.Label(label="Nessun documento recente.", xalign=0)
            empty.get_style_context().add_class("launcher-sub")
            self._browse_box.pack_start(empty, False, False, 0)
        else:
            for doc in docs:
                row = Gtk.Button()
                row.set_relief(Gtk.ReliefStyle.NONE)
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_border_width(6)
                box.pack_start(_load_icon("text-x-generic", 24), False, False, 0)
                col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
                t = Gtk.Label(label=doc.name, xalign=0)
                t.get_style_context().add_class("row-title")
                t.set_ellipsize(Pango.EllipsizeMode.END)
                s = Gtk.Label(label=doc.uri, xalign=0)
                s.get_style_context().add_class("row-sub")
                s.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
                col.pack_start(t, False, False, 0)
                col.pack_start(s, False, False, 0)
                box.pack_start(col, True, True, 0)
                row.add(box)
                row.connect("clicked", lambda _b, u=doc.uri: self._open_uri(u))
                self._browse_box.pack_start(row, False, False, 0)

        self._browse_box.show_all()

    def _app_tile(self, app, *, favorite: bool = False) -> Gtk.Widget:
        btn = Gtk.Button()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.get_style_context().add_class("tile")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_border_width(6)
        box.pack_start(_load_icon(app.icon, 36), False, False, 0)
        title = Gtk.Label(label=app.name, xalign=0)
        title.get_style_context().add_class("tile-title")
        title.set_ellipsize(Pango.EllipsizeMode.END)
        title.set_max_width_chars(16)
        sub = Gtk.Label(label=("Preferita" if favorite else (app.comment or "App")), xalign=0)
        sub.get_style_context().add_class("tile-sub")
        sub.set_ellipsize(Pango.EllipsizeMode.END)
        sub.set_max_width_chars(16)
        box.pack_start(title, False, False, 0)
        box.pack_start(sub, False, False, 0)
        btn.add(box)
        btn.connect("clicked", lambda _b, d=app.desktop_id: self._launch_app(d))
        btn.connect("button-press-event", self._on_app_button, app.desktop_id)
        return btn

    def _on_app_button(self, _w, event, desktop_id: str) -> bool:
        # Right-click toggles favorite
        if event.button == 3:
            fav_mod.toggle_favorite(desktop_id)
            self._build_browse()
            return True
        return False

    def _launch_app(self, desktop_id: str) -> None:
        apps_mod.launch_desktop_id(desktop_id)
        self.close_animated()

    def _open_uri(self, uri: str) -> None:
        recent_mod.open_uri(uri)
        self.close_animated()

    def _on_action(self, _btn, action_id: str) -> None:
        if action_id in ("reboot", "poweroff"):
            label = "riavviare" if action_id == "reboot" else "spegnere"
            dlg = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=f"Confermi di voler {label} il sistema?",
            )
            resp = dlg.run()
            dlg.destroy()
            if resp != Gtk.ResponseType.OK:
                return
        run_action(action_id)
        self.close_animated()

    def _on_query(self, entry: Gtk.Entry) -> None:
        text = entry.get_text().strip()
        if not text:
            self._show_browse()
            return
        self._show_results(text)

    def _show_browse(self) -> None:
        for child in list(self.body.get_children()):
            self.body.remove(child)
        self.body.pack_start(self._browse_box, False, False, 0)
        self._browse_box.show_all()

    def _show_results(self, text: str) -> None:
        for child in list(self.body.get_children()):
            self.body.remove(child)
        self._results = Gtk.ListBox()
        self._results.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._results.connect("row-activated", self._on_result_row)
        hits = self._engine.query(text)
        if not hits:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label="Nessun risultato", xalign=0)
            lbl.set_margin_start(8)
            lbl.set_margin_top(12)
            row.add(lbl)
            self._results.add(row)
        else:
            for hit in hits:
                row = Gtk.ListBoxRow()
                row._hit = hit  # type: ignore[attr-defined]
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_border_width(8)
                box.pack_start(_load_icon(hit.icon, 28), False, False, 0)
                col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                t = Gtk.Label(label=hit.title, xalign=0)
                t.get_style_context().add_class("row-title")
                s = Gtk.Label(label=f"{hit.category} · {hit.subtitle}", xalign=0)
                s.get_style_context().add_class("row-sub")
                s.set_ellipsize(Pango.EllipsizeMode.END)
                col.pack_start(t, False, False, 0)
                col.pack_start(s, False, False, 0)
                box.pack_start(col, True, True, 0)
                row.add(box)
                self._results.add(row)
        self.body.pack_start(self._results, True, True, 0)
        self._results.show_all()

    def _on_result_row(self, _lb, row) -> None:
        hit = getattr(row, "_hit", None)
        if hit is None:
            return
        self._engine.execute(hit)
        self.close_animated()

    def _on_activate_search(self, *_a) -> None:
        if self.entry.get_text().strip():
            children = self._results.get_children() if hasattr(self, "_results") else []
            if children:
                self._on_result_row(self._results, children[0])

    def _on_key(self, _w, event) -> bool:
        if event.keyval == Gdk.KEY_Escape:
            self.close_animated()
            return True
        return False

    def _on_focus_out(self, *_a) -> bool:
        return False

    def _on_delete(self, *_a) -> bool:
        self.close_animated()
        return True

    def open_animated(self) -> None:
        self._engine.reload()
        self._build_browse()
        self._show_browse()
        screen = self.get_screen()
        mon = screen.get_primary_monitor()
        geo = screen.get_monitor_geometry(mon)
        w, h = 760, 620
        self.resize(min(w, geo.width - 80), min(h, geo.height - 100))
        self.move(geo.x + (geo.width - self.get_allocated_width()) // 2, geo.y + 64)
        # center after map
        def _center() -> bool:
            ww = self.get_allocated_width() or w
            self.move(geo.x + (geo.width - ww) // 2, geo.y + 64)
            return False

        self.show_all()
        self.present()
        self.entry.grab_focus()
        self._opacity = 0.0
        self.set_opacity(0.0)
        GLib.idle_add(_center)
        GLib.timeout_add(16, self._fade_in)

    def close_animated(self) -> None:
        if self._closing:
            return
        self._closing = True
        GLib.timeout_add(16, self._fade_out)

    def _fade_in(self) -> bool:
        self._opacity = min(1.0, self._opacity + 0.14)
        self.set_opacity(self._opacity)
        return self._opacity < 1.0

    def _fade_out(self) -> bool:
        self._opacity = max(0.0, self._opacity - 0.16)
        self.set_opacity(self._opacity)
        if self._opacity <= 0.0:
            self.hide()
            self._closing = False
            Gtk.main_quit()
            return False
        return True

    def capture_png(self, path: Path) -> bool:
        """Save a PNG screenshot of the launcher window."""
        self.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration()
        gdk_win = self.get_window()
        if gdk_win is None:
            return False
        w = self.get_allocated_width()
        h = self.get_allocated_height()
        if w <= 1 or h <= 1:
            return False
        pb = Gdk.pixbuf_get_from_window(gdk_win, 0, 0, w, h)
        if pb is None:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        pb.savev(str(path), "png", [], [])
        return True


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    if "--json" in argv or "--snapshot" in argv:
        print(json.dumps(api.snapshot(), indent=2, ensure_ascii=False))
        return 0
    if "--search" in argv:
        idx = argv.index("--search")
        q = argv[idx + 1] if idx + 1 < len(argv) else ""
        print(json.dumps(api.search_query(q), indent=2, ensure_ascii=False))
        return 0
    if "--set-shortcut" in argv:
        idx = argv.index("--set-shortcut")
        sc = argv[idx + 1] if idx + 1 < len(argv) else prefs.DEFAULT_SHORTCUT
        prefs.save_shortcut(sc)
        print(json.dumps(api.get_shortcut(), indent=2))
        return 0
    if "--screenshot" in argv:
        idx = argv.index("--screenshot")
        out = Path(
            argv[idx + 1]
            if idx + 1 < len(argv)
            else "docs/releases/nova-launcher-screenshot.png"
        )
        win = NovaLauncher()
        win._opacity = 1.0
        win.set_opacity(1.0)
        win._engine.reload()
        win._build_browse()
        win._show_browse()
        screen = win.get_screen()
        geo = screen.get_monitor_geometry(screen.get_primary_monitor())
        win.resize(760, 620)
        win.move(geo.x + 100, geo.y + 80)
        win.show_all()
        win.present()
        win.queue_draw()
        deadline = GLib.get_monotonic_time() + 1_500_000
        while GLib.get_monotonic_time() < deadline:
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
            GLib.usleep(20_000)
        ok = win.capture_png(out)
        win.destroy()
        size = out.stat().st_size if out.is_file() else 0
        print("PASS" if ok and size > 10_000 else "FAIL", out, size)
        return 0 if ok and size > 10_000 else 1

    win = NovaLauncher()
    win.open_animated()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
