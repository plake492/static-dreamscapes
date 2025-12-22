# Track Creation Guide

Quick guide for creating YouTube lofi tracks from Notion documents.

---

## Quick Start (Standard 3-Hour Track)

```bash
# 1. Create track folder structure
yarn scaffold-track --track 25 --notion-url "https://notion.so/..."

# 2. Find matching songs (3 hours = 180 minutes)
yarn query --track 25 --notion-url "https://notion.so/..."

# 3. Prepare songs for rendering
yarn prepare-render --track 25

# 4. Import track to database
yarn import-songs --track 25 --notion-url "https://notion.so/..."

# 5. Add background video to Tracks/25/Video/25.mp4

# 6. Test render (5 minutes)
yarn render --track 25 --duration test

# 7. Full render (3 hours)
yarn render --track 25 --duration 3
```

**That's it!** These 7 commands create a complete 3-hour YouTube track.

---

## What Each Command Does

### 1. Scaffold Track
```bash
yarn scaffold-track --track 25 --notion-url "URL"
```
Creates folder structure: `Tracks/25/{Songs,Video,Image,Rendered,metadata}`

### 2. Query for Songs
```bash
yarn query --track 25 --notion-url "URL"
```
Finds matching songs from your library. Saves to `./output/track-25-matches.json`

### 3. Prepare Render
```bash
yarn prepare-render --track 25
```
Copies matched songs to `Tracks/25/Songs/`. Creates `remaining-prompts.md` with gaps.

### 4. Import Track
```bash
yarn import-songs --track 25 --notion-url "URL"
```
Analyzes audio (BPM, key, duration) and stores in database.

### 5. Add Video
Place looping background video at `Tracks/25/Video/25.mp4` (must be MP4 format).

### 6. Test Render
```bash
yarn render --track 25 --duration test
```
Creates 5-minute test. Output: `Rendered/25/output_{timestamp}/{filename-from-notion}.mp4`

### 7. Full Render
```bash
yarn render --track 25 --duration 3
```
Renders complete 3-hour track. Output: `Rendered/25/output_{timestamp}/{filename-from-notion}.mp4`

---

## Different Track Durations

**1 hour:**
```bash
yarn render --track 25 --duration 1
```

**30 minutes:**
```bash
yarn render --track 25 --duration 0.5
```

**Use all songs (auto):**
```bash
yarn render --track 25 --duration auto
```

---

## Handling Missing Songs

If `remaining-prompts.md` shows gaps:

1. **Generate songs** using the prompts in that file
2. **Name them correctly:** `A_1_2_25a.mp3` = Arc 1, Prompt 2, variant 25a
3. **Save to** `Tracks/25/Songs/`
4. **Re-import:** `yarn import-songs --track 25 --notion-url "URL"`

---

## Advanced Options

### Custom Query Options

**Get 5 songs per prompt:**
```bash
yarn query --track 25 --notion-url "URL" --top-k 5
```

**High-quality matches only (70%+ similarity):**
```bash
yarn query --track 25 --notion-url "URL" --min-similarity 0.7
```

**Custom output location:**
```bash
yarn query --track 25 --notion-url "URL" --output ./custom/results.json
```

### Custom Render Options

**Adjust volume:**
```bash
yarn render --track 25 --duration 3 --volume 2.0
```

**Change crossfade duration:**
```bash
yarn render --track 25 --duration 3 --crossfade 8
```

**Custom output path:**
```bash
yarn render --track 25 --duration 3 --output ./my-videos/track.mp4
```

### Analyze Gaps (Optional)

See which prompts didn't get good matches:
```bash
yarn gaps ./output/track-25-matches.json
```

Shows prompts without matches and recommends how many songs to generate.

---

## Song Naming Convention

**Format:** `{arc_letter}_{arc_num}_{prompt_num}_{variant}.mp3`

**Examples:**
- `A_1_1_25a.mp3` - Arc 1, Prompt 1, Track 25 variant a
- `B_2_4_25b.mp3` - Arc 2, Prompt 4, Track 25 variant b
- `C_3_7_25c.mp3` - Arc 3, Prompt 7, Track 25 variant c
- `D_4_12_25d.mp3` - Arc 4, Prompt 12, Track 25 variant d

**Arc letters:** A=Arc1, B=Arc2, C=Arc3, D=Arc4

---

## Common Issues

### "No matches found"
Lower similarity threshold:
```bash
yarn query --track 25 --notion-url "URL" --min-similarity 0.5
```

### "Background video not found"
Ensure file exists: `Tracks/25/Video/25.mp4` (must match track number)

### Render too quiet/loud
Adjust volume boost (default: 1.75):
```bash
yarn render --track 25 --duration 3 --volume 2.5  # Louder
yarn render --track 25 --duration 3 --volume 1.5  # Quieter
```

### Changed Notion doc after scaffolding
No problem! All commands fetch fresh data from Notion. Scaffold is just a snapshot.

---

## File Locations

| What | Where |
|------|-------|
| Track folder | `./Tracks/{N}/` |
| Songs | `./Tracks/{N}/Songs/` |
| Background video | `./Tracks/{N}/Video/{N}.mp4` |
| Query results | `./output/track-{N}-matches.json` |
| Remaining prompts | `./Tracks/{N}/remaining-prompts.md` |
| Rendered video | `./Rendered/{N}/output_{timestamp}/{filename}.mp4` |
| Track metadata | `./Tracks/{N}/metadata/track_info.json` |

---

## Tips

- **Always test render first** before doing the full 3-hour render
- **Run `yarn gaps`** to see what's missing before generating songs
- **Use `--track` parameter** - it auto-resolves all file paths
- **Keep track numbers consistent** in folder names and song variants
- **The Notion "Filename" field** determines the output filename

---

## See Also

- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - Complete command documentation
- **[PROMPT_CRAFTING_GUIDE.md](./PROMPT_CRAFTING_GUIDE.md)** - Writing good prompts
- **[README.md](../README.md)** - Project overview
