# KIWI profile — novaos-m01

KIWI NG description for NovaOS **0.2** live + installable ISO (profile name kept for pipeline compatibility).

| File | Purpose |
|------|---------|
| `appliance.kiwi` | Image description (repos, packages, live ISO type, Calamares, devtools) |
| `config.sh` | Chroot configure: identity, users, SDDM, installer launcher |
| `iso-esp-excludes.yaml` | ESP file filter (Fedora KIWI practice) |
| `PUBLIC_DEMO_CREDENTIALS.txt` | Public demo login for **live** only (not a secret) |

Installer configs are **not** stored here permanently: `scripts/build-iso.sh` syncs `installer/calamares/` into the description `root/` overlay at build time.

Also see repository root `SECURITY.md`, `installer/README.md`, ADR-008.

Build:

```bash
sudo scripts/build-iso.sh
```

Pins: `configs/fedora/release.env`
