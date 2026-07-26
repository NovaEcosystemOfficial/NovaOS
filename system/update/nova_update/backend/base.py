"""Backend interface for Nova Update Broker."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..protocol import PackageUpdate, Progress


class UpdateBackend(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def check(self, channel: str) -> list[PackageUpdate]:
        raise NotImplementedError

    @abstractmethod
    def apply(
        self,
        channel: str,
        packages: list[PackageUpdate],
        progress_cb=None,
    ) -> Progress:
        raise NotImplementedError

    def switch_channel(self, channel: str) -> None:
        """Optional: rewrite repo enablement for the active channel."""
        return None
