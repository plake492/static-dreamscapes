# CLI Reference

Complete reference for all CLI commands in the LoFi Track Manager.

---

## Table of Contents

- [init-db](#init-db) - Initialize database
- [import-songs](#import-songs) - Import songs from directory
- [generate-embeddings](#generate-embeddings) - Generate semantic embeddings
- [query](#query) - Find matching songs for track
- [gaps](#gaps) - Analyze playlist gaps
- [scaffold-track](#scaffold-track) - Create track folder structure
- [stage-rename](#stage-rename) - Auto-rename files in Staging folder
- [disperse](#disperse) - Distribute files from Staging to folders 1 and 2
- [consolidate](#consolidate) - Consolidate folders 1 and 2 to Songs with prefixes
- [process](#process) - Disperse and consolidate in one command
- [reset-track](#reset-track) - Reset a track by clearing database and files
- [track-duration](#track-duration) - Calculate track duration
- [prepare-render](#prepare-render) - Prepare songs for rendering
- [render](#render) - Render final video
- [post-render](#post-render) - Import rendered songs to database
- [generate-description](#generate-description) - Generate YouTube description with chapters
- [stats](#stats) - Show database statistics
- [audit-usage](#audit-usage) - Audit and fix song usage tracking
- [batch-import](#batch-import) - Batch import from Notion folder
- [version](#version) - Show version

---

## init-db

Initialize the database schema.

### Usage
```bash
yarn init-db
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | string | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Initialize database with default config
yarn init-db

# Use custom config
yarn init-db --config ./custom/config.yaml
```

### Output
Displays database status with song and track counts.

---

## import-songs

Import songs from a directory with Notion metadata.

### Usage
```bash
yarn import-songs --track <N> --notion-url <URL>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | * | - | Track number (auto-resolves to `./Tracks/{N}/Songs`) |
| `--notion-url`, `-n` | string | Yes | - | Notion document URL |
| `--songs-dir`, `-s` | string | No | `./Tracks/{N}/Songs` | Directory containing audio files |
| `--force` | boolean | No | false | Force re-analysis of existing songs |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

\* Either `--track` or `--songs-dir` is required

### Examples
```bash
# Standard import (auto-resolves to ./Tracks/25/Songs)
yarn import-songs --track 25 --notion-url "https://notion.so/..."

# Custom songs directory
yarn import-songs --notion-url "https://notion.so/..." --songs-dir ./my-songs

# Force re-analysis of existing songs
yarn import-songs --track 25 --notion-url "https://notion.so/..." --force
```

### What It Does
1. Parses Notion document for track metadata and prompts
2. Scans directory for audio files (.mp3, .wav)
3. Analyzes audio (BPM, key, duration, energy)
4. Matches songs to prompts based on filename convention
5. Stores everything in database
6. Validates prompts for forbidden technical phrases

### Output
- Track metadata summary
- Table of imported songs
- Warning if forbidden phrases found in prompts

---

## generate-embeddings

Generate semantic embeddings for all songs in the database.

### Usage
```bash
yarn generate-embeddings
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force`, `-f` | boolean | false | Regenerate all embeddings |
| `--config` | string | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Generate embeddings for new songs only
yarn generate-embeddings

# Force regenerate all embeddings
yarn generate-embeddings --force
```

### What It Does
1. Loads all songs from database
2. Generates 384-dimensional semantic embeddings using sentence transformers
3. Saves embeddings to `./data/embeddings/embeddings.npz`
4. Saves metadata to `./data/embeddings/metadata.json`

### When to Run
- After importing new songs
- When changing embedding models
- Before running queries (first-time setup)

---

## query

Find matching songs from library for a new track.

### Usage
```bash
# If track already imported to database
yarn query --track <N>

# If track not yet imported
yarn query --track <N> --notion-url <URL>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | No* | - | Track number (auto-generates output filename) |
| `--notion-url`, `-n` | string | No* | From DB | Notion document URL (optional if track exists in DB) |
| `--output`, `-o` | string | No | `./output/track-{N}-matches.json` or `./output/query-results.json` | Output JSON file |
| `--duration`, `-d` | number | No | 180 | Target duration in minutes |
| `--songs-per-arc` | number | No | 11 | Songs per arc |
| `--min-similarity` | number | No | 0.6 | Minimum similarity score (0.0-1.0) |
| `--top-k`, `-k` | number | No | 5 | Number of matches per prompt |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

**\*Either `--track` or `--notion-url` must be provided.** If track exists in database, `--notion-url` is auto-loaded.

### Examples
```bash
# Track already imported - simplest usage
yarn query --track 37

# Track not yet imported - provide Notion URL
yarn query --track 37 --notion-url "https://notion.so/..."

# 1-hour track
yarn query --track 25 --duration 60

# Get 10 songs per prompt
yarn query --track 25 --top-k 10

# High-quality matches only (70%+ similarity)
yarn query --track 25 --min-similarity 0.7

# Custom output location
yarn query --track 25 --output ./custom/results.json
```

### What It Does
1. Parses Notion document to extract prompts
2. Generates embeddings for each prompt
3. Searches library using semantic similarity
4. Ranks matches by similarity and other factors
5. Saves results to JSON file
6. Shows contributing tracks table

### Output File Format
```json
{
  "track_title": "...",
  "notion_url": "...",
  "total_prompts": 13,
  "total_matches": 65,
  "results": {
    "arc_1": [
      {
        "prompt_number": 1,
        "prompt_text": "...",
        "matches": [
          {
            "filename": "A_1_1_22a.mp3",
            "score": 0.856,
            "similarity": 0.823,
            "bpm": 85.5,
            "key": "C minor",
            "duration": 180,
            "times_used": 3,
            "last_used_track": "26",
            "last_used_at": "2025-12-15T10:30:00"
          }
        ]
      }
    ]
  }
}
```

**Usage tracking fields:**
- `times_used` - Number of times this song has been used
- `last_used_track` - Track ID where song was last used
- `last_used_at` - Timestamp of last usage (ISO 8601 format)

### Typical Workflow

```bash
# First time for a new track:
# 1. Import track from Notion
yarn scaffold-track --track 37 --notion-url "https://notion.so/..."

# 2. Query for matches (no URL needed anymore)
yarn query --track 37

# Subsequent queries for the same track:
# Just use the track number - Notion URL is stored in database
yarn query --track 37
```

---

## gaps

Analyze playlist to identify prompts needing new song generation.

### Usage
```bash
yarn gaps <playlist-file>
```

### Arguments
| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `playlist` | string | Yes | Path to query results JSON file |

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--min-similarity`, `-m` | number | 0.6 | Minimum acceptable similarity score |

### Examples
```bash
# Analyze gaps with default threshold
yarn gaps ./output/track-25-matches.json

# Use higher quality threshold
yarn gaps ./output/track-25-matches.json --min-similarity 0.7
```

### What It Does
1. Loads query results
2. Identifies prompts with no matches
3. Identifies prompts with low-quality matches
4. Calculates recommendation for new songs to generate

### Output
- Summary table: no matches, low quality, good matches
- List of prompts needing generation
- List of low-quality matches
- Recommendation for how many songs to generate

---

## scaffold-track

Create track folder structure from Notion document.

### Usage
```bash
yarn scaffold-track --track <N> --notion-url <URL>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--track-number` | number | No | - | Alias for `--track` (backward compatible) |
| `--notion-url`, `-n` | string | Yes | - | Notion document URL |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Create track 25 folder structure
yarn scaffold-track --track 25 --notion-url "https://notion.so/..."

# Using backward-compatible alias
yarn scaffold-track --track-number 25 --notion-url "https://notion.so/..."
```

### What It Creates
```
Tracks/{N}/
├── Staging/            # Unformatted files for batch renaming
├── 1/                  # Pre-render audio folder (prefixed A_)
├── 2/                  # Pre-render audio folder (prefixed B_)
├── Songs/              # Main songs directory
├── Video/              # Background video location
├── Image/              # Track artwork
├── Rendered/           # Rendered outputs
├── metadata/
│   └── track_info.json # Track metadata snapshot
└── README.md           # Track overview
```

### Notes
- Creates a **snapshot** of track metadata
- Later commands fetch fresh data from Notion
- Safe to re-run (will prompt for confirmation if folder exists)

---

## stage-rename

Auto-rename unformatted audio files in the Staging folder according to the track's naming convention.

### Usage
```bash
yarn stage-rename --track <N> [--dry-run]
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--dry-run`, `-d` | boolean | No | false | Preview without renaming files |

### Examples
```bash
# Preview rename for track 31
yarn stage-rename --track 31 --dry-run

# Execute rename
yarn stage-rename --track 31
```

### What It Does
1. Scans `Tracks/{N}/Staging/` for audio files
2. Separates formatted files (already named correctly) from unformatted files
3. Reads the Notion doc to determine arc structure and prompt ranges
4. Finds the next available `arc_prompt` combination
5. Renames all unformatted files to `{arc}_{prompt}_{track}{letter}.ext`
6. Auto-increments letters: a, b, c... z, aa, ab... az, ba...
7. Files stay in Staging/ for review

### Naming Logic
- **Already formatted files** are skipped (e.g., `1_1_31a.mp3`)
- **Next arc_prompt** is determined by:
  1. Finding highest arc_prompt in Songs/ and Staging/
  2. Reading Notion doc to find next valid prompt in sequence
  3. If arc is complete, moves to next arc's first prompt
- **All unformatted files** get the SAME arc_prompt prefix
- **Letters** increment for each file: a, b, c...

### Example
```
Input (Staging/):
  - already_formatted_3_8_31p.mp3 (skipped)
  - song1.mp3
  - song2.mp3
  - song (1).mp3

Output (Staging/):
  - 3_8_31p.mp3 (unchanged)
  - 3_9_31a.mp3 (renamed from song1.mp3)
  - 3_9_31b.mp3 (renamed from song2.mp3)
  - 3_9_31c.mp3 (renamed from song (1).mp3)
```

### Requirements
- Track must be scaffolded with `scaffold-track`
- Notion doc cache must exist at `data/cache/notion_docs/`
- Staging/ directory must exist at `Tracks/{N}/Staging/`

---

## disperse

Distribute files from Staging/ evenly into folders 1/ and 2/, split per prompt number.

### Usage
```bash
yarn disperse --track <N> [--dry-run]
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--dry-run`, `-d` | boolean | No | false | Preview without moving files |

### Examples
```bash
# Preview dispersion for track 31
yarn disperse --track 31 --dry-run

# Execute dispersion
yarn disperse --track 31
```

### What It Does
1. Scans `Tracks/{N}/Staging/` for formatted audio files
2. Groups files by `(arc, prompt)` combination
3. For each prompt group, splits files evenly:
   - First half → folder `1/`
   - Second half → folder `2/`
   - If odd count, folder `1/` gets the extra file
4. Moves files from Staging/ to their destination folders

### Dispersion Logic
Files are split **per prompt**, not globally:
- **Prompt 1_1** (4 files): 2 → folder 1, 2 → folder 2
- **Prompt 1_2** (5 files): 3 → folder 1, 2 → folder 2 (odd, so 1 gets extra)
- **Prompt 2_1** (3 files): 2 → folder 1, 1 → folder 2

### Example
```
Input (Staging/):
  - 1_1_31a.mp3
  - 1_1_31b.mp3
  - 1_1_31c.mp3
  - 1_2_31a.mp3
  - 1_2_31b.mp3

Output:
  Folder 1/:
    - 1_1_31a.mp3 (first 2 of prompt 1_1)
    - 1_1_31b.mp3
    - 1_2_31a.mp3 (first 1 of prompt 1_2)

  Folder 2/:
    - 1_1_31c.mp3 (last 1 of prompt 1_1)
    - 1_2_31b.mp3 (last 1 of prompt 1_2)
```

### Use Case
Dispersing files allows you to render the track in two halves for variety, then consolidate them with different prefixes (A_ and B_) for the final render.

---

## consolidate

Consolidate songs from folders 1/ and 2/ into Songs/ with A_ and B_ prefixes.

### Usage
```bash
yarn consolidate [--track <N>] [--dry-run] [--copy]
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | No | - | Process only a specific track number |
| `--dry-run`, `-d` | boolean | No | false | Preview without processing files |
| `--copy`, `-c` | boolean | No | false | Copy files instead of moving |
| `--base-dir`, `-b` | string | No | `./Tracks` | Base directory containing track folders |

### Examples
```bash
# Preview consolidation for all tracks
yarn consolidate --dry-run

# Consolidate specific track (moves files by default)
yarn consolidate --track 31

# Copy files instead of moving (keeps originals)
yarn consolidate --track 31 --copy

# Process all tracks
yarn consolidate
```

### What It Does
1. Scans `Tracks/{N}/1/` and `Tracks/{N}/2/` for audio files
2. Prepends prefixes:
   - Files from `1/` → prepend `A_`
   - Files from `2/` → prepend `B_`
3. Moves (or copies) to `Tracks/{N}/Songs/`
4. **Default behavior**: MOVES files (deletes from 1/ and 2/)
5. **With --copy**: Keeps originals in 1/ and 2/

### Example
```
Input:
  Tracks/31/1/:
    - 1_1_31a.mp3
    - 1_1_31b.mp3

  Tracks/31/2/:
    - 1_1_31c.mp3
    - 1_2_31a.mp3

Output (Tracks/31/Songs/):
  - A_1_1_31a.mp3 (from 1/)
  - A_1_1_31b.mp3 (from 1/)
  - B_1_1_31c.mp3 (from 2/)
  - B_1_2_31a.mp3 (from 2/)
```

### Use Case
The A_ and B_ prefixes allow you to identify which half of the track each song came from, useful for analyzing rendering results and managing variety in your final track composition.

### Output
- Progress bar showing tracks being processed
- Summary table: files moved/copied, files skipped, errors
- Skips files that already exist in Songs/

---

## process

Disperse and consolidate in one command. Combines `disperse` and `consolidate` into a single streamlined workflow.

### Usage
```bash
yarn process --track <N> [--dry-run]
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--dry-run`, `-d` | boolean | No | false | Preview without moving files |

### Examples
```bash
# Preview the complete workflow
yarn process --track 31 --dry-run

# Execute disperse + consolidate
yarn process --track 31
```

### What It Does
1. **Phase 1 - Disperse:** Moves files from `Staging/` → `1/` and `2/`
   - Groups files by (arc, prompt)
   - Splits each group evenly between folders 1 and 2
   - If odd count, folder 1 gets the extra file
2. **Phase 2 - Consolidate:** Moves files from `1/` and `2/` → `Songs/`
   - Adds `A_` prefix to files from folder 1
   - Adds `B_` prefix to files from folder 2

### Example Output
```
🔄 Disperse & Consolidate for Track 31
======================================================================

📦 Phase 1: Dispersing from Staging/ → 1/ and 2/
----------------------------------------------------------------------
   Found 5 formatted file(s) in Staging/

   Prompt 3_9 (5 files):
      → Folder 1: 3 file(s)
      → Folder 2: 2 file(s)

📦 Phase 2: Consolidating from 1/ and 2/ → Songs/
----------------------------------------------------------------------
   Found 3 file(s) in 1/
   Found 2 file(s) in 2/

   From 1/ (A_ prefix): 3 file(s)
   From 2/ (B_ prefix): 2 file(s)

======================================================================

✅ Complete!
   Dispersed 5 file(s)
   Consolidated 5 file(s)
```

### Use Case
Perfect for the staging workflow when you've finished generating all songs for a prompt (or multiple prompts). Instead of running `disperse` then `consolidate` separately, run `process` once to complete both steps.

**Typical workflow:**
```bash
# Generate songs → drop in Staging/
yarn stage-rename --track 31

# Process them in one command
yarn process --track 31

# Repeat for more prompts...
```

### Benefits
- **Faster workflow** - One command instead of two
- **Less typing** - Fewer commands to remember
- **Atomic operation** - Both phases complete or neither does
- **Clear output** - See both phases in one summary

---

## reset-track

Reset a track by clearing songs from database and deleting files. Useful for test tracks or starting over.

### Usage
```bash
yarn reset-track --track <N> [--dry-run]
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number to reset |
| `--dry-run`, `-d` | boolean | No | false | Preview without deleting anything |

### Examples
```bash
# Preview what will be deleted
yarn reset-track --track 9999 --dry-run

# Actually reset the track
yarn reset-track --track 9999
```

### What It Does
1. Removes songs from database (where filename contains track number)
2. Deletes files from `Tracks/{N}/Songs/`
3. Deletes files from `Tracks/{N}/Staging/`
4. Deletes files from `Tracks/{N}/1/`
5. Deletes files from `Tracks/{N}/2/`
6. Deletes all render sessions from `Rendered/{N}/`

### What Is Preserved
- Track folder structure (`Tracks/{N}/`)
- Metadata files (`track_info.json`, etc.)
- Video and Image folders
- `README.md` and other documentation

### Output
```
🔄 Resetting Track 9999
======================================================================

Reset Plan:
======================================================================

📊 Database:
   15 song(s) will be removed from database

📁 /Users/.../Tracks/9999/Songs/
   12 file(s) will be deleted
      • 1_1_9999a.mp3
      • 1_2_9999a.mp3
      • 2_1_9999a.mp3
      ...

📁 /Users/.../Tracks/9999/Staging/
   3 file(s) will be deleted
      • audio.mp3
      • generated.mp3
      • test.mp3

📁 /Users/.../Rendered/9999/
   2 render session(s) will be deleted
      • output_20260105_143022/
      • output_20260104_091533/
======================================================================

⚠️  WARNING: This action cannot be undone!
Reset track 9999? [y/N]: y

✓ Removed 15 song(s) from database
✓ Deleted 12 file(s) from Songs/
✓ Deleted 3 file(s) from Staging/
✓ Deleted 2 render session(s)
✓ Removed empty Rendered/9999/ directory

✅ Track 9999 has been reset
```

### Use Case
Perfect for test tracks where you want to completely start over, or when you need to reimport a track with different settings without leaving old data behind.

### Safety Features
- Dry-run mode for safe preview
- Confirmation prompt before deletion
- Clear summary of what will be deleted
- Only deletes files related to the specified track

---

## track-duration

Calculate total duration of songs in a track.

### Usage
```bash
yarn track-duration --track <N>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | * | - | Track number |
| `--songs-dir`, `-s` | string | * | `./Tracks/{N}` | Songs directory |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

\* Either `--track` or `--songs-dir` is required

### Examples
```bash
# Calculate duration for track 25 (scans entire Tracks/25/ recursively)
yarn track-duration --track 25

# Custom directory
yarn track-duration --songs-dir ./my-songs
```

### What It Does
1. Recursively scans directory for audio files (.mp3, .wav)
2. Analyzes duration of each file
3. Groups by arc if filename matches convention
4. Calculates total duration
5. Shows loop calculations for common video lengths

### Output
- List of all files with durations (MM:SS)
- Duration by arc table
- Total duration in hours/minutes/seconds
- Loop calculations (15 min, 30 min, 1 hr, 1.5 hr, 3 hr)

---

## prepare-render

Prepare track for rendering by organizing matched songs into track folder.

### Usage
```bash
yarn prepare-render --track <N>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--results`, `-p` | string | No | `./output/track-{N}-matches.json` | Path to query results JSON file |
| `--playlist` | string | No | - | Alias for `--results` (backward compatible) |
| `--copy/--move` | boolean | No | true | Copy files (default) or move them |
| `--duration`, `-d` | number | No | - | Target duration in minutes (auto-selects songs) |
| `--skip-recent-tracks` | number | No | - | Skip songs used in last N tracks |
| `--max-usage` | number | No | - | Skip songs used more than X times |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Standard prepare (auto-resolves to ./output/track-25-matches.json)
yarn prepare-render --track 25

# Use custom results file
yarn prepare-render --track 25 --results ./custom/results.json

# Move files instead of copying
yarn prepare-render --track 25 --move

# Auto-select songs for 3-hour duration
yarn prepare-render --track 25 --duration 180

# Skip songs used in last 2 tracks (prevents recent repetition)
yarn prepare-render --track 25 --skip-recent-tracks 2

# Skip songs used more than 5 times (prevents overuse)
yarn prepare-render --track 25 --max-usage 5

# Combine filters for maximum variety
yarn prepare-render --track 25 --skip-recent-tracks 2 --max-usage 5

# Backward-compatible --playlist parameter
yarn prepare-render --track 25 --playlist ./output/track-25-matches.json
```

### What It Does
1. Loads query results JSON
2. Finds source files in database
3. Applies usage filters (if specified):
   - Skips songs used in recent tracks
   - Skips songs exceeding usage limit
4. Copies/moves matched songs to `Tracks/{N}/Songs/`
5. Updates usage tracking for each song (times_used, last_used_track_id, last_used_at)
6. Generates `remaining-prompts.md` with unfilled prompts
7. Shows summary by arc

### With --duration Option
Intelligently selects songs to fill target duration:
- Distributes duration evenly across arcs
- Takes multiple matches per prompt as needed
- Stops when target duration is reached

### Output
- Songs by arc table
- Count of prepared songs
- Location: `Tracks/{N}/Songs/`
- Created: `Tracks/{N}/remaining-prompts.md`

---

## render

Render track by concatenating songs with crossfades over looping background video.

### Usage
```bash
yarn render --track <N> --duration <test|auto|hours>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--duration`, `-d` | string | No | "auto" | Duration: "test" (5min), "auto" (all songs), or hours (e.g., "3", "0.5") |
| `--volume`, `-v` | number | No | 1.75 | Volume multiplier |
| `--crossfade` | number | No | 5 | Crossfade duration in seconds |
| `--output`, `-o` | string | No | Auto-generated | Custom output path |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# 5-minute test render
yarn render --track 25 --duration test

# 3-hour render
yarn render --track 25 --duration 3

# 1-hour render
yarn render --track 25 --duration 1

# 30-minute render
yarn render --track 25 --duration 0.5

# Use all songs (auto duration)
yarn render --track 25 --duration auto

# Custom volume and crossfade
yarn render --track 25 --duration 3 --volume 2.0 --crossfade 8

# Custom output path
yarn render --track 25 --duration 3 --output ./my-videos/track.mp4
```

### What It Does
1. Prepends files from `1/` and `2/` folders (with A_ and B_ prefixes)
2. Loads all MP3 files from `Tracks/{N}/Songs/`
3. Analyzes song durations using ffprobe
4. Generates chapters based on arc changes
5. Builds FFmpeg command with crossfades
6. Loops background video to match audio duration
7. Applies volume boost and fade in/out
8. Renders final video
9. **Automatically generates YouTube description** with chapter titles from Notion

### Output Files
- **Video:** `Rendered/{N}/output_{timestamp}/{filename-from-notion}.mp4`
- **Chapters:** `Rendered/{N}/output_{timestamp}/chapters.txt` (detailed timestamps)
- **YouTube Description:** `Rendered/{N}/output_{timestamp}/youtube-description.txt` ✨ **NEW**
- **Debug:** `Rendered/{N}/output_{timestamp}/ffmpeg_command.txt`
- **Filter:** `Rendered/{N}/output_{timestamp}/filter_complex.txt`
- **Image:** `Rendered/{N}/output_{timestamp}/Image/` (copied from track)

### Requirements
- Background video at `Tracks/{N}/Video/{N}.mp4`
- Songs in `Tracks/{N}/Songs/`
- Track imported to database (for filename lookup)
- **For YouTube description:** Notion doc must include `## 6 CHAPTER TITLES` section (optional, but recommended)

### Duration Options
| Value | Behavior |
|-------|----------|
| `test` | Render 5-minute test |
| `auto` | Use total duration of all songs |
| `3` | 3 hours (10800 seconds) |
| `1` | 1 hour (3600 seconds) |
| `0.5` | 30 minutes (1800 seconds) |

### Chapters Format
YouTube-compatible timestamps with arc markers:
```
0:00 Group 1 - Arc 1: Quiet Night Fade
5:23 Arc 2: First Light Calm
12:45 Arc 3: Morning Glow
18:30 Arc 4: Full Daylight
```

---

## post-render

Import rendered songs back to the database for future reuse.

### Usage
```bash
yarn post-render --track <N>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--rendered-dir`, `-r` | string | No | `./Tracks/{N}/Rendered` | Rendered songs directory |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Import rendered songs for track 25
yarn post-render --track 25

# Custom rendered directory
yarn post-render --track 25 --rendered-dir ./my-rendered
```

### What It Does
1. Scans rendered directory for audio files
2. Parses filenames to extract metadata
3. Analyzes audio (BPM, key, duration)
4. Adds to database with usage_count=0
5. Skips files already in database

### Output
- Count of imported songs
- Count of skipped songs
- Suggestion to regenerate embeddings

---

## generate-description

> **Note**: YouTube description is now automatically generated during `yarn render`. This standalone command is still available if you need to regenerate the description separately.

Generate a formatted YouTube description with chapters, ready to copy/paste.

### Usage
```bash
yarn generate-description --track <N>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--notion-url`, `-n` | string | No | From DB | Notion document URL (auto-loads from database) |
| `--output`, `-o` | string | No | `./Tracks/{N}/youtube-description.txt` | Output file path |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Auto-Generated During Render

The YouTube description is automatically generated when you run `yarn render`. It will be saved to:
```
Rendered/{N}/output_{timestamp}/youtube-description.txt
```

Along with:
- The rendered video file
- `chapters.txt` (detailed chapter timestamps)
- `ffmpeg_command.txt` (render command used)
- Copy of the Image folder

### Manual Generation

Use this command if you need to regenerate the description separately:

```bash
# Generate description for track 37
yarn generate-description --track 37
```

### Notion Format Required

Your Notion doc must include a CHAPTER TITLES section:
```markdown
## 6 CHAPTER TITLES
- Pre-Dawn Stillness — Cycle I
- First Light Calm — Cycle I
- Morning Clarity — Cycle I
- Soft Morning Drift — Cycle I
- Pre-Dawn Stillness — Cycle II
- First Light Calm — Cycle II
- Morning Clarity — Cycle II
- Soft Morning Drift — Cycle II
```

### Output Format
```
[Vibe description from Notion]

Best for:
Late-night coding and development
Studying and deep focus
Writing and creative work
Quiet night productivity

Aesthetic:
[Mood arc from Notion]

Chapters
00:00 Neon Night Entry — Cycle I
14:11 Locked-In Focus Flow — Cycle I
34:16 Midnight Drift — Cycle I
45:47 Rainy Fade — Cycle I
01:20:13 Neon Night Entry — Cycle II
01:44:35 Locked-In Focus Flow — Cycle II
02:18:31 Midnight Drift — Cycle II
02:33:06 Rainy Fade — Cycle II

#lofi #synthwave #codingmusic
```

---

## mark-published

> **⚠️ DEPRECATED**: This command is not currently in use.

Mark track as published with YouTube URL and increment usage counts.

### Usage
```bash
yarn mark-published --track <N> --youtube-url <URL>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | Yes | - | Track number |
| `--youtube-url`, `-u` | string | Yes | - | YouTube video URL |
| `--date`, `-d` | string | No | Today | Published date (YYYY-MM-DD) |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Mark track as published
yarn mark-published --track 25 --youtube-url "https://youtube.com/watch?v=..."

# With custom date
yarn mark-published --track 25 --youtube-url "https://youtube.com/..." --date 2025-01-15
```

### What It Does
1. Updates track record with YouTube URL and published date
2. Increments usage count for all songs in track
3. Saves metadata to `Tracks/{N}/metadata/published.json`

### Output
- Confirmation of track update
- Count of songs with incremented usage
- Summary table with track details

---

## stats

Show statistics about songs or tracks.

### Usage
```bash
yarn stats <songs|tracks>
```

### Arguments
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `type` | string | No | "songs" | Type: "songs" or "tracks" |

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit`, `-l` | number | 10 | Number of results to show |
| `--config` | string | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Show song statistics (default)
yarn stats

# Show song statistics with limit
yarn stats songs --limit 20

# Show track statistics
yarn stats tracks
```

### Song Statistics
- Total songs in database
- Most used songs table (filename, times used, BPM, arc)
- Unused songs table

### Track Statistics
- Total tracks in database
- All tracks table (number, title, status, duration target)

---

## audit-usage

Audit song usage by scanning all track folders and updating the database with accurate usage counts.

### Usage
```bash
yarn audit-usage [--dry-run]
```

### Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--base-dir`, `-b` | string | `./Tracks` | Base directory containing track folders |
| `--dry-run`, `-d` | boolean | false | Preview without updating database |
| `--config` | string | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Audit and update usage tracking
yarn audit-usage

# Preview what would be updated (dry run)
yarn audit-usage --dry-run

# Use custom tracks directory
yarn audit-usage --base-dir ./my-tracks
```

### What It Does
1. Scans all track folders (excludes tracks >= 999)
2. Finds the highest track number
3. Scans each track's Songs folder for audio files
4. Counts how many times each song is used across all tracks
5. Calculates "tracks ago" from the highest track number
6. Identifies discrepancies between database and actual usage
7. Updates database with correct values:
   - `times_used` - Total usage count
   - `last_used_track_id` - Most recent track where used
   - `updated_at` - Timestamp

### Output
- Summary: unique songs found, total usages
- Discrepancies table showing:
  - Filename
  - Database count vs. actual count
  - Last track used
  - How many tracks ago
- Top 10 most used songs with usage statistics
- Songs found in folders but not in database

### When to Use
- After manually copying songs between tracks
- When usage tracking seems incorrect
- Before running `prepare-render` with usage filters
- To verify database integrity
- After importing old tracks

### Example Output
```
🔍 Auditing Song Usage

Found 36 tracks (highest: Track 36)
Scanning Songs folders...

✓ Scanned 36 track folders

Found 245 unique songs with 892 total usages

Found 15 songs with incorrect usage counts:

┌────────────────────┬──────────┬────────┬────────────┬────────────┐
│ Filename           │ DB Count │ Actual │ Last Track │ Tracks Ago │
├────────────────────┼──────────┼────────┼────────────┼────────────┤
│ A_1_1_22a.mp3     │ 3        │ 5      │ Track 35   │ 1          │
│ B_2_3_24b.mp3     │ 2        │ 4      │ Track 33   │ 3          │
└────────────────────┴──────────┴────────┴────────────┴────────────┘

Updating database...

✅ Updated 245 songs in database

Top 10 Most Used Songs:

┌────────────────────┬────────────┬────────────┬────────────┐
│ Filename           │ Times Used │ Last Used  │ Tracks Ago │
├────────────────────┼────────────┼────────────┼────────────┤
│ B_1_1_1001b.mp3   │ 7          │ Track 36   │ 0          │
│ A_1_2_16a.mp3     │ 6          │ Track 35   │ 1          │
└────────────────────┴────────────┴────────────┴────────────┘
```

---

## batch-import

Batch import all tracks from a Notion folder.

### Usage
```bash
yarn batch-import --folder-id <ID>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--folder-id`, `-f` | string | Yes | - | Notion folder/page ID containing track pages |
| `--base-dir`, `-d` | string | No | `./Tracks` | Base directory for track folders |
| `--skip-existing/--reimport` | boolean | No | true | Skip tracks already in database |
| `--yes`, `-y` | boolean | No | false | Skip confirmation prompt |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Batch import all tracks from Notion folder
yarn batch-import --folder-id "abc123..."

# Force reimport of existing tracks
yarn batch-import --folder-id "abc123..." --reimport

# Skip confirmation
yarn batch-import --folder-id "abc123..." --yes

# Custom base directory
yarn batch-import --folder-id "abc123..." --base-dir ./my-tracks
```

### What It Does
1. Fetches all child pages from Notion folder
2. Filters pages starting with "Track" and extracts track numbers
3. Shows preview table of tracks found
4. Imports each track (skip existing if flag set)
5. Shows summary of imported, skipped, and errors

### Requirements
- Tracks must be direct children of the folder
- Page titles must start with "Track {N}"
- Songs directory must exist at `{base-dir}/{N}/Songs`

### Output
- Preview table of tracks to import
- Progress for each track
- Summary: imported, skipped, errors

---

## version

Show version information.

### Usage
```bash
yarn version-info
```

### Output
Displays current version of LoFi Track Manager.

---

## Global Options

All commands support these options:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | string | `./config/settings.yaml` | Path to configuration file |

---

## Common Patterns

### Auto-Path Resolution with --track

Most commands support `--track` parameter for automatic path resolution:

```bash
# These paths are auto-resolved from --track 25:
import-songs --track 25    # → Scans ./Tracks/25/Songs
query --track 25          # → Saves to ./output/track-25-matches.json
prepare-render --track 25 # → Uses ./output/track-25-matches.json
render --track 25         # → Uses ./Tracks/25/Songs and ./Tracks/25/Video/25.mp4
```

### Backward-Compatible Aliases

Some parameters have aliases for backward compatibility:

- `--track-number` → `--track` (scaffold-track)
- `--playlist` → `--results` (prepare-render)

### Standard Workflow

#### Option 1: Query from Song Bank
```bash
# 1. Create track structure
yarn scaffold-track --track 25 --notion-url "URL"

# 2. Query song bank for matches
yarn query --track 25 --notion-url "URL"

# 3. Prepare matched songs for rendering
yarn prepare-render --track 25

# 4. Import songs to database
yarn import-songs --track 25 --notion-url "URL"

# 5. Add background video to Tracks/25/Video/25.mp4

# 6. Render
yarn render --track 25 --duration test  # Test render
yarn render --track 25 --duration 3     # Full render
```

#### Option 2: Generate New Songs with Staging
```bash
# 1. Create track structure
yarn scaffold-track --track 25 --notion-url "URL"

# 2. Generate songs with Suno and add to Staging/
cp *.mp3 Tracks/25/Staging/

# 3. Auto-rename files
yarn stage-rename --track 25 --dry-run  # Preview
yarn stage-rename --track 25            # Execute

# 4. Disperse to folders 1 and 2
yarn disperse --track 25 --dry-run      # Preview
yarn disperse --track 25                # Execute

# 5. Consolidate with prefixes to Songs/
yarn consolidate --track 25 --dry-run   # Preview
yarn consolidate --track 25             # Execute

# 6. Import songs to database
yarn import-songs --track 25 --notion-url "URL"

# 7. Add background video to Tracks/25/Video/25.mp4

# 8. Render
yarn render --track 25 --duration test  # Test render
yarn render --track 25 --duration 3     # Full render
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | SQLite database location | `./data/tracks.db` |
| `NOTION_API_TOKEN` | Notion integration token | From config file |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (command failed) |

---

## See Also

- **[TRACK_CREATION_GUIDE.md](./TRACK_CREATION_GUIDE.md)** - Quick start guide
- **[PROMPT_CRAFTING_GUIDE.md](./PROMPT_CRAFTING_GUIDE.md)** - Writing good prompts
- **[README.md](../README.md)** - Project overview
