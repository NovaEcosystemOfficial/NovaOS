# Nova Platform (`nova-platform` / `nova-platform-python`)

Sprint 19 — first proprietary platform layer for NovaOS.

| Artefact | Path |
|----------|------|
| Daemon | `nova-platformd` → `/run/nova/platform.sock` |
| CLI | `nova-platformctl` |
| Library | `nova_platform` under `/usr/lib/nova/platform/` |
| Logs | `/var/log/nova/{platform,update,services}.log` |
| API | `platform.v1` (JSON Lines) |

## Dev smoke

```bash
NOVA_PLATFORM_SOCKET=/tmp/nova-platform.sock \
NOVA_PLATFORM_LOG_DIR=/tmp/nova-logs \
./system/platform/bin/nova-platformd --foreground -v &

NOVA_PLATFORM_SOCKET=/tmp/nova-platform.sock \
./system/platform/bin/nova-platformctl health
```

Distributed only via Nova Update (RPM `nova-platform`).
