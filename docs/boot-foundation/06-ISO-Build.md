# 06 — ISO Build

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Specificare come si costruisce e si valida la **prima ISO NovaOS**: contenuti, profili, naming, dimensioni attese, modalità di scrittura su USB e criteri di accettazione boot.

Obiettivo: **ISO stabile che si avvia sul PC di sviluppo**.

---

## 2. Componenti coinvolti

| Componente | Ruolo |
|------------|-------|
| Image description (KIWI) | Ricetta ISO |
| Pacchetti Fedora KDE minimi + Nova branding RPMs | Contenuto |
| Hybrid BIOS/UEFI ISO | Avvio ampio |
| Strumento flash | `dd`, Fedora Media Writer, Rufus, balenaEtcher, ecc. |
| Checksum | SHA256 |

### Profili immagine M0.1

| Profilo | Descrizione |
|---------|-------------|
| `novaos-m01-live` | **Primario** — live desktop + installer |
| `novaos-m01-dev` | Opzionale — include ssh, debug symbols ridotti, tool build |

Non rilasciati in M0.1: atomic/ostree, netinstall minimal server, edizioni AI.

---

## 3. Flusso operativo

```text
scripts/build-iso.sh (futuro)
  → kiwi-ng system build …
  → artifacts/novaos-0.1.0-x86_64.iso
  → artifacts/novaos-0.1.0-x86_64.iso.sha256
  → smoke: QEMU boot
  → (opzionale) flash USB → boot HW sviluppo
```

### Contenuto software M0.1 (must)

- Kernel + firmware necessari  
- SDDM + tema Nova  
- Sessione Nova Shell iniziale (Plasma branded)  
- Terminale (Konsole o equivalente)  
- Impostazioni (System Settings)  
- Browser opzionale (utile debug; non obbligatorio per gate)  
- Driver base rete/audio/GPU  

### Contenuto vietato M0.1

- Ollama, Ryuk, AI Core  
- Nova Apps ecosistema  
- Store  
- Account sync cloud forzato  

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| `01-Build-Pipeline.md` | Stages |
| `08-Development-Environment.md` | Host |
| Mirror Fedora | Pacchetti |
| Hardware/VM | Validazione |
| ADR-003 | KIWI primario |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| ISO > 4–6 GB | USB lenti / fail tool | Tagliare lingue/pacchetti |
| Solo UEFI o solo BIOS | HW non parte | Hybrid image |
| Secure Boot reject | Panic boot | Doc: disable SB in BIOS per M0.1 dev **oppure** enroll |
| Persistenza live confusa | Bug fantasmi | Test su live pulita |
| Virus scanner Windows sul file ISO | Falsi positivi rari | Checksum + build Linux-side |
| Naming inconsistente | Caos artefatti | Schema fisso sotto |

### Schema naming

```text
novaos-<version>-<arch>-<profile>.iso
es. novaos-0.1.0-x86_64-live.iso
```

---

## 6. Strategia di implementazione

1. Produrre ISO Fedora KDE “remix” minima.  
2. Integrare RPM branding.  
3. Validare QEMU (`-m 4096 -enable-kvm` o equivalente).  
4. Validare su PC di sviluppo (USB).  
5. Congelare ricetta + versione Fedora nel tag git `m0.1`.  
6. Scrivere note note hardware in `07-Hardware-Support.md`.

### Criteri “ISO stabile”

- 3 boot consecutivi OK in VM  
- 1 boot OK su HW sviluppo  
- Nessun `systemctl --failed` critico a idle  
- Checklist M0.1 verde  

---

## 7. Roadmap tecnica ISO (verso M0.1)

| Step | Deliverable | Exit |
|------|-------------|------|
| I1 | Toolchain installata | kiwi --version OK |
| I2 | ISO vanilla boot VM | desktop Fedora visibile |
| I3 | os-release NovaOS + splash logo | brand visibile |
| I4 | SDDM theme Nova | login branded |
| I5 | Nova Shell defaults | layout iniziale |
| I6 | Terminal + Settings | app ok |
| I7 | Poweroff/reboot | ok da UI |
| I8 | USB HW sviluppo | M0.1 dichiarabile |
| I9 | (opz.) Install su disco test | installed boot ok |

---

## 8. Riferimenti

- `01-Build-Pipeline.md`, `05-Installer.md`, `09-Testing-Strategy.md`, `10-Milestone-0.1.md`
