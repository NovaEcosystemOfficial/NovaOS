"""JSON protocol for system.update.v1 over a Unix socket."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

API = "system.update.v1"


@dataclass
class PackageUpdate:
    name: str
    epoch: str = "0"
    version: str = ""
    release: str = ""
    arch: str = "x86_64"
    update_class: str = "nova"  # os | nova | apps
    summary: str = ""
    size_bytes: int = 0

    @property
    def nevra(self) -> str:
        e = f"{self.epoch}:" if self.epoch not in ("", "0") else ""
        return f"{self.name}-{e}{self.version}-{self.release}.{self.arch}"


@dataclass
class Progress:
    phase: str = "idle"  # idle | checking | applying | done | error
    percent: int = 0
    message: str = ""


@dataclass
class Status:
    api: str = API
    channel: str = "stable"
    backend: str = "mock"
    progress: Progress = field(default_factory=Progress)
    last_check: str | None = None
    pending: list[PackageUpdate] = field(default_factory=list)
    signature_policy: str = "warn"
    signatures_ok: bool | None = None
    reboot_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "api": self.api,
            "channel": self.channel,
            "backend": self.backend,
            "progress": asdict(self.progress),
            "last_check": self.last_check,
            "pending": [asdict(p) for p in self.pending],
            "signature_policy": self.signature_policy,
            "signatures_ok": self.signatures_ok,
            "reboot_required": self.reboot_required,
        }


def encode(obj: dict[str, Any]) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def decode_line(line: bytes | str) -> dict[str, Any]:
    if isinstance(line, bytes):
        line = line.decode("utf-8")
    data = json.loads(line)
    if not isinstance(data, dict):
        raise ValueError("protocol message must be a JSON object")
    return data


def request(method: str, params: dict[str, Any] | None = None, req_id: int = 1) -> dict[str, Any]:
    return {"api": API, "id": req_id, "method": method, "params": params or {}}


def response(req_id: Any, result: Any = None, error: str | None = None) -> dict[str, Any]:
    msg: dict[str, Any] = {"api": API, "id": req_id}
    if error:
        msg["error"] = error
    else:
        msg["result"] = result
    return msg
