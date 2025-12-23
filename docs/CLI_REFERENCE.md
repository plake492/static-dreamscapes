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
- [track-duration](#track-duration) - Calculate track duration
- [prepare-render](#prepare-render) - Prepare songs for rendering
- [render](#render) - Render final video
- [post-render](#post-render) - Import rendered songs to database
- [mark-published](#mark-published) - Mark track as published
- [stats](#stats) - Show database statistics
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
yarn query --track <N> --notion-url <URL>
```

### Options
| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `--track`, `-t` | number | No | - | Track number (auto-generates output filename) |
| `--notion-url`, `-n` | string | Yes | - | Notion document URL for new track |
| `--output`, `-o` | string | No | `./output/track-{N}-matches.json` or `./output/query-results.json` | Output JSON file |
| `--duration`, `-d` | number | No | 180 | Target duration in minutes |
| `--songs-per-arc` | number | No | 11 | Songs per arc |
| `--min-similarity` | number | No | 0.6 | Minimum similarity score (0.0-1.0) |
| `--top-k`, `-k` | number | No | 5 | Number of matches per prompt |
| `--config` | string | No | `./config/settings.yaml` | Path to config file |

### Examples
```bash
# Standard 3-hour track query
yarn query --track 25 --notion-url "https://notion.so/..."

# 1-hour track
yarn query --track 25 --notion-url "https://notion.so/..." --duration 60

# Get 10 songs per prompt
yarn query --track 25 --notion-url "https://notion.so/..." --top-k 10

# High-quality matches only (70%+ similarity)
yarn query --track 25 --notion-url "https://notion.so/..." --min-similarity 0.7

# Custom output location
yarn query --track 25 --notion-url "https://notion.so/..." --output ./custom/results.json
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

### Output Files
- **Video:** `Rendered/{N}/output_{timestamp}/{filename-from-notion}.mp4`
- **Chapters:** `Rendered/{N}/output_{timestamp}/chapters.txt`
- **Debug:** `Rendered/{N}/output_{timestamp}/ffmpeg_command.txt`
- **Filter:** `Rendered/{N}/output_{timestamp}/filter_complex.txt`
- **Image:** `Rendered/{N}/output_{timestamp}/Image/` (copied from track)

### Requirements
- Background video at `Tracks/{N}/Video/{N}.mp4`
- Songs in `Tracks/{N}/Songs/`
- Track imported to database (for filename lookup)

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

## mark-published

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

```bash
yarn scaffold-track --track 25 --notion-url "URL"
yarn query --track 25 --notion-url "URL"
yarn prepare-render --track 25
yarn import-songs --track 25 --notion-url "URL"
# Add background video
yarn render --track 25 --duration test
yarn render --track 25 --duration 3
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
