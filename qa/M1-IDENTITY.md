# M1 — Nova Identity (QA / rollback)

Branch: `m1-nova-identity`  
Base: `v0.1.0-foundation`

## Scope

Branding only: system name, logo, wallpaper, color scheme, KSplash, SDDM theme,
system icon, os-release LOGO, Plasma look-and-feel defaults.

**Not changed:** kernel, bootloader, cmdline (`plymouth.enable=0` stays), systemd
services, Plasma session wrapper / VM graphics env, build pipeline scripts.

## Restore points

| Tag | Meaning |
|-----|---------|
| `m1-rp-0-start` | Branch start (= Foundation commit) |
| `m1-rp-1-assets` | After `branding/m1` + `assets/` exports |
| `m1-rp-2-overlay` | After KIWI `root/usr/share` overlay |
| `m1-rp-3-defaults` | After `config.sh` theme flips |
| `m1-rp-4-docs` | After CHANGELOG/README/QA docs |

Full rollback to Foundation:

```bash
git checkout v0.1.0-foundation
```

Partial rollback example (undo defaults only):

```bash
git revert <commit-of-m1-rp-3-defaults>
```

## Install paths (live image)

| Item | Path |
|------|------|
| Mark / wordmark | `/usr/share/novaos/branding/` |
| Pixmap / LOGO | `/usr/share/pixmaps/novaos.png` |
| Icons | `/usr/share/icons/hicolor/*/apps/novaos.png` |
| Wallpaper | `/usr/share/wallpapers/NovaOS/` |
| Colors | `/usr/share/color-schemes/NovaOS.colors` |
| SDDM | `/usr/share/sddm/themes/novaos/` |
| Look-and-feel + KSplash | `/usr/share/plasma/look-and-feel/org.novaos.desktop/` |

## Checklist visiva

- [x] Static ISO: SDDM theme `novaos`, LookAndFeel, colors, wallpaper, KSplash, `LOGO=novaos` (`_m1-verify-identity.sh` PASS — 2026-07-25)
- [ ] Manual: SDDM greeter shows NovaOS mark + ink card (theme `novaos`)
- [ ] Manual: Desktop wallpaper is NovaOS Ink Field
- [ ] Manual: Color scheme / window chrome follows Nova dark ink + stellar accents
- [ ] Manual: Brief KSplash (org.novaos.desktop) on session start
- [x] About / `os-release` shows `NAME=NovaOS`, `LOGO=novaos` (static PASS)
- [ ] Manual: VirtualBox VMSVGA 3D OFF still reaches desktop
- [ ] Manual: VMware / open-vm-tools path still reaches desktop
- [x] `make smoke` PASS (virtio + qxl) — `kwin-plasma` 2026-07-25 (`smoke-20260725T180703Z`)

ISO SHA256 (M1 rebuild): `1fe0531b50bc5ee6ec6206893811343be2108cdb699bf7008e0486848cf81ab4`

## Rebuild

```bash
sudo make iso
make smoke
# optional full P0:
sudo make p0-gate
```
