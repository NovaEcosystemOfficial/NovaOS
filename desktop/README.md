# `desktop/`

Ambiente desktop di NovaOS: **Nova Shell** (Experience Layer).

## Responsabilità previste

- Sessione grafica e shell desktop secondo Design System
- Horizon Bar, Launcher, Notification Center, Control Center, NovaAI Stage
- Impostazioni di sistema lato UI
- Integrazione con primitive AI di sistema
- Coerenza con branding e Design System

## Implementato (fondazioni)

| Path | Sprint | Descrizione |
|------|--------|-------------|
| [`nova-update/`](nova-update/README.md) | 15 | GUI **Nova Update** (GTK + `.desktop`) |
| [`nova-center/`](nova-center/README.md) | 16–17 | Pannello di controllo **Nova Center** (`center.v1`, Wi-Fi dettagliato) |

## Specifica di design

**[`docs/design-system/`](../docs/design-system/README.md)** — in particolare `05-Desktop-Layout.md` e `10-User-Experience.md`.

Upstream tecnico di riferimento (ADR-002): Plasma come base; **l’identità utente è Nova Shell**, non KDE stock.
