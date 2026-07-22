# KIWI profile — novaos-m01

Real KIWI NG description for NovaOS 0.1 live ISO.

| File | Purpose |
|------|---------|
| `appliance.kiwi` | Image description (repos, packages, live ISO type) |
| `config.sh` | Chroot configure: identity, users, SDDM, graphical target |
| `iso-esp-excludes.yaml` | ESP file filter (Fedora KIWI practice) |
| `CREDENTIALS.txt` | Default login for the image |

Build:

```bash
sudo scripts/build-iso.sh
```

Pins: `configs/fedora/release.env`
