# ADR-008 — Installer Engine

| Campo | Valore |
|-------|--------|
| **ID** | ADR-008 |
| **Titolo** | Scelta del motore di installazione su disco |
| **Stato** | Accettato |
| **Sprint** | Post-Foundation 0.1 → Milestone 0.2 |
| **Data** | 2026-07-25 |
| **Decisori** | Engineering (implementazione su live KIWI esistente) |

---

## 1. Problema

Foundation 0.1 fornisce una Live ISO avviabile ma **non installabile** su disco. Serve un installer stabile, supportato, dual-boot capable, senza regressioni sulla modalità Live e compatibile con la pipeline KIWI attuale (ADR-003).

---

## 2. Alternative valutate

### 2.1 Anaconda (Fedora-native)

Pro: coerenza Fedora, kickstart, familiarità enterprise.  
Contro: integrazione pesante con immagini KIWI live overlay; tipicamente pensato per Lorax/`product.img`; branding e packaging più costosi per M0.2.

### 2.2 Calamares

Pro: già packaging Fedora (`calamares` 3.3.x); default upstream/Fedora già allineati a KIWI/Lorax LiveOS (`/run/rootfsbase`); partitioning Alongside/Replace/Erase/Manual; `os-prober` per dual-boot; UX branding semplice.  
Contro: non è lo strumento “ufficiale” Fedora Workstation (Anaconda).

### 2.3 Installer Nova custom

Pro: controllo totale UX.  
Contro: fuori scope; architettura strangler vieta di riscrivere l’installer al giorno zero.

---

## 3. Decisione

**Adottare Calamares** come motore di installazione per NovaOS Milestone **0.2 (Installable)**.

- Sorgente configurazione: `installer/calamares/`
- Overlay immagine: sincronizzato in `configs/kiwi/novaos-m01/root/` a build-time
- Dual-boot: partitioning Alongside + Manual + `os-prober` / `GRUB_DISABLE_OS_PROBER=false`
- Live: resta overlay KIWI; Calamares è solo un pacchetto + launcher (nessun impatto sul boot live)
- Anaconda resta candidata futura se si passa a media Lorax/Atomic (ADR-006)

---

## 4. Conseguenze

| Area | Impatto |
|------|---------|
| Pipeline | Stesso profilo `novaos-m01` + pacchetti installer/devtools |
| Live | Nessuna regressione richiesta; smoke P0 resta obbligatorio |
| Installato | Utente creato dall’installer; demo `nova` rimossa; autologin disabilitato di default |
| Dual-boot | Best-effort supportato (UEFI + GPT); erase non è default |
| Reversibilità | Rimuovere pacchetti Calamares + overlay `installer/calamares` riporta a live-only |

---

## 5. Riferimenti

- `docs/boot-foundation/05-Installer.md`
- `installer/README.md`
- ADR-001 (Fedora), ADR-003 (KIWI), ADR-005 (SDDM), ADR-006 (mutable DNF)
