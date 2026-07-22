# Platform Architecture — NovaOS

**Sprint 3 — Architettura software**  
**Stato:** Specifica ufficiale (pre-implementazione, nessun codice)  
**Orizzonte:** mantenibilità a 10 anni  
**Lingua:** italiano

Documentazione tecnica dell’architettura software di piattaforma.  
Non contiene codice né SDK implementati: solo contratti, confini e cicli di vita.

## Mappa dei componenti

```text
Nova Apps ──► Nova SDK ──► Nova Services / AI Core
                 │
Nova Shell ◄─────┼──────── Ryuk (system service, NON un’app)
                 │
              NovaOS (system layer)
                 │
           Linux Foundation
```

| Ruolo chiave | Componente |
|--------------|------------|
| Contratto globale | **Nova Platform** |
| Orchestratore AI | **Nova AI Core** |
| Assistente nativo OS | **Ryuk** (servizio di sistema) |
| Desktop | **Nova Shell** |

## Indice

| # | Documento | Contenuto |
|---|-----------|-----------|
| 01 | [`01-Nova-Platform.md`](01-Nova-Platform.md) | Layer, bus, API platform, longevità |
| 02 | [`02-NovaOS.md`](02-NovaOS.md) | System layer, session, update, config |
| 03 | [`03-Nova-Shell.md`](03-Nova-Shell.md) | Experience layer e `platform.shell` |
| 04 | [`04-Nova-AI-Core.md`](04-Nova-AI-Core.md) | Orchestratore AI, provider, policy |
| 05 | [`05-Ryuk.md`](05-Ryuk.md) | Assistente sistema, Skills, controllo Shell/Apps |
| 06 | [`06-Nova-Services.md`](06-Nova-Services.md) | Identity, intent, notify, audit, … |
| 07 | [`07-Nova-Apps.md`](07-Nova-Apps.md) | App native ecosistema e intent |
| 08 | [`08-Nova-SDK.md`](08-Nova-SDK.md) | SDK e superficie developer |
| 09 | [`09-Security.md`](09-Security.md) | Trust, AuthZ, AI/Ryuk/Skills security |
| 10 | [`10-Boot-Sequence.md`](10-Boot-Sequence.md) | Boot, sessione, shutdown, failure |

## Vincoli Sprint 3

- Nessuna implementazione codice  
- Nessuna ISO  
- Allineamento ad ADR, Design System e visione esistenti  

## Relazioni

- ADR: [`../adr/`](../adr/README.md)
- Design System / Nova Shell UX: [`../design-system/`](../design-system/README.md)
- Architettura high-level: [`../architecture.md`](../architecture.md)
