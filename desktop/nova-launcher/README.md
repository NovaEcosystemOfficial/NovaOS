# Nova Launcher

Official NovaOS application launcher (`launcher.v1`).

Runs **in parallel** with the KDE Application Launcher. Does not remove Kickoff.

## Open

- Menu applications → **Nova Launcher**
- Nova Shell logo (if `nova-launcher` is installed)
- Shortcut default: **Meta+Space** (configurable)
- CLI: `nova-launcher`

## Select as primary (Plasma)

1. System Settings → Shortcuts → Custom / Application
2. Assign **Meta** or **Meta+Space** to `nova-launcher`
3. Optionally disable Kickoff’s Meta binding

KDE launcher stays installed until a later sprint.

## API

```bash
nova-launcher --json
nova-launcher --search "center"
nova-launcher --set-shortcut "Meta+A"
```

Ryuk can call `nova_launcher.api` / `launcher.search.v1`.
