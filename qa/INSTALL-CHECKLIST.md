# NovaOS 0.2 — Install checklist (Tier 3)

Use this after `sudo make iso` and preferably after `sudo make install-gate`.

## A. Live regression (must PASS)

| # | Check | Pass when |
|---|-------|-----------|
| L1 | Boot ISO in VM (UEFI) | Greeter/autologin → Plasma |
| L2 | `make smoke` / P0 desktop | plasmashell or kwin-plasma |
| L3 | Desktop shows **Install NovaOS** | Icon / app menu entry opens Calamares |
| L4 | NetworkManager | Wi‑Fi/Ethernet UI works in live |

## B. Clean-disk install (VM)

| # | Check | Pass when |
|---|-------|-----------|
| I1 | Calamares welcome | Product name NovaOS |
| I2 | Partition: **Erase disk** (VM only) | Confirmed after prompt (`prompt-install: true`) |
| I3 | Create admin user ≠ `nova` | Password ≥ 6 chars |
| I4 | Install completes | Finished page; reboot |
| I5 | Boot from disk | SDDM login (no autologin) |
| I6 | Session | Plasma X11; Konsole; System Settings |
| I7 | Network | NetworkManager connects |
| I8 | Devtools | `gcc --version`, `make --version`, `git --version` |
| I9 | Demo user gone | `id nova` fails |
| I10 | Marker | `/etc/novaos/install-state` contains `mode=installed` |

## C. Dual-boot (VM with pre-existing OS or free space)

| # | Check | Pass when |
|---|-------|-----------|
| D1 | Pre-seed second OS or free partition | Visible in Calamares |
| D2 | Choose **Alongside** or **Manual** | Existing partitions not wiped unexpectedly |
| D3 | Install NovaOS to free space | Completes |
| D4 | GRUB menu | Shows NovaOS + other OS (os-prober) |
| D5 | Boot other OS | Other OS still starts |
| D6 | Boot NovaOS | Login + Plasma OK |

## D. Hardware (real machine)

Same as B/C with UEFI. Prefer Manual partitioning if unsure.  
**Never** select Erase disk on a machine with data you need.

## Commands

```bash
make validate
sudo make setup && make check
sudo make iso
sudo make p0-gate          # live stability
sudo make install-gate     # installer present in ISO
make smoke                 # live desktop smoke
```
