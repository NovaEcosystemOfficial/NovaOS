# ADR-002 — Desktop Environment

| Campo | Valore |
|-------|--------|
| **ID** | ADR-002 |
| **Titolo** | Selezione del Desktop Environment |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | ADR-001 (Base Linux) |

---

## 1. Problema

NovaOS deve offrire un’esperienza desktop riconoscibile come prodotto Nova, non come distro generica rinominata. Il Desktop Environment (DE) è lo strato di esperienza più visibile e determina:

- capacità di branding e theming profondi;
- toolkit UI (Qt vs GTK) e stack tecnologico del team;
- integrazione con display manager, gestori sessione, impostazioni;
- facilità di sostituzione progressiva con componenti Nova;
- percezione di modernità per un OS AI-First.

Va scelto un DE di partenza **upstream**, accettando che nel lungo periodo parti possano essere sostituite da componenti Nova (`desktop/`).

---

## 2. Alternative valutate

### 2.1 KDE Plasma

Desktop moderno basato su Qt, altamente configurabile, con ecosistema KWin, Plasma Shell, Frameworks e SDDM tipicamente associato.

### 2.2 GNOME

Desktop opinionated basato su GTK/Mutter, focus su semplicità e consistency, standard di fatto su molte workstation (Fedora Workstation default, Ubuntu default).

### 2.3 XFCE

Desktop leggero basato su GTK, tradizionale, orientato a performance e semplicità, meno “vetrina” di un prodotto OS premium contemporaneo.

---

## 3. Analisi vantaggi / svantaggi

### KDE Plasma

| Vantaggi | Svantaggi |
|----------|-----------|
| Personalizzazione profonda: ideale per identità Nova forte | Superficie ampia: più da governare/QA |
| Look moderno out-of-the-box, adatto a un brand di prodotto | Rischio di “troppo configurabile” se non si definisce un defaults Nova |
| Qt è solido per app complesse e tool nativi futuri | Stack Qt ≠ GTK: alcune app GNOME-style richiedono temi/bridge |
| Integrazione naturale con SDDM (ADR-005) | Percezione storica (superata ma residuale) di “pesantezza” |
| Widget, pannelli, KWin effects: spazio per AI entry-point di sistema | Upgrade Plasma major possono richiedere adattamenti al branding |
| Fedora ha spin KDE ufficiale (coerenza con ADR-001) | Curva di learning per team abituati solo a GNOME |

### GNOME

| Vantaggi | Svantaggi |
|----------|-----------|
| UX coerente e “finita”, ottima per utenti non tecnici | Estensione/theming profondi spesso in conflitto con upstream |
| Documentazione e pattern consolidati | Branding distintivo Nova più difficile senza combattere il DE |
| Ottima accessibilità e gestualità moderne | Modello opinionated rallenta la sostituzione progressiva “a pezzi” |
| Default su Fedora Workstation: path comodo se si scegliesse GNOME-first | GNOME Shell extensions: fragili tra major |
| Buon supporto corporate/upstream Red Hat | Meno flessibile per shell AI-first altamente custom |

### XFCE

| Vantaggi | Svantaggi |
|----------|-----------|
| Leggero, prevedibile, basso consumo | Estetica e paradigma meno adatti a un OS AI-First “di punta” |
| Semplice da comprendere e modificare a livello base | Meno innovazione UX recente rispetto a Plasma/GNOME |
| Buono per hardware modesto | Ecosistema estensioni/modernità limitato |
| GTK familiare | Rischio di percepire NovaOS come “distro leggera”, non come piattaforma ecosistema |

---

## 4. Decisione proposta

**Raccomandazione: adottare KDE Plasma come Desktop Environment ufficiale di NovaOS.**

In concreto:

1. Plasma come sessione di default delle immagini NovaOS.
2. Defaults Nova (layout, tema, font, scorciatoie, entry point AI) definiti in `branding/` + overlay di configurazione, non lasciati al “Plasma stock”.
3. GNOME e XFCE **non** sono edizioni ufficiali nella fase iniziale (riduzione superficie di supporto).
4. Nel lungo periodo, componenti Plasma possono essere wrappati/sostituiti secondo la strategia strangler (`desktop/`), mantenendo compatibilità sessione dove serve.

---

## 5. Motivazione tecnica

1. **Brand first (UI guidelines)**  
   Le linee guida NovaOS richiedono riconoscibilità di prodotto. Plasma consente un controllo visivo e di layout superiore senza doversi appoggiare a un ecosistema di extension fragili.

2. **AI come capacità di sistema**  
   Un OS AI-First avrà pannelli, scorciatoie globali, overlay e indicatori di stato. Plasma offre primitive (plasmoid, KWin, global shortcuts, system tray) più adatte a sperimentare superfici AI di sistema rispetto al modello GNOME più chiuso.

3. **Sostituzione progressiva**  
   La modularità Plasma si allinea meglio all’idea di sostituire pezzi (launcher, settings pages, lock screen policy) con componenti Nova nel tempo.

4. **Coerenza con ADR-001 e ADR-005**  
   Fedora KDE + SDDM è un binomio consolidato, riduce attrito di integrazione iniziale.

5. **XFCE scartato come default di prodotto**  
   Resta valutabile solo per un’eventuale edizione “lite” futura su hardware vincolato, non come volto di NovaOS.

6. **GNOME scartato come default (non come incompatibilità)**  
   Le app GTK continueranno a funzionare. Si evita però di basare l’identità del sistema su un DE che resiste alla differenziazione profonda.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **Nova Shell / pannelli proprietari** | Sostituire parti della shell Plasma con UI Nova | Fase 3+ |
| **Sessione Nova ufficiale** | `nova-session` che compone componenti misti Plasma/Nova | Dopo Platform API |
| **Edizione Lite (XFCE o Plasma Mobile-like)** | Solo se emerge requisito HW | Post-MVP |
| **Supporto GNOME “compat”** | Non ufficiale, community | Se richiesta esplicita |
| **Design tokens nativi Qt** | Libreria temi Nova per app native | Con Ecosystem Native |

---

## 7. Conseguenze

### Positive

- Identità desktop differenziabile.
- Allineamento tecnico con Fedora KDE e SDDM.
- Spazio naturale per entry point AI di sistema.

### Negative / rischi

- Bisogna disciplinare i defaults (evitare “museo di opzioni”).
- Competenze Qt/Plasma necessarie nel team.
- QA su personalizzazioni a ogni major Plasma.

### Mitigazioni

- “Nova Plasma Profile” versionato e testato.
- Freeze delle opzioni esposte all’utente finale nelle prime release.
- Documentare cosa è supportato vs cosa è nascosto.

---

## 8. Riferimenti

- [`../ui-guidelines.md`](../ui-guidelines.md)
- ADR-001, ADR-005

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
