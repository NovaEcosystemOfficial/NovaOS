"""Release channels for Nova Update."""

from __future__ import annotations

from dataclasses import dataclass

# Historical alias from early platform docs (stable/beta/dev).
_ALIASES = {
    "dev": "developer",
}


@dataclass(frozen=True)
class Channel:
    id: str
    label: str
    description: str
    repo_id: str


CHANNELS: dict[str, Channel] = {
    "stable": Channel(
        id="stable",
        label="Stable",
        description="Release verificate per utenti finali",
        repo_id="novaos-stable",
    ),
    "beta": Channel(
        id="beta",
        label="Beta",
        description="Pre-release per early adopter",
        repo_id="novaos-beta",
    ),
    "developer": Channel(
        id="developer",
        label="Developer",
        description="Canale sviluppatori interni",
        repo_id="novaos-developer",
    ),
    "nightly": Channel(
        id="nightly",
        label="Nightly",
        description="Build giornaliere / CI",
        repo_id="novaos-nightly",
    ),
}

DEFAULT_CHANNEL = "stable"


def normalize_channel(name: str) -> str:
    key = (name or "").strip().lower()
    key = _ALIASES.get(key, key)
    if key not in CHANNELS:
        allowed = ", ".join(CHANNELS)
        raise ValueError(f"unknown channel '{name}'; expected one of: {allowed}")
    return key


def list_channels() -> list[Channel]:
    return list(CHANNELS.values())
