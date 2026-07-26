# Nova Hub

Home ufficiale di NovaOS (Sprint 21).

## Layout

```text
desktop/nova-hub/
  bin/nova-hub
  org.novaos.Hub.desktop
  data/news.json
  nova_hub/
    api.py          # hub.v1
    app.py          # GTK3 GUI
    backend/        # Platform/Update (condiviso con Center quando presente)
```

## Install

RPM `nova-hub` → `/usr/share/nova/hub/`, `/usr/bin/nova-hub`.

Solo via Nova Update.
