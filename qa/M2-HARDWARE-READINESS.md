# M2 — Real Hardware Readiness (audit)

Branch: `m2-hw-readiness`  
Base: `m1-nova-identity` / Foundation `v0.1.0-foundation`  
Restore: `m2-rp-0-start`  
Date: 2026-07-25

**Scope:** audit + fix only issues that compromise live boot / evaluation on real hardware.  
**Out of scope:** new product features, Anaconda/Calamares installer product, dual-boot UX, Secure Boot signing.

Legend: **PASS** | **WARNING** | **TODO** | **FAIL**

---

## Boot & install

| ID | Item | Status | Evidence / notes |
|----|------|--------|------------------|
| M2-01 | UEFI boot | **PASS** | KIWI `firmware="uefi"`, `shim-x64`, `grub2-efi-x64*`. Live ISO boots under OVMF. |
| M2-02 | Secure Boot | **WARNING** | `shim-x64` present; **no** production signing / MOK enrollment flow. **Documented:** disable Secure Boot in firmware for M2, or expect unsigned-chain failures. Tools `mokutil` + `efibootmgr` added for inspection only. |
| M2-03 | GPT | **WARNING** | Live ISO has EFI fat image; **no** installed GPT partition recipe (no installer). Target GPT layout remains documentation-only (`docs/boot-foundation/04-File-System.md`). |
| M2-04 | Dual boot (existing Linux) | **TODO** | Explicitly deferred. No `os-prober` / install-time EFI menu merge. Live boot does not alter host EFI entries. |
| M2-05 | Disk installer | **FAIL** | Image is **live-only** (overlay ISO). No Anaconda/Calamares/liveinst. Real-disk install is not available in M2. |

---

## Drivers & devices

| ID | Item | Status | Evidence / notes |
|----|------|--------|------------------|
| M2-10 | WiFi | **PASS*** | `NetworkManager` + `NetworkManager-wifi` + `plasma-nm`. `linux-firmware` added for device blobs. *Chip-specific validation on reference HW still manual. |
| M2-11 | Bluetooth | **WARNING→fix** | Was missing; `bluez` + `bluedevil` added, `bluetooth.service` enabled. Validate adapter on HW. |
| M2-12 | Audio | **WARNING→FIX** | Had `pipewire`/`wireplumber`/`plasma-pa`; added `pipewire-pulseaudio`, `pipewire-alsa`, `alsa-sof-firmware`. Validate SOF/HDA on laptop. |
| M2-13 | Touchpad | **PASS** | `xorg-x11-drv-libinput`; user in `input` group. |
| M2-14 | Battery | **WARNING→FIX** | Was missing `upower`; added + enabled. Plasma battery applet can function. |
| M2-15 | Suspend / Resume | **WARNING** | Nothing disables suspend; path via logind. **Not validated** on real laptop (VM smoke only). Resume black-screen risk if GPU path wrong — mitigated by bare-metal GL ungating. |
| M2-16 | Power management | **WARNING→FIX** | Added `power-profiles-daemon` + enable. No TLP (avoid conflict with PPD). |
| M2-17 | Graphics acceleration | **WARNING→FIX** | Mesa packages were present but **global software GL / QPainter** forced for VMs. Runtime gate: soft-GL only when `systemd-detect-virt -q`. Bare metal uses Mesa/HW path. |
| M2-18 | HiDPI | **WARNING→FIX** | Removed forced SDDM `-dpi 96`. Scaling still X11-limited (Wayland session remains disabled for Foundation VM stability). |

---

## Policy / known constraints (unchanged by design)

| Topic | Status | Note |
|-------|--------|------|
| Plymouth | WARNING | Still `plymouth.enable=0` (Foundation VM stability). Not an install blocker. |
| SELinux | WARNING | `selinux=0` / permissive for bring-up. |
| Wayland Plasma | WARNING | Still X11-first; Wayland session kept disabled. |
| NVIDIA proprietary | TODO | Nouveau / Mesa only; proprietary out of scope. |

---

## Minimal fixes applied in M2 (non-feature)

1. Packages: `linux-firmware`, `alsa-sof-firmware`, `upower`, `power-profiles-daemon`, `bluez`, `bluedevil`, `pipewire-pulseaudio`, `pipewire-alsa`, `mokutil`, `efibootmgr`
2. Runtime VM detection for software GL / `KWIN_COMPOSE=Q` (bare metal ungated)
3. Drop forced SDDM `-dpi 96`
4. Enable `bluetooth.service`, `upower.service`, `power-profiles-daemon.service`

**Not added (features / deferred):** Anaconda, Calamares, `os-prober`, Secure Boot signing, Wayland re-enable, Plymouth on.

---

## Manual validation matrix (reference PC)

Run on a real UEFI laptop with Secure Boot **off**:

| Test | Result (fill on HW) |
|------|---------------------|
| Boot live ISO UEFI | |
| WiFi associate | |
| Bluetooth pair | |
| Audio playback | |
| Touchpad / gestures | |
| Battery % in panel | |
| Suspend → resume | |
| Power profile switch | |
| `glxinfo` / renderer ≠ llvmpipe (bare metal) | |
| HiDPI readability | |
| Confirm Secure Boot on → document failure mode | |

---

## Automated verification (2026-07-25)

| Check | Result |
|-------|--------|
| ISO rebuild with M2 packages | **PASS** (`BUILD OK`) |
| Desktop smoke virtio + qxl | **PASS** (`kwin-plasma`) |
| ISO SHA256 | `5359c9fa34791e3e04d34f414f2a91b1952b9c3333c2bab433658356f00dc638` |

## Rollback

```bash
git checkout m2-rp-0-start
# or
git checkout v0.1.0-foundation
```
