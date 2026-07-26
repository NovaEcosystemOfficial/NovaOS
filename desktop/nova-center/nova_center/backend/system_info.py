"""System identity via Nova Platform API (no direct filesystem reads)."""

from __future__ import annotations

from . import platform_bridge


def collect() -> dict:
    info = platform_bridge.call("get-system-info")
    return {
        "version": info.get("version") or "",
        "version_id": info.get("version_id") or "",
        "pretty_name": info.get("pretty_name") or "NovaOS",
        "name": info.get("name") or "NovaOS",
        "hostname": info.get("hostname") or "",
        "kernel": info.get("kernel") or "",
        "architecture": info.get("architecture") or "",
        "uptime": info.get("uptime"),
        "uptime_human": info.get("uptime_human") or "",
        "boot_time": info.get("boot_time"),
    }


def collect_full() -> dict:
    return platform_bridge.call("get-system-info")
