# 02 — Color Palette

**NovaOS Design System — Colore**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica token (pre-implementazione)

---

## 1. Scopo

Definire la palette ufficiale di NovaOS / Nova Shell: ruoli semantici, temi chiaro/scuro, stati, AI e regole d’uso. Il colore è un **sistema**, non una raccolta di swatch.

---

## 2. Filosofia del colore

1. **Campo freddo, segnale caldo** — superfici ink/silver; azione primaria “stellar amber”.
2. **Luce = significato** — cyan riservato a intelligenza/sistema; non decorazione.
3. **Un accento dominante per vista** — evitare arcobaleni di CTA.
4. **Temi pari dignità** — chiaro e scuro sono due espressioni dello stesso brand, non un afterthought.
5. **No purple-as-AI** — rifiuto deliberato del cliché viola/indigo da template AI.

### Motivazione

Il contrasto caldo/freddo crea riconoscibilità immediata senza copiare Material blu, Apple grigio-blu o Breeze. L’amber richiama la *nova* (flash); il cyan segnala cognizione/AI.

---

## 3. Nucleo cromatico (Core)

Valori in sRGB esadecimali di riferimento. In implementazione futura andranno convertiti in token OKLCH per percettività uniforme.

### 3.1 Brand core

| Token | Hex | Ruolo |
|-------|-----|-------|
| `nova.ink.950` | `#070B12` | Vuoto profondo, boot, chrome scuro estremo |
| `nova.ink.900` | `#0C121C` | Sfondo dark primario |
| `nova.ink.800` | `#141C2A` | Superficie dark elevata |
| `nova.ink.700` | `#1C2738` | Superficie dark secondaria / well |
| `nova.silver.100` | `#F3F6FA` | Sfondo light primario |
| `nova.silver.200` | `#E7EDF5` | Superficie light secondaria |
| `nova.silver.300` | `#D5DEEA` | Bordi / divider light |
| `nova.steel.500` | `#8B9BB0` | Testo secondario, icone muted |
| `nova.steel.700` | `#3E4B5E` | Testo secondario su light |

### 3.2 Accenti di marca

| Token | Hex | Ruolo |
|-------|-----|-------|
| `nova.stellar.500` | `#E8A54B` | **Primary action** / focus caldo |
| `nova.stellar.400` | `#F0B85F` | Hover primary |
| `nova.stellar.600` | `#C4892F` | Pressed primary |
| `nova.stellar.100` | `#FFF1DC` | Soft wash primary (light) |
| `nova.signal.400` | `#3DD6C6` | AI attiva, indicatori live |
| `nova.signal.500` | `#2BB3A8` | AI default / intelligence |
| `nova.signal.600` | `#1F8F87` | AI pressed / testo su wash |
| `nova.signal.100` | `#D7F7F3` | Wash AI su light |
| `nova.signal.900` | `#0B2E2C` | Wash AI su dark |

### 3.3 Neutri di testo

| Token | Hex | Uso |
|-------|-----|-----|
| `nova.text.primary.dark` | `#E9EEF6` | Body su dark |
| `nova.text.primary.light` | `#121820` | Body su light |
| `nova.text.muted.dark` | `#9AA8BA` | Secondary dark |
| `nova.text.muted.light` | `#5A6B80` | Secondary light |
| `nova.text.inverse` | `#070B12` | Su bottoni stellar |

---

## 4. Semantica di stato

| Token | Hex | Uso |
|-------|-----|-----|
| `nova.state.success` | `#3CB87A` | Completato, sync ok |
| `nova.state.warning` | `#E0A33A` | Attenzione (vicino a stellar ma più “alert”) |
| `nova.state.danger` | `#E2555A` | Errore, distruttivo |
| `nova.state.info` | `#4C8DFF` | Info neutra non-AI (rara) |

**Regola:** `signal` (cyan) ≠ `info` (blu). Cyan = intelligenza Nova; blu info = messaggio tecnico generico.

---

## 5. Materiali: vetro, blur, trasparenza

### 5.1 Nova Glass

Materiale distintivo delle superfici flottanti di Nova Shell (pannelli, launcher, control center).

| Token | Light | Dark | Note |
|-------|-------|------|------|
| `glass.bg` | `rgba(243,246,250,0.72)` | `rgba(12,18,28,0.72)` | Base traslucida |
| `glass.bg.elevated` | `rgba(255,255,255,0.78)` | `rgba(20,28,42,0.78)` | Pannelli sopra il desktop |
| `glass.border` | `rgba(18,24,32,0.08)` | `rgba(233,238,246,0.10)` | Bordo sottile, non hairline nero Windows |
| `glass.highlight` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.06)` | Edge light superiore 1px |

### 5.2 Blur

| Token | Valore | Uso |
|-------|--------|-----|
| `blur.glass` | 24px | Nova Glass standard |
| `blur.glass.strong` | 40px | Control Center / launcher |
| `blur.overlay` | 12px | Scrim dietro dialoghi |
| `blur.none` | 0 | Preferenza reduced transparency |

**Motivazione:** blur sufficiente a legare UI e wallpaper senza “pozzanghera milky” da acrylic generico. Mai stack di ombre multiple + blur estremo.

### 5.3 Overlay / scrim

| Token | Valore |
|-------|--------|
| `scrim.default` | `rgba(7,11,18,0.45)` |
| `scrim.strong` | `rgba(7,11,18,0.62)` |

---

## 6. Tema scuro (Dark) — default di fabbrica proposto

**Motivazione:** l’identità “ink + stellar + signal” è più caratterizzante su campo scuro; il boot e Nova Shell “Luminous Precision” nascono al meglio in dark. L’utente può passare al chiaro.

| Ruolo | Token |
|-------|-------|
| Background app/shell | `nova.ink.900` |
| Surface 1 | `nova.ink.800` |
| Surface 2 | `nova.ink.700` |
| Primary CTA | `nova.stellar.500` |
| AI indicator | `nova.signal.400` |
| Testo | `nova.text.primary.dark` |
| Glass | `glass.*` dark |

Wallpaper di sistema: fondali scuri a bassa frequenza (nebula soft, grain minimo), non foto stock vivaci.

---

## 7. Tema chiaro (Light)

| Ruolo | Token |
|-------|-------|
| Background | `nova.silver.100` |
| Surface 1 | `#FFFFFF` (opaco) / glass elevated |
| Surface 2 | `nova.silver.200` |
| Primary CTA | `nova.stellar.600` (per contrasto WCAG su bianco) |
| AI indicator | `nova.signal.600` su wash `signal.100` |
| Testo | `nova.text.primary.light` |

**Regola:** in light, ridurre trasparenze aggressive su testo piccolo; preferire superfici più opache per leggibilità.

---

## 8. Applicazione per superficie

| Superficie | Note colore |
|------------|-------------|
| Boot | Ink 950 → alone stellar/signal misurato |
| Login / greeter | Glass + mark; CTA stellar |
| Nova Shell chrome | Ink/silver + glass panels |
| Finestra attiva | Bordo `stellar` 1px a opacità bassa **oppure** alone di focus, non glow grosso |
| Notifiche AI | Stripe o dot `signal`, non banner viola |
| Danger | Solo `state.danger` — mai stellar per distruttivo |

---

## 9. Accessibilità

- Testo body: contrasto ≥ **4.5:1** sul fondo usato.
- CTA primary: contrasto ≥ **4.5:1** (usare stellar.600 su light se serve).
- Non veicolare informazione **solo** con il colore (accompagnare icona/testo).
- Modalità daltonismo: verificare stellar vs danger (warm ambigui) — danger resta più rosso saturo; stellar più giallo-ambrato.

---

## 10. Cosa non fare

- Gradient mesh arcobaleno come identità.
- Viola come primary AI.
- Rosso/giallo/verde come chrome finestre.
- Bordi RGB animati.
- Accenti diversi per ogni app ecosistema senza token condivisi.

---

## 11. Consegna futura in `branding/`

Quando si produrranno asset: `tokens.json` / `tokens.css` con i nomi di questo documento, più palette ASE/SVG per il team. Sprint 2 congela **solo** la specifica.
