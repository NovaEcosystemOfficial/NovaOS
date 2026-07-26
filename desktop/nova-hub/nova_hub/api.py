"""Internal Nova Hub API facade (hub.v1)."""

from __future__ import annotations

from typing import Any

from . import __version__
from .backend import ecosystem, news, platform_bridge, updates

API_VERSION = "hub.v1"


def _platform_status() -> dict[str, Any]:
    try:
        ping = platform_bridge.call("ping")
        health = platform_bridge.call("health")
        return {
            "ok": True,
            "label": "attivo",
            "ping": ping,
            "health": health,
        }
    except platform_bridge.PlatformUnavailable as exc:
        return {"ok": False, "label": "non attivo", "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "label": "errore", "error": str(exc)}


def get_home() -> dict[str, Any]:
    """Aggregate payload for the Hub home screen."""
    platform = _platform_status()
    dash: dict[str, Any] = {}
    network: dict[str, Any] = {}
    services: dict[str, Any] = {}
    errors: list[str] = []

    if platform["ok"]:
        try:
            dash = platform_bridge.call("get-dashboard")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"dashboard: {exc}")
        try:
            network = platform_bridge.call("get-network")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"network: {exc}")
        try:
            services = platform_bridge.call("get-services")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"services: {exc}")
    else:
        errors.append(platform.get("error") or "Nova Platform non attivo")

    upd = updates.collect()
    if upd.get("error"):
        errors.append(f"update: {upd['error']}")

    mem = dash.get("memory") or {}
    disk = dash.get("disk_root") or {}
    net_ifaces = network.get("interfaces") or network.get("devices") or []
    net_label = "—"
    if isinstance(net_ifaces, list) and net_ifaces:
        up = [
            i
            for i in net_ifaces
            if isinstance(i, dict)
            and (i.get("operstate") == "up" or i.get("connected") or i.get("state") == "up")
        ]
        net_label = f"{len(up)} attive / {len(net_ifaces)}" if up else f"0/{len(net_ifaces)} attive"
    elif network.get("primary"):
        net_label = str(network.get("primary"))

    svc_list = services.get("services") or services.get("items") or []
    if not isinstance(svc_list, list):
        svc_list = []

    notifications: list[dict] = []
    pending = int(upd.get("pending_count") or dash.get("pending_count") or 0)
    if pending:
        notifications.append(
            {
                "level": "info",
                "text": f"{pending} aggiornamenti disponibili",
            }
        )
    if not platform["ok"]:
        notifications.append({"level": "critical", "text": "Nova Platform non attivo"})
    if upd.get("service") not in (None, "attivo") and upd.get("error"):
        notifications.append({"level": "warn", "text": f"Nova Update: {upd.get('service')}"})

    return {
        "api": API_VERSION,
        "hub_version": __version__,
        "welcome": f"Benvenuto in NovaOS",
        "novaos_version": dash.get("novaos_version") or "—",
        "pretty_name": dash.get("pretty_name") or "NovaOS",
        "hostname": dash.get("hostname"),
        "uptime_human": dash.get("uptime_human") or "—",
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
        "network_label": net_label,
        "network": network,
        "platform": platform,
        "update": {
            "service": upd.get("service"),
            "channel": upd.get("channel") or dash.get("update_channel"),
            "pending_count": pending,
            "pending": upd.get("pending") or [],
            "last_check": upd.get("last_check") or dash.get("last_check"),
            "error": upd.get("error"),
        },
        "health": dash.get("health") or {},
        "services": svc_list,
        "errors": errors,
        "notifications": notifications,
        "ecosystem": ecosystem.catalog(),
        "news": news.load_news(),
    }


def check_updates() -> dict[str, Any]:
    return {"api": API_VERSION, **updates.check()}


def apply_updates() -> dict[str, Any]:
    return {"api": API_VERSION, **updates.apply()}


def snapshot() -> dict[str, Any]:
    return {"api": API_VERSION, "home": get_home()}
