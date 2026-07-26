"""Configuration for nova-updated."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _first_existing(*candidates: Path) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path
    return None


@dataclass
class UpdateConfig:
    channel: str = "stable"
    backend: str = "auto"  # auto | dnf | mock | localrpm
    check_interval_hours: int = 6
    signature_policy: str = "warn"  # warn | enforce | off
    socket_path: Path = field(default_factory=lambda: Path("/run/nova/update.sock"))
    state_dir: Path = field(default_factory=lambda: Path("/var/lib/nova/update"))
    repo_config_dir: Path = field(default_factory=lambda: Path("/etc/yum.repos.d"))
    keys_dir: Path = field(default_factory=lambda: Path("/etc/pki/novaos"))
    enabled_classes: tuple[str, ...] = ("os", "nova", "apps")
    # localrpm backend paths (e2e / offline repo)
    local_repo_root: Path | None = None
    local_install_root: Path | None = None

    @classmethod
    def load(cls, path: Path | None = None) -> UpdateConfig:
        cfg = cls()

        conf_path = path or _first_existing(
            Path(os.environ["NOVA_UPDATE_CONF"])
            if os.environ.get("NOVA_UPDATE_CONF")
            else Path("/nonexistent"),
            Path("/etc/nova/update/nova-update.conf"),
            Path(__file__).resolve().parents[1] / "conf" / "nova-update.conf",
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
                key, value = (p.strip() for p in line.split("=", 1))
                key = key.lower()
                if section not in (None, "update", "nova-update", "broker"):
                    continue
                if key == "channel":
                    cfg.channel = value.lower()
                elif key == "backend":
                    cfg.backend = value.lower()
                elif key == "check_interval_hours":
                    cfg.check_interval_hours = int(value)
                elif key == "signature_policy":
                    cfg.signature_policy = value.lower()
                elif key == "socket_path":
                    cfg.socket_path = Path(value)
                elif key == "state_dir":
                    cfg.state_dir = Path(value)
                elif key == "repo_config_dir":
                    cfg.repo_config_dir = Path(value)
                elif key == "keys_dir":
                    cfg.keys_dir = Path(value)
                elif key == "enabled_classes":
                    cfg.enabled_classes = tuple(
                        p.strip() for p in value.split(",") if p.strip()
                    )

        # Environment overrides win (dev / validation / containers).
        if os.environ.get("NOVA_UPDATE_SOCKET"):
            cfg.socket_path = Path(os.environ["NOVA_UPDATE_SOCKET"])
        if os.environ.get("NOVA_UPDATE_STATE_DIR"):
            cfg.state_dir = Path(os.environ["NOVA_UPDATE_STATE_DIR"])
        if os.environ.get("NOVA_UPDATE_BACKEND"):
            cfg.backend = os.environ["NOVA_UPDATE_BACKEND"]
        if os.environ.get("NOVA_UPDATE_CHANNEL"):
            cfg.channel = os.environ["NOVA_UPDATE_CHANNEL"]
        if os.environ.get("NOVA_UPDATE_SIGNATURE_POLICY"):
            cfg.signature_policy = os.environ["NOVA_UPDATE_SIGNATURE_POLICY"]
        if os.environ.get("NOVA_UPDATE_KEYS_DIR"):
            cfg.keys_dir = Path(os.environ["NOVA_UPDATE_KEYS_DIR"])
        if os.environ.get("NOVA_UPDATE_LOCAL_REPO"):
            cfg.local_repo_root = Path(os.environ["NOVA_UPDATE_LOCAL_REPO"])
        if os.environ.get("NOVA_UPDATE_INSTALL_ROOT"):
            cfg.local_install_root = Path(os.environ["NOVA_UPDATE_INSTALL_ROOT"])

        return cfg
