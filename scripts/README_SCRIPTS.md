# 🎛️ Static Dreamscapes — Script Reference

> Central documentation for all shell utilities used by the **Static Dreamscapes Automation System**.  
> These scripts handle file organization, audio preparation, runtime verification, and final mix rendering.

Each script lives under `/scripts/` and is invoked by the orchestration layer (`agent/orchestrator.py`).

---

## 🧩 Overview

| Step | Script                                                | Description                                                     | Continue on Fail |
| ---- | ----------------------------------------------------- | --------------------------------------------------------------- | ---------------- |
| 1    | [`rename_by_mod_time.sh`](#1️⃣-rename_by_mod_timesh)   | Sorts and renames tracks chronologically by modification time.  | ❌               |
| 2    | [`prepend_tracks.sh`](#2️⃣-prepend_trackssh)           | Prepends phase prefixes (A* / B*) to maintain arc order.        | ❌               |
| 3    | `analyze_audio.py`                                    | Extracts BPM, duration, key, RMS, brightness, etc.              | ✅               |
| 4    | [`track_length_report.sh`](#4️⃣-track_length_reportsh) | Verifies cumulative runtime ≈ 3 hours.                          | ❌               |
| 5    | [`build_mix.sh`](#5️⃣-build_mixsh)                     | Combines all tracks into a single rendered mix with crossfades. | ❌               |

All scripts log activity to `logs/orchestrator.log` and are executed in sequence by the AI agent.

---

## 1️⃣ `rename_by_mod_time.sh`

**Location:** `scripts/rename_by_mod_time.sh`  
**Called by:** `agent/orchestrator.py`

### 🧠 Purpose

Sorts all `.mp3` files in `/Arc_Library/` by modification time and renames them sequentially to preserve creation order.  
This maintains the intended musical flow across phases.

### ⚙️ Usage

```bash
bash scripts/rename_by_mod_time.sh
```

### 📥 Inputs

- `/Arc_Library/Phase_X/` — folders containing .mp3 tracks
- File modification timestamps — used for sorting

### 📤 Outputs

- Sequentially renamed .mp3 files (e.g. `001_track.mp3`, `002_track.mp3`)
- Log entries appended to `logs/orchestrator.log`

### 🪢 Dependencies

- `bash`, `find`, `sort`, `mv`

### 🧩 Agent Notes

- Must run before `prepend_tracks.sh`
- Return code 0 = success; otherwise stop pipeline
- Typical runtime: ~2–4 s for 20–30 files

---

## 2️⃣ `prepend_tracks.sh`

**Location:** `scripts/prepend_tracks.sh`  
**Called by:** `agent/orchestrator.py`

### 🧠 Purpose

Prepends phase identifiers (A*, B*) to track filenames for structured playback order.
Ensures arc continuity and enables phase-based filtering during analysis and rendering.

### ⚙️ Usage

```bash
bash scripts/prepend_tracks.sh
```

### 📥 Inputs

- `/Arc_Library/Phase_X/` — renamed .mp3 files
- Arc mapping rules — e.g. first half = A*, second half = B*

### 📤 Outputs

- Updated filenames like `A_001_track.mp3`, `B_002_track.mp3`
- Log entries appended to `logs/orchestrator.log`

### 🪢 Dependencies

- `bash`, `mv`

### 🧩 Agent Notes

- Runs after `rename_by_mod_time.sh`
- Return code 0 = success; otherwise halt
- Typical runtime: ~1–2 s

---

## 4️⃣ `track_length_report.sh`

**Location:** `scripts/track_length_report.sh`  
**Called by:** `agent/orchestrator.py`

### 🧠 Purpose

Calculates the total runtime of all .mp3 files in `/Arc_Library/`.
Used to confirm the total length is close to 3 hours (≈ 10,800 seconds).

### ⚙️ Usage

```bash
bash scripts/track_length_report.sh
```

### 📥 Inputs

- `/Arc_Library/Phase_X/` — finalized .mp3 files

### 📤 Outputs

- `total_length.txt` — text file with cumulative seconds + HH:MM:SS format
- Log entries in `logs/orchestrator.log`

### 🪢 Dependencies

- `bash`, `ffprobe` (FFmpeg), `awk`

### 🧩 Agent Notes

- Must run before `build_mix.sh`
- Return code 0 = success; otherwise stop pipeline
- Acceptable tolerance: ± 60 seconds from 3-hour goal
- Typical runtime: ~3–5 s

---

## 5️⃣ `build_mix.sh`

**Location:** `scripts/build_mix.sh`  
**Called by:** `agent/orchestrator.py`

### 🧠 Purpose

Builds the final 3-hour mix using FFmpeg by combining all processed .mp3 files.
Applies crossfades and normalizes levels for a cohesive listening experience.

### ⚙️ Usage

```bash
bash scripts/build_mix.sh
```

### 📥 Inputs

- `/Arc_Library/Phase_X/` — ordered .mp3 files
- `/metadata/song_index.json` — reference for song tagging
- Crossfade duration (default 2–3 s)

### 📤 Outputs

- `Rendered/Final_Mix.mp3` — complete audio mix
- `Rendered/final_mix.log` — FFmpeg operation log

### 🪢 Dependencies

- FFmpeg with crossfade support

### 🧩 Agent Notes

- Runs after duration verification
- Return code 0 = success; otherwise stop pipeline
- Expected render time: 2–3 min for 3-hour mix
- After completion, orchestrator verifies final length with FFprobe

---

## 🧠 Pipeline Summary

| Step | Script                   | Purpose                                 | Continue on Fail |
| ---- | ------------------------ | --------------------------------------- | ---------------- |
| 1    | `rename_by_mod_time.sh`  | Sort and rename tracks by modified time | ❌               |
| 2    | `prepend_tracks.sh`      | Add phase prefixes                      | ❌               |
| 3    | `analyze_audio.py`       | Extract audio metadata                  | ✅               |
| 4    | `track_length_report.sh` | Verify total duration (~3 h)            | ❌               |
| 5    | `build_mix.sh`           | Render final mix                        | ❌               |

---

## 🧾 Logging Conventions

All scripts append runtime data to `logs/orchestrator.log` in this format:

```
[TIMESTAMP] [SCRIPT_NAME] Status: SUCCESS | FAIL
Details: <description or error message>
```

The orchestrator reads these logs to decide whether to continue or halt execution.

---

## 🧰 Maintenance Notes

- Keep script names and paths consistent with this README.
- Each script must exit with code 0 for success.
- Avoid manual edits in `/Rendered/` — it's overwritten each build.
- Logs are rotated automatically by `orchestrator.py` after each successful render.

---

## ✅ Next Steps

For integration context, see:

- `agent/analyze_audio.py`
- `agent/orchestrator.py`
- `agent/docs/04_AI_AGENT_WORKFLOW.md`
