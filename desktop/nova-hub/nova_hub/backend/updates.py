"""Nova Update broker bridge — prefers nova_center.updates when present."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _try_center() -> bool:
    candidates = (
        Path("/usr/share/nova/center"),
        Path(__file__).resolve().parents[3] / "nova-center",
    )
    for root in candidates:
        if not (root / "nova_center" / "backend" / "updates.py").is_file():
            continue
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        try:
            from nova_center.backend import updates as _upd  # type: ignore

            globals()["collect"] = _upd.collect
            globals()["check"] = _upd.check
            globals()["apply"] = _upd.apply
            return True
        except ImportError:
            continue
    return False


if not _try_center():
    _UPDATE_CANDIDATES = (
        Path("/usr/lib/nova/update"),
        Path(__file__).resolve().parents[4] / "system" / "update",
    )
    for _root in _UPDATE_CANDIDATES:
        if (_root / "nova_update").is_dir() and str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
            break

    try:
        from nova_update.client import UpdateClient
        from nova_update.config import UpdateConfig
    except ImportError:  # pragma: no cover
        UpdateClient = None  # type: ignore
        UpdateConfig = None  # type: ignore

    def _client():
        if UpdateClient is None or UpdateConfig is None:
            return None
        cfg = UpdateConfig.load()
        sock = Path(os.environ.get("NOVA_UPDATE_SOCKET", cfg.socket_path))
        return UpdateClient(sock)

    def collect() -> dict:
        base = {
            "available": False,
            "service": "non raggiungibile",
            "channel": None,
            "last_check": None,
            "pending": [],
            "pending_count": 0,
            "backend": None,
            "error": None,
            "open_command": ["nova-update-gui"],
        }
        client = _client()
        if client is None:
            base["error"] = "libreria nova_update assente"
            return base
        try:
            status = client.call("GetStatus")
            channel = client.call("GetChannel")
            pending = status.get("pending") or []
            base.update(
                {
                    "available": True,
                    "service": "attivo",
                    "channel": channel.get("channel") or status.get("channel"),
                    "channels": channel.get("channels") or [],
                    "last_check": status.get("last_check"),
                    "pending": pending,
                    "pending_count": len(pending),
                    "backend": status.get("backend"),
                    "progress": status.get("progress"),
                }
            )
            return base
        except Exception as exc:  # noqa: BLE001
            base["error"] = str(exc)
            base["service"] = "errore"
            return base

    def check() -> dict:
        client = _client()
        if client is None:
            raise RuntimeError("libreria nova_update assente")
        return client.call("Check")

    def apply() -> dict:
        client = _client()
        if client is None:
            raise RuntimeError("libreria nova_update assente")
        return client.call("Apply")
