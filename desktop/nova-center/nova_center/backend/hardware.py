"""Hardware inventory via Nova Platform API."""

from __future__ import annotations

from . import platform_bridge


def collect() -> dict:
    return platform_bridge.call("get-hardware")
