# 08 — Development Environment

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire l’**ambiente di sviluppo e build** necessario per produrre e testare la prima ISO NovaOS in modo ripetibile sul PC del team.

Obiettivo: un nuovo engineer può preparare la macchina seguendo questo documento e arrivare a build+boot senza folklore orale.

---

## 2. Componenti coinvolti

| Componente | Ruolo |
|------------|-------|
| OS host consigliato | **Fedora** (stessa major target dell’immagine, o N-1 documentata) |
| KIWI NG + dipendenze | Build ISO |
| QEMU/KVM + virt-manager opzionale | Test senza USB |
| Git | Sorgenti overlay/ricette |
| DNF | Pacchetti host |
| USB tool | Flash su HW |
| Editor / IDE | Documentazione e futuri file ricetta |

### Non richiesti per M0.1

- Cluster build  
- Account Nova Cloud  
- GPU NVIDIA dedicata  
- Installazione Ollama  

---

## 3. Flusso operativo (setup host)

```text
1. Installare Fedora workstation/server su host di build
2. Abilitare virtualizzazione nel BIOS
3. dnf install: kiwi, qemu-kvm, git, … (lista da congelare in scripts/)
4. Clonare repo NovaOS
5. Verificare spazio disco (≥ 80 GB liberi consigliati)
6. Eseguire build ISO (quando gli script esisteranno)
7. Boot in QEMU; poi USB su Reference Dev PC
```

### Layout directory di lavoro proposto

```text
~/novaos-build/          # fuori git o gitignored artifacts
  cache/                 # dnf/kiwi cache
  artifacts/             # ISO generate
repo NovaOS/             # questo repository
  docs/boot-foundation/  # queste specifiche
  (futuro) image/        # kiwi descriptions
  (futuro) overlay/      # branding files
  scripts/               # entrypoint build
```

---

## 4. Dipendenze

| Dipendenza | Criticità |
|------------|-----------|
| Rete verso mirror Fedora | Alta |
| KVM disponibile | Alta per test veloci |
| Diritti root/sudo per kiwi | Alta |
| RAM host ≥ 16 GB consigliata | Media-Alta durante build |
| Conoscenza ADR stack | Media |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| Build su Windows host nativo | KIWI non idiomatico | WSL2 limitato; **preferire VM/host Fedora** |
| Nested virt assente | QEMU lento | Usare host bare-metal Fedora |
| SELinux blocca kiwi paths | Fail build | Context corretti / doc troubleshooting |
| Due engineer con Fedora diverse | Drift | Pin major + container build futuro |
| Artefatti committati per sbaglio | Repo gonfio | `.gitignore` già esclude `*.iso` |

---

## 6. Strategia di implementazione

1. Scrivere checklist setup host (markdown → poi script `scripts/setup-build-host.sh`).  
2. Congelare versioni tool (`kiwi --version` nel README build).  
3. Fornire comando QEMU “golden” per smoke test.  
4. Separare profili: `build-host` vs `test-vm` vs `reference-pc`.  
5. Non mescolare sviluppo app ecosistema con build ISO sullo stesso critical path.

### Comando QEMU di riferimento (specifica, non codice repo ancora)

Parametri target da documentare in script futuro:

- memoria ≥ 4096 MB  
- UEFI firmware (`OVMF`)  
- CPU host passthrough se possibile  
- disco ISO come CD-ROM  

---

## 7. Riferimenti

- `01-Build-Pipeline.md`, `06-ISO-Build.md`, `07-Hardware-Support.md`  
- ADR-001, ADR-003
