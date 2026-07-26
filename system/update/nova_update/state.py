"""Persistent broker state."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .protocol import PackageUpdate, Progress


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class BrokerState:
    channel: str = "stable"
    last_check: str | None = None
    pending: list[PackageUpdate] = field(default_factory=list)
    progress: Progress = field(default_factory=Progress)
    reboot_required: bool = False
    signatures_ok: bool | None = None
    history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "channel": self.channel,
            "last_check": self.last_check,
            "pending": [asdict(p) for p in self.pending],
            "progress": asdict(self.progress),
            "reboot_required": self.reboot_required,
            "signatures_ok": self.signatures_ok,
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: dict) -> BrokerState:
        pending = [PackageUpdate(**p) for p in data.get("pending", [])]
        progress = Progress(**data.get("progress", {}))
        return cls(
            channel=data.get("channel", "stable"),
            last_check=data.get("last_check"),
            pending=pending,
            progress=progress,
            reboot_required=bool(data.get("reboot_required", False)),
            signatures_ok=data.get("signatures_ok"),
            history=list(data.get("history") or []),
        )


class StateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.path = state_dir / "state.json"

    def load(self, default_channel: str = "stable") -> BrokerState:
        if not self.path.is_file():
            return BrokerState(channel=default_channel)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return BrokerState.from_dict(data)

    def save(self, state: BrokerState) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def touch_check(state: BrokerState) -> None:
        state.last_check = _utcnow()
