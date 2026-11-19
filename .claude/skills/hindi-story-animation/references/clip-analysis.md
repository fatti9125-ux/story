# Reference clip analysis (frame-by-frame findings)

Source: 24 clips, each 30 s, 640×360, 30 fps, 900 frames (21,600 frames total). Method:
- `clip_metrics.py`: per-frame pixel difference → held-frame %, exposure runs, cuts, luminance.
- `frame_regions.py`: per-frame bounding box of changed pixels → isolates mouth / eyes / body / camera.
- 2 fps contact sheets for every clip, plus full-30 fps strips for blinks, mouths, walks and fades.

Raw numbers: `reference-clip-metrics.json`.

## Global findings

- **Animated on 1s.** Exposure histograms are dominated by 1-frame runs. Movement is smooth tweening, not 2s/3s drawn animation.
- **5-frame holds** are the second most common run length in dialogue clips (04, 05, 06, 08). These are the mouth swaps.
- **Truly identical frames are rare** even in "idle" shots (clip 03: only 12.7% held), because the camera keeps drifting (slow push-ins and reframes).
- Shots with the most change (10 walking 17%, 17 camera 23%, 24 masked 16% of the frame changing) come from BG scrolling and parallax, not character redraws.
- Close-ups reuse the wide BG, scaled up.

## Per clip

| # | Topic | Key measured findings |
|---|---|---|
| 01 | Villager design | Cuts at 2.3/6.3/10.3/15.1/19.1/23.8 s: wide → CU A → CU B pattern. Couples: pink-shirt man + pink-sari woman, green-shirt man (red gamchha) + teal-sari woman, brown-vest young man. Outline, flat fills, one shadow tone. |
| 02 | Royal/sage design | Grey sage (white robe, long layered beard, topknot, tilak), king (crown, gold jewellery, green sash, blue throne), adviser (purple-yellow turban with feather, teal coat, pearl necklace), orange-robed sage (black beard, rudraksha). Parrot + magic gem in the forest wide. |
| 03 | Silent idle | 12.7% held. Body frozen. Blinks plus slow camera push/reframe (2.3–7.9 s reframes from medium to close). Breathing barely visible. Two-shot holds: both silent, eyes toward each other. |
| 04 | Blinks/eyelines | Blink = 7–8 frames (open, ¼, ½, closed ×3, ½, open), measured at 17.43 s. Eye-band changes only. Mouth swaps every 5 f (y192–251 band). **Body/head tween of 13 f repeating every ~1.7 s** (14.07, 15.93, 17.60 s) with ease in-out. Head turns 3/4 → front with an arm reveal. |
| 05 | Male lip-sync | Mouth-change gap histogram: 5 f ×27, 4 f ×10, 6 f ×2, 2 f ×3. Moustache stays over the mouth. Torso held. Head moves occasionally. |
| 06 | Female lip-sync | Gaps: 5 f ×35, 4 f ×6, 3 f ×2. Pointing and hand-on-chest accents are timed separately from the mouth. Pressed lips during pauses. |
| 07 | Conversation | Shots: 0–2.67 wide two-shot, 2.67–10.23 CU woman, 10.23–17.13 CU man, 17.13–25.8 two-shot with gestures, 25.8– CU woman. Screen sides stay fixed. The listener barely moves. |
| 08 | Gestures | Leave neutral → hold the accent (0.5–1.3 s) → lower. Hand frame swaps: point, open palm, hand-on-chest. Two-hand poses for the king. Brown-vest man points upward. |
| 09 | Reactions | Worried brows (angled inner ends), widening eyes, closed-mouth listening. Reaction shots are 1.5–3 s around the partner's line. |
| 10 | Walking | Full-body: ~32-f cycle, slow small stride, translated over a static BG (2.3–7.3 s). Waist-up: character centered, houses/trees scroll (10.9–14.3, 17.2–20.9). Side-by-side couple walk. Bicycle + pedestrian in a wide street. Guards walk with the landscape scrolling. |
| 11 | Faint & carry | 0–7 s talking CU with eyes closing. 7.0–9.5 s whole body rotates (pivot at the feet) onto the bed, then a cut to lying + standing husband. 12.4 s short dip. 18.4 s carry: combined pose, BG tracks past tree and house, FG tree occludes. 24.9 s reaction CU of another woman at a doorway. |
| 12 | Seated/standing | Woman seated on a bed edge beside a standing man. Turbaned man in an armchair. Sage seated beside a prone woman. Cross-legged on a bed. King seated frontally. Hip contact matches the furniture. Calendar insert at 26 s. |
| 13 | Parrot | Beak open/close plus wing "hand" gestures while talking. Blink like humans. Flight: wing poses cycle with the bird centered and the forest scrolling (17–21.7 s). Perched: feet gripping the rock, tail overlapping it. |
| 14 | Outdoor BGs | Forest river + stone arches, village courtyard (two houses + banyan), wide thatched village with FG flowers, colourful town street with gate, night village (blue-purple grade + FG flowers), riverbank. FG accent in a corner, MG path for characters, BG trees/hills. |
| 15 | Interiors | Cream room (doorway, bags, hanging cloth, pot), blue room (shelves of steel pots, lantern niche, pink bed), green sitting room (red sofas, curtains, big window), sparse mud room. FG pot in front of the acting area. |
| 16 | Palace | Symmetric throne room (sun-burst throne, red carpet, pillars, curtains) with a slow push-in. Throne CU. Adviser reverse angle with a curved stair. Patterned gold hall with arched windows. Crowd arrays along the aisle. |
| 17 | Camera | Reframe wide → MCU inside one shot. Village walk with houses sliding. Carry tracking past a tree. Forest walk with near trees faster than far ones. Parrot tracking. Lateral reveal across the court lineup (24–30 s). |
| 18 | Props | Thumb inks and presses on a document (insert). Gold coins on a pink cloth. Gem at the hip → hand release → gem moves. Hand-to-hand gem exchange. Gem held over a blade. Healing gem over a sleeping woman's face. |
| 19 | Magic | Sage fades to transparent over ~3 s (2.5–5.5 s) with the BG held. Gem sparkles. Stone tints grey → gold over ~6 s (13.5–19.5 s). Blade silver → gold in ~1 s (22.5–23 s). Translucent figure resolves to full opacity beside a villager (27.3–30 s). |
| 20 | Fades | Luminance curves: linear ~15 f out → 1 f black → ~15 f in, on all five transitions (e.g. 135→2→136 over 31 f). Hard cut doorway → interior. |
| 21 | Calendar | Window reaction → dip → travel (waist-up walk) → calendar: pill highlight grows 17 → 18 → 19 at ~15 f per date → palace wide. Second sweep: home → travel → calendar → town street → doorway arrival. |
| 22 | Occlusion | Woman passes **behind** the stationary man (back layer), exits left. Carried figure over the walker. Tree in front. Foreground pot. Gate in front of street figures. Spear behind the couple, foliage at the frame edge. |
| 23 | Groups | Trio on a balcony (speaker center, gestures across). Village group under a tree in a wide. Three indoor characters in a shallow inward line. Court crowds arrayed symmetrically. |
| 24 | Masked character | Walk-up wide (0–4.8 s) → two-shot standoff → masked MCU: acting via narrowed eyes, brows, arm beats. Villager reaction CU with worried brows + open-palm plea. Masked MCU with the BG drifting/panning (22–30 s). |
