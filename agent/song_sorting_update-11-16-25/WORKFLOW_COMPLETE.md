# Complete Song Bank Workflow

**Status**: ✅ Implementation Complete
**Date**: 2025-11-19

## Overview

This document describes the complete end-to-end workflow for creating tracks using the song bank system. All scripts have been implemented and are ready for testing.

---

## System Architecture

### Directory Structure

```
static-dreamwaves/
├── tracks/                      # Track projects
│   └── <number>/               # Individual track folders
│       ├── half_1/             # Songs for first half (no prefixes)
│       ├── half_2/             # Songs for second half (no prefixes)
│       ├── video/              # Background video (<number>.mp4)
│       ├── image/              # Cover art (<number>.jpg)
│       ├── metadata.json       # Track metadata
│       └── bank_selection.json # Selected bank songs (auto-generated)
│
├── song_bank/                  # Centralized song repository
│   ├── tracks/                 # Songs organized by source track
│   │   └── <number>/          # e.g., 016/
│   │       └── A_2_5_016a.mp3 # Named: half_phase_song_track_order
│   ├── track_flows/           # Track flow documents
│   │   └── 04_neon_rain_calm.md
│   └── metadata/
│       ├── song_catalog.json  # Master song index
│       └── prompt_index.json  # Prompt references
│
└── rendered/                   # Final rendered mixes
    └── <number>/
        └── output_<timestamp>/
            └── output.mp4
```

### Song Naming Convention

Bank songs use the format: `A_2_5_016a.mp3`

- `A` = Half (A = first half, B = second half)
- `2` = Phase (1-4: Calm, Flow, Uplift, Reflect)
- `5` = Song number within phase
- `016` = Source track number (zero-padded to 3 digits)
- `a` = Order letter (a, b, c... for variations/versions)

---

## Complete Workflow

### Step 1: Create New Track Template

**Script**: `create_track_template.py`

```bash
# Auto-increment track number (if last is 15, creates 16)
./venv/bin/python3 agent/create_track_template.py

# Or specify track number
./venv/bin/python3 agent/create_track_template.py --track-number 20
```

**What it does**:
- Scans `tracks/` to find next available number
- Creates folder structure: `half_1/`, `half_2/`, `video/`, `image/`
- Generates `metadata.json` with track information
- Creates `README.md` with workflow instructions

**Output**:
```
tracks/16/
├── half_1/          (empty - for songs)
├── half_2/          (empty - for songs)
├── video/           (empty - add 16.mp4)
├── image/           (empty - add 16.jpg)
├── metadata.json    (track metadata)
└── README.md        (instructions)
```

---

### Step 2: Select Songs from Bank (Optional)

**Script**: `select_bank_songs.py`

**Option A: Select by Count**
```bash
# Select 5 songs from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04
```

**Option B: Select by Duration**
```bash
# Select ~30 minutes of songs
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04
```

**What it does**:
- Queries `song_catalog.json` for available songs
- Filters by flow ID (optional) and theme (optional)
- Selects songs matching criteria
- Saves selection to `bank_selection.json`
- Does NOT copy files yet (preview only)

**Output**: `tracks/16/bank_selection.json`

**Execute the Selection** (copy files):
```bash
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

**What execute does**:
- Reads `bank_selection.json`
- Copies selected songs to `half_1/` or `half_2/` based on song's half metadata
- Marks selection as executed

---

### Step 3: Add New Songs Manually

After selecting from bank (or if bank is empty), add new songs:

```bash
# Generate songs in Suno, download to ~/Downloads/

# Move to track folders
mv ~/Downloads/new_song_*.mp3 tracks/16/half_1/
mv ~/Downloads/other_song_*.mp3 tracks/16/half_2/
```

**Important**:
- Songs should NOT have A_ or B_ prefixes at this stage
- Just use descriptive filenames from Suno
- Organize manually into half_1/ and half_2/ as desired

---

### Step 4: Add Video and Image

```bash
# Copy background video
cp ~/path/to/background.mp4 tracks/16/video/16.mp4

# Copy cover art
cp ~/path/to/cover.jpg tracks/16/image/16.jpg
```

---

### Step 5: Build Track

**Script**: `build_track.py`

```bash
# Build 3-hour mix (default)
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# Build 1-hour mix
./venv/bin/python3 agent/build_track.py --track 16 --duration 1

# Build 5-minute test
./venv/bin/python3 agent/build_track.py --track 16 --duration test
```

**What it does**:
1. Reads all songs from `half_1/` (alphabetically sorted)
2. Reads all songs from `half_2/` (alphabetically sorted)
3. Creates temporary `temp_songs/` folder
4. Copies songs with automatic A_/B_ prefixes:
   - `half_1/song1.mp3` → `temp_songs/A_001_song1.mp3`
   - `half_1/song2.mp3` → `temp_songs/A_002_song2.mp3`
   - `half_2/song1.mp3` → `temp_songs/B_001_song1.mp3`
   - etc.
5. Copies prefixed songs to `tracks/16/songs/` (for build_mix.sh)
6. Calls existing `build_mix.sh` script with FFmpeg rendering
7. Generates `tracklist.json` with render metadata
8. Cleans up temporary folders

**Output**:
- `rendered/16/output_<timestamp>/output.mp4`
- `rendered/16/output_<timestamp>/tracklist.json`

**Options**:
- `--keep-temp`: Keep `temp_songs/` folder for debugging

---

### Step 6: Add New Songs to Bank

**Script**: `add_to_bank.py`

```bash
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

**What it does**:
1. Scans `half_1/` and `half_2/` for songs not already in bank
2. For each new song, prompts for metadata:
   - Half (A/B) - defaults to folder location
   - Phase (1-4) - Calm/Flow/Uplift/Reflect
   - Song number within phase
   - Order letter (a-z)
3. Generates bank filename (e.g., `A_2_5_016a.mp3`)
4. Copies to `song_bank/tracks/16/`
5. Runs audio analysis (optional with `--analyze` flag)
6. Updates `song_catalog.json` and `prompt_index.json`

**Interactive Example**:
```
🎵 Song: epic_synthwave_beat.mp3
   Suggested half: A
   Half (A/B) [default: A]: A
   Phase (1=Calm, 2=Flow, 3=Uplift, 4=Reflect): 2
   Song number within phase (e.g., 5): 5
   Order letter (a-z, e.g., 'a' for first, 'b' for second): a

   ✅ Added to bank: A_2_5_016a.mp3
```

**Options**:
- `--analyze`: Run audio analysis with librosa
- `--auto`: Auto-mode with default values (for testing)

---

## Script Reference

### 1. `create_track_template.py`

**Purpose**: Create new track folder structure
**Location**: `agent/create_track_template.py`

**Usage**:
```bash
./venv/bin/python3 agent/create_track_template.py [--track-number N]
```

**Key Functions**:
- `get_next_track_number()` - Auto-increment track number
- `create_track_template(track_number)` - Generate folder structure

---

### 2. `select_bank_songs.py`

**Purpose**: Query and select songs from bank
**Location**: `agent/select_bank_songs.py`

**Usage**:
```bash
# Select by count
./venv/bin/python3 agent/select_bank_songs.py --track N --count 5 [--flow-id 04] [--theme "neon rain"]

# Select by duration
./venv/bin/python3 agent/select_bank_songs.py --track N --duration 30 [--flow-id 04]

# Execute selection (copy files)
./venv/bin/python3 agent/select_bank_songs.py --track N --execute
```

**Key Functions**:
- `select_songs_by_count(catalog, count, flow_id, theme)` - Select N songs
- `select_songs_by_duration(catalog, target_minutes, flow_id, theme)` - Select by duration
- `execute_selection(track_number)` - Copy selected files to track

---

### 3. `build_track.py`

**Purpose**: Build final mix with automatic A_/B_ prefixing
**Location**: `agent/build_track.py`

**Usage**:
```bash
./venv/bin/python3 agent/build_track.py --track N --duration [1|2|3|test] [--keep-temp]
```

**Key Functions**:
- `get_songs_from_half(half_folder)` - Get MP3s from half folder
- `create_temp_prefixed_songs(track_number, half_1_songs, half_2_songs)` - Apply A_/B_ prefixes
- `build_mix(track_number, duration_hours)` - Call FFmpeg render
- `save_tracklist(output_folder, track_number, tracklist, duration_hours)` - Save metadata

---

### 4. `add_to_bank.py`

**Purpose**: Add new songs to bank with metadata
**Location**: `agent/add_to_bank.py`

**Usage**:
```bash
./venv/bin/python3 agent/add_to_bank.py --track N --flow-id ID [--analyze] [--auto]
```

**Key Functions**:
- `get_new_songs_from_track(track_number)` - Find non-banked songs
- `prompt_for_metadata(song_path, suggested_half)` - Interactive metadata entry
- `generate_bank_filename(half, phase, song_num, track_num, order)` - Create bank name
- `add_song_to_bank(song_path, metadata, track_number, flow_id, catalog, prompt_index)` - Add to catalog

---

## Metadata Schemas

### `tracks/<number>/metadata.json`

```json
{
  "track_number": 16,
  "created": "2025-11-19T10:30:00",
  "status": "in_progress",
  "track_flow_id": "04",
  "title": "Track 16",
  "theme": "Neon Rain Calm",
  "duration_target_hours": 3,
  "notes": "Add notes about this track here",
  "bank_songs": {
    "count": 5,
    "total_duration": 1800,
    "sources": ["A_2_5_015a", "B_1_3_014b"]
  },
  "new_songs": {
    "count": 10,
    "total_duration": 3000,
    "files": ["new_song_1.mp3", "new_song_2.mp3"]
  }
}
```

### `tracks/<number>/bank_selection.json`

```json
{
  "track_number": 16,
  "created": "2025-11-19T10:35:00",
  "selection_method": "count",
  "selection_criteria": {
    "count": 5,
    "flow_id": "04",
    "theme": null
  },
  "selected_songs": [
    {
      "track_id": "A_2_5_015a",
      "filename": "A_2_5_015a.mp3",
      "source": "song_bank/tracks/15/A_2_5_015a.mp3",
      "phase": 2,
      "half": "A",
      "duration": 180,
      "bpm": 85,
      "prompt": "Neon rain calm synthwave"
    }
  ],
  "total_songs": 5,
  "total_duration": 900,
  "executed": true,
  "executed_at": "2025-11-19T10:40:00"
}
```

### `song_bank/metadata/song_catalog.json`

```json
{
  "catalog_version": "1.0",
  "last_updated": "2025-11-19T11:00:00",
  "total_tracks": 15,
  "tracks": {
    "A_2_5_016a": {
      "filename": "A_2_5_016a.mp3",
      "path": "song_bank/tracks/16/A_2_5_016a.mp3",
      "original_filename": "epic_synthwave_beat.mp3",
      "source_track": 16,
      "flow_id": "04",
      "naming_breakdown": {
        "half": "A",
        "phase": 2,
        "song_num": 5,
        "track_num": 16,
        "order": "a"
      },
      "audio_analysis": {
        "duration": 180,
        "bpm": 85,
        "brightness": 0.65,
        "energy": 0.72,
        "key": "C#m"
      },
      "added_to_bank": "2025-11-19T11:00:00",
      "track_flow": {
        "flow_id": "04",
        "prompt": "Neon rain calm synthwave"
      }
    }
  }
}
```

---

## Testing the Workflow

### End-to-End Test

```bash
# 1. Create track template
./venv/bin/python3 agent/create_track_template.py
# Output: Created tracks/16/

# 2. Add some test songs manually
echo "test" > tracks/16/half_1/test_song_1.mp3
echo "test" > tracks/16/half_2/test_song_2.mp3

# 3. Add video (use any MP4)
cp test_video.mp4 tracks/16/video/16.mp4

# 4. Build track (test mode - 5 minutes)
./venv/bin/python3 agent/build_track.py --track 16 --duration test --keep-temp
# Should create: rendered/16/output_<timestamp>/output.mp4

# 5. Add songs to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04 --auto
# Should create: song_bank/tracks/16/A_1_1_016a.mp3

# 6. Verify catalog
cat song_bank/metadata/song_catalog.json
# Should show added song

# 7. Create new track and select from bank
./venv/bin/python3 agent/create_track_template.py
./venv/bin/python3 agent/select_bank_songs.py --track 17 --count 2
./venv/bin/python3 agent/select_bank_songs.py --track 17 --execute
# Should copy songs to tracks/17/half_1/ or half_2/
```

---

## Key Implementation Details

### Automatic A_/B_ Prefixing

The prefixing happens **only during render** in `build_track.py`:

1. Songs remain unprefixed in `half_1/` and `half_2/`
2. During build, temporary copies are made with prefixes:
   - `A_001_`, `A_002_`, etc. for half_1 songs
   - `B_001_`, `B_002_`, etc. for half_2 songs
3. Prefixed copies used for FFmpeg render
4. Original files remain unchanged

### Song Selection Intelligence

Current implementation is basic (first N songs). Future enhancements:

- **Phase balancing**: Select mix of phases 1-4
- **BPM matching**: Maintain smooth tempo transitions
- **Theme filtering**: Match songs by theme keywords
- **Energy curve**: Build emotional arc automatically

### Integration with Existing Scripts

The new scripts integrate with existing `build_mix.sh`:

1. `build_track.py` creates `tracks/<num>/songs/` folder
2. Copies A_/B_ prefixed songs to that folder
3. Calls `bash scripts/build_mix.sh <num> <duration>`
4. `build_mix.sh` reads from `tracks/<num>/songs/` as usual
5. Renders to `rendered/<num>/output_<timestamp>/`

---

## Next Steps

### Immediate
- [ ] Test complete workflow end-to-end
- [ ] Verify FFmpeg rendering works with new structure
- [ ] Create example track flow document

### Future Enhancements
- [ ] Integrate full audio analysis (librosa) in `add_to_bank.py`
- [ ] Implement smart song selection (phase balance, BPM matching)
- [ ] Add theme filtering and prompt matching
- [ ] Create web UI for bank management
- [ ] Add track flow document parser
- [ ] Implement automatic emotional arc generation

---

## Files Created

### Python Scripts
- ✅ `agent/create_track_template.py` - Track template generator
- ✅ `agent/select_bank_songs.py` - Bank query and selection
- ✅ `agent/build_track.py` - Mix builder with auto-prefixing
- ✅ `agent/add_to_bank.py` - Bank addition with metadata

### Metadata Structures
- ✅ `song_bank/metadata/song_catalog.json` - Master song index
- ✅ `song_bank/metadata/prompt_index.json` - Prompt references

### Documentation
- ✅ `agent/song_sorting_update-11-16-25/USER_REQUIREMENTS.md` - Original requirements
- ✅ `agent/song_sorting_update-11-16-25/ARCHITECTURE.md` - Initial architecture
- ✅ `agent/song_sorting_update-11-16-25/REVISED_WORKFLOW.md` - Corrected workflow
- ✅ `agent/song_sorting_update-11-16-25/WORKFLOW_COMPLETE.md` - This document

---

## Summary

**Status**: ✅ All core scripts implemented and ready for testing

**Workflow Summary**:
1. Create track template (auto-increment)
2. Select songs from bank (count or duration)
3. Add new songs manually to half_1/half_2
4. Build track with automatic A_/B_ prefixing
5. Add new songs to bank with metadata

**Key Innovation**: Automatic A_/B_ prefixing during render eliminates manual file organization while maintaining proper playback order.
