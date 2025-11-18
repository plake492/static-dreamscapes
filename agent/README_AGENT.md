# 🤖 Static Dreamscapes — AI Agent Reference

> Documentation for the **Python agent layer** of the Static Dreamscapes Automation System.  
> The agent handles orchestration, analysis, and metadata management — serving as the intelligent core of the automated pipeline.

All Python logic lives in `/agent/`.  
This layer communicates with the shell utilities in `/scripts/` and manages the end-to-end workflow from track ingestion to rendered mix.

---

## 🧩 Overview

| Component          | File                                      | Description                                                                |
| ------------------ | ----------------------------------------- | -------------------------------------------------------------------------- |
| **Orchestrator**   | [`orchestrator.py`](#1️⃣-orchestratorpy)   | Central controller that coordinates all stages of the pipeline.            |
| **Audio Analyzer** | [`analyze_audio.py`](#2️⃣-analyze_audiopy) | Uses `librosa` to extract musical features and update structured metadata. |

---

## 1️⃣ `orchestrator.py`

**Location:** `agent/orchestrator.py`
**Depends on:** Bash scripts in `/scripts/`, `analyze_audio.py`, `watchdog`, `os`, `subprocess`, `json`, `time`, `logging`

---

### 🧠 Purpose

The orchestrator is the **central automation brain**.
It detects new Suno-generated audio files, waits for downloads to complete, then executes all stages of the production pipeline in sequence.

It is responsible for:

- Running shell scripts (`rename_by_mod_time.sh`, `prepend_tracks.sh`, etc.)
- Calling `analyze_audio.py` at the correct point
- Handling logging, error catching, and pipeline recovery
- Writing merged metadata JSONs in `/metadata/`
- Triggering the final FFmpeg mix build
- Tracking build history automatically

---

### ⚙️ Three Operating Modes

**1. Watch Mode (`--watch`)**
```bash
./venv/bin/python3 agent/orchestrator.py --watch
```
- Continuously monitors `/arc_library/` for new MP3 files
- Uses 60-second cooldown after last file detection
- Automatically triggers full pipeline when ready
- Ideal for hands-off operation during Suno batch downloads

**2. Run Once (`--run-once`)**
```bash
./venv/bin/python3 agent/orchestrator.py --run-once
./venv/bin/python3 agent/orchestrator.py --run-once --track-num 5
```
- Executes full pipeline immediately
- Optional `--track-num` argument for build_mix.sh
- Returns exit code 0 on success, non-zero on failure
- Suitable for manual or scheduled execution

**3. Analyze Only (`--analyze-only`)**
```bash
./venv/bin/python3 agent/orchestrator.py --analyze-only
```
- Runs only the audio analysis step
- Skips rename, prepend, verification, and rendering
- Useful for updating metadata without full build

---

### 🧾 Pipeline Execution Order

| Step | Script/Module | Must Succeed | Description |
|------|---------------|--------------|-------------|
| 1 | `rename_by_mod_time.sh` | ✅ Yes | Sort and rename tracks by modification time (per phase folder) |
| 2 | `prepend_tracks.sh` | ✅ Yes | Add phase prefixes (A*/B*) |
| 3 | `analyze_audio.py` | ⚠️ Can fail | Extract audio metadata (continues on fail) |
| 4 | `track_length_report.sh` | ✅ Yes | Verify ~3 hour runtime |
| 5 | `build_mix.sh` | ✅ Yes | Render final mix with FFmpeg |

**Critical Rule:** Steps 1, 2, 4, 5 must succeed (exit code 0) or pipeline halts. Only step 3 (analysis) can continue on failure.

---

### 📤 Outputs

- `logs/orchestrator.log` — execution trace with timestamps
- Updated metadata under `/metadata/phase_X.json` and `song_index.json`
- `metadata/build_history.json` — chronological build records
- `rendered/<track_num>/output_<timestamp>/output.mp4` — finished mix

---

### 🪢 Key Features

- **Comprehensive logging**: File and console handlers with different log levels
- **Script timeout**: 10-minute max per script execution
- **Duration validation**: Checks total duration against 3-hour target (±60s tolerance)
- **Build history tracking**: Automatically records timestamp, file count, duration, runtime
- **Error recovery**: Continues with analysis failures, halts on critical failures
- **File watching**: Intelligent cooldown to batch multiple file additions

---

## 2️⃣ `analyze_audio.py`

**Location:** `agent/analyze_audio.py`  
**Depends on:** `librosa`, `json`, `os`, `numpy`, `logging`

---

### 🧠 Purpose

Analyzes every `.mp3` file within `/Arc_Library/` and extracts key musical and acoustic data for metadata structuring.
Outputs detailed JSON files per phase and an aggregated index used for later curation or playlist creation.

---

### ⚙️ Features Extracted

| Attribute      | Description                                          |
| -------------- | ---------------------------------------------------- |
| `duration_sec` | Total track duration in seconds                      |
| `bpm`          | Estimated tempo using onset detection                |
| `rms`          | Average loudness (Root Mean Square)                  |
| `brightness`   | Mean spectral centroid — represents tonal brightness |
| `key_guess`    | Estimated musical key via chroma features            |

---

### 📥 Inputs

- `/arc_library/phase_1_calm_intro/`
- `/arc_library/phase_2_flow_focus/`
- `/arc_library/phase_3_uplift_clarity/`
- `/arc_library/phase_4_reflective_fade/`

---

### 📤 Outputs

| File                        | Description                          |
| --------------------------- | ------------------------------------ |
| `/metadata/phase_X.json`    | Structured metadata for each phase   |
| `/metadata/song_index.json` | Master index for all analyzed tracks |
| `logs/orchestrator.log`     | Log entries appended                 |

---

### ⚙️ Example Usage

Run manually:

```bash
python3 agent/analyze_audio.py
```

Or automatically (called by orchestrator):

```python
subprocess.run(["python3", "agent/analyze_audio.py"])
```

---

### 🧩 Agent Integration Notes

- Should return code 0 when analysis completes successfully.
- Automatically overwrites older metadata with fresh analysis results.
- Handles skipped or missing files gracefully (logs warnings, not errors).
- Can be imported as a function:

```python
from agent.analyze_audio import analyze_audio_batch
analyze_audio_batch("/Arc_Library/", "/metadata/")
```

---

## 🧠 Data Flow Summary

```mermaid
graph TD
  A[/arc_library/ new Suno tracks] --> B[orchestrator.py]
  B --> C[rename_by_mod_time.sh]
  C --> D[prepend_tracks.sh]
  D --> E[analyze_audio.py]
  E --> F[/metadata/ JSON updates]
  F --> G[track_length_report.sh]
  G --> H[build_mix.sh]
  H --> I[/rendered/ Final Mix]
```

---

## 🧾 Logging Standards

All agent actions log to `logs/orchestrator.log` in the format:

```
[TIMESTAMP] [MODULE] Status: SUCCESS | WARNING | ERROR
Details: <description>
```

Examples:

```
[2025-10-29 23:31:04] [analyze_audio.py] Status: SUCCESS — 12 files analyzed.
[2025-10-29 23:34:22] [build_mix.sh] Status: SUCCESS — Final mix rendered (02:58:44).
```

---

## 🧰 Maintenance Notes

- Both scripts must remain in `/agent/` to preserve import paths.
- `analyze_audio.py` should avoid external dependencies beyond `librosa` and `numpy`.
- Ensure FFmpeg and librosa are installed system-wide before running.
- The orchestrator should handle `.sh` script failures with `subprocess.CalledProcessError` handling.
- Logs are rotated automatically after successful renders.

---

## ✅ Related Documentation

- `04_AI_AGENT_WORKFLOW.md` — detailed pipeline logic
- `05_AUDIO_ANALYSIS.md` — deep dive into librosa feature extraction
- `06_SCRIPT_DEFINITIONS.md` — shell script descriptions
- `../scripts/README_SCRIPTS.md` — mechanical layer reference
