"""Nova Notify Agent — session watcher for Nova Update events."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_CANDIDATES = (
    Path("/usr/share/nova/desktop"),
    Path(__file__).resolve().parents[1],
)
for _root in _CANDIDATES:
    if (_root / "nova_desktop").is_dir() and str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
        break

from nova_desktop.notify import notify  # noqa: E402

_UPDATE_CANDIDATES = (
    Path("/usr/lib/nova/update"),
    Path(__file__).resolve().parents[3] / "system" / "update",
)
for _root in _UPDATE_CANDIDATES:
    if (_root / "nova_update").is_dir() and str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
        break

STATE_PATH = Path.home() / ".config" / "nova" / "notify-state.json"
POLL_SEC = int(os.environ.get("NOVA_NOTIFY_POLL", "120"))
CHECK_EVERY = int(os.environ.get("NOVA_NOTIFY_CHECK_EVERY", "3"))  # polls


def _load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(data: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _client():
    try:
        from nova_update.client import UpdateClient
        from nova_update.config import UpdateConfig
    except ImportError:
        return None
    cfg = UpdateConfig.load()
    sock = Path(os.environ.get("NOVA_UPDATE_SOCKET", cfg.socket_path))
    return UpdateClient(sock)


def _pending_names(status: dict) -> list[str]:
    pending = status.get("pending") or []
    return sorted(str(p.get("name") or "") for p in pending if p.get("name"))


def _maybe_reboot_hint(applied: list[dict]) -> bool:
    keys = ("kernel", "glibc", "systemd", "novaos-release", "nova-desktop")
    names = {str(p.get("name") or "") for p in applied}
    return any(k in names for k in keys)


def tick(force_check: bool = False) -> None:
    client = _client()
    if client is None:
        return
    state = _load_state()
    try:
        if force_check:
            result = client.call("Check")
            status = result
        else:
            status = client.call("GetStatus")
    except Exception as exc:
        print(f"nova-notify-agent: broker: {exc}", file=sys.stderr)
        return

    names = _pending_names(status)
    prev = state.get("pending_names") or []
    if names and names != prev:
        body = ", ".join(names[:6])
        if len(names) > 6:
            body += f" (+{len(names) - 6})"
        notify(
            "Aggiornamento disponibile",
            f"{len(names)} pacchetti: {body}",
            icon="system-software-update",
        )
        state["pending_names"] = names
        state["last_available_notify"] = time.time()

    history = []
    try:
        hist = client.call("GetHistory")
        history = hist.get("history") or []
    except Exception:
        history = []

    if history:
        latest = history[0]
        stamp = str(latest.get("timestamp") or latest.get("id") or "")
        if stamp and stamp != state.get("last_history_stamp"):
            pkgs = latest.get("packages") or []
            names_h = ", ".join(p.get("name", "?") for p in pkgs[:5]) or "pacchetti"
            notify(
                "Aggiornamento installato",
                names_h,
                icon="emblem-ok",
            )
            state["last_history_stamp"] = stamp
            state["pending_names"] = []
            reboot = bool(status.get("reboot_required")) or _maybe_reboot_hint(pkgs)
            if reboot:
                notify(
                    "Riavvio consigliato",
                    "Alcuni aggiornamenti NovaOS richiedono un riavvio per essere completamente attivi.",
                    icon="system-reboot",
                    urgency="normal",
                )

    _save_state(state)


def main() -> int:
    if os.environ.get("NOVA_NOTIFY_ONCE") == "1":
        tick(force_check=True)
        return 0

    # Initial soft check after login
    time.sleep(8)
    polls = 0
    while True:
        force = polls % CHECK_EVERY == 0
        try:
            tick(force_check=force)
        except Exception as exc:  # pragma: no cover
            print(f"nova-notify-agent: {exc}", file=sys.stderr)
        polls += 1
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    raise SystemExit(main())
