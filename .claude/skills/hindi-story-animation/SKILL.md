---
name: hindi-story-animation
description: Build 2D Hindi moral/folk story animation scenes (village, palace, forest, sage, king, parrot, magic stories) from a video script, using the user's Adobe Animate (.fla/XFL) character rigs and backgrounds. Use whenever the user gives a script, scene list, shot list, FLA character or BG files, or asks to animate, stage, time, lip-sync, block or edit a scene in this "Hindi kahani" cartoon style. Encodes timing rules measured frame-by-frame from 24 reference clips (30 fps puppet/symbol animation).
---

# Hindi Story 2D Animation: Scene Building Skill

This style is **cut-out (symbol/puppet) animation in Adobe Animate**: flat vector characters with
thick dark outlines and one cel-shadow tone, painted (semi-realistic, soft-shaded) backgrounds,
**30 fps, animated on 1s** with classic/motion tweens, and lots of held poses where only eyes, mouth
and a slow camera move. Every number below was measured from the reference clips; see
`references/clip-analysis.md` for the per-clip evidence and `references/timing-cheatsheet.md`
for a compact frame table.

Use the user's own characters and backgrounds. Treat the reference clips only as a guide to
technique and timing. Do not recreate their characters, branding or watermark ("Jeevan Toons").

## 1. Project settings (always)

| Setting | Value |
|---|---|
| Stage | 1920×1080 (reference renders were 640×360, 16:9) |
| FPS | **30** |
| Animation | On 1s (tweens), except mouth swaps (5-frame holds) and blinks (frame-by-frame symbol) |
| Easing | Ease in-out on every body/camera tween (body sway area curve rose then fell symmetrically) |
| Audio | Hindi dialogue VO + light BGM; dialogue drives shot length |

## 2. Workflow: script → scenes

1. **Break the script into beats.** Each line of dialogue or action becomes one beat. Mark the speaker, listener, location, time of day, props and any magic or transition.
2. **Group beats into scenes by location.** Each location gets one BG FLA/symbol. Close-ups reuse the *same* BG, scaled up and re-positioned, rather than separate art (seen in every interior: the CU wall is the wide BG cropped).
3. **Write a shot list** with the grammar in §4. Fill the template in `references/shot-list-template.md`.
4. **Time each shot from audio.** Shot length = line length + 10–20 frames head/tail. Keep reaction cutaways at 1.5–3 s.
5. **Build in Animate** (see §8): BG layers → characters → FG layers → camera → mouth/eye passes → transitions.
6. **Polish pass:** blinks every 2–4 s, body-sway loop on speakers, eyelines toward partner, camera drift on every held shot.

## 3. Character rig requirements (check every FLA the user supplies)

Each character should be a graphic/movie-clip symbol with these **separate nested parts**. If a part is
missing, tell the user before animating.

- **Head group**: head base, **eyes symbol** (frames: open, half, closed, plus directional pupils L/R/C and a worried/angry brow variant), **mouth symbol** (≥5 frames: closed/neutral, small open, wide open, rounded "O", teeth-visible; plus a closed smile and a closed frown), brows (separate for angled-brow acting), moustache/beard *over* the mouth layer, hair/turban/crown, earrings (women: big gold earrings, bindi, hair bun).
- **Torso** with neck pivot; scarf/dupatta/sash as a separate overlapping layer.
- **Arms**: upper arm → forearm → hand, each with its own pivot (shoulder, elbow, wrist). **Hand symbol frames**: relaxed, open palm up, point (index), fist/grip, hand-on-chest, holding prop.
- **Legs** (full-body chars): thigh → shin → foot, dhoti/pyjama/sari panel as overlay.
- **Head-turn views**: front, 3/4 left, 3/4 right (swap on the head symbol, hidden inside a short tween).
- Pre-built poses as symbol frames: stand, sit (bed/chair), cross-legged, lying (prone), carried.

Bird (parrot) rig: body, head, **beak upper/lower** (talking), eye with blink, wing L/R (fold / raise /
gesture / 3–4 flap poses), tail, feet (perch grip).

## 4. Shot grammar (how stories are cut)

The measured pattern for a dialogue scene (clip 07: 2.7 s wide → 7.6 s CU A → 6.9 s CU B → 8.7 s two-shot → CU A):

1. **Establishing exterior wide** (3–5 s), often with a character walking toward the door.
2. **Interior wide/two-shot** (2.5–5 s): full bodies, both characters on the floor line. Speaker on one side, listener on the other.
3. **Shot / reverse-shot close-ups** (MCU, chest up), 4–8 s each = one line each. The speaker faces toward the listener's screen side. The same BG is scaled 2–2.5× behind them.
4. **Return to the two-shot** for gestures, arguments and entrances/exits.
5. **Reaction cutaway** (1.5–3 s) on the listener: closed mouth, blink, brow change.
6. Leave the scene with a **dip to black** (location or time change) or a **hard cut** (same location, new angle).

Rules:
- **180° rule**: a character keeps the same screen side across all shots in a scene.
- **Eyeline**: pupils toward the partner's screen side, always. Even crowd members look toward the throne or speaker.
- Speaker = mouth loop + sway + gestures. Listener = only blinks, rare small head tilt, closed mouth.
- Masked/beard-covered speakers act through **brows, eye narrowing, head tilt and arm beats** (clip 24).
- Groups: shallow line, inward-facing, slight overlap, main speaker at center or nearest camera (clip 23).
- Court/crowd: symmetrical arrays either side of a central aisle, repeated extras, king centered on the throne (clip 16, 23).

## 5. Animation timing rules (30 fps, measured)

| Action | Timing | How |
|---|---|---|
| **Lip-sync** | Mouth frame changes **every 5 frames** (≈6/s). Occasional 4 or 6. | Random cycle of mouth frames for the duration of each spoken phrase. Close the mouth on pauses ≥10 frames. Not phoneme-exact. Use a stronger open shape on stressed words. |
| **Blink** | **7–8 frames**: open → ¼ lid (1f) → ½ lid (1f) → closed (3f) → ½ (1f) → open | Eye symbol frame swap. Every 2–4 s. Add a blink at the start of any head turn and at emotional beats. Listener blinks more. |
| **Talking body sway / head turn** | **13-frame** ease-in-out tween, repeating about every **50 frames (1.7 s)** while speaking | Small rotation/translate of head+torso (2–4°). Head view swap hidden mid-tween. |
| **Hand gesture** | Raise 6–10 f → hold accent 15–40 f → lower 8–12 f | Rotate shoulder/elbow/wrist separately, swap the hand frame at the peak (point, open palm, hand-on-chest). Overlap: forearm leads 1–2 f behind upper arm. |
| **Idle/silent hold** | Body completely still, blinks only, plus **camera push-in** | Optional breathing: torso scale Y +1% over 45 f and back. Keep it subtle (reference breathing was barely visible). |
| **Full-body walk** (wide) | **≈32-frame cycle (16 f per step)**, slow, small stride | Walk-cycle graphic symbol looped. Translate the whole symbol across a static BG. Ground-line Y stays constant. Feet plant for ~4 f. |
| **Waist-up walk** (MS travel) | Same cycle. **Character fixed in frame, BG layers scroll** past | Arm swing + 1–2% vertical bob each step. Parallax: FG bushes fast, trees medium, sky/hills slow or still. |
| **Paired walk** | Both on the same cycle, offset 4–8 frames | Inner character slightly behind. |
| **Faint/collapse** | Talk → eyes half-close + expression drop (≈20 f) → **whole-body rotation pivoted at the feet, ~75 f (2.5 s), ease-in** onto bed/floor | Then cut to the lying pose symbol. Optionally tilt the camera. |
| **Carry** | One combined "carrier+carried" pose symbol | Carried character limp: head tilted back, eyes closed. BG pans behind (tracking). FG tree passes in front. |
| **Sit / stand** | Use pose symbols matched to the furniture contact point (hips on bed edge, chair seat) | No in-between needed. Cut on the action or hold through a reframe. |
| **Parrot talk** | Beak open/close every 4–6 f. Wing gesture raise ~8 f, hold, lower | Perched body still, tail overlaps rock. Blink like humans. |
| **Parrot flight** | Flap cycle ≈ 8–10 f (3–4 wing poses) | Bird near frame center, BG tracks past (clip 13, 17). |

## 6. Camera

- **Every held shot drifts**: slow ease-in-out push-in, about 5–15% scale over the shot (3–8 s). Use a pan instead when two characters are framed. Pure static frames are rare.
- **Reframes** inside one shot: wide → medium over 1.5–3 s (clip 17, 0–6 s).
- **Tracking/parallax**: walking, carrying and flying shots keep the subject centered and scroll BG layers at different speeds (FG ≈ 1.5×, MG 1×, BG 0.3×, sky 0).
- **Lateral reveal** of crowds/lineups: slow horizontal pan across a row of faces (clip 17, 22, 23).
- Implement with an Animate **Camera layer** or a parent "WORLD" symbol that you scale/translate. Keep the camera tween ease at ≥50.

## 7. Transitions and effects (measured)

| Effect | Frames | Implementation |
|---|---|---|
| **Dip to black** (location/time change) | **15 f fade-out (linear) → 1 f black → 15 f fade-in** (≈1 s total) | Black solid layer on top, alpha 0→100→0. Both shots keep moving during the fade. |
| Hard cut | 0 | Same location, new angle. Cut on a gesture or at the end of a line. |
| Ghost **disappear** | Alpha 100→0 over ~90 f (3 s), BG held | Color Effect → Alpha on the character symbol. |
| Ghost/figure **appear** | Alpha 0→100 over ~30–45 f, often with a light glow | Translucent figure resolves beside the reacting villager. |
| **Material change** (stone→gold, silver blade→gold) | Slow version: tint ramps 0→100% over ~180 f. Fast version: ~30 f | Color Effect → Tint (gold #F5D90A to #FFE600) keyframes. Add a sparkle symbol loop on the magic object. |
| Magic gem | Sparkle/twinkle loop, 2–3 f per sparkle frame | Separate sparkle layer above the gem. Gem rotates slowly when moving. |
| **Calendar time-passage** | Full-screen calendar graphic. Highlight pill **grows one date every ~15 f** across 2–4 dates (1.5–2.5 s) | Insert after a dip to black or between travel shots. Then cut to the new location. |
| Prop **insert close-up** | 2–4 s | Hand + prop at large scale (thumbprint on a document, coins, gem in hand). Match prop scale/colour to the wide. |
| Night | Same BG with a dark blue multiply overlay at 40–60% opacity, darker characters (Brightness −30%) | Reuse day BGs. |

## 8. Building scenes in Adobe Animate (the user's FLA files)

- `.fla` (CS5.5+) is a **ZIP of an XFL project**: `DOMDocument.xml` (main timeline, scenes, layers, frames, tweens), `LIBRARY/*.xml` (symbols), `bin/` (bitmaps). When given FLA files:
  1. Copy the archive and unzip it into its own folder. Never edit the original.
  2. Inventory the library: list symbols, their nested parts, frame labels (mouth/eye/hand frames) and registration points. Report missing rig parts (§3) to the user.
  3. Write the scene either as **JSFL** (preferred: the user runs it via *Commands → Run Command* and Animate does the tweening safely), or by editing XFL XML directly and re-zipping (`zip -r -X out.fla mimetype ...`, with `mimetype` first and uncompressed when present).
- Scene construction order with JSFL:
  1. `fl.getDocumentDOM()`: set `frameRate=30`, `width/height`, then add a scene per location/sequence (`dom.addNewScene("SC03_House_Night")`).
  2. Layers, top to bottom: `CAMERA` · `FX_fade` · `FG` (pots, plants, door frames) · `CHAR_front` · `CHAR_back` · `MG_props` · `BG` (+ `BG_sky` for parallax).
  3. Place BG and character instances (`library.addItemToDocument`). Set the floor line and scale (wide: characters ≈ 55–65% of frame height. MCU: head+chest fills ≈ 70%).
  4. Add keyframes from the shot list, then `createMotionTween()` or classic tweens with ease.
  5. Mouth pass: inside the character's graphic instance, set `firstFrame` / loop "single frame" on the mouth symbol every 5 frames over the dialogue ranges.
  6. Blink pass: eye-symbol frame sequence per §5, every 60–120 frames, staggered between characters.
  7. Transitions: black-solid alpha keyframes per §7.
- Keep **graphic symbols** (not movie clips) for anything that must scrub and export frame-accurately.
- Export: *File → Export Video/Media*, H.264, 1920×1080, 30 fps.

## 9. Visual style checklist (for any new asset the user asks for)

- Characters: thick dark-brown/black outline (≈3 px at 1080p), flat fills with one shadow tone, large almond eyes with lashes for women, moustaches for most men, saturated costumes (pink, green, teal, maroon), gold jewellery. Head:body about 1:6.
- Villagers: kurta + dhoti, gamchha scarf. Women: sari with contrasting border, bindi, bun, bangles. King: crown, gold armour/necklaces, sash. Adviser: turban with a feather. Sage: saffron or white robe, topknot, long beard, rudraksha beads.
- BGs: soft painted shading, warm palettes. Interiors: shelves with steel pots, hanging cloth/bags, lantern, framed deity picture, bed with a pink sheet. Exteriors: thatched/tiled huts, big banyan tree, flowers in the FG corners. Palace: symmetrical throne, red carpet, pillars, curtains.
- The FG layer always contains something (pot, plant, flower, doorframe, spear) for depth.

## 9b. Voice-over

Follow `references/voice-style.md` (measured from the reference audio): narrator plus fixed
character voices, brisk expressive delivery (~4 syllables/s), 0.3–0.6 s gaps between lines,
continuous music bed about 25 dB under the voice, final mix at about −16 LUFS. When the user supplies VO, use it
as-is and drive the lip-sync from its loudness envelope. Never clone a real person's voice.

## 10. Output for each request

When the user gives a script, deliver:
1. A **shot list** (`references/shot-list-template.md` format) with frame ranges at 30 fps.
2. **Dopesheet** per shot: dialogue frame ranges → mouth on/off, blink frames, gesture keys, camera keys.
3. **JSFL script(s)** (or modified XFL) that build the scenes from the user's library.
4. A list of missing assets or rig parts.

Analysis helpers for new reference clips: `scripts/clip_metrics.py <clips...>` (holds, cuts,
exposure histogram) and `scripts/frame_regions.py <clip> <start> <end>` (per-frame changed bounding box,
which isolates mouth vs eye vs body vs camera motion). Run them with `python3 -I`.
