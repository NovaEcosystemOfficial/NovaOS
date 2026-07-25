# 05 — Installer

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire la strategia **installer** per la prima ISO. Per M0.1 l’obiettivo primario è una ISO che **si avvii correttamente sul PC di sviluppo**; l’installazione su disco è altamente desiderabile ma può essere:

- **percorso A (consigliato):** live ISO + installer grafico Fedora/Calamares/Anaconda opportunamente branded;
- **percorso B (accettabile per smoke HW):** live-only senza install, se il disco di sviluppo è riservato a VM.

Scope installer M0.1: **funzionale e sobrio**, non ancora il full Design System onboarding (NovaCloud/AI).

---

## 2. Componenti coinvolti

| Componente | Ruolo |
|------------|-------|
| Live environment | Desktop Nova Shell iniziale avviabile senza install |
| Installer engine | Anaconda (Fedora-native) **o** Calamares (se adottato) |
| Branding installer | Logo, titolo “NovaOS”, pochi wallpaper |
| Bootloader install | GRUB/systemd-boot su target disk |
| Account setup | Creazione utente admin locale |

**Non inclusi:** wizard NovaAI, NovaCloud link, Ryuk intro, Store.

---

## 3. Flusso operativo

### Percorso Live-first (raccomandato M0.1)

```text
Boot ISO
  → Prova NovaOS (live)
  → [opzionale] Avvia Installer
       → Lingua / tastiera
       → Disco (guided)
       → Utente + password
       → Installazione
       → Riavvio → SDDM Nova → Nova Shell
```

### Flusso minimo accettabile “dev only”

```text
Boot ISO live → valida Milestone checklist → (install dopo)
```

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| Scelta engine installer | Allineare a KIWI/livemedia output |
| Firmware UEFI sul PC target | Preferito |
| Spazio disco target | ≥ 25 GB liberi consigliati |
| `04-File-System.md` | Layout partizioni |
| Branding assets | Logo |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| Anaconda custom branding complesso | Ritardo | Branding minimo; accettare UI upstream con nome NovaOS |
| Calamares vs Fedora packaging | Integrazione extra | Valutare solo se riduce tempo netto |
| Installer cancella disco sbagliato | Data loss | Guided + conferma esplicita; test solo su VM/disco dedicati |
| Secure Boot | Boot fallisce | Documentare stato (signed vs enrolled keys) in M0.1 |
| Dual boot | Complessità | Fuori scope M0.1 ufficiale; best-effort |
| OEM/BitLocker alien | Confusione | Avviso in docs HW |

---

## 6. Strategia di implementazione

1. **Decisione engine:** **Calamares** (ADR-008) sulla Live KIWI esistente; Anaconda riservata a futuri media Lorax/Atomic.  
2. ISO 0.2: live + installer branded minimally (`installer/calamares/`).  
3. Dual-boot: partitioning Alongside/Manual + `os-prober`; erase non è default.  
4. Post-install: SDDM senza autologin demo; rimozione utente `nova`; GRUB con altri OS.  
5. Test install su **VM** (`qa/INSTALL-CHECKLIST.md`) prima del PC fisico.  
6. Gate: `make validate-installer` + `sudo make install-gate` + checklist Tier 3.

### UX vincoli (Design System light)

- Titolo prodotto NovaOS  
- Niente promo ecosistema nel primo schermo  
- Un compito per step  

---

## 7. Roadmap installer

| Versione | Capacità |
|----------|----------|
| 0.1 | Live only (freeze foundation) |
| **0.2** | **Live + Calamares install + dual-boot best-effort** |
| 0.3+ | Onboarding Design System (tema, senza AI ancora) |
| 1.x | Opzioni NovaAI/Cloud come da platform docs |

---

## 8. Riferimenti

- `06-ISO-Build.md`, `02-Boot-Flow.md`, `10-Milestone-0.1.md`  
- `../design-system/07-Boot-Experience.md` (target; subset ora)
