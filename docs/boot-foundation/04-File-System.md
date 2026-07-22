# 04 — File System

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire il **layout del filesystem** della prima immagine NovaOS: dove vivono branding, temi, defaults della sessione e (futuro) overlay Nova, senza introdurre ancora la gerarchia completa Platform/Ryuk.

Obiettivi M0.1:

- rootfs coerente con Fedora;
- path stabili per logo, greeter, wallpaper, look-and-feel;
- separazione chiaro tra **vendor Fedora** e **overlay Nova**;
- predisposizione non invasiva a future directory `nova/`.

---

## 2. Componenti coinvolti

| Area | Path previsti (proposta) |
|------|---------------------------|
| OS identity | `/etc/os-release`, `/usr/lib/os-release` |
| Plymouth theme | `/usr/share/plymouth/themes/novaos/` |
| SDDM theme | `/usr/share/sddm/themes/novaos/` |
| Wallpapers | `/usr/share/wallpapers/NovaOS/` |
| Look-and-feel / layout | `/usr/share/plasma/look-and-feel/org.novaos.shell/` (nome da confermare in implementazione) |
| Icons/branding | `/usr/share/pixmaps/`, `/usr/share/novaos/branding/` |
| Defaults utente skel | `/etc/skel/.config/` (layout Horizon iniziale) |
| Documentazione locale opzionale | `/usr/share/doc/novaos/` |
| Futuro Platform (non M0.1) | `/usr/lib/nova/`, `/etc/nova/` — **creare solo stub vuoti se utili; niente demoni** |

---

## 3. Flusso operativo

### Build-time

```text
Overlay Nova nel tree di build
  → install files in rootfs paths
  → set default SDDM theme
  → set default Plasma look-and-feel / wallpaper
  → update os-release PRETTY_NAME="NovaOS 0.1"
```

### Runtime (utente nuovo)

```text
Login → skel copia defaults → sessione Nova Shell iniziale
```

### Live vs installed

| Contesto | FS |
|----------|-----|
| Live ISO | Overlay squashfs + cow (comportamento tool di build) |
| Installato | Ext4 (o btrfs se scelto in installer) su root |

Per M0.1 su PC di sviluppo: accettabile **live trial** + install opzionale; priorità = boot funzionante.

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| FHS Linux / Fedora | Compatibilità pacchetti |
| Temi SDDM/Plasma | Path attesi dai componenti |
| Installer | Partizionamento (`05-Installer.md`) |
| Update futuri | Evitare di patchare file Fedora “a mano” senza pacchetto |

**Strategia packaging:** anche in M0.1 preferire file Nova in **pacchetti RPM** (`novaos-branding`, `novaos-sddm-theme`, `novaos-shell-defaults`) invece di copie sparse non tracciate.

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| Sovrascrivere file Fedora senza pacchetto | Update rompe branding | RPM dedicati |
| Path Plasma cambiano tra major | Tema non applica | Pin Fedora; smoke test look-and-feel |
| Skel troppo aggressivo | Confonde utenti esistenti | Skel solo per nuovi utenti |
| Permessi theme | SDDM non legge asset | uid/gid e SELinux contexts corretti |
| Disk pieno in build | Fail | Monitorare size rootfs |

---

## 6. Strategia di implementazione

1. Inventario file minimi branding (logo SVG/PNG, wallpaper 1–2, tema SDDM, splash).  
2. Creare pacchetti `novaos-*` nella image description.  
3. Non creare ancora `/usr/lib/nova/ryuk` o simili.  
4. Documentare ogni path in tabella “source overlay → destinazione”.  
5. Verificare con `rpm -ql novaos-branding` post-build.

### Partitioning di riferimento (installato)

| Mount | FS | Note M0.1 |
|-------|-----|-----------|
| `/boot/efi` | FAT32 | UEFI |
| `/boot` | ext4 | se separato |
| `/` | ext4 (default semplice) | btrfs opzionale dopo |
| swap | file o partition | secondo installer |

Immutabilità rpm-ostree: **non** in M0.1 (ADR-006 trajectoria futura).

---

## 7. Riferimenti

- `01-Build-Pipeline.md`, `05-Installer.md`, `06-ISO-Build.md`  
- Design System branding paths futuri in `branding/`
