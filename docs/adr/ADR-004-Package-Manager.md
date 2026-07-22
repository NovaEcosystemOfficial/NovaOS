# ADR-004 — Package Manager

| Campo | Valore |
|-------|--------|
| **ID** | ADR-004 |
| **Titolo** | Selezione del gestore pacchetti |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | ADR-001 (Base Linux) |

---

## 1. Problema

Il package manager è il meccanismo primario di installazione, aggiornamento e dipendenze del software di sistema. Per NovaOS determina:

- formato dei pacchetti dell’ecosistema Nova;
- integrazione con update system (ADR-006);
- esperienza sviluppatore e CI;
- modello di repository (ufficiali Fedora + repo Nova).

La scelta è fortemente vincolata dalla base Linux, ma va resa esplicita perché tocca packaging delle app native (NovaDocs, NovaStudio, …) e dei componenti OS.

---

## 2. Alternative valutate

### 2.1 DNF

Gestore pacchetti di Fedora/RHEL/CentOS Stream, opera su RPM, supporta moduli/repo multipli, API robuste, evoluzione verso DNF5.

### 2.2 APT

Gestore pacchetti Debian/Ubuntu, opera su DEB, standard de facto del mondo Debian-like.

### 2.3 Pacman

Gestore pacchetti Arch Linux, modello semplice e veloce, orientato a rolling release.

---

## 3. Analisi vantaggi / svantaggi

### DNF

| Vantaggi | Svantaggi |
|----------|-----------|
| Coerente al 100% con Fedora (ADR-001) | Meno familiare a chi viene solo da Debian |
| Buone API / scripting per tooling Nova | Storicamente percepito più lento di pacman (mitigato da DNF5) |
| Integrazione naturale con rpm-ostree / layering (ADR-006) | Complessità repo/modularity da governare |
| Ecosistema RPM enterprise-proven | Packaging RPM ha learning curve |
| Transazioni, history, rollback a livello package | UX utente finale va comunque wrappata da UI Nova |

### APT

| Vantaggi | Svantaggi |
|----------|-----------|
| Maturo, diffusissimo, tooling ricco | Richiederebbe base Debian/Ubuntu → contraddice ADR-001 |
| Familiarità elevata nel settore | Dual-stack RPM+DEB sarebbe un incubo operativo |
| Buona storia di pinning e policy | Non integra il percorso rpm-ostree scelto in ADR-006 |
| Facile trovare contributor | Migrazione futura costosissima se scelta “per abitudine” |

### Pacman

| Vantaggi | Svantaggi |
|----------|-----------|
| Velocità e semplicità concettuale | Legato ad Arch → non adatto come base prodotto (ADR-001) |
| PKGBUILD accessibili | AUR non è un modello di supply chain per OS commerciale |
| Ottimo per lab interni | Nessun path pulito verso update atomici Fedora-like |

---

## 4. Decisione proposta

**Raccomandazione: adottare DNF come package manager ufficiale di NovaOS.**

In concreto:

1. RPM come formato di packaging dei componenti di sistema Nova.
2. Repository NovaOS ufficiali (prodotti ecosistema + componenti OS) consumati via DNF.
3. APT e Pacman non sono supportati come gestori di sistema.
4. Eventuali formati paralleli (Flatpak per sandbox app) possono essere valutati **in ADR dedicate future**, senza sostituire DNF come root package manager del sistema.

---

## 5. Motivazione tecnica

1. **Coerenza vincolante con ADR-001**  
   Su Fedora, DNF non è un’opzione tra pari: è il gestore nativo. Scegliere APT/Pacman come “primari” implicherebbe cambiare base o mantenere un Frankenstein inaccettabile.

2. **Allineamento ad ADR-006**  
   Il percorso verso `rpm-ostree` presuppone mondo RPM. DNF resta lo strumento di day-2 management sulla variante mutabile e il riferimento concettuale per il layering sulle edizioni atomiche.

3. **Ecosistema app native**  
   NovaDocs, NovaStudio, ecc. potranno essere distribuiti come RPM firmati nei repo Nova, con dipendenze di sistema chiare — requisito per la “natività”.

4. **APT/Pacman valutati e scartati motivatamente**  
   Non per inferiorità assoluta, ma per **incompatibilità strategica** con la base e con il modello di update. In un ADR onesto vanno comunque analizzati: qui lo sono, e perdono sul criterio di coerenza di piattaforma.

5. **Esperienza utente**  
   L’utente finale di NovaOS non dovrà necessariamente “parlare DNF”: Software Center / update UI Nova potranno astrarlo. La decisione riguarda il **contratto tecnico di piattaforma**.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **DNF5 ovunque** | Standardizzare su DNF5 non appena stabile nei target Nova | Allineamento alle release Fedora adottate |
| **Repo Nova a canali** | `stable`, `beta`, `dev` | Con primo programma di release |
| **Flatpak come canale app sandboxed** | Complementare, non sostitutivo | ADR futura dedicata |
| **Firmare e attestare pacchetti** | Sigstore/GPG policy | Prima di release pubblica |
| **Packaging monorepo → RPM** | Pipeline da `apps/` e `system/` a artefatti | Fase Ecosystem Native |

---

## 7. Conseguenze

### Positive

- Una sola verità sul packaging di sistema.
- Compatibilità nativa con update path atomico.
- Base chiara per CI di build pacchetti Nova.

### Negative / rischi

- Skill RPM necessarie nel team.
- Tentazione di “installare roba da script generici” bypassando DNF → da vietare in policy.

### Mitigazioni

- Linee guida packaging Nova (da scrivere in Fase 1).
- Template RPM per componenti ecosistema.
- Gate CI: niente dipendenze non tracciate nei repo ufficiali.

---

## 8. Riferimenti

- ADR-001, ADR-003, ADR-006
- [`../architecture.md`](../architecture.md)

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
