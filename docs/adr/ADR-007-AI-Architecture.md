# ADR-007 — AI Architecture

| Campo | Valore |
|-------|--------|
| **ID** | ADR-007 |
| **Titolo** | Architettura di intelligenza artificiale di sistema |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | Trasversale (`ai/`, `system/`, ecosystem NovaAI) |
| **Influenza** | Privacy, Platform API, Experience Layer, app native |

---

## 1. Problema

NovaOS è un sistema operativo **AI-First**: l’intelligenza artificiale deve essere una capacità di piattaforma, non un chatbot installato a parte. Prima di implementare `ai/`, occorre decidere l’architettura di runtime:

- dove girano i modelli (dispositivo vs cloud);
- quali provider esterni sono ammessi;
- come si garantiscono privacy, consenso e degradazione elegante offline;
- come le app native (NovaDocs, NovaStudio, …) consumano AI senza reimplementarla.

Le opzioni considerate spaziano da solo-locale a solo-cloud, fino a un modello ibrido.

---

## 2. Alternative valutate

### 2.1 Ollama locale (solo on-device)

Runtime locale per modelli LLM/VLM, tipicamente via API locale, adatto a offline e privacy-first.

### 2.2 OpenAI API (solo cloud)

Inferenza remota tramite API OpenAI; qualità elevata, dipendenza di rete e policy dati esterne.

### 2.3 Gemini API (solo cloud)

Inferenza remota tramite API Google Gemini; caratteristiche analoghe sul piano architetturale (cloud provider), con differenze di modello/prezzo/ecosistema.

### 2.4 Architettura ibrida

Layer NovaAI di sistema che instrada le richieste verso runtime locale (es. Ollama) e/o provider cloud (OpenAI, Gemini, altri) in base a policy, capability, consenso utente e stato rete.

---

## 3. Analisi vantaggi / svantaggi

### Ollama locale (only)

| Vantaggi | Svantaggi |
|----------|-----------|
| Privacy e offline reali | Qualità/limiti legati a HW utente |
| Nessun costo API variabile per uso base | Modelli grandi esclusi su macchine entry-level |
| Controllo supply chain modelli (con policy) | Manutenzione modelli, GPU/NPU drivers, storage |
| Allineato a “AI di sistema” anche senza account | Feature avanzate (tool lunghi, multimodal top-tier) più deboli |
| Ideale per dati sensibili on-device | UX delusa se presentato come unico motore “sempre al top” |

### OpenAI API (only)

| Vantaggi | Svantaggi |
|----------|-----------|
| Qualità all’avanguardia, time-to-capability alto | Soft-dependency da rete e vendor |
| Operazioni ridotte sul device | Privacy/compliance da gestire con attenzione |
| Ideale per picchi di complessità | Costi per-token a scala |
| Buona maturità tooling | OS inutilizzabile in modalità AI se offline → viola UI guidelines |
| | Vendor lock-in se le app chiamano OpenAI direttamente |

### Gemini API (only)

| Vantaggi | Svantaggi |
|----------|-----------|
| Alternativa cloud competitiva | Stessi limiti strutturali del cloud-only |
| Integrazione possibile con ecosystem Google | Policy dati e regioni da governare |
| Buon fit multimodale in certi scenari | Non risolve offline/privacy locale |
| | Stesso rischio di bypass del Platform Layer |

> Nota: OpenAI e Gemini sono valutati come **rappresentanti della classe “cloud provider”**. La decisione architetturale non è “quale brand cloud vince in eterno”, ma se il sistema può dipendere da un solo cloud.

### Architettura ibrida

| Vantaggi | Svantaggi |
|----------|-----------|
| Locale per default sensibili / offline; cloud per potenza | Maggiore complessità di routing, policy e test |
| Evita vendor lock-in singolo | Serve astrazione API stabile (NovaAI System API) |
| Consente UX degradata elegante senza rete | Configurazione utente più ricca (da progettare bene) |
| Allinea NovaCloud (account, quota) e on-device | Rischio di “due cervelli” incoerenti se non unificati in UX |
| Compatibile con visione AI-First di piattaforma | Osservabilità e audit più impegnativi |

---

## 4. Decisione proposta

**Raccomandazione: adottare un’architettura AI ibrida mediata dal Platform Layer NovaAI.**

### Principi operativi

1. **Nessuna app nativa parla direttamente** con Ollama/OpenAI/Gemini in modo non governato.  
   Tutte passano da **NovaAI System API** (`ai/`).

2. **Runtime locale di riferimento iniziale:** Ollama (o equivalente compatibile approvato), per inference on-device.

3. **Provider cloud ammessi (classe):** almeno uno tra OpenAI API e Gemini API nella prima fase di integrazione cloud; l’architettura deve permettere **multi-provider** tramite adapter.

4. **Policy di default (proposta prodotto):**  
   - task leggeri / dati locali sensibili → preferisci locale;  
   - task che richiedono modelli top / tool cloud → cloud solo con consenso e rete;  
   - offline → locale only; feature cloud chiaramente non disponibili.

5. **Fail-open rispetto al sistema:** se AI non è disponibile, NovaOS resta usabile (principio già in `ui-guidelines.md`).

---

## 5. Motivazione tecnica

1. **AI-First ≠ Cloud-Only**  
   Un sistema operativo che smette di “essere intelligente” senza rete non è una capacità di sistema: è un servizio remoto con skin locale. Il locale è obbligatorio per credibilità OS.

2. **AI-First ≠ Solo-Local**  
   Promettere solo Ollama condanna l’esperienza sui device non top e limita l’ecosistema (NovaStudio, NovaPromo, ecc.) rispetto a competitor cloud-augmented. L’ibrido è pragmatico.

3. **Platform Layer come vera decisione**  
   La scelta strategica non è “Ollama vs OpenAI vs Gemini”, è **introdurre un broker di sistema** con:
   - autenticazione/consent;
   - routing;
   - limiti di risorsa;
   - audit;
   - capability discovery per le app.

4. **Perché Ollama come motore locale iniziale**  
   - API semplice, adozione ampia, buon fit desktop Linux;  
   - sostituibile dietro interfaccia NovaAI se domani si preferisce un altro runtime (llama.cpp server, vLLM, vendor NPU, …).

5. **Perché non scegliere un solo cloud vendor come fondazione**  
   OpenAI-only o Gemini-only creano lock-in e single point of policy failure. Entrambi restano **adapter validi**, non “il cervello del sistema”.

6. **Allineamento ecosistema**  
   NovaAI è prodotto e layer; NovaCloud fornisce identità/quota/sync policy; le app consumano primitive, non SDK vendor sparsi.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **Model registry Nova** | Catalogo modelli approvati on-device + firma | System Core |
| **NPU/GPU acceleration profiles** | Profili HW ufficiali | Con device target |
| **Provider aggiuntivi** | Anthropic, Azure OpenAI, endpoint self-hosted | Per policy/mercato |
| **Agent di sistema con permessi** | Tool che agiscono su OS con conferma | Fase AI-First OS |
| **Federated / private cloud Nova** | Inferenza su infra NovaCloud propria | NovaCloud maturo |
| **Sostituzione Ollama** | Runtime locale alternativo senza breaking API app | Se KPI lo richiedono |
| **Policy pack per verticali** | NovaBeauty/NovaSky con regole dominio | Ecosystem Native |

---

## 7. Conseguenze

### Positive

- Coerente con visione OS AI-First e UI guidelines.
- Privacy e potenza non sono mutuamente esclusive.
- App ecosistema disaccoppiate dai vendor.

### Negative / rischi

- Complessità di implementazione superiore al singolo backend.
- UX da curare per evitare confusione “quale modello mi sta rispondendo?”.
- Costi cloud da misurare e mostrare con trasparenza.

### Mitigazioni

- API unica + indicatori UI di modalità (locale/cloud).
- Telemetria privacy-first e opt-in.
- Test matrix: offline, online, denied consent, quota exceeded.
- Budget e rate limit di piattaforma.

---

## 8. Schema logico (target)

```text
App native / Desktop / Shell
        │
        ▼
┌───────────────────────────┐
│   NovaAI System API       │
│  auth · policy · routing  │
└───────────┬───────────────┘
            │
     ┌──────┴──────┐
     ▼             ▼
 Local Runtime   Cloud Adapters
 (Ollama …)      (OpenAI / Gemini / …)
     │             │
     └──────┬──────┘
            ▼
     Audit / Quota / UX signals
```

---

## 9. Riferimenti

- [`../vision.md`](../vision.md)
- [`../architecture.md`](../architecture.md) — Platform Layer / NovaAI
- [`../ui-guidelines.md`](../ui-guidelines.md) — AI controllabile e fail-safe
- [`../roadmap.md`](../roadmap.md) — Fasi 2 e 5
- Directory di progetto: `ai/`

---

## 10. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
