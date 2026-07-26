"""Dashboard aggregate for platform.v1 (used by Nova Center)."""

from __future__ import annotations

import time
from pathlib import Path

from . import hardware, system


def _read_cpu_times() -> tuple[int, int] | None:
    try:
        line = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0]
    except OSError:
        return None
    parts = line.split()
    if not parts or parts[0] != "cpu" or len(parts) < 5:
        return None
    vals = [int(x) for x in parts[1:]]
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
    total = sum(vals)
    return idle, total


def cpu_percent(sample_seconds: float = 0.12) -> float | None:
    a = _read_cpu_times()
    if a is None:
        return None
    time.sleep(max(sample_seconds, 0.05))
    b = _read_cpu_times()
    if b is None:
        return None
    idle_delta = b[0] - a[0]
    total_delta = b[1] - a[1]
    if total_delta <= 0:
        return 0.0
    busy = 1.0 - (idle_delta / total_delta)
    return round(max(0.0, min(100.0, busy * 100.0)), 1)


def _root_disk(disks: list[dict]) -> dict | None:
    for d in disks:
        if d.get("mount") == "/":
            return d
    return disks[0] if disks else None


def _health(
    cpu: float | None,
    mem_pct: float | None,
    disk_pct: float | None,
    update_service: str | None,
    pending: int,
    platform_ok: bool,
) -> dict:
    level = "ok"
    notes: list[str] = []
    if not platform_ok:
        level = "critical"
        notes.append("Nova Platform non attivo")
    if cpu is not None and cpu >= 90:
        level = "critical"
        notes.append("CPU molto alta")
    elif cpu is not None and cpu >= 75:
        level = "warn" if level == "ok" else level
        notes.append("CPU elevata")
    if mem_pct is not None and mem_pct >= 90:
        level = "critical"
        notes.append("RAM quasi esaurita")
    elif mem_pct is not None and mem_pct >= 80:
        level = "warn" if level == "ok" else level
        notes.append("RAM elevata")
    if disk_pct is not None and disk_pct >= 95:
        level = "critical"
        notes.append("Disco quasi pieno")
    elif disk_pct is not None and disk_pct >= 85:
        level = "warn" if level == "ok" else level
        notes.append("Disco in esaurimento")
    if update_service and update_service not in ("attivo", "attivo (socket)", "active", "active (socket)"):
        level = "warn" if level == "ok" else level
        notes.append("Nova Update non attivo")
    if pending:
        notes.append(f"{pending} aggiornamenti disponibili")
    labels = {"ok": "Sistema in salute", "warn": "Attenzione", "critical": "Critico"}
    return {
        "level": level,
        "label": labels.get(level, level),
        "notes": notes,
    }


def _update_summary() -> dict:
    """Best-effort summary from update broker without requiring Center."""
    base = {
        "service": "non raggiungibile",
        "channel": None,
        "last_check": None,
        "pending_count": 0,
    }
    sock = Path("/run/nova/update.sock")
    if not sock.exists():
        return base
    try:
        import sys

        for root in (Path("/usr/lib/nova/update"),):
            if (root / "nova_update").is_dir() and str(root) not in sys.path:
                sys.path.insert(0, str(root))
                break
        from nova_update.client import UpdateClient
        from nova_update.config import UpdateConfig

        cfg = UpdateConfig.load()
        client = UpdateClient(Path(cfg.socket_path))
        status = client.call("GetStatus")
        channel = client.call("GetChannel")
        pending = status.get("pending") or []
        return {
            "service": "attivo",
            "channel": channel.get("channel") or status.get("channel"),
            "last_check": status.get("last_check"),
            "pending_count": len(pending),
            "backend": status.get("backend"),
        }
    except Exception:
        return {**base, "service": "attivo (socket)" if sock.exists() else base["service"]}


def collect() -> dict:
    sysinfo = system.get_system_info()
    hw = hardware.collect()
    upd = _update_summary()
    cpu = cpu_percent()
    mem = hw.get("memory") or {}
    disk = _root_disk(hw.get("disks") or [])
    disk_pct = None
    if disk and disk.get("percent"):
        try:
            disk_pct = float(str(disk["percent"]).rstrip("%"))
        except ValueError:
            disk_pct = None
    health = _health(
        cpu,
        mem.get("percent_used"),
        disk_pct,
        upd.get("service"),
        int(upd.get("pending_count") or 0),
        platform_ok=True,
    )
    return {
        "novaos_version": sysinfo.get("version"),
        "pretty_name": sysinfo.get("pretty_name"),
        "hostname": sysinfo.get("hostname"),
        "kernel": sysinfo.get("kernel"),
        "architecture": sysinfo.get("architecture"),
        "uptime": sysinfo.get("uptime"),
        "uptime_human": sysinfo.get("uptime_human"),
        "cpu_percent": cpu,
        "cpu_model": (hw.get("cpu") or {}).get("model"),
        "cpu_cores": (hw.get("cpu") or {}).get("cores"),
        "cpu_loadavg": (hw.get("cpu") or {}).get("loadavg"),
        "memory": mem,
        "disk_root": disk,
        "battery": hw.get("battery"),
        "update_service": upd.get("service"),
        "update_channel": upd.get("channel"),
        "last_check": upd.get("last_check"),
        "pending_count": upd.get("pending_count"),
        "health": health,
    }
