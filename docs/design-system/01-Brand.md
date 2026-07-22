# 01 — Brand

**NovaOS Design System — Identità di marca**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica ufficiale di design (pre-asset)  
**Superficie primaria:** Nova Shell

---

## 1. Scopo

Questo documento definisce **chi è NovaOS** sul piano percettivo: nome, personalità, promesse visive e confini rispetto ad altri sistemi operativi. Tutto ciò che appare in Nova Shell, installer, boot e app native deve poter superare il test:

> *Se rimuovo il logo, riconosco ancora Nova?*

Se la risposta è no, il branding è troppo debole.

---

## 2. Posizionamento

| Dimensione | Dichiarazione |
|------------|---------------|
| **Cosa è** | Sistema operativo AI-First, cuore dell’ecosistema Nova |
| **Cosa non è** | Distro rinominata, theme pack, “Linux con assistente” |
| **Promessa** | Eleganza operativa: potenza sotto controllo, AI come capacità di sistema |
| **Territorio emotivo** | Calma tecnologica, precisione, luminosità controllata |
| **Antagonisti percettivi** | Windows (taskbar/Start paradigm), macOS (dock/traffic lights), KDE stock (Breeze generico) |

---

## 3. Filosofia del brand

### 3.1 Nova = nuova luce, non rumore

Una *nova* è un aumento improvviso di luminosità: energia, chiarezza, segnale. Il brand traduce questa idea in **luci utili**, non in glow decorativi ovunque.

### 3.2 Intelligenza silenziosa

L’AI non grida. Si manifesta come **presenza affidabile**: suggerimenti proporzionati, stati chiari, zero mascotte invadenti.

### 3.3 Minimalismo strutturale

Si rimuove ciò che non serve al compito. Il minimalismo Nova è **architettonico** (gerarchia, ritmo, vuoto intenzionale), non povertà grafica.

### 3.4 Velocità percepita

La velocità non si comunica con animazioni frenetiche, ma con **risposta immediata**, transizioni brevi e interfacce che non fanno aspettare senza feedback.

### 3.5 Affidabilità visibile

Stati, conferme e rollback sono parte del brand: un OS serio non nasconde la verità dietro metafore carine.

---

## 4. Personalità di marca (brand personality)

| Tratto | Intensità | Come si vede |
|--------|-----------|--------------|
| Elegante | Alta | Tipografia curata, pochi materiali, contrasti deliberati |
| Veloce | Alta | Feedback < 100ms dove possibile, motion corte |
| Minimale | Alta | Una composizione per vista, pochi accenti |
| Tecnologico | Alta | Griglie precise, segnali di sistema nitidi |
| Intelligente | Alta | AI integrata nelle superfici, non “app a parte” |
| Affidabile | Alta | Copy onesto, stati espliciti, niente dark pattern |
| Giocoso | Bassa | Mai meme di sistema; ironia solo se utile |
| Agressivo / gamer | Null | Vietato RGB caotico, neon illimitati |

**Archetipo:** *Il Navigatore* — guida con chiarezza, non domina con spettacolo.

---

## 5. Nome e nomenclatura

| Nome | Uso |
|------|-----|
| **NovaOS** | Sistema operativo / prodotto |
| **Nova Shell** | Desktop ufficiale e cuore dell’esperienza utente |
| **NovaAI** | Capacità AI di sistema (non “assistente con nome da pet”) |
| **Nova Cloud** / prodotti ecosistema | Come da ecosistema; in UI di sistema usare naming coerente |

### Regole

- In UI: **Nova Shell** per l’ambiente desktop, non “Plasma”, non “Desktop Environment”.
- Verso utenti finali non esporre nomi upstream (KDE, SDDM, Fedora) come identità di prodotto.
- L’entry point AI di sistema si chiama **NovaAI** (o invocazione “Nova”), mai nomi che evochino Siri/Cortana/Chatbot generici.

---

## 6. Stile grafico (art direction)

### Direzione: **Luminous Precision** (Precisione luminosa)

- Superfici sobrie, profondità controllata, luce come segnale.
- Geometrie a **raggio contenuto** (non pill infinite, non squircle Apple ovunque).
- Materiale distintivo: **Nova Glass** — vetro tecnico opalescente, non acrylic Windows né vibrancy macOS.
- Accento caldo “stellar” su campo freddo “ink” → contrasto di carattere unico.
- Griglia rigorosa; allineamenti ottici, non “widget sparsi”.

### Vietato (anti-pattern di identità)

| Evitare | Perché |
|---------|--------|
| Copiare layout Windows 11 (taskbar centrale + Start) | Conflitto di riconoscimento |
| Dock basso centrato con magnify | Lettura macOS |
| Breeze blue + pannello KDE di default | Lettura “tema KDE” |
| Viola/indigo “AI cliché” come colore dominante | Generico e già saturo nel mercato AI |
| Glow multistrato ovunque | Rumore, non eleganza |
| Traffici luci rosso/giallo/verde | Firma Apple |
| Icone Fluent/SF clonate | Contaminazione di linguaggio |

---

## 7. Logo e mark (specifica concettuale)

> Sprint 2 non produce file grafici. Qui si definisce il *brief* vincolante per `branding/`.

### 7.1 Mark “Nova”

- Simbolo astratto di **nucleo + alone** (sorgente luminosa), geometria semplice, leggibile a 16px.
- Non una mascotte; non una lettera N ornate; non una stella a 5 punte banale.
- Preferenza: monolinea o forma piena a due pesi (core pieno + ring sottile).

### 7.2 Wordmark

- “NovaOS” in tipografia display del sistema (vedi `03-Typography.md`).
- Tracking leggermente aperto; “OS” non deve sembrare pedice tecnico brutto.
- Divieto di gradienti arcobaleno sul wordmark ufficiale.

### 7.3 Clear space e minimo

- Clear space ≥ altezza della “o” del wordmark su tutti i lati.
- Dimensione minima mark: 16×16 dp; wordmark orizzontale minimo ~96 dp di larghezza.

### 7.4 Varianti

| Variante | Uso |
|----------|-----|
| Mark alone | Favicon, boot splash piccolo, AppIcon sistema |
| Wordmark | About, installer hero, documentazione |
| Lockup orizzontale | Navbar, header ufficiali |
| Mono chiaro/scuro | Su fotografie / fondali estremi |

---

## 8. Voice & tone (brand verbale in UI)

| Contesto | Tono |
|----------|------|
| Sistema | Diretto, preciso, rispettoso |
| Errori | Onesto + next step |
| AI | Collaborativo, mai paternalistico |
| Onboarding | Accogliente, una cosa alla volta |
| Successo | Sobrio (“Fatto”), non confetti |

**Pronomi:** “tu” in italiano UI consumer; “Lei” solo in contesti enterprise espliciti.

---

## 9. Relazione con l’ecosistema Nova

NovaOS è il **cuore**; le app (NovaDocs, NovaStudio, NovaPromo, NovaBeauty, NovaSky, NovaCloud, NovaAI) ereditano:

- palette e token;
- tipografia;
- raggio, blur, motion;
- tono.

Possono avere accenti di dominio **secondari**, mai un’identità che rompe la lettura “sono su Nova”.

---

## 10. Test di riconoscimento (gate di brand)

Prima di approvare qualsiasi superficie:

1. **Blind test:** screenshot senza wordmark — il team la riconosce come Nova?
2. **Swap test:** se sostituissi i colori con quelli di Windows/macOS/KDE, il layout sembra ancora “loro”? Se sì, il layout è contaminato.
3. **AI test:** togliendo l’AI, resta un OS con carattere? Se no, l’AI era solo trucco.
4. **Distance test:** a 1 metro / su laptop 13", la gerarchia regge?

---

## 11. Motivazione della direzione

Si è scartato un look “enterprise grigio anonimo” (no personalità) e un look “cyberpunk neon” (no affidabilità).  
**Luminous Precision** bilancia eleganza e tecnologia: luce come informazione, silenzio come lusso, AI come infrastruttura.

---

## 12. Riferimenti incrociati

- `02-Color-Palette.md` — colori e temi
- `03-Typography.md` — voce tipografica
- `05-Desktop-Layout.md` — Nova Shell
- `09-Design-Principles.md` — principi operativi
- `../ui-guidelines.md` — gate UX precedenti
- `../../branding/` — destinazione asset futuri
