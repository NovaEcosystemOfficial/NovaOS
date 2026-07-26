"""Method dispatch for platform.v1."""

from __future__ import annotations

from typing import Any

from nova_platform import API_VERSION, __version__
from nova_platform.collectors import dashboard, hardware, network, system
from nova_platform.logging_setup import get_logger
from nova_platform.monitor import collect_services, health
from nova_platform.protocol import response

log = get_logger("platform")

# Normalize kebab-case and PascalCase / aliases to a canonical key.
_ALIASES = {
    "ping": "ping",
    "Ping": "ping",
    "get-version": "get-version",
    "GetVersion": "get-version",
    "get_version": "get-version",
    "get-hostname": "get-hostname",
    "GetHostname": "get-hostname",
    "get_hostname": "get-hostname",
    "get-uptime": "get-uptime",
    "GetUptime": "get-uptime",
    "get_uptime": "get-uptime",
    "get-session": "get-session",
    "GetSession": "get-session",
    "get_session": "get-session",
    "get-network": "get-network",
    "GetNetwork": "get-network",
    "get_network": "get-network",
    "get-system-info": "get-system-info",
    "GetSystemInfo": "get-system-info",
    "get_system_info": "get-system-info",
    "get-hardware": "get-hardware",
    "GetHardware": "get-hardware",
    "get_hardware": "get-hardware",
    "get-dashboard": "get-dashboard",
    "GetDashboard": "get-dashboard",
    "get_dashboard": "get-dashboard",
    "get-services": "get-services",
    "GetServices": "get-services",
    "get_services": "get-services",
    "health": "health",
    "Health": "health",
    "GetHealth": "health",
}


class PlatformService:
    def dispatch(self, message: dict[str, Any]) -> dict[str, Any]:
        req_id = message.get("id", 0)
        method = message.get("method") or ""
        canonical = _ALIASES.get(method) or _ALIASES.get(str(method).replace("_", "-"))
        if not canonical:
            log.warning("unknown method: %s", method)
            return response(req_id, error=f"unknown method: {method}")
        try:
            result = self._invoke(canonical, message.get("params") or {})
            log.debug("ok method=%s", canonical)
            return response(req_id, result=result)
        except Exception as exc:
            log.exception("handler error method=%s", canonical)
            return response(req_id, error=str(exc))

    def _invoke(self, method: str, params: dict[str, Any]) -> Any:
        if method == "ping":
            return {"pong": True, "api": API_VERSION, "version": __version__}
        if method == "get-version":
            return system.get_version()
        if method == "get-hostname":
            return system.get_hostname()
        if method == "get-uptime":
            return system.get_uptime()
        if method == "get-session":
            return system.get_session()
        if method == "get-network":
            return network.collect()
        if method == "get-system-info":
            return system.get_system_info()
        if method == "get-hardware":
            return hardware.collect()
        if method == "get-dashboard":
            return dashboard.collect()
        if method == "get-services":
            return collect_services()
        if method == "health":
            return health()
        raise ValueError(f"unhandled method {method}")
