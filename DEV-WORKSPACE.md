# NovaOS development workspace

**Sprint 6+ — real ISO build infrastructure**

## Build the first live ISO (Fedora host)

```bash
make validate          # static pipeline checks
sudo make setup        # install kiwi/qemu
make check             # host readiness
sudo make iso          # produce ISO
make vm                # boot in QEMU
```

Output:

- `iso/releases/novaos-0.1.0-x86_64-live.iso`
- `iso/latest/novaos-current.iso`

Login (public demo, not a secret): `nova` / `novaos` — see `SECURITY.md` and `configs/kiwi/novaos-m01/PUBLIC_DEMO_CREDENTIALS.txt`.

## Layout

| Path | Role |
|------|------|
| `configs/kiwi/novaos-m01/` | KIWI description (appliance + config.sh) |
| `configs/fedora/release.env` | Fedora/NovaOS version pins |
| `scripts/build-iso.sh` | KIWI build entrypoint |
| `build/work/` | KIWI target dirs |
| `iso/releases/` | Published ISO artifacts |
| `vm/` | QEMU test disk |

## Scope of this ISO

Included: boot, SDDM, stock Plasma desktop, Konsole, System Settings, NetworkManager.  
Excluded: Ryuk, Nova AI, Nova Shell product, Nova Cloud/Store/Apps.

## Requirements

- Fedora host with KVM recommended
- ~80 GB free disk
- Root for KIWI build
- Network access to Fedora mirrors
