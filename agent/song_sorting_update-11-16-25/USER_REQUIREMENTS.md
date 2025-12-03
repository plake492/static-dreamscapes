# User Requirements - Song Sorting Update

The structure of how songs are sorted will be changing significantly.

# GOAL

Create a bank of songs with information that can be automatically consumed by scripts and AI to provide existing tracks to upcoming, or inprogress tracks.

## Track labeling

I will be adding created songs that are labeled in the following format **A_2_5_15a**

- The A_ is only relevant to identify if a song was used in the first half or second help of the song (A_, or _B for now).

- The first digit follow A_ represents the phase number it was used in: 1,2,3,4.

- The second digit is the song number according to a doc that will be provided (explained below) which can be correlated to certain metadata

- The third digit is the track number (the 15th track created, or track that is in the rendered and track folders as 15).

- The letter at the end indicates what order the track was used in the phase, a - 1, b - 2, etc. There will sometimes be letters up to and possibly exceeding f, this should be tracked as metadata.

---
## Reference File

You will be provided with a manually added x_track_flow (4_track_flow)

You will plan the project setup that determines where all of these songs and docs will be added

The doc will be in the following format (There will be other info that will be used in later iterations). **Ignore the checkboxes, these are not relevant**

```markdown
## 🌇 **Phase 1 – Urban Rainfall (Opening Ambience)**

- [x]  **1.** ambient vaporwave hum, soft rain textures, slow city rhythm — *neon rain calm*
- [x]  **2.** distant traffic reverb, warm pad layers, muted reflections — *neon rain calm*
- [x]  **3.** mellow lofi beat, gentle reverb, soft window glow — *neon rain calm*

---

## 🚦 **Phase 2 – Deep Focus Flow (Creative Pulse)**

- [x]  **4.** midtempo lofi vaporwave beat, smooth analog bass — *neon rain calm*
- [x]  **5.** rhythmic synth chords, teal reflections, light static — *neon rain calm*
- [x]  **6.** steady vaporwave pulse, deep city-night focus — *neon rain calm*
- [ ]  **7.** dreamwave textures, clean analog clarity, productive flow — *neon rain calm*

---

## 🌃 **Phase 3 – Midnight Stillness (Inner Reflection)**

- [ ]  **8.** minimal lofi chords, tape hiss warmth, window ambience — *neon rain calm*
- [ ]  **9.** soft rhythmic fade, nostalgic synth resonance — *neon rain calm*
- [ ]  **10.** emotional analog layers, subdued midnight bass — *neon rain calm*

---

## 🌌 **Phase 4 – Dreamfade (Night's End)**

- [ ]  **11.** slow vaporwave outro, static haze drifting — *neon rain calm*
- [ ]  **12.** warm pads with gentle delay, fading into night quiet — *neon rain calm*
- [ ]  **13.** analog fade-out, soft rain noise dissolving into silence — *neon rain calm*

---
```

The h2 represent the arc 1,2,3,4.

The number beside the checkbox represents the track number **When generating, there will typically be 4 or more tracks per number**

The text following the number is the prompt. This will be used to give more detailed info on the theme and feel of the song, and will be used to further determine what tracks to use based on provided documents about new or in process tracks.
