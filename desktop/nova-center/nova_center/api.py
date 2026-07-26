"""Internal Nova Center API facade (center.v1).

Stable entry points for the GUI and future consumers (Ryuk skills, Shell).
Collectors always read live system data — no mock payloads.
"""

from __future__ import annotations

from typing import Any

from . import __version__
from .backend import dashboard, hardware, network, services, system_info, updates

API_VERSION = "center.v1"


def get_dashboard() -> dict[str, Any]:
    return {
        "api": API_VERSION,
        "center_version": __version__,
        **dashboard.collect(),
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


def check_updates() -> dict[str, Any]:
    return {"api": API_VERSION, **updates.check()}


def apply_updates() -> dict[str, Any]:
    return {"api": API_VERSION, **updates.apply()}


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
