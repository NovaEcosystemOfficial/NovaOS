# ADR-003 — Build System

| Campo | Valore |
|-------|--------|
| **ID** | ADR-003 |
| **Titolo** | Selezione del sistema di build delle immagini |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | ADR-001 (Base Linux) |

---

## 1. Problema

NovaOS dovrà produrre, in fasi successive, immagini installabili e/o live (ISO e artefatti correlati). Serve decidere **quale sistema di build** userà il team per:

- definire in modo dichiarativo il contenuto dell’immagine;
- riprodurre build in CI;
- supportare varianti (dev, stable, HW-specific);
- evolvere verso appliance immutabili senza cambiare completamente toolchain.

In Sprint 1 non si costruisce ancora la ISO: si sceglie lo strumento e i criteri.

---

## 2. Alternative valutate

### 2.1 KIWI NG

Tool dichiarativo (XML/YAML description) per costruire immagini di sistemi Linux (ISO, qcow, OEM, PXE, ecc.), originato nell’ecosistema SUSE/openSUSE ma capace di target multipli, incluso Fedora/RPM in scenari supportati.

### 2.2 livemedia-creator

Toolkit Fedora/Red Hat (Lorax stack) per creare live media e immagini installabili a partire da kickstart e repository Fedora.

### 2.3 Cubic

UI/tool orientato a remix di Ubuntu (chroot grafico dell’ISO), molto usato per derivate desktop Ubuntu-like.

---

## 3. Analisi vantaggi / svantaggi

### KIWI NG

| Vantaggi | Svantaggi |
|----------|-----------|
| Descrizione immagini dichiarativa e versionabile | Curva di apprendimento iniziale non banale |
| Supporto a molti formati di output (live, install, cloud, disk) | Documentazione e esempi spesso openSUSE-centrici |
| Adatto a un prodotto OS con più edizioni | Setup CI più articolato all’inizio |
| Buona disciplina “appliance engineering” | Va validato il target Fedora nei pipeline Nova |
| Allineato a una visione di lungo periodo (non solo remix ISO) | Overkill se si volesse solo un remix one-shot |

### livemedia-creator

| Vantaggi | Svantaggi |
|----------|-----------|
| Native Fedora: massima coerenza con ADR-001 | Meno “multi-output product engineer” di KIWI |
| Kickstart familiare nell’ecosistema RHEL/Fedora | Tooling a tratti frammentato (Lorax, livemedia-creator, varianti) |
| Percorso diretto alle pratiche ufficiali Fedora | Personalizzazioni molto profonde richiedono disciplina kickstart |
| Buono per MVP ISO Fedora-based | Portabilità verso non-Fedora scarsa (accettabile se ADR-001 tiene) |
| Integrabile in CI con container Fedora | Meno astrazione dichiarativa unificata multi-formato |

### Cubic

| Vantaggi | Svantaggi |
|----------|-----------|
| Rapidità per prototipi visuali su Ubuntu | Dipende da Ubuntu: **non coerente** con ADR-001 Fedora |
| Bassa barriera d’ingresso | Modello “remix” più che “image as code” enterprise |
| Utile a demo rapide | Scarso fit con DNF/rpm-ostree e piano immutabile |
| Community tutorial abbondanti | Rischio di debito: ISO fatte a mano difficili da riprodurre |

---

## 4. Decisione proposta

**Raccomandazione: adottare KIWI NG come sistema di build primario di NovaOS.**

In parallelo:

1. **livemedia-creator** resta **alternativa operativa ammessa** per spike e prototipi ISO Fedora nelle prime iterazioni di Platform Base, se accelera l’apprendimento del team.
2. **Cubic** viene **scartato** come toolchain ufficiale, perché ottimizzato per Ubuntu e per un modello di remix non allineato alla base scelta.
3. Tutte le descrizioni di immagine ufficiali vivranno sotto controllo versione (es. futuro `installer/` / `image/` — da definire in Fase di implementazione, non in questo sprint di codice).

---

## 5. Motivazione tecnica

1. **NovaOS non è un remix estetico**  
   Serve un tool pensato per descrivere un’appliance/OS riproducibile. KIWI NG spinge verso “image as code”, coerente con una software house che costruisce un prodotto.

2. **Multi-formato nel tempo**  
   Oltre alla ISO installer serviranno immagini per VM, cloud, possibly OEM. KIWI riduce il rischio di accumulare tool diversi per ogni target.

3. **Coerenza con la traiettoria immutabile**  
   Anche se l’immutabilità arriva dopo (ADR-006), scegliere un build system capace di evolvere evita un ripartenza totale tra MVP mutabile e edizione atomica.

4. **livemedia-creator non è “sbagliato”**  
   È la scelta più naturale “Fedora-pure”. Viene mantenuto come piano B/spike perché riduce il time-to-first-ISO. La primazia di KIWI deriva dalla visione prodotto pluriennale, non da ostilità al tooling Fedora.

5. **Cubic eliminato per incoerenza strategica**  
   Adottarlo spingerebbe il progetto indietro verso Ubuntu, contraddicendo ADR-001, oppure creerebbe una dipendenza morta.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **Catalogo edizioni KIWI** | `novaos-desktop`, `novaos-dev`, `novaos-atomic` | Dopo prima ISO interna |
| **CI signed artifacts** | Build → sign → publish automatici | Con `.github` workflows |
| **bootc / container-native images** | Se l’OS evolve verso container-built hosts | Con ADR-006 in fase avanzata |
| **Promozione livemedia-creator** | Solo se KIWI blocca delivery su Fedora | Review ADR esplicita |
| **SBOM delle immagini** | Distinte distro package + componenti Nova | Requisito sicurezza prodotto |

---

## 7. Conseguenze

### Positive

- Toolchain di build orientata al prodotto, non al one-off.
- Maggiore riproducibilità e auditabilità.
- Spazio per più artefatti oltre la ISO.

### Negative / rischi

- Investimento iniziale di competenza KIWI.
- Necessità di validare pipeline Fedora in modo rigoroso.
- Tentazione di “fare comunque Cubic” per velocità → da rifiutare.

### Mitigazioni

- Spike time-boxed con livemedia-creator per apprendere contenuti Fedora.
- ADR review dopo il primo green build.
- Documentare convention delle image description Nova.

---

## 8. Riferimenti

- ADR-001, ADR-006
- [`../roadmap.md`](../roadmap.md) — Fase 1 Platform Base

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
