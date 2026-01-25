# Database Schema

SQLite database structure for the LoFi Track Manager.

---

## Overview

**Location:** `./data/tracks.db`
**Type:** SQLite 3
**Tables:** 2 (songs, tracks)
**Size:** ~100KB per 100 songs

---

## Songs Table

Stores individual audio files with metadata and analysis.

### Schema

```sql
CREATE TABLE songs (
    -- Identity
    id TEXT PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    file_path TEXT NOT NULL,

    -- Parsed from filename (e.g., A_1_2_25a.mp3)
    arc_number INTEGER,
    prompt_number INTEGER,
    song_number INTEGER,
    order_marker TEXT,

    -- From Notion document
    track_id TEXT,
    track_title TEXT,
    arc_name TEXT,
    arc_phase INTEGER,
    prompt_text TEXT,
    anchor_phrase TEXT,

    -- Audio analysis (librosa)
    duration_seconds REAL,
    bpm REAL,
    key TEXT,
    energy_level REAL,
    tempo_category TEXT,

    -- For semantic search
    vibe_tags TEXT,          -- JSON array
    mood_keywords TEXT,      -- JSON array
    combined_text TEXT,      -- For embedding generation

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    times_used INTEGER DEFAULT 0,

    -- Usage tracking
    last_used_track_id TEXT,
    last_used_at TIMESTAMP,

    FOREIGN KEY (track_id) REFERENCES tracks(id)
);
```

### Indexes

```sql
CREATE INDEX idx_arc_number ON songs(arc_number);
CREATE INDEX idx_bpm ON songs(bpm);
CREATE INDEX idx_key ON songs(key);
CREATE INDEX idx_track_id ON songs(track_id);
CREATE INDEX idx_filename ON songs(filename);
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | TEXT | UUID | `550e8400-e29b-41d4-a716-446655440000` |
| `filename` | TEXT | Audio filename (unique) | `A_1_2_25a.mp3` |
| `file_path` | TEXT | Absolute path | `/path/to/Tracks/25/Songs/A_1_2_25a.mp3` |
| `arc_number` | INTEGER | Arc number (1-4) | `1` |
| `prompt_number` | INTEGER | Prompt within arc | `2` |
| `song_number` | INTEGER | Song variant | `1` |
| `order_marker` | TEXT | Track + variant | `25a` |
| `track_id` | TEXT | Parent track UUID | `track_uuid` |
| `track_title` | TEXT | Track name | `Midnight Neon CRT Desk` |
| `arc_name` | TEXT | Arc description | `Quiet Night Fade` |
| `arc_phase` | INTEGER | Arc number (duplicate of arc_number) | `1` |
| `prompt_text` | TEXT | Full prompt | `soft ambient pads, minimal motion...` |
| `anchor_phrase` | TEXT | Key phrase | `ambient pads` |
| `duration_seconds` | REAL | Length in seconds | `182.5` |
| `bpm` | REAL | Beats per minute | `85.3` |
| `key` | TEXT | Musical key | `C minor` |
| `energy_level` | REAL | Energy score (0-1) | `0.42` |
| `tempo_category` | TEXT | Tempo classification | `slow`, `medium`, `fast` |
| `vibe_tags` | TEXT | JSON array of vibes | `["calm", "ambient", "night"]` |
| `mood_keywords` | TEXT | JSON array of moods | `["quiet", "serene"]` |
| `combined_text` | TEXT | Concatenated metadata | Used for embeddings |
| `created_at` | TIMESTAMP | Import time | `2025-01-15 10:30:00` |
| `updated_at` | TIMESTAMP | Last update | `2025-01-20 15:45:00` |
| `times_used` | INTEGER | Usage count | `3` |
| `last_used_track_id` | TEXT | Track ID where last used | `26` |
| `last_used_at` | TIMESTAMP | When last used | `2025-01-20 10:30:00` |

---

## Tracks Table

Stores track-level metadata from Notion documents.

### Schema

```sql
CREATE TABLE tracks (
    -- Identity
    id TEXT PRIMARY KEY,
    notion_url TEXT UNIQUE,
    title TEXT NOT NULL,
    output_filename TEXT,
    upload_schedule TEXT,
    duration_target INTEGER DEFAULT 180,

    -- Theme/vibe
    overall_theme TEXT,
    mood_arc TEXT,
    vibe_description TEXT,

    -- SEO
    visible_hashtags TEXT,   -- JSON array
    hidden_tags TEXT,        -- JSON array

    -- Metrics targets
    ctr_target TEXT,
    retention_target TEXT,

    -- Track management
    track_number INTEGER,
    track_folder TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft',

    -- Rendering
    rendered_at TIMESTAMP,
    youtube_url TEXT,

    -- Cached notion content
    notion_content_json TEXT
);
```

### Indexes

```sql
CREATE INDEX idx_track_number ON tracks(track_number);
CREATE INDEX idx_status ON tracks(status);
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | TEXT | UUID | `track-uuid` |
| `notion_url` | TEXT | Notion page URL | `https://notion.so/Track-25-...` |
| `title` | TEXT | Track title | `Midnight Neon CRT Desk` |
| `output_filename` | TEXT | Filename for renders | `midnight-neon-crt-desk-3hr-lofi.mp4` |
| `upload_schedule` | TEXT | Upload date | `2025-01-20` |
| `duration_target` | INTEGER | Target minutes | `180` (3 hours) |
| `overall_theme` | TEXT | Theme description | `Nighttime coding vibes` |
| `mood_arc` | TEXT | Mood progression | `Calm → Focus → Deep work → Wind down` |
| `vibe_description` | TEXT | Detailed vibe | `Chill, ambient, nostalgic...` |
| `visible_hashtags` | TEXT | JSON array | `["lofi", "studymusic"]` |
| `hidden_tags` | TEXT | JSON array | `["chill", "ambient"]` |
| `ctr_target` | TEXT | CTR goal | `8-10%` |
| `retention_target` | TEXT | Retention goal | `45-55%` |
| `track_number` | INTEGER | Track number | `25` |
| `track_folder` | TEXT | Folder path | `Tracks/25` |
| `created_at` | TIMESTAMP | Creation time | `2025-01-15 10:00:00` |
| `updated_at` | TIMESTAMP | Last update | `2025-01-20 12:00:00` |
| `status` | TEXT | Track status | `draft`, `ready`, `published` |
| `rendered_at` | TIMESTAMP | Render time | `2025-01-20 14:00:00` |
| `youtube_url` | TEXT | YouTube link | `https://youtube.com/watch?v=...` |
| `notion_content_json` | TEXT | Cached Notion JSON | Full Notion page content |

---

## Status Values

### Track Status

- **`draft`** - Initial state after import
- **`ready`** - Songs prepared, ready to render
- **`rendering`** - Currently rendering
- **`rendered`** - Render complete
- **`published`** - Uploaded to YouTube

### Tempo Category

- **`slow`** - BPM < 80
- **`medium`** - BPM 80-120
- **`fast`** - BPM > 120

---

## Relationships

```
tracks (1) ----< (many) songs
  └── track_id foreign key
```

One track has many songs.
Each song belongs to one track.

---

## Sample Queries

### Get all songs for a track

```sql
SELECT * FROM songs
WHERE track_id = 'track-uuid'
ORDER BY arc_number, prompt_number;
```

### Find songs by BPM range

```sql
SELECT filename, bpm, key
FROM songs
WHERE bpm BETWEEN 80 AND 100
ORDER BY bpm;
```

### Get most used songs

```sql
SELECT filename, times_used, bpm
FROM songs
WHERE times_used > 0
ORDER BY times_used DESC
LIMIT 10;
```

### Find unused songs

```sql
SELECT filename, arc_number, bpm
FROM songs
WHERE times_used = 0
ORDER BY created_at DESC;
```

### Get track with song count

```sql
SELECT t.title, t.track_number, COUNT(s.id) as song_count
FROM tracks t
LEFT JOIN songs s ON s.track_id = t.id
GROUP BY t.id
ORDER BY t.track_number;
```

### Get songs used in recent tracks

```sql
SELECT filename, last_used_track_id, last_used_at, times_used
FROM songs
WHERE last_used_track_id IN ('24', '25', '26')
ORDER BY last_used_at DESC;
```

### Get songs filtered by usage limits

```sql
-- Songs used more than 5 times
SELECT filename, times_used, last_used_track_id, last_used_at
FROM songs
WHERE times_used > 5
ORDER BY times_used DESC;

-- Songs never used
SELECT filename, arc_number, bpm, key
FROM songs
WHERE times_used = 0 OR times_used IS NULL
ORDER BY created_at DESC;
```

### Get usage statistics by track

```sql
SELECT
    last_used_track_id,
    COUNT(*) as songs_used,
    AVG(times_used) as avg_usage_before
FROM songs
WHERE last_used_track_id IS NOT NULL
GROUP BY last_used_track_id
ORDER BY last_used_track_id;
```

---

## Database Operations

### View Database Statistics

```bash
yarn stats

# Or directly
./scripts/view_db.sh stats
```

### Backup Database

```bash
cp data/tracks.db data/tracks.db.backup
```

### Reset Database

```bash
rm data/tracks.db
yarn init-db
```

**Warning:** This deletes all data!

### Export to CSV

```bash
sqlite3 data/tracks.db <<EOF
.mode csv
.header on
.output songs.csv
SELECT * FROM songs;
.output tracks.csv
SELECT * FROM tracks;
EOF
```

### View Schema

```bash
sqlite3 data/tracks.db .schema
```

---

## Database Maintenance

### Check Integrity

```bash
sqlite3 data/tracks.db "PRAGMA integrity_check;"
```

### Vacuum (Optimize)

```bash
sqlite3 data/tracks.db "VACUUM;"
```

### Get Database Size

```bash
du -h data/tracks.db
```

---

## Performance

### Typical Sizes

- **100 songs:** ~100KB
- **1000 songs:** ~1MB
- **10000 songs:** ~10MB

### Query Performance

- **Get song by ID:** <1ms
- **Search by BPM:** <5ms
- **Get all songs for track:** <10ms
- **Complex joins:** <50ms

---

## Migration Notes

### Schema Changes

Schema is created by `init_schema()` in `src/core/database.py:37-148`

**Safe operations:**
```bash
yarn init-db  # Creates tables if missing, doesn't modify existing
```

**Destructive operations:**
```bash
rm data/tracks.db  # Deletes everything
```

### Usage Tracking Migration

To add usage tracking fields to existing databases:

```bash
# Preview changes (dry run)
python3 scripts/migrate_add_usage_tracking.py --dry-run

# Apply migration
python3 scripts/migrate_add_usage_tracking.py

# Verify migration
python3 scripts/migrate_add_usage_tracking.py --verify
```

After migration, backfill existing usage data:

```bash
# Preview what will be backfilled (dry run)
python3 scripts/backfill_usage_tracking.py --dry-run

# Backfill all tracks
python3 scripts/backfill_usage_tracking.py

# Backfill specific tracks only
python3 scripts/backfill_usage_tracking.py --tracks "24,25,26"
```

**What backfill does:**
- Scans `/Tracks/*/Songs/` directories
- Updates `times_used` counter for each song
- Sets `last_used_track_id` to the most recent track
- Sets `last_used_at` to the track folder creation time

### Adding Indexes

Indexes are automatically created during `init_schema()`. To add new indexes without dropping tables, run:

```bash
sqlite3 data/tracks.db "CREATE INDEX IF NOT EXISTS idx_new_field ON songs(new_field);"
```

---

## See Also

- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - Database commands (`stats`, `init-db`)
- **[09-FILE-STRUCTURE.md](./09-FILE-STRUCTURE.md)** - File organization
- **[07-SYSTEM-OVERVIEW.md](./07-SYSTEM-OVERVIEW.md)** - System architecture
