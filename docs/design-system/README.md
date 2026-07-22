# Design System — NovaOS / Nova Shell

**Sprint 2 — Identità visiva completa**  
**Stato:** Specifica ufficiale di design (pre-asset, pre-codice)  
**Lingua:** italiano

Questo è il **sistema di design** che guida lo sviluppo futuro di NovaOS. Non contiene immagini, mockup né codice: solo documentazione vincolante.

## Dichiarazione

**Nova Shell** è il desktop ufficiale di NovaOS e il cuore dell’esperienza utente. L’identità deve essere riconoscibile a colpo d’occhio e **non** deve sembrare Windows, macOS o KDE stock.

**Direzione artistica:** *Luminous Precision* — precisione luminosa (campo ink, accento stellar, segnale AI cyan, materiale Nova Glass).

**Nota architetturale (Sprint 3):** Pulse / AI Stage sono superfici UI di Nova Shell che invocano **Ryuk**, assistente nativo implementato come **servizio di sistema** (non come applicazione). L’orchestrazione dei modelli spetta a **Nova AI Core**. Dettaglio: [`../platform/`](../platform/README.md).

## Indice dei documenti

| # | Documento | Contenuto |
|---|-----------|-----------|
| 01 | [`01-Brand.md`](01-Brand.md) | Filosofia, personalità, naming, art direction |
| 02 | [`02-Color-Palette.md`](02-Color-Palette.md) | Palette, temi chiaro/scuro, glass, blur |
| 03 | [`03-Typography.md`](03-Typography.md) | Nova Sans / Display / Mono, scale, pesi |
| 04 | [`04-Icons.md`](04-Icons.md) | Nova Icons, griglia, metafore |
| 05 | [`05-Desktop-Layout.md`](05-Desktop-Layout.md) | Nova Shell: bar, launcher, finestre, centri |
| 06 | [`06-Animations.md`](06-Animations.md) | Motion tokens, easing, AI pulse |
| 07 | [`07-Boot-Experience.md`](07-Boot-Experience.md) | Boot, login, onboarding |
| 08 | [`08-Sound-Design.md`](08-Sound-Design.md) | Identità sonora e catalogo eventi |
| 09 | [`09-Design-Principles.md`](09-Design-Principles.md) | Dieci principi vincolanti |
| 10 | [`10-User-Experience.md`](10-User-Experience.md) | Flussi, pattern, gate UX |

## Promesse che il design deve trasmettere

Eleganza · Velocità · Minimalismo · Tecnologia · Intelligenza artificiale · Affidabilità

## Cosa non include Sprint 2

- File immagine / logo esportati  
- Mockup Figma/Sketch obbligatori  
- Codice di Nova Shell  
- Asset audio finali  

La produzione asset avverrà in `branding/` nelle fasi successive, **in conformità** a questi documenti.

## Relazioni

- Linee guida precedenti: [`../ui-guidelines.md`](../ui-guidelines.md)
- ADR stack tecnico: [`../adr/`](../adr/README.md)
- Destinazione asset: [`../../branding/`](../../branding/README.md)
