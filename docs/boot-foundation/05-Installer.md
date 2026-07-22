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

1. **Decisione engine** entro inizio implementazione ISO: default proposto **Anaconda** (coerenza Fedora) salvo spike contrario.  
2. Prima ISO: live + installer stock branded minimally.  
3. Nascondere/skip moduli cloud/AI.  
4. Post-install: stesso look SDDM + Nova Shell della live.  
5. Test install su **VM** prima del PC fisico di sviluppo.  
6. Checklist: reboot installed system passa criteri M0.1.

### UX vincoli (Design System light)

- Titolo prodotto NovaOS  
- Niente promo ecosistema nel primo schermo  
- Un compito per step  

---

## 7. Roadmap installer (oltre M0.1)

| Versione | Capacità |
|----------|----------|
| 0.1 | Live + install base |
| 0.2 | Branding installer più completo |
| 0.3+ | Onboarding Design System (tema, senza AI ancora) |
| 1.x | Opzioni NovaAI/Cloud come da platform docs |

---

## 8. Riferimenti

- `06-ISO-Build.md`, `02-Boot-Flow.md`, `10-Milestone-0.1.md`  
- `../design-system/07-Boot-Experience.md` (target; subset ora)
