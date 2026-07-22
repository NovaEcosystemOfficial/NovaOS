# 05 — Ryuk

**Native System Assistant Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Dichiarazione fondamentale

> **Ryuk non è un’applicazione.**  
> **Ryuk è un servizio di sistema** di NovaOS: l’assistente nativo del sistema operativo.

Ryuk è il layer di assistenza che:

- interagisce con NovaOS;
- controlla Nova Shell;
- utilizza **Nova AI Core** come orchestratore AI;
- usa modelli **locali** via AI Core → Ollama;
- usa modelli **cloud** opzionali via AI Core;
- controlla le applicazioni Nova tramite intent/capability;
- estende le proprie funzionalità tramite **Skills**.

L’utente può percepire Ryuk attraverso Pulse / AI Stage in Nova Shell, ma il processo autorevole è un **system service**, non una app in `apps/`.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Assistenza di sistema | Comprendere richieste utente orientate al sistema e alle app Nova |
| Orchestrazione azioni | Pianificare e eseguire azioni consentite (shell, apps, services) |
| Conversazione di sistema | Stato dialogo, turn-taking, contesto sessione |
| Skills | Caricare, governare, eseguire estensioni |
| Conferme | Richiedere conferma umana su side-effect sensibili |
| Multimodalità UI | Chiedere a Shell di mostrare card/preview/toast |
| Degraded mode | Funzionare in subset se AI Core è limitato |

### Non responsabilità

- Essere un LLM runtime (delega a Nova AI Core)
- Sostituire il package manager o il kernel
- Eseguire codice Skill senza sandbox/policy
- Bypassare Security

### Confini rispetto ad altri componenti

| Componente | Relazione |
|------------|-----------|
| Nova AI Core | Ryuk **consuma** AI; non la rimpiazza |
| Nova Shell | Ryuk **controlla** UI via API; non include chrome |
| Nova Apps | Ryuk le **comanda** via intent, non le embedda |
| NovaOS | Ryuk richiede azioni sistema via API privilegiate |

---

## 3. Architettura

```text
┌────────────────────────────── Ryuk (system service) ─────────────────────────────┐
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │ Session Hub     │  │ Dialogue        │  │ Action Planner                   │  │
│  │ (user sessions) │  │ Manager         │  │                                  │  │
│  └─────────────────┘  └─────────────────┘  └──────────────────────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │ Skill Runtime   │  │ Capability      │  │ Confirmation Gate                │  │
│  │                 │  │ Client          │  │                                  │  │
│  └─────────────────┘  └─────────────────┘  └──────────────────────────────────┘  │
│  ┌─────────────────┐  ┌─────────────────┐                                        │
│  │ Shell Driver    │  │ Apps Driver     │                                        │
│  └─────────────────┘  └─────────────────┘                                        │
│                         Ryuk Control API (internal)                              │
└───────────────┬───────────────────┬────────────────────┬─────────────────────────┘
                │                   │                    │
                ▼                   ▼                    ▼
         Nova AI Core         Nova Shell          Nova Services / Apps
         (platform.ai)       (platform.shell)     (intent/capabilities)
```

### Componenti

| Componente | Funzione |
|------------|----------|
| **Session Hub** | Una sessione assistente per utente grafico loggato |
| **Dialogue Manager** | Storia breve, intent parsing, chiarimenti |
| **Action Planner** | Decompone goal → azioni capability |
| **Confirmation Gate** | Policy UX: ask / allow-once / deny |
| **Skill Runtime** | Carica Skills firmati, esegue in sandbox |
| **Capability Client** | Chiama platform APIs |
| **Shell Driver** | Wrapper `platform.shell.v1` |
| **Apps Driver** | Wrapper `platform.intent` / `platform.apps` |
| **System Driver** | Wrapper session/update/config (privilegi stretti) |

---

## 4. Skills

### 4.1 Cos’è una Skill

Una **Skill** è un pacchetto versionato che estende Ryuk con:

- metadati (nome, permessi richiesti, trigger);
- schemi di input/output;
- logica (manifest + handler isolato);
- eventuali prompt template (dichiarativi).

### 4.2 Esempi (non esaustivi)

- `skill.shell.arrange_windows`
- `skill.docs.summarize_open_document` (via NovaDocs intent)
- `skill.system.update_check`
- `skill.promo.draft_campaign` (NovaPromo)

### 4.3 Governance Skills

| Regola | Dettaglio |
|--------|-----------|
| Firma | Solo Skills firmati Nova o trust store utente |
| Permessi | Dichiarati; concessi a install/runtime |
| Sandbox | No root arbitrario; solo capability whitelist |
| Kill switch | Disabilitabili da Settings / policy |

---

## 5. Flusso di comunicazione

### 5.1 Richiesta utente tipica

```text
Utente: “Metti a fuoco NovaDocs e riassumi il documento aperto”
    → Shell Pulse → Ryuk Session Hub
    → Dialogue Manager
    → AI Core (system_plan / chat)     [locale o cloud via policy]
    → Action Planner:
         1. shell.FocusApp("novadocs")
         2. intent novadocs.get_active_document
         3. ai.Complete(summarize) 
         4. shell.ShowAIStage(result card)
    → Confirmation Gate se serve
    → Esecuzione + audit
```

### 5.2 Controllo Nova Shell

```text
Ryuk Shell Driver → OpenLauncher / ShowAIStage / SetDoNotDisturb / FocusApp …
```

### 5.3 Controllo Nova Apps

```text
Ryuk Apps Driver → platform.intent.Invoke(app_id, action, payload)
                 → app esegue e ritorna risultato strutturato
```

### 5.4 Interazione NovaOS

```text
Ryuk System Driver → system.update.Check / system.config.Get
                   → azioni distruttive sempre con Confirmation Gate + Security
```

### 5.5 Uso modelli

```text
Ryuk ──platform.ai.v1──► Nova AI Core ──► Ollama (locale)
                                      └──► Cloud adapters (opzionali)
```

Ryuk **non** apre socket diretti verso Ollama/OpenAI/Gemini in architettura target.

---

## 6. Dipendenze

| Dipendenza | Criticità |
|------------|-----------|
| Nova AI Core | Alta (senza AI: comandi espliciti/Skills limitate) |
| Nova Shell | Alta per UX; headless admin mode possibile in futuro |
| NovaOS APIs | Alta per azioni sistema |
| Permissions / Audit | Obbligatoria |
| Skill store locale | Media |
| Nova Apps intent handlers | Per controllo app |

**Dipendenti:** Pulse UI, scorciatoie globali, eventualmente greeter (subset).

---

## 7. API interne

### 7.1 `platform.ryuk.v1` (ingresso verso Shell/SDK controllati)

| Metodo | Descrizione |
|--------|-------------|
| `StartSession()` | Apre sessione assistente |
| `SendUserMessage(text\|audio_ref\|payload)` | Input utente |
| `Cancel()` | Stop pianificazioni |
| `GetStatus()` | idle/thinking/awaiting_confirmation/degraded |
| `Confirm(action_id, decision)` | allow/deny |
| `ListSkills()` / `SetSkillEnabled(id, bool)` | gestione |
| `Subscribe(RyukEvents)` | stream UI |

### 7.2 API interne di controllo (solo servizio Ryuk)

Non pubbliche alle app generiche:

| Area | Esempi |
|------|--------|
| Shell Driver | tutti i metodi `platform.shell.v1` ammessi dal ruolo `ryuk` |
| Apps Driver | intent allowlist dinamica |
| System Driver | subset `system.*` ad alto privilegio |
| Skill RPC | `skill.invoke` sandbox |

### 7.3 Eventi

`Thinking`, `Message`, `ActionProposed`, `ActionStarted`, `ActionCompleted`, `ConfirmationRequired`, `Error`, `SkillLoaded`.

---

## 8. Ciclo di vita

| Stato servizio | Descrizione |
|----------------|-------------|
| Inactive | Non avviato |
| Starting | Attende `ai` e bus; carica Skills di sistema |
| Ready | Accetta sessioni |
| SessionActive | Dialogo in corso |
| AwaitingConfirmation | Gate aperto; timeout → deny |
| Degraded | AI off/local only; Skills ridotte |
| Quiesced | Sessione utente locked: pausa azioni |
| Stopping | Cancella job; persiste preferenze Skills |

**Unit concept:** `nova-ryuk.service` sotto Service Supervisor, parte di `nova-session.target` (per-user) o ibrido system+user — scelta implementativa futura, vincolo: **privilegi minimi necessari**, sessione legata all’utente grafico.

Restart policy: on-failure con backoff; Shell mostra Pulse degraded se Ryuk assente.

---

## 9. Modello di controllo delle Nova Apps

Ryuk controlla le app Nova **solo** se:

1. l’app espone intent documentati (`07-Nova-Apps.md`);
2. l’intent è nella allowlist della Skill o del piano;
3. Permissions Service autorizza il chiamante `ryuk`;
4. per side-effect rilevanti, Confirmation Gate approva.

Nessun “controllo UI per pixel hacking” come via primaria: solo **contratti**.

---

## 10. Longevità (10 anni)

- Skills consentono estensione senza rilasciare un Ryuk monolitico ogni mese.
- Planner può evolvere (regole → LLM plan → hybrid) dietro lo stesso `platform.ryuk.v1`.
- Separazione da AI Core protegge l’assistente dal churn dei vendor.
- Shell Driver isola Ryuk dai rewrite del toolkit grafico.

---

## 11. Anti-pattern vietati

- Distribure Ryuk come flatpak/app utente “opzionale” unica forma.
- Far chiamare Ollama direttamente da Ryuk in produzione.
- Dare a Skills accesso root implicito.
- Far diventare Ryuk un “RPA cieco” senza conferme.

---

## 12. Riferimenti

- `04-Nova-AI-Core.md`, `03-Nova-Shell.md`, `07-Nova-Apps.md`, `09-Security.md`
- Design System: Pulse / AI Stage
- ADR-007
