"""Live network status from NetworkManager / ip /sys (no mocks)."""

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
            timeout=8,
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


def _nm_field(blob: str, key: str) -> str | None:
    prefix = f"{key}:"
    for line in blob.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip() or None
    return None


def _wifi_signal_percent(device: str) -> int | None:
    """Best-effort signal from nmcli device wifi list (IN-USE row)."""
    nmcli = shutil.which("nmcli")
    if not nmcli:
        return None
    out = _run(
        [
            nmcli,
            "-t",
            "-f",
            "IN-USE,SSID,SIGNAL,SECURITY",
            "device",
            "wifi",
            "list",
            "ifname",
            device,
        ]
    )
    for line in out.splitlines():
        # IN-USE may be "*" or "*:" depending on version; fields colon-separated
        parts = line.split(":")
        if not parts:
            continue
        in_use = parts[0]
        if in_use in ("*", "yes", "Sí", "sì"):
            # SSID can contain escaped colons (\:)
            # nmcli -t escapes : as \:
            raw = line[len(parts[0]) + 1 :]
            fields: list[str] = []
            buf = ""
            esc = False
            for ch in raw:
                if esc:
                    buf += ch
                    esc = False
                    continue
                if ch == "\\":
                    esc = True
                    continue
                if ch == ":":
                    fields.append(buf)
                    buf = ""
                    continue
                buf += ch
            fields.append(buf)
            if len(fields) >= 2 and fields[1].isdigit():
                return int(fields[1])
            if len(fields) >= 2:
                # SIGNAL is usually second after SSID
                for cand in fields[1:]:
                    if cand.isdigit():
                        return int(cand)
    # Fallback: /proc/net/wireless
    try:
        text = Path("/proc/net/wireless").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("Inter"):
            continue
        if not line.lstrip().startswith(f"{device}:"):
            continue
        bits = line.replace("|", " ").split()
        # iface status link level noise …
        if len(bits) >= 4:
            try:
                level = float(bits[3].rstrip("."))
                # level is often negative dBm-ish quality; map roughly if 0–100 already
                if level < 0:
                    return max(0, min(100, int(2 * (level + 100))))
                return max(0, min(100, int(level)))
            except ValueError:
                return None
    return None


def _wifi_details(devices: list[dict], addrs: list[dict]) -> list[dict]:
    """Enrich Wi-Fi NICs with SSID, signal, security, IP (live nmcli)."""
    nmcli = shutil.which("nmcli")
    enriched: list[dict] = []
    for d in devices:
        if d.get("type") not in ("wifi", "wlan"):
            continue
        device = d.get("device") or ""
        state = d.get("state") or "unknown"
        conn = d.get("connection")
        detail = {
            "device": device,
            "state": state,
            "status": _wifi_status_label(state),
            "connection": conn,
            "ssid": None,
            "signal_percent": None,
            "security": None,
            "ipv4": None,
            "hw_address": None,
            "autoconnect": None,
        }
        for row in addrs:
            if row.get("device") == device:
                detail["ipv4"] = row.get("ipv4")
                break
        if nmcli and device:
            show = _run([nmcli, "-t", "device", "show", device])
            detail["hw_address"] = _nm_field(show, "GENERAL.HWADDR")
            general_conn = _nm_field(show, "GENERAL.CONNECTION")
            if general_conn and general_conn != "--":
                detail["connection"] = general_conn
                conn = general_conn
            # Active connection properties
            if conn and conn not in ("--", "", None):
                cshow = _run([nmcli, "-t", "connection", "show", conn])
                detail["ssid"] = _nm_field(cshow, "802-11-wireless.ssid")
                detail["security"] = _nm_field(cshow, "802-11-wireless-security.key-mgmt")
                auto = _nm_field(cshow, "connection.autoconnect")
                if auto is not None:
                    detail["autoconnect"] = auto.lower() in ("yes", "true", "1")
            if state.startswith("connected"):
                detail["signal_percent"] = _wifi_signal_percent(device)
                if not detail["security"]:
                    # From scan line for in-use AP
                    scan = _run(
                        [
                            nmcli,
                            "-t",
                            "-f",
                            "IN-USE,SSID,SIGNAL,SECURITY",
                            "device",
                            "wifi",
                            "list",
                            "ifname",
                            device,
                        ]
                    )
                    for line in scan.splitlines():
                        if line.startswith("*:") or line.startswith("*:"):
                            pass
                        parts = line.split(":")
                        if parts and parts[0] in ("*", "yes"):
                            # last field often security; SSID may contain \:
                            if len(parts) >= 4:
                                detail["security"] = parts[-1] or detail["security"]
                            break
        enriched.append(detail)
    return enriched


def _wifi_status_label(state: str) -> str:
    s = (state or "").lower()
    if s.startswith("connected"):
        return "Connesso"
    if s in ("disconnected", "deactivating", "down"):
        return "Disconnesso"
    if s == "unavailable":
        return "Non disponibile"
    if s in ("connecting", "prepare", "config", "need-auth", "ip-config", "ip-check"):
        return "Connessione in corso"
    return state or "sconosciuto"


def _wifi_radio() -> dict:
    nmcli = shutil.which("nmcli")
    if not nmcli:
        return {"wifi": None, "wifi_hw": None}
    out = _run([nmcli, "-t", "radio"])
    # WIFI-HW:enabled  WIFI:enabled  …
    result = {"wifi": None, "wifi_hw": None}
    # Prefer key-value style if present
    kv = _run([nmcli, "-t", "-f", "WIFI-HW,WIFI", "radio"])
    if kv and ":" in kv:
        # may be single line WIFI-HW:enabled:WIFI:enabled or two fields
        parts = kv.split(":")
        if len(parts) >= 2:
            result["wifi_hw"] = parts[0] if parts[0] in ("enabled", "disabled") else parts[1] if len(parts) > 1 else None
        # Fallback parse table from `nmcli radio`
    for line in out.splitlines():
        cols = line.split()
        if len(cols) >= 2 and cols[0].upper().startswith("WIFI") and not cols[0].upper().startswith("WIFI-HW"):
            result["wifi"] = cols[1]
        if len(cols) >= 2 and cols[0].upper().startswith("WIFI-HW"):
            result["wifi_hw"] = cols[1]
    # `nmcli -t radio` on Fedora: enabled:enabled:… order WIFI-HW WIFI WWAN-HW WWAN
    t = _run([nmcli, "-t", "radio"])
    if t and ":" in t and result["wifi"] is None:
        bits = t.split(":")
        if len(bits) >= 2:
            result["wifi_hw"] = bits[0]
            result["wifi"] = bits[1]
    return result


def _supplicant_ok() -> dict:
    systemctl = shutil.which("systemctl")
    state = "unknown"
    if systemctl:
        state = _run([systemctl, "is-active", "wpa_supplicant.service"]) or "unknown"
    path_ok = Path("/usr/sbin/wpa_supplicant").exists() or Path("/usr/bin/wpa_supplicant").exists()
    usrmerge_ok = Path("/usr/sbin").is_symlink() or (
        Path("/usr/sbin/wpa_supplicant").exists() and Path("/usr/bin/wpa_supplicant").exists()
    )
    return {
        "wpa_supplicant": state,
        "binary_present": path_ok,
        "usrmerge_ok": bool(Path("/usr/sbin").is_symlink()),
        "detail_usrmerge": usrmerge_ok,
    }


def collect() -> dict:
    devices = _nmcli_device()
    addrs = _addresses()
    default_iface = _default_route_iface()

    ethernet = [d for d in devices if d.get("type") == "ethernet"]
    wifi = [d for d in devices if d.get("type") in ("wifi", "wlan")]

    if not devices:
        net = Path("/sys/class/net")
        if net.is_dir():
            for iface in sorted(net.iterdir()):
                name = iface.name
                if name == "lo":
                    continue
                oper = (
                    (iface / "operstate").read_text(encoding="utf-8").strip()
                    if (iface / "operstate").is_file()
                    else "unknown"
                )
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

    wifi_details = _wifi_details(wifi, addrs)
    radio = _wifi_radio()
    supp = _supplicant_ok()

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
        primary_nic = default_iface if default_iface and default_iface != "lo" else None

    primary_wifi = next(
        (w for w in wifi_details if (w.get("state") or "").startswith("connected")),
        wifi_details[0] if wifi_details else None,
    )

    return {
        "connected": connected,
        "status": "connesso" if connected else "non connesso",
        "default_interface": default_iface,
        "primary_nic": primary_nic,
        "primary_ipv4": primary_ip,
        "ethernet": ethernet,
        "wifi": wifi,
        "wifi_details": wifi_details,
        "primary_wifi": primary_wifi,
        "wifi_radio": radio,
        "supplicant": supp,
        "devices": devices,
        "addresses": addrs,
    }
