# Nova Shell Foundation

**Vision 2.0** · Pacchetto `nova-shell` 0.2.11 · API `shell.v1`

Chrome esperienza Nova: Top Bar a strut (non overlay), launcher esterno,
API search/dock per evoluzioni future.

## 1. Top Bar (Vision 2.0)

| Regola | Comportamento |
|--------|----------------|
| Strut | `_NET_WM_STRUT` / `_NET_WM_STRUT_PARTIAL` — ridimensiona l’area di lavoro |
| No overlay | Mai sopra le finestre; la X di chiusura resta cliccabile |
| No auto-hide | Rimosso il reveal al bordo superiore |
| Layout | Logo (sx) · centro vuoto · Notifiche · Wi‑Fi · Audio · Batteria* · Ora |

\*Batteria solo se presente. CPU/RAM/Disco/kernel **non** sono nella barra
(→ futuro Control Center).

`TopBarManager` posiziona il pannello `DOCK` e pubblica gli strut EWMH.

## 2. Architettura

```text
nova-shell (GTK3)
   │
   ├─► platform.v1   get-dashboard / get-network / get-hardware / get-services
   ├─► shell.search.v1   QuickSearch.query / execute
   └─► shell.dock.v1     favorites / recent / open_apps (API; UI dock non in questa release)
```

**Regola:** nessuna lettura diretta di `/proc` o `/sys` nel processo Shell.
Metriche solo da Nova Platform.

Logo → `nova-launcher` se installato.

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

Solo **Nova Update** stable.

```bash
nova-updater check
nova-updater apply
```

Poi logout/login (autostart) oppure `nova-shell`.
