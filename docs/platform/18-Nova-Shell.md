# Nova Shell Foundation

**Sprint 22** · Pacchetto `nova-shell` 0.2.8 · API `shell.v1`

Inizio dello strato esperienza Nova Shell: chrome proprietario che sostituirà
progressivamente gli elementi desktop stock.

## 1. Componenti (0.2.8)

| Componente | Stato |
|------------|--------|
| **Horizon Bar** | Barra superiore: logo, ora, data, batteria, rete, volume, update, Ryuk |
| **Nova Launcher** | Click sul logo → ricerca istantanea (app/docs/comandi/settings) |
| **Quick Search** | Motore `shell.search.v1` (catalogo pacchettizzato; Ryuk consumer futuro) |
| **Widgets** | CPU, RAM, Disco, Rete, Aggiornamenti (via Platform) |
| **Dock API** | `shell.dock.v1` — preferiti / recent / open (open = stub compositor) |
| **Animazioni** | Fade launcher, slide-in barra, hover CSS |

## 2. Architettura

```text
nova-shell (GTK3)
   │
   ├─► platform.v1   get-dashboard / get-network / get-hardware / get-services
   ├─► shell.search.v1   QuickSearch.query / execute
   └─► shell.dock.v1     favorites / recent / open_apps
```

**Regola:** nessuna lettura diretta di `/proc` o `/sys` nel processo Shell.
Metriche solo da Nova Platform.

Volume: mostrato quando Platform espone `audio`/`volume`; altrimenti `n/d`.

## 3. Percorsi

| Path | Ruolo |
|------|--------|
| `/usr/bin/nova-shell` | Entry point |
| `/usr/share/nova/shell/` | Codice + `data/catalog.json` |
| `/etc/xdg/autostart/org.novaos.Shell.desktop` | Autostart sessione |

## 4. CLI

```bash
nova-shell                 # GUI
nova-shell --json          # snapshot shell.v1
nova-shell --search "hub"  # Quick Search
```

## 5. Distribuzione

Solo **Nova Update** stable. Companion `novaos-release` 0.2.8.

```bash
nova-updater check
nova-updater apply
```

Poi logout/login (autostart) oppure `nova-shell`.
