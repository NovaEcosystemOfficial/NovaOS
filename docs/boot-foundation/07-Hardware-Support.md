# 07 — Hardware Support

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire il **perimetro hardware** supportato per la prima ISO: cosa è ufficialmente target, cosa è best-effort, come si diagnostica, e come si evita di inseguire ogni periferica prima del boot stabile.

Priorità: **PC di sviluppo del team** + VM di riferimento.

---

## 2. Componenti coinvolti

| Area | Stack tipico M0.1 |
|------|-------------------|
| Architettura | **x86_64** only |
| Firmware | UEFI preferito; BIOS legacy best-effort |
| CPU | Intel/AMD con estensioni virtualizzazione utili in host di build |
| GPU | iGPU Intel/AMD; NVIDIA proprietario **non** requisito M0.1 |
| Input | Tastiera/mouse USB |
| Storage | NVMe/SATA; USB 3 stick per ISO |
| Rete | Ethernet e Wi-Fi comuni via kernel Fedora |

---

## 3. Flusso operativo (qualifica HW)

```text
1. Dichiarare "Reference Dev PC" (modello, CPU, GPU, BIOS version)
2. Dichiarare "Reference VM" (QEMU/KVM, 4+ GB RAM, virtio)
3. Boot ISO → raccogliere: journal, lspci, lsusb, dmesg errori
4. Classificare: Supported / Best-effort / Unsupported
5. Aggiornare questa matrice ad ogni ritrovamento rilevante
```

### Matrice iniziale (da compilare in implementazione)

| Classe | Esempio | Policy M0.1 |
|--------|---------|-------------|
| Reference | PC sviluppo team | Deve passare checklist |
| VM reference | QEMU/KVM q35 | Deve passare checklist |
| Best-effort | Altro laptop consumer | Fix solo se bloccante banale |
| Unsupported | ARM, pre-UEFI esotici | Nessun impegno M0.1 |

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| Kernel/firmware Fedora | Abilitazione device |
| Mesa / drivers | Compositor |
| Secure Boot policy | Vedi ISO build |
| Spazio USB ≥ size ISO | Flash |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| NVIDIA proprietary need | Wayland/SDDM issue | Usare iGPU o nouveau best-effort; doc known issue |
| Wi-Fi needs out-of-tree | No rete | Ethernet/tethering per debug |
| Old GPU no GLES | Shell effects crash | Disabilitare effetti; composizione soft |
| USB stick lento/corrotto | Boot random fail | Verificare SHA256; altro stick |
| Secure Boot | Blocco | Disabilitare in BIOS per fase M0.1 dev |
| Hybrid graphics switch | Black screen | Kernel params documentati (nomodeset emergenza) |

### Escape hatch di boot

Documentare voci GRUB temporanee:

- `nomodeset`  
- rimozione `quiet rhgb` per debug  
- sessione Plasma di fallback se Nova Shell defaults rompono  

---

## 6. Strategia di implementazione

1. Schedare **un** PC fisico + **una** VM come gate ufficiali M0.1.  
2. Non accettare bug HW esotici come bloccanti milestone.  
3. Tenere `known-issues.md` (futuro) sotto boot-foundation o wiki interna.  
4. Firmware update del PC di sviluppo consigliato prima dei test.  
5. RAM minima: **4 GB** (8 GB consigliati).  

### Target non-goal M0.1

- Certificazione vendor  
- Tablet/2-in-1 gesture perfette  
- HiDPI multi-monitor edge cases (best-effort)  
- Raspberry / ARM  

---

## 7. Riferimenti

- `06-ISO-Build.md`, `09-Testing-Strategy.md`, `08-Development-Environment.md`
