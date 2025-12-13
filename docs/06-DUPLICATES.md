# Duplicate Prevention Guide

How the LoFi Track Manager prevents duplicates and handles re-imports.

---

## 🛡️ Overview

The system has comprehensive duplicate prevention built into every import operation. You can safely run import commands multiple times without creating duplicates.

---

## ✅ Duplicate Prevention Mechanisms

### 1. Import Songs (`yarn import-songs`)

**How it works:**
- Checks if `filename` exists in database before processing
- Skips songs already imported
- Only analyzes new songs

**Example:**
```bash
# First import
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/9/Songs"
# Result: Imports 43 songs

# Run again
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/9/Songs"
# Result: Skips all 43 songs, 0 new imports
```

**Output:**
```
📥 Importing Track from Notion

Analyzing audio files...
  ⊘ 1_1_45a.mp3 (already in database)
  ⊘ 1_2_46a.mp3 (already in database)
  ...

✅ Imported 0 new songs
Skipped 43 existing songs
```

---

### 2. Post-Render (`yarn post-render`)

**How it works:**
- Checks each rendered file against database
- Shows which files are skipped
- Reports skip count

**Example:**
```bash
yarn post-render --track 20
```

**Output:**
```
📥 Importing Rendered Songs

Found 15 audio files

  ✓ A_1_1_20a.mp3 (Arc 1, BPM: 95.3)
  ✓ B_1_2_20b.mp3 (Arc 1, BPM: 93.8)
  ⊘ A_2_6_19a.mp3 (already in database)
  ⊘ B_2_6_13c.mp3 (already in database)
  ...

✅ Imported 12 new songs
Skipped 3 existing songs
```

---

### 3. Track Records

**How it works:**
- Checks `notion_url` for uniqueness
- Prevents duplicate track entries
- Logs existing track info

**Code:**
```python
existing_track = db.get_track_by_notion_url(notion_url)
if existing_track:
    logger.info(f"Track already exists: {existing_track.title}")
    track = existing_track
```

---

## 🔄 Force Re-Import

Sometimes you want to re-analyze songs (e.g., after audio file updates).

### Use `--force` Flag

```bash
yarn import:force \
  --notion-url "URL" \
  --songs-dir "./Tracks/9/Songs"
```

**What it does:**
- Re-analyzes all audio files
- Updates existing database records
- Useful after:
  - Audio file modifications
  - BPM/key corrections
  - Metadata updates

**When to use:**
- Audio files were edited
- Need to update BPM/key data
- Notion document was updated

**When NOT to use:**
- Normal imports (use regular `import-songs`)
- Just checking status (use `yarn stats`)

---

## 📊 Check What's Already Imported

### Quick Stats

```bash
# Overall statistics
yarn stats

# Track overview
yarn stats:tracks

# Song details
yarn stats:songs
```

### Database Viewer

```bash
# View all songs
./scripts/view_db.sh songs

# View all tracks
./scripts/view_db.sh tracks

# Quick stats
./scripts/view_db.sh stats
```

### Check Specific Track

```bash
# Check if track folder has songs
ls -la Tracks/9/Songs/

# Count files
ls Tracks/9/Songs/*.mp3 | wc -l
```

---

## 🔍 How to Tell If Already Imported

### Method 1: Check Stats

```bash
yarn stats:tracks
```

**Output shows imported tracks:**
```
Total tracks in database: 2

┏━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Number ┃ Title          ┃ Status ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 9      │ Night Shift    │ draft  │
│ 13     │ TRACK 13       │ draft  │
└────────┴────────────────┴────────┘
```

### Method 2: Run Import (Safe)

```bash
yarn import-songs --notion-url "URL" --songs-dir "PATH"
```

**If already imported:**
```
✅ Imported 0 new songs
Skipped 43 existing songs
```

**If not imported:**
```
✅ Imported 43 songs!
```

### Method 3: Database Query

```bash
./scripts/view_db.sh stats
```

**Output:**
```
Total songs: 89
Songs per arc:
  Arc 1: 24
  Arc 2: 27
  Arc 3: 18
  Arc 4: 20
Total tracks: 2
```

---

## 💡 Common Scenarios

### Scenario 1: Forgot If I Imported

**Solution:** Just run import again (safe)

```bash
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/9/Songs"
```

**Result:** Skips existing, imports only new songs

---

### Scenario 2: Added New Songs to Track

**Setup:**
- Track 9 already imported (43 songs)
- Generated 5 new songs
- Added to `Tracks/9/Songs/`

**Solution:** Run import again

```bash
yarn import-songs --notion-url "URL" --songs-dir "./Tracks/9/Songs"
```

**Result:**
```
✅ Imported 5 new songs
Skipped 43 existing songs
```

---

### Scenario 3: Updated Audio Files

**Setup:**
- Re-generated some songs with better quality
- Same filenames, different audio

**Solution:** Use force flag

```bash
yarn import:force --notion-url "URL" --songs-dir "./Tracks/9/Songs"
```

**Result:** Re-analyzes all songs, updates database

---

### Scenario 4: Multiple Tracks in Same Folder

**Not recommended!** Each track should have its own folder.

**Correct structure:**
```
Tracks/
├── 9/
│   └── Songs/
│       ├── 1_1_45a.mp3
│       └── 1_2_46a.mp3
├── 13/
│   └── Songs/
│       ├── 1_1_50a.mp3
│       └── 1_2_51a.mp3
```

---

## 🚫 What Can't Be Duplicated

### 1. Songs (by filename)
- ✅ Prevented
- **Key:** `filename` (unique constraint)
- **Check:** `db.get_song_by_filename()`

### 2. Tracks (by Notion URL)
- ✅ Prevented
- **Key:** `notion_url` (unique constraint)
- **Check:** `db.get_track_by_notion_url()`

---

## 🔧 Manual Duplicate Cleanup

If you somehow end up with duplicates (shouldn't happen), you can clean them up:

### Check for Duplicates

```bash
./scripts/view_db.sh shell
```

```sql
-- Find duplicate songs
SELECT filename, COUNT(*) as count
FROM songs
GROUP BY filename
HAVING count > 1;

-- Find duplicate tracks
SELECT notion_url, COUNT(*) as count
FROM tracks
GROUP BY notion_url
HAVING count > 1;
```

### Remove Duplicates (Careful!)

```sql
-- Keep newest, delete older duplicates
DELETE FROM songs
WHERE id NOT IN (
  SELECT MAX(id)
  FROM songs
  GROUP BY filename
);
```

**Note:** This should never be necessary - the system prevents duplicates!

---

## 📝 Best Practices

### 1. Normal Imports

Use regular import (not force):
```bash
yarn import-songs --notion-url "URL" --songs-dir "PATH"
```

### 2. After Editing Audio

Use force flag:
```bash
yarn import:force --notion-url "URL" --songs-dir "PATH"
```

### 3. Check Before Big Operations

```bash
yarn stats:tracks  # See what's imported
yarn stats:songs   # See song count
```

### 4. Regular Embeddings Regeneration

After imports or post-render:
```bash
yarn generate-embeddings
```

---

## 🎯 Summary

**You can safely:**
- ✅ Run `import-songs` multiple times
- ✅ Run `post-render` multiple times
- ✅ Re-import tracks
- ✅ Import new songs to existing tracks

**The system will:**
- ✅ Skip existing songs automatically
- ✅ Only import new songs
- ✅ Prevent duplicate entries
- ✅ Report what was skipped

**No risk of:**
- ❌ Duplicate song entries
- ❌ Duplicate track entries
- ❌ Database corruption
- ❌ Lost data

---

## 📖 Related Documentation

- [Command Reference](./05-COMMANDS.md) - All commands
- [Workflow Guide](./04-WORKFLOW.md) - Complete workflow
- [Troubleshooting](./10-TROUBLESHOOTING.md) - Common issues

---

**Import with confidence!** The system has your back. 🛡️
