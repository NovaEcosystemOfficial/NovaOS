"""Live system identity and host facts."""

from __future__ import annotations

import os
import platform
import socket
import time
from pathlib import Path


def read_os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    for path in (Path("/etc/os-release"), Path("/usr/lib/os-release")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key] = value.strip().strip('"')
        break
    return data


def _uptime_seconds() -> float | None:
    try:
        raw = Path("/proc/uptime").read_text(encoding="utf-8").split()[0]
        return float(raw)
    except OSError:
        return None


def _human_uptime(seconds: float | None) -> str:
    if seconds is None:
        return "sconosciuto"
    secs = int(seconds)
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    mins, _ = divmod(rem, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}g")
    if hours or days:
        parts.append(f"{hours}h")
    parts.append(f"{mins}m")
    return " ".join(parts)


def collect() -> dict:
    osrel = read_os_release()
    up = _uptime_seconds()
    try:
        hostname = socket.gethostname()
    except OSError:
        hostname = Path("/etc/hostname").read_text(encoding="utf-8").strip() if Path("/etc/hostname").is_file() else "unknown"
    return {
        "version": osrel.get("VERSION") or osrel.get("VERSION_ID") or "",
        "version_id": osrel.get("VERSION_ID") or "",
        "pretty_name": osrel.get("PRETTY_NAME") or osrel.get("NAME") or "NovaOS",
        "name": osrel.get("NAME") or "NovaOS",
        "hostname": hostname,
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "uptime": up,
        "uptime_human": _human_uptime(up),
        "boot_time": (time.time() - up) if up is not None else None,
    }


def collect_full() -> dict:
    base = collect()
    osrel = read_os_release()
    paths = {
        "/etc/nova": Path("/etc/nova").is_dir(),
        "/etc/novaos": Path("/etc/novaos").is_dir(),
        "/usr/lib/nova": Path("/usr/lib/nova").is_dir(),
        "/var/lib/nova": Path("/var/lib/nova").is_dir(),
        "/usr/share/nova": Path("/usr/share/nova").is_dir(),
    }
    return {
        **base,
        "os_release": osrel,
        "version_id": osrel.get("VERSION_ID") or "",
        "pretty_name": osrel.get("PRETTY_NAME") or "",
        "variant": osrel.get("VARIANT") or "",
        "id_like": osrel.get("ID_LIKE") or "",
        "paths": paths,
        "cwd": os.getcwd(),
        "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "",
    }
