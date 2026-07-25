# NovaOS Foundation 0.1 — P0 Gate Report

- Date: 2026-07-25T15:43:59+02:00
- ISO: `iso/NovaOS_0.1.iso`
- SHA256: `be0f4733c1f46837f0ad2b066541d0d12d5061edb3f807ba450685097ce2453a`
- Smoke dir: `/var/tmp/novaos-build/logs/smoke-20260725T132759Z`
- Tag: `v0.1.0-foundation`

| ID | Result | Notes |
|----|--------|-------|
| P0-INT | PASS | ISO SHA256 OK |
| P0-M5 | PASS | konsole present |
| P0-M6 | PASS | systemsettings present |
| P0-M7 | PASS | systemd poweroff.target present |
| P0-M8 | PASS | systemd reboot.target present |
| P0-R-ISSUE001 | PASS | no bare exit in 98vboxadd-xclient.sh |
| P0-STACK | PASS | sddm + startplasma-x11 present |
| P0-S1 | PASS | QEMU boot / smoke completed |
| P0-S2 | PASS | graphical session stayed up (smoke PASS) |
| P0-S3 | PASS | desktop session verified (kwin-plasma) |
| P0-R1 | PASS | smoke virtio+qxl both PASS |

**GATE: PASS** — Foundation 0.1 P0 automated checks green.

Re-run: `sudo make p0-gate`
