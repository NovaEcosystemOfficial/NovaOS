"""System identity collectors for platform.v1."""

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


def uptime_seconds() -> float | None:
    try:
        raw = Path("/proc/uptime").read_text(encoding="utf-8").split()[0]
        return float(raw)
    except OSError:
        return None


def human_uptime(seconds: float | None) -> str:
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


def get_hostname() -> dict:
    try:
        hostname = socket.gethostname()
    except OSError:
        hostname = (
            Path("/etc/hostname").read_text(encoding="utf-8").strip()
            if Path("/etc/hostname").is_file()
            else "unknown"
        )
    fqdn = hostname
    try:
        fqdn = socket.getfqdn()
    except OSError:
        pass
    return {"hostname": hostname, "fqdn": fqdn}


def get_version() -> dict:
    from nova_platform import API_VERSION, __version__

    osrel = read_os_release()
    return {
        "platform_version": __version__,
        "api": API_VERSION,
        "os_name": osrel.get("NAME") or "NovaOS",
        "os_version": osrel.get("VERSION") or osrel.get("VERSION_ID") or "",
        "os_version_id": osrel.get("VERSION_ID") or "",
        "pretty_name": osrel.get("PRETTY_NAME") or "NovaOS",
    }


def get_uptime() -> dict:
    up = uptime_seconds()
    return {
        "uptime_seconds": up,
        "uptime_human": human_uptime(up),
        "boot_time": (time.time() - up) if up is not None else None,
    }


def get_session() -> dict:
    return {
        "user": os.environ.get("USER") or os.environ.get("LOGNAME") or "",
        "uid": os.getuid() if hasattr(os, "getuid") else None,
        "xdg_session_type": os.environ.get("XDG_SESSION_TYPE"),
        "xdg_current_desktop": os.environ.get("XDG_CURRENT_DESKTOP"),
        "display": os.environ.get("DISPLAY"),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY"),
        "desktop_session": os.environ.get("DESKTOP_SESSION"),
        "logname": os.environ.get("LOGNAME"),
    }


def get_system_info() -> dict:
    osrel = read_os_release()
    host = get_hostname()
    up = get_uptime()
    paths = {
        "/etc/nova": Path("/etc/nova").is_dir(),
        "/etc/novaos": Path("/etc/novaos").is_dir(),
        "/usr/lib/nova": Path("/usr/lib/nova").is_dir(),
        "/var/lib/nova": Path("/var/lib/nova").is_dir(),
        "/usr/share/nova": Path("/usr/share/nova").is_dir(),
        "/var/log/nova": Path("/var/log/nova").is_dir(),
        "/run/nova": Path("/run/nova").is_dir(),
    }
    return {
        "version": osrel.get("VERSION") or osrel.get("VERSION_ID") or "",
        "version_id": osrel.get("VERSION_ID") or "",
        "pretty_name": osrel.get("PRETTY_NAME") or osrel.get("NAME") or "NovaOS",
        "name": osrel.get("NAME") or "NovaOS",
        "hostname": host["hostname"],
        "fqdn": host["fqdn"],
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "uptime": up["uptime_seconds"],
        "uptime_human": up["uptime_human"],
        "boot_time": up["boot_time"],
        "os_release": osrel,
        "variant": osrel.get("VARIANT") or "",
        "id_like": osrel.get("ID_LIKE") or "",
        "paths": paths,
        "session": get_session(),
    }
