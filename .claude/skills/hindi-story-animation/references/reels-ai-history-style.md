# Instagram Reels — AI-video history style (measured from 3 user samples)

Samples: Napoleon (101 s, 35 shots), Burkina Faso (97 s, 37 shots), Herero (83 s, 33 shots).

## Format
- 9:16. Samples were 720×1280; export **1080×1920, 30 fps**, H.264, AAC, mix ≈ −14 LUFS for phones.
- Shot length median **2.5–2.9 s**, max ~6 s. One caption line = one shot.
- Instagram UI covers bottom ~20 % and top ~12 %: keep captions between 55–75 % of frame height.
- Separate 1080×1920 cover frame (title readable in the 3:4 grid crop).

## Story structure (identical in all three)
1. Hook (0–3 s): blurred pull-focus image → strongest shot + shock line ("This emperor terrified Europe for 11 years").
2. Black card cliffhanger completing the hook ("…then died alone").
3. Date line: "It's 1804."
4. Rise: one fact per shot (≈8–10 shots).
5. Black card at the turning point ("Europe belongs to him").
6. Conflict / fall (≈10–12 shots).
7. Ending repeats the hook line → seamless loop (Reels replays count).

## Visuals
- Painterly cinematic cartoon (Disney/Pixar concept art × Arcane): dark teal night palette, orange fire key light, smoke, embers, volumetric light.
- Low angles, extreme face close-ups, crowds and silhouettes, maps and documents as inserts.
- One hero with a fixed look in every shot (hat / beret / uniform) → keep a character reference image and reuse it.
- **Real motion inside each shot** (image-to-video AI: Kling / Runway / Veo / Hailuo): characters run, charge, lift papers; smoke drifts; strong camera push-in. Not puppet animation.

## Captions
- Bold rounded sans (e.g. "Luckiest Guy"/"Bangers"-like), white, ALL CAPS, dark drop shadow, centred, 2 lines max, appears in sync with the voice.
- Black cards: same font, larger, centred on pure black.

## Audio
- Very deep male documentary narrator (F0 ≈ 75–95 Hz), slow, dramatic pauses.
- Dark cinematic bed + bass hits on cuts, whooshes, fire/explosion SFX. Samples measured −19 to −20 LUFS.

## Pipeline
script.md (one row per shot: caption · image prompt · motion prompt) → character reference image → still per shot (image model, reference-locked) → image-to-video 5 s per shot → trim to the caption's VO length → captions + black cards + grade + music/SFX → 1080×1920 MP4 + cover.

## Cautions
- Real tragedies: verify every fact against reliable sources before production.
- Label AI content on Instagram ("AI info"). Vary topics to avoid mass-produced/inauthentic-content flags.
