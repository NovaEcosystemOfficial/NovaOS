# 06 — Animations

**NovaOS Design System — Motion**  
**Sprint:** 2 — Identità visiva  
**Stato:** Specifica ufficiale

---

## 1. Scopo

Definire il linguaggio di movimento di NovaOS / Nova Shell: durata, easing, quali elementi si animano, e cosa è vietato. La motion comunica **velocità** ed **eleganza**, non spettacolo.

---

## 2. Filosofia del motion

1. **Corto, decisivo, reversibile.**  
2. **La fisica è allusione, non simulazione** — niente bounce da icon pack.  
3. **Feedback immediato > intro lunghe.**  
4. **AI pulse è respirazione, non discoteca.**  
5. **`prefers-reduced-motion` è di prima classe.**

### Motivazione

Un OS lento percepito è un OS non affidabile. Animazioni lunghe stile “cinematic desktop” tradiscono la promessa di velocità. Allo stesso tempo, zero motion rende l’UI piatta e poco leggibile nei cambi di stato.

---

## 3. Token di durata

| Token | ms | Uso |
|-------|-----|-----|
| `motion.instant` | 0–80 | Press feedback, toggle |
| `motion.fast` | 120 | Hover, focus ring |
| `motion.normal` | 180 | Panels, menu |
| `motion.emphasis` | 240 | Launcher open/close |
| `motion.slow` | 320 | Theme crossfade, workspace |
| `motion.ritual` | 480–800 | Solo boot/onboarding hero |

Oltre 800ms: **vietato** in UI quotidiana.

---

## 4. Easing

| Token | Curva | Uso |
|-------|-------|-----|
| `ease.standard` | cubic-bezier(0.2, 0.0, 0.0, 1.0) | Default decelerate |
| `ease.exit` | cubic-bezier(0.4, 0.0, 1.0, 1.0) | Chiusure |
| `ease.emphasized` | cubic-bezier(0.2, 0.0, 0.0, 1.2) *clamp* | Solo se senza overshoot visibile; preferire 0.2,0,0,1 |
| `ease.linear` | linear | Progress deterministici |

**Vietato:** bounce, elastic, spring esagerati su finestre e menu.

---

## 5. Motivi ammessi (catalogo)

### 5.1 Fade + slight rise

Opacity 0→1, translateY 4–8px. Menu, tooltip, toast.

### 5.2 Scale from origin

Launcher e Control Center: scale 0.96→1 + fade, transform-origin verso Nova Core / Quick.

### 5.3 Sheet slide

Notification Center: translateX 12px→0 + fade (non full swipe da off-screen se riduce snappiness; max 24px).

### 5.4 Focus strip

Apertura app: capsule appare con fade; riordino con swap soft 180ms.

### 5.5 Window map/unmap

160–200ms opacity + scale 0.98; compatibile con compositor.

### 5.6 AI Pulse

Alone `signal` con opacità 0.35↔0.7 periodo ~2.4s, easing sine; **una** sola aureola. Mai RGB cycle.

### 5.7 Stato successo

Check draw 180ms o fade colore success — no confetti.

---

## 6. Motivi vietati

- Parallax wallpaper continuo.
- Genie/minimize verso dock stile macOS.
- Flip 3D finestre.
- Particle field permanente.
- Shake aggressivo errori (max micro-shake 2px × 2 se proprio utile).
- Skeleton shimmer rumoroso su tutta la shell.

---

## 7. Reduced motion

Se `prefers-reduced-motion: reduce`:

- Solo fade ≤ 120ms o cut.
- Pulse AI → static dot.
- Boot: crossfade minimo, no timeline lunga.

---

## 8. Performance

- Preferire opacity/transform.
- Evitare animare blur radius in loop.
- Disabilitare motion non essenziali su low-power mode.

---

## 9. Allineamento alle promesse di brand

| Promessa | Come la motion la sostiene |
|----------|----------------------------|
| Velocità | ≤ 240ms azioni comuni |
| Eleganza | Easing decelerati, pochi pixel di travel |
| AI | Pulse lento e ciano, non strobo |
| Affidabilità | Transizioni prevedibili, stesso pattern ovunque |
