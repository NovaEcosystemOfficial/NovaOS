# ADR-006 — Update System

| Campo | Valore |
|-------|--------|
| **ID** | ADR-006 |
| **Titolo** | Selezione del sistema di aggiornamento |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | ADR-001 (Base Linux), ADR-004 (Package Manager) |

---

## 1. Problema

Un sistema operativo prodotto non può basarsi su aggiornamenti “fai da te”. NovaOS deve definire:

- come gli utenti ricevono patch di sicurezza e feature;
- se il modello è mutabile classico o immutabile/atomico;
- come si aggiornano OS vs app native dell’ecosistema;
- come si gestiscono rollback e affidabilità.

Le alternative principali nel perimetro dello stack Fedora/RPM sono **DNF** (transazioni pacchetto) e **rpm-ostree** (immagini atomiche / OSTree).

---

## 2. Alternative valutate

### 2.1 DNF (aggiornamento mutabile basato su pacchetti)

Modello tradizionale: il sistema è un insieme di RPM aggiornati tramite transazioni DNF (o UI che lo wrappano).

### 2.2 rpm-ostree (aggiornamento atomico / immutabile)

Modello image-based: il host è aggiornato per deploy atomici OSTree, con rollback nativo; spesso combinato con layering di pacchetti e app containerizzate/sandboxed.

---

## 3. Analisi vantaggi / svantaggi

### DNF

| Vantaggi | Svantaggi |
|----------|-----------|
| Semplice da adottare subito su Fedora mutabile | Drift di configurazione tra macchine nel tempo |
| Flessibile per sviluppatori e early adopter interni | Aggiornamenti non atomici: risk di stati parziali |
| Coerente con packaging RPM dei componenti Nova in fase early | Rollback meno “pulito” rispetto a OSTree |
| Tooling e conoscenza ampiamente disponibili | Più difficile promettere “tutti i NovaOS identici” sul campo |
| Ideale per iterare rapidamente in Platform Base | Superficie di rottura più alta in supporto utenti finali |

### rpm-ostree

| Vantaggi | Svantaggi |
|----------|-----------|
| Aggiornamenti atomici e reboot-based previsibili | Complessità operativa e cognitiva iniziale |
| Rollback robusto: requirement da prodotto serio | Workflow sviluppatore diverso (image, rebase, overlay) |
| Eccellente per flotte omogenee e supporto | Alcuni workflow classici “install RPM ovunque” vanno ripensati |
| Allineato a Fedora Atomic / bootc direction | Non obbligatorio (né ottimale) al giorno zero del MVP |
| Separazione più chiara OS immutabile vs app | Richiede maturità di build pipeline (ADR-003) |

---

## 4. Decisione proposta

**Raccomandazione a due tempi:**

1. **Breve periodo (Platform Base → primo MVP esperienza):** aggiornamenti basati su **DNF** su immagine Fedora mutabile personalizzata NovaOS.  
2. **Traiettoria ufficiale di prodotto:** evolvere verso **rpm-ostree** (edizione Atomic NovaOS) come modello preferito per release utente finale.

In concreto:

- Non dichiarare NovaOS “immutable-only” prima di avere pipeline immagini e QA.
- Progettare repo, packaging e componenti **senza chiudere la porta** a ostree (niente assunzioni hard “root fs liberamente mutable forever”).
- UI di update Nova dovrà astrarre il backend (DNF oggi, rpm-ostree domani) dietro un contratto di piattaforma.

---

## 5. Motivazione tecnica

1. **Realismo di delivery**  
   Forzare rpm-ostree dal primo giorno aumenta rischio e ritarda desktop/installer/AI. DNF consente di costruire fondamenta e componenti Nova più in fretta.

2. **Visione di prodotto**  
   Un OS AI-First con ecosistema di app native beneficia enormemente di host riproducibili e rollback: rpm-ostree è la destinazione giusta, non un optional eterno.

3. **Coerenza con ADR-001/003/004**  
   Fedora + RPM + (KIWI/livemedia) è uno dei percorsi più credibili verso atomic desktop. La scelta “DNF now, ostree next” è una strategia, non un’indecisione.

4. **Separazione OS vs ecosistema**  
   Anche con DNF iniziale, le app Nova possono già tendere a cicli di release indipendenti (repo app). Con rpm-ostree, l’OS diventa immagine; le app restano aggiornabili con meccanismi dedicati — modello più sano.

5. **Perché non “solo rpm-ostree subito”**  
   Mancano ancora (volontariamente) codice, ISO e maturità CI. L’atomicità senza pipeline è teatro architetturale.

6. **Perché non “solo DNF per sempre”**  
   Contradirebbe l’ambizione di qualità da software house su flotte reali e supporto di lungo periodo.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **NovaOS Atomic edition** | Default utente finale su rpm-ostree | Post-MVP Experience, con ADR update |
| **Canali ostree** | `stable`, `beta` | Con programma di release |
| **bootc** | Image build container-native per host | Valutazione quando maturo sul target |
| **Update agent Nova** | Demone/UI unica per OS+policy | System Core / Experience |
| **Policy dual-track** | Dev mutabile (DNF), Prod atomica | Quando esistono entrambe le edizioni |
| **Rollback UX** | Flusso assistito anche con AI “cosa è cambiato” | AI-First OS |

---

## 7. Conseguenze

### Positive

- Roadmap update chiara senza bloccare Sprint implementativi.
- Destinazione tecnica allineata a Fedora Atomic.
- Spazio per imparare packaging prima di congelare l’host.

### Negative / rischi

- Debito se il team “si trova bene con DNF” e non migra mai.
- Due modelli da documentare durante la transizione.
- App che scrivono in path sbagliati romperanno in atomic mode.

### Mitigazioni

- Milestone esplicita in roadmap: “M-atomic”.
- Linee guida filesystem hierarchy per componenti Nova (writable vs immutable).
- Spike rpm-ostree entro la Fase System Core, non rimandare a tempo indeterminato.

---

## 8. Riferimenti

- ADR-001, ADR-003, ADR-004
- [`../architecture.md`](../architecture.md) — System Layer / Update & Packaging
- [`../roadmap.md`](../roadmap.md)

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
