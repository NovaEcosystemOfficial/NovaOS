# `nova-updater`

CLI ufficiale per il sistema di aggiornamento NovaOS (Sprint 15).

Parla con il demone **`nova-updated`** tramite il socket Unix configurato
(`/run/nova/update.sock` in produzione).

## Comandi

```bash
nova-updater status
nova-updater check
nova-updater apply
nova-updater channel get
nova-updater channel set stable|beta|developer|nightly
nova-updater verify
nova-updater progress
nova-updater ping
```

## Dev

```bash
NOVA_UPDATE_SOCKET=/tmp/nova-update.sock ./shell/nova-updater/nova-updater status
```

Specifica: [`docs/platform/11-Nova-Update.md`](../../docs/platform/11-Nova-Update.md)
