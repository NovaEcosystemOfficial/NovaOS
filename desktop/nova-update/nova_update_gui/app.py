"""Nova Update GTK GUI — official Applications menu client."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Pango  # noqa: E402

# Allow running from monorepo without install
_UPDATE_LIB = Path("/usr/lib/nova/update")
_DEV_LIB = Path(__file__).resolve().parents[2] / "system" / "update"
for candidate in (_UPDATE_LIB, _DEV_LIB):
    if (candidate / "nova_update").is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        break

from nova_update.client import UpdateClient  # noqa: E402
from nova_update.config import UpdateConfig  # noqa: E402

CHANNELS = [
    ("stable", "Stable"),
    ("beta", "Beta"),
    ("developer", "Developer"),
    ("nightly", "Nightly"),
]


def read_os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    for path in (Path("/etc/os-release"), Path("/usr/lib/os-release")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            k, v = line.split("=", 1)
            data[k] = v.strip().strip('"')
        break
    return data


def service_status() -> str:
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "nova-updated.service"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        state = (proc.stdout or proc.stderr or "").strip() or "unknown"
        if state == "active":
            return "attivo"
        if state == "inactive":
            return "inattivo"
        return state
    except Exception:
        cfg = UpdateConfig.load()
        sock = Path(os.environ.get("NOVA_UPDATE_SOCKET", cfg.socket_path))
        return "attivo (socket)" if sock.exists() else "non raggiungibile"


class NovaUpdateWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Nova Update")
        self.set_default_size(720, 560)
        self.set_border_width(16)
        self.client = self._make_client()
        self.pending: list[dict] = []

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(root)

        title = Gtk.Label(label="Nova Update")
        title.get_style_context().add_class("title")
        title.set_halign(Gtk.Align.START)
        title.override_font(Pango.FontDescription("Sans Bold 18"))
        root.pack_start(title, False, False, 0)

        # Version + channel + service
        info = Gtk.Grid(column_spacing=12, row_spacing=8)
        root.pack_start(info, False, False, 0)

        self.version_label = Gtk.Label(label="—", xalign=0)
        self.channel_combo = Gtk.ComboBoxText()
        for cid, label in CHANNELS:
            self.channel_combo.append(cid, label)
        self.channel_combo.connect("changed", self._on_channel_changed)
        self.service_label = Gtk.Label(label="—", xalign=0)

        info.attach(Gtk.Label(label="Versione NovaOS:", xalign=0), 0, 0, 1, 1)
        info.attach(self.version_label, 1, 0, 1, 1)
        info.attach(Gtk.Label(label="Canale aggiornamenti:", xalign=0), 0, 1, 1, 1)
        info.attach(self.channel_combo, 1, 1, 1, 1)
        info.attach(Gtk.Label(label="Servizio nova-updated:", xalign=0), 0, 2, 1, 1)
        info.attach(self.service_label, 1, 2, 1, 1)

        # Pending list
        pending_frame = Gtk.Frame(label="Aggiornamenti disponibili")
        root.pack_start(pending_frame, True, True, 0)
        self.pending_store = Gtk.ListStore(str, str, str)
        tree = Gtk.TreeView(model=self.pending_store)
        for i, title_col in enumerate(("Pacchetto", "Versione", "Classe")):
            tree.append_column(Gtk.TreeViewColumn(title_col, Gtk.CellRendererText(), text=i))
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(tree)
        pending_frame.add(scroll)

        # History
        hist_frame = Gtk.Frame(label="Cronologia aggiornamenti")
        root.pack_start(hist_frame, True, True, 0)
        self.history_store = Gtk.ListStore(str, str, str)
        hist_tree = Gtk.TreeView(model=self.history_store)
        for i, title_col in enumerate(("Data", "Pacchetti", "Canale")):
            hist_tree.append_column(
                Gtk.TreeViewColumn(title_col, Gtk.CellRendererText(), text=i)
            )
        hist_scroll = Gtk.ScrolledWindow()
        hist_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hist_scroll.add(hist_tree)
        hist_frame.add(hist_scroll)

        self.status_bar = Gtk.Label(label="Pronto.", xalign=0)
        root.pack_start(self.status_bar, False, False, 0)

        buttons = Gtk.Box(spacing=8)
        buttons.set_halign(Gtk.Align.END)
        root.pack_start(buttons, False, False, 0)

        self.btn_refresh = Gtk.Button(label="Aggiorna stato")
        self.btn_check = Gtk.Button(label="Controlla aggiornamenti")
        self.btn_install = Gtk.Button(label="Installa aggiornamenti")
        self.btn_install.get_style_context().add_class("suggested-action")
        self.btn_refresh.connect("clicked", lambda *_: self.refresh())
        self.btn_check.connect("clicked", self._on_check)
        self.btn_install.connect("clicked", self._on_install)
        buttons.pack_start(self.btn_refresh, False, False, 0)
        buttons.pack_start(self.btn_check, False, False, 0)
        buttons.pack_start(self.btn_install, False, False, 0)

        self._suppress_channel = False
        self.refresh()

    def _make_client(self) -> UpdateClient:
        cfg = UpdateConfig.load()
        sock = Path(os.environ.get("NOVA_UPDATE_SOCKET", cfg.socket_path))
        return UpdateClient(sock)

    def _set_status(self, text: str) -> None:
        self.status_bar.set_text(text)

    def refresh(self) -> None:
        osrel = read_os_release()
        pretty = osrel.get("PRETTY_NAME") or osrel.get("VERSION") or "sconosciuta"
        version = osrel.get("VERSION") or osrel.get("VERSION_ID") or ""
        self.version_label.set_text(f"{pretty} ({version})" if version else pretty)
        self.service_label.set_text(service_status())

        try:
            ch = self.client.call("GetChannel")
            current = ch.get("channel", "stable")
            self._suppress_channel = True
            self.channel_combo.set_active_id(current)
            self._suppress_channel = False
            st = self.client.call("GetStatus")
            self.pending = st.get("pending") or []
            self._fill_pending(self.pending)
            hist = self.client.call("GetHistory")
            self._fill_history(hist.get("history") or [])
            self._set_status(
                f"Ultimo check: {st.get('last_check') or 'mai'} · backend={st.get('backend')}"
            )
        except (FileNotFoundError, ConnectionRefusedError, PermissionError, OSError, RuntimeError) as exc:
            self._set_status(f"Broker non raggiungibile: {exc}")

    def _fill_pending(self, pending: list[dict]) -> None:
        self.pending_store.clear()
        for pkg in pending:
            self.pending_store.append(
                [
                    str(pkg.get("name", "")),
                    f"{pkg.get('version', '')}-{pkg.get('release', '')}",
                    str(pkg.get("update_class", "")),
                ]
            )

    def _fill_history(self, history: list[dict]) -> None:
        self.history_store.clear()
        for entry in history:
            pkgs = entry.get("packages") or []
            names = ", ".join(
                f"{p.get('name')} {p.get('version')}-{p.get('release')}" for p in pkgs
            )
            self.history_store.append(
                [
                    str(entry.get("timestamp", "")),
                    names or "—",
                    str(entry.get("channel", "")),
                ]
            )

    def _on_channel_changed(self, combo: Gtk.ComboBoxText) -> None:
        if self._suppress_channel:
            return
        channel = combo.get_active_id()
        if not channel:
            return
        try:
            self.client.call("SetChannel", {"channel": channel})
            self._set_status(f"Canale impostato: {channel}")
        except Exception as exc:
            self._set_status(f"Errore canale: {exc}")

    def _on_check(self, *_args) -> None:
        self.btn_check.set_sensitive(False)
        self._set_status("Controllo aggiornamenti…")

        def work() -> None:
            try:
                result = self.client.call("Check")
                GLib.idle_add(self._check_done, result, None)
            except Exception as exc:
                GLib.idle_add(self._check_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _check_done(self, result, error) -> bool:
        self.btn_check.set_sensitive(True)
        if error:
            self._set_status(f"Check fallito: {error}")
            return False
        self.pending = result.get("pending") or []
        self._fill_pending(self.pending)
        n = len(self.pending)
        self._set_status(
            f"Trovati {n} aggiornamenti." if n else "Sistema aggiornato: nessun update."
        )
        try:
            hist = self.client.call("GetHistory")
            self._fill_history(hist.get("history") or [])
        except Exception:
            pass
        return False

    def _on_install(self, *_args) -> None:
        if not self.pending:
            self._set_status("Nessun aggiornamento da installare. Esegui prima il controllo.")
            return
        self.btn_install.set_sensitive(False)
        self._set_status("Installazione aggiornamenti…")

        def work() -> None:
            try:
                result = self.client.call("Apply")
                GLib.idle_add(self._install_done, result, None)
            except Exception as exc:
                GLib.idle_add(self._install_done, None, exc)

        import threading

        threading.Thread(target=work, daemon=True).start()

    def _install_done(self, result, error) -> bool:
        self.btn_install.set_sensitive(True)
        if error:
            self._set_status(f"Installazione fallita: {error}")
            return False
        applied = result.get("applied") or []
        names = ", ".join(p.get("name", "?") for p in applied) or "nessuno"
        self._set_status(f"Installati: {names}")
        self.refresh()
        return False


def main() -> int:
    # Prefer Wayland/X11 from session; fall back for headless smoke.
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        print("Nova Update GUI requires a graphical session.", file=sys.stderr)
        print(json.dumps({"os": read_os_release(), "service": service_status()}, indent=2))
        return 2
    win = NovaUpdateWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
