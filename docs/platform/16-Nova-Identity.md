# 16 — Nova Identity

**Sprint:** 20 — Nova Identity  
**Package:** `nova-identity` **0.2.6**  
**Release train:** NovaOS v0.2.6  
**Distribuzione:** solo via Nova Update

## 1. Obiettivo

Ogni superficie utente deve comunicare **NovaOS**, non Fedora.
Identity centralizza asset, personalizza il terminale e fornisce i comandi
ufficiali di riconoscimento del sistema.

## 2. Asset condivisi (`/usr/share/nova/assets/`)

| Path | Contenuto |
|------|-----------|
| `logo/` | `novaos.png`, `novaos.svg` |
| `icons/hicolor/` | icone app |
| `colors/` | schema colori Plasma `NovaOS` |
| `fonts/` | token CSS (`novaos-tokens.css`) |
| `wallpaper/NovaOS/` | wallpaper ufficiale |
| `splash/` | Plasma splash QML + mark |
| `palette/novaos.json` | palette e path canonici |
| `sddm/theme.conf` | greeter punta agli asset condivisi |

Tutte le applicazioni Nova devono usare questi path (vedi `nova_shared.paths`).

## 3. Branding desktop

- Splash Plasma: look-and-feel `org.novaos.desktop`
- Boot: tema Plymouth `novaos` (se plymouth attivo)
- Login: SDDM `novaos` + logo/wallpaper da assets
- About System: `kcm-about-distrorc` → Nome/Logo NovaOS
- Wallpaper / color scheme / pixmaps pubblicati anche nei path tradizionali

## 4. Nova Terminal

- Prompt bash/zsh: prefisso **NovaOS**
- Banner interattivo (`nova-version` + hint `nova-about`)
- Profilo Konsole `NovaOS` (colori brand, font mono)

## 5. Comandi

| Comando | Output |
|---------|--------|
| `nova-about` | Logo ASCII + versione/kernel/platform/center/update/host/CPU/RAM/GPU |
| `nova-info` | JSON riassuntivo |
| `nova-version` | Stringa versione |
| `nova-health` | Health Platform (JSON) |
| `nova-diagnose` | Path, binary, health |

## 6. Consumatori

- **Nova Center 0.2.6** — logo header da `/usr/share/nova/assets/logo/`
- **Nova Welcome 0.2.6** — logo pagina benvenuto + Icon=`novaos`
- **Nova Desktop 0.2.6** — Requires `nova-identity`; SDDM theme.conf dagli assets

## 7. OTA

```text
nova-identity-0.2.6-1.nova.noarch.rpm
(+ companion: novaos-release, nova-center, nova-welcome, nova-desktop, nova-update-gui 0.2.6)
```

Installazione solo tramite Nova Update / Nova Center. Nessun deploy host automatico.
