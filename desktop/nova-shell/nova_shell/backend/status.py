"""Live shell status — all metrics via Nova Platform API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from . import platform_bridge


def _net_label(network: dict) -> str:
    devices = network.get("devices") or network.get("interfaces") or []
    if not isinstance(devices, list) or not devices:
        return "—"
    up = []
    for d in devices:
        if not isinstance(d, dict):
            continue
        state = str(d.get("state") or d.get("operstate") or "").lower()
        if "connect" in state or state == "up":
            name = d.get("connection") or d.get("device") or d.get("ifname") or "net"
            up.append(str(name))
    if up:
        return up[0] if len(up) == 1 else f"{len(up)} up"
    return "offline"


def _ryuk_status(services: dict) -> dict[str, Any]:
    items = services.get("services") or services.get("items") or []
    if isinstance(items, list):
        for s in items:
            if isinstance(s, dict) and s.get("id") in ("nova-ryuk", "ryuk"):
                state = str(s.get("state") or s.get("status") or "planned")
                return {
                    "label": "Ryuk",
                    "state": state,
                    "ok": state in ("active", "active (socket)", "installed"),
                    "planned": state == "planned" or bool(s.get("planned")),
                }
    return {"label": "Ryuk", "state": "planned", "ok": False, "planned": True}


def _volume_from_platform(dash: dict, hardware: dict) -> dict[str, Any]:
    """Volume when Platform exposes it; otherwise unavailable (no local mixer reads)."""
    for src in (dash, hardware):
        audio = src.get("audio") or src.get("volume")
        if isinstance(audio, dict) and (
            audio.get("percent") is not None or audio.get("level") is not None
        ):
            pct = audio.get("percent", audio.get("level"))
            return {
                "available": True,
                "percent": pct,
                "muted": bool(audio.get("muted")),
                "label": f"{pct}%" if pct is not None else "—",
            }
    return {"available": False, "percent": None, "muted": False, "label": "n/d"}


def collect() -> dict[str, Any]:
    now = datetime.now()
    platform_ok = True
    platform_error = None
    dash: dict[str, Any] = {}
    network: dict[str, Any] = {}
    hardware: dict[str, Any] = {}
    services: dict[str, Any] = {}

    try:
        dash = platform_bridge.call("get-dashboard")
        network = platform_bridge.call("get-network")
        hardware = platform_bridge.call("get-hardware")
        services = platform_bridge.call("get-services")
    except platform_bridge.PlatformUnavailable as exc:
        platform_ok = False
        platform_error = str(exc)
    except Exception as exc:  # noqa: BLE001
        platform_ok = False
        platform_error = str(exc)

    mem = dash.get("memory") or (hardware.get("memory") if hardware else {}) or {}
    disk = dash.get("disk_root") or {}
    bat = dash.get("battery") or (hardware.get("battery") if hardware else {}) or {}
    pending = int(dash.get("pending_count") or 0)

    return {
        "clock": {
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%a %d %b"),
            "iso": now.isoformat(timespec="seconds"),
        },
        "platform_ok": platform_ok,
        "platform_error": platform_error,
        "battery": {
            "present": bool(bat.get("present")),
            "percent": bat.get("capacity_percent"),
            "status": bat.get("status"),
            "label": (
                f"{bat.get('capacity_percent')}%"
                if bat.get("present") and bat.get("capacity_percent") is not None
                else ("AC" if not bat.get("present") else "—")
            ),
        },
        "network": {"label": _net_label(network), "raw": network},
        "volume": _volume_from_platform(dash, hardware),
        "updates": {
            "pending_count": pending,
            "service": dash.get("update_service"),
            "channel": dash.get("update_channel"),
            "label": f"{pending} upd" if pending else "OK",
        },
        "ryuk": _ryuk_status(services),
        "widgets": {
            "cpu_percent": dash.get("cpu_percent"),
            "memory_percent": mem.get("percent_used"),
            "memory_human": (
                f"{mem.get('used_human') or '—'} / {mem.get('total_human') or '—'}"
                if mem
                else "—"
            ),
            "disk_percent": disk.get("percent"),
            "disk_human": (
                f"{disk.get('used_human') or '—'} / {disk.get('size_human') or '—'}"
                if disk
                else "—"
            ),
            "network_label": _net_label(network),
            "updates_label": f"{pending} pending" if pending else "aggiornato",
            "pending_count": pending,
        },
        "novaos_version": dash.get("novaos_version"),
        "hostname": dash.get("hostname"),
    }
