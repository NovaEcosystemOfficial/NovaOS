# Nova Center

Pannello di controllo ufficiale di NovaOS (Sprint 16).

## Layout

```
desktop/nova-center/
├── bin/nova-center              # launcher → /usr/bin/nova-center
├── org.novaos.Center.desktop    # menu Applicazioni
└── nova_center/
    ├── api.py                   # facade center.v1
    ├── app.py                   # GUI GTK3
    └── backend/                 # collector dati reali
        ├── system_info.py
        ├── hardware.py
        ├── network.py
        ├── services.py          # include stub Ryuk (planned)
        └── updates.py           # bridge system.update.v1
```

## Sezioni

1. **Dashboard** — health, CPU/RAM/disco live, uptime, batteria, Nova Update  
2. **Hardware** — CPU, RAM, disco, GPU, temperatura, batteria  
3. **Rete** — connessione, ethernet, Wi-Fi (SSID, segnale, IP, sicurezza, autoconnect)  
4. **Sistema** — os-release, cartelle Nova, servizi  
5. **Nova Services** — `nova-updated`, Ryuk (predisposto), altri  
6. **Aggiornamenti** — Controlla / Installa aggiornamenti + Apri Nova Update

## API interna

`center.v1` espone `get_dashboard`, `get_hardware`, `get_network`, `get_system`,
`get_services`, `get_updates`, `snapshot`. Pensata per future skill Ryuk / Shell.

## Dipendenze

- Python ≥ 3.11, PyGObject, GTK3  
- Opzionale: `novaos-update` (socket `/run/nova/update.sock`)

## Avvio (dev)

```bash
./desktop/nova-center/bin/nova-center
# headless smoke (dump JSON):
DISPLAY= ./desktop/nova-center/bin/nova-center
```

## Packaging

RPM `nova-center` (`packages/SPECS/nova-center.spec`) — distribuibile via Nova Update.
