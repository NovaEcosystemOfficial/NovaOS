# 02 — Boot Flow

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Descrivere il **flusso di avvio** dalla power-on al desktop utilizzabile per Milestone 0.1, allineato al Design System dove possibile ma **semplificato**: niente Ryuk, niente Nova AI Core, niente onboarding cloud.

Obiettivo percettivo M0.1:

1. Boot corretto  
2. Logo NovaOS  
3. Login personalizzato  
4. Desktop Nova Shell iniziale  
5. Terminale e Impostazioni apribili  
6. Spegnimento / riavvio funzionanti  

---

## 2. Componenti coinvolti

| Componente | Ruolo M0.1 |
|------------|------------|
| Firmware UEFI/BIOS | POST, boot device |
| Bootloader (GRUB/systemd-boot — secondo scelta immagine) | Menu / kickoff kernel |
| Linux kernel + initramfs | Hardware minimo, root pivot |
| systemd | Target grafici |
| Plymouth (o equivalente splash) | Logo NovaOS in early boot |
| SDDM + tema Nova | Login |
| Sessione Nova Shell iniziale | Desktop (Plasma customizzato / look-and-feel Nova) |
| KWin / compositor | Finestre |
| Portali / session tools | Shutdown/reboot |

---

## 3. Flusso operativo

```text
Power On
  → Firmware
  → Bootloader (voce "NovaOS")
  → Kernel + initramfs
  → systemd (default graphical.target)
  → Plymouth: logo NovaOS / splash
  → SDDM (tema Nova): login
  → Avvio sessione "Nova Shell" (desktop iniziale)
  → Horizon Bar / layout ridotto + wallpaper Nova
  → Utente: Terminale, Impostazioni, Spegni/Riavvia
```

### Stati M0.1

| Stato | Criterio |
|-------|----------|
| `BOOTING` | Splash/logo visibile |
| `GREETER` | SDDM con branding Nova |
| `SESSION_STARTING` | Transizione post-login |
| `DESKTOP_READY` | Barra/desktop visibili, input ok |
| `DEGRADED` | Es. audio assente — accettabile se desktop ok |
| `POWER_OFF` / `REBOOT` | Comandi da UI funzionanti |

### Cosa è esplicitamente assente nel flusso M0.1

- Attesa `ai.ready` / `ryuk.ready`  
- First-run NovaCloud / NovaAI  
- Pulse assistente funzionale (può esistere placeholder UI disabilitato o nascosto)

---

## 4. Dipendenze

| Dipendenza | Motivo |
|------------|--------|
| ADR-005 SDDM | Greeter |
| ADR-002 Plasma | Base sessione |
| Design System boot/login | Logo, greeter look |
| Driver GPU minimi | Compositor |
| `03-System-Services.md` | Unità abilitate |

---

## 5. Possibili criticità

| Criticità | Sintomo | Mitigazione |
|-----------|---------|-------------|
| Black screen post-SDDM | Sessione non parte | Fallback sessione Plasma stock di debug; log journal |
| Plymouth nasconde error kernel | Debug difficile | Kernel cmdline temporanea senza quiet/splash |
| Wayland vs X11 su HW specifico | Sessione crash | Provare sessione alternativa; documentare default |
| Autologin accidentale | Salta greeter | Disabilitare autologin in M0.1 ufficiale |
| Shutdown bloccato da app | Hang | Timeout session inhibitor; test espliciti |
| Logo non mostrato | Branding fallito | Verificare path tema Plymouth/SDDM nel rootfs |

---

## 6. Strategia di implementazione

1. **Boot vanilla** Fedora KDE → conferma graphical.target.  
2. **Aggiungere splash** logo Nova (Plymouth theme minimo).  
3. **Tematizzare SDDM** (nome sessione “Nova Shell”).  
4. **Applicare look-and-feel / layout** desktop iniziale.  
5. **Validare power actions** da menu sessione.  
6. Solo dopo: rifiniture motion/blur Design System (non bloccanti M0.1).

### Sessione nominale

- Nome mostrato: **Nova Shell**  
- Implementazione M0.1: sessione basata su Plasma con packaging/branding Nova (strangler: sostituire pezzi dopo).

---

## 7. Riferimenti

- `../design-system/07-Boot-Experience.md`  
- `../platform/10-Boot-Sequence.md` (target lungo termine; M0.1 è subset)  
- `03-System-Services.md`, `10-Milestone-0.1.md`
