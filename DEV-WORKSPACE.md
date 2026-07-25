# NovaOS development workspace

**Milestone 0.2 — live + installable ISO (Calamares)**

## Build the installable live ISO (Fedora host)

```bash
make validate
make validate-installer
sudo make setup        # install kiwi/qemu
make check             # host readiness
sudo make iso          # produce ISO
sudo make p0-gate      # live stability
sudo make install-gate # installer present in image
make vm                # boot in QEMU
```

**Host requirements:** ~80 GB free Linux filesystem, root for KIWI, network to Fedora mirrors.  
If the repo lives on a small live overlay, set `NOVAOS_BUILD_DIR` to a large local disk before building.

Output:

- `iso/releases/NovaOS_0.2.iso` (and versioned copies per `release.env`)
- `iso/NovaOS_0.2.iso`
- `iso/latest/novaos-current.iso`

Login live (public demo, not a secret): `nova` / `novaos` — see `SECURITY.md`.  
Install: launch **Install NovaOS** → Calamares. Installed systems use the account you create (demo user removed).

## Layout

| Path | Role |
|------|------|
| `configs/kiwi/novaos-m01/` | KIWI description (appliance + config.sh) |
| `installer/calamares/` | Canonical Calamares config (synced at build) |
| `configs/fedora/release.env` | Fedora/NovaOS version pins |
| `scripts/build-iso.sh` | KIWI build entrypoint + installer sync |
| `build/work/` | KIWI target dirs |
| `iso/releases/` | Published ISO artifacts |
| `vm/` | QEMU test disk |
| `qa/INSTALL-CHECKLIST.md` | Manual install / dual-boot tests |

## Scope of this ISO

Included: boot, SDDM, Plasma, Konsole, System Settings, NetworkManager, **Calamares installer**, os-prober, development tools.  
Excluded: Ryuk, Nova AI, Nova Shell product, Nova Cloud/Store/Apps.

## Dual-boot notes

- Prefer **Alongside** or **Manual** when another OS is present.
- Erase disk is available but never pre-selected; confirm at prompt.
- UEFI + GPT recommended; match firmware mode of the existing OS.
