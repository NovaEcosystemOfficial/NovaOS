# 15 — Nova Platform Foundation

**Sprint:** 19 — Nova Platform Foundation  
**Package:** `nova-platform` **0.2.5** (Provides: `nova-platform-python`)  
**API:** `platform.v1`  
**Socket:** `/run/nova/platform.sock` (`root:nova` `0660`)  
**Release train:** NovaOS v0.2.5  
**Distribuzione:** solo via Nova Update

> Specifica architetturale storica: [`01-Nova-Platform.md`](01-Nova-Platform.md).  
> Questo documento descrive la **prima implementazione** del Platform Layer.

## 1. Obiettivo

Da Sprint 19 NovaOS espone servizi proprietari usabili da tutte le applicazioni Nova.
Le app **non** devono leggere direttamente `/proc`, `/sys` o `os-release` se esiste un
metodo in `platform.v1`.

## 2. Componenti

| Componente | Ruolo |
|------------|--------|
| **nova-platformd** | Demone Platform Service |
| **nova-platformctl** | CLI (`health`, `ping`, …) |
| **nova_platform** | Libreria Python condivisa (`nova-platform-python`) |
| **/var/log/nova/** | `platform.log`, `update.log`, `services.log` |

## 3. Protocollo

JSON Lines su Unix stream (stesso pattern di `system.update.v1`):

```json
{"api":"platform.v1","id":1,"method":"get-system-info","params":{}}
{"api":"platform.v1","id":1,"result":{...}}
```

## 4. API iniziali

| Method | Descrizione |
|--------|-------------|
| `ping` | Liveness |
| `get-version` | Versione platform + OS |
| `get-hostname` | Hostname / FQDN |
| `get-session` | Contesto sessione (XDG/DISPLAY) |
| `get-uptime` | Uptime |
| `get-network` | Rete / Wi‑Fi (NM) |
| `get-system-info` | Identità sistema completa |
| `get-hardware` | CPU/RAM/disco/GPU/batteria |
| `get-dashboard` | Aggregato health per Nova Center |
| `get-services` | Monitor servizi Nova |
| `health` | Report JSON completo |

Alias PascalCase accettati (`GetSystemInfo`, …).

## 5. Monitor servizi

Il demone sonda periodicamente:

- `nova-platformd` / `platform.sock`
- `nova-updated` / `update.sock`
- `nova-center`, `nova-welcome`, `nova-update-gui` (binary)
- stub pianificati: Ryuk, AI Core

## 6. Health CLI

```bash
nova-platformctl health
```

Output JSON con: `status`, `version`, `sockets`, `services`, `errors`.

## 7. Consumatori

| App | Uso |
|-----|-----|
| **Nova Center 0.2.5+** | Dashboard/Hardware/Rete/Sistema/Services solo via Platform |
| Future Nova Apps | Solo `PlatformClient` / SDK |

Nova Update resta su `system.update.v1` (`/run/nova/update.sock`).

## 8. OTA

```text
nova-platform-0.2.5-1.nova.noarch.rpm
nova-center-0.2.5-1.nova.noarch.rpm   # Requires: nova-platform
novaos-release-0.2.5-1.nova.noarch.rpm
```

Installazione solo con Nova Update. Nessun `dnf`/`rpm` manuale sul host di sviluppo.
