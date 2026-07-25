# `iso/`

Directory di **output** delle immagini ISO (e checksum correlati) generate dalla pipeline.

## Scopo

Destinazione chiara per gli artefatti consegnabili, separata da `build/work`.

## Struttura

```text
iso/
├── README.md
├── NovaOS_0.2.iso          # copia root (gitignored)
├── NovaOS_0.2.iso.sha256
├── releases/               # ISO versionate (gitignored content)
└── latest/novaos-current.iso
```

## Naming

Da `configs/fedora/release.env` (`NOVAOS_ISO_NAME`):

```text
NovaOS_0.2.iso
```

Alternate documented form: `novaos-<version>-<arch>-live.iso`.

## Build

```bash
sudo make iso
# or full gate:
sudo bash scripts/build-installable-release.sh
```

Requires root, Fedora host, ~80 GB free on a real Linux filesystem.

## Policy git

I file `*.iso` sono ignorati dal `.gitignore`. Non committare ISO.
