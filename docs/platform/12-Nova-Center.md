# 12 — Nova Center

**Sprint:** 16 — Nova Center Foundation  
**API:** `center.v1`  
**Package:** `nova-center`

## 1. Ruolo

Nova Center è il **pannello di controllo ufficiale** di NovaOS: applicazione nativa nel menu Applicazioni che espone stato sistema, hardware, rete, servizi Nova e ponte verso Nova Update.

## 2. Architettura

| Layer | Path | Responsabilità |
|-------|------|----------------|
| GUI | `desktop/nova-center/nova_center/app.py` | GTK3, sezioni modulari |
| API | `desktop/nova-center/nova_center/api.py` | Facade stabile `center.v1` |
| Backend | `desktop/nova-center/nova_center/backend/` | Collector da `/proc`, `/sys`, `ip`, `systemctl`, socket Update |
| Launcher | `/usr/bin/nova-center` + `org.novaos.Center.desktop` | Menu applicazioni |

Nessun mock: i collector leggono sempre dati live.

## 3. Sezioni

1. Dashboard  
2. Hardware  
3. Rete  
4. Sistema  
5. Nova Services (`nova-updated`, stub Ryuk, AI Core pianificato)  
6. Aggiornamenti (bridge `system.update.v1` + “Apri Nova Update”)

## 4. Ryuk

Lo slot `nova-ryuk` è **predisposto** (catalogo servizi + note UI). Nessun demone, skill o socket Ryuk in questo sprint.

## 4b. Accesso a Nova Update

Nova Center parla con `nova-updated` su `/run/nova/update.sock` (**root:nova** `0660`,
socket activation). L’utente desktop deve appartenere al gruppo `nova` (Calamares /
post-install / `sysusers.d`). Nessun sudo per Check/Status.

## 5. Distribuzione

RPM `nova-center` pubblicabile sul canale Nova Update (`apps`/`nova`) senza ricostruire l’ISO.

## 6. Criteri di uscita Sprint 16

- [x] App avviabile dal menu  
- [x] Dati reali (os-release, hardware, rete, servizi)  
- [x] Integrazione stato Nova Update  
- [x] RPM installabile via Nova Update  
- [ ] Integrazione Ryuk reale (sprint successivi)
