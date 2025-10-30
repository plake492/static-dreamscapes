# 🎛️ Static Dreamscapes — Audio Analysis Guide

## Purpose

This document instructs the AI agent how to run and integrate the `analyze_audio.py` script to generate song metadata for the Arc Library. The analysis step converts Suno-generated audio into measurable data (duration, BPM, key, energy, brightness) for better arc curation.

---

## 1. Execution Context

The agent should trigger this analysis:

* Whenever new `.mp3` files are added to `/Arc_Library/`.
* After a full batch of Suno tracks has been downloaded for a mix cycle.
* Before playlist generation (`curate_mix.js`).

### CLI Example

```bash
python3 agent/analyze_audio.py --input ./Arc_Library --output ./metadata
```

### Expected Outcome

* Each phase file in `/metadata/` updated with new entries.
* A global `song_index.json` refreshed with filename → phase mapping.
* Console log confirms total processed files.

---

## 2. Input / Output Flow

| Input                            | Output                                    |
| :------------------------------- | :---------------------------------------- |
| `/Arc_Library/**/*.mp3`          | `/metadata/Phase_X.json` per phase        |
| (derived phase name from folder) | `/metadata/song_index.json` global lookup |

**Example:**

```
Arc_Library/
  Phase_2_Flow_Focus/
    Midtempo_Groove/A_02_05-CityDreams.mp3
→ metadata/Phase_2_Flow_Focus.json
→ metadata/song_index.json
```

---

## 3. Metadata Fields Generated

| Field          | Type          | Description                             |
| :------------- | :------------ | :-------------------------------------- |
| `filename`     | string        | Name of the analyzed audio file         |
| `duration_sec` | float         | Length of track in seconds              |
| `bpm`          | float         | Estimated tempo using beat tracking     |
| `rms`          | float         | Average loudness (energy proxy)         |
| `brightness`   | float         | Average spectral centroid (tone warmth) |
| `zcr`          | float         | Zero-crossing rate (texture)            |
| `key_guess`    | string        | Estimated musical key                   |
| `phase_name`   | string        | Phase folder the track belongs to       |
| `file_path`    | string        | Absolute or relative path to file       |
| `analyzed_at`  | ISO timestamp | UTC analysis timestamp                  |

---

## 4. Integration in Workflow

**Step 1:** Suno outputs new `.mp3` tracks → saved to `/Arc_Library/Phase_X_*/*`
**Step 2:** Run `analyze_audio.py` to extract metrics.
**Step 3:** AI agent merges metadata into `/metadata` JSON schema.
**Step 4:** `curate_mix.js` reads updated data to build balanced arcs (BPM, brightness, RMS considered).
**Step 5:** `build_mix.sh` uses generated playlist to assemble via FFmpeg.

---

## 5. Automation Trigger

If running in continuous mode, the agent should:

1. Watch `/Arc_Library/` for new files (hash comparison).
2. Wait until batch completes (N minutes of no new writes).
3. Execute analysis automatically.
4. Log completion in `metadata/logs/audio_analysis.log`.

Example log entry:

```
[2025-10-28T17:35:02Z] Analyzed 16 new tracks (Phases 1–4)
```

---

## 6. Error Handling

* If `librosa` fails to load a file, skip it and log to `/metadata/logs/errors.log`.
* If BPM or key cannot be determined, default to `0` or `"Unknown"`.
* Always write valid JSON even for partial results.

---

## 7. AI Behavior Summary

**Agent Responsibilities:**

* Ensure all new Suno tracks are analyzed before curation.
* Validate that each file in `/Arc_Library/` exists in `song_index.json`.
* Re-analyze if file modification time changes.
* Use analysis data to:

  * Balance energy across phases.
  * Suggest which tracks to reuse vs replace.
  * Detect overall arc consistency.

---

## 8. Future Upgrades

* Integrate spectral contrast → richer warmth detection.
* Add loudness normalization suggestion for FFmpeg.
* Optional: train a small model to classify phase directly from audio features.

---

This document allows the AI agent to correctly incorporate `analyze_audio.py` into its end-to-end automation loop — ensuring every Suno-generated song contributes to a structured, data-aware Static Dreamscapes ecosystem.
