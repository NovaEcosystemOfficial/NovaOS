# NovaOS Vision 2.0

**Documento di visione esperienza**  
**Stato:** ufficiale — guida ogni scelta grafica e tecnica  
**Lingua:** italiano

> Questa non è una semplice distribuzione Linux personalizzata.  
> L’obiettivo è un sistema operativo moderno, elegante e intelligente che mette l’utente al centro.

---

## 1. Filosofia

| Principio | Significato |
|-----------|-------------|
| Minimalismo | Solo ciò che serve, niente di più |
| Eleganza | Forma e dettaglio coerenti con l’identità Nova |
| Fluidità | Transizioni brevi, naturali, mai teatrali |
| Velocità | Il sistema deve sembrare e essere reattivo |
| Nessuna distrazione | Nessun rumore UI, badge o chrome inutile |
| AI non invasiva | L’intelligenza aiuta; non invade |

**Regole operative**

- Se una funzione può essere semplificata, va semplificata.
- L’utente non deve cercare il sistema: il sistema anticipa l’utente.
- Prima di ogni nuova feature: *«Migliora davvero l’esperienza dell’utente?»* — se no, non implementarla.

---

## 2. Desktop

- Desktop **pulito**: lo sfondo è il protagonista.
- Icone **opzionali**.
- Nessun elemento inutile.
- Senza finestre aperte il desktop diventa **Nova Home** (Home intelligente).

---

## 3. Nova Home

Il desktop non è uno spazio vuoto. Mostra solo ciò che è utile:

- Saluto
- Ora
- Meteo *(futuro)*
- Documenti recenti
- Attività recenti
- Aggiornamenti
- Accesso rapido alle app Nova
- Stato Ryuk

**Tutto deve poter essere nascosto.**

---

## 4. Top Bar

- Sottile, mai invasiva.
- **Mai** sopra le finestre; **mai** impedire chiusura/uso delle app.
- Deve **ridimensionare l’area di lavoro** (strut / reserved space), non coprirla.
- Contenuto minimo:
  - Logo Nova
  - Ora
  - Notifiche
  - Wi‑Fi
  - Audio
  - Batteria *(solo se presente)*

CPU, RAM, Disco e metriche di sistema vivono nel **Control Center**, non nella barra.

---

## 5. Dock

- Inferiore, **centrata**.
- Animazioni morbide; ingrandimento al hover.
- Indicatori app aperte.
- Drag & drop; personalizzabile.

---

## 6. Nova Hub

Cuore dell’interfaccia — **non** un menu Start.

Punto di accesso al sistema:

- Ricerca, Applicazioni, Documenti, Impostazioni  
- Nova Center, Nova Update  
- NovaDocs, Nova Studio, NovaPromo, NovaSky, NovaBeauty, NovaCloud  
- Ryuk  

*(Nota: Hub/Launcher evolvono verso questa visione; Kickoff KDE resta finché Hub non è stabile.)*

---

## 7. Control Center

Accessibile dalle icone della Top Bar:

- Wi‑Fi, Bluetooth, Audio, Luminosità, VPN  
- Tema, Modalità Focus  
- Stato sistema, Aggiornamenti  

---

## 8. Animazioni

Ogni motion deve essere **breve**, **fluida**, **elegante**.  
Mai appariscente. Mai rallentare il sistema.

---

## 9. Finestre

- Angoli arrotondati  
- Blur leggero  
- Ombra morbida  
- Apertura/chiusura animate  

---

## 10. Ryuk

Ryuk **non** è un’applicazione: è parte del sistema operativo.

Ogni componente deve poter dialogare con Ryuk. In futuro controllerà:

- applicazioni, file, aggiornamenti, impostazioni  
- notifiche, automazioni  

---

## 11. Identità

NovaOS **non** deve sembrare KDE, GNOME, Windows o macOS.

Può ispirarsi alle migliori idee, ma deve avere **identità propria**.  
Test: da uno screenshot l’utente deve poter dire *«Questo è NovaOS.»*

---

## 12. Allineamento con il codebase (snapshot)

| Visione 2.0 | Stato attuale (indicativo) |
|-------------|----------------------------|
| Top Bar sottile, strut, no overlay | `nova-shell` TopBarManager (auto-hide) — da allineare a strut + chrome minimo |
| Metriche solo in Control Center | Widget CPU/RAM/Disco ancora in barra — da spostare |
| Dock centrata | API dock in shell — UI da completare |
| Nova Hub come cuore | `nova-hub` + `nova-launcher` in parallelo a KDE |
| Control Center | Da implementare |
| Nova Home sul desktop vuoto | Da implementare |
| Ryuk di sistema | Placeholder / planned nei servizi Platform |

I prossimi sprint devono **chiudere il gap** verso Vision 2.0, una superficie alla volta, senza regressioni e solo via Nova Update.

---

## 13. Relazioni

- Visione strategica fondativa: [`../vision.md`](../vision.md)  
- Design System: [`../design-system/`](../design-system/README.md)  
- Platform / Shell / Hub / Launcher: [`../platform/`](../platform/README.md)  
