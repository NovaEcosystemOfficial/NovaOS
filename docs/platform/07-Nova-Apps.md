# 07 — Nova Apps

**Native Ecosystem Applications Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire come le **applicazioni native** dell’ecosistema Nova vivono su NovaOS: packaging, contratti di natività, intent verso Ryuk/Shell, uso di AI Core via SDK.

App previste (non esaustivo): NovaDocs, NovaStudio, NovaPromo, NovaBeauty, NovaSky, superfici NovaCloud/NovaAI **applicative** (distinct da AI Core e da Ryuk).

---

## 2. Responsabilità delle Nova Apps

| Responsabilità | Descrizione |
|----------------|-------------|
| Dominio | Implementare valore verticale (docs, studio, …) |
| Natività | Esporre intent/capabilities documentati |
| UX coerente | Design System + SDK components |
| AI consumption | Solo via Nova SDK → AI Core |
| Permessi | Dichiarare e rispettare grants |
| Aggiornamento | Pacchetti firmati nei canali Nova |

### Non responsabilità

- Orchestrare AI di sistema (AI Core)
- Essere l’assistente OS (Ryuk)
- Possedere il chrome desktop (Shell)

**Nota:** Ryuk controlla le app; le app **non** sono Ryuk.

---

## 3. Architettura di un’app nativa

```text
┌────────────────── Nova App (es. NovaDocs) ──────────────────┐
│  UI Domain                                                  │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────────────┐  │
│  │ App Logic  │ │ Intent     │ │ Nova SDK clients        │  │
│  │            │ │ Handlers   │ │ (ai, notify, identity)  │  │
│  └────────────┘ └────────────┘ └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
         Intent Service · Permissions · AI Core · Notify
```

---

## 4. Contratto di natività (requisiti)

Un’app è **Nova-native** se:

1. è pacchettizzata per NovaOS (RPM/canale ufficiale, ADR-004);
2. dichiara un **App Manifest** (id, permessi, intent, min Platform API);
3. registra intent all’avvio/ sessione;
4. usa Design System tokens;
5. non bypassa AI Core / Secrets;
6. supporta invocazioni da Ryuk per gli intent pubblicati;
7. gestisce `AI_UNAVAILABLE` senza crash.

---

## 5. Flusso di comunicazione

### 5.1 Launch da Shell

```text
Launcher → apps.Launch(app_id) → processo app → shell Focus Strip
```

### 5.2 Controllo da Ryuk

```text
Ryuk → intent.Invoke(app_id, "summarize_selection")
    → Permissions
    → Handler app → risultato → Ryuk → AI Stage / app UI
```

### 5.3 AI in-app

```text
App → SDK.ai.Complete → AI Core → provider
```

---

## 6. Componenti (manifest e runtime)

| Artefatto | Contenuto |
|-----------|-----------|
| `nova-app.json` (nome da definire) | id, version, intents[], permissions[], skills_affinity[] |
| Desktop entry Nova | Integrazione launcher |
| Intent handlers | IPC endpoints |
| Sandbox profile | Se applicabile (fase futura) |

### Intent minimi consigliati (per app)

| Intent generico | Semantica |
|-----------------|-----------|
| `app.focus` | Porta app in primo piano |
| `app.open` | Apri risorsa |
| `app.search` | Cerca nel dominio |
| `app.status` | Stato sintetico per Ryuk |

Intent di dominio aggiuntivi per ciascuna app.

---

## 7. Dipendenze

| Dipendenza | Uso |
|------------|------|
| Nova SDK | API client |
| Intent / Permissions / Notify | Piattaforma |
| AI Core (opzionale per app) | Feature AI |
| Design System | UI |
| DNF/repo Nova | Distribuzione |

---

## 8. API interne rilevanti

Le app **consumano**:

- `platform.apps.v1` (register, launch metadata)
- `platform.intent.v1`
- `platform.ai.v1` via SDK
- `platform.notify.v1`
- `platform.identity.v1`

Le app **non** consumano direttamente:

- `platform.shell.v1` privilegiato (riservato a Ryuk/Settings)
- adapter cloud AI grezzi

### `platform.apps.v1` (sintesi)

`Register`, `Unregister`, `Launch`, `List`, `Resolve`, `GetManifest`

---

## 9. Ciclo di vita app

| Stato | Descrizione |
|-------|-------------|
| Installed | Pacchetto presente |
| Enabled | Visibile in launcher |
| Running | Processo attivo + intent registered |
| Background | Eventuali worker dichiarati |
| Updating | Stop controllato → replace → restart |
| Disabled / Removed | Unregister intent; revoke opzionale |

---

## 10. Relazione con Ryuk Skills

- Skill può richiedere intent di un’app.
- Se l’app non è installata: Ryuk propone installazione (futuro store) o fallisce chiaro.
- Skill non incorpora logica di dominio dell’app: la **delega**.

---

## 11. Longevità

- Manifest + intent stabili = Ryuk e Shell restano agnostici.
- Nuove app ecosistema senza modificare AI Core.
- Versioning Platform API nel manifest evita runtime misteriosi.

---

## 12. Riferimenti

- `08-Nova-SDK.md`, `05-Ryuk.md`, `01-Nova-Platform.md`
- Visione ecosistema in `../vision.md`
