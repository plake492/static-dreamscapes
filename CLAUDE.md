# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static Dreamscapes is an automated pipeline for generating 3-hour Synthwave/Lo-Fi/Vaporwave mixes for YouTube. The system transforms Suno-generated songs into cohesive, branded mixes organized by emotional arc structure, with full automation from audio ingestion to final rendering.

## Setup

### Initial Setup
```bash
# 1. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Make shell scripts executable
chmod +x scripts/*.sh
```

### Dependencies
- Python 3.8+ with librosa, numpy, ffmpeg-python, watchdog
- FFmpeg with crossfade support
- Bash shell

## Core Commands

### Orchestrator (Automated Pipeline)
```bash
# Activate virtual environment first
source venv/bin/activate

# Watch mode - continuously monitor Arc_Library for new files
./venv/bin/python3 agent/orchestrator.py --watch

# Run pipeline once immediately
./venv/bin/python3 agent/orchestrator.py --run-once

# Run pipeline with specific track number for build_mix.sh
./venv/bin/python3 agent/orchestrator.py --run-once --track-num 5

# Only run audio analysis
./venv/bin/python3 agent/orchestrator.py --analyze-only
```

### Audio Analysis (Manual)
```bash
# Analyze all tracks and generate metadata
./venv/bin/python3 agent/analyze_audio.py --input ./Arc_Library --output ./metadata
```

### Track Management
```bash
# Rename tracks chronologically by modification time
bash scripts/rename_by_mod_time.sh <folder_path>
bash scripts/rename_by_mod_time.sh <folder_path> --dry-run  # Preview only

# Add phase prefixes (A*/B*) to maintain arc order
bash scripts/prepend_tracks.sh

# Verify total runtime (should be ~3 hours / 10,800 seconds)
bash scripts/track_length_report.sh
```

### Build & Render (Manual)
```bash
# Build final mix with crossfades
bash scripts/build_mix.sh <track_number> [duration]

# Examples:
bash scripts/build_mix.sh 5 1      # 1 hour mix
bash scripts/build_mix.sh 5 2      # 2 hours
bash scripts/build_mix.sh 5 test   # 5 minutes for testing
```

## Architecture

### Phase-Based Emotional Arc

The system follows a strict 4-phase structure for each 3-hour mix:

1. **Phase 1 - Calm Intro**: Ambient, nostalgic, warm opening (70-80 BPM)
2. **Phase 2 - Flow/Focus**: Steady mid-tempo for sustained attention (80-90 BPM)
3. **Phase 3 - Uplift/Clarity**: Bright, optimistic, creative momentum (90-100 BPM)
4. **Phase 4 - Reflective Fade**: Slow, analog-warm closing (60-75 BPM)

Each phase maps to `/Arc_Library/Phase_X_*/` directories and has corresponding metadata in `/metadata/Phase_X.json`.

### Two-Layer Design

**Shell Scripts (`/scripts/`)**
- Handle mechanical tasks: renaming, sorting, verifying, rendering
- Lightweight, modular, executed sequentially by orchestrator
- Must exit with code 0 for success; non-zero halts pipeline

**Python Agent (`/agent/`)**
- Intelligent orchestration layer that decides when to run scripts
- Handles error recovery, metadata generation, and analysis
- `orchestrator.py`: Main automation entry point with three modes:
  - `--watch`: Continuous file monitoring with 60s cooldown
  - `--run-once`: Single pipeline execution
  - `--analyze-only`: Audio analysis only
- `analyze_audio.py`: Extracts BPM, key, brightness, loudness via librosa

### Metadata System

**Structure:**
- `/metadata/Phase_X.json`: Per-phase song collections
- `/metadata/song_index.json`: Global lookup table linking track IDs to locations
- `/metadata/build_history.json`: Historical record of rendered mixes

**Audio Features Extracted:**
- Duration, BPM (tempo), RMS energy
- Brightness (spectral centroid)
- Zero-crossing rate (texture/roughness)
- Key estimation via chroma analysis

### Pipeline Execution Order

1. `rename_by_mod_time.sh` → Sort/rename by modification time
2. `prepend_tracks.sh` → Add phase prefixes
3. `analyze_audio.py` → Extract audio metadata (can continue on fail)
4. `track_length_report.sh` → Verify ~3 hour runtime
5. `build_mix.sh` → FFmpeg crossfade rendering

**Critical Rule:** Steps 1, 2, 4, 5 must succeed (exit code 0) or pipeline halts. Only step 3 (analysis) can continue on failure.

## Key Implementation Details

### FFmpeg Rendering Strategy

`build_mix.sh` uses complex filter chains:
- Loops background video indefinitely (`-stream_loop -1`)
- Applies volume boost (default 1.75x)
- Crossfades between songs using `acrossfade` filter (5s overlap default)
- Repeats song sequence to fill target duration
- Adds fade-in (3s) and fade-out (10s) to final mix
- Outputs as H.264 video with AAC audio (192k bitrate)

### File Organization

```
Arc_Library/
  Phase_1_Calm_Intro/
  Phase_2_Flow_Focus/
  Phase_3_Uplift_Clarity/
  Phase_4_Reflective_Fade/

Rendered/
  <track_num>/
    output_<timestamp>/
      output.mp4
      ffmpeg_command.txt
      filter_complex.txt

metadata/
  Phase_1.json, Phase_2.json, etc.
  song_index.json
  build_history.json
```

### Script Conventions

- All scripts log to `logs/orchestrator.log` in format:
  ```
  [TIMESTAMP] [SCRIPT_NAME] Status: SUCCESS | FAIL
  Details: <description or error>
  ```
- Scripts use null delimiters (`-print0`) to handle filenames with spaces
- `rename_by_mod_time.sh` skips files already numbered (matching `^[0-9]+[_\-\. ]`)
- FFmpeg command and filter complex are saved to output directory for debugging

## Important Context

- Do not manually modify `/Rendered/` - it's rebuilt on every run
- Script names must remain consistent with documentation or orchestrator won't detect them
- Always use the virtual environment (`venv/`) when running Python scripts
- Logs are written to `logs/orchestrator.log` with timestamps
- Acceptable runtime tolerance: ±60 seconds from 3-hour goal (10,800s)
- Orchestrator watch mode uses a 60-second cooldown after last file before triggering pipeline
- Build history is automatically tracked in `/metadata/build_history.json`
