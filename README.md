# NovaOS

**Il sistema operativo AI-First al centro dell'ecosistema Nova.**

NovaOS non è una semplice distribuzione Linux personalizzata. È un progetto ambizioso: costruire, nel tempo, un vero sistema operativo orientato all'intelligenza artificiale, basato su Linux, sostituendo progressivamente i componenti standard con componenti sviluppati dal team Nova.

---

## Cos'è NovaOS

NovaOS è il **cuore dell'ecosistema Nova**: un sistema operativo Linux di nuova generazione progettato perché l'intelligenza artificiale non sia un'applicazione aggiuntiva, ma una capacità nativa del sistema.

L'obiettivo non è “mettere un assistente sopra Linux”. L'obiettivo è evolvere l'intero stack — shell, desktop, installer, servizi di sistema e applicazioni — verso un'esperienza unificata, coerente e AI-native, in cui ogni componente dell'ecosistema Nova possa vivere come parte integrante del sistema operativo.

### L'ecosistema Nova

NovaOS è destinato a ospitare, come componenti nativi, le applicazioni e i servizi dell'ecosistema:

| Prodotto | Ruolo nell'ecosistema |
|----------|------------------------|
| **NovaDocs** | Documentazione, scrittura e knowledge management |
| **NovaStudio** | Ambiente creativo e produttivo per lo sviluppo |
| **NovaPromo** | Strumenti per comunicazione e promozione |
| **NovaBeauty** | Esperienze e strumenti per il settore beauty |
| **NovaSky** | Servizi e applicazioni verticali NovaSky |
| **NovaCloud** | Infrastruttura cloud e sincronizzazione |
| **NovaAI** | Motore e servizi di intelligenza artificiale |

Nel tempo, queste soluzioni non resteranno “app installabili”: diventeranno **componenti nativi** di NovaOS.

---

## Visione

Creare un sistema operativo in cui l'AI sia una primitiva di sistema: presente nella shell, nel desktop, nei flussi di installazione, nella gestione delle applicazioni e nei servizi di sistema — con un'identità di prodotto unica e un'esperienza utente coerente su tutto l'ecosistema Nova.

> **Linux come fondazione. Nova come evoluzione. L'AI come capacità di sistema.**

---

## Missione

La missione di NovaOS è:

1. **Fondare** un sistema operativo basato su Linux, con roadmap chiara e architettura evolutiva.
2. **Sostituire progressivamente** componenti standard (desktop, shell, installer, servizi) con componenti Nova.
3. **Integrare nativamente** l'ecosistema Nova (NovaDocs, NovaStudio, NovaPromo, NovaBeauty, NovaSky, NovaCloud, NovaAI).
4. **Garantire** qualità da software house: documentazione, branding, processi e standard prima del codice di produzione.
5. **Costruire nel tempo** un prodotto riconoscibile, sostenibile e orientato a utenti e sviluppatori.

---

## Obiettivi del progetto

### Obiettivi strategici

- Diventare il sistema operativo di riferimento dell'ecosistema Nova.
- Offrire un'esperienza AI-First coerente, non frammentata in plugin isolati.
- Mantenere la solidità e la compatibilità dell'ecosistema Linux durante l'evoluzione.
- Costruire un brand di sistema operativo riconoscibile (identità, UX, tono di voce).

### Obiettivi tecnici (lungo termine)

- Stack desktop e shell proprietari o fortemente customizzati.
- Installer Nova con esperienza di onboarding AI-aware.
- Layer di sistema per servizi AI locali e cloud (NovaAI / NovaCloud).
- Runtime e integrazioni native per le applicazioni dell'ecosistema.
- Pipeline di build, packaging e distribuzione professionali.

### Obiettivi di processo

- Documentazione come artefatto di primo livello.
- Decisioni architetturali tracciabili.
- Roadmap per fasi, senza saltare le fondamenta.
- Decisioni tecniche tramite ADR prima di codice e ISO.

---

## Stato attuale dello sviluppo

| Elemento | Stato |
|----------|--------|
| **Sprint** | Sprint 6 — ISO build infrastructure |
| **Build** | KIWI description + scripts **operativi** |
| **ISO** | Generabile con `sudo make iso` su host Fedora |
| **Nova Shell / Ryuk / AI** | Non inclusi (intenzionale) |
| **Guida build** | [`DEV-WORKSPACE.md`](DEV-WORKSPACE.md) |

### Prima ISO (M0.1 foundation)

```bash
make validate && sudo make setup && make check && sudo make iso && make vm
```

Login immagine: `nova` / `novaos` — `configs/kiwi/novaos-m01/CREDENTIALS.txt`

---

## Roadmap iniziale

| Fase | Nome | Focus |
|------|------|--------|
| **Sprint 0** | Foundation | Repository, documentazione, branding, processi |
| **Sprint 1** | Decisioni tecniche | ADR su base, desktop, build, packaging, update, AI |
| **Sprint 2** | Identità visiva | Design System completo, specifica Nova Shell |
| **Sprint 3** | Architettura software | Platform, AI Core, Ryuk, Services, SDK, Security |
| **Sprint 4** | Boot Foundation | Pipeline ISO, boot flow, Milestone 0.1 |
| **Sprint 5** | Dev Infrastructure | Workspace build/configs/assets/iso/packages/vm/tools |
| **Fase 1** | Platform Base | Toolchain attiva, packaging, **prima ISO (M0.1)** |
| **Fase 2** | System Core | Componenti di sistema, servizi, integrazioni AI di base |
| **Fase 3** | Experience Layer | Implementazione Nova Shell, installer, UI in prodotto |
| **Fase 4** | Ecosystem Native | Integrazione nativa di NovaDocs, NovaStudio e resto ecosistema |
| **Fase 5** | AI-First OS | Capacità AI di sistema mature e differenziazione competitiva |

Dettaglio completo: [`docs/roadmap.md`](docs/roadmap.md).

---

## Struttura del repository

```text
NovaOS/
├── build/            # Workdir/cache/log di build
├── configs/          # Fedora, KIWI NG, bootstrap, profili
├── assets/           # Asset da impacchettare (branding, splash, sddm, …)
├── iso/              # Output ISO + checksum
├── packages/         # Sorgenti RPM Nova (branding/release/theme)
├── scripts/          # Entrypoint pipeline (stub Sprint 5)
├── vm/               # Test QEMU/KVM
├── tools/            # Utility (lint workspace)
├── docs/             # Documentazione ufficiale
├── branding/         # Identità creativa di progetto
├── desktop/          # Futuro Nova Shell (non implementato)
├── shell/            # Futura CLI Nova
├── installer/        # Installer (spec in boot-foundation)
├── apps/             # Futuro ecosistema
├── ai/               # Futuro Nova AI Core
├── system/           # Futuro system / Ryuk
├── .github/          # CI/CD futuro
├── DEV-WORKSPACE.md  # Guida infrastruttura Sprint 5
├── README.md
├── LICENSE
└── .gitignore
```

Dettaglio motivato: [`DEV-WORKSPACE.md`](DEV-WORKSPACE.md).

### Documentazione (`docs/`)

| Documento | Contenuto |
|-----------|-----------|
| [`vision.md`](docs/vision.md) | Visione strategica e ruolo nell'ecosistema Nova |
| [`roadmap.md`](docs/roadmap.md) | Roadmap per fasi e principi di avanzamento |
| [`architecture.md`](docs/architecture.md) | Architettura di riferimento (alto livello) |
| [`ui-guidelines.md`](docs/ui-guidelines.md) | Linee guida UI/UX del sistema |
| [`adr/`](docs/adr/README.md) | Architecture Decision Records (Sprint 1) |
| [`design-system/`](docs/design-system/README.md) | Identità visiva e Nova Shell (Sprint 2) |
| [`platform/`](docs/platform/README.md) | Architettura software (Sprint 3) |
| [`boot-foundation/`](docs/boot-foundation/README.md) | Prima ISO / Milestone 0.1 (Sprint 4) |

---

## Principi di lavoro

1. **Fondamenta prima del codice** — nessuna scorciatoia su visione, architettura e standard.
2. **Sostituzione progressiva** — evoluzione controllata, non “fork e riscrittura totale” al giorno zero.
3. **Ecosistema unificato** — NovaOS è la piattaforma; i prodotti Nova ne sono i cittadini nativi.
4. **AI come capacità di sistema** — non come feature cosmética.
5. **Qualità da software house** — documentazione, processi e decisioni esplicite.

---

## Come contribuire (fase infrastruttura)

1. Leggere [`DEV-WORKSPACE.md`](DEV-WORKSPACE.md).  
2. Verificare la struttura: `bash tools/lint/lint-workspace.sh` e `bash scripts/check-env.sh`.  
3. Non introdurre Ryuk/AI/Shell di prodotto finché M0.1 non è in esecuzione pianificata.  
4. Le ricette KIWI e i pacchetti branding arriveranno negli sprint di build ISO.

---

## Licenza

Questo progetto è rilasciato sotto i termini descritti nel file [`LICENSE`](LICENSE).

---

## Contatti e ownership

**Progetto:** NovaOS  
**Organizzazione:** Nova  
**Ruolo del repository:** Cuore dell'ecosistema Nova — sistema operativo AI-First basato su Linux

Per la visione completa, consultare [`docs/vision.md`](docs/vision.md).
