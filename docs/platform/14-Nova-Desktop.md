# 14 — Nova Desktop Experience

**Sprint:** 18 — Nova Desktop Experience  
**Package:** `nova-desktop` **0.2.4**  
**Release train:** NovaOS v0.2.4  
**Distribuzione:** solo via Nova Update (RPM OTA)

> Nota indice: Welcome resta [`14-Nova-Welcome.md`](14-Nova-Welcome.md).  
> Questo documento usa lo stesso prefisso numerico richiesto dallo sprint  
> (`14-Nova-Desktop`); in indice è elencato come Sprint 18 Desktop.

## 1. Obiettivo

Eliminare comportamenti indesiderati residui del desktop Fedora/KDE stock e
rendere login, branding, sessione e notifiche coerenti con l’identità NovaOS.

## 2. Fix login (tastiera virtuale)

- Tema SDDM ufficiale: **`novaos`** (`/usr/share/sddm/themes/novaos`)
- `VirtualKeyboardLoader` sostituito da stub inerte (nessun Qt Virtual Keyboard)
- Pulsante “Virtual Keyboard” nascosto
- Drop-in `/etc/sddm.conf.d/zzz-novaos-desktop.conf` + `zzzz-novaos-no-vkeyboard.conf`:
  - `Current=novaos`
  - `InputMethod=` (kill switch SDDM per qtvirtualkeyboard)
  - `GreeterEnvironment=QT_IM_MODULE=compose,QT_VIRTUALKEYBOARD_DESKTOP_DISABLE=1,…`
- Login: solo tastiera fisica

## 3. Branding Nova

| Elemento | Destinazione |
|----------|--------------|
| Look-and-feel | `org.novaos.desktop` |
| Color scheme | `NovaOS` |
| Wallpaper | `NovaOS` (Ink Field) |
| About System | `/etc/xdg/kcm-about-distrorc` → Nome/Logo NovaOS |
| Defaults | `/etc/xdg/kdeglobals` → LookAndFeelPackage=org.novaos.desktop |
| Icona | `/usr/share/pixmaps/novaos.png` + hicolor |

Voci menu Fedora residue (se presenti) sono nascoste con override in
`/usr/local/share/applications/` (`NoDisplay=true`).

## 4. Nova Session

- `%post` abilita/avvia `nova-updated.socket`
- Autostart `nova-session-check`: verifica broker, socket, `nova-center`, `nova-update-gui`
- Env sessione: `/etc/xdg/plasma-workspace/env/novaos-desktop-env.sh`

## 5. Nova Notifications

Agent: **`nova-notify-agent`** (autostart XDG).

| Evento | Notifica |
|--------|----------|
| Nuovi pending da Nova Update | Aggiornamento disponibile |
| Nuova entry in history | Aggiornamento installato |
| `reboot_required` / pacchetti critici | Riavvio consigliato |

Stato locale: `~/.config/nova/notify-state.json`  
Trasporto: `org.freedesktop.Notifications` (fallback `notify-send`).

## 6. Miglioramenti desktop

- Launcher Center/Update con icona `novaos` e categoria `X-NovaOS`
- Override in `/usr/local/share/applications` (precede `/usr/share`)
- Menu senza duplicati evidenti di entry Fedora nascoste

## 7. Validazione

Dopo `nova-updater apply` di `nova-desktop` 0.2.4:

1. Logout/login: nessuna tastiera virtuale  
2. Informazioni di sistema / About: NovaOS  
3. `nova-session-check` → `NOVA_SESSION_CHECK_OK`  
4. Nova Update e Nova Center avviabili  
5. Con aggiornamenti pending: notifica “Aggiornamento disponibile”

## 8. Pacchetto OTA

```text
nova-desktop-0.2.4-1.nova.noarch.rpm
→ packages/repo/channels/stable/nova/x86_64/
```

**Non** installare a mano su `/usr`. Solo Nova Update.
