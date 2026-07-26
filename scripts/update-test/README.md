# Nova Update — test environment

Ambiente completo per dimostrare aggiornamenti incrementali **senza ricostruire l’ISO**.

## Flusso

```text
bootstrap tools → build hello-nova-update RPM → publish local repo (createrepo_c)
  → install baseline 1.0.0 → publish 1.0.1 → nova-updater check/apply → verify
```

## Comandi

```bash
# Gate completo (consigliato)
make test-update

# Passi manuali
./scripts/update-test/bootstrap-update-test-tools.sh
./scripts/update-test/build-test-package.sh 1.0.0
./scripts/update-test/publish-local-repo.sh stable nova
./scripts/update-test/run-e2e-update-flow.sh
```

## Layout generato

```text
build/work/update-test/
├── host-tools/          # rpmbuild + createrepo_c (user-space)
├── artifacts/           # RPM prodotti
├── repo/channels/stable/# repository file:// + repodata
├── rootfs/              # install root di prova
├── yum.repos.d/         # snippet .repo locale
└── state/               # stato broker
```

## Backend

Il flusso e2e usa il backend **`localrpm`**: legge gli RPM del repo locale e
installa via `rpm2cpio` nel rootfs di test (nessun privilegio `rpm --root`).
