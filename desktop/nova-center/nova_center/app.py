"""Nova Center GTK GUI — official NovaOS control panel."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk  # noqa: E402

from nova_center import api  # noqa: E402

SECTIONS = [
    ("dashboard", "Dashboard"),
    ("hardware", "Hardware"),
    ("network", "Rete"),
    ("system", "Sistema"),
    ("services", "Nova Services"),
    ("updates", "Aggiornamenti"),
]

DASHBOARD_POLL_MS = 2000

CSS = b"""
window {
  background-color: #f4f6f8;
}
.nova-title {
  font-weight: bold;
  font-size: 18pt;
  color: #0f2744;
}
.nova-subtitle {
  color: #4a5d73;
}
.health-ok { color: #1b7a4e; font-weight: bold; }
.health-warn { color: #9a6b00; font-weight: bold; }
.health-critical { color: #a32020; font-weight: bold; }
.meter-label { color: #334155; }
.sidebar-row {
  padding: 4px 0;
}
progressbar trough {
  min-height: 12px;
  border-radius: 6px;
  background-color: #d9e2ec;
}
progressbar progress {
  min-height: 12px;
  border-radius: 6px;
  background-color: #1f6feb;
}
"""


def _fmt_ts(value) -> str:
    if not value:
        return "mai"
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).astimezone().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except (OSError, OverflowError, ValueError):
            return str(value)
    return str(value)


def _kv_grid(pairs: list[tuple[str, str]]) -> Gtk.Grid:
    grid = Gtk.Grid(column_spacing=16, row_spacing=8)
    for row, (key, val) in enumerate(pairs):
        k = Gtk.Label(label=key, xalign=0)
        k.get_style_context().add_class("dim-label")
        v = Gtk.Label(label=val or "—", xalign=0)
        v.set_line_wrap(True)
        v.set_max_width_chars(72)
        v.set_selectable(True)
        grid.attach(k, 0, row, 1, 1)
        grid.attach(v, 1, row, 1, 1)
    return grid


def _frame(title: str, child: Gtk.Widget) -> Gtk.Frame:
    frame = Gtk.Frame(label=title)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_border_width(12)
    box.pack_start(child, True, True, 0)
    frame.add(box)
    return frame


def _scroll(child: Gtk.Widget) -> Gtk.ScrolledWindow:
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scroll.add(child)
    return scroll


def _meter_row(title: str, fraction: float | None, text: str) -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    label = Gtk.Label(label=title, xalign=0)
    label.get_style_context().add_class("meter-label")
    bar = Gtk.ProgressBar()
    bar.set_show_text(True)
    if fraction is None:
        bar.set_fraction(0.0)
        bar.set_text(text or "—")
    else:
        bar.set_fraction(max(0.0, min(1.0, fraction)))
        bar.set_text(text)
    box.pack_start(label, False, False, 0)
    box.pack_start(bar, False, False, 0)
    box._progress = bar  # type: ignore[attr-defined]
    return box


class NovaCenterWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Nova Center")
        self.set_default_size(960, 680)
        self.set_border_width(0)
        self._dash_widgets: dict[str, Gtk.Widget] = {}
        self._poll_id = 0
        self._refreshing = False

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(outer)

        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        header.set_border_width(16)
        outer.pack_start(header, False, False, 0)

        title_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.pack_start(title_row, False, False, 0)

        title = Gtk.Label(label="Nova Center")
        title.set_halign(Gtk.Align.START)
        title.get_style_context().add_class("nova-title")
        title_row.pack_start(title, True, True, 0)

        self.btn_refresh = Gtk.Button(label="Aggiorna")
        self.btn_refresh.connect("clicked", lambda *_: self.refresh())
        title_row.pack_end(self.btn_refresh, False, False, 0)

        self.subtitle = Gtk.Label(label="Pannello di controllo NovaOS", xalign=0)
        self.subtitle.get_style_context().add_class("nova-subtitle")
        header.pack_start(self.subtitle, False, False, 0)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        outer.pack_start(body, True, True, 0)

        self.sidebar = Gtk.ListBox()
        self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar.set_size_request(180, -1)
        for sid, label in SECTIONS:
            row = Gtk.ListBoxRow()
            row._section_id = sid  # type: ignore[attr-defined]
            row.get_style_context().add_class("sidebar-row")
            lbl = Gtk.Label(label=label, xalign=0)
            lbl.set_margin_start(12)
            lbl.set_margin_end(12)
            lbl.set_margin_top(10)
            lbl.set_margin_bottom(10)
            row.add(lbl)
            self.sidebar.add(row)
        self.sidebar.connect("row-selected", self._on_section)
        body.pack_start(self.sidebar, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        body.pack_start(sep, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        body.pack_start(self.stack, True, True, 0)

        self.pages: dict[str, Gtk.Box] = {}
        for sid, _label in SECTIONS:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            page.set_border_width(16)
            self.pages[sid] = page
            self.stack.add_named(_scroll(page), sid)

        self.status_bar = Gtk.Label(label="Pronto.", xalign=0)
        self.status_bar.set_margin_start(16)
        self.status_bar.set_margin_end(16)
        self.status_bar.set_margin_bottom(12)
        outer.pack_start(self.status_bar, False, False, 0)

        self.sidebar.select_row(self.sidebar.get_row_at_index(0))
        self.refresh()
        self._poll_id = GLib.timeout_add(DASHBOARD_POLL_MS, self._poll_dashboard)

    def _on_section(self, _listbox, row) -> None:
        if row is None:
            return
        sid = getattr(row, "_section_id", None)
        if sid:
            self.stack.set_visible_child_name(sid)

    def _clear_page(self, sid: str) -> None:
        page = self.pages[sid]
        for child in list(page.get_children()):
            page.remove(child)

    def _set_status(self, text: str) -> None:
        self.status_bar.set_text(text)

    def _poll_dashboard(self) -> bool:
        if self._refreshing:
            return True
        if self.stack.get_visible_child_name() != "dashboard":
            return True
        if not self._dash_widgets:
            return True

        def work() -> None:
            try:
                data = api.get_dashboard()
                GLib.idle_add(self._update_dashboard_live, data)
            except Exception:  # noqa: BLE001
                pass

        import threading

        threading.Thread(target=work, daemon=True).start()
        return True

    def _update_dashboard_live(self, d: dict) -> bool:
        w = self._dash_widgets
        if not w:
            return False
        health = d.get("health") or {}
        if "health_label" in w:
            lbl: Gtk.Label = w["health_label"]  # type: ignore[assignment]
            ctx = lbl.get_style_context()
            for cls in ("health-ok", "health-warn", "health-critical"):
                ctx.remove_class(cls)
            level = health.get("level") or "ok"
            ctx.add_class(f"health-{level}")
            notes = health.get("notes") or []
            note = f" — {'; '.join(notes)}" if notes else ""
            lbl.set_text(f"{health.get('label') or '—'}{note}")
        if "uptime" in w:
            w["uptime"].set_text(str(d.get("uptime_human") or "—"))  # type: ignore[union-attr]
        cpu = d.get("cpu_percent")
        if "cpu_bar" in w:
            bar: Gtk.ProgressBar = w["cpu_bar"]  # type: ignore[assignment]
            if cpu is None:
                bar.set_fraction(0.0)
                bar.set_text("—")
            else:
                bar.set_fraction(cpu / 100.0)
                bar.set_text(f"{cpu:.1f}%")
        mem = d.get("memory") or {}
        mp = mem.get("percent_used")
        if "ram_bar" in w:
            bar = w["ram_bar"]  # type: ignore[assignment]
            if mp is None:
                bar.set_fraction(0.0)
                bar.set_text("—")
            else:
                bar.set_fraction(float(mp) / 100.0)
                bar.set_text(
                    f"{mp}% · {mem.get('used_human')} / {mem.get('total_human')}"
                )
        disk = d.get("disk_root") or {}
        if "disk_bar" in w:
            bar = w["disk_bar"]  # type: ignore[assignment]
            pct = None
            if disk.get("percent"):
                try:
                    pct = float(str(disk["percent"]).rstrip("%"))
                except ValueError:
                    pct = None
            if pct is None:
                bar.set_fraction(0.0)
                bar.set_text("—")
            else:
                bar.set_fraction(pct / 100.0)
                bar.set_text(
                    f"{disk.get('percent')} · {disk.get('used_human')} / {disk.get('size_human')}"
                )
        bat = d.get("battery")
        if "battery_line" in w and bat and bat.get("present"):
            cap = bat.get("capacity_percent")
            w["battery_line"].set_text(  # type: ignore[union-attr]
                f"{bat.get('status') or '—'} · {cap}%" if cap is not None else str(bat.get("status") or "—")
            )
        self._set_status(
            f"Live · CPU {cpu if cpu is not None else '—'}% · "
            f"RAM {mp if mp is not None else '—'}% · uptime {d.get('uptime_human') or '—'}"
        )
        return False

    def refresh(self) -> None:
        if self._refreshing:
            return
        self._refreshing = True
        self.btn_refresh.set_sensitive(False)
        self._set_status("Lettura dati di sistema…")

        def work() -> None:
            try:
                data = {
                    "dashboard": api.get_dashboard(),
                    "hardware": api.get_hardware(),
                    "network": api.get_network(),
                    "system": api.get_system(),
                    "services": api.get_services(),
                    "updates": api.get_updates(),
                }
                GLib.idle_add(self._refresh_done, data, None)
            except Exception as exc:  # noqa: BLE001 — surface to UI
                GLib.idle_add(self._refresh_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _refresh_done(self, data, error) -> bool:
        self._refreshing = False
        self.btn_refresh.set_sensitive(True)
        if error:
            self._set_status(f"Errore: {error}")
            return False
        assert data is not None
        self._render_dashboard(data["dashboard"])
        self._render_hardware(data["hardware"])
        self._render_network(data["network"])
        self._render_system(data["system"])
        self._render_services(data["services"])
        self._render_updates(data["updates"])
        ver = data["dashboard"].get("novaos_version") or "—"
        self.subtitle.set_text(
            f"{data['dashboard'].get('pretty_name') or 'NovaOS'} · Center "
            f"{data['dashboard'].get('center_version') or ''}"
        )
        self._set_status(f"Aggiornato · NovaOS {ver} · API {data['dashboard'].get('api')}")
        return False

    def _render_dashboard(self, d: dict) -> None:
        self._clear_page("dashboard")
        self._dash_widgets = {}
        page = self.pages["dashboard"]

        health = d.get("health") or {}
        health_lbl = Gtk.Label(xalign=0)
        level = health.get("level") or "ok"
        health_lbl.get_style_context().add_class(f"health-{level}")
        notes = health.get("notes") or []
        note = f" — {'; '.join(notes)}" if notes else ""
        health_lbl.set_text(f"{health.get('label') or '—'}{note}")
        self._dash_widgets["health_label"] = health_lbl
        page.pack_start(_frame("Stato generale", health_lbl), False, False, 0)

        uptime_lbl = Gtk.Label(label=str(d.get("uptime_human") or "—"), xalign=0)
        uptime_lbl.set_selectable(True)
        self._dash_widgets["uptime"] = uptime_lbl
        page.pack_start(
            _frame(
                "Identità",
                _kv_grid(
                    [
                        ("Versione NovaOS", str(d.get("novaos_version") or "—")),
                        ("Nome", str(d.get("pretty_name") or "—")),
                        ("Hostname", str(d.get("hostname") or "—")),
                        ("Kernel", str(d.get("kernel") or "—")),
                        ("Architettura", str(d.get("architecture") or "—")),
                    ]
                ),
            ),
            False,
            False,
            0,
        )
        page.pack_start(_frame("Uptime", uptime_lbl), False, False, 0)

        meters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        cpu = d.get("cpu_percent")
        cpu_row = _meter_row(
            f"CPU · {d.get('cpu_cores') or '—'} core",
            (cpu / 100.0) if cpu is not None else None,
            f"{cpu:.1f}%" if cpu is not None else "—",
        )
        self._dash_widgets["cpu_bar"] = cpu_row._progress  # type: ignore[attr-defined]
        meters.pack_start(cpu_row, False, False, 0)

        mem = d.get("memory") or {}
        mp = mem.get("percent_used")
        ram_row = _meter_row(
            "RAM",
            (float(mp) / 100.0) if mp is not None else None,
            (
                f"{mp}% · {mem.get('used_human')} / {mem.get('total_human')}"
                if mp is not None
                else "—"
            ),
        )
        self._dash_widgets["ram_bar"] = ram_row._progress  # type: ignore[attr-defined]
        meters.pack_start(ram_row, False, False, 0)

        disk = d.get("disk_root") or {}
        dp = None
        if disk.get("percent"):
            try:
                dp = float(str(disk["percent"]).rstrip("%"))
            except ValueError:
                dp = None
        disk_row = _meter_row(
            f"Disco · {disk.get('mount') or '/'}",
            (dp / 100.0) if dp is not None else None,
            (
                f"{disk.get('percent')} · {disk.get('used_human')} / {disk.get('size_human')}"
                if disk
                else "—"
            ),
        )
        self._dash_widgets["disk_bar"] = disk_row._progress  # type: ignore[attr-defined]
        meters.pack_start(disk_row, False, False, 0)
        page.pack_start(_frame("Utilizzo in tempo reale", meters), False, False, 0)

        bat = d.get("battery")
        if bat and bat.get("present"):
            bat_lbl = Gtk.Label(xalign=0)
            cap = bat.get("capacity_percent")
            bat_lbl.set_text(
                f"{bat.get('status') or '—'} · {cap}%"
                if cap is not None
                else str(bat.get("status") or "—")
            )
            bat_lbl.set_selectable(True)
            self._dash_widgets["battery_line"] = bat_lbl
            page.pack_start(
                _frame(
                    "Batteria",
                    _kv_grid(
                        [
                            ("Stato", str(bat.get("status") or "—")),
                            (
                                "Carica",
                                f"{cap}%" if cap is not None else "—",
                            ),
                            ("Modello", str(bat.get("name") or "—")),
                        ]
                    ),
                ),
                False,
                False,
                0,
            )

        page.pack_start(
            _frame(
                "Nova Update",
                _kv_grid(
                    [
                        ("Servizio", str(d.get("update_service") or "—")),
                        ("Canale", str(d.get("update_channel") or "—")),
                        ("Ultimo controllo", _fmt_ts(d.get("last_check"))),
                        ("Aggiornamenti in sospeso", str(d.get("pending_count", 0))),
                    ]
                ),
            ),
            False,
            False,
            0,
        )
        page.show_all()

    def _render_hardware(self, h: dict) -> None:
        self._clear_page("hardware")
        page = self.pages["hardware"]
        cpu = h.get("cpu") or {}
        mem = h.get("memory") or {}
        load = cpu.get("loadavg")
        load_s = ", ".join(f"{x:.2f}" for x in load) if load else "—"
        page.pack_start(
            _frame(
                "CPU",
                _kv_grid(
                    [
                        ("Modello", str(cpu.get("model") or "—")),
                        ("Core", str(cpu.get("cores") or "—")),
                        ("Load average", load_s),
                    ]
                ),
            ),
            False,
            False,
            0,
        )
        pct = mem.get("percent_used")
        page.pack_start(
            _frame(
                "Memoria",
                _kv_grid(
                    [
                        ("Installata", str(mem.get("total_human") or "—")),
                        ("Utilizzata", str(mem.get("used_human") or "—")),
                        ("Disponibile", str(mem.get("available_human") or "—")),
                        ("Uso", f"{pct}%" if pct is not None else "—"),
                    ]
                ),
            ),
            False,
            False,
            0,
        )

        disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        disks = h.get("disks") or []
        if not disks:
            disk_box.pack_start(Gtk.Label(label="Nessun volume rilevato", xalign=0), False, False, 0)
        for disk in disks:
            disk_box.pack_start(
                Gtk.Label(
                    label=(
                        f"{disk.get('mount')} · {disk.get('source')} · "
                        f"{disk.get('used_human')}/{disk.get('size_human')} ({disk.get('percent')})"
                    ),
                    xalign=0,
                ),
                False,
                False,
                0,
            )
        page.pack_start(_frame("Disco", disk_box), False, False, 0)

        gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for gpu in h.get("gpus") or ["—"]:
            gpu_box.pack_start(Gtk.Label(label=str(gpu), xalign=0), False, False, 0)
        page.pack_start(_frame("GPU", gpu_box), False, False, 0)

        temps = h.get("temperatures") or []
        if temps:
            tbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            for t in temps:
                tbox.pack_start(
                    Gtk.Label(
                        label=f"{t.get('name')}: {t.get('celsius'):.1f} °C",
                        xalign=0,
                    ),
                    False,
                    False,
                    0,
                )
            page.pack_start(_frame("Temperatura", tbox), False, False, 0)

        bat = h.get("battery")
        if bat and bat.get("present"):
            page.pack_start(
                _frame(
                    "Batteria",
                    _kv_grid(
                        [
                            ("Modello", str(bat.get("name") or "—")),
                            ("Stato", str(bat.get("status") or "—")),
                            (
                                "Carica",
                                f"{bat.get('capacity_percent')}%"
                                if bat.get("capacity_percent") is not None
                                else "—",
                            ),
                            ("Tecnologia", str(bat.get("technology") or "—")),
                        ]
                    ),
                ),
                False,
                False,
                0,
            )
        page.show_all()

    def _render_network(self, n: dict) -> None:
        self._clear_page("network")
        page = self.pages["network"]
        page.pack_start(
            _frame(
                "Connessione",
                _kv_grid(
                    [
                        ("Stato", str(n.get("status") or "—")),
                        ("Interfaccia predefinita", str(n.get("default_interface") or "—")),
                        ("Scheda di rete", str(n.get("primary_nic") or "—")),
                        ("Indirizzo IP", str(n.get("primary_ipv4") or "—")),
                    ]
                ),
            ),
            False,
            False,
            0,
        )

        def _dev_list(title: str, devices: list) -> None:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            if not devices:
                box.pack_start(Gtk.Label(label="Nessuna interfaccia", xalign=0), False, False, 0)
            for d in devices:
                conn = d.get("connection") or "—"
                box.pack_start(
                    Gtk.Label(
                        label=f"{d.get('device')} · {d.get('state')} · {conn}",
                        xalign=0,
                    ),
                    False,
                    False,
                    0,
                )
            page.pack_start(_frame(title, box), False, False, 0)

        _dev_list("Ethernet", n.get("ethernet") or [])

        wifi_details = n.get("wifi_details") or []
        if wifi_details:
            for w in wifi_details:
                sig = w.get("signal_percent")
                page.pack_start(
                    _frame(
                        f"Wi-Fi · {w.get('device') or 'scheda'}",
                        _kv_grid(
                            [
                                ("Scheda wireless", str(w.get("device") or "—")),
                                ("Stato", str(w.get("status") or w.get("state") or "—")),
                                ("SSID", str(w.get("ssid") or "—")),
                                (
                                    "Intensità segnale",
                                    f"{sig}%" if sig is not None else "—",
                                ),
                                ("Indirizzo IP", str(w.get("ipv4") or "—")),
                                ("Sicurezza", str(w.get("security") or "—")),
                                (
                                    "Riconnessione automatica",
                                    (
                                        "sì"
                                        if w.get("autoconnect") is True
                                        else "no"
                                        if w.get("autoconnect") is False
                                        else "—"
                                    ),
                                ),
                                ("Profilo NM", str(w.get("connection") or "—")),
                            ]
                        ),
                    ),
                    False,
                    False,
                    0,
                )
        else:
            _dev_list("Wi-Fi", n.get("wifi") or [])

        radio = n.get("wifi_radio") or {}
        supp = n.get("supplicant") or {}
        page.pack_start(
            _frame(
                "Stack wireless",
                _kv_grid(
                    [
                        ("Radio Wi-Fi", str(radio.get("wifi") or "—")),
                        ("Hardware Wi-Fi", str(radio.get("wifi_hw") or "—")),
                        ("wpa_supplicant", str(supp.get("wpa_supplicant") or "—")),
                        (
                            "usrmerge (/usr/sbin→bin)",
                            "ok" if supp.get("usrmerge_ok") else "rotto",
                        ),
                    ]
                ),
            ),
            False,
            False,
            0,
        )
        page.show_all()

    def _render_system(self, s: dict) -> None:
        self._clear_page("system")
        page = self.pages["system"]
        page.pack_start(
            _frame(
                "Informazioni sistema",
                _kv_grid(
                    [
                        ("PRETTY_NAME", str(s.get("pretty_name") or "—")),
                        ("VERSION_ID", str(s.get("version_id") or "—")),
                        ("VERSION", str(s.get("version") or "—")),
                        ("NAME", str(s.get("name") or "—")),
                        ("VARIANT", str(s.get("variant") or "—")),
                        ("ID_LIKE", str(s.get("id_like") or "—")),
                        ("Hostname", str(s.get("hostname") or "—")),
                        ("Kernel", str(s.get("kernel") or "—")),
                        ("Architettura", str(s.get("architecture") or "—")),
                        ("Utente", str(s.get("user") or "—")),
                    ]
                ),
            ),
            False,
            False,
            0,
        )
        paths = s.get("paths") or {}
        pbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        for path, exists in sorted(paths.items()):
            mark = "presente" if exists else "assente"
            pbox.pack_start(Gtk.Label(label=f"{path} · {mark}", xalign=0), False, False, 0)
        page.pack_start(_frame("Cartelle principali Nova", pbox), False, False, 0)

        # Live Nova service summary in System section
        try:
            svc = api.get_services()
            sbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            for item in svc.get("services") or []:
                sbox.pack_start(
                    Gtk.Label(
                        label=f"{item.get('label')}: {item.get('state')}",
                        xalign=0,
                    ),
                    False,
                    False,
                    0,
                )
            page.pack_start(_frame("Stato servizi Nova", sbox), False, False, 0)
        except Exception:  # noqa: BLE001
            pass
        page.show_all()

    def _render_services(self, s: dict) -> None:
        self._clear_page("services")
        page = self.pages["services"]
        for item in s.get("services") or []:
            pairs = [
                ("Unit", str(item.get("unit") or "—")),
                ("Stato", str(item.get("state") or "—")),
                (
                    "Socket",
                    (
                        f"{item.get('socket')} ({'ok' if item.get('socket_present') else 'assente'})"
                        if item.get("socket")
                        else "—"
                    ),
                ),
            ]
            if item.get("note"):
                pairs.append(("Nota", str(item["note"])))
            page.pack_start(_frame(str(item.get("label") or item.get("id")), _kv_grid(pairs)), False, False, 0)
        page.show_all()

    def _render_updates(self, u: dict) -> None:
        self._clear_page("updates")
        page = self.pages["updates"]
        pending = u.get("pending") or []
        avail = (
            f"{len(pending)} pacchetti"
            if pending
            else ("nessuno" if u.get("available") else "sconosciuto")
        )
        page.pack_start(
            _frame(
                "Nova Update",
                _kv_grid(
                    [
                        ("Servizio", str(u.get("service") or "—")),
                        ("Canale", str(u.get("channel") or "—")),
                        ("Backend", str(u.get("backend") or "—")),
                        ("Ultimo controllo", _fmt_ts(u.get("last_check"))),
                        ("Disponibilità", avail),
                        ("Errore", str(u.get("error") or "—")),
                    ]
                ),
            ),
            False,
            False,
            0,
        )

        store = Gtk.ListStore(str, str, str)
        for pkg in pending:
            store.append(
                [
                    str(pkg.get("name", "")),
                    f"{pkg.get('version', '')}-{pkg.get('release', '')}",
                    str(pkg.get("update_class", "")),
                ]
            )
        tree = Gtk.TreeView(model=store)
        for i, title in enumerate(("Pacchetto", "Versione", "Classe")):
            tree.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(), text=i))
        page.pack_start(_frame("Aggiornamenti disponibili", _scroll(tree)), True, True, 0)

        actions = Gtk.Box(spacing=8)
        actions.set_halign(Gtk.Align.START)
        self.btn_upd_check = Gtk.Button(label="Controlla aggiornamenti")
        self.btn_upd_install = Gtk.Button(label="Installa aggiornamenti")
        self.btn_upd_install.get_style_context().add_class("suggested-action")
        self.btn_upd_install.set_sensitive(bool(pending))
        btn_open = Gtk.Button(label="Apri Nova Update")
        self.btn_upd_check.connect("clicked", self._on_updates_check)
        self.btn_upd_install.connect("clicked", self._on_updates_install)
        btn_open.connect("clicked", self._open_nova_update)
        actions.pack_start(self.btn_upd_check, False, False, 0)
        actions.pack_start(self.btn_upd_install, False, False, 0)
        actions.pack_start(btn_open, False, False, 0)
        page.pack_start(actions, False, False, 0)
        page.show_all()

    def _on_updates_check(self, *_args) -> None:
        self.btn_upd_check.set_sensitive(False)
        self._set_status("Controllo aggiornamenti…")

        def work() -> None:
            try:
                result = api.check_updates()
                GLib.idle_add(self._updates_check_done, result, None)
            except Exception as exc:
                GLib.idle_add(self._updates_check_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _updates_check_done(self, result, error) -> bool:
        btn = getattr(self, "btn_upd_check", None)
        if btn is not None:
            btn.set_sensitive(True)
        if error:
            self._set_status(f"Check fallito: {error}")
            return False
        pending = result.get("pending") or []
        n = len(pending)
        if n:
            self._set_status(
                f"Trovati {n} aggiornamenti. Premi «Installa aggiornamenti» per applicarli."
            )
        else:
            self._set_status("Sistema aggiornato: nessun update.")
        self.refresh()
        return False

    def _on_updates_install(self, *_args) -> None:
        btn = getattr(self, "btn_upd_install", None)
        if btn is not None:
            btn.set_sensitive(False)
        self._set_status("Installazione aggiornamenti…")

        def work() -> None:
            try:
                result = api.apply_updates()
                GLib.idle_add(self._updates_install_done, result, None)
            except Exception as exc:
                GLib.idle_add(self._updates_install_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _updates_install_done(self, result, error) -> bool:
        if error:
            self._set_status(f"Installazione fallita: {error}")
            btn = getattr(self, "btn_upd_install", None)
            if btn is not None:
                btn.set_sensitive(True)
            return False
        applied = result.get("applied") or []
        names = ", ".join(p.get("name", "?") for p in applied) or "nessuno"
        self._set_status(f"Installati: {names}")
        self.refresh()
        return False

    def _open_nova_update(self, *_args) -> None:
        cmd = shutil.which("nova-update-gui")
        if not cmd:
            # Dev fallback
            repo = Path(__file__).resolve().parents[2] / "bin" / "nova-update-gui"
            # parents[2] = nova-center; sibling is nova-update
            sibling = Path(__file__).resolve().parents[3] / "nova-update" / "bin" / "nova-update-gui"
            if sibling.is_file():
                cmd = str(sibling)
            elif repo.is_file():
                cmd = str(repo)
        if not cmd:
            self._set_status("nova-update-gui non trovato")
            return
        try:
            subprocess.Popen([cmd], start_new_session=True)  # noqa: S603
            self._set_status("Nova Update avviato")
        except OSError as exc:
            self._set_status(f"Impossibile aprire Nova Update: {exc}")


def main() -> int:
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("Nova Center requires a graphical session.", file=sys.stderr)
        print(json.dumps(api.snapshot(), indent=2, default=str))
        return 2
    # Ensure package import when launched from /usr/share/nova/center
    win = NovaCenterWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
