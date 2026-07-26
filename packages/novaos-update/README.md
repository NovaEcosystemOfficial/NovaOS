# `novaos-update` package sources

Sorgenti e metadati per il pacchetto RPM che distribuisce:

- `nova-updated`
- `nova-updater`
- config `/etc/nova/update/`
- unit systemd
- file `.repo` canali
- stub UI Nova Update

Lo `.spec` ufficiale è in [`../SPECS/novaos-update.spec`](../SPECS/novaos-update.spec).
Il codice vive nel monorepo sotto `system/update/`, `shell/nova-updater/`,
`desktop/nova-update/`, `packages/repo/`.
