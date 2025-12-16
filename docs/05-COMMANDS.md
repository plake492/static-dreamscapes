# Command Reference

Complete reference for all LoFi Track Manager commands.

---

## 📋 Command Overview

### Setup & Database
- [`init-db`](#init-db) - Initialize database
- [`generate-embeddings`](#generate-embeddings) - Generate semantic embeddings

### Import & Analysis
- [`import-songs`](#import-songs) - Import tracks from Notion
- [`import:force`](#importforce) - Force re-import tracks

### Query & Search
- [`query`](#query) - Find matching songs for new track
- [`gaps`](#gaps) - Analyze playlist gaps

### Track Management
- [`scaffold-track`](#scaffold-track) - Create track folder structure
- [`track-duration`](#track-duration) - Calculate track duration
- [`prepare-render`](#prepare-render) - Prepare songs for rendering
- [`post-render`](#post-render) - Import rendered songs
- [`publish`](#publish) - Mark track as published

### Statistics
- [`stats`](#stats) - View song statistics
- [`stats:songs`](#statssongs) - Detailed song statistics
- [`stats:tracks`](#statstracks) - Track overview

### Utilities
- [`version`](#version) - Show version info
- [`help`](#help) - Show help

---

## Setup & Database

### `init-db`

Initialize the SQLite database.

**Usage:**
```bash
yarn init-db
```

**What it does:**
- Creates `data/tracks.db`
- Sets up songs, tracks, arcs tables
- Creates indexes for performance

**When to use:**
- First time setup
- After deleting database

---

### `generate-embeddings`

Generate semantic embeddings for all songs in database.

**Usage:**
```bash
yarn generate-embeddings

# Force regenerate all
yarn generate-embeddings --force
```

**Options:**
- `--force`, `-f` - Regenerate all embeddings

**What it does:**
- Loads all songs from database
- Generates 384-dimensional vectors
- Saves to `data/embeddings/embeddings.npz`
- Creates metadata file

**When to use:**
- After importing tracks
- After `post-render`
- When adding songs to library

**Output:**
```
🎨 Generating Embeddings

Processing 89 songs...
  1/89: B_1_3_19d.mp3
  2/89: A_2_6_19a.mp3
  ...

✅ Generated embeddings for 89 songs!
Saved to: data/embeddings/embeddings.npz
```

---

## Import & Analysis

### `import-songs`

Import a track from Notion with audio analysis.

**Usage:**
```bash
yarn import-songs \
  --notion-url "https://notion.so/Track-9" \
  --songs-dir "./Tracks/9/Songs"
```

**Required:**
- `--notion-url`, `-n` - Notion document URL
- `--songs-dir`, `-s` - Directory with audio files

**What it does:**
- Fetches Notion document
- Parses prompts and arcs
- Analyzes each audio file (BPM, key, duration)
- Adds to database
- Skips existing songs automatically

**Duplicate handling:**
- Skips songs already in database
- Use `import:force` to re-analyze

**Output:**
```
📥 Importing Track from Notion

Notion URL: https://notion.so/Track-9
Songs directory: ./Tracks/9/Songs

Parsing Notion document...
Track: Night Shift Coding Vol 2
Arcs: 4

Analyzing audio files...
  ✓ 1_1_45a.mp3 (Arc 1, BPM: 95.3, Duration: 222s)
  ✓ 1_2_46a.mp3 (Arc 1, BPM: 93.8, Duration: 289s)
  ...

✅ Imported 43 songs!
```

---

### `import:force`

Force re-import and re-analyze existing tracks.

**Usage:**
```bash
yarn import:force \
  --notion-url "https://notion.so/Track-9" \
  --songs-dir "./Tracks/9/Songs"
```

**Difference from `import-songs`:**
- Re-analyzes existing songs
- Updates database records
- Useful after audio file changes

---

## Query & Search

### `query`

Find matching songs from library for a new track.

**Usage:**
```bash
yarn query \
  --notion-url "https://notion.so/Track-20" \
  --output "./output/playlists/track-20-matches.json"
```

**Required:**
- `--notion-url`, `-n` - New track's Notion URL
- `--output`, `-o` - Output JSON file path

**Optional:**
- `--top-k`, `-k` - Matches per prompt (default: 5)
- `--min-similarity` - Minimum similarity score (default: 0.6)
- `--target-duration`, `-d` - Target duration in minutes (default: 180)
- `--songs-per-arc` - Songs per arc (default: 11)

**What it does:**
- Parses new track from Notion
- Searches library for each prompt
- Scores matches using multi-factor algorithm
- Outputs JSON with top matches

**Output JSON structure:**
```json
{
  "track_title": "Neon Rain Focus Flow",
  "total_prompts": 19,
  "total_matches": 27,
  "results": {
    "arc_1": [
      {
        "prompt_number": 1,
        "prompt_text": "Ambient synth pad...",
        "matches": [
          {
            "filename": "B_1_3_19d.mp3",
            "score": 0.786,
            "similarity": 0.782,
            "bpm": 95.3,
            "key": "D minor",
            "arc": 1,
            "duration": 222
          }
        ]
      }
    ]
  }
}
```

**Example:**
```bash
# Basic query
yarn query \
  --notion-url "URL" \
  --output "./output/playlists/track-20.json"

# More matches per prompt
yarn query \
  --notion-url "URL" \
  --output "file.json" \
  --top-k 10

# Higher quality threshold
yarn query \
  --notion-url "URL" \
  --output "file.json" \
  --min-similarity 0.7
```

---

### `gaps`

Analyze query results to identify which prompts need new generation.

**Usage:**
```bash
yarn gaps "./output/playlists/track-20-matches.json"

# Custom threshold
yarn gaps "./output/playlists/track-20-matches.json" --min-similarity 0.7
```

**Required:**
- Playlist JSON file path

**Optional:**
- `--min-similarity`, `-m` - Minimum acceptable score (default: 0.6)

**What it does:**
- Analyzes query results
- Identifies prompts with no matches
- Identifies prompts with low-quality matches
- Provides generation recommendations

**Output:**
```
Gap Analysis Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Category                     ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ No matches (need generation) │    10 │      52.6% │
│ Low quality (< 70%)          │     1 │       5.3% │
│ Good matches (≥ 70%)         │     8 │      42.1% │
└──────────────────────────────┴───────┴────────────┘

❌ Prompts Needing New Generation:
arc_1:
  1. Ambient synth pad intro, deep bass line...
  2. Distant traffic reverb, warm pad layers...

💡 Recommendation:
Generate approximately 11 new songs
This represents 57.9% of the track
```

---

## Track Management

### `scaffold-track`

Create track folder structure from Notion document.

**Usage:**
```bash
yarn scaffold-track \
  --track-number 20 \
  --notion-url "https://notion.so/Track-20"
```

**Required:**
- `--track-number`, `-t` - Track number
- `--notion-url`, `-n` - Notion URL

**What it does:**
- Creates `Tracks/{N}/` folder
- Creates subdirectories: Songs, Rendered, metadata
- Creates README.md with track info
- Creates metadata.json

**Created structure:**
```
Tracks/20/
├── Songs/          # Place songs here
├── Rendered/       # Place rendered tracks here
├── metadata/       # Metadata files
│   └── track.json
└── README.md       # Track info from Notion
```

---

### `track-duration`

Calculate total duration of all songs in a track.

**Usage:**
```bash
# By track number
yarn track-duration --track 20

# By directory
yarn track-duration --songs-dir "./Tracks/20/Songs"
```

**Options:**
- `--track`, `-t` - Track number
- `--songs-dir`, `-s` - Songs directory path

**What it does:**
- Scans directory for audio files
- Analyzes duration of each file
- Groups by arc
- Shows total duration

**Output:**
```
⏱️  Calculating Track Duration

Scanning: ./Tracks/20/Songs

Duration Summary
┏━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┓
┃ Arc   ┃ Songs ┃ Duration ┃ Minutes ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━┩
│ Arc 1 │ 12    │ 2272s    │ 37.9m   │
│ Arc 2 │ 13    │ 3217s    │ 53.6m   │
│ Arc 3 │ 11    │ 2524s    │ 42.1m   │
│ Arc 4 │ 10    │ 2536s    │ 42.3m   │
└───────┴───────┴──────────┴─────────┘

Total Duration:
  • 10551 seconds
  • 175.9 minutes
  • 2.93 hours
```

---

### `prepare-render`

Copy matched songs from library to track folder for rendering.

**Usage:**
```bash
yarn prepare-render \
  --track 20 \
  --playlist "./output/playlists/track-20-matches.json"

# Move instead of copy
yarn prepare-render \
  --track 20 \
  --playlist "file.json" \
  --move
```

**Required:**
- `--track`, `-t` - Track number
- `--playlist`, `-p` - Query results JSON

**Options:**
- `--copy/--move` - Copy (default) or move files

**What it does:**
- Reads query results
- Finds best match for each prompt
- Copies/moves files to `Tracks/{N}/Songs/`
- Shows summary by arc

**Output:**
```
🎬 Preparing Track for Render

Track: 20

Found 9 songs to copy

  ✓ B_1_3_19d.mp3 (arc_1, prompt 3)
  ✓ A_2_6_19a.mp3 (arc_2, prompt 1)
  ...

✅ Prepared 9 songs for rendering

      Songs by Arc
┏━━━━━━━┳━━━━━━━┓
┃ Arc   ┃ Songs ┃
┡━━━━━━━╇━━━━━━━┩
│ arc_1 │     3 │
│ arc_2 │     4 │
└───────┴───────┘
```

---

### `post-render`

Import rendered songs back to library for future reuse.

**Usage:**
```bash
yarn post-render --track 20

# Custom directory
yarn post-render \
  --track 20 \
  --rendered-dir "./custom/path"
```

**Required:**
- `--track`, `-t` - Track number

**Optional:**
- `--rendered-dir`, `-r` - Custom rendered directory

**What it does:**
- Scans `Tracks/{N}/Rendered/` for audio
- Parses filenames
- Analyzes audio (BPM, key, duration)
- Adds to database (skips duplicates)

**Output:**
```
📥 Importing Rendered Songs

Track: 20

Found 15 audio files

  ✓ A_1_1_20a.mp3 (Arc 1, BPM: 95.3)
  ⊘ B_2_6_13c.mp3 (already in database)
  ...

✅ Imported 12 new songs
Skipped 3 existing songs

💡 Next step: Regenerate embeddings
   yarn generate-embeddings
```

---

### `publish`

Mark track as published with YouTube URL.

**Usage:**
```bash
yarn publish \
  --track 20 \
  --youtube-url "https://youtube.com/watch?v=..."

# With custom date
yarn publish \
  --track 20 \
  --youtube-url "URL" \
  --date "2025-01-15"
```

**Required:**
- `--track`, `-t` - Track number
- `--youtube-url`, `-u` - YouTube video URL

**Optional:**
- `--date`, `-d` - Publish date (YYYY-MM-DD, default: today)

**What it does:**
- Updates track status to PUBLISHED
- Stores YouTube URL
- Increments usage count for all songs
- Creates `published.json` metadata

**Output:**
```
📺 Marking Track as Published

Track: 20
YouTube URL: https://youtube.com/watch?v=...

✓ Updated track record
✓ Incremented usage count for 46 songs
✓ Saved metadata: ./Tracks/20/metadata/published.json

✅ Track marked as published successfully!

Track       20
YouTube     https://youtube.com/watch?v=...
Published   2025-12-06
Songs Used  46
```

---

## Statistics

### `stats`

View song statistics.

**Usage:**
```bash
yarn stats
```

**Output:**
```
📊 Song Statistics

Total songs in database: 89

Most Used Songs:
┏━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Filename       ┃ Uses   ┃ Arc   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ B_2_6_13c.mp3  │ 3      │ Arc 2 │
│ A_2_6_19a.mp3  │ 2      │ Arc 2 │
└────────────────┴────────┴───────┘
```

---

### `stats:songs`

Detailed song statistics.

**Usage:**
```bash
yarn stats:songs

# Limit results
yarn stats:songs --limit 20
```

---

### `stats:tracks`

Track overview.

**Usage:**
```bash
yarn stats:tracks
```

**Output:**
```
📊 Track Statistics

Total tracks in database: 2

                  All Tracks
┏━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Number ┃ Title          ┃ Status ┃ Duration ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ 9      │ Night Shift    │ draft  │ 180 min  │
│ 13     │ TRACK 13       │ draft  │ 180 min  │
└────────┴────────────────┴────────┴──────────┘
```

---

## Utilities

### `version`

Show system version information.

**Usage:**
```bash
yarn version
```

---

### `help`

Show all available commands.

**Usage:**
```bash
yarn help
```

---

## Database Viewing Scripts

### `view_db.sh`

View database contents directly.

**Usage:**
```bash
# View all songs
./scripts/view_db.sh songs

# View all tracks
./scripts/view_db.sh tracks

# View songs in specific arc
./scripts/view_db.sh arc 2

# Quick stats
./scripts/view_db.sh stats

# Open SQLite shell
./scripts/view_db.sh shell
```

---

## Command Cheat Sheet

```bash
# Setup
yarn init-db
yarn generate-embeddings

# Import
yarn import-songs --notion-url "URL" --songs-dir "PATH"
yarn import:force --notion-url "URL" --songs-dir "PATH"

# Query & Analyze
yarn query --notion-url "URL" --output "FILE"
yarn gaps "FILE"

# Track Management
yarn scaffold-track --track-number N --notion-url "URL"
yarn prepare-render --track N --playlist "FILE"
yarn post-render --track N
yarn publish --track N --youtube-url "URL"

# Stats
yarn stats
yarn stats:tracks
yarn track-duration --track N

# Database
./scripts/view_db.sh stats
./scripts/view_db.sh songs
```

---

## Related Documentation

- [Workflow Guide](./04-WORKFLOW.md) - Complete workflow
- [Duplicate Prevention](./06-DUPLICATES.md) - How duplicates work
- [Troubleshooting](./10-TROUBLESHOOTING.md) - Common issues

---

**Need more help?** Check the [FAQ](./11-FAQ.md)!
