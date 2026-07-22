# Roadmap di NovaOS

**Documento di roadmap di prodotto e piattaforma**  
**Sprint corrente:** Sprint 5 — Development Infrastructure *(fase corrente)*.  
**Lingua:** italiano

---

## 1. Scopo del documento

Questo documento definisce la **traiettoria di evoluzione** di NovaOS: dalle fondamenta organizzative fino a un sistema operativo AI-First in cui l’ecosistema Nova è nativo.

Non è un piano di sprint giornaliero. È una **mappa per fasi**, pensata per una software house che costruisce un OS nel tempo.

---

## 2. Principi di avanzamento

1. **Nessuna fase salta le fondamenta della precedente.**
2. **Nessuna ISO prima della Platform Base.**
3. **Scelta di distro e stack via ADR (Sprint 1)** — implementazione solo dopo accettazione.
4. **Sostituzione progressiva** dei componenti standard solo quando esiste un’alternativa Nova matura.
5. **Documentazione aggiornata** a ogni cambio di fase o decisione architetturale rilevante.
6. **Ecosistema prima della frammentazione** — ogni nuova capability deve rafforzare NovaOS come cuore Nova.

---

## 3. Panoramica delle fasi

```text
Sprint 0 → … → Sprint 4 → Sprint 5 → Fase 1 (exec) → Fase 2 → …
Docs / ADR / Design / Platform / Boot → Dev workspace → ISO M0.1 → AI/Ryuk later
```

| Fase | Nome | Esito atteso |
|------|------|--------------|
| Sprint 0 | Foundation | Repository, docs, branding folder, processi base |
| Sprint 1 | Decisioni tecniche | ADR su base, desktop, build, packaging, DM, update, AI |
| Sprint 2 | Identità visiva | Design System completo; specifica **Nova Shell** |
| Sprint 3 | Architettura software | Platform docs: AI Core, Ryuk, Services, SDK, Security, Boot |
| Sprint 4 | Boot Foundation | Specifica pipeline ISO e **Milestone 0.1** |
| Sprint 5 | Dev Infrastructure | Workspace `build/configs/assets/iso/packages/vm/tools` |
| Fase 1 | Platform Base (exec) | Toolchain attiva, **realizzazione ISO M0.1** |
| Fase 2 | System Core | Servizi, AI Core, Ryuk (dopo M0.1 stabile) |
| Fase 3 | Experience Layer | Nova Shell avanzata, installer maturo |
| Fase 4 | Ecosystem Native | App Nova native |
| Fase 5 | AI-First OS | AI di sistema matura |

---

## 4. Sprint 0 — Foundation *(completato)*

### Obiettivo

Costruire le fondamenta di progetto come farebbe una software house prima dello sviluppo: struttura, visione, architettura di riferimento, roadmap, standard UI, licenza e igiene di repository.

### Deliverable

- [x] Struttura directory del monorepo/progetto
- [x] `README.md` completo
- [x] Documentazione in `docs/` (`vision`, `roadmap`, `architecture`, `ui-guidelines`)
- [x] `LICENSE` e `.gitignore`
- [x] Aree dedicate: `.github/`, `branding/`, `desktop/`, `shell/`, `installer/`, `apps/`, `ai/`, `system/`, `scripts/`

### Explicitamente escluso

- Codice del sistema operativo
- Scelta della distribuzione Linux
- Creazione di ISO o immagini di installazione
- Implementazione di desktop/shell/installer

### Criterio di uscita

Il team condivide una direzione unica: NovaOS è un OS AI-First, cuore dell’ecosistema Nova, e lo Sprint 0 è chiuso senza debito di ambiguità strategica.

---

## 4-bis. Sprint 1 — Decisioni tecniche *(completato in documentazione; ADR in accettazione)*

### Obiettivo

Definire le **decisioni tecniche fondamentali** tramite Architecture Decision Records, senza scrivere codice OS e senza produrre ISO.

### Deliverable

- [x] Cartella `docs/adr/`
- [x] ADR-001 Base Linux
- [x] ADR-002 Desktop Environment
- [x] ADR-003 Build System
- [x] ADR-004 Package Manager
- [x] ADR-005 Display Manager
- [x] ADR-006 Update System
- [x] ADR-007 AI Architecture
- [ ] Accettazione formale degli ADR da parte del team (stato → Accettata)

### Stack raccomandato (in proposta)

Vedi indice: [`adr/README.md`](adr/README.md).

### Explicitamente escluso

- Codice del sistema operativo
- Creazione di ISO
- Implementazione di desktop/shell/installer

### Criterio di uscita

Gli ADR sono reviewati e accettati (o emendati). La Fase 1 può partire su uno stack ufficiale senza ambiguità.

---

## 4-ter. Sprint 2 — Identità visiva *(completato in documentazione)*

### Obiettivo

Definire l’**identità visiva completa** di NovaOS e la specifica di **Nova Shell**, senza codice, senza immagini e senza mockup binari.

### Deliverable

- [x] Cartella `docs/design-system/`
- [x] Documenti 01–10 (Brand → UX)
- [x] Naming ufficiale desktop: **Nova Shell**
- [x] Direzione *Luminous Precision* (palette, type, layout, motion, boot, sound, principles)
- [ ] Produzione asset in `branding/` (fase successiva)
- [ ] Implementazione UI (Fase 3)

### Explicitamente escluso

- Codice di Nova Shell
- File immagine / logo esportati
- Mockup grafici obbligatori
- ISO

### Criterio di uscita

Il team condivide un linguaggio visivo unico, riconoscibile e anti-clone (non Windows/macOS/KDE stock), sufficiente a guidare branding e implementazione.

---

## 4-quater. Sprint 3 — Architettura software *(completato in documentazione)*

### Obiettivo

Progettare l’**architettura software** di Nova Platform per un orizzonte di mantenimento decennale, senza implementare codice.

### Deliverable

- [x] Cartella `docs/platform/`
- [x] Documenti 01–10 (Platform → Boot Sequence)
- [x] **Nova AI Core** definito come orchestratore AI
- [x] **Ryuk** definito come assistente nativo **system service** (non app), con Skills
- [ ] Accettazione formale dell’architettura da parte del team
- [ ] Implementazione (Fase 2+)

### Explicitamente escluso

- Codice
- ISO
- Implementazione Skills/runtime

### Criterio di uscita

Confini e API concettuali chiari tra NovaOS, Shell, AI Core, Ryuk, Services, Apps, SDK e Security.

---

## 4-quinquies. Sprint 4 — Boot Foundation *(completato in documentazione)*

### Obiettivo

Progettare la **prima build realmente avviabile** (Milestone 0.1): ISO stabile su PC di sviluppo, senza Ryuk/AI/Cloud/Store/Apps.

### Deliverable

- [x] Cartella `docs/boot-foundation/`
- [x] Documenti 01–10 (pipeline → milestone)
- [x] Freeze scope M0.1
- [ ] Implementazione toolchain/ISO (esecuzione Fase 1)
- [ ] PASS test Tier 1–2 su Reference PC

### In scope M0.1

Boot · Logo · Login Nova · Nova Shell iniziale · Terminale · Impostazioni · Spegnimento/Riavvio

### Fuori scope M0.1

Ryuk · Nova AI · Nova Cloud · Nova Store · Nova Apps

### Criterio di uscita Sprint 4 (docs)

Il team sa come costruire e validare M0.1; lo scope è congelato.

### Criterio di uscita Milestone 0.1 (prodotto)

Checklist in `boot-foundation/09-Testing-Strategy.md` e DoD in `10-Milestone-0.1.md`.

---

## 4-sexies. Sprint 5 — Development Infrastructure *(fase corrente)*

### Obiettivo

Creare il **workspace professionale** di build (directory, config template, script stub, VM, packaging layout) senza implementare ancora NovaOS/Shell/Ryuk/AI.

### Deliverable

- [x] `build/`, `configs/`, `assets/`, `iso/`, `packages/`, `scripts/`, `vm/`, `tools/`
- [x] README motivati per ogni area
- [x] Template Fedora/KIWI/bootstrap
- [x] Stub script pipeline
- [x] `DEV-WORKSPACE.md`
- [ ] Host Fedora preparato + ricetta KIWI reale (prossimo sprint esecutivo)
- [ ] Prima ISO M0.1

### Explicitamente escluso

- Nova Shell (codice)
- Ryuk / Nova AI
- ISO completa funzionante

### Criterio di uscita Sprint 5

Il team ha un albero di sviluppo chiaro e comandi ufficiali (anche stub) per costruire NovaOS negli sprint successivi.

---

## 5. Fase 1 — Platform Base

### Obiettivo

Operazionalizzare la **base tecnica** su cui costruire NovaOS, dando seguito agli ADR accettati.

### Attività principali

- Congelare lo stack accettato (Fedora/Plasma/DNF/… secondo ADR).
- Impostare toolchain di build (KIWI NG) e ambienti di sviluppo riproducibili (`boot-foundation/08`).
- Realizzare la **Milestone 0.1** secondo `docs/boot-foundation/` (ISO avviabile).
- Introdurre packaging RPM di branding (`novaos-branding`, tema SDDM, defaults shell).
- Attivare CI leggera (validazione ricette; build full quando il runner lo consente).
- Definire policy di versioning (`0.1.0`).
- **Non** introdurre Ryuk/AI in questa fase di esecuzione M0.1.

### Deliverable attesi

- ADR accettati come baseline ufficiale
- Pipeline CI minima
- Documento operativo di packaging e boot/update
- Ambiente di build documentato
- Prima bozza di image description (ancora senza release pubblica obbligatoria)

### Criterio di uscita

Esiste una piattaforma di partenza ufficiale, giustificata e riproducibile, **senza** aver ancora preteso un desktop Nova completo.

---

## 6. Fase 2 — System Core

### Obiettivo

Introdurre i **componenti di sistema** e i contratti di piattaforma che abiliteranno AI, cloud e app native.

### Attività principali

- Avviare `system/`: servizi core, configurazioni, identity hooks, update hooks.
- Avviare `ai/`: primitive NovaAI a livello sistema (API locali, policy, sandboxing).
- Definire integrazioni con NovaCloud (account, sync, telemetria opzionale e privacy-first).
- Stabilire contratti per intent, notifiche, ricerca di sistema, capability registry.
- Definire modelli di sicurezza e permessi per capacità AI.

### Deliverable attesi

- Bozza di Platform API
- Servizi minimi deployabili in ambiente di sviluppo
- Policy di sicurezza AI documentate
- Primi test di integrazione sistema ↔ AI

### Criterio di uscita

Un’applicazione “nova-native” di prova può consumare almeno una primitiva di sistema (es. AI o identity) in modo documentato.

---

## 7. Fase 3 — Experience Layer

### Obiettivo

Costruire lo strato di esperienza utente: **desktop**, **shell**, **installer**.

### Attività principali

- `desktop/`: shell grafica / ambiente, sessioni, impostazioni, coerenza con UI guidelines
- `shell/`: esperienza CLI/TUI allineata al brand e, nel tempo, AI-assisted
- `installer/`: installazione, partizionamento guidato, onboarding, prima configurazione AI/cloud
- Applicare `docs/ui-guidelines.md` come standard vincolante di prodotto
- Costruire asset in `branding/` necessari all’esperienza di sistema

### Deliverable attesi

- MVP di esperienza desktop Nova (anche se ancora parziale)
- Installer tecnico o wizard di onboarding in forma iniziale
- Shell con identità Nova misurabile (prompt, tool, docs integrate)

### Criterio di uscita

Un utente interno può installare/avviare un’immagine di sviluppo e riconoscere NovaOS come prodotto, non come distro anonima.

---

## 8. Fase 4 — Ecosystem Native

### Obiettivo

Portare i prodotti dell’ecosistema Nova a **componenti nativi** del sistema.

### Ordine di integrazione suggerito (adattabile)

1. **NovaAI** — perché abilita gli altri
2. **NovaCloud** — identità, sync, servizi
3. **NovaDocs** / **NovaStudio** — produttività quotidiana
4. **NovaPromo** — creatività e go-to-market
5. **NovaBeauty** / **NovaSky** — verticali di dominio

### Attività principali

- Packaging e distribuzione delle app come cittadini di prima classe in `apps/`
- Deep link con Platform API (AI, cloud, file providers, intent)
- Allineamento UX e branding
- Policy di aggiornamento coordinate OS ↔ app

### Criterio di uscita

Almeno due prodotti ecosistema sono installati/gestiti come nativi e usano servizi di sistema Nova in produzione interna.

---

## 9. Fase 5 — AI-First OS

### Obiettivo

Raggiungere la differenziazione: l’AI è una **capacità di sistema matura**.

### Esempi di capacità target

- Assistenza contestuale a livello desktop e shell
- Automazione di flussi di sistema con conferma umana e audit
- Ricerca unificata locale/cloud con policy chiare
- Onboarding e recovery assistiti
- Agent di sistema con permessi granulari e isolamento

### Criterio di uscita

NovaOS offre vantaggi AI **non replicabili** installando un chatbot su una distro generica.

---

## 10. Roadmap dell’ecosistema (vista sincronizzata)

| Prodotto | Sprint 0 | Fasi 1–2 | Fasi 3–4 | Fase 5 |
|----------|----------|----------|----------|--------|
| NovaAI | Ruolo definito in docs | Primitive di sistema | Integrazione esperienza | Maturità AI-OS |
| NovaCloud | Ruolo definito | Contratti e identity | Sync nativo | Servizi avanzati |
| NovaDocs | Mappatura nativa | — | App nativa | AI documentale di sistema |
| NovaStudio | Mappatura nativa | — | App nativa | Workflow AI assistiti |
| NovaPromo | Mappatura nativa | — | App nativa | Pipeline creativa AI |
| NovaBeauty | Mappatura nativa | — | Verticale nativo | Esperienze AI di dominio |
| NovaSky | Mappatura nativa | — | Verticale nativo | Esperienze AI di dominio |

---

## 11. Milestone di governance

| Milestone | Descrizione |
|-----------|-------------|
| **M0** | Chiusura Sprint 0 Foundation |
| **M1** | Accettazione ADR Sprint 1 (stack tecnico ufficiale) |
| **M1b** | Chiusura Sprint 2 Design System (identità Nova Shell) |
| **M1c** | Accettazione architettura Sprint 3 (`docs/platform`) |
| **M0.1** | ISO avviabile: boot, logo, login, Nova Shell iniziale, terminale, settings, power |
| **M0.0-infra** | Workspace Sprint 5 pronto (configs/scripts/vm) |
| **M2** | Prima Platform API stabile (bozza implementata) |
| **M3** | Prima esperienza desktop/installer riconoscibile |
| **M4** | Primo duo di app ecosistema native |
| **M5** | Dichiarazione pubblica “AI-First OS” supportata da capability reali |

---

## 12. Rischi e mitigazioni

| Rischio | Impatto | Mitigazione |
|---------|---------|-------------|
| Saltare a ISO/distro troppo presto | Debito strategico | Gate di fase obbligatori |
| AI solo cosmetica | Visione indebolita | Capability di sistema in architettura |
| App ecosistema scollegate | Fragilità del brand | Contratti di natività e UI unica |
| Scope eccessivo | Rallentamento | Roadmap per fasi + MVP per fase |
| Compatibilità Linux trascurata | Lock-in prematuro | Principio di sostituzione progressiva |

---

## 13. Aggiornamento della roadmap

La roadmap si aggiorna quando:

- una fase viene chiusa;
- emerge un vincolo tecnico che sposta le priorità;
- l’ecosistema Nova introduce un prodotto che richiede natività anticipata.

Ogni aggiornamento rilevante deve riflettersi anche in `architecture.md` e, se necessario, in `vision.md`.

---

## 14. Prossimo passo immediato

Dopo Sprint 5 (workspace pronto):

1. preparare host Fedora e completare `scripts/setup-build-host.sh`;
2. scrivere ricetta `configs/kiwi/novaos-m01/`;
3. implementare `scripts/build-iso.sh` per la prima ISO vanilla → branded M0.1;
4. validare con `scripts/run-vm.sh` + checklist Tier 0–2;
5. solo dopo M0.1: Shell avanzata / AI / Ryuk.

Rif: [`DEV-WORKSPACE.md`](../DEV-WORKSPACE.md) nella root del repository.
