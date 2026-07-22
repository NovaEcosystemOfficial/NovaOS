# 09 — Design Principles

**NovaOS Design System — Principi**  
**Sprint:** 2 — Identità visiva  
**Stato:** Carta dei principi (vincolante)

---

## 1. Scopo

Elencare i principi che governano ogni decisione di design su NovaOS e Nova Shell. In caso di conflitto tra gusto individuale e questi principi, **vincono i principi**.

---

## 2. I dieci principi Nova

### P1 — Riconoscibilità strutturale

Nova si riconosce dalla geografia e dai materiali (Horizon Bar, Glass, stellar/signal), non solo dal wallpaper.  
**Test:** blind test senza logo.

### P2 — Un compito per superficie

Ogni vista ha un lavoro. Notification ≠ Control ≠ Launcher ≠ AI Stage.  
**Motivazione:** riduce carico cognitivo e copia di Action Center generici.

### P3 — Brand first, contenuto subito dopo

Nei momenti rituali (boot, onboarding) il brand è hero. Nel lavoro quotidiano, il contenuto utente è hero e il chrome tace.

### P4 — Luce come informazione

Blur, alone, cyan e amber comunicano stato. Se la luce non informa, è rumore — e si rimuove.

### P5 — Velocità percepita

Feedback ≤ 100ms dove possibile; motion UI ≤ 240ms. Preferire cut onesti a animazioni lunghe.

### P6 — Minimalismo strutturale

Togliere widget, opzioni e accenti finché resta chiarezza. Minimalismo ≠ vuoto sterile: è gerarchia.

### P7 — AI controllabile

L’intelligenza propone; l’utente dispone sulle azioni sensibili. Sempre percorso locale/off. Mai dark pattern cloud.

### P8 — Affidabilità visibile

Stati, errori e progress dicono la verità. Niente spinner eterni senza messaggio; niente successo finto.

### P9 — Coerenza ecosistema

NovaDocs, NovaStudio e le altre app sembrano cittadini dello stesso pianeta. Accenti di dominio sì; dialetti incompatibili no.

### P10 — Rispetto dell’attenzione

Silenzio sonoro di default, notifiche sobrie, reduced motion, privacy indicators chiari. L’attenzione è una risorsa dell’utente, non del marketing.

---

## 3. Principi anti-imitazione

| Non diventare | Perché |
|---------------|--------|
| Windows | Paradigmi Start/taskbar full-bleed/Action Center mescolati |
| macOS | Dock magnify, traffic lights, global menu come identità |
| KDE stock | Festival di widget, Breeze come volto, “tutto configurabile” in faccia all’utente |

Configurabilità avanzata può esistere in Settings → Avanzate; **non** è la prima impressione.

---

## 4. Principi di materiale

1. Un blur standard (`blur.glass`), non cinque.  
2. Un’ombra per elevazione.  
3. Raggi dalla scala `radius.*`.  
4. Trasparenza ridotta su testo piccolo e su tema light se serve leggibilità.

---

## 5. Principi tipografici e iconici

1. Nova Sans come voce; niente Inter-as-brand.  
2. Sentence case.  
3. Icone outline coerenti; AI duotone solo dove serve.  
4. Numeri tabulari nei pannelli sistema.

---

## 6. Principi etici di interfaccia

1. Consenso AI/cloud esplicito.  
2. Nessuna telemetria oscura in onboarding.  
3. Distruttivo sempre confermato.  
4. Linguaggio onesto, italiano chiaro.

---

## 7. Come usare questo documento in review

Ogni PR di UI / mockup futuro deve dichiarare:

- principi rispettati;
- eventuali eccezioni motivate;
- esito blind test (se superficie di shell).

Se un’eccezione contradice P1, P7 o P10, serve approvazione Creative Director + System Designer.
