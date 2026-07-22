# ADR-005 — Display Manager

| Campo | Valore |
|-------|--------|
| **ID** | ADR-005 |
| **Titolo** | Selezione del Display Manager |
| **Stato** | Proposta |
| **Sprint** | Sprint 1 — Decisioni tecniche |
| **Data** | 2026-07-22 |
| **Dipende da** | ADR-002 (Desktop Environment) |

---

## 1. Problema

Il Display Manager (DM) gestisce login grafico, selezione sessione, avvio del desktop e spesso lo schermo di blocco/greeter. Per NovaOS è una superficie critica di brand (prima impressione post-boot) e di sicurezza (autenticazione locale, eventuale integrazione account NovaCloud in futuro).

La scelta deve essere coerente con il DE e personalizzabile secondo le UI guidelines.

---

## 2. Alternative valutate

### 2.1 SDDM (Simple Desktop Display Manager)

Display manager di riferimento tipico per KDE Plasma, basato su Qt, theming QML, integrazione consolidata con sessioni Plasma.

### 2.2 GDM (GNOME Display Manager)

Display manager di GNOME, basato su stack GNOME, esperienza greeter allineata a GNOME Shell, default su molte workstation GNOME.

---

## 3. Analisi vantaggi / svantaggi

### SDDM

| Vantaggi | Svantaggi |
|----------|-----------|
| Match naturale con KDE Plasma (ADR-002) | Meno “opinionated enterprise” di GDM in alcuni scenari |
| Temi QML: branding Nova sul greeter più diretto | Qualità temi community variabile → serve tema ufficiale Nova |
| Lighter coupling verso un DE non-GNOME | Funzionalità avanzate (account remotely flavored) da progettare |
| Ampio uso su spin KDE Fedora | Wayland/greeter quirks da testare su HW target |
| Coerente con stack Qt del desktop | Team deve governare sicurezza del tema (niente JS/QML non auditato) |

### GDM

| Vantaggi | Svantaggi |
|----------|-----------|
| Greeter moderno e accessibile in contesti GNOME | Theming profondo limitato / non incoraggiato |
| Integrazione account/online a tratti più “GNOME-native” | Accoppiato culturalmente e tecnicamente a GNOME |
| Default noto su Fedora Workstation | Con Plasma diventa stack misto (GTK greeter + Qt desktop) |
| Buona maturità su Wayland in setup GNOME | Branding NovaOS più difficile senza sembrare “GNOME login + altro DE” |

---

## 4. Decisione proposta

**Raccomandazione: adottare SDDM come Display Manager ufficiale di NovaOS.**

In concreto:

1. SDDM come greeter di default sulle immagini desktop.
2. Tema greeter ufficiale Nova (asset in `branding/`, pacchetto dedicato).
3. Sessione di default: Plasma (ADR-002).
4. GDM non supportato ufficialmente nelle edizioni iniziali.

---

## 5. Motivazione tecnica

1. **Coerenza dello stack Experience**  
   Plasma + SDDM riduce frizioni di sessione, theming e dipendenze. GDM+Plasma è possibile ma crea un’esperienza ibrida e un costo di QA ingiustificato.

2. **Brand first**  
   Il login è parte del primo viewport post-boot. SDDM consente un greeter fedelmente Nova senza combattere le policy di theming GNOME.

3. **Sostituzione progressiva**  
   In prospettiva, Nova potrà sostituire il greeter con un componente proprio. SDDM, essendo relativamente focalizzato, è un buon punto di partenza da wrappare rispetto a un GDM più chiuso nel proprio ecosistema.

4. **Sicurezza**  
   La scelta del DM non risolve da sola auth forte: PAM, disk encryption, e future integrazioni NovaCloud restano layer separati. SDDM è adeguato come frontend locale.

---

## 6. Possibili evoluzioni future

| Evoluzione | Descrizione | Quando |
|------------|-------------|--------|
| **Nova Greeter** | Greeter proprietario (anche basato su SDDM o sostitutivo) | Experience Layer maturo |
| **Login NovaCloud** | Opzione account cloud oltre a locale | Con Platform identity |
| **Biometrie / HW keys** | Integrazione PAM | Con HW supportati |
| **Multi-seat / kiosk** | Sessioni specializzate | Edizioni verticali (es. promo/demo) |

---

## 7. Conseguenze

### Positive

- Stack desktop coerente Qt/Plasma/SDDM.
- Maggiore controllo del branding al login.
- Minor numero di componenti GNOME obbligatori nel critical path.

### Negative / rischi

- Bisogna mantenere un tema SDDM di qualità produzione.
- Test Wayland/X11 (se applicabile) sul greeter.

### Mitigazioni

- Un solo tema ufficiale supportato.
- Checklist QA login/logout/lock/switch user ad ogni release.

---

## 8. Riferimenti

- ADR-002
- [`../ui-guidelines.md`](../ui-guidelines.md)

---

## 9. Note di review

_Spazio riservato a obiezioni del team, data di accettazione e firme._
