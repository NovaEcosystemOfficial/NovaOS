# 08 — Nova SDK

**Developer Platform Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire il **Nova SDK**: l’insieme di librerie, schemi, tool e linee guida che consentono di costruire applicazioni e Skills **native** sulla Nova Platform per i prossimi 10 anni.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Client API | Binding stabili verso platform.* |
| Schemi | Tipi Intent, Manifest, Skill, AI request |
| Tooling | Generatori, linter manifest, simulatori |
| Auth helpers | Gestione capability token |
| UI kit (fase successiva) | Componenti allineati Design System |
| Documentazione developer | Contract-first |

### Non responsabilità

- Implementare demoni di sistema
- Sostituire Ryuk
- Esporre backdoor admin alle app

---

## 3. Architettura

```text
┌────────────────────── Nova SDK ──────────────────────┐
│  Language bindings (priorità future da ADR dedicati) │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌───────────────┐  │
│  │ Core   │ │ AI     │ │ Intent │ │ Notify/Id…    │  │
│  │ Client │ │ Client │ │ Client │ │               │  │
│  └────────┘ └────────┘ └────────┘ └───────────────┘  │
│  Schemas (JSON Schema / Protobuf — scelta futura)    │
│  Devtools: nova-cli, manifest check, bus spy         │
└──────────────────────────┬───────────────────────────┘
                           │ IPC sicuro
                    Nova Platform Services
```

---

## 4. Flusso di comunicazione

```text
App code → SDK client → (auth session) → Nova Bus → Service
        ← typed result / stream ←
```

Errori tipizzati unificati (`DENIED`, `UNAVAILABLE`, …) allineati ad AI Core e Permissions.

---

## 5. Componenti SDK

| Pacchetto logico | Contenuto |
|------------------|-----------|
| `nova-sdk-core` | Bus connect, version negotiate, identity |
| `nova-sdk-ai` | Complete/Embed/Cancel wrappers |
| `nova-sdk-intent` | Register/Invoke helpers |
| `nova-sdk-notify` | Post notifications |
| `nova-sdk-app` | Manifest helpers, lifecycle |
| `nova-sdk-skill` | Scaffold Skill (per sviluppatori Skills Ryuk) |
| `nova-cli` | Check, pack, sign (fase packaging) |

---

## 6. Dipendenze

| Dipendenza | Note |
|------------|------|
| Platform API level | Dichiarato dall’app |
| Design System | Per UI kit futuro |
| Security / Permissions | Impliciti in ogni call |

SDK **non** dipende da Ollama SDK vendor nelle app.

---

## 7. API interne esposte (superficie developer)

La superficie pubblica mirror dei contratti:

- `platform.ai.v1` (sottoinsieme app-safe)
- `platform.intent.v1`
- `platform.notify.v1`
- `platform.identity.v1` (read-mostly)
- `platform.capabilities.v1` (discovery)
- `platform.ryuk.v1` — **non** per app generiche; solo componenti di sistema / test harness firmati

Policy: le app non ottengono Shell Driver completo.

---

## 8. Ciclo di vita SDK

| Fase | Policy |
|------|--------|
| Preview | API unstable, feature flag |
| GA `v1` | SemVer strict |
| Deprecation | Warning compile-time/runtime ≥ 18 mesi |
| EOL binding linguaggio | Piano migrazione documentato |

Allineamento: **SDK version** ↔ **Platform API level** matrix pubblicata.

---

## 9. Longevità (10 anni)

- Contract schemas nel repo docs/SDK come source of truth.
- Multi-language bindings dietro stesso schema.
- Compatibility tests in CI quando esisterà codice.
- Niente “god object” SDK: moduli per dominio.

---

## 10. Riferimenti

- `01-Nova-Platform.md`, `07-Nova-Apps.md`, `04-Nova-AI-Core.md`
