"""Monitor Nova services (units, sockets, binaries)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from nova_platform.logging_setup import get_logger

log = get_logger("services")
ulog = get_logger("update")

# Catalog — extend as new Nova services ship.
NOVA_SERVICES = [
    {
        "id": "nova-platformd",
        "unit": "nova-platformd.service",
        "label": "Nova Platform",
        "socket": "/run/nova/platform.sock",
        "binary": "nova-platformd",
        "planned": False,
    },
    {
        "id": "nova-updated",
        "unit": "nova-updated.service",
        "label": "Nova Update Broker",
        "socket": "/run/nova/update.sock",
        "binary": "nova-updated",
        "planned": False,
    },
    {
        "id": "nova-center",
        "unit": None,
        "label": "Nova Center",
        "socket": None,
        "binary": "nova-center",
        "planned": False,
        "note": "Applicazione desktop (non systemd).",
    },
    {
        "id": "nova-welcome",
        "unit": None,
        "label": "Nova Welcome",
        "socket": None,
        "binary": "nova-welcome",
        "planned": False,
        "note": "First-boot wizard (autostart).",
    },
    {
        "id": "nova-update-gui",
        "unit": None,
        "label": "Nova Update GUI",
        "socket": None,
        "binary": "nova-update-gui",
        "planned": False,
    },
    {
        "id": "nova-ryuk",
        "unit": "nova-ryuk.service",
        "label": "Ryuk",
        "socket": None,
        "binary": "nova-ryuk",
        "planned": True,
        "note": "Pianificato.",
    },
    {
        "id": "nova-ai-core",
        "unit": "nova-ai-core.service",
        "label": "Nova AI Core",
        "socket": None,
        "binary": None,
        "planned": True,
        "note": "Pianificato.",
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
    unit = entry.get("unit")
    state = _systemctl_state(unit) if unit else "n/a"
    sock = entry.get("socket")
    socket_up = bool(sock and Path(sock).exists())
    binary = entry.get("binary")
    binary_present = bool(binary and shutil.which(binary))
    if unit and state in ("unknown", "inactive", "failed") and socket_up:
        state = "active (socket)"
    if not unit and binary_present:
        state = "installed"
    elif not unit and not binary_present:
        state = "not-installed"
    if entry.get("planned") and state in ("not-installed", "unknown", "inactive", "n/a"):
        state = "planned"
    errors: list[str] = []
    if entry.get("planned"):
        pass
    elif unit and state in ("failed",):
        errors.append(f"{unit} failed")
    elif sock and not socket_up and state not in ("planned", "not-installed"):
        errors.append(f"socket mancante: {sock}")
    elif binary and not binary_present and not entry.get("planned"):
        errors.append(f"binary mancante: {binary}")
    return {
        "id": entry["id"],
        "unit": unit,
        "label": entry["label"],
        "state": state,
        "socket": sock,
        "socket_present": socket_up,
        "binary": binary,
        "binary_present": binary_present,
        "planned": bool(entry.get("planned")),
        "note": entry.get("note"),
        "errors": errors,
        "ok": not errors and state not in ("failed",),
    }


def collect_services() -> dict:
    items = [_probe(entry) for entry in NOVA_SERVICES]
    for item in items:
        if item["errors"]:
            log.warning("%s: %s", item["id"], "; ".join(item["errors"]))
        else:
            log.info("%s state=%s", item["id"], item["state"])
        if item["id"] == "nova-updated":
            if item["socket_present"]:
                ulog.info("update.sock present state=%s", item["state"])
            else:
                ulog.warning("update.sock missing")
    return {
        "services": items,
        "nova_updated": next((s for s in items if s["id"] == "nova-updated"), None),
        "nova_platformd": next((s for s in items if s["id"] == "nova-platformd"), None),
        "ryuk": next((s for s in items if s["id"] == "nova-ryuk"), None),
    }


def health() -> dict:
    import os

    from nova_platform import API_VERSION, __version__
    from nova_platform.collectors import system

    services = collect_services()
    items = services["services"]
    errors: list[str] = []
    for s in items:
        errors.extend(s.get("errors") or [])
    platform_sock = Path(os.environ.get("NOVA_PLATFORM_SOCKET", "/run/nova/platform.sock"))
    sockets = {
        "platform": platform_sock.exists(),
        "update": Path("/run/nova/update.sock").exists(),
    }
    if not sockets["platform"]:
        errors.append(f"platform.sock assente ({platform_sock})")
    version = system.get_version()
    overall = "ok" if not errors else "degraded"
    if any(s.get("state") == "failed" for s in items):
        overall = "error"
    return {
        "status": overall,
        "api": API_VERSION,
        "version": __version__,
        "os": version,
        "sockets": sockets,
        "services": items,
        "errors": errors,
    }
