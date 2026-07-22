# 02 — NovaOS

**System Layer Architecture**  
**Sprint:** 3 — Architettura software  
**Stato:** Specifica ufficiale (pre-implementazione)

---

## 1. Scopo

Definire **NovaOS** come strato di sistema operativo: il nucleo che governa sessione, dispositivi, configurazione, aggiornamenti host e l’integrazione con la Linux Foundation, esponendo servizi stabili agli strati superiori.

NovaOS (system layer) ≠ Nova Shell (experience) ≠ Nova Platform (contratto globale).  
Qui si descrive il **sistema**.

---

## 2. Responsabilità

| Area | Responsabilità |
|------|----------------|
| Sessione | Login, lock, switch user, idle, logout |
| Host lifecycle | Boot handoff, shutdown, reboot, sleep/hibernate |
| Configurazione | Store impostazioni di sistema, profili |
| Device | Eventi HW, power, display, input di base |
| Update host | Coordinamento con DNF / futuro rpm-ostree (ADR-006) |
| Integrazione pacchetti | Repo Nova, pinning, health |
| Security baseline | Hardening, policy agent, secure defaults |
| Supervisione servizi | Unit di sistema Nova (ready state) |

### Non responsabilità

- Rendering UI desktop (Nova Shell)
- Orchestrazione LLM (Nova AI Core)
- Dialogo assistente (Ryuk)
- Business logic delle app ecosistema

---

## 3. Architettura

```text
┌──────────────────────────────────────────────┐
│                 NovaOS System                │
│  ┌────────────┐ ┌────────────┐ ┌───────────┐ │
│  │ Session    │ │ Config     │ │ Device    │ │
│  │ Manager    │ │ Store      │ │ Broker    │ │
│  └────────────┘ └────────────┘ └───────────┘ │
│  ┌────────────┐ ┌────────────┐ ┌───────────┐ │
│  │ Update     │ │ Service    │ │ Policy    │ │
│  │ Broker     │ │ Supervisor │ │ Agent     │ │
│  └────────────┘ └────────────┘ └───────────┘ │
│              Nova Bus (system side)          │
└──────────────────────┬───────────────────────┘
                       │
              Linux Foundation (Fedora base)
```

### Componenti

| Componente | Funzione |
|------------|----------|
| **Session Manager** | Coordina greeter → sessione grafica Nova Shell |
| **Config Store** | Key-value gerarchico versionato (`nova.*`) |
| **Device Broker** | Normalizza eventi udev/power/display |
| **Update Broker** | Espone stato update; deleca a DNF/ostree backend |
| **Service Supervisor** | Ordine e health di servizi Nova (`nova-*`) |
| **Policy Agent** | Applica policy locali (kiosk, focus, privacy defaults) |

---

## 4. Flusso di comunicazione

### 4.1 Avvio sessione

```text
SDDM/Greeter → Session Manager → avvia Nova Shell
                              → segnala session.started su Nova Bus
                              → Service Supervisor verifica dipendenze sessione
```

### 4.2 Aggiornamento

```text
Update UI / Ryuk → Update Broker → backend (DNF | rpm-ostree)
                                → eventi update.available / update.applied
                                → Audit
```

### 4.3 Cambio impostazione di sistema

```text
Settings App / Shell → Config Store → evento config.changed
                                    → consumatori (Shell, Services, AI policy)
```

---

## 5. Dipendenze

| Dipendenza | Tipo |
|------------|------|
| Linux kernel / systemd (o init scelto) | Runtime |
| Packaging DNF/RPM | Distribuzione |
| Display Manager (SDDM) | Login grafico |
| Nova Services | Molti servizi girano “su” NovaOS |
| Security model | Policy Agent |

**Dipendenti:** Nova Shell, Ryuk (per azioni sistema), Update UI, Installer post-boot.

---

## 6. API interne

### `system.session.v1`

| Metodo | Descrizione |
|--------|-------------|
| `GetState()` | active/locked/greeter |
| `Lock()` / `Unlock()` | Lock screen |
| `Logout()` / `Reboot()` / `Shutdown()` | Con conferma policy |
| `Subscribe(SessionEvents)` | stream eventi |

### `system.config.v1`

| Metodo | Descrizione |
|--------|-------------|
| `Get(key)` / `Set(key,value)` | Con schema validation |
| `Watch(prefix)` | notifiche |
| `ExportProfile()` / `ImportProfile()` | backup impostazioni |

### `system.device.v1`

| Metodo | Descrizione |
|--------|-------------|
| `ListDevices()` | snapshot |
| `Subscribe(DeviceEvents)` | plug/unplug/power |

### `system.update.v1`

| Metodo | Descrizione |
|--------|-------------|
| `Check()` / `Apply()` | secondo backend |
| `GetChannel()` / `SetChannel()` | stable/beta/dev |
| `GetProgress()` | stato |

### `system.supervisor.v1`

| Metodo | Descrizione |
|--------|-------------|
| `ListUnits()` | servizi Nova |
| `Restart(unit)` | privilegiato |
| `Health()` | ready/degraded |

---

## 7. Ciclo di vita

| Stato host | Comportamento NovaOS |
|------------|----------------------|
| Booting | Service Supervisor porta online i target `nova-system.target` |
| Ready | Session Manager in ascolto del greeter |
| In session | Config/Device/Update attivi |
| Updating | Modalità manutenzione; Shell può mostrare UI |
| Shutting down | Stop ordinato: Apps → Shell → Ryuk → AI Core → Services → System |

Persistenza: Config Store su disco cifrato se FDE attiva; segreti mai in plain config.

---

## 8. Evoluzione a 10 anni

- Backend update sostituibile (DNF → rpm-ostree → bootc) senza cambiare `system.update.v1` semanticamente.
- Session Manager resta stabile anche se Nova Shell viene riscritta.
- Policy Agent acquisisce profili enterprise senza accoppiare le app.

---

## 9. Riferimenti

- ADR-001, ADR-006
- `01-Nova-Platform.md`, `10-Boot-Sequence.md`, `09-Security.md`
