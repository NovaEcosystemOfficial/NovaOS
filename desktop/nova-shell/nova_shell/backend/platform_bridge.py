"""Platform bridge for Nova Shell — only platform.v1, no /proc reads."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PLATFORM_CANDIDATES = (
    Path("/usr/lib/nova/platform"),
    Path(__file__).resolve().parents[4] / "system" / "platform",
)
for _root in _PLATFORM_CANDIDATES:
    if (_root / "nova_platform").is_dir() and str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
        break

try:
    from nova_platform.client import PlatformClient
    from nova_platform.config import PlatformConfig
except ImportError:  # pragma: no cover
    PlatformClient = None  # type: ignore
    PlatformConfig = None  # type: ignore


class PlatformUnavailable(RuntimeError):
    """platform.sock missing or daemon not reachable."""


def client() -> "PlatformClient":
    if PlatformClient is None or PlatformConfig is None:
        raise PlatformUnavailable(
            "libreria nova_platform assente — installare nova-platform via Nova Update"
        )
    cfg = PlatformConfig.load()
    sock = Path(os.environ.get("NOVA_PLATFORM_SOCKET", cfg.socket_path))
    return PlatformClient(sock)


def call(method: str, params: dict | None = None) -> dict:
    try:
        return client().call(method, params)
    except FileNotFoundError as exc:
        raise PlatformUnavailable(
            "Nova Platform non attivo — "
            "sudo systemctl enable --now nova-platformd.socket"
        ) from exc
    except (ConnectionError, ConnectionRefusedError) as exc:
        raise PlatformUnavailable("Nova Platform non raggiungibile") from exc
    except OSError as exc:
        if getattr(exc, "errno", None) == 2:
            raise PlatformUnavailable("Nova Platform socket assente") from exc
        raise
