# 13 — Nova Wi-Fi Foundation

**Sprint:** 17  
**Stack:** NetworkManager + `wpa_supplicant` (nessun iwd in questo sprint)

## 1. Problema trovato (host NovaOS)

La scheda Wi-Fi (`ath9k` / AR9462, iface `wlp3s0`) era rilevata dal kernel ma NetworkManager
la marcava **`unavailable`** con:

```text
Couldn't initialize supplicant interface: Failed to D-Bus activate wpa_supplicant service
Unable to locate executable '/usr/sbin/wpa_supplicant': No such file or directory
```

Causa: **usrmerge rotto** — `/usr/sbin` era una directory reale (creata da overlay che facevano
`mkdir …/usr/sbin` e installavano script lì) invece del symlink Fedora `/usr/sbin → bin`.
Il pacchetto `wpa_supplicant` installa il binario in `/usr/bin`, mentre l’unit systemd usa
`ExecStart=/usr/sbin/wpa_supplicant`.

## 2. Soluzione

| Componente | Azione |
|------------|--------|
| `scripts/lib/ensure-usrmerge.sh` | Ripristina `/usr/sbin → bin` |
| `scripts/fix-nova-wifi.sh` | Ripara host live + riavvia NM |
| `configs/network/20-novaos-wifi.conf` | Policy NM (`wifi.backend=wpa_supplicant`) |
| `appliance.kiwi` | Pacchetti: `wpa_supplicant`, `iw`, `wireless-regdb`, `linux-firmware` |
| `build-iso.sh` | Post-install in `/usr/bin` (niente `mkdir usr/sbin`) |
| `localrpm` backend | Dopo extract su `/`, ripara usrmerge |
| Nova Center | Sezione Rete: SSID, segnale, IP, sicurezza, autoconnect |

## 3. Autoconnect

I profili Wi-Fi salvati da NetworkManager hanno `connection.autoconnect=yes` di default.
`fix-nova-wifi.sh` e l’uso di NM assicurano che i profili esistenti restino in autoconnect.
All’avvio: NM → D-Bus activate `wpa_supplicant` → radio up → riconnessione profili salvati.

## 4. Live ISO vs installato

Stesso stack in entrambi i casi (KIWI + `config.sh` + post-install Calamares):

- `NetworkManager` + `NetworkManager-wifi` + `wpa_supplicant` + firmware
- Policy in `/etc/NetworkManager/conf.d/20-novaos-wifi.conf`
- Guardrail usrmerge in `config.sh` e `novaos-post-install.sh`

## 5. Nova Center

API `center.v1` / `get_network()` espone `wifi_details[]` con:

- scheda, stato (Connesso/Disconnesso/…), SSID, segnale %, IPv4, sicurezza, autoconnect

## 6. Non-obiettivi

- Migrazione a **iwd**
- Portal captive personalizzato
- Workaround `chmod 777` o GUI come root
