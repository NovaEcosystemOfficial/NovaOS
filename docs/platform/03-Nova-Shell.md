# 03 — Nova Shell

**Experience Layer Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire **Nova Shell** come strato di esperienza desktop di NovaOS: chrome di sistema, finestre, launcher, centri, superfici AI di invocazione — implementato secondo il Design System, controllabile da Ryuk tramite API dedicate.

Nova Shell è un **prodotto di esperienza**, non il nome marketing di Plasma stock.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Chrome | Horizon Bar, Nova Core, Focus Strip, Tray, Clock |
| Windowing UX | Titlebar Nova, focus, snap, workspace UX |
| Launcher | Search, app grid, places, suggestions |
| Notification Center | Coda notifiche, brief AI dismissibile |
| Control Center | Toggle rapidi, NovaAI mode |
| Pulse / AI Stage | Superfici di invocazione Ryuk/AI (UI only) |
| Theming | Applicazione token Design System |
| Accessibility shell | Focus, keyboard, contrast |

### Non responsabilità

- Inferenza LLM (Nova AI Core)
- Logica assistente e Skills (Ryuk)
- Packaging update host (NovaOS Update Broker)
- Contenuto business delle Nova Apps

---

## 3. Architettura

```text
┌──────────────────────── Nova Shell ────────────────────────┐
│  Shell Host (session compositor integration)               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────┐  │
│  │ Horizon │ │Launcher │ │ Notif   │ │ Control Center   │  │
│  │  Bar    │ │         │ │ Center  │ │                  │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────┐  │
│  │ Window  │ │ Pulse   │ │ AI Stage│ │ Settings bridge  │  │
│  │ Decor   │ │         │ │         │ │                  │  │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────────┘  │
│                 Shell Controller (API server)              │
└───────────────────────────┬────────────────────────────────┘
                            │ platform.shell.v1
              Ryuk · Settings · Nova Services (notify)
```

### Componenti

| Componente | Ruolo |
|------------|-------|
| **Shell Host** | Processo/sessione principale Experience |
| **Horizon Bar** | Chrome primario |
| **Launcher Controller** | Index app + search UI |
| **Notification Sink** | Consuma `platform.notify` |
| **Control Center VM** | Stato toggle ↔ services |
| **Window Decor Adapter** | Unifica look finestre |
| **Pulse / AI Stage UI** | Frontend per Ryuk (no business logic AI) |
| **Shell Controller** | Espone `platform.shell.v1` |

---

## 4. Flusso di comunicazione

### 4.1 Apertura app

```text
User → Launcher → platform.apps.Launch → App process
                 → Focus Strip update
```

### 4.2 Notifica

```text
App/Service → platform.notify.Post → Notification Sink → UI card
```

### 4.3 Controllo da Ryuk

```text
Ryuk → platform.shell.v1 (es. OpenLauncher, ShowAIStage, SetFocusMode)
    → Shell Controller valida permission session-local
    → UI update
```

### 4.4 Invocazione assistente

```text
User → Pulse → Shell apre AI Stage → inoltra sessione a Ryuk
            → Ryuk usa AI Core → eventuali shell actions di ritorno
```

---

## 5. Dipendenze

| Dipendenza | Motivo |
|------------|--------|
| NovaOS Session Manager | Ciclo vita sessione |
| Design System | Layout/token |
| ADR-002 Plasma (upstream) | Base tecnica sostituibile |
| `platform.notify`, `platform.apps`, `platform.identity` | Dati |
| Ryuk (opzionale a runtime) | Se assente, Pulse mostra degraded state |

**Dipendenti:** Ryuk (controllo UX), utente finale.

---

## 6. API interne — `platform.shell.v1`

| Metodo | Descrizione | Privilegio |
|--------|-------------|------------|
| `OpenLauncher(query?)` | Apre launcher | session |
| `CloseLauncher()` | Chiude | session |
| `OpenNotificationCenter()` | Sheet destra | session |
| `OpenControlCenter()` | Pannello quick | session |
| `ShowAIStage(mode)` | compact/full | session + ryuk |
| `HideAIStage()` | Chiude stage | session |
| `FocusApp(app_id)` | Porta in focus | session |
| `ListWindows()` | Snapshot finestre | session |
| `SetDoNotDisturb(bool)` | Focus mode chrome | session |
| `SetTheme(light\|dark\|auto)` | Tema | session |
| `ShowToast(message, actions?)` | Feedback | session |
| `Subscribe(ShellEvents)` | eventi UI | session |

Eventi: `LauncherOpened`, `WindowFocused`, `ThemeChanged`, `AIStageVisibilityChanged`, …

---

## 7. Ciclo di vita

| Stato | Descrizione |
|-------|-------------|
| Starting | Shell Host si aggancia alla sessione |
| Ready | Horizon Bar visibile; emette `shell.ready` |
| Degraded | Ryuk/AI offline: UI usabile, Pulse in stato muted |
| Locked | Chrome ridotto / lock surface |
| Stopping | Salva stato UI; chiude stage; exit |

Crash policy: Session Manager può riavviare Shell senza perdere le app client se il windowing system lo consente; altrimenti recovery session.

---

## 8. Longevità

- `platform.shell.v1` resta stabile anche se si sostituisce il toolkit UI.
- Adapter verso upstream (Plasma) isolati in moduli sostituibili.
- Nessuna business rule AI dentro Shell: evita riscritture ad ogni cambio modello.

---

## 9. Riferimenti

- `../design-system/05-Desktop-Layout.md`
- `05-Ryuk.md`, `02-NovaOS.md`, `06-Nova-Services.md`
