# Complete Track Creation Workflow

End-to-end guide for creating tracks with the LoFi Track Manager.

---

## 🎯 Overview

The LoFi Track Manager streamlines your track production by finding reusable songs from your library, reducing new generation by 60-70%.

**Time Savings:** 4-5 hours → 2-3 hours per track (40-60% faster)

---

## 📋 Two Workflow Options

Choose the workflow that fits your needs:

### Option A: Song Bank Workflow (Reuse Existing Songs)
Best for tracks where you have a large library and want to maximize reuse.

[Jump to Song Bank Workflow](#song-bank-workflow)

### Option B: Staging Workflow (Generate New Songs in Batches)
Best for generating new songs for a track. Auto-renames files, splits them for rendering variety, and consolidates for final render.

[Jump to Staging Workflow](#staging-workflow)

---

## Song Bank Workflow

### Step 1: Query for Matching Songs

Find reusable songs from your library for a new track. All filtering happens here so you can see the filtered pool size before running `prepare-render`:

```bash
yarn query \
  --track 20 \
  --top-k 5
```

With filters:
```bash
# Skip songs used in the last 2 tracks and used more than 5 times total
yarn query --track 20 --skip-recent-tracks 2 --max-usage 5

# Only pull from specific source tracks
yarn query --track 20 --from-tracks "1002,1003"

# Skip songs from a retired theme
yarn query --track 20 --skip-themes "sunrise"

# Use top-scored matches instead of random sampling
yarn query --track 20 --no-random
```

**What it does:**
- Parses your Notion track document
- Pre-filters the song pool based on any filter flags and prints the post-filter count
- Searches the filtered pool using semantic embeddings
- Returns matches per prompt (randomly sampled by default, or top-scored with `--no-random`)
- Outputs JSON with similarity scores

**Example output:**
```
🔍 Querying for Matching Songs

Track: Neon Rain Focus Flow
Arcs: 4

Arc 1: Phase 1 – Calm Intro
  Prompt 1: Found 3 matches (best: 75.3%)
  Prompt 2: No matches
  Prompt 3: Found 3 matches (best: 78.6%)
  ...

✅ Query complete!
Total matches: 27
```

---

### Step 2: Analyze Gaps

Identify which prompts need new song generation:

```bash
yarn gaps "./output/playlists/track-20-matches.json"
```

**Adjustable threshold:**
```bash
yarn gaps "./output/playlists/track-20-matches.json" --min-similarity 0.7
```

**Example output:**
```
Gap Analysis Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Category                     ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ No matches (need generation) │    10 │      52.6% │
│ Low quality (< 70%)          │     1 │       5.3% │
│ Good matches (≥ 70%)         │     8 │      42.1% │
└──────────────────────────────┴───────┴────────────┘

💡 Recommendation:
Generate approximately 11 new songs
This represents 57.9% of the track
```

---

### Step 3: Scaffold Track Folder

Create the track folder structure:

```bash
yarn scaffold-track \
  --track-number 20 \
  --notion-url "https://notion.so/Track-20"
```

**Creates:**
```
Tracks/20/
├── Songs/          # Original/matched songs go here
├── Rendered/       # Final rendered tracks
├── metadata/       # Track metadata & config
└── README.md       # Track info from Notion
```

---

### Step 4: Prepare for Rendering

Copy matched songs to your track folder:

```bash
yarn prepare-render --track 20
```

**Options:**
```bash
# Copy files (default - keeps originals)
yarn prepare-render --track 20

# Move files (removes originals)
yarn prepare-render --track 20 --move

# Auto-select songs for a target duration
yarn prepare-render --track 20 --duration 180
```

> **Note:** Usage filters (`--skip-recent-tracks`, `--max-usage`, `--skip-themes`, `--from-tracks`) are applied at the `query` step, not here. Run `query` with those flags so you can confirm the filtered pool size before preparing.

**Example output:**
```
🎬 Preparing Track for Render

Found 9 songs to copy

  ✓ B_1_3_19d.mp3 (arc_1, prompt 3)
  ✓ A_2_6_19a.mp3 (arc_2, prompt 1)
  ✓ B_2_6_13c.mp3 (arc_2, prompt 2)
  ...

✅ Prepared 9 songs for rendering

      Songs by Arc
┏━━━━━━━┳━━━━━━━┓
┃ Arc   ┃ Songs ┃
┡━━━━━━━╇━━━━━━━┩
│ arc_1 │     3 │
│ arc_2 │     4 │
│ arc_3 │     1 │
│ arc_4 │     1 │
└───────┴───────┘
```

---

### Step 5: Generate Missing Songs

**Manual step:** Use your AI music generator (Suno, Udio, etc.)

1. Look at the gaps identified in Step 2
2. Generate songs for those specific prompts
3. Name them properly: `A_1_1_20a.mp3` (Arc 1, Prompt 1, Song 20, Order a)
4. Save to `Tracks/20/Songs/`

**Naming convention:**
```
Format: [Prefix]_Arc_Prompt_Song[Order].mp3

Examples:
- 1_1_20a.mp3  → Arc 1, Prompt 1, Song 20, Order a
- A_2_6_20a.mp3 → Arc 2, Prompt 6, Song 20, Order a (rendered version)
- B_3_2_20b.mp3 → Arc 3, Prompt 2, Song 20, Order b (alternate)
```

---

### Step 6: Render Video with FFmpeg

**Automated rendering:** The system uses FFmpeg to create professional video renders

```bash
# Test render (5 minutes)
yarn render --track 20 --duration test

# Full 3-hour render
yarn render --track 20 --duration 3

# Auto duration (uses all songs)
yarn render --track 20 --duration auto

# Custom settings
yarn render --track 20 --duration 3 --volume 2.0 --crossfade 8
```

**Output location:** `Rendered/20/output_{timestamp}/output.mp4`

**Features:**
- Automatic crossfades between songs
- Looping background video
- Volume boost and fades
- Debug files (ffmpeg_command.txt, filter_complex.txt)

---

### Step 7: Import Rendered Songs

Add your rendered songs back to the library for future reuse:

```bash
yarn post-render --track 20
```

**What it does:**
- Scans `Tracks/20/Rendered/` for audio files
- Analyzes each file (BPM, key, duration)
- Adds to database (skips duplicates)
- Makes songs searchable for future tracks

**Example output:**
```
📥 Importing Rendered Songs

Found 15 audio files

  ✓ A_1_1_20a.mp3 (Arc 1, BPM: 95.3)
  ✓ B_1_2_20b.mp3 (Arc 1, BPM: 93.8)
  ⊘ A_2_6_19a.mp3 (already in database)
  ...

✅ Imported 12 new songs
Skipped 3 existing songs

💡 Next step: Regenerate embeddings
   yarn generate-embeddings
```

---

### Step 8: Regenerate Embeddings

Make your new songs searchable:

```bash
yarn generate-embeddings
```

**Why?** New songs need embeddings for semantic search to work in future queries.

---

### Step 9: Mark as Published

Track YouTube publication and update statistics:

```bash
yarn publish \
  --track 20 \
  --youtube-url "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

**With custom date:**
```bash
yarn publish \
  --track 20 \
  --youtube-url "https://youtube.com/watch?v=..." \
  --date "2025-01-15"
```

**What it does:**
- Updates track status to PUBLISHED
- Stores YouTube URL
- Increments usage count for all songs
- Creates `Tracks/20/metadata/published.json`

---

### Step 10: Verify & Review

Check your work:

```bash
# View track duration
yarn track-duration --track 20

# View statistics
yarn stats

# View database
./scripts/view_db.sh songs
./scripts/view_db.sh tracks
```

---

## Staging Workflow

For generating new songs in batches with automatic organization and naming.

### Step 1: Scaffold Track with Staging

Create track structure including Staging/ directory:

```bash
yarn scaffold-track \
  --track-number 31 \
  --notion-url "https://notion.so/Track-31"
```

**Creates:**
```
Tracks/31/
├── Songs/          # Final songs after consolidation
├── Staging/        # NEW: Drop unformatted files here
├── 1/              # First half of files for rendering
├── 2/              # Second half of files for rendering
├── Video/          # Background videos
├── Image/          # Artwork
├── Rendered/       # Final rendered tracks
└── metadata/       # Track metadata & config
```

---

### Step 2: Generate Songs in Batches

Generate songs with your AI music generator (Suno, Udio, etc.):

1. Look at your Notion doc for the next prompt(s) you want to generate
2. Generate multiple variations (3-5 songs per prompt recommended)
3. Download raw files with any names (e.g., `audio1.mp3`, `song-v2.mp3`, etc.)
4. Drop them into `Tracks/31/Staging/`

**No need to rename manually!** The next step handles this automatically.

---

### Step 3: Auto-Rename Files

Automatically rename files based on Notion doc structure:

```bash
# Preview what will happen (recommended first time)
yarn stage-rename --track 31 --dry-run

# Actually rename files
yarn stage-rename --track 31
```

**What it does:**
- Scans Staging/ for unformatted audio files
- Parses Notion doc to find next arc_prompt
- Renames all files with same arc_prompt, incrementing letters (a, b, c...)
- Validates against Notion doc structure
- Keeps files in Staging/ for review

**Example output:**
```
Found 5 unformatted file(s) to process:
Next arc_prompt: 3_9
Starting letter: a

Rename Plan:
======================================================================
  audio1.mp3                     -> 3_9_31a.mp3
  generated-track.mp3            -> 3_9_31b.mp3
  song-final.mp3                 -> 3_9_31c.mp3
  output-v2.mp3                  -> 3_9_31d.mp3
  untitled.mp3                   -> 3_9_31e.mp3
======================================================================

✅ Successfully renamed 5 file(s) in Staging/
```

**Smart features:**
- Skips already-formatted files (e.g., `3_8_31a.mp3` won't be touched)
- Continues letter sequence from existing files
- Validates arc/prompt exists in Notion doc
- Scans both Songs/ and Staging/ to determine next position

---

### Step 4: Disperse to Folders 1 and 2

Split files for rendering variety:

```bash
# Preview distribution (recommended)
yarn disperse --track 31 --dry-run

# Actually move files
yarn disperse --track 31

# OR use combined command (disperse + consolidate in one - see Step 5)
yarn process --track 31 --dry-run   # Preview both phases
yarn process --track 31              # Execute both at once
```

**Note:** If using `yarn process`, skip Steps 4 and 5 - it does both automatically.

**What it does:**
- Groups files by (arc, prompt)
- Splits each group evenly between folders 1/ and 2/
- If odd count, folder 1 gets the extra file
- Moves from Staging/ → 1/ and 2/

**Example output:**
```
Dispersion Plan:
======================================================================

Prompt 3_9 (5 files):
  → Folder 1: 3 file(s)
  → Folder 2: 2 file(s)
    3_9_31a.mp3                    → 1/
    3_9_31b.mp3                    → 1/
    3_9_31c.mp3                    → 1/
    3_9_31d.mp3                    → 2/
    3_9_31e.mp3                    → 2/
======================================================================

✅ Successfully dispersed 5 file(s)
```

**Why split files?**
Folders 1/ and 2/ represent the two halves of your final track render. This ensures variety - different versions of the same prompt appear in different parts of the track.

---

### Step 5: Consolidate to Songs/

Prefix and move to final Songs/ directory:

```bash
yarn consolidate --track 31
```

**What it does:**
- Adds `A_` prefix to all files in folder 1/
- Adds `B_` prefix to all files in folder 2/
- Moves all files to Songs/
- Tracks which rendering half each song came from

**Example:**
```
Before:
  Tracks/31/1/3_9_31a.mp3
  Tracks/31/1/3_9_31b.mp3
  Tracks/31/2/3_9_31d.mp3

After:
  Tracks/31/Songs/A_3_9_31a.mp3
  Tracks/31/Songs/A_3_9_31b.mp3
  Tracks/31/Songs/B_3_9_31d.mp3
```

**Why A_ and B_ prefixes?**
- Tracks which render half the song was used in
- Helps identify song sources during final render
- Enables usage tracking per rendering session

---

### Step 6: Repeat for More Prompts

Continue generating songs in batches:

**Option 1: Separate commands**
```bash
# Generate next batch of songs → drop in Staging/
yarn stage-rename --track 31
yarn disperse --track 31

# Generate another batch → drop in Staging/
yarn stage-rename --track 31
yarn disperse --track 31

# When done with all prompts, consolidate
yarn consolidate --track 31
```

**Option 2: Streamlined workflow (recommended)**
```bash
# Generate songs → drop in Staging/
yarn stage-rename --track 31
yarn process --track 31    # Disperse + consolidate in one

# Repeat for more prompts...
yarn stage-rename --track 31
yarn process --track 31
```

**Workflow loop:**
1. Generate songs for 1-3 prompts
2. Drop in Staging/
3. Run `stage-rename`
4. Run `process` (or `disperse` if doing multiple batches, then `consolidate` once at end)
5. Repeat until all prompts complete

---

### Step 7: Render Video with FFmpeg

Same as Song Bank Workflow:

```bash
# Test render (5 minutes)
yarn render --track 31 --duration test

# Full 3-hour render
yarn render --track 31 --duration 3
```

**Output location:** `Rendered/31/output_{timestamp}/output.mp4`

---

### Step 8: Import Rendered Songs

Add songs back to library:

```bash
yarn post-render --track 31
```

---

### Step 9: Regenerate Embeddings

Make new songs searchable:

```bash
yarn generate-embeddings
```

---

### Step 10: Verify & Review

Check your work:

```bash
# View track duration
yarn track-duration --track 31

# View statistics
yarn stats
```

---

## 🔄 Visual Workflows

### Song Bank Workflow

```
┌─────────────────────┐
│  1. Query Library   │ → Find matching songs from existing tracks
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  2. Analyze Gaps    │ → Identify what needs to be generated
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  3. Scaffold Track  │ → Create folder structure
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  4. Prepare Render  │ → Copy matched songs to track folder
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 5. Generate Songs   │ → Manual: Use AI for gaps
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  6. Render Video    │ → FFmpeg: Create final video
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 7. Import Rendered  │ → Add songs back to library
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 8. Regen Embeddings │ → Make new songs searchable
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   9. Verify         │ → Check duration & stats
└─────────────────────┘
```

### Staging Workflow

```
┌─────────────────────┐
│  1. Scaffold Track  │ → Create folder structure with Staging/
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 2. Generate Batch   │ → Manual: Create 3-5 songs for prompt(s)
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ 3. Auto-Rename      │ → yarn stage-rename (Staging/ files)
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  4. Disperse        │ → yarn disperse (Staging/ → 1/ and 2/)
└──────────┬──────────┘
           ↓
     ┌────┴────┐
     ↓         ↓
   More      Done with
  Prompts?   All Prompts?
     │         │
     └────┐    ↓
          │  ┌─────────────────────┐
          │  │ 5. Consolidate      │ → yarn consolidate (1/2/ → Songs/)
          │  └──────────┬──────────┘
          │             ↓
          │  ┌─────────────────────┐
          │  │ 6. Render Video     │ → FFmpeg: Create final video
          │  └──────────┬──────────┘
          │             ↓
          │  ┌─────────────────────┐
          │  │ 7. Import & Embed   │ → post-render + embeddings
          │  └──────────┬──────────┘
          │             ↓
          │  ┌─────────────────────┐
          └─>│ 8. Verify           │ → Check duration & stats
             └─────────────────────┘
```

---

## 💡 Tips & Best Practices

### Usage Tracking & Filtering

**Prevent song overuse and repetition:**

The system automatically tracks every time a song is used and when it was last used. Apply filtering flags on `query` — this lets you see the filtered pool size before committing to `prepare-render`:

```bash
# Skip songs used in last 2 tracks (prevents recent repetition)
yarn query --track 27 --skip-recent-tracks 2

# Skip songs used more than 5 times (prevents overuse)
yarn query --track 27 --max-usage 5

# Combine both filters for maximum variety
yarn query --track 27 --skip-recent-tracks 2 --max-usage 5

# Restrict to specific source tracks
yarn query --track 27 --from-tracks "1002,1003"

# Skip songs from a retired theme
yarn query --track 27 --skip-themes "sunrise"
```

**Backfill existing usage data:**

If you have existing tracks and want to populate usage tracking:

```bash
python3 scripts/backfill_usage_tracking.py

# For specific tracks only
python3 scripts/backfill_usage_tracking.py --tracks "24,25,26"

# Preview changes without updating database
python3 scripts/backfill_usage_tracking.py --dry-run
```

**View usage statistics:**

Query results now include usage data (times_used, last_used_track, last_used_at) to help you make informed decisions about which songs to use.

### Optimize Query Results

**Adjust top-k for more options:**
```bash
yarn query --notion-url "URL" --output "file.json" --top-k 10
```

**Use higher similarity threshold:**
```bash
yarn gaps "file.json" --min-similarity 0.75
```

### File Organization

**Keep your folders organized:**
```
Tracks/
├── 9/              # Completed track
│   ├── Songs/      # Original songs used
│   ├── Rendered/   # Final renders
│   └── metadata/   # Track info
├── 13/             # Completed track
└── 20/             # Work in progress
```

### Batch Operations

**Import multiple old tracks at once:**
```bash
# Build your library first
yarn import-songs --notion-url "TRACK_9" --songs-dir "./Tracks/9/Songs"
yarn import-songs --notion-url "TRACK_13" --songs-dir "./Tracks/13/Songs"
yarn import-songs --notion-url "TRACK_17" --songs-dir "./Tracks/17/Songs"

# Then generate embeddings once
yarn generate-embeddings
```

### When to Regenerate Embeddings

**Always regenerate after:**
- Importing new tracks
- Running `post-render`
- Adding songs to library

**Command:**
```bash
yarn generate-embeddings
```

### Quality Thresholds

**Recommended similarity thresholds:**
- `0.6` (60%) - Default, balanced
- `0.7` (70%) - High quality matches only
- `0.5` (50%) - More lenient, more matches

---

## 📊 Expected Results

### Typical Track Stats

**For a 19-prompt track:**
- Good matches (≥60%): 8-10 prompts (42-53%)
- Need generation: 9-11 prompts (47-58%)
- **Time savings: ~2 hours**

**For a 50-song library:**
- First new track: ~60% reuse
- After 3 tracks: ~70% reuse
- After 5+ tracks: ~75% reuse

---

## 🎯 Success Metrics

**Track the improvements:**

```bash
# Before each new track
yarn stats:tracks  # Total tracks
yarn stats:songs   # Total songs in library

# After publishing
yarn stats         # See usage counts
```

**Look for:**
- Increasing song reuse percentage
- Decreasing generation time
- Growing library size

---

## ⏱️ Time Breakdown

### Traditional Workflow (4-5 hours)
- Planning: 30 min
- Generation: 2-3 hours
- Rendering: 1-2 hours

### With LoFi Manager (2-3 hours)
- Query & gaps: 5 min
- Prepare: 5 min
- Generation: 1-1.5 hours (40% reduction)
- Rendering: 1-2 hours
- Import & publish: 5 min

**Savings: 2 hours per track!**

---

## 🔄 Iterative Improvement

Each track you create:
1. ✅ Adds more songs to library
2. ✅ Increases reuse rate
3. ✅ Reduces generation time
4. ✅ Builds valuable analytics

**After 5 tracks:** Your library becomes highly effective, with 70-80% reuse rates!

---

## 📖 Related Documentation

- [Command Reference](./05-COMMANDS.md) - All commands in detail
- [Duplicate Prevention](./06-DUPLICATES.md) - How duplicates are handled
- [File Structure](./09-FILE-STRUCTURE.md) - Folder organization
- [Troubleshooting](./10-TROUBLESHOOTING.md) - Common issues

---

**Ready to create your first track?** Start with Step 1! 🚀
