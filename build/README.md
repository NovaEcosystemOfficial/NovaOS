# `build/`

Area di **lavoro della build** di NovaOS: directory operative usate da KIWI NG e dagli script durante la generazione delle immagini.

## Scopo (Sprint 5)

Ospitare cache, rootfs temporanei e metadati di build **senza** versionare artefatti pesanti. Questa cartella è infrastruttura di sviluppo, non il prodotto ISO finale (che vive in `iso/` come output dichiarato).

## Motivazione

Separare:

| Path | Ruolo |
|------|--------|
| `build/` | Workspace sporco / intermedio |
| `iso/` | Output pubblicabile (ISO, checksum) |
| `configs/` | Ricette versionate |
| `scripts/` | Automazioni entrypoint |

Mantenere ricette e output mescolati rende impossibile CI pulita e `.gitignore` prevedibile.

## Struttura

```text
build/
├── README.md          # questo file
├── cache/             # cache DNF/KIWI (locale, non committare)
├── work/              # tree di lavoro KIWI / chroot temporanei
└── logs/              # log di build per diagnosi
```

## Cosa non va qui

- Codice di Nova Shell, Ryuk, Nova AI
- Asset di branding sorgente (stanno in `assets/` / `branding/`)
- ISO finali (copiare/promuovere in `iso/`)

## Utilizzo previsto

Gli script in `scripts/` punteranno a:

- `build/work` come directory di build KIWI
- `build/cache` come cache pacchetti
- `build/logs` per `*.log` timestampati

## Policy git

`cache/`, `work/`, `logs/` sono **gitignored** a livello contenuto (restano i `.gitkeep` / README di struttura).
