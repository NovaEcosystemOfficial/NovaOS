# 06 — Nova Services

**Platform Services Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire i **Nova Services**: demoni e servizi di piattaforma che implementano capacità trasversali (identità, notifiche, intent, sync, permessi, audit, ecc.) usate da NovaOS, Nova Shell, Ryuk, AI Core e Apps.

---

## 2. Responsabilità (insieme dei servizi)

| Servizio | Responsabilità |
|----------|----------------|
| **Identity Service** | Utente locale, sessioni, link NovaCloud opzionale |
| **Permissions Service** | Grant capability ad app, Ryuk, Skills |
| **Intent Service** | Registry e dispatch intent inter-app / sistema |
| **Notification Service** | Coda, policy DND, fan-out a Shell |
| **Capability Registry** | Discovery di capacità runtime |
| **Audit Service** | Log di sicurezza e azioni AI/Ryuk |
| **Sync Service** | Bridge NovaCloud (preferenze, non necessariamente file full) |
| **Search Indexer** (fase successiva) | Indice locale opt-in |
| **Secrets Service** | Storage credenziali/token cloud |
| **Skills Broker** | Install/enable metadata Skills per Ryuk |

### Non responsabilità

- UI (Shell)
- Orchestrazione LLM (AI Core)
- Pianificazione assistente (Ryuk)

---

## 3. Architettura

```text
┌────────────────────── Nova Services Plane ──────────────────────┐
│  Identity │ Permissions │ Intent │ Notify │ Capabilities        │
│  Audit    │ Secrets     │ Sync   │ Skills Broker │ (Search…)    │
│                     Nova Bus / IPC fabric                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
            NovaOS Supervisor │ AI Core │ Ryuk │ Shell │ Apps/SDK
```

Ogni servizio:

- ha interfaccia versionata;
- pubblica health a `system.supervisor`;
- scrive audit quando tocca decisioni di sicurezza.

---

## 4. Flusso di comunicazione (esempi)

### 4.1 App chiede permesso

```text
App → Permissions.Request(cap)
   → UX prompt via Shell (se necessario)
   → Grant persistito
   → Audit
```

### 4.2 Intent cross-app

```text
Ryuk/App → Intent.Invoke("novadocs.open", payload)
        → Intent Service risolve handler
        → Permissions check
        → Target app
        → Result
```

### 4.3 Notifica

```text
Producer → Notify.Post → policy DND → Shell Notification Center
```

---

## 5. Componenti e API interne (sintesi)

### `platform.identity.v1`

`GetUser`, `GetSession`, `LinkCloud`, `UnlinkCloud`, `Subscribe`

### `platform.permissions.v1`

`Check`, `Request`, `Revoke`, `ListGrants`

### `platform.intent.v1`

`RegisterHandler`, `Unregister`, `Invoke`, `Resolve`

### `platform.notify.v1`

`Post`, `Dismiss`, `List`, `SetDoNotDisturb`

### `platform.capabilities.v1`

`List`, `Resolve(name)`, `Advertise`

### `platform.audit.v1`

`Append`, `Query` (privilegiato), `Export`

### `platform.secrets.v1`

`Put`, `Get`, `Delete` (ACL stretta)

### `platform.sync.v1`

`GetStatus`, `Trigger`, `SetScope`

### `platform.skills.v1` (metadata)

`ListInstalled`, `Install`, `Remove`, `GetManifest`  
(Esecuzione: Ryuk Skill Runtime)

---

## 6. Dipendenze

| Servizio | Dipende da |
|----------|------------|
| Permissions | Identity, Shell (per prompt), Audit |
| Intent | Permissions, Capabilities, Apps |
| Notify | Config (DND), Shell |
| Sync | Identity, Secrets, Network |
| Skills Broker | Audit, Permissions, filesystem firmati |
| AI Core | Permissions, Audit, Secrets (token cloud) |
| Ryuk | quasi tutti |

---

## 7. Ciclo di vita

Target concettuali:

1. `nova-system.target` — Identity, Audit, Permissions, Secrets, Capabilities  
2. `nova-session.target` — Notify, Intent handlers user, Sync user  
3. Post-ready — Skills Broker, Search (opzionali)

Ordine di shutdown inverso; Sync flush best-effort.

---

## 8. Longevità

- Servizi piccoli, single-purpose, sostituibili.
- Intent/Capabilities come spina dorsale: nuove app senza cambiare Shell.
- Audit immutabile append-only locale; retention policy configurabile.

---

## 9. Riferimenti

- `01-Nova-Platform.md`, `09-Security.md`, `05-Ryuk.md`
