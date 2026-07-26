"""Hostname helpers shared with Nova Center / Welcome."""

from __future__ import annotations

import re
import socket
import subprocess
from pathlib import Path

_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$")


def get_hostname() -> str:
    try:
        return socket.gethostname()
    except OSError:
        path = Path("/etc/hostname")
        if path.is_file():
            return path.read_text(encoding="utf-8").strip() or "novaos"
        return "novaos"


def validate_hostname(name: str) -> tuple[bool, str]:
    value = (name or "").strip().lower()
    if not value:
        return False, "Inserisci un nome computer."
    if len(value) > 63:
        return False, "Massimo 63 caratteri."
    if not _HOSTNAME_RE.match(value):
        return False, "Usa solo lettere, numeri e trattini (non all’inizio/fine)."
    return True, value


def set_hostname(name: str) -> tuple[bool, str]:
    ok, normalized = validate_hostname(name)
    if not ok:
        return False, normalized
    err = ""
    for cmd in (
        ["hostnamectl", "set-hostname", normalized],
        ["pkexec", "hostnamectl", "set-hostname", normalized],
    ):
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            if proc.returncode == 0:
                return True, normalized
            err = (proc.stderr or proc.stdout or "").strip()
        except (OSError, subprocess.SubprocessError) as exc:
            err = str(exc)
    return False, err or "Impossibile impostare l’hostname"
