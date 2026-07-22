# ADR-001 — Base Linux

| Campo | Valore |
|-------|--------|
| **ID** | ADR-001 |
| **Titolo** | Selezione della distribuzione Linux di base |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Decisori** | System Architect / Technical Lead (proposta al team) |

---

## 1. Problema

NovaOS è un sistema operativo AI-First basato su Linux che, nel tempo, sostituirà componenti standard con componenti Nova. Prima di scrivere codice, produrre ISO o impegnare toolchain, è necessario scegliere la **base Linux** su cui costruire.

La scelta influenza:

- ciclo di rilascio e supporto;
- gestore pacchetti e modello di aggiornamento;
- strumenti di build delle immagini;
- disponibilità di pacchetti freschi (critico per stack AI);
- facilità di personalizzazione del desktop;
- costo di manutenzione a lungo termine come prodotto.

**Vincolo di Sprint 0:** la scelta non era stata fatta. Questo ADR la affronta in modo esplicito.

---

## 2. Alternative valutate

### 2.1 Fedora (in particolare Fedora KDE / Workstation)

Distribuzione sponsorizzata da Red Hat, rilasci a cadenza ~6 mesi, pacchetti moderni, ecosistema DNF/RPM, percorso nativo verso sistemi immutabili (`rpm-ostree`, Fedora Atomic Desktops, `bootc`).

### 2.2 Ubuntu

Distribuzione Canonical, LTS pluriennali molto popolari, ecosistema APT/DEB, ampia documentazione, forte presenza desktop consumer e enterprise.

### 2.3 Debian

Base storica di stabilità, rilasci conservative, ecosistema APT/DEB, eccellente per server e sistemi “set-and-forget”, meno orientata all’innovazione desktop rapida.

### 2.4 Arch Linux

Rolling release, KISS, pacchetti all’avanguardia (e AUR), controllo totale, modello di manutenzione adatto a utenti esperti più che a un prodotto OS supportato da software house.

---

## 3. Analisi vantaggi / svantaggi

### Fedora KDE / Workstation

| Vantaggi | Svantaggi |
|----------|-----------|
| Pacchetti recenti: favorevole a toolchain AI, driver, stack grafici | Ciclo di supporto per release più breve rispetto a Debian/Ubuntu LTS |
| Spin KDE ufficiale: allineamento naturale con Plasma | Breaking change più frequenti tra major |
| Percorso chiaro verso immutabilità (`rpm-ostree`, Atomic, bootc) | Meno “familiare” al mass market rispetto a Ubuntu |
| DNF moderno, quality packaging RPM | Alcuni software commerciali arrivano prima/solo su Ubuntu |
| Buona integrazione con strumenti di image build (KIWI, livemedia-creator) | Richiede disciplina di QA a ogni upgrade di versione |
| Governance upstream trasparente, adatta a un fork/derivata di prodotto | Ecosystem Snap non è il default (di solito un vantaggio per Nova) |

### Ubuntu

| Vantaggi | Svantaggi |
|----------|-----------|
| LTS con supporto lungo: ideale per promesse di stabilità prodotto | Spinta verso Snap può confliggere con controllo della supply chain Nova |
| Enorme base utenti e documentazione | Personalizzazione profonda del desktop a volte in tensione con scelte Canonical |
| APT maturo, ecosystem software vasto | Percorso immutabile/atomico meno centrale rispetto a Fedora |
| Cubic e tooling di remix ampiamente usati | GNOME “Canonical-flavored” se si resta sul default |
| Facile hiring/onboarding di contributor abituati a Debian-like | Pacchetti LTS possono essere troppo indietro per AI locale all’avanguardia |

### Debian

| Vantaggi | Svantaggi |
|----------|-----------|
| Stabilità e prevedibilità eccellenti | Pacchetti spesso troppo datati per un OS AI-First |
| Politiche software chiare, affidabilità comprovata | Desktop “prodotto” richiede più lavoro di integrazione |
| Base di molte derivate di successo | Ciclo di rilascio lento vs ambizione Nova di evoluzione continua |
| APT consolidato | Meno spinta upstream su atomic desktop / OS immutabili |
| Ideale come rootfs server-like | Time-to-capability AI più alto (backport, repo terzi, rischio) |

### Arch Linux

| Vantaggi | Svantaggi |
|----------|-----------|
| Sempre aggiornato; ideale per sperimentazione | Rolling release difficile da supportare come prodotto consumer |
| Documentazione Wiki di altissimo livello | Nessun modello LTS nativo |
| Pacman semplice e potente; AUR ricco | Superficie di rottura elevata; costo supporto clienti alto |
| Massima libertà di composizione del sistema | Non adatto come promessa di stabilità per ecosistema Nova |
| Ottimo laboratorio interno | ISO “prodotto” richiede comunque un wrapper di governance che Arch non fornisce |

---

## 4. Decisione proposta

**Raccomandazione: adottare Fedora come base Linux di NovaOS, partendo dallo spin/variante KDE come riferimento di esperienza.**

In concreto:

1. **Base tecnica:** Fedora (versione stabile corrente al momento dell’avvio Fase “Platform Base”).
2. **Profilo desktop di riferimento:** Fedora KDE Plasma Desktop.
3. **Modello di prodotto:** derivata NovaOS governata dal team (branding, selezione pacchetti, servizi Nova), non un semplice remix estetico.
4. **Traiettoria:** progettare da subito l’architettura in modo compatibile con un’evoluzione verso immagini immutabili Fedora-like (`rpm-ostree` / Atomic), senza obbligare l’immutabilità dal giorno uno.

---

## 5. Motivazione tecnica

La decisione non privilegia la popolarità bruta, ma l’**allineamento con la visione NovaOS**:

1. **AI-First richiede pacchetti freschi**  
   Runtime, librerie GPU/NPU, stack container e tool locali evolvono rapidamente. Fedora riduce il gap rispetto a upstream meglio di Debian stable e spesso meglio di Ubuntu LTS “congelata”.

2. **Sostituzione progressiva dei componenti**  
   Fedora è già organizzata per varianti (Workstation, KDE, Atomic). Questo combacia con la strategia “strangler” definita in architettura: partire mutabile, migrare pezzi verso un modello più controllato.

3. **Coerenza con le altre ADR**  
   - Desktop → Plasma (ADR-002) ha spin ufficiale su Fedora.  
   - Package manager → DNF (ADR-004).  
   - Update → percorso verso rpm-ostree (ADR-006).  
   - Build → KIWI NG / livemedia-creator (ADR-003) sono realistici su ecosistema RPM/Fedora.

4. **Controllo della supply chain**  
   Evitare dipendenza strutturale da canali tipo Snap come default di distribuzione delle app Nova. NovaOS vuole app **native** dell’ecosistema, non “store di terzi” come centro di gravità.

5. **Arch scartato come base prodotto**  
   Eccellente come laboratorio, inadatto come fondazione di un OS supportato con installer, update policy e promesse verso utenti dell’ecosistema Nova.

6. **Ubuntu scartato come prima scelta (non come nemico)**  
   Resta un’alternativa forte, soprattutto per LTS e familiarità. È stata posposta perché il vincolo Snap/immutability path e il fit con Plasma+atomic sono meno lineari rispetto a Fedora per il piano NovaOS. Potrà essere rivalutata se emergono requisiti commerciali che la impongono.

7. **Debian scartato come base desktop AI-First**  
   Ottima stabilità, insufficiente velocità di innovazione per l’orizzonte Nova senza un overhead elevato di manutenzione pacchetti.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando valutarla |
|------------|-------------|------------------|
| **Fedora Atomic / bootc** | Passare a immagini immutabili come default di prodotto | Dopo MVP esperienza (Fase 3+) e ADR-006 consolidata |
| **Multi-edition** | Edizione “Stable” (ciclo più conservativo) e “Dev” (tracking Fedora rawhide/n+1) | Quando esiste base utenti interna |
| **Rebase controllato** | Policy di upgrade NovaOS allineata a N versioni Fedora supportate | Con il primo programma di supporto ufficiale |
| **Rivalutazione Ubuntu LTS** | Solo se partner/hardware/certificazioni lo richiedono | Gate commerciale esplicito |
| **Kernel/HW enablement layer** | Overlay Nova per hardware target senza abbandonare Fedora | Con primi device ufficiali |
| **Laboratorio Arch isolato** | Non come base prodotto, ma come sandbox R&D | Opzionale, repo separato |

---

## 7. Conseguenze

### Positive

- Stack decisionale coerente (desktop, package, update, build).
- Migliore velocità di adozione stack AI locale.
- Percorso credibile verso OS “prodotto” con update atomici.

### Negative / rischi da mitigare

- Serve piano di QA per upgrade Fedora → Fedora.
- Comunicazione utente su cicli di rilascio più corti delle LTS classiche.
- Alcuni vendor software potrebbero richiedere packaging dedicato.

### Mitigazioni

- Definire “NovaOS Supported Releases” (es. N e N-1).
- CI di smoke test su immagini ad ogni rebase.
- Repository Nova per pacchetti critici dell’ecosistema.

---

## 8. Riferimenti

- [`../architecture.md`](../architecture.md)
- [`../roadmap.md`](../roadmap.md)
- ADR-002, ADR-003, ADR-004, ADR-006

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
