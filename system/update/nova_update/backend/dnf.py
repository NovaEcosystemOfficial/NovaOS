"""DNF backend for mutable NovaOS hosts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..channels import CHANNELS, normalize_channel
from ..protocol import PackageUpdate, Progress
from .base import UpdateBackend


def _which_dnf() -> str | None:
    for name in ("dnf5", "dnf"):
        path = shutil.which(name)
        if path:
            return path
    return None


class DnfBackend(UpdateBackend):
    name = "dnf"

    def __init__(
        self,
        repo_config_dir: Path | None = None,
        repo_templates_dir: Path | None = None,
        **_kwargs,
    ) -> None:
        self.dnf = _which_dnf()
        self.repo_config_dir = repo_config_dir or Path("/etc/yum.repos.d")
        # Templates shipped with the package / monorepo.
        self.repo_templates_dir = repo_templates_dir or (
            Path(__file__).resolve().parents[4] / "packages" / "repo" / "conf"
        )

    def available(self) -> bool:
        return self.dnf is not None

    def _run(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        if not self.dnf:
            raise RuntimeError("dnf/dnf5 not found")
        return subprocess.run(
            [self.dnf, *args],
            check=check,
            text=True,
            capture_output=True,
        )

    def check(self, channel: str) -> list[PackageUpdate]:
        channel = normalize_channel(channel)
        self.switch_channel(channel)
        # Refresh metadata for Nova repos only when possible.
        self._run(["makecache", "--refresh"], check=False)
        proc = self._run(
            ["check-update", "--quiet"],
            check=False,
        )
        # dnf check-update: 0 = none, 100 = updates available, others = error
        if proc.returncode not in (0, 100):
            raise RuntimeError(proc.stderr.strip() or "dnf check-update failed")
        updates: list[PackageUpdate] = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("Last metadata") or line.startswith("Security:"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name_arch = parts[0]
            version_full = parts[1]
            name, _, arch = name_arch.rpartition(".")
            if not name:
                name, arch = name_arch, "x86_64"
            ver, _, rel = version_full.rpartition("-")
            if not ver:
                ver, rel = version_full, "1"
            update_class = "nova" if name.startswith("nova") else "os"
            if name.startswith("nova") and not name.startswith("novaos-"):
                update_class = "apps"
            updates.append(
                PackageUpdate(
                    name=name,
                    version=ver,
                    release=rel,
                    arch=arch,
                    update_class=update_class,
                    summary=f"update from {CHANNELS[channel].repo_id}",
                )
            )
        return updates

    def apply(
        self,
        channel: str,
        packages: list[PackageUpdate],
        progress_cb=None,
    ) -> Progress:
        channel = normalize_channel(channel)
        self.switch_channel(channel)
        if progress_cb:
            progress_cb(Progress(phase="applying", percent=5, message="dnf upgrade"))
        names = [p.name for p in packages] if packages else []
        args = ["upgrade", "-y"]
        if names:
            args.extend(names)
        proc = self._run(args, check=False)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or "dnf upgrade failed")
        if progress_cb:
            progress_cb(Progress(phase="done", percent=100, message="dnf upgrade complete"))
        return Progress(phase="done", percent=100, message="dnf upgrade complete")

    def switch_channel(self, channel: str) -> None:
        channel = normalize_channel(channel)
        active = CHANNELS[channel].repo_id
        # Enable only the matching novaos-*.repo if present.
        if not self.repo_config_dir.is_dir():
            return
        for repo_file in self.repo_config_dir.glob("novaos-*.repo"):
            text = repo_file.read_text(encoding="utf-8")
            # Prefer matching by filename novaos-<channel>.repo
            enabled = repo_file.name == f"{active}.repo"
            new_lines: list[str] = []
            for line in text.splitlines():
                if line.strip().lower().startswith("enabled="):
                    new_lines.append(f"enabled={'1' if enabled else '0'}")
                else:
                    new_lines.append(line)
            repo_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
