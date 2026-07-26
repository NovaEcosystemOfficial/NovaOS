"""Verify Nova session services and surface a single status notification if broken."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

_CANDIDATES = (
    Path("/usr/share/nova/desktop"),
    Path(__file__).resolve().parents[1],
)
for _root in _CANDIDATES:
    if (_root / "nova_desktop").is_dir() and str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
        break

from nova_desktop.notify import notify  # noqa: E402


def _unit_active(name: str) -> bool:
    try:
        r = subprocess.run(
            ["systemctl", "is-active", "--quiet", name],
            check=False,
            timeout=5,
        )
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _which(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def main() -> int:
    if os.environ.get("NOVA_SESSION_CHECK_SILENT") == "1":
        quiet = True
    else:
        quiet = False

    problems: list[str] = []
    if not (_unit_active("nova-updated.socket") or _unit_active("nova-updated.service")):
        problems.append("nova-updated non attivo")
    if not _which("nova-center"):
        problems.append("Nova Center assente")
    if not _which("nova-update-gui"):
        problems.append("Nova Update assente")
    if not Path("/run/nova/update.sock").exists() and not Path(
        os.environ.get("NOVA_UPDATE_SOCKET", "/run/nova/update.sock")
    ).exists():
        problems.append("socket update mancante")

    if problems and not quiet:
        notify(
            "Sessione Nova: attenzione",
            "; ".join(problems),
            icon="dialog-warning",
            urgency="normal",
        )
        print("NOVA_SESSION_CHECK_FAIL", "; ".join(problems))
        return 1
    print("NOVA_SESSION_CHECK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
