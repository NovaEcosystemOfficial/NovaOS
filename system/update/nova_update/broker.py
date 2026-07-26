"""Update Broker implementing system.update.v1."""

from __future__ import annotations

import logging
from dataclasses import asdict

from .backend import create_backend
from .channels import list_channels, normalize_channel
from .config import UpdateConfig
from .protocol import Progress, Status, response
from .signatures import verify_updates
from .state import StateStore, _utcnow

log = logging.getLogger("nova-updated")


def _read_os_release() -> dict[str, str]:
    from pathlib import Path

    data: dict[str, str] = {}
    for path in (Path("/etc/os-release"), Path("/usr/lib/os-release")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            data[key] = value.strip().strip('"')
        break
    return data


def _service_active() -> str:
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("systemctl"):
        try:
            proc = subprocess.run(
                ["systemctl", "is-active", "nova-updated.service"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return (proc.stdout or "").strip() or "unknown"
        except Exception:
            pass
    sock = Path("/run/nova/update.sock")
    return "active" if sock.exists() else "inactive"


class UpdateBroker:
    def __init__(self, config: UpdateConfig) -> None:
        self.config = config
        self.store = StateStore(config.state_dir)
        self.state = self.store.load(default_channel=config.channel)
        try:
            self.state.channel = normalize_channel(self.state.channel)
        except ValueError:
            self.state.channel = normalize_channel(config.channel)
        self.backend = create_backend(
            config.backend,
            repo_config_dir=config.repo_config_dir,
            keys_dir=config.keys_dir,
            repo_root=config.local_repo_root,
            install_root=config.local_install_root,
        )

    def status(self) -> Status:
        return Status(
            channel=self.state.channel,
            backend=self.backend.name,
            progress=self.state.progress,
            last_check=self.state.last_check,
            pending=list(self.state.pending),
            signature_policy=self.config.signature_policy,
            signatures_ok=self.state.signatures_ok,
            reboot_required=self.state.reboot_required,
        )

    def get_channel(self) -> dict:
        return {
            "channel": self.state.channel,
            "channels": [
                {"id": c.id, "label": c.label, "description": c.description}
                for c in list_channels()
            ],
        }

    def set_channel(self, channel: str) -> dict:
        channel = normalize_channel(channel)
        self.state.channel = channel
        self.state.pending = []
        self.backend.switch_channel(channel)
        self.store.save(self.state)
        return self.get_channel()

    def check(self) -> dict:
        self.state.progress = Progress(phase="checking", percent=0, message="checking updates")
        self.store.save(self.state)
        try:
            pending = self.backend.check(self.state.channel)
            report = verify_updates(
                [p.name for p in pending],
                keys_dir=self.config.keys_dir,
                policy=self.config.signature_policy,
            )
            self.state.pending = pending
            self.state.signatures_ok = report.ok
            StateStore.touch_check(self.state)
            self.state.progress = Progress(
                phase="idle",
                percent=100,
                message=f"{len(pending)} updates available",
            )
            self.store.save(self.state)
            return {
                "pending": [asdict(p) for p in pending],
                "signatures": asdict(report),
                "last_check": self.state.last_check,
            }
        except Exception as exc:
            self.state.progress = Progress(phase="error", percent=0, message=str(exc))
            self.store.save(self.state)
            raise

    def apply(self) -> dict:
        if self.config.signature_policy == "enforce":
            report = verify_updates(
                [p.name for p in self.state.pending],
                keys_dir=self.config.keys_dir,
                policy="enforce",
            )
            if not report.ok:
                raise RuntimeError(report.message)

        packages = list(self.state.pending)
        if not packages:
            # Re-check if nothing cached.
            self.check()
            packages = list(self.state.pending)
        if not packages:
            return {"applied": [], "message": "no updates available"}

        def on_progress(prog: Progress) -> None:
            self.state.progress = prog
            self.store.save(self.state)

        self.state.progress = Progress(phase="applying", percent=0, message="applying updates")
        self.store.save(self.state)
        try:
            final = self.backend.apply(self.state.channel, packages, progress_cb=on_progress)
            self.state.pending = []
            self.state.progress = final
            self.state.reboot_required = any(p.update_class == "os" for p in packages)
            entry = {
                "timestamp": _utcnow(),
                "channel": self.state.channel,
                "packages": [asdict(p) for p in packages],
                "backend": self.backend.name,
            }
            self.state.history = [entry, *self.state.history][:50]
            self.store.save(self.state)
            return {
                "applied": [asdict(p) for p in packages],
                "reboot_required": self.state.reboot_required,
                "progress": asdict(final),
                "history_entry": entry,
            }
        except Exception as exc:
            self.state.progress = Progress(phase="error", percent=0, message=str(exc))
            self.store.save(self.state)
            raise

    def get_progress(self) -> dict:
        return asdict(self.state.progress)

    def get_history(self) -> dict:
        return {"history": list(self.state.history)}

    def get_system_info(self) -> dict:
        osrel = _read_os_release()
        return {
            "os_release": osrel,
            "pretty_name": osrel.get("PRETTY_NAME") or osrel.get("NAME", "NovaOS"),
            "version": osrel.get("VERSION") or osrel.get("VERSION_ID", ""),
            "service": _service_active(),
            "channel": self.state.channel,
            "backend": self.backend.name,
        }

    def verify_signatures(self) -> dict:
        report = verify_updates(
            [p.name for p in self.state.pending],
            keys_dir=self.config.keys_dir,
            policy=self.config.signature_policy,
        )
        self.state.signatures_ok = report.ok
        self.store.save(self.state)
        return asdict(report)

    def dispatch(self, message: dict) -> dict:
        req_id = message.get("id")
        method = (message.get("method") or "").strip()
        params = message.get("params") or {}
        try:
            if method in ("GetStatus", "Status", "status"):
                result = self.status().to_dict()
            elif method in ("GetChannel", "get_channel"):
                result = self.get_channel()
            elif method in ("SetChannel", "set_channel"):
                result = self.set_channel(params.get("channel", ""))
            elif method in ("Check", "check"):
                result = self.check()
            elif method in ("Apply", "apply"):
                result = self.apply()
            elif method in ("GetProgress", "get_progress"):
                result = self.get_progress()
            elif method in ("GetHistory", "get_history"):
                result = self.get_history()
            elif method in ("GetSystemInfo", "get_system_info"):
                result = self.get_system_info()
            elif method in ("VerifySignatures", "verify_signatures"):
                result = self.verify_signatures()
            elif method in ("Ping", "ping"):
                result = {"pong": True, "backend": self.backend.name}
            else:
                return response(req_id, error=f"unknown method '{method}'")
            return response(req_id, result=result)
        except Exception as exc:
            log.exception("method %s failed", method)
            return response(req_id, error=str(exc))
