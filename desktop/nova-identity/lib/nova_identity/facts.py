"""Collect identity / about facts (platform.v1 when available)."""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path


def _platform_client():
    for root in (Path("/usr/lib/nova/platform"),):
        if (root / "nova_platform").is_dir() and str(root) not in sys.path:
            sys.path.insert(0, str(root))
            break
    try:
        from nova_platform.client import PlatformClient
        from nova_platform.config import PlatformConfig
    except ImportError:
        return None
    cfg = PlatformConfig.load()
    sock = Path(os.environ.get("NOVA_PLATFORM_SOCKET", cfg.socket_path))
    if not sock.exists():
        return None
    return PlatformClient(sock)


def _os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    for path in (Path("/etc/os-release"), Path("/usr/lib/os-release")):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            data[k] = v.strip().strip('"')
        break
    return data


def _pkg_version(name: str) -> str:
    try:
        proc = subprocess.run(
            ["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", name],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        out = (proc.stdout or "").strip()
        if proc.returncode == 0 and out and "not installed" not in out:
            return out
    except (OSError, subprocess.SubprocessError):
        pass
    return "—"


def _mem_human() -> str:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                kb = int(line.split()[1])
                return f"{kb / 1024 / 1024:.1f} GiB"
    except (OSError, ValueError):
        pass
    return "—"


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "—"


def _gpu() -> str:
    lspci = shutil.which("lspci")
    if not lspci:
        return "—"
    try:
        proc = subprocess.run([lspci], capture_output=True, text=True, timeout=5, check=False)
        for line in proc.stdout.splitlines():
            if any(x in line for x in ("VGA", "3D", "Display")):
                return line.split(":", 2)[-1].strip() if ":" in line else line.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "—"


def collect_about() -> dict:
    osrel = _os_release()
    hostname = socket.gethostname()
    client = _platform_client()
    platform_ver = "—"
    hardware: dict = {}
    if client is not None:
        try:
            ver = client.call("get-version")
            platform_ver = ver.get("platform_version") or platform_ver
            hardware = client.call("get-hardware") or {}
            host = client.call("get-hostname") or {}
            hostname = host.get("hostname") or hostname
            sysinfo = client.call("get-system-info") or {}
            if sysinfo.get("pretty_name"):
                osrel["PRETTY_NAME"] = sysinfo["pretty_name"]
        except Exception:
            pass

    cpu = (hardware.get("cpu") or {}).get("model") or _cpu_model()
    mem = (hardware.get("memory") or {}).get("total_human") or _mem_human()
    gpus = hardware.get("gpus") or []
    gpu = gpus[0] if gpus else _gpu()

    return {
        "pretty_name": osrel.get("PRETTY_NAME") or "NovaOS",
        "version": osrel.get("VERSION") or osrel.get("VERSION_ID") or "—",
        "kernel": platform.release(),
        "hostname": hostname,
        "platform": platform_ver,
        "center": _pkg_version("nova-center"),
        "update": _pkg_version("novaos-update"),
        "identity": _pkg_version("nova-identity"),
        "cpu": cpu,
        "ram": mem,
        "gpu": gpu,
        "architecture": platform.machine(),
    }


ASCII_LOGO = r"""
 ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗  ██████╗ ███████╗
 ████╗  ██║██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝
 ██╔██╗ ██║██║   ██║██║   ██║███████║██║   ██║███████╗
 ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║   ██║╚════██║
 ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║╚██████╔╝███████║
 ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
"""


def format_about(data: dict) -> str:
    lines = [
        ASCII_LOGO.rstrip(),
        "",
        f"  {data.get('pretty_name', 'NovaOS')}",
        f"  Versione      {data.get('version')}",
        f"  Kernel        {data.get('kernel')}",
        f"  Nova Platform {data.get('platform')}",
        f"  Nova Center   {data.get('center')}",
        f"  Nova Update   {data.get('update')}",
        f"  Nova Identity {data.get('identity')}",
        f"  Hostname      {data.get('hostname')}",
        f"  CPU           {data.get('cpu')}",
        f"  RAM           {data.get('ram')}",
        f"  GPU           {data.get('gpu')}",
        "",
    ]
    return "\n".join(lines)


def collect_info() -> dict:
    about = collect_about()
    return {
        "name": "NovaOS",
        "pretty_name": about["pretty_name"],
        "version": about["version"],
        "kernel": about["kernel"],
        "hostname": about["hostname"],
        "architecture": about["architecture"],
        "components": {
            "platform": about["platform"],
            "center": about["center"],
            "update": about["update"],
            "identity": about["identity"],
        },
    }


def collect_health() -> dict:
    client = _platform_client()
    if client is None:
        return {
            "status": "unavailable",
            "errors": ["nova-platformd non raggiungibile"],
            "hint": "Installa/avvia nova-platform via Nova Update",
        }
    try:
        return client.call("health")
    except Exception as exc:
        return {"status": "error", "errors": [str(exc)]}


def collect_diagnose() -> dict:
    health = collect_health()
    about = collect_about()
    paths = {
        "/usr/share/nova/assets": Path("/usr/share/nova/assets").is_dir(),
        "/usr/share/nova/assets/logo/novaos.png": Path("/usr/share/nova/assets/logo/novaos.png").is_file(),
        "/run/nova/platform.sock": Path("/run/nova/platform.sock").exists(),
        "/run/nova/update.sock": Path("/run/nova/update.sock").exists(),
        "/var/log/nova": Path("/var/log/nova").is_dir(),
    }
    bins = {
        name: bool(shutil.which(name))
        for name in (
            "nova-platformctl",
            "nova-updater",
            "nova-center",
            "nova-update-gui",
            "nova-about",
        )
    }
    errors = list(health.get("errors") or [])
    for path, ok in paths.items():
        if not ok:
            errors.append(f"manca {path}")
    for name, ok in bins.items():
        if not ok:
            errors.append(f"comando assente: {name}")
    return {
        "status": "ok" if not errors else "issues",
        "about": about,
        "health": health,
        "paths": paths,
        "binaries": bins,
        "errors": errors,
    }
