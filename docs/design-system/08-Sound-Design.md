# 08 — Sound Design

**NovaOS Design System — Identità sonora**  
**Sprint:** 2 — Identità visiva / sensoriale  
**Stato:** Specifica ufficiale (pre-asset audio)

---

## 1. Scopo

Definire la personalità sonora di NovaOS: quando suona, cosa suona, quanto è discreto. Nessun file audio in questo sprint — solo brief e regole.

---

## 2. Filosofia sonora

1. **Silenzio come default di lusso** — molti eventi restano muti.  
2. **Suono = conferma o allerta**, non decorazione continua.  
3. **Timbrica unica** — non Windows ding, non macOS boop, non notification stock Android.  
4. **AI ha una firma sonora minima**, riconoscibile ma non “vocaloid”.  
5. **Accessibilità** — sempre spegnibile; mai unico canale di informazione critica.

### Motivazione

L’eleganza passa anche dal non assillare. La velocità si sente nel feedback aptico/visivo prima che in jingle lunghi. L’affidabilità richiede allerte chiare, non melodie.

---

## 3. Identità timbrica (“Nova Tone”)

| Parametro | Direzione |
|-----------|-----------|
| Base | Tono sintetico caldo-cristallino (sine/triangle soft), non orchestra |
| Armonia | Intervalli aperti (5ª/ottava), niente tritoni “error game” |
| Coda | Decay breve 120–350ms |
| Spazio | Reverb cortissimo o null; niente cattedrale |
| AI signature | Armonico superiore leggero verso timbro “glass”, allineato al cyan percettivo |

**Vietato:** chiptune loop, voice assistant parlante di default, hit cinematici lunghi, remix di brand altrui.

---

## 4. Catalogo eventi

| ID | Evento | Comportamento | Durata max |
|----|--------|---------------|------------|
| `snd.boot` | Fine boot / ready | Chime ascendente a 2 note soft | 600ms |
| `snd.login.ok` | Login riuscito | Conferma breve 1 nota | 200ms |
| `snd.login.fail` | Login fallito | Low tick; non aggressivo | 180ms |
| `snd.notify` | Notifica generica | Tick alto soft | 150ms |
| `snd.notify.ai` | Notifica NovaAI | Tick + armonico signal | 180ms |
| `snd.critical` | Allerta sicurezza | Doppia nota bassa | 300ms |
| `snd.success` | Operazione completata (rara) | 2 note rapide | 220ms |
| `snd.device.in` | Device connected | Up soft | 160ms |
| `snd.device.out` | Device removed | Down soft | 160ms |
| `snd.volume` | Feedback volume | Click scalato | 40ms |
| `snd.capture` | Screenshot | Shutter soft non-camera-phone | 120ms |

Eventi **muti di default:** hover, apertura menu, switch focus finestra, typing, Pulse breath (solo visual).

---

## 5. Policy di volume e preferenze

| Preferenza | Default proposto |
|------------|------------------|
| Suoni di sistema | On, volume 40% |
| Suono boot | Off su laptop; On opzionale su desktop/HT |
| Suoni notifica | On |
| Suoni AI | On ma distinti e rari |
| Non disturbare | Muta tutto tranne critical |

Rispetto di focus/silent mode dal Control Center.

---

## 6. Spazializzazione e canali

- Mono o stereo stretti; no surround obbligatorio.
- Output su device di default; non “rubare” exclusive mode alle app media.
- Latency bassa prioritaria sul volume.

---

## 7. Voce

- **Nessuna voce parlante di sistema di default.**  
- NovaAI può usare TTS solo se l’utente lo abilita e per contenuti richiesti.
- Vietato: frasi di boot parlante.

---

## 8. Consegna futura in `branding/sounds/`

Naming file allineato agli ID (`snd.notify.wav`, ecc.), 48kHz, loudness normalizzata (target circa -16 LUFS short, da calibrare), silenzio di coda minimo.

---

## 9. Motivazione delle scelte restrittive

Meno suoni → più significato quando appaiono. Una firma a 2 note vale più di una library rumorosa. La distinzione `notify` vs `notify.ai` rafforza l’AI come capacità di sistema senza teatralità.
