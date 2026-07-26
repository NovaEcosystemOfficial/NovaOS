"""Internal Nova Center API facade (center.v1).

Stable entry points for the GUI and future consumers (Ryuk skills, Shell).
Collectors always read live system data — no mock payloads.
"""

from __future__ import annotations

from typing import Any

from . import __version__
from .backend import hardware, network, services, system_info, updates

API_VERSION = "center.v1"


def get_dashboard() -> dict[str, Any]:
    sysinfo = system_info.collect()
    upd = updates.collect()
    return {
        "api": API_VERSION,
        "center_version": __version__,
        "novaos_version": sysinfo.get("version"),
        "pretty_name": sysinfo.get("pretty_name"),
        "uptime": sysinfo.get("uptime"),
        "uptime_human": sysinfo.get("uptime_human"),
        "hostname": sysinfo.get("hostname"),
        "kernel": sysinfo.get("kernel"),
        "architecture": sysinfo.get("architecture"),
        "update_service": upd.get("service"),
        "update_channel": upd.get("channel"),
        "last_check": upd.get("last_check"),
        "pending_count": upd.get("pending_count"),
    }


def get_hardware() -> dict[str, Any]:
    return {"api": API_VERSION, **hardware.collect()}


def get_network() -> dict[str, Any]:
    return {"api": API_VERSION, **network.collect()}


def get_system() -> dict[str, Any]:
    return {"api": API_VERSION, **system_info.collect_full()}


def get_services() -> dict[str, Any]:
    return {"api": API_VERSION, **services.collect()}


def get_updates() -> dict[str, Any]:
    return {"api": API_VERSION, **updates.collect()}


def snapshot() -> dict[str, Any]:
    """Full snapshot for debugging / future export."""
    return {
        "api": API_VERSION,
        "dashboard": get_dashboard(),
        "hardware": get_hardware(),
        "network": get_network(),
        "system": get_system(),
        "services": get_services(),
        "updates": get_updates(),
    }
