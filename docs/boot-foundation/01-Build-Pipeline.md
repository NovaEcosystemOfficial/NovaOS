# 01 — Build Pipeline

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Stato:** Specifica operativa (pre-implementazione codice di build)  
**Milestone target:** 0.1

---

## 1. Obiettivi

Definire la **pipeline di build** che produce artefatti riproducibili di NovaOS fino alla prima ISO installabile/avviabile sul PC di sviluppo.

Per Milestone 0.1 la pipeline deve:

- partire dalla base Fedora (ADR-001);
- applicare overlay di branding e sessione **Nova Shell iniziale**;
- produrre un’immagine avviabile (live e/o installer);
- essere eseguibile in ambiente di sviluppo documentato (`08-Development-Environment.md`);
- **non** includere Ryuk, Nova AI, Nova Cloud, Store, Apps ecosistema.

---

## 2. Componenti coinvolti

| Componente | Ruolo in pipeline |
|------------|-------------------|
| **Host di build** | Fedora (consigliato) o container di build |
| **KIWI NG** | Tool primario di image build (ADR-003) |
| **livemedia-creator** | Alternativa/spike se KIWI blocca (ADR-003) |
| **DNF / repo Fedora** | Risoluzione pacchetti (ADR-004) |
| **Overlay Nova** | File di branding, SDDM theme, defaults Shell |
| **CI (futura)** | `.github/workflows` — smoke build (post-M0.1 early) |
| **Artifact store** | Directory locale `artifacts/` (gitignored) |

### Overlay Nova (concettuale)

```text
nova-overlay/
  branding/          # logo, wallpaper, splash
  sddm-theme-nova/   # greeter
  nova-shell-defaults/  # layout Horizon-like iniziale / plasma look-and-feel
  configs/           # hostname, os-release, session name
  packages/          # lista pacchetti M0.1
```

---

## 3. Flusso operativo

```text
1. Sync fonti (repo docs + overlay + image description)
2. Resolve pacchetti da mirror Fedora
3. KIWI: prepare → create root → apply overlay → package image
4. Output: ISO (e opzionale qcow2 per test VM)
5. Verifica checksum + smoke test boot (09-Testing-Strategy)
6. Tag milestone locale: novaos-0.1.0-dev
```

### Pipeline stages (logici)

| Stage | Input | Output | Criterio di successo |
|-------|-------|--------|----------------------|
| **prepare** | image description YAML/XML | config validata | kiwi dry-run OK |
| **bootstrap** | repo Fedora | rootfs base | chroot funziona |
| **customize** | overlay Nova | rootfs branded | os-release NovaOS, tema SDDM presente |
| **image** | rootfs | ISO/qcow | file generato, size ragionevole |
| **verify** | ISO | report test | boot VM o HW smoke OK |

---

## 4. Dipendenze

| Dipendenza | Nota |
|------------|------|
| ADR-001 Fedora | Base pacchetti |
| ADR-003 KIWI NG | Build system |
| ADR-004 DNF | Packaging |
| Rete verso mirror | Build online nella prima fase |
| Spazio disco | ≥ 40–80 GB liberi consigliati sul host di build |
| KVM/QEMU o HW | Per validare boot |

**Non dipendenze M0.1:** Nova AI Core, Ryuk, SDK, app ecosistema.

---

## 5. Possibili criticità

| Criticità | Impatto | Mitigazione |
|-----------|---------|-------------|
| KIWI + target Fedora poco familiare al team | Ritardo | Spike time-boxed + fallback livemedia-creator |
| Mirror lenti / mirror break | Build fallisce | Mirror locali, cache DNF |
| Overlay Plasma fragile tra versioni | Look “rotto” | Pin versione Fedora; set minimo di file defaults |
| ISO troppo grande | Distribuzione lenta | Trim pacchetti; niente debug bloat in M0.1 |
| Non riproducibilità | “Funziona solo sulla mia macchina” | Documentare host, hash pacchetti, script unico entrypoint |
| Scope creep (AI/Ryuk) | Derail milestone | Freeze scope in `10-Milestone-0.1.md` |

---

## 6. Strategia di implementazione

### Fase A — Skeleton (settimana 1 operativa)

1. Creare image description minima Fedora KDE.  
2. Build ISO vanilla (senza branding) → prova boot.  
3. Congelare versione Fedora target (es. N).

### Fase B — Branding overlay

1. `os-release` / pretty name NovaOS.  
2. Logo splash + SDDM theme.  
3. Defaults Nova Shell iniziale (layout ridotto).

### Fase C — Hardening pipeline

1. Script `scripts/build-iso.sh` (entrypoint unico — da scrivere in fase codice).  
2. Checksum + naming artefatti.  
3. Checklist smoke test obbligatoria prima di dichiarare verde.

### Fase D — CI light (opzionale M0.1, consigliata subito dopo)

- Job che valida sintassi image description e presenza overlay.  
- Build full può restare manuale sul PC di sviluppo finché non c’è runner adeguato.

### Principio

> **Prima verde e banale, poi bella.**  
> Una ISO che bootta senza branding batte una ISO perfetta che non parte.

---

## 7. Roadmap tecnica verso la prima ISO (sintesi)

Vedi anche `10-Milestone-0.1.md` e `06-ISO-Build.md`.

```text
Env ready → Vanilla Fedora ISO boot → Overlay branding → SDDM Nova
  → Nova Shell defaults → Terminal/Settings verify → Shutdown/Reboot
  → Tag M0.1
```

---

## 8. Riferimenti

- ADR-001, ADR-003, ADR-004  
- `06-ISO-Build.md`, `08-Development-Environment.md`, `10-Milestone-0.1.md`
