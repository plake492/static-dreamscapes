# Revised Workflow - Song Bank System

**Updated:** November 18, 2025
**Based on:** User feedback and workflow requirements

---

## Overview

This document outlines the **revised workflow** for creating tracks with a mix of banked songs and new manually-added songs.

### Key Principles
1. **Track template creation** - Auto-generate folder structure
2. **Manual song placement** - User adds songs to `half_1/` and `half_2/` folders (no prefixes)
3. **Bank song selection** - Script pulls songs from bank by count OR duration
4. **Automatic prefixing** - Render script applies A_/B_ prefixes automatically
5. **Post-render banking** - Add new songs to bank after successful render

---

## Workflow Steps

### Step 1: Create Track Template

```bash
# Auto-creates next track number (e.g., if 15 exists, creates 16)
./venv/bin/python3 agent/create_track_template.py
```

**Output:**
```
Created track template: tracks/16/
  ├── half_1/         (empty - for first half songs)
  ├── half_2/         (empty - for second half songs)
  ├── video/          (empty - for background video)
  ├── image/          (empty - for cover art)
  └── metadata.json   (template metadata)

Next steps:
1. Select songs from bank: python agent/select_bank_songs.py --track 16
2. Add new songs manually to half_1/ and half_2/
3. Add video and image assets
4. Build track: python agent/build_track.py --track 16
```

**With custom track number:**
```bash
./venv/bin/python3 agent/create_track_template.py --track-number 20
```

---

### Step 2: Select Songs from Bank

You have two options for pulling songs from the bank:

#### Option A: By Count (number of songs)

```bash
# Select 5 songs from bank for track 16
./venv/bin/python3 agent/select_bank_songs.py \
  --track 16 \
  --count 5 \
  --flow-id 04 \
  --theme "neon rain calm"
```

**Output:**
```
Selected 5 songs from bank for track 16:
  1. song_bank/tracks/007/A_1_1_007a.mp3 → tracks/16/half_1/ (4.5 min, Phase 1)
  2. song_bank/tracks/008/A_1_2_008a.mp3 → tracks/16/half_1/ (3.8 min, Phase 1)
  3. song_bank/tracks/045/A_2_4_045a.mp3 → tracks/16/half_2/ (5.2 min, Phase 2)
  4. song_bank/tracks/098/B_3_8_098b.mp3 → tracks/16/half_2/ (4.1 min, Phase 3)
  5. song_bank/tracks/112/B_4_11_112a.mp3 → tracks/16/half_2/ (6.3 min, Phase 4)

Total duration: 24.0 minutes
Copied to: tracks/16/bank_selection.json

Run this to copy songs:
  ./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

#### Option B: By Duration (target length)

```bash
# Select ~30 minutes of songs from bank for track 16
./venv/bin/python3 agent/select_bank_songs.py \
  --track 16 \
  --duration 30 \
  --flow-id 04 \
  --theme "neon rain calm"
```

**Output:**
```
Selected songs totaling 29.8 minutes from bank for track 16:
  1. song_bank/tracks/007/A_1_1_007a.mp3 → tracks/16/half_1/ (4.5 min, Phase 1)
  2. song_bank/tracks/008/A_1_2_008a.mp3 → tracks/16/half_1/ (3.8 min, Phase 1)
  3. song_bank/tracks/009/A_1_3_009b.mp3 → tracks/16/half_1/ (4.2 min, Phase 1)
  4. song_bank/tracks/045/A_2_4_045a.mp3 → tracks/16/half_2/ (5.2 min, Phase 2)
  5. song_bank/tracks/046/A_2_5_046b.mp3 → tracks/16/half_2/ (4.8 min, Phase 2)
  6. song_bank/tracks/098/B_3_8_098b.mp3 → tracks/16/half_2/ (4.1 min, Phase 3)
  7. song_bank/tracks/112/B_4_11_112a.mp3 → tracks/16/half_2/ (3.2 min, Phase 4)

Total duration: 29.8 minutes (target: 30.0 minutes)
Copied to: tracks/16/bank_selection.json

Run this to copy songs:
  ./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

#### Execute the Copy

```bash
# After reviewing bank_selection.json, execute the copy
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

**What it does:**
- Copies selected songs from `song_bank/` to `tracks/16/half_1/` or `tracks/16/half_2/`
- Songs are copied **without** A_/B_ prefixes at this stage
- Preserves original filenames for now

---

### Step 3: Add New Songs Manually

Generate new songs in Suno for the remaining slots, then manually add them:

```bash
# Download from Suno, then move to appropriate half
mv ~/Downloads/new_ambient_track.mp3 tracks/16/half_1/
mv ~/Downloads/new_focus_track.mp3 tracks/16/half_1/
mv ~/Downloads/new_bright_track.mp3 tracks/16/half_2/
mv ~/Downloads/new_fade_track.mp3 tracks/16/half_2/
```

**Current state of `tracks/16/`:**
```
tracks/16/
  ├── half_1/
  │   ├── A_1_1_007a.mp3              (from bank)
  │   ├── A_1_2_008a.mp3              (from bank)
  │   ├── new_ambient_track.mp3       (manual)
  │   └── new_focus_track.mp3         (manual)
  ├── half_2/
  │   ├── A_2_4_045a.mp3              (from bank)
  │   ├── new_bright_track.mp3        (manual)
  │   └── B_4_11_112a.mp3             (from bank)
  ├── video/ (empty)
  └── image/ (empty)
```

---

### Step 4: Add Video and Image

```bash
# Add background video (required for render)
cp ~/path/to/neon_rain_bg.mp4 tracks/16/video/16.mp4

# Add cover image (optional)
cp ~/path/to/cover_art.jpg tracks/16/image/16.jpg
```

---

### Step 5: Build Track (Auto A_/B_ Prefixing)

```bash
# Build complete 3-hour track
./venv/bin/python3 agent/build_track.py \
  --track 16 \
  --duration 3
```

**What the build script does:**

1. **Reads songs from folders:**
   - `tracks/16/half_1/` → Songs for first half (A_ prefix)
   - `tracks/16/half_2/` → Songs for second half (B_ prefix)

2. **Sorts songs alphabetically within each half:**
   - `half_1/`: A_1_1_007a.mp3, A_1_2_008a.mp3, new_ambient_track.mp3, new_focus_track.mp3
   - `half_2/`: A_2_4_045a.mp3, B_4_11_112a.mp3, new_bright_track.mp3

3. **Temporarily applies A_/B_ prefixes for rendering:**
   - `half_1/` songs → prefixed with `A_`
   - `half_2/` songs → prefixed with `B_`
   - Creates temp files like: `A_001_file.mp3`, `A_002_file.mp3`, `B_001_file.mp3`, etc.

4. **Builds mix with FFmpeg:**
   - Background video: `tracks/16/video/16.mp4`
   - Songs in order: All A_ tracks, then all B_ tracks
   - Crossfades between songs
   - Loops to fill 3 hours

5. **Outputs:**
   - `rendered/16/output_20251118_173000/output.mp4`
   - `rendered/16/output_20251118_173000/ffmpeg_command.txt`
   - `rendered/16/output_20251118_173000/tracklist.json`

**Important:** Original files in `half_1/` and `half_2/` remain **unchanged** (no prefixes added permanently)

---

### Step 6: Add New Songs to Bank (Post-Render)

After successful render, add the NEW songs (not banked ones) to the song bank:

```bash
# Add new songs from track 16 to the bank
./venv/bin/python3 agent/add_to_bank.py \
  --track 16 \
  --flow-id 04
```

**What it does:**

1. **Identifies new songs:**
   - Scans `tracks/16/half_1/` and `tracks/16/half_2/`
   - Filters out songs already in bank (by filename match)
   - New songs: `new_ambient_track.mp3`, `new_focus_track.mp3`, `new_bright_track.mp3`

2. **Prompts for metadata:**
   ```
   Song: new_ambient_track.mp3

   Which phase? (1-4): 1
   Which song number from flow? (1-20): 3
   Position in phase? (a/b/c/d...): c

   Rename to: A_1_3_016c.mp3
   Confirm? (y/n): y
   ```

3. **Adds to bank:**
   - Copies to `song_bank/tracks/016/A_1_3_016c.mp3`
   - Creates symlink in `song_bank/by_phase/phase_1/A_1_3_016c.mp3`
   - Runs audio analysis
   - Updates `song_bank/catalog.json`
   - Links to track flow prompt in `song_bank/prompt_index.json`

4. **Result:**
   - 3 new songs added to bank
   - Available for future track selection
   - Metadata linked to track flow #04

---

## Complete Workflow Summary

```bash
# 1. Create track template (auto-increments from last track)
./venv/bin/python3 agent/create_track_template.py

# 2. Select songs from bank (by count OR duration)
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04
# OR
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04

# 2a. Review selection, then execute copy
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute

# 3. Generate new songs in Suno, download to ~/Downloads/

# 4. Manually move new songs to half_1/ or half_2/
mv ~/Downloads/*.mp3 tracks/16/half_1/

# 5. Add video and image
cp background.mp4 tracks/16/video/16.mp4
cp cover.jpg tracks/16/image/16.jpg

# 6. Build track (auto A_/B_ prefixing during render)
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# 7. After successful render, add new songs to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

## Key Files Generated

### `tracks/16/bank_selection.json`
```json
{
  "track_number": 16,
  "flow_id": "04",
  "selection_method": "count",
  "selection_criteria": {
    "count": 5,
    "theme": "neon rain calm"
  },
  "selected_songs": [
    {
      "source": "song_bank/tracks/007/A_1_1_007a.mp3",
      "destination": "tracks/16/half_1/",
      "phase": 1,
      "song_number": 1,
      "duration": 4.5,
      "bpm": 72,
      "prompt": "ambient vaporwave hum, soft rain textures"
    }
  ],
  "total_duration": 24.0,
  "executed": false
}
```

### `rendered/16/output_<timestamp>/tracklist.json`
```json
{
  "track_number": 16,
  "build_timestamp": "2025-11-18T17:30:00Z",
  "total_duration": 10812,
  "tracks": [
    {
      "position": 1,
      "source": "tracks/16/half_1/A_1_1_007a.mp3",
      "render_name": "A_001_A_1_1_007a.mp3",
      "from_bank": true,
      "bank_track": "007",
      "duration": 270
    },
    {
      "position": 2,
      "source": "tracks/16/half_1/new_ambient_track.mp3",
      "render_name": "A_002_new_ambient_track.mp3",
      "from_bank": false,
      "duration": 245
    }
  ]
}
```

---

## Script Responsibilities

### `create_track_template.py`
- Auto-increment track number (scan `tracks/` for highest number)
- Create folder structure: `half_1/`, `half_2/`, `video/`, `image/`
- Generate template `metadata.json`
- Output next steps for user

### `select_bank_songs.py`
- Query song bank by count OR duration
- Match songs to theme/flow
- Consider phase distribution
- Prioritize unused songs
- Generate `bank_selection.json`
- Execute copy when `--execute` flag is used
- NO prefixing (files copied as-is)

### `build_track.py`
- Read songs from `half_1/` and `half_2/`
- **Temporarily** apply A_/B_ prefixes for rendering
- Sort and order tracks
- Call FFmpeg to build mix with video
- Generate tracklist metadata
- Clean up temp prefixed files
- Leave original files unchanged

### `add_to_bank.py`
- Identify new (non-banked) songs in track folder
- Interactive prompt for phase/song/order metadata
- Rename with proper convention (e.g., `A_1_3_016c.mp3`)
- Copy to song bank
- Run audio analysis
- Update catalog and prompt index

---

## Benefits of This Approach

### For User
- **Simple workflow:** Create template, select from bank, add new songs, build
- **No manual prefixing:** A_/B_ applied automatically during render
- **Flexible selection:** Choose by song count OR duration
- **Clear separation:** Bank songs vs new songs clearly differentiated

### For Automation
- **Clean folder structure:** No mixed states, clear input/output
- **Reusable songs:** Bank grows with each track
- **Traceable lineage:** Know which songs came from bank vs new
- **Metadata preserved:** Track flow links maintained

### For Scalability
- **Template system:** Consistent structure for every track
- **Bank query system:** Find best songs by theme, phase, duration
- **Post-render banking:** Bank only grows after successful renders
- **Version control friendly:** Clean file organization

---

**Document Status:** Ready for implementation
**Next Step:** Implement `create_track_template.py`
