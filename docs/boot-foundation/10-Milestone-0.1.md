# 10 — Milestone 0.1

**NovaOS Boot Foundation**  
**Sprint:** 4 — Prima build avviabile  
**Stato:** Definizione di milestone ufficiale  
**Codename proposto:** `novaos-foundation-boot`

---

## 1. Obiettivi

Congelare lo **scope della Milestone 0.1**: la prima build NovaOS realmente avviabile sul PC di sviluppo.

### In scope (esclusivo)

| # | Capacità | Done when |
|---|----------|-----------|
| 1 | **Boot corretto** | Da firmware a greeter/desktop senza panic |
| 2 | **Logo NovaOS** | Splash e/o greeter mostrano branding Nova |
| 3 | **Schermata di login personalizzata** | SDDM tema Nova |
| 4 | **Desktop Nova Shell iniziale** | Sessione branded (layout/defaults iniziali) |
| 5 | **Apertura del terminale** | App terminale funziona |
| 6 | **Apertura delle impostazioni** | System Settings funziona |
| 7 | **Spegnimento e riavvio** | Da UI di sessione, completano correttamente |

### Esplicitamente fuori scope

- Ryuk  
- Nova AI / Nova AI Core / Ollama  
- Nova Cloud  
- Nova Store  
- Nova Apps (Docs, Studio, Promo, Beauty, Sky, …)  
- Platform bus completo, Skills, SDK runtime  
- rpm-ostree / immutabile  
- Secure Boot production signing completo  
- Multi-arch (solo x86_64)

---

## 2. Componenti coinvolti

| Componente | Livello M0.1 |
|------------|--------------|
| Fedora base | Richiesto |
| KIWI (o fallback) | Richiesto per produrre ISO |
| Plymouth/splash | Logo |
| SDDM + tema Nova | Login |
| Plasma → Nova Shell iniziale | Desktop |
| Konsole (o equiv.) | Terminale |
| System Settings | Impostazioni |
| systemd-logind | Power |

---

## 3. Flusso operativo verso il rilascio interno M0.1

```text
Prep env (08)
  → Pipeline skeleton (01)
  → ISO vanilla boot (06)
  → Branding + SDDM + Shell defaults (02, 04)
  → Services trim (03)
  → Test Tier 0–2 (09)
  → Install opzionale (05)
  → Dichiarazione M0.1 PASS
```

### Definition of Done (DoD)

Una build è **Milestone 0.1** se e solo se:

1. Esiste ISO versionata + SHA256.  
2. Checklist Tier 1 (`09-Testing-Strategy.md`) 100% PASS in VM.  
3. Checklist Tier 2 PASS sul Reference Dev PC.  
4. Nessun servizio Ryuk/AI abilitato.  
5. Note note in `artifacts/.../RELEASE-NOTES-0.1.md` (cosa manca / known issues).  
6. Tag git consigliato: `v0.1.0` o `m0.1` (quando si implementa).

---

## 4. Dipendenze

| Dipendenza | Stato |
|------------|-------|
| ADR-001…005 accettati o comunque operativi | Necessari |
| Design System (logo guidelines) | Necessario per asset minimi |
| Host di build Fedora | Necessario |
| Reference PC dichiarato | Necessario |
| Platform Sprint 3 | **Non bloccante** per M0.1 (guida il futuro) |

---

## 5. Possibili criticità

| Criticità | Rischio | Risposta |
|-----------|---------|----------|
| Tentativo di “aggiungere Ryuk tanto è pronto” | Derail | Rifiuto scope; backlog 0.2+ |
| Perfezionismo Design System | Ritardo | Branding minimo accettabile > pixel perfect |
| HW NVIDIA-only | Boot fail | Escape hatch / iGPU |
| Installer branding infinito | Ritardo | Live boot basta per DoD; install è consigliato |
| Confondere Nova Shell M0.1 con prodotto finale | Aspettative | Comunicare “iniziale / strangler” |

---

## 6. Strategia di implementazione (roadmap tecnica ISO)

### Wave 0 — Enablement

- Setup host (`08`)  
- Vanilla image boot in QEMU  

### Wave 1 — Identity

- `os-release` NovaOS  
- Logo splash  
- SDDM theme  

### Wave 2 — Desktop

- Look-and-feel / layout Nova Shell iniziale  
- Wallpaper  
- Pin terminale + impostazioni  

### Wave 3 — Power & polish minimo

- Verifica shutdown/reboot  
- Rimozione failed units  
- Trim pacchetti evidenti  

### Wave 4 — Gate

- Tier 1 + Tier 2 PASS  
- Tag milestone  
- Retrospettiva → pianificare 0.2 (più branding / installer / stabilità)

### Oltre M0.1 (non ora)

| Milestone futura (indicativa) | Contenuto |
|-------------------------------|-----------|
| 0.2 | Installer branded, più HW, hardening |
| 0.3 | Prima integrazioni Platform services innocue |
| 0.4+ | Nova AI Core / Ryuk dietro feature flag |

---

## 7. Criteri di qualità (non funzionali) M0.1

| Attributo | Target pragmatico |
|-----------|-------------------|
| Tempo a greeter (SSD/VM) | Ordine di grandezza < 60–90s (non vincolo rigoroso) |
| Stabilità | 3 boot di fila OK |
| Superficie | Minima; zero AI |
| Documentazione | Questa cartella + note release |

---

## 8. Comunicazione interna

Messaggio di rilascio interno suggerito:

> NovaOS 0.1 è una **foundation boot**: si avvia, mostra identità Nova, offre un desktop iniziale usabile (terminale/impostazioni/power). Non è ancora l’OS AI-First completo.

---

## 9. Riferimenti

- Tutti i documenti in `docs/boot-foundation/`  
- ADR, Design System, Platform (contesto, non scope)
