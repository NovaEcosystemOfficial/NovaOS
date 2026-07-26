# 11 — Nova Update

**Sistema ufficiale di aggiornamento NovaOS**  
**Sprint:** 15 — Nova Update Foundation  
**Stato:** Specifica + fondazione implementata  
**Dipende da:** ADR-004, ADR-006, `system.update.v1`

---

## 1. Scopo

Consentire a NovaOS di ricevere **aggiornamenti incrementali** (sistema, componenti Nova, applicazioni) tramite repository RPM dedicati, **senza** redistribuire una nuova ISO a ogni patch.

Componenti:

| Componente | Ruolo |
|------------|--------|
| **nova-updated** | Demone Update Broker (`system.update.v1`) |
| **nova-updater** | CLI amministrativa / power-user |
| **Repo Nova Update** | Canali RPM firmati |
| **Nova Update (GUI)** | UI futura in Experience Layer (basi in `desktop/nova-update/`) |

---

## 2. Canali di release

| Canale | ID | Destinatari | Cadenza tipica |
|--------|-----|-------------|----------------|
| Stable | `stable` | Utenti finali | Release verificate |
| Beta | `beta` | Early adopter | Pre-release |
| Developer | `developer` | Sviluppatori interni | Feature incomplete OK |
| Nightly | `nightly` | CI / smoke automatici | Build giornaliere |

Mappatura storica: il canale `dev` di ADR-004/API bozza è **rinominato** in `developer`. Alias di compatibilità: `dev` → `developer`.

Un host è su **un solo canale attivo** alla volta. Cambiare canale aggiorna i file `.repo` DNF e richiede `Check()` successivo.

---

## 3. Architettura

```text
┌──────────────┐   ┌──────────────┐   ┌─────────────────┐
│ Nova Update  │   │ nova-updater │   │ Ryuk / Settings │
│     (GUI)    │   │    (CLI)     │   │                 │
└──────┬───────┘   └──────┬───────┘   └────────┬────────┘
       │                  │                    │
       └──────────────────┼────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │  nova-updated   │  Unix socket /run/nova/update.sock
                 │ Update Broker   │  API system.update.v1
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         DNF backend  (futuro)    Signature
         (oggi)       rpm-ostree   gate (GPG)
              │
              ▼
     Repo Nova Update (canale)
     packages/repo/channels/<channel>/
```

Il broker **astrae** il backend: oggi DNF su host mutabile; domani rpm-ostree senza cambiare la semantica di `system.update.v1` (ADR-006).

---

## 4. API `system.update.v1`

| Metodo | Descrizione |
|--------|-------------|
| `Check()` | Interroga i repo del canale; restituisce pacchetti disponibili |
| `Apply()` | Applica aggiornamenti (richiede capability `system.update.apply`) |
| `GetChannel()` / `SetChannel()` | `stable` \| `beta` \| `developer` \| `nightly` |
| `GetProgress()` | Stato idle/checking/applying + percent/message |
| `GetStatus()` | Snapshot: canale, ultimo check, aggiornamenti pending, backend |
| `VerifySignatures()` | Verifica policy firme (foundation; enforce in release pubbliche) |

Eventi (bus futuro): `update.available`, `update.progress`, `update.applied`, `update.failed`.

---

## 5. Tipologie di aggiornamento

| Classe | Esempi | Repo path |
|--------|--------|-----------|
| Sistema | kernel, mesa, novaos-release | `os/` |
| Componenti Nova | nova-updated, branding, shell defaults | `nova/` |
| Applicazioni | NovaDocs, NovaStudio, … | `apps/` |

Tutti transitano dallo stesso broker; i metadata RPM (`Provides`/`Group`) distinguono la classe in UI.

---

## 6. Firme

- Chiavi pubbliche in `/etc/pki/novaos/` (e mirror in `packages/repo/keys/`).
- Policy config: `signature_policy = warn | enforce`.
- Prima delle release pubbliche: `enforce` obbligatorio (ADR-004).
- Foundation Sprint 15: modulo firme + hook pre-Apply; chiavi placeholder, non produzione.

---

## 7. Percorsi runtime

| Path | Uso |
|------|-----|
| `/usr/libexec/nova-updated` | Demone |
| `/usr/bin/nova-updater` | CLI |
| `/etc/nova/update/nova-update.conf` | Config broker |
| `/etc/yum.repos.d/novaos-*.repo` | Repo DNF per canale |
| `/var/lib/nova/update/state.json` | Stato persistente |
| `/run/nova/update.sock` | IPC JSON — `root:nova` mode `0660` (systemd socket activation) |
| `/usr/lib/sysusers.d/nova.conf` | Gruppo di sistema `nova` |
| `/usr/share/nova/update/ui/` | Asset GUI (futuro) |

---

## 8. Sicurezza

- Socket Unix `/run/nova/update.sock`: **SocketUser=root**, **SocketGroup=nova**, **SocketMode=0660**.
- Account interattivi (installer Calamares + post-install) sono membri del gruppo `nova` →
  Nova Center / `nova-updater` parlano col broker **senza sudo**.
- `Apply` resta privilegiato (root nel demone / PolicyKit futuro).
- Capability `system.update.apply` (Settings, Ryuk+confirm).
- Audit su Check/Apply/SetChannel.
- AI può riassumere changelog; **non** può forzare Apply/reboot.

---

## 9. Criteri di uscita Sprint 15

- [x] Specifica ufficiale Nova Update
- [x] `nova-updated` + `nova-updater` funzionanti in modalità mock/dev
- [x] Struttura repository multi-canale
- [x] Predisposizione verifica firme
- [x] Stub GUI Nova Update
- [x] Inclusione automatica nell’immagine (`build-iso.sh` overlay + enable)
- [x] `nova-updater` / `nova-update-gui` nel PATH e voce menu Applications
- [x] Repo `.repo` + chiave GPG in `/etc/pki/novaos/` al build
- [ ] Repo remoto pubblico + chiavi di produzione (post-foundation)

### Integrazione immagine (obbligatoria)

| Meccanismo | File |
|------------|------|
| Overlay rootfs | `scripts/lib/sync-nova-update-overlay.sh` ← `scripts/build-iso.sh` |
| Enable live | `configs/kiwi/novaos-m01/config.sh` |
| Enable installato | `installer/calamares/modules/services-systemd.conf` + `novaos-post-install.sh` |
| Preset systemd | `system/update/systemd/80-novaos-update.preset` |

### Ambiente di test (senza ISO)

```bash
make test-update
```

Costruisce `hello-nova-update` RPM, pubblica un repo `file://` locale con
`createrepo_c`, esegue check → detect → apply → verify (`1.0.0` → `1.0.1`).
Vedi `scripts/update-test/README.md`.

---

## 10. Riferimenti

- ADR-004, ADR-006
- `02-NovaOS.md` — Update Broker
- `09-Security.md` — `system.update.apply`
- Codice: `system/update/`, `shell/nova-updater/`, `desktop/nova-update/`, `packages/repo/`
