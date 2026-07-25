# Changelog

All notable changes to NovaOS are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows foundation tags (`v0.1.0-foundation`, …) until product semver stabilizes.

---

## [0.1.0-foundation] — 2026-07-25

Foundation freeze: first bootable NovaOS live ISO (Fedora 44 / KIWI NG / Plasma X11).

### Added

- KIWI profile `configs/kiwi/novaos-m01` producing `iso/NovaOS_0.1.iso`
- Live demo user `nova` / `novaos` (public credentials; see `SECURITY.md`)
- Automated desktop smoke: `scripts/smoke-desktop.sh` (virtio + qxl)
- P0 stability gate: `scripts/qa-p0-gate.sh` / `make p0-gate`
- VM-oriented graphics stack: VBox guest additions stubs, open-vm-tools, software GL defaults

### Fixed

- **ISSUE-001** — After graphical login, session returned to console/greeter  
  - **Cause:** `98vboxadd-xclient.sh` used bare `exit 0` while sourced by SDDM `Xsession`  
  - **Fix:** replace with `return 0`; guard other sourced `exit` in `xinitrc.d`  
  - **Regression:** `smoke-desktop.sh` must PASS (`kwin-plasma` / plasmashell)
- Missing `systemd-pam` / session bus race → no `XDG_RUNTIME_DIR` (session died early)
- Fedora `plasma-wayland.conf` forcing Wayland greeter on VM X11 path

### Security / scope

- Ryuk, Nova AI Core, and product Nova Shell are **not** included or enabled
- SELinux set permissive in image for foundation bring-up

### Known limitations (accepted for freeze)

- Branding is minimal (stock Breeze / SDDM breeze; full Nova theme is post-0.1)
- Installer path not required for this freeze (live boot)
- QEMU nested `vmware-svga` is unreliable; smoke uses virtio + qxl stand-ins
- Interactive UI power actions (M7/M8) gated via systemd targets + desktop session smoke

### Verification

P0 gate (`make p0-gate`) must be **PASS** on the freeze ISO before tagging.

---

## [Unreleased]

_No changes yet beyond 0.1.0-foundation._
