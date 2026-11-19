# Timing cheatsheet (30 fps)

| Item | Frames | Seconds |
|---|---|---|
| Mouth shape hold while talking | 5 (4–6) | 0.17 |
| Mouth closes on pause | ≥10 f silence | 0.33 |
| Blink (full) | 7–8 | 0.25 |
| Blink interval | 60–120 | 2–4 |
| Talk sway/head tween | 13 | 0.43 |
| Talk sway repeat | ~50 | 1.7 |
| Gesture raise / hold / lower | 6–10 / 15–40 / 8–12 | |
| Walk step / cycle | 16 / 32 | 0.53 / 1.07 |
| Parrot flap cycle | 8–10 | 0.3 |
| Faint rotation | ~75 | 2.5 |
| Dip to black (out + black + in) | 15 + 1 + 15 | 1.03 |
| Ghost disappear | ~90 | 3 |
| Ghost appear | 30–45 | 1–1.5 |
| Tint transform slow / fast | ~180 / ~30 | 6 / 1 |
| Calendar date step | ~15 | 0.5 |
| Establishing wide | 90–150 | 3–5 |
| Dialogue CU (one line) | 120–240 | 4–8 |
| Reaction cutaway | 45–90 | 1.5–3 |
| Prop insert | 60–120 | 2–4 |
| Camera push-in on held shot | whole shot, 5–15% scale | |

Frame math: `frame = round(seconds × 30) + 1` (Animate frames are 1-based).
