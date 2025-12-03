# Song Bank Architecture Plan
**Based on New Naming Convention & Track Flow System**

**Date:** November 18, 2025
**Status:** Planning - Updated with Manual Workflow

---

## 1. Overview

This architecture implements a new song organization system based on **structured naming conventions** and **track flow references**. The goal is to create a queryable song bank that can intelligently suggest tracks for new mixes, while supporting a manual workflow for track creation.

### Key Changes
- **Track template creation:** Auto-generate folder structure for new tracks
- **Manual song addition:** Add songs to `half_1/` and `half_2/` folders without prefixes
- **Smart bank selection:** Pull songs by count OR duration from existing bank
- **Automated rendering:** Render script applies A_/B_ prefixes automatically

---

## 2. Naming Convention Breakdown

### Format: `A_2_5_15a` (Applied at render time, NOT at creation)

| Component | Position | Meaning | Example | Notes |
|-----------|----------|---------|---------|-------|
| **Half** | Prefix | `A_` or `B_` | `A_` | Applied by render script (half_1 → A_, half_2 → B_) |
| **Phase** | 1st digit | `1`, `2`, `3`, `4` | `2` | Which phase (1=Calm, 2=Focus, 3=Uplift, 4=Fade) |
| **Song Number** | 2nd digit | `1-99` | `5` | References entry in track flow doc |
| **Track Number** | 3rd component | `1-999` | `15` | The 15th track ever created (global ID) |
| **Phase Order** | Letter suffix | `a`, `b`, `c`... `f`+ | `a` | Order within the phase (a=1st, b=2nd, etc.) |

### Examples

```
A_1_3_007a.mp3  → First half, Phase 1, Song #3, Track #7, first in phase
B_4_12_156c.mp3 → Second half, Phase 4, Song #12, Track #156, third in phase
A_2_7_089b.mp3  → First half, Phase 2, Song #7, Track #89, second in phase
```

---

## 3. Directory Structure

### Track Template Structure

```
tracks/
├── 15/                           # Previous track
│   ├── image/
│   │   └── 15.jpg
│   ├── video/
│   │   └── 15.mp4
│   ├── half_1/                   # First half songs (will become A_*)
│   │   ├── song_001.mp3
│   │   ├── song_002.mp3
│   │   └── ...
│   ├── half_2/                   # Second half songs (will become B_*)
│   │   ├── song_007.mp3
│   │   ├── song_008.mp3
│   │   └── ...
│   ├── track_flow.md             # Reference to track flow used
│   └── metadata.json             # Track metadata
│
├── 16/                           # NEW: Auto-created by template script
│   ├── image/
│   ├── video/
│   ├── half_1/
│   ├── half_2/
│   ├── track_flow.md
│   └── metadata.json
│
└── 17/                           # Future tracks...
```

### Full Project Structure

```
static-dreamwaves/
├── tracks/                       # NEW: Track-centric organization
│   ├── 001/
│   ├── 002/
│   ├── ...
│   └── 016/
│       ├── image/
│       ├── video/
│       ├── half_1/               # Songs manually added here
│       ├── half_2/               # Songs manually added here
│       ├── track_flow.md
│       └── metadata.json
│
├── song_bank/                    # NEW: Song repository (past tracks)
│   ├── catalog.json              # All songs with metadata
│   ├── by_phase/
│   │   ├── phase_1/
│   │   │   ├── A_1_1_007a.mp3
│   │   │   └── A_1_2_008a.mp3
│   │   ├── phase_2/
│   │   ├── phase_3/
│   │   └── phase_4/
│   └── by_track/
│       ├── 007/
│       │   └── A_1_1_007a.mp3 (symlink)
│       └── 008/
│           └── A_1_2_008a.mp3 (symlink)
│
├── track_flows/                  # NEW: Track flow reference docs
│   ├── 01_neon_rain_calm.md
│   ├── 02_midnight_drive.md
│   └── 04_current_flow.md
│
├── rendered/                     # EXISTING: Final output
│   ├── 15/
│   │   └── output_20251118/
│   │       └── output.mp4
│   └── 16/
│
├── arc_library/                  # LEGACY: Keep for backward compatibility
├── metadata/                     # LEGACY: Keep for backward compatibility
│
└── agent/                        # Python automation
    ├── create_track_template.py # NEW: Create track folder structure
    ├── select_bank_songs.py     # NEW: Select songs from bank
    ├── build_track.py            # NEW: Build complete track with A_/B_
    └── add_to_bank.py            # NEW: Add completed track songs to bank
```

---

## 4. Workflow: Creating a New Track

### Step 1: Create Track Template

```bash
# Auto-creates next track number (16 if 15 exists)
./venv/bin/python3 agent/create_track_template.py

# Or specify track number
./venv/bin/python3 agent/create_track_template.py --track-number 20

# Creates:
# tracks/16/
#   ├── image/
#   ├── video/
#   ├── half_1/
#   ├── half_2/
#   ├── track_flow.md (template)
#   └── metadata.json (template)
```

**Output:**
```
✓ Created track template: tracks/16/
  - image/
  - video/
  - half_1/
  - half_2/
  - track_flow.md
  - metadata.json

Next steps:
1. Add background video: tracks/16/video/16.mp4
2. Add cover image: tracks/16/image/16.jpg
3. Select songs from bank OR add new songs to half_1/ and half_2/
```

### Step 2A: Select Songs from Bank (Optional)

**By Count:**
```bash
# Get 8 songs from bank matching track flow
./venv/bin/python3 agent/select_bank_songs.py \
  --track-number 16 \
  --flow-id 04 \
  --count 8 \
  --output tracks/16/bank_selection.json
```

**By Duration:**
```bash
# Get ~30 minutes of songs from bank
./venv/bin/python3 agent/select_bank_songs.py \
  --track-number 16 \
  --flow-id 04 \
  --duration 30 \
  --output tracks/16/bank_selection.json
```

**Output: `tracks/16/bank_selection.json`**
```json
{
  "track_number": 16,
  "flow_id": "04",
  "selection_criteria": {
    "type": "duration",
    "target": 30,
    "actual": 29.8
  },
  "selected_songs": [
    {
      "source": "song_bank/by_phase/phase_1/A_1_1_007a.mp3",
      "phase": 1,
      "song_number": 1,
      "duration": 4.5,
      "bpm": 72,
      "prompt": "ambient vaporwave hum, soft rain textures"
    },
    {
      "source": "song_bank/by_phase/phase_1/A_1_2_008a.mp3",
      "phase": 1,
      "song_number": 2,
      "duration": 3.8,
      "bpm": 70,
      "prompt": "distant traffic reverb, warm pad layers"
    }
  ],
  "instructions": "Copy selected songs to half_1/ or half_2/ as needed"
}
```

**Manually copy songs:**
```bash
# Review bank_selection.json and copy songs to appropriate half
cp song_bank/by_phase/phase_1/A_1_1_007a.mp3 tracks/16/half_1/
cp song_bank/by_phase/phase_1/A_1_2_008a.mp3 tracks/16/half_1/
```

### Step 2B: Generate New Songs in Suno

1. Open Suno and use prompts from `track_flows/04_current_flow.md`
2. Download new MP3s to `~/Downloads/`
3. Manually organize into halves:
   ```bash
   mv ~/Downloads/new_song_1.mp3 tracks/16/half_1/
   mv ~/Downloads/new_song_2.mp3 tracks/16/half_1/
   mv ~/Downloads/new_song_3.mp3 tracks/16/half_2/
   mv ~/Downloads/new_song_4.mp3 tracks/16/half_2/
   ```

### Step 3: Add Video and Image

```bash
# Add background video
cp ~/path/to/background.mp4 tracks/16/video/16.mp4

# Add cover image
cp ~/path/to/cover.jpg tracks/16/image/16.jpg
```

### Step 4: Build Track (Renders with A_/B_ prefixes)

```bash
# Build complete track - automatically applies A_/B_ prefixes
./venv/bin/python3 agent/build_track.py \
  --track-number 16 \
  --duration 3 \
  --output rendered/16/
```

**What it does:**
1. Reads songs from `tracks/16/half_1/` and `tracks/16/half_2/`
2. Applies A_ prefix to half_1 songs
3. Applies B_ prefix to half_2 songs
4. Orders by filename within each half
5. Builds final mix with FFmpeg crossfades
6. Outputs to `rendered/16/output_<timestamp>/output.mp4`

### Step 5: Add Songs to Bank (After rendering)

```bash
# Add all songs from this track to the bank for future reuse
./venv/bin/python3 agent/add_to_bank.py \
  --track-number 16 \
  --flow-id 04
```

**What it does:**
1. Reads songs from `tracks/16/half_1/` and `tracks/16/half_2/`
2. Renames with proper convention: `A_2_5_016a.mp3`, `B_4_12_016c.mp3`, etc.
3. Copies to `song_bank/by_phase/` and creates symlinks in `song_bank/by_track/`
4. Updates `song_bank/catalog.json` with metadata
5. Links songs to track flow prompts

---

## 5. Track Template Files

### File: `tracks/16/track_flow.md` (Auto-generated template)

```markdown
---
track_number: 16
track_flow_id: null
title: "Track 16"
created: 2025-11-18T17:30:00Z
status: in_progress
---

# Track 16 Flow

## Instructions

1. Update `track_flow_id` to reference a track flow (e.g., "04" for track_flows/04_current_flow.md)
2. OR define custom flow below

## Phase 1 - Calm Intro

Songs for half_1:
- Song #1: [Prompt from track flow or custom]
- Song #2: [Prompt from track flow or custom]

## Phase 2 - Flow Focus

Songs for half_1:
- Song #3: [Prompt from track flow or custom]

## Phase 3 - Uplift Clarity

Songs for half_2:
- Song #7: [Prompt from track flow or custom]

## Phase 4 - Reflective Fade

Songs for half_2:
- Song #12: [Prompt from track flow or custom]
```

### File: `tracks/16/metadata.json` (Auto-generated template)

```json
{
  "track_number": 16,
  "track_flow_id": null,
  "title": "Track 16",
  "created": "2025-11-18T17:30:00Z",
  "status": "in_progress",
  "half_1": {
    "songs": [],
    "total_duration": 0,
    "song_count": 0
  },
  "half_2": {
    "songs": [],
    "total_duration": 0,
    "song_count": 0
  },
  "render_history": [],
  "notes": ""
}
```

---

## 6. Song Bank Catalog Schema

### File: `song_bank/catalog.json`

```json
{
  "version": "1.0",
  "last_updated": "2025-11-18T18:00:00Z",
  "total_songs": 156,
  "songs": {
    "A_1_1_007a": {
      "filename": "A_1_1_007a.mp3",
      "original_filename": "ambient_hum_001.mp3",
      "path_by_phase": "song_bank/by_phase/phase_1/A_1_1_007a.mp3",
      "path_by_track": "song_bank/by_track/007/A_1_1_007a.mp3",
      "breakdown": {
        "half": "A",
        "phase": 1,
        "song_number": 1,
        "track_number": 7,
        "phase_order": "a"
      },
      "source_track": {
        "track_number": 7,
        "flow_id": "01",
        "prompt": "ambient vaporwave hum, soft rain textures, slow city rhythm",
        "theme": "neon rain calm"
      },
      "audio": {
        "duration": 245.7,
        "bpm": 72.3,
        "key": "D minor",
        "brightness": 1842.5,
        "energy": 0.034,
        "mood_tags": ["ambient", "vaporwave", "rain", "calm"]
      },
      "usage": {
        "times_used": 1,
        "last_used": "2025-11-01T14:30:00Z",
        "used_in_tracks": [7]
      },
      "quality_rating": 4.5,
      "added_to_bank": "2025-11-02T10:15:00Z"
    }
  }
}
```

---

## 7. Core Scripts

### 7.1 `agent/create_track_template.py`

**Purpose:** Create folder structure for new track

**Usage:**
```bash
# Auto-detect next track number
./venv/bin/python3 agent/create_track_template.py

# Specify track number
./venv/bin/python3 agent/create_track_template.py --track-number 20

# Use specific track flow
./venv/bin/python3 agent/create_track_template.py --flow-id 04
```

**What it creates:**
- `tracks/N/image/`
- `tracks/N/video/`
- `tracks/N/half_1/`
- `tracks/N/half_2/`
- `tracks/N/track_flow.md` (template or pre-filled from flow)
- `tracks/N/metadata.json`

### 7.2 `agent/select_bank_songs.py`

**Purpose:** Select songs from bank based on criteria

**Usage by Count:**
```bash
# Get 8 songs from bank
./venv/bin/python3 agent/select_bank_songs.py \
  --track-number 16 \
  --flow-id 04 \
  --count 8 \
  --prefer-unused \
  --output tracks/16/bank_selection.json
```

**Usage by Duration:**
```bash
# Get 30 minutes of songs
./venv/bin/python3 agent/select_bank_songs.py \
  --track-number 16 \
  --flow-id 04 \
  --duration 30 \
  --prefer-unused \
  --output tracks/16/bank_selection.json
```

**Selection Logic:**
1. Filter by track flow (matching prompts/theme)
2. Filter by phase progression (follow emotional arc)
3. Prioritize unused or less-used songs if `--prefer-unused`
4. Consider BPM transitions (smooth flow)
5. Match target count or duration

**Output:** JSON file with selected songs and copy instructions

### 7.3 `agent/build_track.py`

**Purpose:** Build final mix with automatic A_/B_ prefixing

**Usage:**
```bash
# Build 3-hour track
./venv/bin/python3 agent/build_track.py \
  --track-number 16 \
  --duration 3 \
  --output rendered/16/

# Build test (5 minutes)
./venv/bin/python3 agent/build_track.py \
  --track-number 16 \
  --duration test \
  --output rendered/16/
```

**Process:**
1. Validate track structure (video, songs exist)
2. Read songs from `half_1/` and `half_2/`
3. Apply phase detection (analyze audio to determine phase 1-4)
4. Apply naming: `half_1/song.mp3` → `A_2_5_016a.mp3`
5. Update `metadata.json` with song list
6. Call FFmpeg to render mix with crossfades
7. Save to `rendered/16/output_<timestamp>/output.mp4`

**Naming Logic:**
```python
# For each song in half_1/
filename = f"A_{phase}_{song_number}_{track_number}{order_letter}.mp3"

# For each song in half_2/
filename = f"B_{phase}_{song_number}_{track_number}{order_letter}.mp3"
```

### 7.4 `agent/add_to_bank.py`

**Purpose:** Add completed track songs to bank for reuse

**Usage:**
```bash
# Add all songs from track 16 to bank
./venv/bin/python3 agent/add_to_bank.py \
  --track-number 16 \
  --flow-id 04

# Add only specific half
./venv/bin/python3 agent/add_to_bank.py \
  --track-number 16 \
  --flow-id 04 \
  --half 1

# Preview without copying
./venv/bin/python3 agent/add_to_bank.py \
  --track-number 16 \
  --flow-id 04 \
  --dry-run
```

**Process:**
1. Read `tracks/16/metadata.json` (contains phase assignments from build)
2. For each song, rename with proper convention
3. Copy to `song_bank/by_phase/{phase}/`
4. Create symlink in `song_bank/by_track/{track_number}/`
5. Update `song_bank/catalog.json`
6. Link to track flow prompts

---

## 8. Example End-to-End Workflow

### Creating Track 16 with mix of bank + new songs

```bash
# Step 1: Create template
./venv/bin/python3 agent/create_track_template.py --flow-id 04
# Output: Created tracks/16/

# Step 2: Get 30 minutes of songs from bank
./venv/bin/python3 agent/select_bank_songs.py \
  --track-number 16 \
  --flow-id 04 \
  --duration 30 \
  --prefer-unused \
  --output tracks/16/bank_selection.json

# Step 3: Review bank_selection.json and copy songs
# (Manual: Copy songs to half_1/ and half_2/ as suggested)

# Step 4: Generate remaining songs in Suno
# (Manual: Download and add to half_1/ and half_2/)

# Step 5: Add video and image
cp ~/Videos/bg_16.mp4 tracks/16/video/16.mp4
cp ~/Images/cover_16.jpg tracks/16/image/16.jpg

# Step 6: Build track (applies A_/B_ automatically)
./venv/bin/python3 agent/build_track.py \
  --track-number 16 \
  --duration 3 \
  --output rendered/16/

# Step 7: Review output
open rendered/16/output_20251118_180000/output.mp4

# Step 8: Add songs to bank for future reuse
./venv/bin/python3 agent/add_to_bank.py \
  --track-number 16 \
  --flow-id 04
```

**Final Result:**
- `rendered/16/output.mp4` - Final 3-hour mix
- `song_bank/` updated with 24 new songs (with A_/B_ naming)
- `tracks/16/metadata.json` - Complete track record
- Ready to create track 17 and reuse songs from track 16

---

## 9. Migration Plan

### Phase 1: Setup Infrastructure (Week 1)
- [ ] Create `tracks/` directory structure
- [ ] Create `song_bank/` directory structure
- [ ] Create `track_flows/` directory
- [ ] Implement `create_track_template.py`
- [ ] Test template creation with tracks/01/

### Phase 2: Build Core Scripts (Week 2)
- [ ] Implement `select_bank_songs.py`
  - [ ] Selection by count
  - [ ] Selection by duration
  - [ ] Smart matching algorithm
- [ ] Implement `build_track.py`
  - [ ] Read from half_1/ and half_2/
  - [ ] Apply A_/B_ prefixes automatically
  - [ ] Phase detection logic
  - [ ] FFmpeg integration
- [ ] Test with mock track

### Phase 3: Bank Management (Week 3)
- [ ] Implement `add_to_bank.py`
- [ ] Create `song_bank/catalog.json` schema
- [ ] Test adding songs to bank
- [ ] Create query utilities (search bank by phase, BPM, etc.)

### Phase 4: Migration & Testing (Week 4)
- [ ] Migrate existing track 15 (or earlier) to new structure
- [ ] Populate initial song bank from past tracks
- [ ] Create track flow documents for past themes
- [ ] End-to-end test: Create track 16 from scratch
- [ ] Documentation and user guides

---

## 10. Benefits of This Approach

### Manual Control
- **No forced imports:** You decide what goes where
- **Flexible workflow:** Mix bank songs + new songs easily
- **Visual organization:** See half_1 and half_2 clearly separated

### Automation Where It Counts
- **Template creation:** No manual folder setup
- **Smart selection:** Get songs by duration or count
- **Automatic naming:** A_/B_ applied at render time
- **Bank integration:** Easy to reuse past work

### Scalability
- **Track-centric:** Each track is self-contained
- **Queryable bank:** Find reusable songs fast
- **Theme matching:** Songs linked to prompts/flows
- **Historical tracking:** See what worked in past tracks

---

## 11. Questions to Resolve

1. **Phase Detection:** Should `build_track.py` auto-detect phase from audio analysis, or read from filename/metadata?
2. **Song Number Assignment:** How to assign song numbers to new tracks (manual edit in metadata.json, or auto-detect from prompt matching)?
3. **Order Letter Assignment:** Should order letters (a, b, c) be assigned automatically based on filename sort, or manually specified?
4. **Bank Selection Algorithm:** What weights for selection? (BPM match 40%, theme match 30%, freshness 30%?)
5. **Quality Ratings:** Manual rating after render, or automated based on usage frequency?

---

**Document Maintained By:** Static Dreamscapes Development Team
**Last Updated:** November 18, 2025
**Status:** Updated per user feedback - Ready for implementation
