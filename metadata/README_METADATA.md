# 🧾 Static Dreamscapes — Metadata Directory

This directory stores all structured metadata for the Static Dreamscapes automation system, including per-phase song catalogs, global song index, and build history.

---

## Directory Structure

```
metadata/
├── phase_1_calm_intro.json          # Phase 1 song catalog
├── phase_2_flow_focus.json          # Phase 2 song catalog
├── phase_3_uplift_clarity.json      # Phase 3 song catalog
├── phase_4_reflective_fade.json     # Phase 4 song catalog
├── song_index.json                  # Global lookup table
├── build_history.json               # Historical record of all renders
├── mixes/                           # Per-mix metadata
│   ├── track_09_neon_arcade.json
│   ├── track_10_dawn_drive.json
│   └── ...
└── logs/                            # Analysis and processing logs
    ├── audio_analysis.log
    └── errors.log
```

---

## File Descriptions

### Phase Files (`Phase_X_*.json`)

Each phase file contains an array of all songs belonging to that emotional arc stage.

**Schema:**
```json
{
  "phase": 1,
  "name": "Calm Intro",
  "description": "Ambient, nostalgic warmth for opening atmosphere",
  "songs": [
    {
      "filename": "A_01_01-RainyAfterHours.mp3",
      "duration_sec": 245.7,
      "bpm": 72.5,
      "rms": 0.04523,
      "brightness": 1847.32,
      "zcr": 0.08234,
      "key_guess": "A",
      "phase_name": "phase_1_calm_intro",
      "file_path": "arc_library/phase_1_calm_intro/ambient_warmth/A_01_01-RainyAfterHours.mp3",
      "analyzed_at": "2025-10-29T18:45:00Z"
    }
  ]
}
```

**Fields:**
- `filename`: Original MP3 filename
- `duration_sec`: Track length in seconds
- `bpm`: Estimated tempo via beat tracking
- `rms`: Average loudness (energy proxy)
- `brightness`: Spectral centroid (higher = brighter tone)
- `zcr`: Zero-crossing rate (texture/roughness indicator)
- `key_guess`: Estimated musical key (C, C#, D, etc.)
- `phase_name`: Source phase folder
- `file_path`: Relative or absolute path to file
- `analyzed_at`: UTC timestamp of analysis

---

### Global Song Index (`song_index.json`)

Maps every track filename to its phase and metadata location for fast lookup.

**Schema:**
```json
{
  "A_01_01-RainyAfterHours.mp3": {
    "phase": "phase_1_calm_intro",
    "path": "metadata/phase_1_calm_intro.json"
  },
  "A_02_05-CityDreams.mp3": {
    "phase": "phase_2_flow_focus",
    "path": "metadata/phase_2_flow_focus.json"
  }
}
```

---

### Build History (`build_history.json`)

Chronological record of all pipeline executions and rendered mixes.

**Schema:**
```json
{
  "builds": [
    {
      "timestamp": "2025-10-29T23:15:42Z",
      "track_number": 5,
      "total_files": 24,
      "metadata": {
        "duration_seconds": 10812.5,
        "pipeline_runtime": 187.3,
        "success": true
      }
    }
  ]
}
```

**Fields:**
- `timestamp`: UTC time when build completed
- `track_number`: Track number passed to build_mix.sh (if any)
- `total_files`: Number of MP3 files processed
- `metadata.duration_seconds`: Total mix duration
- `metadata.pipeline_runtime`: Time taken to run full pipeline
- `metadata.success`: Whether build completed successfully

---

### Mix Metadata (`mixes/track_X_*.json`)

Individual metadata files for each finished 3-hour mix.

**Schema:**
```json
{
  "track_number": 9,
  "title": "Neon Arcade Memories",
  "duration_sec": 10800,
  "phases": [
    {
      "phase": 1,
      "songs": ["A_01_01-RainyAfterHours.mp3", "A_01_02-SleeplessStatic.mp3"]
    },
    {
      "phase": 2,
      "songs": ["A_02_05-CityDreams.mp3", "A_02_07-SteadySignal.mp3"]
    },
    {
      "phase": 3,
      "songs": ["A_03_03-DaylightReflect.mp3"]
    },
    {
      "phase": 4,
      "songs": ["A_04_06-TwilightStatic.mp3"]
    }
  ],
  "themes": ["Retro Nostalgia", "City Night", "Arcade Glow"],
  "rendered_output": "rendered/track_09_neon_arcade_memories.mp3",
  "render_date": "2025-10-29T10:00:00Z",
  "ai_notes": {
    "mix_balance": "Good warm/cool ratio, smooth pacing",
    "suggested_improvements": "Add brighter Phase 3 element next iteration"
  }
}
```

---

## Usage by Orchestrator

The orchestrator interacts with these files automatically:

1. **Audio Analysis** → Updates phase JSON files and song_index.json
2. **Pipeline Execution** → Reads song_index.json for validation
3. **Build Completion** → Appends entry to build_history.json
4. **Curation** (future) → Queries phase files by BPM, brightness, etc.

---

## Maintenance

### Backup
Periodically back up this directory to preserve analysis data:
```bash
tar -czf metadata_backup_$(date +%Y%m%d).tar.gz metadata/
```

### Validation
Check for orphaned entries (files in metadata but not in arc_library):
```bash
# (Script to be implemented)
python3 agent/validate_metadata.py
```

### Reset
To start fresh (caution: deletes all metadata):
```bash
rm -f metadata/phase_*.json metadata/song_index.json metadata/build_history.json
```

---

## Related Documentation

- [agent/docs/03_METADATA_SCHEMA.md](../agent/docs/03_METADATA_SCHEMA.md) - Detailed schema definitions
- [agent/docs/05_ADUIO_ANALYSIS.md](../agent/docs/05_ADUIO_ANALYSIS.md) - How analysis populates these files
- [agent/analyze_audio.py](../agent/analyze_audio.py) - Audio analysis script

---

This metadata system enables the AI agent to make intelligent curation decisions based on measurable audio characteristics, ensuring every Static Dreamscapes mix maintains the signature emotional arc and sonic identity.
