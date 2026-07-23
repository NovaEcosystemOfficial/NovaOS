# KIWI profile — novaos-m01

Real KIWI NG description for NovaOS 0.1 live ISO.

| File | Purpose |
|------|---------|
| `appliance.kiwi` | Image description (repos, packages, live ISO type) |
| `config.sh` | Chroot configure: identity, users, SDDM, graphical target |
| `iso-esp-excludes.yaml` | ESP file filter (Fedora KIWI practice) |
| `PUBLIC_DEMO_CREDENTIALS.txt` | Public demo login (not a secret) |

Also see repository root `SECURITY.md`.

Build:

```bash
sudo scripts/build-iso.sh
```

Pins: `configs/fedora/release.env`
