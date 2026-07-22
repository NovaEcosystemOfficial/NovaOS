# `tools/`

Utility e tool di supporto allo sviluppo NovaOS (non il sistema operativo stesso).

## Scopo (Sprint 5)

Riservare spazio per:

- helper di validazione ricette;
- wrapper versionati di tool esterni;
- piccole utility del team (lint path, tree check).

## Motivazione

Separare `tools/` da `scripts/`:

| Cartella | Natura |
|----------|--------|
| `scripts/` | Pipeline ufficiale (setup, build-iso, run-vm) |
| `tools/` | Utility collaterali, sperimentali o one-off promossi |

## Struttura

```text
tools/
├── README.md
└── lint/            # controlli statici del workspace
```

## Regole

- Niente demoni di sistema Nova.
- Niente dipendenze da Ryuk/AI.
- Se un tool diventa parte della pipeline → migrare/chiamare da `scripts/`.

## Stato Sprint 5

Include un check strutturale minimo del workspace.
