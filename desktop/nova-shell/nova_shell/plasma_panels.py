"""Remove Plasma panels so Nova Top Bar is the only top chrome."""

from __future__ import annotations

import shutil
import subprocess


_SCRIPT = """
var allPanels = panels();
for (var i = allPanels.length - 1; i >= 0; --i) {
    try { allPanels[i].remove(); } catch (e) {}
}
"""


def _qdbus() -> str | None:
    for name in ("qdbus-qt6", "qdbus6", "qdbus"):
        path = shutil.which(name)
        if path:
            return path
    return None


def hide_plasma_panels() -> bool:
    """Best-effort: strip all Plasma panels via plasmashell scripting API."""
    qdbus = _qdbus()
    if qdbus is None:
        return False
    try:
        proc = subprocess.run(  # noqa: S603
            [
                qdbus,
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                _SCRIPT,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False
