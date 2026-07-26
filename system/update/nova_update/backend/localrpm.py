"""Local RPM repository backend for Nova Update e2e tests.

Scans a channel directory for ``*.rpm``, compares against an installed
package DB (JSON) under the test install root, and applies updates with
``rpm2cpio | cpio`` (works without ``rpm --root`` / privileges).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from ..channels import normalize_channel
from ..protocol import PackageUpdate, Progress
from .base import UpdateBackend


def _rpm_query(rpm_path: Path, fmt: str) -> str:
    proc = subprocess.run(
        ["rpm", "-qp", "--queryformat", fmt, str(rpm_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return proc.stdout.strip()


def _evr_tuple(version: str, release: str) -> tuple:
    """Best-effort comparable EVR (good enough for test packages)."""
    return (version, release)


class LocalRpmBackend(UpdateBackend):
    name = "localrpm"

    def __init__(
        self,
        repo_root: Path | None = None,
        install_root: Path | None = None,
        **_kwargs,
    ) -> None:
        self.repo_root = Path(
            repo_root
            or Path(__file__).resolve().parents[4]
            / "build"
            / "work"
            / "update-test"
            / "repo"
            / "channels"
        )
        self.install_root = Path(
            install_root
            or Path(__file__).resolve().parents[4]
            / "build"
            / "work"
            / "update-test"
            / "rootfs"
        )
        self.db_path = self.install_root / "var" / "lib" / "nova-update" / "installed.json"

    def available(self) -> bool:
        return shutil.which("rpm") is not None and shutil.which("rpm2cpio") is not None

    def _load_installed(self) -> dict[str, dict]:
        if not self.db_path.is_file():
            return {}
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _save_installed(self, data: dict[str, dict]) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _channel_dir(self, channel: str) -> Path:
        channel = normalize_channel(channel)
        return self.repo_root / channel

    def _list_repo_rpms(self, channel: str) -> list[Path]:
        base = self._channel_dir(channel)
        if not base.is_dir():
            return []
        return sorted(base.rglob("*.rpm"))

    def _pkg_from_rpm(self, rpm_path: Path) -> PackageUpdate:
        name = _rpm_query(rpm_path, "%{NAME}")
        version = _rpm_query(rpm_path, "%{VERSION}")
        release = _rpm_query(rpm_path, "%{RELEASE}")
        arch = _rpm_query(rpm_path, "%{ARCH}")
        summary = _rpm_query(rpm_path, "%{SUMMARY}")
        size_s = _rpm_query(rpm_path, "%{SIZE}")
        update_class = "nova"
        if name.startswith("nova") and not name.startswith("novaos-") and name != "hello-nova-update":
            update_class = "apps"
        if name in ("novaos-release",) or name.endswith("-kernel"):
            update_class = "os"
        if name == "hello-nova-update":
            update_class = "nova"
        return PackageUpdate(
            name=name,
            version=version,
            release=release,
            arch=arch,
            update_class=update_class,
            summary=summary,
            size_bytes=int(size_s) if size_s.isdigit() else rpm_path.stat().st_size,
        )

    def check(self, channel: str) -> list[PackageUpdate]:
        installed = self._load_installed()
        # Newest NEVRA per name in repo
        newest: dict[str, tuple[tuple, PackageUpdate, Path]] = {}
        for rpm in self._list_repo_rpms(channel):
            pkg = self._pkg_from_rpm(rpm)
            key = _evr_tuple(pkg.version, pkg.release)
            cur = newest.get(pkg.name)
            if cur is None or key > cur[0]:
                newest[pkg.name] = (key, pkg, rpm)

        updates: list[PackageUpdate] = []
        for name, (evr, pkg, _rpm) in sorted(newest.items()):
            have = installed.get(name)
            if have is None:
                updates.append(pkg)
                continue
            if evr > _evr_tuple(have.get("version", ""), have.get("release", "")):
                updates.append(pkg)
        return updates

    def apply(
        self,
        channel: str,
        packages: list[PackageUpdate],
        progress_cb=None,
    ) -> Progress:
        installed = self._load_installed()
        # Map name -> newest rpm path
        newest_rpm: dict[str, Path] = {}
        newest_pkg: dict[str, PackageUpdate] = {}
        for rpm in self._list_repo_rpms(channel):
            pkg = self._pkg_from_rpm(rpm)
            prev = newest_pkg.get(pkg.name)
            if prev is None or _evr_tuple(pkg.version, pkg.release) > _evr_tuple(
                prev.version, prev.release
            ):
                newest_rpm[pkg.name] = rpm
                newest_pkg[pkg.name] = pkg

        targets = packages or list(newest_pkg.values())
        total = max(len(targets), 1)
        self.install_root.mkdir(parents=True, exist_ok=True)

        for idx, pkg in enumerate(targets, start=1):
            rpm_path = newest_rpm.get(pkg.name)
            if rpm_path is None:
                raise RuntimeError(f"package {pkg.name} not found in local repo")
            if progress_cb:
                progress_cb(
                    Progress(
                        phase="applying",
                        percent=int(idx * 100 / total),
                        message=f"install {rpm_path.name}",
                    )
                )
            self._extract_rpm(rpm_path)
            if str(self.install_root) in ("/", "/.") or self.install_root.resolve() == Path("/"):
                self._repair_usrmerge()
            installed[pkg.name] = {
                "version": pkg.version,
                "release": pkg.release,
                "arch": pkg.arch,
                "nevra": pkg.nevra,
                "rpm": rpm_path.name,
            }

        self._save_installed(installed)
        if self._is_live_root():
            self._activate_systemd_units(
                [p.name for p in targets],
                progress_cb=progress_cb,
            )
        return Progress(
            phase="done",
            percent=100,
            message=f"installed {len(targets)} package(s) into {self.install_root}",
        )

    def _is_live_root(self) -> bool:
        root = self.install_root.resolve()
        return str(self.install_root) in ("/", "/.") or root == Path("/")

    # Packages that ship systemd units localrpm must enable (cpio skips %post).
    _UNIT_BY_PACKAGE: dict[str, tuple[str, ...]] = {
        "nova-platform": ("nova-platformd.socket", "nova-platformd.service"),
        "novaos-update": ("nova-updated.socket", "nova-updated.service"),
    }

    def _activate_systemd_units(self, package_names: list[str], progress_cb=None) -> None:
        """Enable/start units that RPM %post would have handled.

        localrpm extracts payload only (rpm2cpio|cpio), so socket activation
        never runs. Without this, Center fails with ``No such file or directory``
        on ``/run/nova/platform.sock``.
        """
        units: list[str] = []
        for name in package_names:
            units.extend(self._UNIT_BY_PACKAGE.get(name, ()))
        if not units:
            return
        seen: set[str] = set()
        ordered: list[str] = []
        for unit in units:
            if unit not in seen:
                seen.add(unit)
                ordered.append(unit)
        if progress_cb:
            progress_cb(
                Progress(
                    phase="applying",
                    percent=98,
                    message=f"enable systemd: {', '.join(ordered)}",
                )
            )
        subprocess.run(
            ["systemctl", "daemon-reload"],
            check=False,
            capture_output=True,
            text=True,
        )
        for unit in ordered:
            subprocess.run(
                ["systemctl", "enable", "--now", unit],
                check=False,
                capture_output=True,
                text=True,
            )

    def _repair_usrmerge(self) -> None:
        """Keep /usr/sbin → bin after naive cpio extracts (Wi-Fi / wpa_supplicant)."""
        sbin = self.install_root / "usr" / "sbin"
        bin_dir = self.install_root / "usr" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        if sbin.is_symlink():
            return
        if sbin.is_dir():
            for child in list(sbin.iterdir()):
                dest = bin_dir / child.name
                if dest.exists() or dest.is_symlink():
                    if child.is_dir() and not child.is_symlink():
                        shutil.rmtree(child, ignore_errors=True)
                    else:
                        child.unlink(missing_ok=True)
                else:
                    child.rename(dest)
            try:
                sbin.rmdir()
            except OSError:
                shutil.rmtree(sbin, ignore_errors=True)
        elif sbin.exists():
            sbin.unlink()
        sbin.symlink_to("bin")

    def _extract_rpm(self, rpm_path: Path) -> None:
        # rpm2cpio | cpio into install_root (no chroot privileges required)
        proc = subprocess.Popen(
            ["rpm2cpio", str(rpm_path)],
            stdout=subprocess.PIPE,
        )
        assert proc.stdout is not None
        cpio = subprocess.run(
            ["cpio", "-idmu", "--quiet", "-D", str(self.install_root)],
            stdin=proc.stdout,
            check=False,
            capture_output=True,
            text=True,
        )
        proc.wait()
        if proc.returncode != 0 or cpio.returncode not in (0,):
            # cpio returns 0 on success; some versions warn on stdout
            err = cpio.stderr or f"rpm2cpio rc={proc.returncode}"
            if proc.returncode != 0:
                raise RuntimeError(f"failed to extract {rpm_path.name}: {err}")
