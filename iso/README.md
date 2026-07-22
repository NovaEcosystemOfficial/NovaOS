# `iso/`

Directory di **output** delle immagini ISO (e checksum correlati) generate dalla pipeline.

## Scopo (Sprint 5)

Avere una destinazione chiara e professionale per gli artefatti “consegnabili” interni, separata da `build/work`.

## Motivazione

| Path | Contenuto |
|------|-----------|
| `build/` | Intermedi, cache, log |
| `iso/` | ISO + `.sha256` pronti per test VM/USB |

Gli sviluppatori e i tester cercano sempre `iso/` — non devono scavare nei workdir KIWI.

## Struttura

```text
iso/
├── README.md
├── releases/     # ISO versionate (gitignored content)
└── latest/       # opzionale: copia/symlink della candidata corrente (gitignored)
```

## Naming (da `docs/boot-foundation/06-ISO-Build.md`)

```text
novaos-<version>-<arch>-<profile>.iso
es. novaos-0.1.0-x86_64-live.iso
```

## Policy git

I file `*.iso` sono già ignorati dal `.gitignore` root. Non committare ISO.

## Stato Sprint 5

Struttura pronta. Nessuna ISO generata in questo sprint.
