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

## [Unreleased] — M2 Real Hardware Readiness (branch `m2-hw-readiness`)

Audit + minimal fixes for live evaluation on real UEFI hardware. No installer
product, no Secure Boot signing, no dual-boot feature.

### Added

- Checklist `qa/M2-HARDWARE-READINESS.md` (PASS / WARNING / TODO / FAIL)
- Packages: `linux-firmware`, `alsa-sof-firmware`, `upower`, `power-profiles-daemon`,
  `bluez`, `bluedevil`, `pipewire-pulseaudio`, `pipewire-alsa`, `mokutil`, `efibootmgr`

### Changed

- Software GL / `KWIN_COMPOSE=Q` applied only when `systemd-detect-virt -q` (bare metal uses Mesa)
- Removed forced SDDM `-dpi 96` (HiDPI-friendly)
- Enable `bluetooth`, `upower`, `power-profiles-daemon` services

### Documented limitations

- **Secure Boot:** not supported for production; disable in firmware for M2
- **Installer:** live-only (FAIL for disk install) — deferred
- **Dual boot:** TODO — deferred
- **GPT install layout:** WARNING — no on-disk installer to apply it

---

## [Unreleased] — M1 Nova Identity (branch `m1-nova-identity`)

Branding-only milestone on top of Foundation 0.1. No kernel/bootloader/cmdline,
no session/graphics stack changes, no build-pipeline script changes.

### Added

- Official M1 assets (Luminous Precision): mark, wordmark, wallpaper, system icon
- Color scheme `NovaOS` (`/usr/share/color-schemes/NovaOS.colors`)
- SDDM theme `novaos` (X11 / software-GL friendly)
- Plasma look-and-feel `org.novaos.desktop` + KSplash QML
- KIWI root overlay under `configs/kiwi/novaos-m01/root/usr/share/…`
- Identity defaults: SDDM theme, LookAndFeel, ColorScheme, `os-release` `LOGO=novaos`
- Restore tags: `m1-rp-0-start` … `m1-rp-4-docs` (see `qa/M1-IDENTITY.md`)

### Known limitations

- Plymouth remains **disabled** (`plymouth.enable=0`) for VirtualBox/VMware stability
- Stock Plasma layout (panels); product Nova Shell layout is out of scope
- RPM packaging of branding packages remains deferred (overlay installs files)

### Rollback

```bash
git checkout v0.1.0-foundation
# or revert M1 commits / reset to m1-rp-0-start
```
