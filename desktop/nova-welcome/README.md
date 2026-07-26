# Nova Welcome

Esperienza ufficiale di **primo avvio** di NovaOS (Sprint 17).

## Layout

```
desktop/nova-welcome/
├── bin/nova-welcome
├── org.novaos.Welcome.desktop
├── org.novaos.Welcome.autostart.desktop   → /etc/xdg/autostart/
└── nova_welcome/
    ├── app.py          # wizard Qt/PySide6
    └── state.py
```

Condivide helper con Nova Center via `desktop/nova-shared/` (`nova_shared`).

## Comportamento

- Autostart al login (`/etc/xdg/autostart/…`)
- Se esiste `~/.config/nova/welcome-completed` → esce subito (codice 0)
- Al termine scrive il marker e può aprire **Nova Center**
- `--force` riesegue il wizard (solo debug)

## Distribuzione

RPM `nova-welcome` via Nova Update. **Non** installare a mano su `/usr`.
