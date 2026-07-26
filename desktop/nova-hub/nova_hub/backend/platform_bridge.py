"""Shared Platform bridge — prefers nova_center copy when installed."""

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
        if not (root / "nova_center" / "backend" / "platform_bridge.py").is_file():
            continue
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        try:
            from nova_center.backend import platform_bridge as _pb  # type: ignore

            globals()["PlatformUnavailable"] = _pb.PlatformUnavailable
            globals()["call"] = _pb.call
            globals()["client"] = _pb.client
            return True
        except ImportError:
            continue
    return False


if not _try_center():
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

    def client():
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
                "Nova Platform non attivo (socket assente). "
                "sudo systemctl enable --now nova-platformd.socket"
            ) from exc
        except (ConnectionError, ConnectionRefusedError) as exc:
            raise PlatformUnavailable(
                "Nova Platform non raggiungibile — "
                "sudo systemctl enable --now nova-platformd.socket"
            ) from exc
        except OSError as exc:
            if getattr(exc, "errno", None) == 2:
                raise PlatformUnavailable(
                    "Nova Platform non attivo (socket assente). "
                    "sudo systemctl enable --now nova-platformd.socket"
                ) from exc
            raise
