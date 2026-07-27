# Nova Launcher

**Sprint 22** · Pacchetto `nova-launcher` 0.2.10 · API `launcher.v1`

Launcher ufficiale di NovaOS. In questa fase gira **in parallelo** al menu
applicazioni KDE (Kickoff): non lo elimina. Può essere scelto come predefinito
assegnando Meta / Meta+Space nelle scorciatoie Plasma.

## 1. Apertura

| Metodo | Dettaglio |
|--------|-----------|
| Icona Nova (Shell) | Se `nova-launcher` è installato |
| Menu applicazioni | Voce **Nova Launcher** |
| Scorciatoia | Default `Meta+Space` (`--set-shortcut`) |
| CLI | `nova-launcher` |

## 2. Layout

- Ricerca in alto
- Azioni rapide (Center, Update, Terminale, File, Impostazioni, Riavvia, Spegni)
- Applicazioni preferite
- Tutte le applicazioni (database `.desktop` / Gio)
- Documenti recenti (Gtk RecentManager)

## 3. Architettura

```text
nova-launcher (GTK3)
  ├─ apps.py       Gio.AppInfo / .desktop
  ├─ search.py     launcher.search.v1  (Ryuk-ready)
  ├─ favorites.py  ~/.config/nova/launcher-favorites.json
  ├─ recent.py     documenti recenti
  ├─ actions.py    azioni rapide
  └─ api.py        facade launcher.v1
```

Modulo separato da Center / Update / OTA. Nessuna modifica a quei componenti.

## 4. Design

Tema NovaOS (palette `#0f2744`), angoli 18px, tile con hover, fade open/close.
Nessun chrome Kickoff/KDE nella UI.

## 5. Distribuzione

Solo Nova Update stable.

```bash
nova-updater check
nova-updater apply
nova-launcher
```
