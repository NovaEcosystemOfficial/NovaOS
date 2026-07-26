# `system/`

Componenti di sistema, servizi core e (in prospettiva) unità come **Ryuk**.

## Responsabilità previste

- Session, update, config, device, policy (NovaOS system layer)
- Service Supervisor e target di boot
- Ospitare servizi di sistema documentati in `docs/platform/` (incl. Ryuk come system service)

## Implementato

| Path | Sprint | Descrizione |
|------|--------|-------------|
| [`update/`](update/README.md) | 15 | **nova-updated** — Update Broker (`system.update.v1`) |

## Specifica

- [`docs/platform/02-NovaOS.md`](../docs/platform/02-NovaOS.md)
- [`docs/platform/11-Nova-Update.md`](../docs/platform/11-Nova-Update.md)
- [`docs/platform/05-Ryuk.md`](../docs/platform/05-Ryuk.md)
- [`docs/platform/06-Nova-Services.md`](../docs/platform/06-Nova-Services.md)
- [`docs/platform/10-Boot-Sequence.md`](../docs/platform/10-Boot-Sequence.md)
