# 01 — Nova Platform

**NovaOS Platform Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica architetturale ufficiale (pre-implementazione)  
**Orizzonte:** progettazione a 10 anni

---

## 1. Scopo

Definire **Nova Platform**: il contratto di piattaforma su cui poggiano NovaOS, Nova Shell, Nova AI Core, Ryuk, i servizi di sistema e le applicazioni native dell’ecosistema Nova.

Nova Platform non è un singolo processo: è l’**insieme stabile di layer, bus, API e garanzie** che permette di evolvere componenti per un decennio senza riscrivere l’ecosistema.

---

## 2. Responsabilità

| Responsabilità | Descrizione |
|----------------|-------------|
| Contratti stabili | Versionare API pubbliche/interne con politica di compatibilità |
| Isolamento | Separare kernel/userland base, system services, experience, AI, apps |
| Orchestrazione | Definire chi parla con chi (bus, capability, identity) |
| Estendibilità | Skills, plugin, app native senza fork del core |
| Osservabilità | Log, audit, metriche, tracing cross-componente |
| Sicurezza | Confini di trust, least privilege, attestation |
| Longevità | Preferire interfacce evolutive a dipendenze monolitiche |

### Non responsabilità

- Implementare UI di Nova Shell
- Scegliere modelli LLM specifici in modo permanente
- Sostituire il kernel Linux

---

## 3. Architettura a layer (vista decennale)

```text
┌─────────────────────────────────────────────────────────────────┐
│  NOVA APPS          NovaDocs · Studio · Promo · Beauty · Sky …  │
├─────────────────────────────────────────────────────────────────┤
│  NOVA SDK           Client libraries · Tooling · Schemas        │
├─────────────────────────────────────────────────────────────────┤
│  EXPERIENCE         Nova Shell · Greeter · Installer surfaces   │
├─────────────────────────────────────────────────────────────────┤
│  ASSISTANT LAYER    Ryuk (system service) · Skills runtime      │
├─────────────────────────────────────────────────────────────────┤
│  AI ORCHESTRATION   Nova AI Core (router, policy, providers)    │
├─────────────────────────────────────────────────────────────────┤
│  NOVA SERVICES      Identity · Sync · Notify · Update · Intent… │
├─────────────────────────────────────────────────────────────────┤
│  NOVAOS SYSTEM      Session · Device · Config · Security agents │
├─────────────────────────────────────────────────────────────────┤
│  LINUX FOUNDATION   Kernel · init · drivers · packaging base    │
└─────────────────────────────────────────────────────────────────┘
```

**Regola d’oro:** ogni layer parla solo con i layer adiacenti tramite API versionate, salvo eccezioni documentate (es. Ryuk → Shell via capability esplicita).

---

## 4. Componenti della piattaforma

| Componente | Documento | Ruolo |
|------------|-----------|-------|
| NovaOS | `02-NovaOS.md` | Sistema operativo / system layer |
| Nova Shell | `03-Nova-Shell.md` | Experience desktop |
| Nova AI Core | `04-Nova-AI-Core.md` | Orchestratore AI |
| Ryuk | `05-Ryuk.md` | Assistente nativo (system service) |
| Nova Services | `06-Nova-Services.md` | Servizi di piattaforma |
| Nova Apps | `07-Nova-Apps.md` | App native ecosistema |
| Nova SDK | `08-Nova-SDK.md` | SDK e contratti developer |
| Security | `09-Security.md` | Modello di sicurezza |
| Boot Sequence | `10-Boot-Sequence.md` | Ordine di avvio |

---

## 5. Flusso di comunicazione (bus di piattaforma)

### 5.1 Nova Bus (concettuale)

Canale ufficiale inter-processo della piattaforma (implementazione futura: D-Bus + canale capabilities dedicato, o equivalente). Tipi di messaggio:

| Tipo | Esempio |
|------|---------|
| **Intent** | `open.app`, `search.system`, `files.reveal` |
| **Capability call** | `shell.focus_window`, `ai.complete` |
| **Event** | `session.locked`, `notify.posted`, `ai.provider.changed` |
| **Query** | `capabilities.list`, `apps.resolve` |

### 5.2 Diagramma di flusso tipico (comando utente via Ryuk)

```text
Utente → Nova Shell (Pulse) → Ryuk
                              ├→ Nova AI Core (pianificazione / NLP)
                              ├→ Nova Services (identity, permissions)
                              ├→ Nova Shell (UI actions)
                              └→ Nova Apps (intent mirati)
```

### 5.3 Diagramma (app nativa che usa AI)

```text
NovaDocs → Nova SDK → Nova AI Core → Provider (Ollama / Cloud)
                   ↘ Permissions Service → Audit
```

Le app **non** chiamano Ollama o provider cloud direttamente in produzione.

---

## 6. Dipendenze

| Dipende da | Perché |
|------------|--------|
| Linux Foundation (ADR-001 Fedora) | Host OS |
| ADR stack (DNF, SDDM, …) | Vincoli di packaging/update |
| Design System | Contratti UX per Experience |
| Policy sicurezza | Gate su ogni capability sensibile |

| Dipendenti | Nota |
|------------|------|
| Tutti i componenti Nova | Devono dichiarare dipendenze di layer |

---

## 7. API interne (contratti di piattaforma)

Namespace logici stabili (versionati `v1`, `v2`, …):

| API | Consumatori principali |
|-----|------------------------|
| `platform.identity.v1` | Shell, Apps, Ryuk, Cloud |
| `platform.capabilities.v1` | SDK, Ryuk, Services |
| `platform.intent.v1` | Shell, Apps, Ryuk |
| `platform.notify.v1` | Services, Shell, Apps |
| `platform.ai.v1` | SDK, Ryuk, Shell |
| `platform.shell.v1` | Ryuk, Settings |
| `platform.apps.v1` | Launcher, Ryuk, Update |
| `platform.audit.v1` | Security, AI Core, Ryuk |

**Politica di compatibilità (10 anni):**

- Minor: solo aggiunte backward-compatible.
- Major: deprecazione ≥ 18 mesi, dual-run quando possibile.
- Rimozione solo dopo metrica “zero consumatori interni supportati”.

---

## 8. Ciclo di vita della piattaforma

| Fase | Attività |
|------|----------|
| Design | ADR + docs `platform/` |
| Bootstrap | Implementazione services minimi |
| Stabilize | Freeze `v1` API |
| Expand | Apps, Skills, AI providers |
| Evolve | `v2` parallelo, migrazione guidata |
| Retire | Deprecazione controllata |

Versionamento prodotto: **NovaOS release** ⊇ **Platform API level** (es. NovaOS 3.x richiede Platform ≥ 2.1).

---

## 9. Principi di longevità (10 anni)

1. **Contract-first** — schema e API prima del codice.  
2. **Replaceable providers** — Ollama/OpenAI/Gemini dietro adapter.  
3. **Strangler-friendly** — componenti upstream sostituibili pezzo a pezzo.  
4. **Observability by default** — senza telemetria oscura; audit locale sempre.  
5. **Security as boundary** — non come feature opzionale.  
6. **Documentazione come artefatto di build** — ogni cambio API aggiorna `platform/` e SDK.

---

## 10. Relazioni

- Visione: `../vision.md`
- Architettura high-level: `../architecture.md`
- ADR: `../adr/`
- Design System / Nova Shell UX: `../design-system/`
