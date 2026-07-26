"""Nova service status via Nova Platform monitor API."""

from __future__ import annotations

from . import platform_bridge


def collect() -> dict:
    return platform_bridge.call("get-services")
