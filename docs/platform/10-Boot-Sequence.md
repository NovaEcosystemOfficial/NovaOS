# 10 — Boot Sequence

**System Startup & Session Bring-up**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire la **sequenza di boot e di sessione** di NovaOS: dall’accensione all’operatività di Nova Shell, Nova AI Core e Ryuk, inclusi stati degraded e spegnimento ordinato.

Allineata a Design System (`07-Boot-Experience.md`) sul piano UX; qui sul piano **architetturale**.

---

## 2. Responsabilità di questo documento

| Area | Contenuto |
|------|-----------|
| Ordine di avvio | Dipendenze tra target/servizi |
| Ready semantics | Quando un componente è “pronto” |
| Failure modes | Cosa succede se AI/Ryuk falliscono |
| Session handoff | Greeter → Shell |
| Shutdown | Ordine inverso sicuro |

---

## 3. Architettura della sequenza

```text
Power On
  → Firmware / Bootloader
  → Linux kernel + init
  → nova-system.target
  → Display Manager (SDDM) + Greeter Nova
  → Autenticazione
  → nova-session.target (utente)
  → Nova Shell
  → Nova AI Core (user/system scope definito)
  → Ryuk
  → Nova Apps on-demand
```

---

## 4. Fasi dettagliate

### Fase A — Kernel & init

- Linux Foundation avvia init/systemd.
- Driver essenziali, filesystem, rete base.
- **UI:** eventuale splash vendor; poi Nova Boot Splash appena possibile.

### Fase B — `nova-system.target`

Avvio ordinato:

1. Audit Service (il più presto utile)
2. Secrets / Identity (machine + local users)
3. Permissions + Capability Registry
4. Config Store
5. Policy Agent
6. Device Broker
7. Update Broker (idle)
8. AI Core **system instance** (probe Ollama; può restare idle)

**Ready:** `system.supervisor.Health == ready|degraded`

### Fase C — Greeter

- SDDM + tema Nova.
- Identity per autenticazione locale (e cloud link solo se già configurato e policy ok).
- Nessun Ryuk completo richiesto al login (opzionale assist soft futuro).

### Fase D — `nova-session.target`

Post-login:

1. Session Manager marca sessione attiva  
2. Notification + Intent (user)  
3. Sync (opzionale, background)  
4. **Nova Shell** start → `shell.ready`  
5. Skills Broker (metadata)  
6. **Nova AI Core** session bind / ensure ready  
7. **Ryuk** start → `ryuk.ready`  
8. Shell abilita Pulse full (se Ryuk ready) altrimenti degraded  

### Fase E — Idle produttivo

- Apps lanciate on-demand.
- Indexer/search se abilitati (posteriori).

---

## 5. Flusso di comunicazione (boot events)

```text
Supervisor → Bus: system.phase(system_ready)
Greeter → SessionManager: login_success
SessionManager → Bus: session.started
Shell → Bus: shell.ready
AI Core → Bus: ai.ready | ai.degraded
Ryuk → Bus: ryuk.ready | ryuk.degraded
Shell ← aggiorna Pulse state
```

---

## 6. Componenti coinvolti

| Componente | Ruolo nel boot |
|------------|----------------|
| Service Supervisor | Ordine e health |
| Greeter | Auth UX |
| Session Manager | Handoff |
| Nova Shell | Experience |
| Nova AI Core | Orchestratore AI |
| Ryuk | Assistente sistema |
| Ollama | Dipendenza soft di AI Core |

---

## 7. Dipendenze (vincoli d’ordine)

| Componente | Attende |
|------------|---------|
| Greeter | Identity locale minima |
| Shell | session.started |
| Ryuk | bus + permissions; AI preferred ma non hard-block assoluto |
| Apps | shell opzionale; intent registry |

**Hard fail boot utente:** filesystem, display, session manager.  
**Soft fail:** AI Core, Ryuk, Sync, cloud — sistema resta usabile.

---

## 8. API interne usate in sequenza

- `system.supervisor.v1` — target reachability  
- `system.session.v1` — started/locked  
- `platform.ai.v1 GetHealth`  
- `platform.ryuk.v1 GetStatus`  
- `platform.shell` ready events  

---

## 9. Ciclo di vita completo (power cycle)

### Startup states

`OFF → FIRMWARE → KERNEL → SYSTEM_READY → GREETER → SESSION_STARTING → SHELL_READY → ASSISTANT_READY → IDLE`

`ASSISTANT_READY` = Ryuk ready **oppure** explicit degraded acknowledged.

### Lock

```text
Lock → Ryuk quiesce actions → Shell lock surface → AI continua solo se policy lock-safe (default: no cloud, no Skills side-effect)
```

### Shutdown

```text
Request (Shell/Ryuk/System)
  → Confirm se user-initiated via Ryuk
  → Apps close intents (best effort)
  → Ryuk stop (cancel jobs)
  → Shell stop
  → session.target down
  → AI Core drain
  → system.target down
  → kernel poweroff
```

---

## 10. Failure matrix

| Fallimento | Comportamento |
|------------|---------------|
| Ollama assente | AI degraded; cloud se consentito; altrimenti AI_OFF features |
| AI Core crash | Restart backoff; Ryuk degraded; Shell usabile |
| Ryuk crash | Pulse muted; Shell usabile; auto-restart |
| Shell crash | Session Manager recovery / re-login path |
| Permissions down | Deny-by-default; safe mode limitato |

---

## 11. Longevità

- Target/fasi restano stabili anche se i binari cambiano.
- Nuovi servizi si agganciano a `system` o `session` senza riscrivere il greeter.
- Immortalità del contratto eventi (`system.phase`, `shell.ready`, …).

---

## 12. Riferimenti

- `02-NovaOS.md`, `03-Nova-Shell.md`, `04-Nova-AI-Core.md`, `05-Ryuk.md`
- `../design-system/07-Boot-Experience.md`
- ADR-005 SDDM, ADR-006 Update
