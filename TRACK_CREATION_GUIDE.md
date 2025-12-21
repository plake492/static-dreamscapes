# Track Creation Guide

**Complete step-by-step guide for creating tracks from scratch to final render**

---

## Overview

This guide walks you through the complete process of creating a new track:
1. Setting up the track structure
2. Finding matching songs from your library
3. Generating any missing songs
4. Rendering the final video

**Typical Timeline:**
- Setup & Query: 5-10 minutes
- Generate missing songs: 30-60 minutes (if needed)
- Rendering: 10-30 minutes (depending on duration)

---

## Prerequisites

- ✅ Notion document created with track structure
- ✅ Songs library imported into database
- ✅ Embeddings generated (`yarn generate-embeddings`)
- ✅ Background video prepared (for final render)

---

## Complete Workflow: 10 Steps

### Step 1: Create Notion Document

Create a Notion page with your track structure:

**Required elements:**
- Track title
- 4 arcs with mood descriptions
- 3-4 prompts per arc (typically 12-16 prompts total)

**Example structure:**
```
# Track 24: Pre-Dawn CRT Desk

Arc 1: Quiet Night Fade
  - Prompt 1: soft ambient pads, minimal motion...
  - Prompt 2: slow vaporwave chord wash...
  - Prompt 3: CRT-like drone tones...

Arc 2: First Light Calm
  - Prompt 4: warm lo-fi pulse...
  (etc.)
```

---

### Step 2: Scaffold Track Folder

Create the folder structure for your track.

```bash
yarn scaffold-track --track-number 24 --notion-url "https://notion.so/Track-24-..."
```

**What this creates:**
```
Tracks/24/
├── Songs/              # Where songs will go
├── Video/              # Background video
├── Rendered/           # Rendered output
├── Image/              # Track artwork
├── metadata/           # Track info snapshot
│   └── track_info.json
└── README.md           # Track overview
```

**Important:** This is just a snapshot. All later commands fetch fresh data from Notion, so you can edit the Notion doc anytime.

---

### Step 3: Query for Matching Songs

Find songs from your library that match your track's prompts.

#### Scenario A: Target Specific Duration (Most Common)

**For a 3-hour track:**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 180 \
  --output track-24-matches.json
```

- `--duration 180` = 180 minutes (3 hours)
- System distributes songs evenly across your 4 arcs
- Selects multiple songs per prompt to hit the target duration

**For a 1-hour track:**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 60 \
  --output track-24-matches.json
```

**For a 30-minute track:**
```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 30 \
  --output track-24-matches.json
```

#### Scenario B: Fixed Number of Songs per Prompt

Get exactly N songs for each prompt:

```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --top-k 3 \
  --output track-24-matches.json
```

- `--top-k 3` = Get 3 best matches for each prompt
- Total songs = (number of prompts) × 3
- Example: 12 prompts × 3 songs = 36 songs total

#### Scenario C: High-Quality Matches Only

Only include songs that match really well:

```bash
yarn query \
  --notion-url "https://notion.so/Track-24-..." \
  --duration 180 \
  --min-similarity 0.7 \
  --output track-24-matches.json
```

- `--min-similarity 0.7` = Only songs with 70%+ similarity
- Higher threshold = better matches but potentially fewer songs
- Default is 0.6 (60%)

---

### Step 4: Analyze Gaps (Optional but Recommended)

See which prompts didn't get good matches:

```bash
yarn gaps track-24-matches.json
```

**Output shows:**
- ✅ Prompts with matches
- ⚠️ Prompts with no matches
- 📊 How many new songs you need to generate
- 📈 Similarity scores for each match

**Example output:**
```
Arc 1 - Prompt 1: ✅ 5 matches (best: 78.6%)
Arc 1 - Prompt 2: ⚠️ 0 matches
Arc 1 - Prompt 3: ✅ 3 matches (best: 65.2%)

Summary:
- Matched: 11/13 prompts (84.6%)
- Missing: 2 prompts
- Need to generate: ~8 new songs
```

---

### Step 5: Copy Matched Songs to Track Folder

Copy the matched songs to your track folder:

```bash
yarn prepare-render --results track-24-matches.json --track 24
```

**What this does:**
1. Copies all matched songs to `Tracks/24/Songs/`
2. Generates `Tracks/24/remaining-prompts.md` with prompts that need songs
3. Organizes songs by arc and prompt

**After this step:**
- ✅ Check `Tracks/24/Songs/` - Should have matched songs
- 📄 Check `Tracks/24/remaining-prompts.md` - Shows what's missing

---

### Step 6: Generate Missing Songs (If Needed)

If the gaps analysis showed missing prompts:

**6.1. Open the remaining prompts file:**
```bash
cat Tracks/24/remaining-prompts.md
```

**6.2. Copy prompts to your AI music generator** (e.g., Suno)

**6.3. Generate the missing songs**

**6.4. Save songs with proper naming convention:**

**Naming format:** `{arc_letter}_{arc_num}_{prompt_num}_{variant}.mp3`

**Examples:**
- `A_1_1_24a.mp3` - Arc 1, Prompt 1, variant 24a
- `B_2_4_24b.mp3` - Arc 2, Prompt 4, variant 24b
- `C_3_7_24c.mp3` - Arc 3, Prompt 7, variant 24c

**Arc letters:**
- Arc 1 = A
- Arc 2 = B
- Arc 3 = C
- Arc 4 = D

**Save to:** `Tracks/24/Songs/`

---

### Step 7: Import Track to Database

Import the complete track (matched songs + newly generated):

```bash
yarn import-songs \
  --notion-url "https://notion.so/Track-24-..." \
  --songs-dir "./Tracks/24/Songs"
```

**What this does:**
- Scans all songs in `Tracks/24/Songs/`
- Extracts audio metadata (BPM, key, duration)
- Links songs to prompts from Notion doc
- Stores everything in database

**Then regenerate embeddings:**
```bash
yarn generate-embeddings
```

This updates the embeddings with your new songs for future tracks.

---

### Step 8: Add Background Video

Place your background video file:

**Location:** `Tracks/24/Video/24.mp4`

**Requirements:**
- Format: MP4
- Should loop seamlessly
- Recommended resolution: 1920×1080 or higher
- Length: At least 10-20 seconds (will loop automatically)

**Tips:**
- Use a subtle, non-distracting animation
- Match the mood of your track (e.g., nighttime for dark tracks)
- Test that it loops smoothly

---

### Step 9: Test Render

Do a quick 5-minute test render:

```bash
yarn render --track 24 --duration test
```

**Output location:** `Rendered/{output-filename-from-notion}.mp4`
*Example:* `Rendered/midnight-neon-crt-desk-3hr-lofi-synthwave-night-coding.mp4`

**What to check:**
- ✅ Audio crossfades are smooth
- ✅ Video loops properly without glitches
- ✅ Volume levels are good
- ✅ No errors in console

**Debug files created:**
- `ffmpeg_command.txt` - Full FFmpeg command used
- `filter_complex.txt` - Audio filter chain details

---

### Step 10: Full Render

Render the complete track:

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

**Render options:**
- `--duration test` - 5-minute test
- `--duration auto` - Use all songs in folder
- `--duration N` - N hours (e.g., 3 = 3 hours, 0.5 = 30 min)
- `--volume N` - Volume boost multiplier (default: 1.75)
- `--crossfade N` - Crossfade duration in seconds (default: 5)
- `--output PATH` - Custom output path (optional)

**Output:** `Rendered/{output-filename-from-notion}.mp4`
*Example:* `Rendered/midnight-neon-crt-desk-3hr-lofi-synthwave-night-coding.mp4`

**Filename source:**
- Uses the "Filename" field from your Notion document
- Falls back to sanitized track title if Filename field is empty
- Ensures you must run `yarn import-songs` first to populate track metadata

**Custom output path:**
```bash
yarn render --track 24 --duration 3 --output ./custom/my-video.mp4
```

**Rendering features:**
- ✨ Automatic crossfades between songs
- 🔁 Looping background video
- 🔊 Volume boost and fade in/out
- 📁 Uses filename from Notion document
- 🎯 Outputs to Rendered/ directory

---

## Common Scenarios

### Scenario 1: 3-Hour YouTube Track

```bash
# Step 1: Scaffold
yarn scaffold-track --track-number 24 --notion-url "URL"

# Step 2: Query for 3 hours of songs
yarn query --notion-url "URL" --duration 180 --output track-24-matches.json

# Step 3: Analyze what's missing
yarn gaps track-24-matches.json

# Step 4: Prepare track
yarn prepare-render --results track-24-matches.json --track 24

# Step 5: Generate missing songs (if any)
# (Use Suno based on remaining-prompts.md)

# Step 6: Import everything
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/24/Songs"
yarn generate-embeddings

# Step 7: Add background video
# (Copy to Tracks/24/Video/24.mp4)

# Step 8: Test
yarn render --track 24 --duration test

# Step 9: Full render
yarn render --track 24 --duration 3
```

---

### Scenario 2: 1-Hour Focus Session

```bash
# Query for 1 hour
yarn query --notion-url "URL" --duration 60 --output track-24-matches.json

# Prepare and render
yarn prepare-render --results track-24-matches.json --track 24
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/24/Songs"
yarn render --track 24 --duration 1
```

---

### Scenario 3: 30-Minute Quick Mix

```bash
# Query for 30 minutes
yarn query --notion-url "URL" --duration 30 --output track-24-matches.json

# Prepare and render
yarn prepare-render --results track-24-matches.json --track 24
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/24/Songs"
yarn render --track 24 --duration 0.5  # 0.5 hours = 30 min
```

---

### Scenario 4: Exact Song Count

Get exactly 48 songs (4 per prompt, 12 prompts):

```bash
# Query with top-k
yarn query --notion-url "URL" --top-k 4 --output track-24-matches.json

# Prepare and render
yarn prepare-render --results track-24-matches.json --track 24
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/24/Songs"
yarn render --track 24 --duration auto  # Uses all songs
```

---

## Quick Reference

### Key Commands

```bash
# Setup
yarn scaffold-track --track-number N --notion-url "URL"

# Query
yarn query --notion-url "URL" --duration 180 --output results.json
yarn gaps results.json

# Prepare
yarn prepare-render --results results.json --track N

# Import
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/N/Songs"
yarn generate-embeddings

# Render
yarn render --track N --duration test
yarn render --track N --duration 3
```

---

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--duration N` | Target N minutes total | `--duration 180` (3 hours) |
| `--top-k N` | N matches per prompt | `--top-k 5` |
| `--min-similarity N` | Quality threshold (0.0-1.0) | `--min-similarity 0.7` |
| `--output FILE` | Save results to file | `--output track-24.json` |

---

### Render Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--duration test` | 5-minute test render | - |
| `--duration auto` | Use all songs | - |
| `--duration N` | N hours | `--duration 3` |
| `--volume N` | Volume boost | `--volume 2.0` |
| `--crossfade N` | Crossfade seconds | `--crossfade 8` |

---

### Song Naming Convention

**Format:** `{arc_letter}_{arc_num}_{prompt_num}_{variant}.mp3`

| Component | Description | Example |
|-----------|-------------|---------|
| `arc_letter` | A, B, C, or D | `A` (Arc 1) |
| `arc_num` | 1, 2, 3, or 4 | `1` |
| `prompt_num` | Prompt number in arc | `3` |
| `variant` | Track + variant letter | `24a` |

**Examples:**
- `A_1_1_24a.mp3` - Arc 1, Prompt 1, Track 24 variant a
- `B_2_4_24b.mp3` - Arc 2, Prompt 4, Track 24 variant b
- `C_3_7_24c.mp3` - Arc 3, Prompt 7, Track 24 variant c
- `D_4_13_24d.mp3` - Arc 4, Prompt 13, Track 24 variant d

---

## Tips & Best Practices

### 🎯 Querying

- **Start with duration-based queries** (`--duration`) for predictable results
- **Use `--min-similarity 0.7`** if you want only high-quality matches
- **Always run `yarn gaps`** to see what's missing before proceeding

### 📁 File Organization

- **Keep track numbers consistent** between folder name and song variants
- **Use descriptive variant letters** (a, b, c) for different takes
- **Always scaffold first** - creates proper folder structure

### 🎬 Rendering

- **Always test render first** (`--duration test`) before full render
- **Check the debug files** if something goes wrong (ffmpeg_command.txt)
- **Use `--duration auto`** when you want to use every song in the folder

### 🎵 Song Generation

- **Generate 2-3 variants** per prompt for variety
- **Match the BPM range** suggested in your Notion doc
- **Use consistent style tags** (e.g., "vaporwave synthwave lofi")

### 🔄 Workflow Efficiency

- **Scaffold multiple tracks early** - you can fill them in later
- **Batch generate songs** - do all missing prompts at once
- **Reuse the query results** - you can re-run prepare-render with same results

---

## Troubleshooting

### "No matches found for prompt X"

**Cause:** No songs in library similar enough to this prompt

**Solutions:**
1. Lower similarity threshold: `--min-similarity 0.5`
2. Generate new songs specifically for this prompt
3. Check if embeddings are up to date: `yarn generate-embeddings`

---

### "Background video not found"

**Cause:** Missing `Tracks/N/Video/N.mp4`

**Solution:**
```bash
# Make sure file exists and matches track number
ls Tracks/24/Video/24.mp4
```

---

### "No MP3 files found in Songs directory"

**Cause:** Haven't run `prepare-render` yet, or folder is empty

**Solutions:**
1. Run `yarn prepare-render --results track-24-matches.json --track 24`
2. Check that query found matches: `yarn gaps track-24-matches.json`

---

### Render output is too quiet/loud

**Solution:** Adjust volume boost
```bash
yarn render --track 24 --duration 3 --volume 2.5  # Louder
yarn render --track 24 --duration 3 --volume 1.5  # Quieter
```

---

### Notion doc changed after scaffold

**Not a problem!** All commands (query, import-songs) fetch fresh data from Notion. The scaffold metadata is just a snapshot for reference.

**Optional:** Re-run scaffold to update the snapshot:
```bash
yarn scaffold-track --track-number 24 --notion-url "URL"
# Answer "yes" to continue when it warns folder exists
```

---

## Next Steps

After rendering:

1. **Review output** - Watch the rendered video
2. **Upload to YouTube** - If it's a public track
3. **Update database** - Mark as published if needed
4. **Archive project files** - Save query results and debug files
5. **Regenerate embeddings** - If you generated new songs

---

## Related Documentation

- **[AGENT_CONTEXT.md](./AGENT_CONTEXT.md)** - Complete technical reference
- **[README.md](./README.md)** - Project overview
- **[docs/05-COMMANDS.md](./docs/05-COMMANDS.md)** - All CLI commands
- **[docs/04-WORKFLOW.md](./docs/04-WORKFLOW.md)** - Workflow details

---

**Happy track creating! 🎵🚀**
