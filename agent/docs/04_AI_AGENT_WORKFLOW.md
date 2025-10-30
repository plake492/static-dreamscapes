# 🤖 Static Dreamscapes — AI Agent Workflow

## Overview

The AI agent acts as both a **cataloging system** and a **curation assistant** for Static Dreamscapes. It interfaces with shell scripts, FFmpeg, and metadata files to ensure smooth automation from song creation to rendered 3‑hour mixes.

---

## 1. Core Responsibilities

1. **Organize** — Detect, tag, and file new songs into the correct phase folders.
2. **Curate** — Build 3‑hour mixes using phase logic and metadata filtering.
3. **Validate** — Confirm total runtime, naming order, and sequence alignment before render.
4. **Render** — Trigger shell scripts to merge selected tracks with crossfades.
5. **Record** — Update metadata after successful build.

---

## 2. Startup Process

1. Load environment variables:

   ```bash
   export TRACKS_DIR="~/Dev/personal/ffmpeg-lofi/Tracks"
   export ARC_LIB="~/Dev/personal/ffmpeg-lofi/Arc_Library"
   export META_DIR="~/Dev/personal/ffmpeg-lofi/metadata"
   export RENDER_DIR="~/Dev/personal/ffmpeg-lofi/Rendered"
   ```

2. Initialize watchers on `/Arc_Library/` and `/Mixes/`.

3. Load all phase JSON metadata files into memory.

4. Build runtime song index for fast lookup.

---

## 3. File Detection & Tagging

When a new `.mp3` appears in `/Arc_Library/`:

1. Extract **audio features** (duration, BPM, energy, frequency centroid).
2. Analyze mood via pretrained model or audio fingerprint.
3. Compare against existing phase averages.
4. Assign phase label (1–4) and mood tags.
5. Create or update entry in `/metadata/Phase_X.json`.
6. Add record to `song_index.json` if missing.
7. Rename using naming convention via shell:

   ```bash
   bash scripts/rename_by_mod_time.sh
   ```

---

## 4. Curation Logic

When planning a new track (e.g., Track 15):

1. Agent selects **3–4 songs per phase** according to target theme (e.g., `Winter`, `City`, `Sunrise`).
2. Pulls tracks with highest freshness and lowest prior usage count.
3. Filters by compatible BPM/key range (within ±5 BPM).
4. Ensures tonal flow → calm → focus → bright → reflective.
5. Calculates total runtime. If under 10,800 sec (3 hr), fills with short ambient fillers.
6. Generates temporary `input.txt` for FFmpeg render.

Example output:

```
file '/Arc_Library/Phase_1_Calm_Intro/A_01_03-Rainy_Hum.mp3'
file '/Arc_Library/Phase_2_Flow_Focus/A_02_05-CityDreams.mp3'
file '/Arc_Library/Phase_3_Uplift_Clarity/A_03_04-SkylineReflections.mp3'
file '/Arc_Library/Phase_4_Reflective_Fade/A_04_06-TapeEchoes.mp3'
```

---

## 5. Rendering Workflow

1. Call verification:

   ```bash
   bash scripts/verify_length.sh
   ```

2. If length ≈ 10,800 sec ± 120 sec → continue.
3. Trigger render:

   ```bash
   bash scripts/build_mix.sh input.txt Track_15_WinterReflections.mp3
   ```

4. Log metadata:

   ```json
   {
     "rendered_output": "Rendered/Track_15_WinterReflections.mp3",
     "runtime": 10802,
     "phases": [1, 2, 3, 4],
     "ai_confidence": 0.92
   }
   ```

5. Move mix JSON summary to `/metadata/mixes/`.

---

## 6. Post‑Render Updates

After successful FFmpeg run:

- Append `used_in` reference to each included song.
- Update cumulative playtime statistics.
- Generate simple `.log` summary for changelog:

  ```bash
  echo "[2025‑10‑28] Built Track_15_WinterReflections (3:00:02)" >> metadata/logs/build_history.log
  ```

---

## 7. AI Selection Rules (Simplified)

| Phase | Priority                | Filters                             | Typical BPM |
| :---- | :---------------------- | :---------------------------------- | :---------- |
| 1     | Calm & analog texture   | `mood: calm, nostalgic, ambient`    | 70–80       |
| 2     | Flow & rhythm stability | `mood: focus, analog, steady`       | 80–90       |
| 3     | Uplift & clarity        | `mood: bright, optimistic, melodic` | 90–100      |
| 4     | Reflective fade         | `mood: slow, reflective, warm`      | 60–75       |

---

## 8. Command Interface (Planned)

```bash
# Register all new songs
ai_agent register --scan ~/Dev/personal/ffmpeg-lofi/Arc_Library

# Generate next release automatically
ai_agent curate --theme "City Signals" --target-length 10800

# Render using verified input list
ai_agent render --mix Track_14_CitySignals

# Refresh metadata
ai_agent sync --update-index
```

---

## 9. Extensibility Hooks

| Function                            | Purpose                                    |
| :---------------------------------- | :----------------------------------------- |
| **analyze_audio_features(path)**    | Extract tempo, key, spectral features.     |
| **suggest_next_track(phase, mood)** | Retrieve optimal next song for continuity. |
| **validate_mix_runtime()**          | Compare total runtime vs 3‑hour goal.      |
| **render_mix()**                    | Wrap FFmpeg CLI into a Node/Python call.   |
| **update_metadata()**               | Commit mix info to JSON and logs.          |

---

## 10. Long‑Term Capabilities

- Theme‑aware curation: detect visual palette and suggest matching songs.
- Predictive track selection using performance data (CTR, retention).
- Dynamic arc composition beyond 4‑phase structure.
- Self‑training tag refinement based on listener engagement metrics.

---

This workflow ensures the AI agent can function autonomously within your codebase—analyzing, tagging, curating, and rendering new Static Dreamscapes mixes while preserving phase structure and sonic identity.
