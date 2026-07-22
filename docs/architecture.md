# Architettura di NovaOS

**Documento di architettura di riferimento**  
**Stato:** high-level + dettaglio in [`platform/`](platform/README.md) (Sprint 3)  
**Lingua:** italiano

---

## 1. Scopo e limiti

Questo documento descrive l’**architettura di riferimento** di NovaOS: layer, confini, responsabilità e principi di evoluzione.

In Sprint 0 **non** si seleziona ancora la distribuzione Linux, **non** si definiscono package concreti e **non** si implementa codice di sistema. Si fissa il modello mentale con cui il team prenderà decisioni nelle fasi successive.

---

## 2. Dichiarazione architetturale

> NovaOS è un sistema operativo basato su Linux, organizzato a layer, in cui i componenti Nova sostituiscono progressivamente equivalenti standard. **Nova AI Core** orchestra l’AI di piattaforma; **Ryuk** è l’assistente nativo come **servizio di sistema** (non un’applicazione); **Nova Shell** è l’experience desktop.

### Implicazioni

- Si parte da una base Linux (scelta in Fase 1).
- Si introduce un **Platform Layer** Nova sopra i servizi tradizionali.
- Desktop, shell e installer sono **Experience Layer** Nova.
- Le app dell’ecosistema consumano contratti stabili, non hook impropri.

---

## 3. Vista a layer

```text
┌─────────────────────────────────────────────────────────────┐
│                 ECOSYSTEM APPS (native)                     │
│  NovaDocs · NovaStudio · NovaPromo · NovaBeauty · NovaSky   │
├─────────────────────────────────────────────────────────────┤
│                 EXPERIENCE LAYER                            │
│              Nova Shell · Greeter · Installer UX            │
├─────────────────────────────────────────────────────────────┤
│                 ASSISTANT LAYER                             │
│              Ryuk (system service) · Skills                 │
├─────────────────────────────────────────────────────────────┤
│                 PLATFORM LAYER (Nova)                       │
│   Nova AI Core · Services (identity/intent/notify/…) · SDK  │
├─────────────────────────────────────────────────────────────┤
│                 SYSTEM LAYER (NovaOS)                       │
│    session · updates · config · device · security baselines │
├─────────────────────────────────────────────────────────────┤
│                 LINUX FOUNDATION                            │
│         kernel · init · userspace · packaging base          │
└─────────────────────────────────────────────────────────────┘
```

Dettaglio contratto e API: **[`platform/`](platform/README.md)**.

| Layer | Responsabilità | Directory di progetto (oggi) |
|-------|----------------|------------------------------|
| Ecosystem Apps | Prodotti nativi Nova | `apps/` |
| Experience | UI di sistema e onboarding | `desktop/`, `shell/`, `installer/`, `branding/` |
| Assistant | Ryuk (system service) + Skills | `system/` (unità dedicate) |
| Platform | Nova AI Core, Services, SDK | `ai/`, contratti in `docs/platform/` |
| System | Servizi e policy di OS | `system/` |
| Linux Foundation | Base OS (Fedora per ADR-001) | (esterna / Fase 1) |

---

## 4. Contesti delimitati (bounded contexts)

### 4.1 `system/` — System Core

Responsabile di:

- ciclo di vita sessione utente;
- aggiornamenti e canali di release;
- configurazione di sistema;
- integrazioni device/hardware a livello OS;
- baseline di sicurezza e hardening.

Non responsabile di:

- UI desktop completa;
- logica di business delle app ecosistema;
- modelli AI.

### 4.2 `ai/` — Nova AI Core

Responsabile di:

- **orchestrazione** AI di piattaforma (non l’assistente conversazionale);
- adapter locali (Ollama) e cloud opzionali;
- policy di consenso, privacy, routing e audit di inferenza;
- model registry e health.

Non responsabile di:

- dialogo assistente e Skills (**Ryuk**, servizio di sistema);
- UI Pulse / AI Stage (**Nova Shell**);
- storage cloud utente (collabora con NovaCloud / Sync Service).

Vedi: [`platform/04-Nova-AI-Core.md`](platform/04-Nova-AI-Core.md), [`platform/05-Ryuk.md`](platform/05-Ryuk.md).

### 4.3 `desktop/`, `shell/`, `installer/` — Experience

Responsabili di:

- interazione utente quotidiana;
- coerenza con UI guidelines e branding;
- onboarding e recovery UX;
- superfici di invocazione AI contestuale.

### 4.4 `apps/` — Ecosystem Native Apps

Responsabili di:

- packaging e integrazioni delle app Nova;
- uso delle Platform API;
- allineamento ai contratti di natività.

### 4.5 `branding/` e `docs/`

Responsabili di:

- identità e standard (branding);
- verità di progetto e decisioni (docs).

### 4.6 `.github/` e `scripts/`

Responsabili di:

- automazioni CI/CD e template di collaborazione;
- script di supporto a build/dev/ops (senza diventare “il prodotto”).

---

## 5. Piattaforma: contratti fondamentali

L’architettura prevede, nel tempo, un insieme di **contratti di piattaforma**. In Sprint 0 sono definiti solo come interfacce concettuali.

### 5.1 Identity & Profile

- sessione utente Nova;
- collegamento opzionale a NovaCloud;
- preferenze di sistema e consenso AI.

### 5.2 Capabilities Registry

- registro delle capacità disponibili (AI, sync, printer, intent handlers, …);
- discovery per app native.

### 5.3 Intent & Navigation

- invocare azioni tra app/sistema (“apri documento”, “genera bozza”, “avvia installazione”).

### 5.4 NovaAI System API

- richieste di completamento/embedding/tool-calling;
- contesto di sistema governato (non accesso illimitato arbitrario);
- modalità locale/cloud con policy esplicite.

### 5.5 NovaCloud Services

- auth, sync, backup, device pairing;
- feature flags e configurazione remota (se adottati, con trasparenza).

### 5.6 Update & Packaging

- aggiornamento OS e componenti Nova;
- canali (stable/beta/dev);
- firma e verificabilità.

### 5.7 Permissions & Security

- modello permessi per app e agent AI;
- least privilege;
- audit trail per azioni sensibili.

---

## 6. Flussi architetturali di riferimento

### 6.1 Avvio sessione (target)

```text
Boot (Linux Foundation)
  → System Layer (sessione, policy)
    → Experience Layer (desktop/shell)
      → Platform Layer ready (AI/Cloud)
        → Ecosystem Apps disponibili
```

### 6.2 Richiesta AI da un’app nativa (target)

```text
App (es. NovaDocs)
  → Platform API (NovaAI)
    → Policy/Permissions
      → Runtime locale e/o NovaCloud
        → Risposta + audit/log consentito
```

### 6.3 Installazione (target)

```text
Installer Nova
  → Setup disco/utente
    → Bootstrap System Layer
      → Opzioni NovaCloud / NovaAI
        → First-run Experience
```

Questi flussi sono **target**: guidano il design, non descrivono un’implementazione esistente.

---

## 7. Strategia di sostituzione progressiva

NovaOS adotta un modello di **strangler architecture** applicato al sistema operativo:

1. **Wrap** — integrare componenti standard dietro interfacce Nova.
2. **Replace** — sostituire il componente quando la versione Nova è pronta.
3. **Retire** — rimuovere dipendenze legacy non più necessarie.

### Esempi (non decisioni vincolanti)

| Area | Stato iniziale tipico | Evoluzione Nova |
|------|------------------------|-----------------|
| Desktop environment | Componente upstream | Desktop Nova |
| Shell | Shell standard | Shell Nova + AI assist |
| Installer | Installer della base | Installer Nova |
| Assistente | Assente / app esterna | NovaAI di sistema |
| Sync | Manuale / terze parti | NovaCloud nativo |

Ogni sostituzione richiederà un ADR e criteri di qualità (UX, performance, sicurezza, manutenibilità).

---

## 8. Qualità architetturali (atributi non funzionali)

| Attributo | Obiettivo |
|-----------|-----------|
| **Evolvibilità** | Layer e contratti permettono cambio componenti senza riscrivere tutto |
| **Sicurezza** | Permessi espliciti, firma aggiornamenti, isolamento AI tools |
| **Privacy** | Consenso chiaro; locale-first dove possibile |
| **Usabilità** | Experience coerente; AI utile e controllabile |
| **Affidabilità** | Update robusti; recovery; ridotta fragilità |
| **Performance** | AI e servizi non devono degradare l’OS base |
| **Osservabilità** | Log/audit mirati; diagnostica per supporto |
| **Compatibilità** | Rispetto ecosystem Linux finché necessario |

---

## 9. Decisioni tecniche (Sprint 1 — ADR)

Le decisioni di piattaforma sono documentate come Architecture Decision Records in [`adr/`](adr/README.md). Sintesi delle **proposte** correnti:

| Tema | ADR | Proposta |
|------|-----|----------|
| Base Linux | [ADR-001](adr/ADR-001-Base-Linux.md) | Fedora (riferimento KDE) |
| Desktop | [ADR-002](adr/ADR-002-Desktop-Environment.md) | KDE Plasma |
| Build immagini | [ADR-003](adr/ADR-003-Build-System.md) | KIWI NG |
| Package manager | [ADR-004](adr/ADR-004-Package-Manager.md) | DNF |
| Display manager | [ADR-005](adr/ADR-005-Display-Manager.md) | SDDM |
| Update | [ADR-006](adr/ADR-006-Update-System.md) | DNF → traiettoria rpm-ostree |
| AI | [ADR-007](adr/ADR-007-AI-Architecture.md) | Ibrida (Ollama + cloud adapters) |

Ancora differite a fasi successive (non bloccanti per lo stack base):

- init system specifics oltre al modello layer;
- linguaggio principale dei demoni di sistema;
- dettagli OEM/OTA di produzione;
- design system token completi in `branding/`.

Le ADR restano in stato *Proposta* finché il team non le accetta formalmente.
---

## 10. Mappa repository ↔ architettura

```text
NovaOS/
├── .github/       → automazione e governance engineering
├── docs/          → architettura, visione, roadmap, UI
├── branding/      → asset e sistemi di identità
├── desktop/       → Experience: desktop
├── shell/         → Experience: CLI/TUI
├── installer/     → Experience: setup/onboarding
├── apps/          → Ecosystem native apps
├── ai/            → Platform: NovaAI
├── system/        → System Layer
└── scripts/       → tooling di supporto
```

Questa mappa è vincolante per l’organizzazione del codice futuro: **il codice dovrà rispettare i confini**, non il contrario.

---

## 11. Governance delle decisioni architetturali

A partire dalla Fase 1 si raccomanda:

- ADR numerati in `docs/adr/`;
- review architetturale per cambiamenti cross-layer;
- aggiornamento di questo documento ad ogni evoluzione di layer o contratto.

### Template minimo ADR (futuro)

1. Titolo e stato  
2. Contesto  
3. Decisione  
4. Conseguenze  
5. Alternative scartate  

---

## 12. Relazione con l’ecosistema Nova

L’architettura tratta i prodotti Nova come **cittadini della piattaforma**:

- non devono reimplementare identity/AI/sync ciascuno per conto proprio;
- devono integrarsi via Platform Layer;
- possono estendere capability registry con handler di dominio;
- restano versionati e rilasciabili, ma con contratto di natività verso NovaOS.

NovaOS non è un “negozio di app”: è il **runtime di prodotto** dell’ecosistema.

---

## 13. Sintesi

L’architettura di NovaOS è deliberatamente **a layer**, **a sostituzione progressiva** e **centrata su contratti di piattaforma**.

Sprint 0 congela questo modello. Le fasi successive lo implementano, una decisione alla volta, senza tradire la visione: un vero sistema operativo AI-First, non una distro personalizzata.
