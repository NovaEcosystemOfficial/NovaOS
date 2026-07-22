# Boot Foundation — NovaOS

**Sprint 4 — Prima build avviabile**  
**Milestone:** 0.1 (`novaos-foundation-boot`)  
**Stato:** Specifica operativa ufficiale (pre-implementazione della pipeline)  
**Lingua:** italiano

Progettazione della **prima ISO/avvio reale** di NovaOS sul PC di sviluppo.  
Niente Ryuk, niente Nova AI, niente Cloud/Store/Apps ecosistema in questo taglio.

## Scope Milestone 0.1

Boot corretto · Logo NovaOS · Login personalizzato · Nova Shell iniziale · Terminale · Impostazioni · Spegnimento/Riavvio

## Indice

| # | Documento | Contenuto |
|---|-----------|-----------|
| 01 | [`01-Build-Pipeline.md`](01-Build-Pipeline.md) | Pipeline di build e stages |
| 02 | [`02-Boot-Flow.md`](02-Boot-Flow.md) | Flusso power-on → desktop |
| 03 | [`03-System-Services.md`](03-System-Services.md) | Servizi ammessi/esclusi |
| 04 | [`04-File-System.md`](04-File-System.md) | Layout path branding/rootfs |
| 05 | [`05-Installer.md`](05-Installer.md) | Live + installer strategy |
| 06 | [`06-ISO-Build.md`](06-ISO-Build.md) | Ricetta ISO e roadmap step I1–I9 |
| 07 | [`07-Hardware-Support.md`](07-Hardware-Support.md) | x86_64, reference PC/VM |
| 08 | [`08-Development-Environment.md`](08-Development-Environment.md) | Host di build |
| 09 | [`09-Testing-Strategy.md`](09-Testing-Strategy.md) | Tier 0–3 e checklist |
| 10 | [`10-Milestone-0.1.md`](10-Milestone-0.1.md) | DoD e freeze scope |

## Roadmap tecnica sintetica → prima ISO

```text
Env → Vanilla boot → Branding/Splash → SDDM Nova → Shell defaults
  → Terminal/Settings → Power actions → USB on Reference PC → M0.1
```

Dettaglio step: `06-ISO-Build.md` (I1–I9) e `10-Milestone-0.1.md` (Wave 0–4).

## Relazioni

- Stack: [`../adr/`](../adr/README.md)  
- UI target: [`../design-system/`](../design-system/README.md)  
- Architettura lunga (non M0.1): [`../platform/`](../platform/README.md)
