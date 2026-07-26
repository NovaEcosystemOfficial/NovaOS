"""Live network status from ip /sys and NetworkManager when available."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> str:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _nmcli_device() -> list[dict]:
    nmcli = shutil.which("nmcli")
    if not nmcli:
        return []
    out = _run(
        [
            nmcli,
            "-t",
            "-f",
            "DEVICE,TYPE,STATE,CONNECTION",
            "device",
            "status",
        ]
    )
    rows: list[dict] = []
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) < 4:
            continue
        device, typ, state, conn = parts[0], parts[1], parts[2], ":".join(parts[3:])
        rows.append(
            {
                "device": device,
                "type": typ,
                "state": state,
                "connection": conn or None,
            }
        )
    return rows


def _addresses() -> list[dict]:
    ip = shutil.which("ip")
    if not ip:
        return []
    out = _run([ip, "-j", "address", "show"])
    if not out:
        # Fallback plain parse
        plain = _run([ip, "-4", "address", "show"])
        rows: list[dict] = []
        current = None
        for line in plain.splitlines():
            if line and line[0].isdigit():
                bits = line.split()
                current = bits[1].rstrip(":") if len(bits) > 1 else None
            elif "inet " in line and current:
                addr = line.split()[1]
                rows.append({"device": current, "ipv4": addr.split("/")[0], "cidr": addr})
        return rows
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    rows = []
    for iface in data:
        name = iface.get("ifname")
        for addr in iface.get("addr_info") or []:
            if addr.get("family") != "inet":
                continue
            rows.append(
                {
                    "device": name,
                    "ipv4": addr.get("local"),
                    "prefix": addr.get("prefixlen"),
                    "cidr": f"{addr.get('local')}/{addr.get('prefixlen')}",
                }
            )
    return rows


def _default_route_iface() -> str | None:
    ip = shutil.which("ip")
    if not ip:
        return None
    out = _run([ip, "route", "show", "default"])
    if "dev " in out:
        parts = out.split()
        try:
            return parts[parts.index("dev") + 1]
        except (ValueError, IndexError):
            return None
    return None


def collect() -> dict:
    devices = _nmcli_device()
    addrs = _addresses()
    default_iface = _default_route_iface()

    ethernet = [d for d in devices if d.get("type") == "ethernet"]
    wifi = [d for d in devices if d.get("type") in ("wifi", "wlan")]

    # Fallback without nmcli: scan /sys/class/net
    if not devices:
        net = Path("/sys/class/net")
        if net.is_dir():
            for iface in sorted(net.iterdir()):
                name = iface.name
                if name == "lo":
                    continue
                oper = (iface / "operstate").read_text(encoding="utf-8").strip() if (iface / "operstate").is_file() else "unknown"
                wireless = (iface / "wireless").exists()
                devices.append(
                    {
                        "device": name,
                        "type": "wifi" if wireless else "ethernet",
                        "state": oper,
                        "connection": None,
                    }
                )
            ethernet = [d for d in devices if d.get("type") == "ethernet"]
            wifi = [d for d in devices if d.get("type") == "wifi"]

    connected = any(
        (d.get("state") or "").startswith("connected") or d.get("state") == "up"
        for d in devices
        if d.get("device") != "lo"
    )
    usable = [row for row in addrs if row.get("device") and row.get("device") != "lo"]
    primary_ip = None
    primary_nic = default_iface
    if default_iface and default_iface != "lo":
        for row in usable:
            if row.get("device") == default_iface:
                primary_ip = row.get("ipv4")
                primary_nic = row.get("device")
                break
    if primary_ip is None and usable:
        primary_ip = usable[0].get("ipv4")
        primary_nic = usable[0].get("device")
    elif primary_ip is None:
        # No non-loopback address — report unset rather than lo
        primary_nic = default_iface if default_iface and default_iface != "lo" else None

    return {
        "connected": connected,
        "status": "connesso" if connected else "non connesso",
        "default_interface": default_iface,
        "primary_nic": primary_nic,
        "primary_ipv4": primary_ip,
        "ethernet": ethernet,
        "wifi": wifi,
        "devices": devices,
        "addresses": addrs,
    }
