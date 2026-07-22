# 03 — System Services

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire **quali servizi di sistema** sono necessari, opzionali o vietati nella prima build avviabile. Mantenere la superficie minima per stabilità.

Focus: sessione grafica, login, desktop, terminale, impostazioni, power management.

---

## 2. Componenti coinvolti

### 2.1 Obbligatori M0.1

| Servizio / stack | Funzione |
|------------------|----------|
| `systemd` | Init e dependency graph |
| `NetworkManager` (o equivalente) | Rete base (utile per update/debug) |
| `SDDM` | Display manager |
| Stack Plasma/Nova Shell iniziale | Sessione utente |
| `pipewire` / audio stack Fedora default | Audio non critico ma tipicamente presente |
| Polkit + logind | Permessi sessione, power |
| UDisks2 | Mount dispositivi base |

### 2.2 Consigliati

| Servizio | Funzione |
|----------|----------|
| `sshd` | Solo immagini **dev** (disabilitato su ISO “clean” se non serve) |
| `chronyd` | Tempo corretto |
| Firewall default Fedora | Baseline |

### 2.3 Esplicitamente esclusi M0.1

| Servizio futuro | Motivo esclusione |
|-----------------|-------------------|
| `nova-ryuk` | Fuori scope |
| `nova-ai-core` | Fuori scope |
| Ollama come servizio di sistema | Fuori scope |
| Nova Cloud sync | Fuori scope |
| Store daemon | Fuori scope |
| Intent/Permissions Nova Platform completi | Prematuri |

---

## 3. Flusso operativo

### Abilitazione target

```text
multi-user.target
  → NetworkManager, chronyd, …
graphical.target
  → sddm.service
       → user session (Nova Shell)
            → user units tipici Plasma (non Ryuk)
```

### Power

```text
UI Spegnimento/Riavvio → logind (via sessione) → systemd poweroff/reboot
```

Niente orchestrazione Ryuk.

---

## 4. Dipendenze

| Area | Dipende da |
|------|------------|
| SDDM | DRM/GPU, PAM, account utente |
| Sessione | dbus utente, compositor |
| Settings / Terminal | pacchetti desktop standard |
| Build | lista pacchetti in image description |

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| Troppi servizi abilitati | Boot lento / instabilità | Allowlist esplicita |
| sshd esposto su ISO | Rischio sicurezza | Solo profilo `dev`; password forte o chiave |
| User units Plasma che pullano telemetria | Rumore | Disabilitare dove possibile |
| Conflitto autostart futuri Nova | Confusione | Directory autostart Nova vuota in M0.1 |
| SELinux denials | Feature rotte | Test in enforcing; raccogliere AVC |

---

## 6. Strategia di implementazione

1. Partire dal set servizi Fedora KDE Spin.  
2. Documentare delta: cosa togliamo / cosa aggiungiamo.  
3. Creare profilo `novaos-m01` = allowlist.  
4. Verificare `systemctl list-units --failed` dopo ogni boot di test.  
5. Introdurre unità `nova-*.service` **solo** quando serve branding/helpers banali (es. set hostname) — non AI.

### Helper ammessi (opzionali, banali)

- `nova-os-release` (file statici, non demone)
- script one-shot di first-boot **minimo** (crea utente live se live ISO) senza cloud

---

## 7. Riferimenti

- `02-Boot-Flow.md`, `05-Installer.md`, `10-Milestone-0.1.md`  
- Platform lunga: `../platform/06-Nova-Services.md` (non implementare ora)
