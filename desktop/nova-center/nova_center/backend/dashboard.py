"""Dashboard aggregates — live system health for Nova Center."""

from __future__ import annotations

import time
from pathlib import Path

from . import hardware, system_info, updates


def _read_cpu_times() -> tuple[int, int] | None:
    """Return (idle, total) jiffies from /proc/stat."""
    try:
        line = Path("/proc/stat").read_text(encoding="utf-8").splitlines()[0]
    except OSError:
        return None
    parts = line.split()
    if not parts or parts[0] != "cpu" or len(parts) < 5:
        return None
    vals = [int(x) for x in parts[1:]]
    idle = vals[3] + (vals[4] if len(vals) > 4 else 0)  # idle + iowait
    total = sum(vals)
    return idle, total


def cpu_percent(sample_seconds: float = 0.12) -> float | None:
    """Sample CPU utilization between two /proc/stat reads."""
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
) -> dict:
    level = "ok"
    notes: list[str] = []
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
    if update_service and update_service not in ("attivo", "attivo (socket)"):
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


def collect() -> dict:
    sysinfo = system_info.collect()
    hw = hardware.collect()
    upd = updates.collect()
    cpu = cpu_percent()
    mem = hw.get("memory") or {}
    disk = _root_disk(hw.get("disks") or [])
    disk_pct = None
    if disk and disk.get("percent"):
        try:
            disk_pct = float(str(disk["percent"]).rstrip("%"))
        except ValueError:
            disk_pct = None
    bat = hw.get("battery")
    health = _health(
        cpu,
        mem.get("percent_used"),
        disk_pct,
        upd.get("service"),
        int(upd.get("pending_count") or 0),
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
        "battery": bat,
        "update_service": upd.get("service"),
        "update_channel": upd.get("channel"),
        "last_check": upd.get("last_check"),
        "pending_count": upd.get("pending_count"),
        "health": health,
    }
