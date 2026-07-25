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

- [ ] SDDM greeter shows NovaOS mark + ink card (theme `novaos`)
- [ ] Desktop wallpaper is NovaOS Ink Field
- [ ] Color scheme / window chrome follows Nova dark ink + stellar accents
- [ ] Brief KSplash (org.novaos.desktop) on session start
- [ ] About / `os-release` shows `NAME=NovaOS`, `LOGO=novaos`
- [ ] VirtualBox VMSVGA 3D OFF still reaches desktop
- [ ] VMware / open-vm-tools path still reaches desktop
- [ ] `make smoke` PASS (virtio + qxl)

## Rebuild

```bash
sudo make iso
make smoke
# optional full P0:
sudo make p0-gate
```
