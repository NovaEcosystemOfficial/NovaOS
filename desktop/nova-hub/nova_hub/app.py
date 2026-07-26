"""Nova Hub GTK GUI — official NovaOS home."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf, GLib, Gtk  # noqa: E402

from nova_hub import api  # noqa: E402
from nova_hub.backend import launch  # noqa: E402

POLL_MS = 4000

CSS = b"""
window {
  background-color: #eef2f6;
}
.hub-brand {
  font-weight: bold;
  font-size: 28pt;
  color: #0f2744;
  letter-spacing: 0.5px;
}
.hub-welcome {
  font-size: 14pt;
  color: #334155;
}
.hub-version {
  color: #64748b;
  font-size: 10pt;
}
.hub-section-title {
  font-weight: bold;
  font-size: 13pt;
  color: #0f2744;
  margin-top: 8px;
}
.hub-card {
  background-color: #ffffff;
  border-radius: 10px;
  border: 1px solid #d7dee8;
}
.hub-metric-label {
  color: #64748b;
  font-size: 9pt;
}
.hub-metric-value {
  font-weight: bold;
  font-size: 14pt;
  color: #0f2744;
}
.hub-ok { color: #1b7a4e; font-weight: bold; }
.hub-warn { color: #9a6b00; font-weight: bold; }
.hub-critical { color: #a32020; font-weight: bold; }
.hub-muted { color: #64748b; }
.hub-eco-name {
  font-weight: bold;
  color: #0f2744;
}
.hub-eco-tag {
  color: #64748b;
  font-size: 9pt;
}
progressbar trough {
  min-height: 10px;
  border-radius: 5px;
  background-color: #d9e2ec;
}
progressbar progress {
  min-height: 10px;
  border-radius: 5px;
  background-color: #1f6feb;
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


def _pct(value) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            value = value.rstrip("%")
        return max(0.0, min(100.0, float(value)))
    except (TypeError, ValueError):
        return None


def _card(child: Gtk.Widget, margin: int = 12) -> Gtk.Frame:
    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.NONE)
    frame.get_style_context().add_class("hub-card")
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_border_width(margin)
    box.pack_start(child, True, True, 0)
    frame.add(box)
    return frame


def _section_label(text: str) -> Gtk.Label:
    lbl = Gtk.Label(label=text, xalign=0)
    lbl.get_style_context().add_class("hub-section-title")
    return lbl


class NovaHubWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Nova Hub")
        self.set_default_size(980, 720)
        self.set_border_width(0)
        self._refreshing = False
        self._poll_id = 0
        self._widgets: dict[str, Gtk.Widget] = {}

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(outer)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        outer.pack_start(scroll, True, True, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_border_width(24)
        content.set_halign(Gtk.Align.CENTER)
        content.set_size_request(880, -1)
        scroll.add(content)

        content.pack_start(self._build_hero(), False, False, 0)
        content.pack_start(self._build_dashboard(), False, False, 0)
        content.pack_start(_section_label("Azioni rapide"), False, False, 0)
        content.pack_start(self._build_actions(), False, False, 0)
        content.pack_start(_section_label("Nova Ecosystem"), False, False, 0)
        content.pack_start(self._build_ecosystem(), False, False, 0)
        content.pack_start(_section_label("Novità NovaOS"), False, False, 0)
        self.news_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.pack_start(_card(self.news_box), False, False, 0)
        content.pack_start(_section_label("Sistema"), False, False, 0)
        content.pack_start(self._build_system(), False, False, 0)

        self.status = Gtk.Label(label="Caricamento…", xalign=0)
        self.status.get_style_context().add_class("hub-muted")
        self.status.set_margin_start(24)
        self.status.set_margin_end(24)
        self.status.set_margin_bottom(12)
        outer.pack_end(self.status, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.refresh()
        self._poll_id = GLib.timeout_add(POLL_MS, self._poll)

    def _build_hero(self) -> Gtk.Widget:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        logo = _logo_path()
        if logo:
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(logo), 72, 72, True)
                row.pack_start(Gtk.Image.new_from_pixbuf(pix), False, False, 0)
            except Exception:
                pass
        col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        brand = Gtk.Label(label="NovaOS", xalign=0)
        brand.get_style_context().add_class("hub-brand")
        col.pack_start(brand, False, False, 0)
        self.welcome = Gtk.Label(label="Benvenuto", xalign=0)
        self.welcome.get_style_context().add_class("hub-welcome")
        col.pack_start(self.welcome, False, False, 0)
        self.version_lbl = Gtk.Label(label="NovaOS —", xalign=0)
        self.version_lbl.get_style_context().add_class("hub-version")
        col.pack_start(self.version_lbl, False, False, 0)
        row.pack_start(col, True, True, 0)

        btn = Gtk.Button(label="Aggiorna")
        btn.connect("clicked", lambda *_: self.refresh())
        row.pack_end(btn, False, False, 0)
        return row

    def _metric(self, key: str, title: str) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_hexpand(True)
        t = Gtk.Label(label=title, xalign=0)
        t.get_style_context().add_class("hub-metric-label")
        v = Gtk.Label(label="—", xalign=0)
        v.get_style_context().add_class("hub-metric-value")
        self._widgets[key] = v
        box.pack_start(t, False, False, 0)
        box.pack_start(v, False, False, 0)
        return box

    def _build_dashboard(self) -> Gtk.Widget:
        grid = Gtk.Grid(column_spacing=18, row_spacing=12)
        grid.set_column_homogeneous(True)
        metrics = [
            ("uptime", "Uptime"),
            ("cpu", "CPU"),
            ("ram", "RAM"),
            ("disk", "Disco"),
            ("net", "Rete"),
            ("platform", "Nova Platform"),
            ("update", "Nova Update"),
        ]
        for i, (key, title) in enumerate(metrics):
            grid.attach(self._metric(key, title), i % 4, i // 4, 1, 1)

        bars = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bars.set_margin_top(8)
        self.cpu_bar = Gtk.ProgressBar(show_text=True)
        self.ram_bar = Gtk.ProgressBar(show_text=True)
        self.disk_bar = Gtk.ProgressBar(show_text=True)
        for bar, label in (
            (self.cpu_bar, "CPU"),
            (self.ram_bar, "RAM"),
            (self.disk_bar, "Disco"),
        ):
            wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            lbl = Gtk.Label(label=label, xalign=0)
            lbl.get_style_context().add_class("hub-metric-label")
            wrap.pack_start(lbl, False, False, 0)
            wrap.pack_start(bar, False, False, 0)
            bars.pack_start(wrap, False, False, 0)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        inner.pack_start(grid, False, False, 0)
        inner.pack_start(bars, False, False, 0)
        return _card(inner)

    def _build_actions(self) -> Gtk.Widget:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_homogeneous(True)
        actions = [
            ("Nova Center", launch.open_center),
            ("Nova Update", launch.open_update),
            ("Terminale", launch.open_terminal),
            ("Impostazioni", launch.open_settings),
            ("File", launch.open_files),
        ]
        for label, fn in actions:
            btn = Gtk.Button(label=label)
            btn.set_size_request(-1, 40)
            btn.connect("clicked", lambda _b, f=fn: self._run_action(f))
            row.pack_start(btn, True, True, 0)
        return _card(row, margin=10)

    def _build_ecosystem(self) -> Gtk.Widget:
        self.eco_flow = Gtk.FlowBox()
        self.eco_flow.set_valign(Gtk.Align.START)
        self.eco_flow.set_max_children_per_line(4)
        self.eco_flow.set_min_children_per_line(2)
        self.eco_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.eco_flow.set_homogeneous(True)
        self.eco_flow.set_column_spacing(10)
        self.eco_flow.set_row_spacing(10)
        return _card(self.eco_flow)

    def _build_system(self) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.sys_updates = Gtk.Label(label="Aggiornamenti: —", xalign=0)
        self.sys_services = Gtk.Label(label="Servizi Nova: —", xalign=0)
        self.sys_services.set_line_wrap(True)
        self.sys_errors = Gtk.Label(label="Errori: nessuno", xalign=0)
        self.sys_errors.set_line_wrap(True)
        self.sys_notes = Gtk.Label(label="Notifiche: —", xalign=0)
        self.sys_notes.set_line_wrap(True)
        for w in (self.sys_updates, self.sys_services, self.sys_errors, self.sys_notes):
            box.pack_start(w, False, False, 0)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_check = Gtk.Button(label="Controlla aggiornamenti")
        btn_check.connect("clicked", lambda *_: self._check_updates())
        btn_apply = Gtk.Button(label="Installa aggiornamenti")
        btn_apply.connect("clicked", lambda *_: self._apply_updates())
        btn_row.pack_start(btn_check, False, False, 0)
        btn_row.pack_start(btn_apply, False, False, 0)
        box.pack_start(btn_row, False, False, 0)
        return _card(box)

    def _run_action(self, fn) -> None:
        ok = fn()
        self.status.set_text("Aperto." if ok else "Comando non disponibile su questo sistema.")

    def _poll(self) -> bool:
        if not self._refreshing:
            self.refresh()
        return True

    def refresh(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True
        self.status.set_text("Aggiornamento dati…")

        def work() -> None:
            try:
                data = api.get_home()
                GLib.idle_add(self._render, data, None)
            except Exception as exc:  # noqa: BLE001
                GLib.idle_add(self._render, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _set_metric(self, key: str, text: str, style: str | None = None) -> None:
        w = self._widgets.get(key)
        if not isinstance(w, Gtk.Label):
            return
        w.set_text(text)
        ctx = w.get_style_context()
        for c in ("hub-ok", "hub-warn", "hub-critical"):
            ctx.remove_class(c)
        if style:
            ctx.add_class(style)

    def _set_bar(self, bar: Gtk.ProgressBar, pct: float | None, text: str) -> None:
        if pct is None:
            bar.set_fraction(0.0)
            bar.set_text(text)
        else:
            bar.set_fraction(pct / 100.0)
            bar.set_text(text)

    def _render(self, data, error) -> bool:
        self._refreshing = False
        if error:
            self.status.set_text(f"Errore: {error}")
            return False
        assert data is not None

        host = data.get("hostname") or ""
        welcome = data.get("welcome") or "Benvenuto"
        if host:
            welcome = f"{welcome}, {host}"
        self.welcome.set_text(welcome)
        ver = data.get("novaos_version") or "—"
        self.version_lbl.set_text(
            f"{data.get('pretty_name') or 'NovaOS'} · Hub {data.get('hub_version') or ''}"
        )

        self._set_metric("uptime", str(data.get("uptime_human") or "—"))
        cpu = _pct(data.get("cpu_percent"))
        self._set_metric("cpu", f"{cpu:.0f}%" if cpu is not None else "—")
        self._set_bar(
            self.cpu_bar,
            cpu,
            f"{cpu:.0f}%" if cpu is not None else "—",
        )
        ram = _pct(data.get("memory_percent"))
        self._set_metric("ram", f"{ram:.0f}%" if ram is not None else "—")
        self._set_bar(self.ram_bar, ram, str(data.get("memory_human") or "—"))
        disk_raw = data.get("disk_percent")
        disk = _pct(disk_raw)
        self._set_metric("disk", str(disk_raw) if disk_raw is not None else "—")
        self._set_bar(self.disk_bar, disk, str(data.get("disk_human") or "—"))
        self._set_metric("net", str(data.get("network_label") or "—"))

        plat = data.get("platform") or {}
        self._set_metric(
            "platform",
            str(plat.get("label") or "—"),
            "hub-ok" if plat.get("ok") else "hub-critical",
        )
        upd = data.get("update") or {}
        pending = int(upd.get("pending_count") or 0)
        upd_txt = f"{upd.get('service') or '—'} · {pending} pending"
        style = "hub-ok"
        if pending:
            style = "hub-warn"
        if upd.get("error") or upd.get("service") not in (None, "attivo"):
            if not pending:
                style = "hub-warn"
        self._set_metric("update", upd_txt, style)

        # Ecosystem
        for child in list(self.eco_flow.get_children()):
            self.eco_flow.remove(child)
        for app in data.get("ecosystem") or []:
            self.eco_flow.add(self._eco_card(app))
        self.eco_flow.show_all()

        # News
        for child in list(self.news_box.get_children()):
            self.news_box.remove(child)
        for item in data.get("news") or []:
            title = Gtk.Label(label=str(item.get("title") or "—"), xalign=0)
            title.get_style_context().add_class("hub-eco-name")
            summary = Gtk.Label(
                label=f"{item.get('date') or ''} — {item.get('summary') or ''}".strip(" —"),
                xalign=0,
            )
            summary.get_style_context().add_class("hub-eco-tag")
            summary.set_line_wrap(True)
            wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            wrap.pack_start(title, False, False, 0)
            wrap.pack_start(summary, False, False, 0)
            self.news_box.pack_start(wrap, False, False, 0)
        if not (data.get("news") or []):
            empty = Gtk.Label(label="Nessuna novità al momento.", xalign=0)
            empty.get_style_context().add_class("hub-muted")
            self.news_box.pack_start(empty, False, False, 0)
        self.news_box.show_all()

        # System
        self.sys_updates.set_text(
            f"Aggiornamenti disponibili: {pending}"
            + (f" (canale {upd.get('channel')})" if upd.get("channel") else "")
        )
        services = data.get("services") or []
        if services:
            names = []
            for s in services[:8]:
                if isinstance(s, dict):
                    names.append(str(s.get("name") or s.get("id") or s.get("unit") or "?"))
                else:
                    names.append(str(s))
            self.sys_services.set_text(f"Servizi Nova: {', '.join(names)}")
        else:
            self.sys_services.set_text("Servizi Nova: — (nessun elenco)")
        errs = data.get("errors") or []
        self.sys_errors.set_text(
            "Errori: nessuno" if not errs else "Errori: " + " · ".join(str(e) for e in errs[:4])
        )
        if errs:
            self.sys_errors.get_style_context().add_class("hub-critical")
        else:
            self.sys_errors.get_style_context().remove_class("hub-critical")
        notes = data.get("notifications") or []
        if notes:
            self.sys_notes.set_text(
                "Notifiche: " + " · ".join(str(n.get("text") or n) for n in notes[:4])
            )
        else:
            self.sys_notes.set_text("Notifiche: nessuna")

        self.status.set_text(f"Aggiornato · NovaOS {ver} · API {data.get('api')}")
        return False

    def _eco_card(self, app: dict) -> Gtk.Widget:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_border_width(10)
        name = Gtk.Label(label=str(app.get("name") or "—"), xalign=0)
        name.get_style_context().add_class("hub-eco-name")
        tag = Gtk.Label(label=str(app.get("tagline") or ""), xalign=0)
        tag.get_style_context().add_class("hub-eco-tag")
        tag.set_line_wrap(True)
        status = Gtk.Label(label=str(app.get("status") or ""), xalign=0)
        status.get_style_context().add_class(
            "hub-ok" if app.get("available") else "hub-muted"
        )
        box.pack_start(name, False, False, 0)
        box.pack_start(tag, False, False, 0)
        box.pack_start(status, False, False, 0)
        btn = Gtk.Button(label="Apri" if app.get("available") else "Presto")
        btn.set_sensitive(bool(app.get("available") and app.get("command")))
        cmd = app.get("command")
        btn.connect(
            "clicked",
            lambda *_a, c=cmd: self._run_action(lambda: launch.open_command(c)),
        )
        box.pack_start(btn, False, False, 0)
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        frame.add(box)
        return frame

    def _check_updates(self) -> None:
        self.status.set_text("Controllo aggiornamenti…")

        def work() -> None:
            try:
                result = api.check_updates()
                GLib.idle_add(self._update_done, result, None)
            except Exception as exc:  # noqa: BLE001
                GLib.idle_add(self._update_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _apply_updates(self) -> None:
        self.status.set_text("Installazione aggiornamenti…")

        def work() -> None:
            try:
                result = api.apply_updates()
                GLib.idle_add(self._update_done, result, None)
            except Exception as exc:  # noqa: BLE001
                GLib.idle_add(self._update_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _update_done(self, result, error) -> bool:
        if error:
            self.status.set_text(f"Errore update: {error}")
        else:
            pending = (result or {}).get("pending") or (result or {}).get("packages") or []
            self.status.set_text(f"Update OK · {len(pending) if isinstance(pending, list) else 'fatto'}")
        self.refresh()
        return False


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if "--snapshot" in argv or "--json" in argv:
        print(json.dumps(api.snapshot(), indent=2, ensure_ascii=False))
        return 0
    win = NovaHubWindow()
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
