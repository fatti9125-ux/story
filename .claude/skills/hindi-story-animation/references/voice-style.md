# Voice-over style (measured from the reference clips' audio)

Measured with `librosa` (pitch via pYIN, loudness envelope) and `ffmpeg ebur128` on the 15
reference clips that kept their original Hindi audio. These numbers come from measurement, not
from listening. Use them to cast and tune TTS voices. Do NOT clone the reference channel's voice
artists. Match the *style* with licensed TTS voices or the user's own VO.

## Overall delivery

| Property | Measured | Use |
|---|---|---|
| Speech density | 70–80% of each dialogue shot is voiced; few gaps | Lines run back-to-back, energetic, no long dead air |
| Speaking rate | ~3.5–4.8 syllable peaks/s (sages slowest, arguments fastest) | Normal-to-brisk conversational Hindi. TTS rate ≈ default to +10% |
| Pauses inside a line | 0.2–0.3 s | Comma / breath |
| Pauses between speakers | 0.3–0.6 s, up to 1.1–1.5 s at a scene beat | Sentence gap 0.4 s. Reaction or scene beat 1.0–1.5 s |
| Pitch range | p10→p90 spans about an octave per speaker | Theatrical, expressive storytelling: rises on questions, drops at line ends |
| Dialogue loudness | −16 to −21 LUFS per segment | Mix the final video to about −16 LUFS integrated (−1 dBTP peak) |
| Music bed | Continuous, 23–30 dB below the speech peaks; held notes audible in pauses | Soft instrumental bed under all dialogue, never stopping between lines |
| Edit vs audio | Lines often continue across shot cuts (L-cuts), e.g. the woman's line runs past the cut to her close-up | Cut on picture rhythm. A line may start before or end after a cut |

## Voice casting (pitch medians are the main guide)

| Character type | Median F0 | Range (p10–p90) | Rate | Notes |
|---|---|---|---|---|
| Adult village man | 130–150 Hz | 66–230 Hz | 3.5–4.7 | Warm, mid-low, expressive. Lifts pitch when pleading (≈180 Hz) |
| Old sage / sadhu | ~100 Hz | 77–135 Hz (up to ~200 on emphasis) | 3.6–4.3 | Deep, calm, slower, steady. Blessing/teaching tone |
| Adviser / official | ~165 Hz | 110–225 Hz | ~4.1 | Brisk, slightly nasal-formal |
| Villain (masked) | ~120 Hz | 87–180 Hz | ~3.8 | Low, continuous (no pauses), menacing |
| Adult village woman | 200–240 Hz | 97–333 Hz | 3.9–4.4 | Bright, expressive. Pointed delivery when arguing |
| Weak / unwell woman | ~210 Hz, ~5 dB quieter | 148–308 Hz | 4.4 | Same voice, softer and breathier before fainting |
| Parrot / magical bird | ~250 Hz | 117–331 Hz with flat sing-song holds | ~4.0 | Higher, child-like or female voice, sustained sing-song notes |

Pattern seen in the montage clips: female-range speech (≈200–330 Hz) often plays over shots of
male characters (the sage wide shot, the king bust). This is probably a narrator or off-screen
speaker. So the style uses a **narrator voice** that bridges scenes, plus character voices for
dialogue.

## TTS recipe

1. Cast one voice per character from the table, plus one narrator. Keep each voice fixed across
   the whole story.
2. Generate line by line with SSML or the service's controls: rate default to +10%; pitch shift
   only within ±10% (bigger shifts sound robotic); add a 0.2–0.3 s break at commas and 0.4 s
   between sentences.
3. Emotion per line from the script (angry, crying, pleading, happy, whisper) via the service's
   style tags (ElevenLabs stability/style, Azure `mstts:express-as`).
4. Assemble: dialogue track (lines with 0.3–0.6 s gaps, 1–1.5 s at scene beats), then a music bed
   at −25 dB relative to the voice, then loudness-normalise to −16 LUFS.
5. Lip-sync: the mouth loop runs only while that character's line plays (5-frame mouth swaps).

Supported services (need the user's API key via the environment's secure credential form):
ElevenLabs (most natural/emotional Hindi), Microsoft Azure Speech (hi-IN neural voices, large
free tier), Google Cloud TTS.
