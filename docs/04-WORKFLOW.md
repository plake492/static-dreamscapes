# Complete Track Creation Workflow

End-to-end guide for creating tracks with the LoFi Track Manager.

---

## 🎯 Overview

The LoFi Track Manager streamlines your track production by finding reusable songs from your library, reducing new generation by 60-70%.

**Time Savings:** 4-5 hours → 2-3 hours per track (40-60% faster)

---

## 📋 Complete Workflow

### Step 1: Query for Matching Songs

Find reusable songs from your library for a new track:

```bash
yarn query \
  --notion-url "https://notion.so/Track-20" \
  --output "./output/playlists/track-20-matches.json" \
  --top-k 5
```

**What it does:**
- Parses your Notion track document
- Searches library using semantic embeddings
- Finds top 5 matches per prompt
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
yarn prepare-render \
  --track 20 \
  --playlist "./output/playlists/track-20-matches.json"
```

**Options:**
```bash
# Copy files (default - keeps originals)
yarn prepare-render --track 20 --playlist "FILE"

# Move files (removes originals)
yarn prepare-render --track 20 --playlist "FILE" --move
```

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

### Step 6: Render in Your DAW

**Manual step:** Arrange, mix, and render

1. Import all songs from `Tracks/20/Songs/` into your DAW
2. Arrange them according to your Notion plan
3. Mix and master the track
4. Render final versions to `Tracks/20/Rendered/`

**Typical renders:**
- `A_Track_20_Full_Mix.mp3` - Full track
- Individual song renders with prefix (A_, B_ for variants)

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

## 🔄 Visual Workflow

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
│  6. Render in DAW   │ → Manual: Arrange, mix, render
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
│  9. Mark Published  │ → Track YouTube publication
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   10. Verify        │ → Check duration & stats
└─────────────────────┘
```

---

## 💡 Tips & Best Practices

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
