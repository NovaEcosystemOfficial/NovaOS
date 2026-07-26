# 14 — Nova Welcome (First Boot)

**Sprint:** 17 — Nova Welcome  
**API:** `welcome.v1` (+ `desktop.shared.v1`)  
**Package:** `nova-welcome` **0.2.3**  
**Release train:** NovaOS v0.2.3

> Nota indice: il documento Wi-Fi resta [`13-Nova-WiFi.md`](13-Nova-WiFi.md).  
> Welcome è il documento **14** (il path `13-Nova-Welcome` richiesto in sprint confliggeva con Wi-Fi).

## 1. Ruolo

**Nova Welcome** è il wizard ufficiale di primo avvio. Sostituisce esperienze
riconducibili a Fedora/KDE nel first-run: branding, copy e flusso sono solo NovaOS.

## 2. Flusso

1. Benvenuto + logo/titolo NovaOS  
2. Hostname (applicazione via `hostnamectl`)  
3. Tema: Nova Dark / Nova Light (catalogo estensibile)  
4. Collegamenti Ecosystem (GitHub, Discord, sito, docs)  
5. Riepilogo  
6. “NovaOS è pronto.” → apre **Nova Center** e scrive il marker di completamento  

## 3. Persistenza

- Marker: `~/.config/nova/welcome-completed`  
- Tema: `~/.config/nova/theme`  
- Se il marker esiste, `nova-welcome` esce subito (autostart no-op)

## 4. Autostart

- Sistema: `/etc/xdg/autostart/org.novaos.Welcome.desktop`  
- Skel nuovi utenti: `/etc/skel/.config/autostart/org.novaos.Welcome.desktop`

## 5. Architettura

| Path | Ruolo |
|------|--------|
| `desktop/nova-welcome/` | GUI Qt/PySide6 |
| `desktop/nova-shared/` | Hostname, temi, launch Center, path config |
| RPM `nova-welcome` | Distribuzione via Nova Update |

## 6. Distribuzione OTA

Solo Nova Update. Nessuna installazione manuale su `/usr` dalla macchina di sviluppo.
