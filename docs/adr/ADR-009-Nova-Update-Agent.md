# ADR-009 — Nova Update Agent

| Campo | Valore |
|-------|--------|
| **ID** | ADR-009 |
| **Titolo** | Agente ufficiale di aggiornamento (nova-updated) |
| **Stato** | Accettato |
| **Sprint** | Sprint 15 — Nova Update Foundation |
| **Data** | 2026-07-26 |
| **Dipende da** | ADR-004 (Package Manager), ADR-006 (Update System) |

---

## 1. Problema

ADR-006 definisce la strategia DNF → rpm-ostree, ma non fissa **come** NovaOS espone aggiornamenti a CLI, GUI e Ryuk. Serve un agente unico che:

- consumi repository RPM dedicati (non solo ISO);
- supporti canali Stable / Beta / Developer / Nightly;
- astragga il backend;
- predispona verifica firme.

---

## 2. Alternative valutate

### 2.1 Solo `dnf` / Software Center stock

Utente e tool usano direttamente DNF o PackageKit generici.

### 2.2 Update Broker Nova (`nova-updated`) + CLI/GUI

Demone di sistema con API `system.update.v1`, client `nova-updater` e futura GUI «Nova Update».

### 2.3 Solo ostree client da subito

Agente basato esclusivamente su rpm-ostree/bootc.

---

## 3. Analisi

| Alternativa | Pro | Contro |
|-------------|-----|--------|
| DNF stock | Zero codice | Nessuna UX Nova, canali/policy/AI non governabili |
| **Update Broker Nova** | Contratto stabile, canali, firme, UI unica | Manutenzione demone |
| Solo ostree | Allineato al target atomico | Troppo presto per host mutabile attuale |

---

## 4. Decisione

**Adottare `nova-updated` come Update Broker ufficiale** e `nova-updater` come CLI.

In concreto:

1. Backend iniziale: **DNF** (o mock in sviluppo).
2. IPC: socket Unix JSON che implementa `system.update.v1`.
3. Canali: `stable`, `beta`, `developer`, `nightly` (alias `dev` → `developer`).
4. Repository dedicati sotto policy Nova (`packages/repo/` + mirror remoto futuro).
5. GUI «Nova Update» come client del broker (non del packaging host diretto).
6. Traiettoria: stesso contratto verso rpm-ostree (ADR-006).

---

## 5. Motivazione

- Coerenza con System Layer e capability `system.update.apply`.
- Aggiornamenti incrementali senza nuova ISO.
- Separazione OS / componenti Nova / app già nel layout repo.
- Evita dipendenza permanente da UI Fedora stock.

---

## 6. Evoluzioni future

| Evoluzione | Quando |
|------------|--------|
| PolicyKit per Apply | Experience / hardening |
| Backend rpm-ostree | Edizione Atomic |
| Enforce firme GPG/Sigstore | Prima release pubblica |
| Eventi su Nova Bus | Con fabric IPC piattaforma |

---

## 7. Conseguenze

- Nuovo pacchetto `novaos-update` (demone + CLI + conf + unit).
- DNF resta il motore; l’utente parla Nova Update.
- Documentazione canali aggiornata rispetto a `stable/beta/dev` a tre valori.

---

## 8. Riferimenti

- [`ADR-006-Update-System.md`](ADR-006-Update-System.md)
- [`../platform/11-Nova-Update.md`](../platform/11-Nova-Update.md)
- `system/update/`, `packages/repo/`
