# `installer/`

Installer e onboarding di NovaOS.

## Milestone 0.2 — Installable (implementato)

Motore: **Calamares** (ADR-008), integrato nella Live ISO KIWI senza regressioni sul boot live.

| Path | Ruolo |
|------|-------|
| `calamares/settings.conf` | Sequenza moduli + branding `novaos` |
| `calamares/modules/` | Partition (dual-boot safe), users, unpackfs, grub, SDDM, post-install |
| `calamares/scripts/novaos-post-install.sh` | Hardening target: no autologin, os-prober, rimozione demo |
| `calamares/branding/novaos/` | Nome prodotto NovaOS |
| `calamares/desktop/novaos-installer.desktop` | Launcher “Install NovaOS” |

Build sync: `scripts/build-iso.sh` copia questo tree in `root/` dell’immagine.

### Dual-boot

- Scelta partizionamento iniziale: **none** (niente erase accidentale)
- Opzioni: Alongside / Replace / Erase / Manual
- `os-prober` + `GRUB_DISABLE_OS_PROBER=false`

### Test

```bash
make validate-installer
sudo make iso
sudo make install-gate
# Manuale: qa/INSTALL-CHECKLIST.md
```

### Reversibilità

Rimuovere pacchetti `calamares*` da `appliance.kiwi` e saltare lo sync in `build-iso.sh` riporta a live-only (Foundation).

## Specifica

- [`docs/boot-foundation/05-Installer.md`](../docs/boot-foundation/05-Installer.md)
- [`docs/adr/ADR-008-Installer-Engine.md`](../docs/adr/ADR-008-Installer-Engine.md)

## Fuori scope (ancora)

Wizard NovaAI / NovaCloud / Ryuk / Store.
