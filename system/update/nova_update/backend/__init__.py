"""Update backends (DNF today, ostree tomorrow)."""

from __future__ import annotations

from .base import UpdateBackend
from .dnf import DnfBackend
from .localrpm import LocalRpmBackend
from .mock import MockBackend


def create_backend(name: str, **kwargs) -> UpdateBackend:
    key = (name or "auto").lower()
    if key == "mock":
        return MockBackend(**kwargs)
    if key == "dnf":
        return DnfBackend(**kwargs)
    if key in ("localrpm", "local"):
        return LocalRpmBackend(**kwargs)
    if key == "auto":
        dnf = DnfBackend(**kwargs)
        if dnf.available():
            return dnf
        return MockBackend(**kwargs)
    raise ValueError(f"unknown backend '{name}'")
