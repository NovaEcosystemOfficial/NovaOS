# Nova Desktop Experience (Sprint 18)

Package **`nova-desktop` 0.2.4** — distributed only via Nova Update.

## Contents

| Area | What |
|------|------|
| Login | SDDM theme `novaos` without Qt Virtual Keyboard |
| Branding | look-and-feel `org.novaos.desktop`, About System, wallpaper, colors |
| Session | `nova-session-check` + enable `nova-updated.socket` on install |
| Notifications | `nova-notify-agent` (available / installed / reboot) |
| Launchers | `/usr/local/share/applications` overrides for Center & Update |

## Validate after OTA apply

1. Login: no virtual keyboard  
2. About System shows NovaOS  
3. `nova-session-check` → OK  
4. `nova-updater check` / GUI works  
5. Notifications after pending updates  
