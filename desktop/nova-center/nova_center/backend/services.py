"""Nova service status probes (live systemd / sockets).

Ryuk and future services are listed as planned stubs until units exist.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# Catalog of Nova services for the control panel.
# status is always probed live; planned units report "not-installed".
NOVA_SERVICES = [
    {
        "id": "nova-updated",
        "unit": "nova-updated.service",
        "label": "Nova Update Broker",
        "socket": "/run/nova/update.sock",
        "planned": False,
    },
    {
        "id": "nova-ryuk",
        "unit": "nova-ryuk.service",
        "label": "Ryuk (assistente di sistema)",
        "socket": None,
        "planned": True,
        "note": "Integrazione predisposta — non implementata (Sprint 16).",
    },
    {
        "id": "nova-ai-core",
        "unit": "nova-ai-core.service",
        "label": "Nova AI Core",
        "socket": None,
        "planned": True,
        "note": "Pianificato — Platform Layer.",
    },
]


def _systemctl_state(unit: str) -> str:
    systemctl = shutil.which("systemctl")
    if not systemctl:
        return "unknown"
    try:
        proc = subprocess.run(
            [systemctl, "is-active", unit],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        state = (proc.stdout or "").strip()
        if state:
            return state
        # Distinguish missing unit
        show = subprocess.run(
            [systemctl, "show", unit, "-p", "LoadState", "--value"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        load = (show.stdout or "").strip()
        if load == "not-found":
            return "not-installed"
        return state or load or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _probe(entry: dict) -> dict:
    unit = entry["unit"]
    state = _systemctl_state(unit)
    sock = entry.get("socket")
    socket_up = bool(sock and Path(sock).exists())
    if state in ("unknown", "inactive", "failed") and socket_up:
        state = "active (socket)"
    if entry.get("planned") and state in ("not-installed", "unknown", "inactive"):
        # Planned units are not expected on Sprint 16 hosts.
        if state != "active":
            state = "planned"
    return {
        "id": entry["id"],
        "unit": unit,
        "label": entry["label"],
        "state": state,
        "socket": sock,
        "socket_present": socket_up,
        "planned": bool(entry.get("planned")),
        "note": entry.get("note"),
    }


def collect() -> dict:
    items = [_probe(entry) for entry in NOVA_SERVICES]
    return {
        "services": items,
        "ryuk": next((s for s in items if s["id"] == "nova-ryuk"), None),
        "nova_updated": next((s for s in items if s["id"] == "nova-updated"), None),
    }
