# 09 — Testing Strategy

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire come si **testa** la prima build avviabile: cosa è obbligatorio per dichiarare M0.1 verde, cosa è regressione minima, e cosa è fuori scope.

Principio: test **manuali strutturati** + pochi automazioni smoke; niente suite AI/Ryuk.

---

## 2. Componenti coinvolti

| Componente | Ruolo nel test |
|------------|----------------|
| QEMU/KVM reference | Smoke rapido ogni build |
| Reference Dev PC | Gate HW |
| Checklist M0.1 | Accettazione |
| journalctl / systemd | Diagnostica |
| SHA256 | Integrità ISO |

---

## 3. Flusso operativo

```text
Build ISO → checksum
  → Test Tier 0: QEMU boot to greeter (10–15 min)
  → Test Tier 1: QEMU full M0.1 checklist
  → Test Tier 2: USB boot Reference PC checklist
  → (opz.) Test Tier 3: install + reboot installed
  → Esito: PASS / FAIL + log allegati
```

### Tier 0 — Smoke (ogni artefatto)

| # | Caso | Pass |
|---|------|------|
| S1 | ISO monta / QEMU parte | Kernel log senza panic immediato |
| S2 | Splash/logo o almeno graphical target | Greeter visibile |
| S3 | Login con credenziali live/test | Desktop appare |

### Tier 1 — Milestone 0.1 (obbligatorio)

| # | Caso | Pass |
|---|------|------|
| M1 | Boot corretto | Arrivo a greeter senza intervento |
| M2 | Logo NovaOS | Visibile in splash e/o greeter |
| M3 | Login personalizzato | Tema SDDM Nova applicato |
| M4 | Desktop Nova Shell iniziale | Layout/branding riconoscibile |
| M5 | Apertura terminale | Finestra shell ok |
| M6 | Apertura impostazioni | System Settings ok |
| M7 | Spegnimento | Poweroff completa |
| M8 | Riavvio | Reboot torna a greeter/desktop |

### Tier 2 — HW sviluppo

Ripetere M1–M8 su Reference Dev PC via USB.

### Tier 3 — Install (consigliato prima di “stabile”)

| # | Caso | Pass |
|---|------|------|
| I1 | Install guided su VM disk | Success |
| I2 | Reboot installed | M1–M8 ok |

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| `10-Milestone-0.1.md` | Definizione scope |
| `07-Hardware-Support.md` | Reference machines |
| Credenziali live documentate | Utente/password di test |
| Tempo engineer | ~1–2 h per gate completo |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| Test solo “a occhio” | Regressioni | Checklist scritta firmata |
| False pass (autologin) | Greeter non testato | Autologin off nei test ufficiali |
| Flaky USB | Fail spurî | Retest + altro media |
| Non catturare log | Debug impossibile | Salvare `journalctl -b` su fail |
| Scope creep nei test | Ritardo | Vietato testare Ryuk/AI in M0.1 |

---

## 6. Strategia di implementazione

1. Pubblicare checklist stampabile/markdown (questa + `10-Milestone-0.1.md`).  
2. Ogni ISO candidata ha cartella `artifacts/novaos-0.1.0/.../test-report.md`.  
3. Automatizzare Tier 0 appena possibile (script QEMU + expect/screenshot opzionale).  
4. Gate umano obbligatorio su Tier 2.  
5. Fail di M5/M6/M7/M8 = **milestone non dichiarabile**.

### Severità

| Livello | Esempio | Effetto |
|---------|---------|---------|
| Blocker | Non arriva al desktop | STOP |
| Major | Terminale non apre | STOP M0.1 |
| Minor | Wallpaper non ideale | Non blocca |
| Won’t fix M0.1 | Wi-Fi chip raro | Documentare |

---

## 7. Riferimenti

- `06-ISO-Build.md`, `10-Milestone-0.1.md`, `02-Boot-Flow.md`
