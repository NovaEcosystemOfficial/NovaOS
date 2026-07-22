# 09 — Security

**Platform Security Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire il **modello di sicurezza** di Nova Platform: confini di trust, autenticazione/autorizzazione, protezione AI/Ryuk/Skills, supply chain, audit e privacy — pensato per mantenibilità decennale.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Trust boundaries | Chi può chiamare cosa |
| AuthN/AuthZ | Identità + capability grants |
| AI safety ops | Policy dati, cloud consent, redaction |
| Ryuk & Skills | Least privilege, conferme, sandbox |
| Secrets | Token cloud, chiavi |
| Supply chain | Firma pacchetti, Skills, immagini |
| Audit & incident | Tracciabilità locale |
| Hardening host | Baseline NovaOS |

---

## 3. Architettura (confini di trust)

```text
┌──────── Untrusted / Less trusted ────────┐
│  External network · Cloud LLM vendors    │
│  User-installed Skills (if allowed)      │
└──────────────────┬───────────────────────┘
                   │ strict adapters
┌──────── Platform trusted computing base ─┐
│  Permissions · Audit · Secrets · AI Core │
│  Ryuk (privileged assistant role)        │
│  NovaOS Policy Agent                     │
└──────────────────┬───────────────────────┘
                   │
┌──────── User session domain ─────────────┐
│  Nova Shell · Nova Apps (per grants)     │
└──────────────────────────────────────────┘
```

**Principio:** Ryuk è privilegiato rispetto alle app, **non** rispetto al Policy Agent e all’Audit. Anche Ryuk è soggetto a deny.

---

## 4. Componenti di sicurezza

| Componente | Ruolo |
|------------|-------|
| **Permissions Service** | ACL capability |
| **Policy Agent (NovaOS)** | Policy host/sessione |
| **Secrets Service** | Vault locale |
| **Audit Service** | Append-only events |
| **AI Policy Engine** | Dentro AI Core |
| **Confirmation Gate** | Dentro Ryuk (UX + security control) |
| **Skill Sandbox** | Isolamento esecuzione |
| **Package signatures** | DNF/RPM / ostree |

---

## 5. Flusso di comunicazione (esempio sensibile)

```text
Ryuk vuole system.shutdown
  → Permissions/Policy check (role ryuk)
  → Confirmation Gate (utente)
  → Audit Append (proposed/allowed)
  → system.session.Shutdown
  → Audit Append (completed)
```

```text
App vuole cloud AI con documento Sensitive
  → AI Policy Engine → DENY cloud
  → Eventuale local-only o errore CONTEXT_DENIED
  → Audit meta (no content leak di default)
```

---

## 6. Modello AuthZ (capability)

Esempi di capability:

| Capability | Chi tipicamente |
|------------|-----------------|
| `ai.complete` | Apps, Ryuk |
| `ai.complete.system_plan` | Ryuk |
| `shell.control` | Ryuk, Settings |
| `apps.intent.invoke` | Ryuk, Apps (limitato) |
| `system.update.apply` | Settings, Ryuk+confirm |
| `secrets.cloud` | AI Core adapters |
| `skills.manage` | Settings, utente admin |

Default: **deny**. Grant espliciti; revisione in Settings.

---

## 7. Ryuk — profilo di sicurezza

| Controllo | Specifica |
|-----------|-----------|
| Ruolo | `role:ryuk` con allowlist capability |
| Conferme | Obbligatorie per: shutdown, delete massivo, invio dati cloud, install Skill, update apply |
| Skills | Firma + permessi dichiarati + sandbox |
| Session binding | Azioni legate all’utente grafico attivo |
| Impersonation | Vietata verso altri utenti |

---

## 8. AI — profilo di sicurezza

| Controllo | Specifica |
|-----------|-----------|
| No direct vendor da app | Solo AI Core |
| Data classes | Public / Private / Sensitive |
| Cloud | Opt-in, indicatori UI, revoca |
| Prompt injection | Tool Bridge non esegue side-effect senza Gate |
| Model integrity | Registry hash / source trust |

---

## 9. Dipendenze

- Identity, Permissions, Audit, Secrets  
- Update Broker (firme)  
- Design System (indicatori privacy/AI mode)  
- ADR-007 hybrid AI  

---

## 10. API interne rilevanti

- `platform.permissions.v1`
- `platform.audit.v1`
- `platform.secrets.v1`
- Policy hooks in `platform.ai.v1` (errori `DENIED`, `CONTEXT_DENIED`)
- Confirmation protocol in `platform.ryuk.v1`

---

## 11. Ciclo di vita sicurezza

| Momento | Azione |
|---------|--------|
| Install OS | Root of trust, chiavi prodotto |
| First boot | Generazione chiavi macchina, policy default |
| Login | Session credentials |
| Runtime | Continuous AuthZ + audit |
| Update | Verifica firme, rollback path |
| Compromise response | Revoca grants, disabilita Skills, AI off |

---

## 12. Privacy

- Telemetria remota: opt-in esplicito (se mai presente).
- Audit locale distinto da telemetria.
- Export/delete dati assistente e history secondo Settings.
- Cloud token solo in Secrets Service.

---

## 13. Longevità

- Capability graph versionato.
- Nuovi rischi AI affrontati aggiornando Policy Engine, non ogni app.
- Skills come superficie estendibile **governata**, non come script liberi.

---

## 14. Riferimenti

- `04-Nova-AI-Core.md`, `05-Ryuk.md`, `06-Nova-Services.md`, ADR-007
