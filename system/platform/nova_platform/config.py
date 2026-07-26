"""Configuration for nova-platformd."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _first_existing(*paths: Path) -> Path | None:
    for p in paths:
        if p.is_file():
            return p
    return None


@dataclass
class PlatformConfig:
    socket_path: Path = Path("/run/nova/platform.sock")
    log_dir: Path = Path("/var/log/nova")
    state_dir: Path = Path("/var/lib/nova/platform")
    monitor_interval_sec: int = 60

    @classmethod
    def load(cls, path: Path | None = None) -> PlatformConfig:
        cfg = cls()
        conf_path = path or _first_existing(
            Path(os.environ["NOVA_PLATFORM_CONF"])
            if os.environ.get("NOVA_PLATFORM_CONF")
            else Path("/nonexistent"),
            Path("/etc/nova/platform/nova-platform.conf"),
            Path(__file__).resolve().parents[1] / "conf" / "nova-platform.conf",
        )
        if conf_path is not None:
            section: str | None = None
            for raw in conf_path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    section = line[1:-1].strip().lower()
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip().strip('"').strip("'")
                if section in (None, "platform", "general"):
                    if key == "socket_path":
                        cfg.socket_path = Path(value)
                    elif key == "log_dir":
                        cfg.log_dir = Path(value)
                    elif key == "state_dir":
                        cfg.state_dir = Path(value)
                    elif key == "monitor_interval_sec":
                        try:
                            cfg.monitor_interval_sec = int(value)
                        except ValueError:
                            pass
        if os.environ.get("NOVA_PLATFORM_SOCKET"):
            cfg.socket_path = Path(os.environ["NOVA_PLATFORM_SOCKET"])
        if os.environ.get("NOVA_PLATFORM_LOG_DIR"):
            cfg.log_dir = Path(os.environ["NOVA_PLATFORM_LOG_DIR"])
        if os.environ.get("NOVA_PLATFORM_STATE_DIR"):
            cfg.state_dir = Path(os.environ["NOVA_PLATFORM_STATE_DIR"])
        return cfg
