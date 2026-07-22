# `ai/`

Componenti e servizi di intelligenza artificiale di sistema.

## Responsabilità previste

- **Nova AI Core** — orchestratore AI di piattaforma (routing, policy, provider)
- Adapter locali (Ollama) e cloud opzionali
- Model registry, health, audit di inferenza
- Supporto a **Ryuk** e alle app native via `platform.ai.v1`

## Cosa non vive qui

- **Ryuk** (assistente nativo) è un **servizio di sistema** documentato in platform; il codice futuro potrà vivere sotto `system/` o unità dedicate, non come app in `apps/`.
- UI Pulse / AI Stage appartengono a Nova Shell (`desktop/`).

## Specifica

**[`docs/platform/04-Nova-AI-Core.md`](../docs/platform/04-Nova-AI-Core.md)**  
**[`docs/platform/05-Ryuk.md`](../docs/platform/05-Ryuk.md)**

## Stato — Sprint 3

Architettura documentata. **Nessun codice.** Implementazione prevista da Fase 2 — System Core in poi.
