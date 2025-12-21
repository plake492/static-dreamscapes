# Static Dreamwaves - Agent Context Document

**Last Updated:** 2024-12-14
**Project Type:** LoFi Music Track Generator & Manager
**Current Phase:** Phase 6 Complete - Full workflow operational

---

## Project Overview

Static Dreamwaves is an AI-powered system for creating long-form LoFi/Synthwave/Vaporwave music tracks (typically 3 hours) designed for focus, coding, and relaxation. The system manages the entire workflow from AI music generation prompts to final rendered video tracks with background visuals.

### Key Capabilities

- **Semantic Song Matching**: Use AI embeddings to find songs that match creative prompts
- **Duration-Aware Selection**: Intelligently select enough songs to fill target durations (e.g., 3 hours)
- **Notion Integration**: Pull track metadata and prompts from Notion workspace
- **Batch Import**: Import multiple tracks from Notion in one operation
- **Video Rendering**: Automated ffmpeg-based rendering with crossfades and looping backgrounds
- **Track Management**: Complete CLI toolset for managing songs, tracks, and rendering workflow

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Notion Workspace                      │
│  - Track metadata (title, mood arcs, prompts)               │
│  - Organized by track number folders                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ batch-import / import-songs
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     SQLite Database                          │
│  - tracks: Track metadata and Notion URLs                   │
│  - songs: Song files with metadata and embeddings           │
│  - arcs: Arc definitions linked to tracks                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Semantic Search Engine                     │
│  - sentence-transformers embeddings                         │
│  - Cosine similarity matching                               │
│  - Duration-aware selection algorithm                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ prepare-render
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Track Preparation                         │
│  - Copy matched songs to Tracks/{N}/Songs/                  │
│  - Generate remaining-prompts.md                            │
│  - Organize by arc and prompt number                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ render
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FFmpeg Rendering                          │
│  - Concatenate songs with crossfades                        │
│  - Loop background video                                    │
│  - Apply volume boost, fades                                │
│  - Output: Rendered/{track}/output_{timestamp}/             │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### tracks
- `id`: INTEGER PRIMARY KEY
- `title`: TEXT - Full track title
- `notion_url`: TEXT - Link to Notion page
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### songs
- `id`: INTEGER PRIMARY KEY
- `track_id`: INTEGER - Foreign key to tracks
- `title`: TEXT - Song title from metadata
- `artist`: TEXT - Artist name
- `file_path`: TEXT - Path to audio file
- `arc_name`: TEXT - Which arc this song belongs to (e.g., "Arc 1")
- `prompt_number`: INTEGER - Prompt number within arc
- `prompt_text`: TEXT - The creative prompt used to generate this song
- `duration_seconds`: INTEGER - Song duration
- `embedding`: BLOB - Sentence transformer vector embedding
- `created_at`: TIMESTAMP

### arcs
- `id`: INTEGER PRIMARY KEY
- `track_id`: INTEGER - Foreign key to tracks
- `arc_number`: INTEGER - Arc sequence (1-4)
- `mood_description`: TEXT - Arc mood/theme
- `created_at`: TIMESTAMP

---

## Directory Structure

```
static-dreamwaves/
├── Tracks/{N}/                    # Individual track folders
│   ├── Songs/                     # Prepared songs for rendering
│   ├── Video/                     # Background video files
│   │   └── {N}.mp4               # Background loop video
│   └── remaining-prompts.md      # Prompts still needing songs
│
├── Rendered/{N}/                  # Rendered output
│   └── output_{timestamp}/
│       ├── output.mp4            # Final rendered video
│       ├── ffmpeg_command.txt    # Debug: Full ffmpeg command
│       └── filter_complex.txt    # Debug: Audio filter chain
│
├── data/
│   └── tracks.db                 # SQLite database
│
├── src/
│   ├── cli/
│   │   └── main.py              # Main CLI application (Typer)
│   ├── database/
│   │   └── db.py                # Database operations
│   ├── models/
│   │   └── models.py            # Pydantic data models
│   └── services/
│       ├── notion_service.py    # Notion API integration
│       ├── embedding_service.py # AI embeddings
│       └── query_service.py     # Semantic search
│
├── scripts/                      # Utility scripts
│   ├── batch_import_from_notion.py  # Import from Notion parent folder
│   ├── consolidate_songs.py     # Copy songs from subdirectories
│   ├── import_all_tracks.py     # Batch import all tracks
│   ├── prepend_text.py          # Add prefix to filenames
│   └── remove_prefix.py         # Remove prefix from filenames
│
└── config/
    └── settings.yaml            # Configuration
```

---

## Key Commands & Workflows

### Complete Workflow: Notion → Rendered Track

```bash
# 1. Import track from Notion
yarn import-songs --notion-url "https://notion.so/..." --songs-dir "./Tracks/24/Songs"

# 2. Generate embeddings for semantic search
yarn generate-embeddings

# 3. Find matching songs for prompts (with duration targeting)
yarn query --track 24 --duration 180 --output track-24-matches.json

# 4. Copy matched songs to track folder and generate remaining prompts doc
yarn prepare-render --results track-24-matches.json --track 24

# 5. Render the final video
yarn render --track 24 --duration 3  # 3 hours
```

### Essential Commands

#### Database Management
```bash
yarn init-db              # Initialize database schema
yarn stats                # Show database statistics (songs/tracks)
yarn stats:songs          # Song statistics only
yarn stats:tracks         # Track statistics only
```

#### Importing & Indexing
```bash
# Import single track from Notion
yarn import-songs --notion-url "<url>" --songs-dir "./Tracks/{N}/Songs"

# Force reimport (overwrite existing)
yarn import:force --notion-url "<url>" --songs-dir "./Tracks/{N}/Songs"

# Batch import from Notion folder
yarn batch-import --folder-id "<notion-folder-id>" -y

# Generate embeddings for all songs
yarn generate-embeddings
```

#### Searching & Querying
```bash
# Interactive semantic search
yarn query --track 24 --duration 180

# Output to JSON file
yarn query --track 24 --duration 180 --output results.json

# Check for missing prompts
yarn gaps --track 24
```

#### Track Preparation
```bash
# Prepare track folder with matched songs
yarn prepare-render --results track-24-matches.json --track 24

# Get track duration statistics
yarn track-duration --track 24
```

#### Rendering
```bash
# Test render (5 minutes)
yarn render --track 24 --duration test

# Auto duration (total of all songs)
yarn render --track 24 --duration auto

# Specific duration in hours
yarn render --track 24 --duration 3

# Custom settings
yarn render --track 24 --duration 3 --volume 2.0 --crossfade 8
```

---

## Duration-Aware Song Selection

The system can intelligently select multiple songs per prompt to fill a target duration (e.g., 180 minutes for 3-hour tracks).

### Algorithm

1. **Calculate arc allocation**: Divides target duration evenly across arcs (4 arcs = ~45 min each)
2. **Distribute songs**: Selects best-matching songs for each prompt until arc duration is met
3. **Arc repetition**: User repeats arcs to fill 3 hours (common workflow)
4. **Balanced selection**: Ensures even distribution across the emotional journey

### Example Output

```
Target duration: 180 minutes (10800 seconds)

Arc 1: 12 songs selected (2703s / 45m 3s)
Arc 2: 13 songs selected (2734s / 45m 34s)
Arc 3: 11 songs selected (2689s / 44m 49s)
Arc 4: 12 songs selected (2674s / 44m 34s)

Total: 48 songs (10800s / 180m 0s)
```

---

## Notion Integration

### Track Document Structure

Each track in Notion must have:

1. **Title**: Full track title (e.g., "Pre-Dawn CRT Desk 🌅 3HR LoFi Mix")
2. **Arc Sections**: 4 arcs with mood progression
3. **Prompts**: Numbered prompts within each arc

### Expected Arc Structure

```markdown
# Track 24

Arc 1: Opening / Introduction
Arc 2: Development / Rising Energy
Arc 3: Peak / Sustained Focus
Arc 4: Resolution / Wind Down
```

### Prompt Format

Each arc should have numbered prompts (typically 3-4 per arc):

```
## Arc 1

### Prompt 1
slow CRT-lit start, faint hum, stillness before dawn — vaporwave synthwave lofi

### Prompt 2
slow vaporwave chord wash, subtle tape flutter — vaporwave synthwave lofi
```

### Batch Import

Notion folder structure:
```
Music Tracks/
├── Track 22/
├── Track 23/
├── Track 24/
└── Track 25/
```

Get folder ID from Notion URL and run:
```bash
yarn batch-import --folder-id "293433e5-7885-8089-913b-fa3d8dd6ed72" -y
```

---

## Rendering System

### FFmpeg Pipeline

The render command builds a complex ffmpeg filter chain:

1. **Input streams**:
   - Background video (stream 0)
   - All songs as separate inputs (streams 1-N)

2. **Audio processing**:
   - Volume boost (default: 1.75x)
   - Sample format conversion (48kHz stereo, fltp)
   - Crossfade between songs (default: 5s, triangular curve)
   - Sequence repetition to fill duration
   - Final trim to exact duration
   - Fade in (3s) and fade out (10s)

3. **Video processing**:
   - Loop background video infinitely (`-stream_loop -1`)
   - Scale to even dimensions (required for H.264)
   - Convert to yuv420p (maximum compatibility)

4. **Output**:
   - H.264 video codec (libx264, CRF 23)
   - AAC audio codec (192kbps)
   - MP4 container

### Render Modes

- **test**: 5-minute render for quick validation
- **auto**: Full duration of all songs in Songs folder
- **hours**: Specify exact duration (e.g., `1`, `0.5`, `3`)

### Debug Files

Each render generates:
- `ffmpeg_command.txt`: Full command for reproduction
- `filter_complex.txt`: Audio filter chain for inspection

---

## Current State

### Database Statistics

- **Total Songs**: 515 (as of last batch import)
- **Total Tracks**: 15 successfully imported
- **Songs on Disk**: 911 audio files in Tracks folders
- **Missing from DB**: ~396 songs (from tracks without valid Notion docs)

### Completed Tracks

Successfully imported tracks: 22, 23, 24, and others from batch import

### Known Issues

#### Failed Imports

1. **Track 6**: No prompts found in Notion doc
2. **Tracks 7, 8**: Have 5 arcs instead of expected 4 (validation error)
3. **Tracks 5, 9**: Songs folders empty at import time
4. **Track 23**: 0 songs found during batch import

#### Solutions

- Fix Notion documents to match expected structure
- Update validation to allow 5+ arcs if needed
- Re-run import after adding songs to folders

---

## Recent Enhancements (Phase 6)

### 1. Duration-Aware Selection
- Added `--duration` option to `prepare-render`
- Intelligently selects multiple songs per prompt
- Distributes duration evenly across arcs

### 2. Remaining Prompts Documentation
- Auto-generates `remaining-prompts.md` in track folder
- Shows prompts that still need songs
- Simplified format: just arc, prompt number, and text
- Easy copy-paste to Suno for generation

### 3. Batch Import from Notion
- Import multiple tracks in one command
- Parallel processing of track pages
- Comprehensive error reporting
- Auto-generates embeddings

### 4. Render Command
- Complete Python implementation of shell script
- Supports test/auto/hours duration modes
- Configurable volume boost and crossfade
- Saves debug files for troubleshooting
- Timestamped output directories

### 5. Recursive Audio Scanning
- `track-duration` now scans all subdirectories
- Supports both .mp3 and .wav files
- Optional arc parsing (won't fail on unusual filenames)

### 6. Embedding Quote Normalization (Bug Fix)
- Fixed inconsistent quote handling in prompt embeddings
- Some Notion prompts had quotes (`"text"`), others didn't
- Quotes were being included in embeddings, affecting semantic similarity
- Solution: Strip surrounding quotes in `embedding_text` property (models.py:184-186)
- Result: Consistent embeddings regardless of quote formatting in source documents

### 7. Utility Scripts
- **consolidate_songs.py**: Copy songs from `Tracks/*/1` and `Tracks/*/2` into `Tracks/*/Songs`
- **import_all_tracks.py**: Batch import all tracks with Notion URLs and songs
- **prepend_text.py**: Add prefix to filenames (e.g., for organizing song variants)
- **remove_prefix.py**: Remove prefix from filenames
- All scripts support `--dry-run` for safe previewing

---

## Development Notes

### Tech Stack

- **Python 3.x** with Typer for CLI
- **SQLite** for local database
- **Pydantic** for type-safe data models
- **sentence-transformers** for embeddings (`all-MiniLM-L6-v2`)
- **Notion API** for workspace integration
- **FFmpeg** for audio/video rendering
- **Rich** for beautiful CLI output

### Key Libraries

```python
# Core
typer          # CLI framework
pydantic       # Data validation
sqlite3        # Database

# AI/ML
sentence-transformers  # Embeddings
numpy                 # Vector operations

# Notion
notion-client  # API integration

# Audio/Video
ffmpeg-python  # Not used (subprocess instead)
```

### Code Architecture

- **CLI Layer** (`src/cli/main.py`): Typer commands, user interaction
- **Service Layer** (`src/services/`): Business logic, integrations
- **Database Layer** (`src/database/`): SQL operations, migrations
- **Models Layer** (`src/models/`): Pydantic schemas

---

## Workflows & Use Cases

### Complete Workflow: Scaffold → Render

This is the complete process from creating a new track to final rendered video.

---

#### **Step 1: Create Notion Document**

Create a Notion document with:
- Track title
- 4 arcs with mood descriptions
- Prompts for each arc (typically 3-4 prompts per arc)

---

#### **Step 2: Scaffold Track Folder (Optional but Recommended)**

Creates folder structure without committing to song matches yet.

```bash
yarn scaffold-track --track-number 24 --notion-url "https://notion.so/Track-24-..."
```

**Creates:**
- `Tracks/24/` with subdirectories: Songs, Video, Rendered, metadata, etc.
- `metadata/track_info.json` (snapshot of track info)
- `README.md` (track overview)

**Note:** This is just a snapshot. Later commands fetch fresh data from Notion.

---

#### **Step 3: Query for Matching Songs**

Find songs from your library that match the track's prompts.

**Scenario A: Target Specific Duration (e.g., 3 hours)**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 180 \
  --output track-24-matches.json
```
- `--duration 180` = 180 minutes (3 hours)
- System distributes duration evenly across arcs
- Selects multiple songs per prompt to fill the target duration

**Scenario B: Fixed Number of Songs per Prompt**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --top-k 3 \
  --output track-24-matches.json
```
- `--top-k 3` = Get exactly 3 best matches for each prompt
- Default is 5 matches per prompt
- Total songs = (number of prompts) × (top-k)

**Scenario C: Custom Duration + Quality Threshold**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 60 \
  --min-similarity 0.7 \
  --output track-24-matches.json
```
- `--duration 60` = 1 hour (60 minutes)
- `--min-similarity 0.7` = Only include songs with 70%+ similarity
- Higher threshold = better matches but potentially fewer songs

**Output:** `track-24-matches.json` with all matched songs

---

#### **Step 4: Analyze Gaps (Optional)**

See which prompts didn't get enough matches.

```bash
yarn gaps track-24-matches.json
```

**Shows:**
- Prompts with no matches
- Prompts with low similarity matches
- How many new songs you need to generate

---

#### **Step 5: Copy Matched Songs to Track Folder**

```bash
yarn prepare-render --results track-24-matches.json --track 24
```

**What it does:**
- Copies matched songs to `Tracks/24/Songs/`
- Generates `Tracks/24/remaining-prompts.md` (prompts still needing songs)
- Organizes songs by arc and prompt

**Check:** `Tracks/24/remaining-prompts.md` to see what's missing

---

#### **Step 6: Generate Missing Songs (If Needed)**

If gaps analysis showed missing prompts:

1. Open `Tracks/24/remaining-prompts.md`
2. Copy prompts to Suno or your AI music generator
3. Generate songs for missing prompts
4. Save songs to `Tracks/24/Songs/` with naming convention:
   - `A_1_1_24a.mp3` (Arc 1, prompt 1, variant 24a)
   - `B_2_4_24b.mp3` (Arc 2, prompt 4, variant 24b)

---

#### **Step 7: Import Track to Database**

Import the track with all songs (matched + newly generated).

```bash
yarn import-songs \
  --notion-url "https://notion.so/Track-24-..." \
  --songs-dir "./Tracks/24/Songs"
```

**What it does:**
- Imports all songs from Tracks/24/Songs/
- Extracts BPM, key, duration from audio files
- Links songs to prompts from Notion doc
- Stores in database

**Then regenerate embeddings:**
```bash
yarn generate-embeddings
```

---

#### **Step 8: Add Background Video**

Place a looping background video at:
```
Tracks/24/Video/24.mp4
```

**Requirements:**
- MP4 format
- Should loop seamlessly
- Recommended: 1920×1080 or higher

---

#### **Step 9: Test Render**

Quick 5-minute test to verify everything works.

```bash
yarn render --track 24 --duration test
```

**Output:** `Rendered/24/output_{timestamp}/output.mp4`

**Check:**
- Audio crossfades working
- Video loops properly
- No errors in console

---

#### **Step 10: Full Render**

Render the complete track.

**For 3-hour track:**
```bash
yarn render --track 24 --duration 3
```

**For auto duration (uses all songs):**
```bash
yarn render --track 24 --duration auto
```

**Custom settings:**
```bash
yarn render --track 24 --duration 3 --volume 2.0 --crossfade 8
```

**Output:** `Rendered/24/output_{timestamp}/output.mp4`

---

### Duration Examples

#### **30-Minute Mix** (e.g., focus session)
```bash
# Query for 30 minutes of songs
yarn query --notion-url "URL" --duration 30 --output track-24-matches.json
yarn prepare-render --results track-24-matches.json --track 24
yarn render --track 24 --duration 0.5  # 0.5 hours = 30 min
```

#### **1-Hour Mix** (e.g., study session)
```bash
yarn query --notion-url "URL" --duration 60 --output track-24-matches.json
yarn prepare-render --results track-24-matches.json --track 24
yarn render --track 24 --duration 1
```

#### **3-Hour Mix** (e.g., deep work / YouTube upload)
```bash
yarn query --notion-url "URL" --duration 180 --output track-24-matches.json
yarn prepare-render --results track-24-matches.json --track 24
yarn render --track 24 --duration 3
```

#### **Custom: Get Exactly 48 Songs** (4 per prompt, 12 prompts)
```bash
yarn query --notion-url "URL" --top-k 4 --output track-24-matches.json
yarn prepare-render --results track-24-matches.json --track 24
yarn render --track 24 --duration auto  # Uses all 48 songs
```

---

### Quick Reference: Key Parameters

**Query Command:**
- `--duration N` - Target N minutes of total songs (distributed across arcs)
- `--top-k N` - Get N best matches per prompt (default: 5)
- `--min-similarity N` - Only include songs with similarity ≥ N (default: 0.6)
- `--output FILE` - Save results to FILE

**Render Command:**
- `--duration test` - 5-minute test render
- `--duration auto` - Use all songs in Tracks/{N}/Songs/
- `--duration N` - Render N hours (e.g., 3 = 3 hours)
- `--volume N` - Volume boost (default: 1.75)
- `--crossfade N` - Crossfade duration in seconds (default: 5)

### Song Naming Convention

Format: `{arc_letter}_{arc_num}_{prompt_num}_{variant}.mp3`

Examples:
- `A_1_1_20a.mp3` - Arc 1 (A), Arc number 1, Prompt 1, variant 20a
- `B_2_4_22c.mp3` - Arc 2 (B), Arc number 2, Prompt 4, variant 22c

This naming helps organize songs by their emotional arc and prompt.

---

## Future Enhancements

### Potential Improvements

1. **Auto-generation integration**: Direct Suno API integration for missing prompts
2. **Playlist optimization**: Reorder songs within arcs for better flow
3. **Multi-track rendering**: Render multiple tracks in batch
4. **YouTube integration**: Auto-upload with metadata
5. **Web UI**: Browser-based interface for non-CLI users
6. **Advanced matching**: Consider tempo, key, energy in semantic search
7. **Template system**: Reusable arc templates for different moods

### Known Limitations

- Manual background video creation required
- No automatic song generation (requires Suno manual workflow)
- Single embedding model (could support multiple)
- No audio analysis features (tempo, key detection)
- Limited to 4-arc structure (validation enforced)

---

## Troubleshooting

### Common Issues

**Issue**: "Background video not found"
**Solution**: Ensure `Tracks/{N}/Video/{N}.mp4` exists with correct track number

**Issue**: "No MP3 files found in Songs directory"
**Solution**: Run `prepare-render` first to copy matched songs to track folder

**Issue**: "Validation error: Expected 4 arcs, got 5"
**Solution**: Update Notion document to have exactly 4 arcs, or modify validation in code

**Issue**: Songs in database but not showing in query results
**Solution**: Run `yarn generate-embeddings` to ensure embeddings exist

**Issue**: Low similarity scores for all matches
**Solution**: Embeddings may be missing, or prompts need refinement for better matching

### Debug Commands

```bash
# Check database contents
sqlite3 data/tracks.db "SELECT COUNT(*) FROM songs;"
sqlite3 data/tracks.db "SELECT * FROM tracks;"

# Verify embeddings exist
sqlite3 data/tracks.db "SELECT COUNT(*) FROM songs WHERE embedding IS NOT NULL;"

# Check track folder structure
ls -R Tracks/24/

# View ffmpeg debug output
cat Rendered/24/output_{timestamp}/ffmpeg_command.txt
cat Rendered/24/output_{timestamp}/filter_complex.txt
```

### Utility Scripts

The `scripts/` directory contains helpful utilities for managing song files and batch operations:

```bash
# Consolidate songs from subdirectories into main Songs folder
python scripts/consolidate_songs.py --base-dir ./Tracks --dry-run
python scripts/consolidate_songs.py --base-dir ./Tracks  # Actually copy
python scripts/consolidate_songs.py --base-dir ./Tracks --track-id 123456  # Specific track

# Batch import all tracks with songs and Notion URLs
python scripts/import_all_tracks.py --dry-run
python scripts/import_all_tracks.py  # Interactive confirmation
python scripts/import_all_tracks.py --tracks "10,11,12"  # Specific tracks

# Batch import from Notion parent folder (scans child pages)
# Add NOTION_PARENT_FOLDER_URL to .env, or use --notion-url
yarn batch-import-folder --dry-run  # Preview what would be imported
yarn batch-import-folder  # Import all matching tracks
yarn batch-import-folder --skip-tracks "14,15,20"  # Skip specific tracks
yarn batch-import-folder --notion-url "https://notion.so/parent"  # Override env var

# Add prefix to filenames (useful for organizing variants)
python scripts/prepend_text.py --folder ./Tracks/24/Songs --prefix "A_" --dry-run
python scripts/prepend_text.py --folder ./Tracks/24/Songs --prefix "A_"

# Remove prefix from filenames
python scripts/remove_prefix.py --folder ./Tracks/24/Songs --prefix "A_" --dry-run
python scripts/remove_prefix.py --folder ./Tracks/24/Songs --prefix "A_"
```

**Pro tip:** Always use `--dry-run` first to preview changes before executing!

---

## Project History

### Phase 1: Foundation
- Initial database schema
- Basic Notion import
- Song metadata extraction

### Phase 2: Semantic Search
- Embedding generation with sentence-transformers
- Cosine similarity matching
- Interactive query command

### Phase 3: Track Management
- Track-prompt relationship modeling
- Gap detection (missing prompts)
- Statistics and reporting

### Phase 4: Preparation Workflow
- `prepare-render` command
- File copying to track folders
- Naming convention enforcement

### Phase 5: Batch Operations
- Batch import from Notion folders
- Parallel track processing
- Error handling and reporting

### Phase 6: Rendering & Polish (Current)
- Duration-aware song selection
- Remaining prompts documentation
- Complete render command
- Recursive audio file scanning
- Production-ready workflow

---

## Contact & Resources

**Project Repository**: [Add GitHub URL if applicable]
**Notion Workspace**: Internal organization
**Output**: YouTube channel (upload manually)

---

## Quick Reference

### Most Used Commands

```bash
# Check status
yarn stats

# Import new track
yarn import-songs --notion-url "<url>" --songs-dir "./Tracks/N/Songs"
yarn generate-embeddings

# Prepare track for rendering
yarn query --track N --duration 180 --output results.json
yarn prepare-render --results results.json --track N

# Render
yarn render --track N --duration test    # Quick test
yarn render --track N --duration 3       # Full 3-hour render
```

### File Locations

- **Database**: `data/tracks.db`
- **Songs**: `Tracks/{N}/Songs/*.mp3`
- **Background**: `Tracks/{N}/Video/{N}.mp4`
- **Output**: `Rendered/{N}/output_{timestamp}/output.mp4`
- **Remaining**: `Tracks/{N}/remaining-prompts.md`

---

**End of Agent Context Document**
