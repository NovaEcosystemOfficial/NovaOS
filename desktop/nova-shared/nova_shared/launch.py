"""Launch other Nova desktop apps."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def open_nova_center() -> bool:
    cmd = shutil.which("nova-center")
    if not cmd:
        repo = Path(__file__).resolve().parents[2] / "nova-center" / "bin" / "nova-center"
        if repo.is_file():
            cmd = str(repo)
    if not cmd:
        return False
    try:
        subprocess.Popen([cmd], start_new_session=True)  # noqa: S603
        return True
    except OSError:
        return False


def open_url(url: str) -> bool:
    xdg = shutil.which("xdg-open")
    if not xdg:
        return False
    try:
        subprocess.Popen([xdg, url], start_new_session=True)  # noqa: S603
        return True
    except OSError:
        return False
