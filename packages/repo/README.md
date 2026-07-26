# Repository ufficiale Nova Update

Layout del repository RPM dedicato agli aggiornamenti incrementali di NovaOS
(Sprint 15). I mirror pubblici punteranno a questa struttura.

```text
packages/repo/
├── README.md
├── conf/                      # file .repo installati in /etc/yum.repos.d/
├── keys/                      # chiavi pubbliche (placeholder in foundation)
└── channels/
    ├── stable/
    │   ├── os/x86_64/
    │   ├── nova/x86_64/
    │   ├── apps/x86_64/
    │   └── repodata/          # generato da createrepo_c
    ├── beta/…
    ├── developer/…
    └── nightly/…
```

## Canali

| Canale | Baseurl tipica (futura) |
|--------|-------------------------|
| stable | `https://updates.novaos.dev/stable/$basearch/` |
| beta | `https://updates.novaos.dev/beta/$basearch/` |
| developer | `https://updates.novaos.dev/developer/$basearch/` |
| nightly | `https://updates.novaos.dev/nightly/$basearch/` |

In sviluppo locale si può servire `packages/repo/channels/<channel>/` via HTTP
file o `baseurl=file:///…`.

## Classi di pacchetto

| Directory | Contenuto |
|-----------|-----------|
| `os/` | Identità OS, kernel overlay Nova, pacchetti sistema |
| `nova/` | Componenti piattaforma (`novaos-update`, branding, shell defaults, …) |
| `apps/` | Applicazioni ecosistema (NovaDocs, …) |

## Metadati

```bash
# Esempio (host con createrepo_c)
createrepo_c packages/repo/channels/stable
```

Gli RPM firmati vanno pubblicati **prima** di aggiornare `repodata/`.
Policy firme: vedi `docs/platform/11-Nova-Update.md`.

## Stato Sprint 15

- Struttura canali e conf `.repo` presenti
- Nessun RPM di produzione pubblicato
- Chiave `keys/novaos-rpm-placeholder.gpg` non è un trust anchor
