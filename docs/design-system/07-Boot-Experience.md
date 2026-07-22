# 07 — Boot Experience

**NovaOS Design System — Boot, login, first-run**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica ufficiale

---

## 1. Scopo

Definire l’esperienza dalla power-on al desktop Nova Shell: firmware splash (dove controllabile), boot grafico, login, first-run onboarding. È la **prima impressione di brand**.

---

## 2. Filosofia

1. **Silenzio luminoso** — pochi elementi, alta cura.  
2. **Una cosa alla volta** — specialmente in onboarding.  
3. **Brand first** — mark e nome dominano; niente changelog nel primo viewport.  
4. **Fiducia** — progress onesto; nessun fake indeterminate infinito senza fallback.  
5. **AI presentata come opzione di sistema**, non come obbligo cloud.

---

## 3. Sequenza end-to-end

```text
Power → [Firmware] → Nova Boot Splash → Login Greeter → (First Run?) → Nova Shell
```

---

## 4. Nova Boot Splash

| Elemento | Specifica |
|----------|-----------|
| Fondo | `nova.ink.950` pieno |
| Centro | Mark Nova (core+ring) dimensione ~64–96px |
| Wordmark | “NovaOS” sotto, `display.md`, tracking -0.02em |
| Progress | Barra sottile 120–160px, colore `stellar`→`signal` lerp lento **oppure** ring stroke sul mark |
| Messaggi | Opzionali, `caption`, muted; max 1 riga (“Preparazione sistema”) |
| Durata percettiva | Il più breve possibile; animazione ≤ `motion.ritual` |

**Vietato:** log kernel a schermo in build utente; spinner generici multipli; mascotte; citazioni random.

### Motivazione

Il boot è un rito breve di riconoscimento. Troppo testo spezza l’eleganza; troppo vuoto senza progress genera ansia.

---

## 5. Login Greeter (schermata di login)

Superficie: greeter Nova (tematizzazione SDDM secondo ADR, identità Nova).

### Layout

```text
┌──────────────────────────────────────────┐
│              (wallpaper blur)            │
│                                          │
│              [ Nova Mark ]               │
│                                          │
│         ┌────────────────────┐           │
│         │  Avatar / Nome     │           │
│         │  Password / Auth   │           │
│         │  [ Accedi ]        │           │
│         └────────────────────┘           │
│                                          │
│   sessione: Nova Shell        ⏻  🌐     │
└──────────────────────────────────────────┘
```

| Parametro | Valore |
|-----------|--------|
| Card | Glass strong, `radius.xl`, width 380px |
| Input | height 40px, `radius.md` |
| CTA | stellar filled |
| Selettore sessione | Nascosto se unica sessione; se multiplo, label “Nova Shell” in chiaro |
| Power / accessibilità | Angolo basso discreto |
| Orologio | Opzionale alto centro, tipografia display sobria |

### Auth

- Password locale default.
- Percorso futuro NovaCloud: secondario, chiaro nei permessi.
- Errori sotto campo, `state.danger`, senza shake violento.

### Motivazione anti-clone

Niente lista utenti laterale “filmstrip” tipica di alcuni greeter; niente semafori; niente riquadro opaco stile Windows greeter generico senza glass Nova.

---

## 6. Unlock / Lock screen

- Stesso linguaggio del greeter, più minimale (niente wordmark enorme).
- Notifiche lock: solo mittente/conteggio secondo privacy settings.
- Media controls discreti se musica in play.

---

## 7. First-run Onboarding

Nome UI: **Benvenuto in NovaOS** (non “Wizard setup” tecnico).

### Principi

- Max **5 passi** per il percorso semplice.
- Un compito per schermata.
- Skip dove sicuro.
- Nessun stats strip, nessun promo ecosistema nel primo viewport oltre una riga di promessa.

### Passi raccomandati

| # | Titolo | Contenuto |
|---|--------|-----------|
| 1 | **NovaOS** | Brand + una frase: “Il sistema operativo AI-First del tuo ecosistema Nova.” CTA Continua |
| 2 | **Aspetto** | Tema chiaro/scuro + 2–3 wallpaper ufficiali |
| 3 | **NovaAI** | Locale / Ibrido / Disattiva — spiegazione onesta |
| 4 | **Account** | Usa locale / collega NovaCloud (opzionale) |
| 5 | **Pronto** | “Entra in Nova Shell” — CTA unica |

### Layout onboarding

- Full-bleed atmosphere (gradiente ink o wallpaper soft).
- Colonna contenuto max 520px centrata.
- Progress dots `signal`/`steel`, non step numerici rumorosi.
- Nessuna card stack multipla nel hero.

---

## 8. Transizione a Nova Shell

- Crossfade greeter → shell 320ms.
- Horizon Bar entra con rise 8px + fade 240ms.
- Niente tour obbligatorio a spotlight; eventuale “Suggerimento” dismissible una tantum.

---

## 9. Accessibilità boot/login

- High contrast option dal greeter.
- Screen reader labels.
- Focus visibile sugli input.
- Reduced motion: splash statico + progress semplice.

---

## 10. Suoni correlati

Vedi `08-Sound-Design.md`: boot chime opzionale brevissimo; login confirm soft; default volume basso / mute-first policy da valutare.
