# `configs/fedora/`

Version pins and package inventories for NovaOS images.

| File | Purpose |
|------|---------|
| `release.env` | `FEDORA_VERSION`, `NOVAOS_VERSION`, ISO basename |
| `packages.base.txt` | Reference list (bootstrap-oriented) |
| `packages.desktop.txt` | Reference list (Plasma/SDDM) |

Authoritative package selection for the image is in `configs/kiwi/novaos-m01/appliance.kiwi`.
`build-iso.sh` rewrites metalink Fedora version from `release.env` at build time.
