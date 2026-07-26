# Nova Hub

**Sprint 21** · Pacchetto `nova-hub` 0.2.7 · API `hub.v1`

Home ufficiale di NovaOS: un unico punto di accesso all’ecosistema, allo stato
sistema e alle azioni rapide. Sostituisce l’idea di utility sparse.

## 1. Ruolo

| Superficie | Ruolo |
|------------|--------|
| **Nova Hub** | Home / launcher ecosistema |
| **Nova Center** | Pannello di controllo dettagliato |
| **Nova Update** | Broker aggiornamenti |

Hub apre Center/Update/terminale/impostazioni/file; non li sostituisce.

## 2. UI

1. **Dashboard** — logo, benvenuto, versione, uptime, CPU/RAM/disco, rete, Platform, Update  
2. **Quick Actions** — Center, Update, Terminale, Impostazioni, File  
3. **Nova Ecosystem** — card placeholder (NovaDocs, NovaPromo, NovaStudio, NovaBeauty, NovaCloud, NovaSky, NovaOS, Ryuk)  
4. **News** — JSON locale `/usr/share/nova/hub/data/news.json` (futuro: server)  
5. **Sistema** — aggiornamenti, servizi, errori, notifiche  

## 3. Architettura

```text
nova-hub (GTK3)
   │
   ├─► platform.v1  (/run/nova/platform.sock)   live metrics
   ├─► system.update.v1 (/run/nova/update.sock) pending / check / apply
   └─► condivide bridge con nova-center se co-installato
```

Codice: `desktop/nova-hub/`. Install: `/usr/share/nova/hub/`, `/usr/bin/nova-hub`.

## 4. Distribuzione

Solo **Nova Update** (stable). Non installare a mano sul host di sviluppo.

```bash
nova-updater check
nova-updater apply
```

Companion: `novaos-release` 0.2.7 (identità NovaOS v0.2.7).
