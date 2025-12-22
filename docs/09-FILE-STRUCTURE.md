# File Organization & Naming Conventions

Complete guide to file structure and naming in the LoFi Track Manager.

---

## Project Structure

```
static-dreamwaves/
├── src/                      # Source code
│   ├── cli/                  # CLI commands
│   ├── core/                 # Database, models, config
│   ├── ingest/               # Notion parser, audio analysis
│   ├── embeddings/           # Embedding generation
│   ├── query/                # Search and matching
│   └── render/               # Rendering utilities
├── data/                     # Data storage
│   ├── tracks.db             # SQLite database
│   ├── embeddings/           # Cached embeddings
│   └── cache/                # Notion document cache
├── config/                   # Configuration
│   └── settings.yaml         # Main config
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── Tracks/                   # Track folders
│   ├── 24/                   # Track 24
│   ├── 25/                   # Track 25
│   └── ...
├── output/                   # Query results
└── Rendered/                 # Rendered videos
```

---

## Track Folder Structure

Each track has its own numbered folder:

```
Tracks/25/
├── Songs/                    # Main audio files
│   ├── A_1_1_25a.mp3        # Arc 1, Prompt 1, variant a
│   ├── A_1_2_25a.mp3        # Arc 1, Prompt 2, variant a
│   ├── B_2_3_25a.mp3        # Arc 2, Prompt 3, variant a
│   └── ...
├── 1/                        # Pre-render audio (prefixed A_)
│   ├── intro.mp3
│   └── ...
├── 2/                        # Pre-render audio (prefixed B_)
│   ├── outro.mp3
│   └── ...
├── Video/                    # Background videos
│   └── 25.mp4               # Looping background (MUST match track number)
├── Image/                    # Track artwork
│   ├── thumbnail.jpg
│   └── banner.jpg
├── Rendered/                 # Rendered output (DEPRECATED - use root /Rendered/)
├── metadata/                 # Track metadata
│   ├── track_info.json      # Snapshot from Notion
│   └── published.json       # Publication info
├── remaining-prompts.md      # Prompts without matches
└── README.md                 # Track overview from Notion
```

---

## Song Filename Convention

### Format

```
{prefix}_{arc}_{prompt}_{variant}.mp3
```

### Components

| Component | Description | Values | Example |
|-----------|-------------|--------|---------|
| `prefix` | Arc letter (optional for main songs) | `A`, `B`, `C`, `D` or none | `A`, `B` |
| `arc` | Arc number | `1`, `2`, `3`, `4` | `1` |
| `prompt` | Prompt number within arc | `1`-`20` | `2` |
| `variant` | Track number + letter | `{N}a`, `{N}b`, `{N}c` | `25a`, `25b` |

### Examples

**Standard songs:**
```
A_1_1_25a.mp3    → Arc 1, Prompt 1, Track 25 variant a
A_1_2_25a.mp3    → Arc 1, Prompt 2, Track 25 variant a
B_2_3_25b.mp3    → Arc 2, Prompt 3, Track 25 variant b
C_3_7_25a.mp3    → Arc 3, Prompt 7, Track 25 variant a
D_4_12_25c.mp3   → Arc 4, Prompt 12, Track 25 variant c
```

**Pre-render songs (folders 1/ and 2/):**
```
intro.mp3        → Moved to Songs/ as A_intro.mp3 during render
transition.mp3   → Moved to Songs/ as A_transition.mp3 during render
outro.mp3        → Moved to Songs/ as B_outro.mp3 during render
```

### Arc Letter Mapping

| Arc Number | Letter |
|------------|--------|
| 1 | A |
| 2 | B |
| 3 | C |
| 4 | D |

### Variant Letters

Use letters `a`, `b`, `c`, `d`, etc. for different variants:
- `25a` - First generation for track 25
- `25b` - Second generation (different take)
- `25c` - Third generation (alternate version)

**Purpose:** Allows multiple versions of the same prompt.

---

## Data Directory Structure

```
data/
├── tracks.db                           # SQLite database
├── embeddings/
│   ├── embeddings.npz                  # Numpy embedding matrix
│   └── metadata.json                   # Embedding metadata
└── cache/
    └── notion_docs/
        ├── 2c8433e578858059.md        # Cached Notion page (by ID)
        └── ...
```

### Embeddings Files

**embeddings.npz:**
```
{
  "embeddings": numpy.array,  # Shape: (N songs, 384 dimensions)
  "song_ids": list            # Corresponding song IDs
}
```

**metadata.json:**
```json
{
  "model": "all-MiniLM-L6-v2",
  "dimension": 384,
  "song_count": 150,
  "generated_at": "2025-01-20T10:30:00"
}
```

---

## Output Directory Structure

```
output/
├── track-24-matches.json     # Query results for track 24
├── track-25-matches.json     # Query results for track 25
└── ...
```

### Query Results Format

```json
{
  "track_title": "Midnight Neon CRT Desk",
  "notion_url": "https://notion.so/...",
  "total_prompts": 13,
  "total_matches": 65,
  "results": {
    "arc_1": [
      {
        "prompt_number": 1,
        "prompt_text": "soft ambient pads...",
        "matches": [
          {
            "filename": "A_1_1_22a.mp3",
            "score": 0.856,
            "similarity": 0.823,
            "bpm": 85.5,
            "key": "C minor",
            "duration": 180
          }
        ]
      }
    ]
  }
}
```

---

## Rendered Output Structure

```
Rendered/
└── 25/
    └── output_20250120_143022/
        ├── midnight-neon-crt-desk-3hr-lofi.mp4    # Final video
        ├── chapters.txt                            # YouTube chapters
        ├── ffmpeg_command.txt                      # Debug: FFmpeg command
        ├── filter_complex.txt                      # Debug: Filter graph
        └── Image/                                  # Copied from track
            ├── thumbnail.jpg
            └── banner.jpg
```

### Filename Source

Output filename comes from (in priority order):
1. **Notion "Filename" field** (e.g., `midnight-neon-crt-desk-3hr-lofi.mp4`)
2. **Sanitized track title** (e.g., `Track-25-Midnight-Neon-CRT-Desk.mp4`)
3. **Generic** (`output.mp4`)

### Chapters File Format

```
# YouTube format (copy to description)
0:00 Group 1 - Arc 1: Quiet Night Fade
5:23 Arc 2: First Light Calm
12:45 Arc 3: Morning Glow
18:30 Arc 4: Full Daylight
```

---

## File Naming Rules

### Track Numbers

- **Use integers only:** `24`, `25`, `999`
- **No leading zeros:** Use `9` not `09`
- **Consistent across:**
  - Folder name: `Tracks/25/`
  - Background video: `Tracks/25/Video/25.mp4`
  - Song variants: `A_1_1_25a.mp3`

### Song Variants

- **Use lowercase letters:** `25a`, `25b`, `25c`
- **Start with `a`:** First variant is always `a`
- **Sequential:** `a`, `b`, `c`, `d`, `e`, ...
- **Same prompt, different variant:**
  - `A_1_1_25a.mp3` - First version of Arc 1, Prompt 1
  - `A_1_1_25b.mp3` - Second version of Arc 1, Prompt 1

### Background Videos

- **MUST match track number:** `Tracks/25/Video/25.mp4` for track 25
- **Format:** MP4 only
- **Naming:** `{track_number}.mp4`
- **Looping:** Should loop seamlessly

### Special Files

| File | Location | Purpose |
|------|----------|---------|
| `remaining-prompts.md` | `Tracks/{N}/` | Prompts without matches |
| `track_info.json` | `Tracks/{N}/metadata/` | Snapshot from Notion |
| `published.json` | `Tracks/{N}/metadata/` | Publication metadata |
| `README.md` | `Tracks/{N}/` | Track overview |

---

## Path Conventions

### Auto-Resolved Paths

When using `--track N`, these paths are auto-resolved:

| What | Pattern | Example (track 25) |
|------|---------|-------------------|
| Songs directory | `./Tracks/{N}/Songs` | `./Tracks/25/Songs` |
| Background video | `./Tracks/{N}/Video/{N}.mp4` | `./Tracks/25/Video/25.mp4` |
| Query results | `./output/track-{N}-matches.json` | `./output/track-25-matches.json` |
| Remaining prompts | `./Tracks/{N}/remaining-prompts.md` | `./Tracks/25/remaining-prompts.md` |

### Custom Paths

You can override with explicit parameters:

```bash
# Use custom songs directory
yarn import-songs --notion-url "..." --songs-dir ./custom/songs

# Use custom query output
yarn query --track 25 --notion-url "..." --output ./custom/results.json

# Use custom render output
yarn render --track 25 --duration 3 --output ./custom/video.mp4
```

---

## Directory Creation

### Auto-Created Directories

These are created automatically when needed:

- `data/` - Created by `init-db`
- `data/embeddings/` - Created by `generate-embeddings`
- `data/cache/notion_docs/` - Created by Notion parser
- `output/` - Created by `query`
- `Tracks/{N}/Songs/` - Created by `scaffold-track`

### Manual Creation Needed

These should be created manually:

- `Tracks/{N}/Video/` - Add background video here
- `Tracks/{N}/Image/` - Add artwork here
- `Tracks/{N}/1/` - Optional pre-render audio
- `Tracks/{N}/2/` - Optional pre-render audio

---

## File Size Reference

### Typical Sizes

| File Type | Size Range | Example |
|-----------|------------|---------|
| Song (MP3) | 3-8 MB | 5 MB per 3-min song |
| Background video | 10-100 MB | 30 MB for 20-sec loop |
| Rendered video (1 hr) | 200-500 MB | 300 MB typical |
| Rendered video (3 hr) | 600-1500 MB | 900 MB typical |
| Database | 100 KB - 10 MB | 1 MB per 1000 songs |
| Embeddings | 1-10 MB | 5 MB per 1000 songs |

---

## Best Practices

### Organization

1. **One track per folder** - Don't mix tracks
2. **Consistent numbering** - Use same number everywhere
3. **Clean variants** - Remove unused variant letters
4. **Backup before render** - Copy Songs/ folder before rendering

### Naming

1. **Follow convention strictly** - Parser expects exact format
2. **No spaces in filenames** - Use underscores or hyphens
3. **Lowercase extensions** - `.mp3` not `.MP3`
4. **Descriptive variants** - Use `a` for AI-gen, `b` for tweaked, etc.

### Storage

1. **Keep source files** - Don't delete original songs
2. **Archive old renders** - Move to `archive/` folder
3. **Clean cache periodically** - Delete old Notion cache
4. **Backup database** - `cp data/tracks.db data/tracks.db.backup`

---

## Common Issues

### "Background video not found"

**Cause:** Video filename doesn't match track number
```
❌ Tracks/25/Video/background.mp4
✅ Tracks/25/Video/25.mp4
```

### "Could not parse filename"

**Cause:** Filename doesn't match convention
```
❌ arc1_prompt2.mp3
❌ A-1-2-25a.mp3
❌ A_1_2.mp3
✅ A_1_2_25a.mp3
```

### "Song not found in database"

**Cause:** Song not imported yet
```bash
# Solution: Import the track
yarn import-songs --track 25 --notion-url "..."
```

---

## Migration & Cleanup

### Rename Songs in Bulk

```bash
# Go to track folder
cd Tracks/25/Songs/

# Rename pattern (example)
for file in arc_*.mp3; do
  # Parse and rename to convention
  # (implement custom logic here)
done
```

### Clean Old Renders

```bash
# Remove old render outputs (keep latest)
cd Rendered/25/
ls -t | tail -n +2 | xargs rm -rf
```

### Archive Old Tracks

```bash
# Move completed tracks to archive
mkdir -p archive
mv Tracks/24 archive/
```

---

## See Also

- **[TRACK_CREATION_GUIDE.md](./TRACK_CREATION_GUIDE.md)** - Creating tracks
- **[08-DATABASE.md](./08-DATABASE.md)** - Database structure
- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - Commands reference
