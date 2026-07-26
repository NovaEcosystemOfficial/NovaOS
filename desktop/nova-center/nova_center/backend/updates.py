"""Bridge to Nova Update broker (system.update.v1) — live data only."""

from __future__ import annotations

import os
import sys
from pathlib import Path

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
except ImportError:  # pragma: no cover - host without broker libs
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
        sock = Path("/run/nova/update.sock")
        if sock.exists():
            base["service"] = "socket presente (client non disponibile)"
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
    except FileNotFoundError:
        base["error"] = "socket mancante"
        base["service"] = "non in esecuzione"
        return base
    except PermissionError:
        base["error"] = "permesso negato sul socket (serve gruppo 'nova'; riavvia la sessione)"
        base["service"] = "socket protetto"
        return base
    except (ConnectionRefusedError, OSError, RuntimeError) as exc:
        base["error"] = str(exc)
        base["service"] = "errore"
        return base


def check() -> dict:
    """Run broker Check and return pending payload."""
    client = _client()
    if client is None:
        raise RuntimeError("libreria nova_update assente")
    return client.call("Check")


def apply() -> dict:
    """Run broker Apply for pending packages."""
    client = _client()
    if client is None:
        raise RuntimeError("libreria nova_update assente")
    return client.call("Apply")
