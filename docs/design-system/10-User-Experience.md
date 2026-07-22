# 10 — User Experience

**NovaOS Design System — UX di sistema**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica UX ufficiale

---

## 1. Scopo

Tradurre brand e layout in **comportamenti**, flussi e qualità dell’esperienza su Nova Shell. Completa i documenti visuali con la dimensione interazionale.

---

## 2. Promessa UX

> Nova Shell ti fa lavorare in fretta, con calma, e con un’intelligenza di sistema che puoi capire e spegnere.

KPI qualitativi (non numerici in Sprint 2):

- Tempo a “mi sento a casa” dopo first-run: entro la prima sessione.
- Zero ambiguità “dove lancio le app / dove è l’AI / dove sono le notifiche”.
- Nessun flusso critico dipende dall’AI.

---

## 3. Modello mentale dell’utente

L’utente deve costruire rapidamente questa mappa:

| Bisogno | Dove |
|---------|------|
| Aprire app / cercare | Nova Core → Launcher |
| App recenti / finestre | Focus Strip |
| Chiedere al sistema | Pulse → NovaAI |
| Notifiche | Notification Center (destra) |
| Toggles rapidi | Control Center |
| Impostazioni profonde | App Impostazioni |
| File | File manager Nova (futuro) / Places nel launcher |

Se un feature non entra in questa mappa, va ripensata.

---

## 4. Flussi fondamentali

### 4.1 Cold start → produttività

Boot → Login → (Onboarding se first-run) → Horizon Bar pronta → Launcher con search focusable via shortcut.

### 4.2 Invocare NovaAI

1. Shortcut globale / click Pulse.  
2. Stage o inline a seconda del contesto.  
3. Se l’azione modifica file/sistema: **preview + conferma**.  
4. Indicatore Locale vs Cloud sempre visibile.

### 4.3 Gestire interruzioni

- Notifica non critica: silenziosa in center.  
- Critica: banner breve + `snd.critical` se audio on.  
- Focus mode: sopprime non-critical.

### 4.4 Installare/aggiornare (target)

- Update UI onesta (ADR-006).  
- Riavvio richiesto: spiegato, schedulabile.  
- AI può riassumere il changelog; non può forzare reboot.

---

## 5. Onboarding UX (dettaglio comportamentale)

Vedi anche `07-Boot-Experience.md`.

- Percorso semplice default; “Avanzate” collassate.
- Passo NovaAI: tre radio chiare con conseguenze in una frase ciascuna.
- Fine onboarding: **un** CTA “Entra in Nova Shell”.
- Checklist post-onboarding opzionale (3 item) nel Notification Center come suggerimenti dismissibili — non modal bloccante.

---

## 6. Pattern di interazione

### 6.1 Bottoni

| Tipo | Uso |
|------|-----|
| Primary | stellar filled — un solo primary per view |
| Secondary | glass/outline |
| Ghost | azioni terziarie |
| Danger | state.danger outlined/filled solo per conferma |

Altezza default 36–40px; padding orizzontale 14–16px; `radius.md`.

### 6.2 Input

Altezza 40px; focus ring 2px `signal` o `stellar` secondo contesto (AI vs form sistema). Placeholder muted; mai placeholder come unica label.

### 6.3 Menu contestuali

Item 32px; hover wash 6–8% white/black; freccia submenu; scorciatoie allineate.

### 6.4 Drag & drop

Ghost opaco 80%; hotspot chiari; no animazioni lunghe al drop.

### 6.5 Undo

Dove possibile, toast con Undo 5–8s per azioni reversibili non distruttive.

---

## 7. Feedback e stati

Ogni superficie critica definisce: **empty, loading, error, offline, permission denied, AI unavailable**.

Esempi copy (tono):

| Stato | Esempio |
|-------|---------|
| Empty notifiche | “Niente di nuovo.” |
| AI offline | “NovaAI locale non disponibile. Puoi riprovare o continuare senza AI.” |
| Cloud denied | “Accesso cloud disattivato nelle preferenze.” |
| Error generico | “Qualcosa non ha funzionato. Riprova. Se continua, apri Diagnostica.” |

---

## 8. Accessibilità UX

- Navigazione tastiera completa su chrome shell.
- Focus ring sempre visibile (token dedicato).
- Target minimi 28–40px.
- Contrasto secondo `02-Color-Palette.md`.
- Screen reader labels su Core, Pulse, Quick.
- Non basare l’info solo su colore o solo su suono.

---

## 9. Internazionalizzazione

- Italiano come lingua di specifica; UI strings esterne in fase implementativa.
- Evitare layout che rompono con stringhe +30% (tedesco).
- Data/ora secondo locale; clock Horizon con formato utente.

---

## 10. Telemetria e fiducia (UX)

- Se esiste telemetria: opt-in chiaro, linguaggio non eufemistico.
- Cruscotto “Privacy & NovaAI” in Impostazioni con toggle comprensibili.
- Mai nascondere modalità cloud dietro “Migliora esperienza” ambiguo.

---

## 11. Qualità della velocità

| Interazione | Target percettivo |
|-------------|-------------------|
| Aprire launcher | ≤ 150ms a primo frame utile |
| Digitare in search | feedback frame-by-frame |
| Aprire Control Center | ≤ 180ms |
| Invocare AI locale piccola | feedback < 300ms anche se risposta completa dopo |
| Commutare tema | ≤ 320ms crossfade |

Se i target non sono raggiungibili, ridurre effetti (blur) prima di “abbellire”.

---

## 12. Esperienze da non progettare (non-goal UX v1)

- Marketplace di widget desktop.
- Temi community non firmati come default.
- Gamification del desktop.
- Assistente parlante proattivo non richiesto.
- Cloni di flussi Windows Settings a deep tree senza IA informativa *opzionale*.

---

## 13. Gate di accettazione UX (review)

- [ ] Mappa mentale (sez. 3) rispettata?
- [ ] Un solo primary CTA per vista?
- [ ] AI off/fail non blocca il compito?
- [ ] Blind test brand superato?
- [ ] Reduced motion definito?
- [ ] Copy in italiano chiaro, senza hype?
- [ ] Nessun pattern Windows/macOS/KDE stock riconoscibile come firma?

---

## 14. Motivazione

UX di un OS AI-First fallisce in due modi: (a) sembra un tema carino su un DE altrui; (b) diventa un chatbot che governa tutto. Nova Shell evita entrambi: geografia propria, AI a strati, silenzio e velocità come lusso quotidiano.
