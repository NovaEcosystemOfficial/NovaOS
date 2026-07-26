"""Live hardware inventory from /proc and /sys."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path


def _read_first(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None


def _cpu() -> dict:
    model = "sconosciuto"
    cores = 0
    try:
        text = Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if line.lower().startswith("model name") and ":" in line:
                model = line.split(":", 1)[1].strip()
                break
        cores = text.count("processor\t:") or text.count("processor:")
    except OSError:
        pass
    if not cores:
        cores = os.cpu_count() or 0
    load = None
    try:
        load = os.getloadavg()
    except OSError:
        pass
    return {
        "model": model,
        "cores": cores,
        "loadavg": list(load) if load else None,
    }


def _mem() -> dict:
    total = avail = used = None
    try:
        data: dict[str, int] = {}
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            key, rest = line.split(":", 1)
            num = rest.strip().split()[0]
            data[key] = int(num) * 1024
        total = data.get("MemTotal")
        avail = data.get("MemAvailable") or data.get("MemFree")
        if total is not None and avail is not None:
            used = total - avail
    except OSError:
        pass
    return {
        "total_bytes": total,
        "used_bytes": used,
        "available_bytes": avail,
        "total_human": _bytes_h(total),
        "used_human": _bytes_h(used),
        "available_human": _bytes_h(avail),
        "percent_used": round(100.0 * used / total, 1) if total and used is not None else None,
    }


def _bytes_h(n: int | None) -> str:
    if n is None:
        return "—"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return str(n)


def _disk() -> list[dict]:
    rows: list[dict] = []
    try:
        proc = subprocess.run(
            ["df", "-B1", "--output=source,fstype,size,used,avail,pcent,target", "-x", "tmpfs", "-x", "devtmpfs"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 7:
                continue
            source, fstype, size, used, avail, pcent, *target_parts = parts
            target = " ".join(target_parts)
            if not target.startswith("/"):
                continue
            # Prefer real block devices / root
            if not (source.startswith("/dev/") or target == "/"):
                continue
            rows.append(
                {
                    "source": source,
                    "fstype": fstype,
                    "size_bytes": int(size),
                    "used_bytes": int(used),
                    "avail_bytes": int(avail),
                    "percent": pcent,
                    "mount": target,
                    "size_human": _bytes_h(int(size)),
                    "used_human": _bytes_h(int(used)),
                }
            )
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return rows


def _gpu() -> list[str]:
    gpus: list[str] = []
    lspci = shutil.which("lspci")
    if lspci:
        try:
            proc = subprocess.run(
                [lspci],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            for line in proc.stdout.splitlines():
                if re.search(r"VGA|3D|Display", line, re.I):
                    gpus.append(line.split(":", 2)[-1].strip() if ":" in line else line.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    if not gpus:
        drm = Path("/sys/class/drm")
        if drm.is_dir():
            for card in sorted(drm.glob("card[0-9]")):
                name = _read_first(card / "device" / "uevent") or card.name
                gpus.append(name.splitlines()[0] if name else card.name)
    return gpus or ["non rilevata"]


def _temperatures() -> list[dict]:
    temps: list[dict] = []
    thermal = Path("/sys/class/thermal")
    if thermal.is_dir():
        for zone in sorted(thermal.glob("thermal_zone*")):
            raw = _read_first(zone / "temp")
            typ = _read_first(zone / "type") or zone.name
            if raw and raw.lstrip("-").isdigit():
                millideg = int(raw)
                temps.append({"name": typ, "celsius": millideg / 1000.0})
    hwmon = Path("/sys/class/hwmon")
    if hwmon.is_dir():
        for mon in sorted(hwmon.iterdir()):
            label_root = _read_first(mon / "name") or mon.name
            for input_path in sorted(mon.glob("temp*_input")):
                raw = _read_first(input_path)
                if not raw or not raw.lstrip("-").isdigit():
                    continue
                idx = input_path.name.replace("temp", "").replace("_input", "")
                label = _read_first(mon / f"temp{idx}_label") or f"{label_root} temp{idx}"
                temps.append({"name": label, "celsius": int(raw) / 1000.0})
    # Deduplicate by name keeping first
    seen: set[str] = set()
    unique: list[dict] = []
    for item in temps:
        if item["name"] in seen:
            continue
        seen.add(item["name"])
        unique.append(item)
    return unique


def _battery() -> dict | None:
    base = Path("/sys/class/power_supply")
    if not base.is_dir():
        return None
    for bat in sorted(base.glob("BAT*")):
        status = _read_first(bat / "status") or "Unknown"
        capacity = _read_first(bat / "capacity")
        tech = _read_first(bat / "technology")
        name = _read_first(bat / "model_name") or bat.name
        return {
            "present": True,
            "name": name,
            "status": status,
            "capacity_percent": int(capacity) if capacity and capacity.isdigit() else None,
            "technology": tech,
        }
    return {"present": False}


def collect() -> dict:
    return {
        "cpu": _cpu(),
        "memory": _mem(),
        "disks": _disk(),
        "gpus": _gpu(),
        "temperatures": _temperatures(),
        "battery": _battery(),
    }
