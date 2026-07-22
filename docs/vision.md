# Visione di NovaOS

**Documento di visione strategica — Sprint 0 (Foundation)**  
**Stato:** ufficiale per la fase fondativa  
**Lingua:** italiano

---

## 1. Premessa

NovaOS non nasce come “un’altra distro Linux con un tema e un wallpaper”.

Nasce come **progetto di sistema operativo**: un percorso pluriennale per costruire, sopra fondazioni Linux solide, un sistema AI-First in cui i componenti standard vengono sostituiti — in modo progressivo, disciplinato e misurabile — da componenti progettati e sviluppati dal team Nova.

Questo documento definisce **perché** esiste NovaOS, **cosa** deve diventare e **come** si colloca rispetto all’intero ecosistema Nova.

---

## 2. Dichiarazione di visione

> **NovaOS sarà il sistema operativo AI-First al centro dell’ecosistema Nova: una piattaforma Linux evoluta in cui intelligenza artificiale, desktop, shell, servizi di sistema e applicazioni native formano un’unica esperienza di prodotto.**

In questa visione:

- **Linux** è la base tecnica affidabile e interoperabile.
- **Nova** è l’identità, il prodotto e la direzione evolutiva.
- **L’AI** non è un addon: è una capacità di sistema.

---

## 3. Il problema che affrontiamo

Oggi l’esperienza “AI su un computer” è tipicamente frammentata:

- assistenti isolati nelle applicazioni;
- integrazioni cloud scollegate dal sistema;
- desktop e shell che non conoscono il contesto dell’utente;
- prodotti di un ecosistema che vivono come software di terze parti sul sistema operativo di qualcun altro.

Per un’organizzazione che costruisce un ecosistema completo (documentazione, studio, promo, verticali, cloud, AI), questa frammentazione è un limite strategico.

**NovaOS esiste per chiudere il cerchio:** trasformare l’ecosistema Nova da insieme di prodotti a **piattaforma di sistema**.

---

## 4. NovaOS come cuore dell’ecosistema

NovaOS è il **cuore** dell’ecosistema Nova. Tutti i prodotti seguenti sono destinati, nel tempo, a diventare **componenti nativi** del sistema operativo:

| Componente ecosistema | Ambito | Destinazione in NovaOS |
|----------------------|--------|-------------------------|
| **NovaDocs** | Documentazione, scrittura, knowledge | App e servizi nativi di produttività documentale |
| **NovaStudio** | Creatività e sviluppo | Ambiente nativo per creazione e engineering |
| **NovaPromo** | Comunicazione e promozione | Suite nativa per contenuti e campagne |
| **NovaBeauty** | Verticale beauty | Esperienze e tool nativi di settore |
| **NovaSky** | Verticale NovaSky | Servizi e app native del dominio Sky |
| **NovaCloud** | Cloud e sync | Layer di sistema per account, sync e servizi remoti |
| **NovaAI** | Intelligenza artificiale | Motore e API di sistema per capacità AI |

### Principio di natività

Un componente è “nativo” quando:

1. è progettato per l’esperienza NovaOS (non solo “compatibile”);
2. può usare servizi di sistema Nova (identità, AI, cloud, notifiche, intent);
3. rispetta branding, UI guidelines e contratti di piattaforma;
4. può essere distribuito, aggiornato e governato come parte del sistema.

---

## 5. Principi guida

### 5.1 AI-First, non AI-washed

L’AI deve migliorare flussi reali: installazione, ricerca, automazione, assistenza contestuale, accessibilità, produttività. Non deve ridursi a un chatbot decorativo.

### 5.2 Sostituzione progressiva

Non si riscrive tutto il giorno zero. Si definiscono confini chiari, si sostituiscono componenti quando la qualità Nova supera lo standard, si mantiene compatibilità dove serve.

### 5.3 Un solo prodotto, molte superfici

Desktop, shell, installer e app devono parlare la stessa lingua di design, interazione e brand.

### 5.4 Fondamenta prima del codice

Visione, architettura, roadmap, standard UI e struttura di repository precedono implementazione, scelta della distro e ISO.

### 5.5 Qualità da software house

Decisioni documentate, ownership chiara, release disciplinata, debito tecnico gestito.

### 5.6 Rispetto delle fondamenta Linux

NovaOS evolve Linux; non lo nega. Compatibilità, packaging e interoperabilità restano vincoli di prim’ordine finché non esistono alternative Nova mature.

---

## 6. Esperienza utente desiderata (orizzonte)

Un utente di NovaOS dovrebbe percepire:

- un sistema **riconoscibile** come Nova, non come una distro generica rinominata;
- un’AI **sempre disponibile** nel contesto giusto (sistema, app, shell);
- un ecosistema di app **coerente**, non un collage di tool scollegati;
- un onboarding e un installer che **guidano**, non che confondono;
- aggiornamenti e servizi cloud **integrati** nel modello mentale del sistema.

---

## 7. Esperienza sviluppatore desiderata (orizzonte)

Un contributore o partner dovrebbe trovare:

- documentazione chiara su visione, architettura e confini dei moduli;
- repository organizzato per aree di responsabilità (`desktop/`, `shell/`, `ai/`, …);
- contratti di piattaforma stabili per integrare app native;
- toolchain e CI prevedibili (introdotti dopo Sprint 0).

---

## 8. Cosa NovaOS non è (in questa fase)

Per evitare ambiguità strategiche, Sprint 0 chiarisce anche i non-obiettivi immediati:

| Non-obiettivo Sprint 0 | Motivo |
|------------------------|--------|
| Scrivere codice del sistema operativo | Prima servono fondamenta e decisioni |
| Scegliere la distribuzione Linux | Scelta architetturale della Fase 1 |
| Produrre una ISO | Conseguenza della piattaforma base, non punto di partenza |
| Rilasciare un “theme pack” e chiamarlo OS | Fuori dalla visione del progetto |

---

## 9. Criteri di successo della visione

La visione si considera sulla buona strada quando:

1. NovaOS è riconosciuto internamente come **piattaforma centrale** dell’ecosistema, non come side-project.
2. Ogni prodotto Nova ha una **traiettoria di nativizzazione** documentata.
3. Le decisioni di sostituzione dei componenti standard sono **motivate da qualità e coerenza**, non da urgenza.
4. L’AI appare nei documenti di architettura come **layer di sistema**, non come feature di una singola app.
5. La documentazione resta allineata allo stato reale del progetto.

---

## 10. Relazione con gli altri documenti

| Documento | Ruolo rispetto alla visione |
|-----------|-----------------------------|
| [`roadmap.md`](roadmap.md) | Traduce la visione in fasi e priorità |
| [`architecture.md`](architecture.md) | Definisce i confini tecnici e i layer |
| [`ui-guidelines.md`](ui-guidelines.md) | Rende la visione tangibile nell’esperienza |
| [`../README.md`](../README.md) | Sintesi pubblica del progetto |

---

## 11. Conclusione

NovaOS è un investimento di lungo periodo: **fondare un sistema operativo** per un ecosistema di prodotti che oggi esistono (o esisteranno) come pezzi separati, e che domani dovranno vivere come un tutt’uno.

Sprint 0 fissa questa direzione. Tutto ciò che verrà dopo — base Linux, codice, ISO, desktop, AI di sistema — dovrà poter rispondere a una domanda semplice:

> *Questo ci avvicina a un vero OS AI-First Nova, o ci allontana verso una distro personalizzata?*

Se la risposta non è chiara, la decisione non è pronta.
