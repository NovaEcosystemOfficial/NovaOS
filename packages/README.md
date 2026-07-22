# `packages/`

Sorgenti e metadati dei **pacchetti Nova** (RPM) destinati alle immagini.

## Scopo (Sprint 5)

Preparare l’alberatura packaging senza ancora implementare Nova Shell, Ryuk o AI.

I primi pacchetti previsti per M0.1 saranno di **branding e identity**, non di piattaforma AI.

## Motivazione

ADR-004 (DNF/RPM): tutto ciò che Nova aggiunge al rootfs dovrebbe arrivare come RPM tracciabile, non come file copiati “a mano” non aggiornabili.

## Struttura

```text
packages/
├── README.md
├── SPECS/              # file .spec (futuri)
├── novaos-branding/    # fonti pacchetto branding
├── novaos-release/     # os-release / identity (futuro)
├── novaos-sddm-theme/  # tema login (futuro)
└── README-PACKAGING.md
```

## Pacchetti M0.1 (pianificati, non implementati ora)

| Pacchetto | Contenuto |
|-----------|-----------|
| `novaos-release` | `/etc/os-release` NovaOS |
| `novaos-branding` | logo, wallpaper refs |
| `novaos-sddm-theme` | greeter |
| `novaos-shell-defaults` | defaults desktop *iniziali* (dopo, non Sprint 5) |

## Esplicitamente non in Sprint 5 / M0.1 early

- `novaos-ryuk`
- `novaos-ai-core`
- App ecosistema

## Stato Sprint 5

Solo documentazione e cartelle riservate.
