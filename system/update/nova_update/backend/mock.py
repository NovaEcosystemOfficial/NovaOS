"""Mock backend for development and offline validation."""

from __future__ import annotations

from ..protocol import PackageUpdate, Progress
from .base import UpdateBackend

_MOCK_BY_CHANNEL: dict[str, list[PackageUpdate]] = {
    "stable": [
        PackageUpdate(
            name="novaos-release",
            version="0.2.1",
            release="1.nova",
            update_class="os",
            summary="NovaOS release identity",
            size_bytes=12_000,
        ),
        PackageUpdate(
            name="novaos-update",
            version="0.1.1",
            release="1.nova",
            update_class="nova",
            summary="Nova Update Broker",
            size_bytes=85_000,
        ),
    ],
    "beta": [
        PackageUpdate(
            name="novaos-update",
            version="0.2.0",
            release="0.3.beta",
            update_class="nova",
            summary="Nova Update Broker (beta)",
            size_bytes=90_000,
        ),
        PackageUpdate(
            name="novadocs",
            version="0.1.0",
            release="0.2.beta",
            update_class="apps",
            summary="NovaDocs beta",
            size_bytes=4_200_000,
        ),
    ],
    "developer": [
        PackageUpdate(
            name="novaos-update",
            version="0.3.0",
            release="0.1.dev",
            update_class="nova",
            summary="Update broker development build",
            size_bytes=95_000,
        ),
    ],
    "nightly": [
        PackageUpdate(
            name="novaos-branding",
            version="0.0.20260726",
            release="1.nightly",
            update_class="nova",
            summary="Nightly branding snapshot",
            size_bytes=2_400_000,
        ),
        PackageUpdate(
            name="novaos-update",
            version="0.3.0",
            release="0.20260726.nightly",
            update_class="nova",
            summary="Nightly update broker",
            size_bytes=96_000,
        ),
    ],
}


class MockBackend(UpdateBackend):
    name = "mock"

    def __init__(self, **_kwargs) -> None:
        self._applied: list[str] = []

    def available(self) -> bool:
        return True

    def check(self, channel: str) -> list[PackageUpdate]:
        return list(_MOCK_BY_CHANNEL.get(channel, []))

    def apply(
        self,
        channel: str,
        packages: list[PackageUpdate],
        progress_cb=None,
    ) -> Progress:
        total = max(len(packages), 1)
        for idx, pkg in enumerate(packages, start=1):
            if progress_cb:
                progress_cb(
                    Progress(
                        phase="applying",
                        percent=int(idx * 100 / total),
                        message=f"mock apply {pkg.name}",
                    )
                )
            self._applied.append(pkg.nevra)
        return Progress(phase="done", percent=100, message=f"applied {len(packages)} packages")
