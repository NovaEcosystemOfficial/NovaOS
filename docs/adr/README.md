# Architecture Decision Records (ADR)

**Progetto:** NovaOS  
**Fase:** Sprint 1 — Decisioni tecniche fondamentali  
**Lingua:** italiano

Questo elenco raccoglie le decisioni architetturali ufficiali del progetto. Ogni ADR valuta alternative multiple e conclude con una **raccomandazione motivata**. Le decisioni restano modificabili solo tramite revisione esplicita dell’ADR e aggiornamento dello stato.

| ID | Titolo | Stato | Raccomandazione sintetica |
|----|--------|-------|---------------------------|
| [ADR-001](ADR-001-Base-Linux.md) | Base Linux | Proposta | Fedora (spin KDE / workstation) |
| [ADR-002](ADR-002-Desktop-Environment.md) | Desktop Environment | Proposta | KDE Plasma |
| [ADR-003](ADR-003-Build-System.md) | Build System | Proposta | KIWI NG (con livemedia-creator come alternativa operativa) |
| [ADR-004](ADR-004-Package-Manager.md) | Package Manager | Proposta | DNF |
| [ADR-005](ADR-005-Display-Manager.md) | Display Manager | Proposta | SDDM |
| [ADR-006](ADR-006-Update-System.md) | Update System | Proposta | DNF nel breve; traiettoria verso rpm-ostree |
| [ADR-007](ADR-007-AI-Architecture.md) | AI Architecture | Proposta | Architettura ibrida (Ollama locale + API cloud) |

## Formato ADR

Ogni documento include:

1. Problema  
2. Alternative valutate  
3. Vantaggi / Svantaggi (per alternativa)  
4. Decisione proposta  
5. Motivazione tecnica  
6. Possibili evoluzioni future  

## Dipendenze tra decisioni

```text
ADR-001 Base Linux
   ├── ADR-002 Desktop
   ├── ADR-003 Build System
   ├── ADR-004 Package Manager
   ├── ADR-005 Display Manager
   └── ADR-006 Update System
ADR-007 AI Architecture (trasversale, ma influenza system/ e ai/)
```

Le raccomandazioni sono **coerenti tra loro**: la scelta della base Linux vincola in larga misura package manager, strumenti di build e percorso aggiornamenti.

## Processo di accettazione

1. Review tecnica del team  
2. Eventuali obiezioni documentate nella sezione “Note di review”  
3. Cambio stato: `Proposta` → `Accettata` / `Deprecata` / `Sostituita da ADR-XXX`
