# `configs/`

Configurazioni **versionate** dell’infrastruttura di build e del profilo Fedora/KIWI per NovaOS.

## Scopo (Sprint 5)

Centralizzare le ricette e i file di configurazione che definiscono *come* si costruisce l’immagine, senza ancora implementare il desktop completo o i servizi AI.

## Motivazione

Le config devono essere:

1. **revisionabili in PR** (diff leggibili);
2. **disaccoppiate** dagli artefatti in `build/` e `iso/`;
3. **allineate agli ADR** (Fedora, KIWI, SDDM, DNF).

## Struttura

```text
configs/
├── README.md
├── fedora/          # profilo pacchetti e override Fedora
├── kiwi/            # image description KIWI NG
├── bootstrap/       # opzioni di bootstrap/ambiente
└── profile/         # profili nominati (m01, dev, …)
```

## Relazione con Milestone 0.1

Le config M0.1 descriveranno una Fedora KDE branded minima.  
**Non** includono Ryuk, Nova AI Core, Ollama, Store, Apps ecosistema.

## Cosa non va qui

- Binary asset (logo, wallpaper) → `assets/`
- Specifica RPM dettagliata del codice sistema → `packages/` quando nasceranno i pacchetti
- Script eseguibili → `scripts/`
