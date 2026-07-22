# 04 — Nova AI Core

**AI Orchestration Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire **Nova AI Core** come **orchestratore dell’intelligenza artificiale** di NovaOS: unico punto di routing, policy, provider adapter e osservabilità per ogni richiesta AI proveniente da Ryuk, Nova Shell, Nova SDK e app native.

Nova AI Core **non** è l’assistente conversazionale (quello è Ryuk).  
Nova AI Core **non** è un modello. È il **piano di controllo** dell’AI di sistema.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Orchestrazione | Pianificare quale provider/modello usare |
| Routing | Locale (Ollama) vs cloud opzionale |
| Policy | Consensi, retention, redaction, rate limit |
| Providers | Adapter Ollama, OpenAI, Gemini, futuri |
| Context packing | Assemblare contesto autorizzato |
| Tool gateway | Esporre tool/skill execution in modo mediato |
| Quota & cost | Budget cloud, limiti locali risorse |
| Health | Stato provider, fallback, degraded mode |
| Audit | Traccia richieste/esiti senza leak di contenuto sensibile di default |

### Non responsabilità

- UX conversazionale persistente (Ryuk)
- Controllo diretto finestre (Shell API)
- Training di modelli fondazionali
- Bypass security (deve invocarle)

---

## 3. Architettura

```text
                    ┌──────────────────┐
   Ryuk / SDK / App │  platform.ai.v1  │
                    └────────┬─────────┘
                             ▼
┌──────────────────── Nova AI Core ────────────────────┐
│  API Gateway                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ AuthN/Z  │ │ Policy   │ │ Context Builder      │  │
│  │          │ │ Engine   │ │                      │  │
│  └──────────┘ └──────────┘ └──────────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ Router   │ │ Memory   │ │ Tool / Skill Bridge  │  │
│  │          │ │ (opt-in) │ │ (via Ryuk/Services)  │  │
│  └──────────┘ └──────────┘ └──────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │              Provider Adapters                 │  │
│  │   Ollama Local │ OpenAI │ Gemini │ Custom…     │  │
│  └────────────────────────────────────────────────┘  │
│  Audit · Metrics · Model Registry                    │
└──────────────────────────────────────────────────────┘
```

### Componenti

| Componente | Funzione |
|------------|----------|
| **API Gateway** | `platform.ai.v1` |
| **AuthN/Z** | Identità chiamante + capability token |
| **Policy Engine** | Locale-only / hybrid / cloud; data classes |
| **Router** | Scelta provider per task profile |
| **Context Builder** | Prompt/context filtrato dai permessi |
| **Model Registry** | Modelli approvati, hash, size, device profile |
| **Provider Adapters** | Traduzione richiesta ↔ vendor |
| **Tool Bridge** | Non esegue side-effect OS da solo: chiede a Ryuk/Services |
| **Audit Writer** | Eventi su `platform.audit` |

---

## 4. Flusso di comunicazione

### 4.1 Completion da Ryuk

```text
Ryuk → ai.Complete(request)
    → AuthZ (ryuk.assistant)
    → Policy (hybrid? consent?)
    → Router → Ollama oppure Cloud Adapter
    → Response stream → Ryuk
    → Audit(meta)
```

### 4.2 Fallback

```text
Cloud fail / offline → Router ripiega su locale se task profile lo consente
                     → altrimenti errore tipizzato AI_UNAVAILABLE
```

### 4.3 App nativa

```text
NovaDocs → SDK → ai.Complete (scope app)
              → Policy può negare tool di sistema
              → Solo capability concesse all’app
```

---

## 5. Dipendenze

| Dipendenza | Motivo |
|------------|--------|
| Ollama (locale) | Runtime default on-device (ADR-007) |
| Cloud adapters | Opzionali |
| Identity / Permissions | AuthZ |
| Config Store | Preferenze NovaAI mode |
| Model Registry storage | Disco modelli |
| Audit Service | Compliance |

**Dipendenti:** Ryuk (primario), SDK/Apps, Shell (stato degraded).

---

## 6. API interne — `platform.ai.v1`

### Tipi principali (concettuali)

- `TaskProfile`: `chat`, `summarize`, `embed`, `code`, `system_plan`, …
- `ProviderPreference`: `auto`, `local`, `cloud`, `local_only`
- `ContentRef`: riferimento a contesto autorizzato (non dump filesystem arbitrario)

### Metodi

| Metodo | Descrizione |
|--------|-------------|
| `Complete(req) → stream\|message` | Generazione |
| `Embed(texts)` | Embeddings |
| `ListModels()` | Modelli disponibili |
| `GetHealth()` | local/cloud status |
| `GetMode()` / coerente con config | auto/local/cloud/off |
| `Cancel(request_id)` | Annulla |
| `Estimate(req)` | Costo/risorse stimati (best-effort) |

### Errori tipizzati

`DENIED`, `AI_OFF`, `LOCAL_UNAVAILABLE`, `CLOUD_UNAVAILABLE`, `QUOTA_EXCEEDED`, `CONTEXT_DENIED`, `MODEL_MISSING`, `TIMEOUT`.

---

## 7. Ciclo di vita

| Stato | Descrizione |
|-------|-------------|
| Stopped | Servizio non avviato |
| Starting | Carica registry, probe Ollama |
| Ready | Accetta richieste |
| Degraded | Solo locale o solo cloud |
| Off | Mode utente off: rifiuta con `AI_OFF` |
| Updating | Swap modello: coda o reject temporaneo |
| Stopping | Drain stream, flush audit |

Avvio: dopo Identity/Config, prima o in parallelo controllato rispetto a Ryuk (Ryuk aspetta `ai.ready` o degrada).

---

## 8. Politiche di routing (default proposti)

| Condizione | Routing |
|------------|---------|
| Mode Off | Deny |
| Mode Local | Solo Ollama |
| Mode Hybrid + offline | Locale |
| Mode Hybrid + task `system_plan` sensibile | Preferisci locale |
| Mode Hybrid + task heavy + consent cloud | Cloud adapter |
| Dati marcati Sensitive | Mai cloud |

---

## 9. Longevità (10 anni)

- Nuovi provider = nuovo adapter, non nuove API app.
- Model Registry permette di ritirare modelli vecchi.
- Policy Engine versionata (regole come dati).
- Separazione netta da Ryuk evita di riscrivere l’assistente ad ogni cambio vendor.

---

## 10. Riferimenti

- ADR-007
- `05-Ryuk.md`, `09-Security.md`, `08-Nova-SDK.md`
