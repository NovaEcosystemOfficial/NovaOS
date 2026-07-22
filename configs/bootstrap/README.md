# `configs/bootstrap/`

Opzioni di bootstrap dell’ambiente di build sull’host di sviluppo.

## Obiettivo

Documentare e (in seguito) parametrizzare:

- pacchetti host richiesti (kiwi, qemu, git, …);
- variabili comuni (`NOVAOS_ROOT`, path `build/`, `iso/`);
- vincoli di versione tool.

## Motivazione

Allineato a `docs/boot-foundation/08-Development-Environment.md`: l’host deve essere riproducibile quanto l’ISO.

## File previsti

| File | Ruolo |
|------|--------|
| `host-packages.txt` | Pacchetti DNF da installare sull’host Fedora |
| `env.sh.example` | Export path e flag |

## Stato Sprint 5

Template iniziali presenti; script di setup in `scripts/`.
