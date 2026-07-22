# Linee guida UI — NovaOS

**Documento di design di sistema — Sprint 0 (Foundation)**  
**Stato:** linee guida fondative (pre-implementazione UI)  
**Lingua:** italiano

---

## 1. Scopo

Questo documento definisce i **principi e gli standard di interfaccia** per NovaOS: desktop, shell, installer, superfici di sistema e applicazioni native dell’ecosistema Nova.

Non è ancora un design system completo con token di produzione. È il **contratto di qualità UX** che governerà le scelte future in `branding/`, `desktop/`, `shell/`, `installer/` e `apps/`.

---

## 2. Obiettivo dell’esperienza

NovaOS deve risultare:

- **riconoscibile** come prodotto Nova al primo sguardo;
- **coerente** tra installer, desktop, shell e app native;
- **calmo e chiaro**, anche quando l’AI è presente;
- **potente senza confusione** — progressiva disclosure, non overload;
- **AI-First ma human-controlled** — l’AI propone, l’utente decide sulle azioni sensibili.

---

## 3. Principi di design

### 3.1 Un sistema, una voce

Desktop, shell e app non sono “mondi diversi”. Condividono gerarchia tipografica, ritmo, tono e pattern di interazione.

### 3.2 Brand first

Il nome e l’identità NovaOS devono essere un segnale forte nelle superfici primarie (lock screen, installer, impostazioni, about). L’interfaccia non deve poter essere scambiata per una distro generica dopo aver rimosso il logo dalla sola barra.

### 3.3 Una composizione, un compito

Ogni vista primaria ha **un lavoro**. Evitare dashboard affollate nella prima esperienza. Una sezione → uno scopo → un messaggio principale.

### 3.4 AI visibile ma non invadente

L’AI ha un posto chiaro nell’IA di sistema (entry point, scorciatoie, suggerimenti contestuali), senza sticker fluttuanti, badge aggressivi o overlay rumorosi sul contenuto.

### 3.5 Chiarezza sopra ornamentalismo

Preferire gerarchia, spaziatura e tipografia espressiva a decorazioni inutili, glow eccessivi e stack di ombre.

### 3.6 Accessibilità come requisito

Contrasto, focus visibile, navigazione da tastiera, dimensioni target, alternative testuali: non sono “fase 2”.

### 3.7 Controllabilità

Ogni azione AI con effetti collaterali (file, sistema, cloud, installazioni) richiede conferma proporzionata al rischio.

---

## 4. Superfici del sistema

| Superficie | Ruolo UX | Priorità di coerenza |
|------------|----------|----------------------|
| **Installer** | Fiducia, chiarezza, onboarding | Alta — prima impressione |
| **Desktop** | Vita quotidiana, multitasking | Alta |
| **Shell** | Potenza e velocità per power user | Alta (identità anche in TUI/CLI) |
| **Settings** | Controllo e trasparenza | Alta |
| **System AI** | Assistenza contestuale | Alta |
| **App native** | Valore di dominio | Alta — stesse regole di piattaforma |

---

## 5. Fondamenta visive

### 5.1 Identità

- NovaOS è il volto del sistema; l’ecosistema Nova ne eredita linguaggio e qualità.
- Gli asset ufficiali vivono in `branding/` (loghi, mark, palette, motion guidelines).
- Non usare placeholder generici in release: meglio wireframe chiari che brand improvvisato.

### 5.2 Colore

Linee guida (da concretizzare in token in `branding/`):

- definire una direzione cromatica **chiara e distintiva**;
- evitare di default look generici da template (es. viola-su-bianco “AI cliché”, cream+terracotta da brochure, dark mode forzato ovunque);
- supportare tema chiaro/scuro come preferenza utente, non come unica identità;
- riservare il colore di accento ad azioni primarie e stati, non a ogni bordo.

### 5.3 Tipografia

- usare font espressivi e professionali, coerenti su tutto il sistema;
- evitare stack di default generici come unica identità tipografica;
- gerarchia tipica: display (raro, momenti di brand) → title → body → caption/mono (shell, codice, log).

### 5.4 Spaziatura e layout

- ritmo consistente (scala di spacing);
- densità adattiva: installer più arioso; tool tecnici più densi ma leggibili;
- evitare card ovunque: le card solo quando aiutano un’interazione o un raggruppamento necessario.

### 5.5 Iconografia e imagery

- set di icone coerente (tratto, corner, optical size);
- imagery di prodotto reale o atmosfera autentica Nova, non stock astratto come idea principale;
- niente collage caotici nel primo viewport di onboarding.

### 5.6 Motion

- 2–3 motion intenzionali per flussi chiave (transizioni di stato, feedback AI, onboarding);
- motion al servizio della gerarchia, non rumore continuo;
- rispetto di `prefers-reduced-motion`.

---

## 6. Pattern di interazione

### 6.1 Navigazione

- destinazioni principali poche e memorabili;
- ricerca di sistema unificata (target architetturale);
- deep link tra app native via intent di piattaforma.

### 6.2 Form e impostazioni

- etichette chiare, errori actionable, default sicuri;
- spiegare le conseguenze delle opzioni AI/cloud in linguaggio umano;
- raggruppare per compito, non per struttura tecnica interna.

### 6.3 Notifiche e sistema

- notifiche sobrie, raggruppabili, silenziabili;
- distinguere: informazione, azione richiesta, allarme sicurezza.

### 6.4 Dialoghi e conferme

- distruttivo → conferma esplicita;
- AI che modifica il sistema → preview + conferma;
- evitare alert spam.

### 6.5 Vuoti e stati

Ogni superficie definisce: loading, empty, error, offline, permission denied, AI unavailable.

---

## 7. Linee guida per l’AI nell’interfaccia

### 7.1 Entry point

Deve esistere un modo coerente per invocare l’AI di sistema (scorciatoia, gesture, comando shell, icona stabile). L’entry point è parte del prodotto, non un widget temporaneo.

### 7.2 Contesto

L’AI può usare contesto di sistema **solo** nei limiti dei permessi. L’UI deve rendere evidente “su cosa sto lavorando”.

### 7.3 Suggerimenti

I suggerimenti sono secondari rispetto al compito dell’utente. Non competono col contenuto principale.

### 7.4 Trasparenza

Mostrare quando una risposta è locale o cloud (se la distinzione esiste), e come disattivare/limitare le funzioni.

### 7.5 Fallimenti

Se NovaAI non è disponibile, il sistema resta usabile. Nessuna dipendenza totale dall’AI per compiti base.

---

## 8. Shell e interfacce testuali

La shell è parte dell’esperienza NovaOS, non un afterthought.

- prompt e messaggi con tono coerente al brand (professionale, diretto);
- aiuto integrato chiaro (`nova help` o equivalente futuro);
- output leggibile; colori accessibili; niente ASCII art invasiva di default;
- assistenza AI in shell: comandi proposti, non eseguiti in silenzio su azioni pericolose.

---

## 9. Installer e first-run

L’installer è la prima UI critica.

### Deve

- comunicare immediatamente NovaOS (brand + una promessa chiara);
- guidare un compito alla volta;
- spiegare opzioni AI/cloud senza dark pattern;
- offrire un percorso “semplice” e uno “avanzato”.

### Non deve

- affollare il primo schermo con promo, stats e moduli multipli;
- sovrapporre badge e sticker al visual principale;
- sembrare un installer generico con logo sostituito.

---

## 10. App native dell’ecosistema

Le app (NovaDocs, NovaStudio, NovaPromo, NovaBeauty, NovaSky, e le superfici NovaCloud/NovaAI) devono:

1. rispettare questi principi;
2. usare componenti/pattern di piattaforma quando disponibili;
3. ereditare identity tokens da `branding/`;
4. esporre intent utili al resto del sistema;
5. evitare UI “da prodotto isolato” che rompe la coerenza OS.

Eccezioni di dominio (es. tool creativi densi) sono ammesse **dentro** il linguaggio Nova, non fuori.

---

## 11. Tono di voce nell’UI

| Contesto | Tono |
|----------|------|
| Errori | Onesti, specifici, con next step |
| AI | Collaborativo, non paternalistico |
| Sicurezza | Chiaro e fermo, senza alarmismo inutile |
| Onboarding | Accogliente e concreto |
| Shell | Conciso e preciso |

Evitare: hype vuoto, meme di sistema, antropomorfismo eccessivo dell’AI.

---

## 12. Checklist qualità UI (gate di review)

Prima di considerare “accettabile” una superficie NovaOS:

- [ ] Il brand è riconoscibile senza dipendere da un solo logo in un angolo?
- [ ] La vista ha un compito primario chiaro?
- [ ] L’AI è utile e controllabile, non rumorosa?
- [ ] Stati vuoti/errore/loading sono progettati?
- [ ] Contrasto e focus keyboard sono adeguati?
- [ ] Coerente con desktop/shell/installer/app correlate?
- [ ] Nessun dark pattern su cloud/AI/telemetry?
- [ ] Compatibile con `prefers-reduced-motion` se usa motion?

---

## 13. Relazione con gli altri artefatti

| Artefatto | Relazione |
|-----------|-----------|
| `branding/` | Token, logo, palette, motion — implementazione visiva |
| `docs/vision.md` | Perché l’esperienza deve essere unificata |
| `docs/architecture.md` | Dove vivono le superfici e le API che le alimentano |
| `docs/roadmap.md` | Quando l’Experience Layer diventa deliverable |

---

## 14. Evoluzione di questo documento

Questo file resta il **contratto UX di alto livello** del repository.  
Dal Sprint 2, le specifiche dettagliate di identità e Nova Shell vivono in:

**[`design-system/`](design-system/README.md)**

In caso di conflitto tra questo documento e il Design System, **prevale il Design System** (più specifico), salvo decisione esplicita di allineamento.

In Fase 3 (Experience Layer) il Design System si evolverà ulteriormente con:

- token design esportati in `branding/`;
- libreria componenti di sistema;
- pattern detail (density, breakpoints);
- specifiche accessibilità misurabili.

Fino ad allora, ogni mockup o prototipo deve dichiarare conformità (o eccezioni motivate) ai principi del Design System e a questo documento.
