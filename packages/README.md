# `packages/`

Sorgenti e metadati dei **pacchetti Nova** (RPM) destinati alle immagini e agli aggiornamenti.

## Motivazione

ADR-004 (DNF/RPM): tutto ciò che Nova aggiunge al rootfs dovrebbe arrivare come RPM tracciabile, non come file copiati “a mano” non aggiornabili.

## Struttura

```text
packages/
├── README.md
├── README-PACKAGING.md
├── SPECS/                 # file .spec
├── repo/                  # repository Nova Update (canali + .repo)
├── novaos-update/         # pacchetto Update Broker (Sprint 15)
├── novaos-branding/       # fonti pacchetto branding
├── novaos-release/        # os-release / identity (futuro)
└── novaos-sddm-theme/     # tema login (futuro)
```

## Pacchetti

| Pacchetto | Stato | Contenuto |
|-----------|-------|-----------|
| `novaos-update` | Fondazione Sprint 15 | `nova-updated`, `nova-updater`, conf, unit, repo files |
| `novaos-release` | Pianificato | `/etc/os-release` NovaOS |
| `novaos-branding` | Pianificato | logo, wallpaper refs |
| `novaos-sddm-theme` | Pianificato | greeter |

## Repository aggiornamenti

Vedi [`repo/README.md`](repo/README.md) — canali `stable` / `beta` / `developer` / `nightly`.

## Test e2e (senza ISO)

Pacchetto di prova [`test/hello-nova-update/`](test/hello-nova-update/) + harness
[`scripts/update-test/`](../scripts/update-test/README.md):

```bash
make test-update
```
