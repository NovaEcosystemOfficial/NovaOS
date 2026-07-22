#!/usr/bin/env python3
"""Static validation helpers runnable without bash (optional CI/Windows check)."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)
    print(f"FAIL: {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    kiwi = ROOT / "configs/kiwi/novaos-m01/appliance.kiwi"
    env = ROOT / "configs/fedora/release.env"
    host = ROOT / "configs/bootstrap/host-packages.txt"
    build = ROOT / "scripts/build-iso.sh"

    if not kiwi.is_file():
        fail(f"missing {kiwi}")
        return 1

    try:
        ET.parse(kiwi)
        ok("appliance.kiwi parses as XML")
    except ET.ParseError as exc:
        fail(f"appliance.kiwi XML: {exc}")

    text = kiwi.read_text(encoding="utf-8")
    for needle in (
        "iso-esp-excludes.yaml",
        "dracut-kiwi-live",
        "sddm",
        "plasma-desktop",
        "konsole",
        "plasma-systemsettings",
        "shim-x64",
        "grub2-tools",
    ):
        if needle in text:
            ok(f"appliance contains {needle}")
        else:
            fail(f"appliance missing {needle}")

    env_vars = {}
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env_vars[k.strip()] = v.strip()
    for key in (
        "FEDORA_VERSION",
        "FEDORA_ARCH",
        "NOVAOS_VERSION",
        "NOVAOS_PROFILE",
        "NOVAOS_ISO_NAME",
        "NOVAOS_MILESTONE",
    ):
        if env_vars.get(key):
            ok(f"release.env {key}={env_vars[key]}")
        else:
            fail(f"release.env missing {key}")

    host_txt = host.read_text(encoding="utf-8")
    if "kiwi-systemdeps-iso-media" in host_txt:
        ok("host-packages has kiwi-systemdeps-iso-media")
    else:
        fail("host-packages missing kiwi-systemdeps-iso-media")
    if re.search(r"(?m)^kiwi-systemdeps-iso$", host_txt):
        fail("host-packages still has obsolete kiwi-systemdeps-iso")

    build_txt = build.read_text(encoding="utf-8")
    if "DESC_WORK=" in build_txt and "TARGET_DIR=" in build_txt:
        ok("build-iso separates DESC_WORK and TARGET_DIR")
    else:
        fail("build-iso missing DESC_WORK/TARGET_DIR separation")

    # Metalink pin dry-run
    sample = text
    ver, arch = env_vars.get("FEDORA_VERSION", "44"), env_vars.get("FEDORA_ARCH", "x86_64")
    sample2, n1 = re.subn(
        r"metalink\?repo=fedora-\d+&amp;arch=[a-z0-9_]+",
        f"metalink?repo=fedora-{ver}&amp;arch={arch}",
        sample,
    )
    _, n2 = re.subn(
        r"metalink\?repo=updates-released-f\d+&amp;arch=[a-z0-9_]+",
        f"metalink?repo=updates-released-f{ver}&amp;arch={arch}",
        sample2,
    )
    if n1 and n2:
        ok("metalink pin patterns match")
    else:
        fail(f"metalink pin patterns (fedora={n1}, updates={n2})")

    if errors:
        print(f"validate-static: FAILED ({len(errors)})")
        return 1
    print("validate-static: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
