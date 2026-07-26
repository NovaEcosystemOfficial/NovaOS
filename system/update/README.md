# `system/update/` — Nova Update Foundation (Sprint 15)

Update Broker ufficiale di NovaOS.

| Artefatto | Descrizione |
|-----------|-------------|
| `nova_update/` | Libreria Python condivisa (`system.update.v1`) |
| `bin/nova-updated` | Demone Update Broker |
| `bin/nova-updater` | Entry point CLI (wrapper; packaging installa in `/usr/bin`) |
| `systemd/nova-updated.service` | Unità systemd |
| `conf/nova-update.conf` | Config di default |

## Quick start (dev)

```bash
# Terminale 1 — demone in mock (nessun root)
NOVA_UPDATE_STATE_DIR=/tmp/nova-update-state \
NOVA_UPDATE_SOCKET=/tmp/nova-update.sock \
./system/update/bin/nova-updated --backend mock --foreground

# Terminale 2 — CLI
NOVA_UPDATE_SOCKET=/tmp/nova-update.sock \
./shell/nova-updater/nova-updater status
./shell/nova-updater/nova-updater check
./shell/nova-updater/nova-updater channel set beta
```

## Image integration

`scripts/build-iso.sh` stages this tree into the KIWI `root/` overlay so every
new live/installable image includes Nova Update without manual setup:

- `/usr/libexec/nova-updated` + systemd unit (enabled)
- `/usr/bin/nova-updater`, `/usr/bin/nova-update-gui`
- `/etc/yum.repos.d/novaos-*.repo` + `/etc/pki/novaos/RPM-GPG-KEY-novaos`
- `/usr/share/applications/org.novaos.Update.desktop`

See [`docs/platform/11-Nova-Update.md`](../../docs/platform/11-Nova-Update.md).
