# Database Reset & Rebuild Guide

Complete guide for resetting the database and rebuilding from scratch with fresh Notion data and embeddings.

---

## When to Use This Guide

Perform a full reset and rebuild when:

- **Template updates**: You've updated prompt templates and need consistent embeddings
- **Schema changes**: Major database schema updates require a clean slate
- **Data corruption**: Database has inconsistent or corrupted data
- **Major refactoring**: System-wide changes that affect how data is stored
- **Quality issues**: Embeddings are producing poor match results
- **Starting fresh**: Want to remove test data and start with production-quality imports

---

## ⚠️ Important Warnings

- **This process DELETES ALL DATABASE DATA**
- **Cannot be undone without a backup**
- **Takes 10-30 minutes depending on track count**
- **Requires all Notion URLs to be available**

**ALWAYS BACKUP FIRST** (see Step 1)

---

## Complete Reset & Rebuild Process

### Step 1: Backup Current Database

**CRITICAL: Always backup before deleting anything!**

```bash
# Create backup with timestamp
cp data/tracks.db "data/tracks.db.backup-$(date +%Y%m%d-%H%M%S)"

# Verify backup was created
ls -lh data/*.backup-*

# Optional: Backup embeddings too
cp -r data/embeddings "data/embeddings.backup-$(date +%Y%m%d-%H%M%S)"
```

**Verify backup:**
```bash
# Check backup file size (should be similar to original)
du -h data/tracks.db*
```

---

### Step 2: Delete Current Database & Embeddings

**WARNING: This deletes all data. Ensure Step 1 backup is complete!**

```bash
# Delete database
rm data/tracks.db

# Delete embeddings
rm -rf data/embeddings/
```

**Verify deletion:**
```bash
# Should show: No such file or directory
ls data/tracks.db
ls data/embeddings/
```

---

### Step 3: Initialize Fresh Database

Create a clean database with the latest schema:

```bash
yarn init-db
```

**Expected output:**
```
✅ Database initialized successfully!

Database: ./data/tracks.db
Tables: songs, tracks
Indexes: 5 indexes created
```

**Verify schema:**
```bash
sqlite3 data/tracks.db ".schema songs"
```

Should show all fields including:
- `last_used_track_id TEXT`
- `last_used_at TIMESTAMP`

---

### Step 4: Re-import All Tracks from Notion

You have three options for re-importing tracks:

#### Option A: Batch Import from Notion Folder (Recommended)

**Best for:** Multiple tracks organized in a Notion parent folder

1. Get your Notion folder ID from the URL:
   ```
   https://notion.so/username/FOLDER_ID_HERE?v=...
   ```

2. Run batch import:
   ```bash
   # Preview what will be imported
   yarn batch-import --folder-id "YOUR_FOLDER_ID" --dry-run

   # Import all tracks
   yarn batch-import --folder-id "YOUR_FOLDER_ID" --yes
   ```

**Expected output:**
```
📦 Batch Import from Notion

Found 20 tracks:
  Track 22 → ./Tracks/22/Songs (45 songs)
  Track 23 → ./Tracks/23/Songs (52 songs)
  Track 24 → ./Tracks/24/Songs (41 songs)
  ...

✅ Successfully imported: 20 tracks
⏭️  Skipped: 0 tracks
❌ Failed: 0 tracks
```

---

#### Option B: Individual Track Import

**Best for:** Importing specific tracks or small numbers of tracks

```bash
# Import each track individually
yarn import-songs --track 22 --notion-url "https://notion.so/Track-22-..."
yarn import-songs --track 23 --notion-url "https://notion.so/Track-23-..."
yarn import-songs --track 24 --notion-url "https://notion.so/Track-24-..."
# ... repeat for all tracks
```

**Note:** This fetches fresh data from Notion each time, so no separate Notion clearing needed.

---

#### Option C: Scripted Batch Import

**Best for:** Many tracks with known URLs

1. Create a file `track_urls.txt`:
   ```
   22 https://notion.so/Track-22-abc123
   23 https://notion.so/Track-23-def456
   24 https://notion.so/Track-24-ghi789
   ```

2. Run import script:
   ```bash
   while read track_num url; do
     echo "Importing Track $track_num..."
     yarn import-songs --track "$track_num" --notion-url "$url"
   done < track_urls.txt
   ```

---

### Step 5: Verify Imports

Check that all tracks were imported correctly:

```bash
# View database statistics
yarn stats

# View track count
yarn stats:tracks

# Check specific track
sqlite3 data/tracks.db "SELECT track_number, title FROM tracks ORDER BY track_number;"

# Check song count per track
sqlite3 data/tracks.db "
SELECT
  last_used_track_id as track,
  COUNT(*) as songs
FROM songs
WHERE last_used_track_id IS NOT NULL
GROUP BY last_used_track_id
ORDER BY track;
"
```

**Expected results:**
- Total tracks matches your imported count
- Total songs matches sum of all audio files
- No missing tracks from your list

---

### Step 6: Generate Fresh Embeddings

Generate semantic embeddings for all songs:

```bash
# Generate embeddings (this takes 2-5 minutes for 700+ songs)
yarn generate-embeddings
```

**Expected output:**
```
🔮 Generating Embeddings

Loading model: all-MiniLM-L6-v2
Processing 731 songs...

Progress: [████████████████████████████] 100%

✅ Generated 731 embeddings
Saved to: ./data/embeddings/embeddings.npz
Metadata: ./data/embeddings/metadata.json
```

**Verify embeddings:**
```bash
# Check embeddings file exists
ls -lh data/embeddings/

# Verify metadata
cat data/embeddings/metadata.json | python3 -m json.tool | head -20
```

---

### Step 7: Backfill Usage Tracking Data

Populate usage tracking from existing `/Tracks/*/Songs/` folders:

```bash
# Preview what will be backfilled (dry run)
python3 scripts/backfill_usage_tracking.py --dry-run

# Backfill all tracks
python3 scripts/backfill_usage_tracking.py
```

**Expected output:**
```
📂 Found 20 track folder(s) to scan

Scanning tracks... ████████████████████ 100%

📊 Backfill Statistics

Summary
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric             ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Tracks Scanned     │    20 │
│ Song Files Found   │   917 │
│ Songs Matched in DB│   833 │
│ Songs Not Found    │    84 │
│ Match Rate         │ 90.8% │
└────────────────────┴───────┘

✅ Database updated successfully!
```

---

### Step 8: Final Verification

Run comprehensive checks to ensure everything is working:

```bash
# 1. Check database integrity
sqlite3 data/tracks.db "PRAGMA integrity_check;"
# Should output: ok

# 2. Verify all tracks have songs
yarn stats:tracks

# 3. Test query on a track
yarn query --track 24 --notion-url "YOUR_TRACK_24_URL" --output ./test-query.json

# 4. Check query results
cat ./test-query.json | python3 -m json.tool | head -50

# 5. Verify usage tracking
sqlite3 data/tracks.db "
SELECT
  COUNT(*) as total_songs,
  COUNT(last_used_track_id) as songs_with_usage,
  AVG(times_used) as avg_usage
FROM songs;
"

# 6. Check embeddings
yarn stats
```

**All checks should pass:**
- ✅ Database integrity: ok
- ✅ All tracks present
- ✅ Query returns matches with similarity scores
- ✅ Usage tracking populated
- ✅ Embeddings generated for all songs

---

## Troubleshooting

### Issue: Import fails for some tracks

**Symptoms:**
```
❌ Failed to import Track 15: No prompts found
```

**Solutions:**
1. **Check Notion document structure:**
   - Ensure track has 4 arcs
   - Prompts are properly formatted
   - Page is shared with integration

2. **Verify Songs folder exists:**
   ```bash
   ls Tracks/15/Songs/
   ```

3. **Check Notion URL is correct:**
   - Copy URL directly from Notion page
   - Ensure it's the page URL, not a database view

4. **Re-import with force flag:**
   ```bash
   yarn import:force --track 15 --notion-url "URL"
   ```

---

### Issue: Embeddings generation fails

**Symptoms:**
```
Error: sentence-transformers model not found
```

**Solutions:**
1. **Ensure virtual environment is activated:**
   ```bash
   source venv/bin/activate
   python3 --version  # Should show 3.10+
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check model download:**
   ```bash
   # Model should download on first run
   yarn generate-embeddings --force
   ```

---

### Issue: Query returns no matches

**Symptoms:**
- Query completes but shows 0 matches for all prompts

**Solutions:**
1. **Verify embeddings exist:**
   ```bash
   ls -lh data/embeddings/
   # Should show embeddings.npz and metadata.json
   ```

2. **Check song count:**
   ```bash
   yarn stats
   # Should show songs > 0
   ```

3. **Regenerate embeddings:**
   ```bash
   yarn generate-embeddings --force
   ```

4. **Test with lower similarity threshold:**
   ```bash
   yarn query --track 24 --notion-url "URL" --min-similarity 0.4
   ```

---

### Issue: Backfill shows low match rate

**Symptoms:**
```
Match Rate: 45.2%
```

**This is normal if:**
- Some tracks haven't been imported to database yet
- Song files have non-standard naming conventions
- Files are in subdirectories (1/, 2/) instead of Songs/

**Solutions:**
1. **Import missing tracks:**
   ```bash
   yarn import-songs --track X --notion-url "URL"
   ```

2. **Consolidate songs from subdirectories:**
   ```bash
   python3 scripts/consolidate_songs.py --base-dir ./Tracks --dry-run
   python3 scripts/consolidate_songs.py --base-dir ./Tracks
   ```

3. **Re-run backfill:**
   ```bash
   python3 scripts/backfill_usage_tracking.py
   ```

---

## Post-Reset Workflow

After successful reset and rebuild, resume normal workflow:

### Creating a New Track

```bash
# 1. Create Notion document with prompts
# 2. Scaffold track folder
yarn scaffold-track --track 27 --notion-url "URL"

# 3. Query for matches
yarn query --track 27 --notion-url "URL" --duration 180

# 4. Analyze gaps
yarn gaps ./output/track-27-matches.json

# 5. Prepare with filters
yarn prepare-render --track 27 --results ./output/track-27-matches.json \
  --skip-recent-tracks 2 --max-usage 5

# 6. Generate missing songs (manual)
# 7. Import new track
yarn import-songs --track 27 --notion-url "URL"
yarn generate-embeddings

# 8. Render
yarn render --track 27 --duration 3
```

---

## Quick Reference: Reset Commands

```bash
# Complete reset in one go (DESTRUCTIVE!)
rm data/tracks.db
rm -rf data/embeddings/
yarn init-db
yarn batch-import --folder-id "YOUR_FOLDER_ID" --yes
yarn generate-embeddings
python3 scripts/backfill_usage_tracking.py
yarn stats
```

---

## Backup & Restore

### Create Backup

```bash
# Backup database
cp data/tracks.db "data/tracks.db.backup-$(date +%Y%m%d-%H%M%S)"

# Backup embeddings
cp -r data/embeddings "data/embeddings.backup-$(date +%Y%m%d-%H%M%S)"

# Backup entire data directory
tar -czf "data-backup-$(date +%Y%m%d-%H%M%S).tar.gz" data/
```

### Restore from Backup

```bash
# List available backups
ls -lh data/*.backup-*

# Restore specific backup
cp data/tracks.db.backup-20251222-143000 data/tracks.db

# Restore embeddings
rm -rf data/embeddings/
cp -r data/embeddings.backup-20251222-143000 data/embeddings/

# Verify restore
yarn stats
```

---

## Time Estimates

**Full reset and rebuild:**

| Step | Time | Notes |
|------|------|-------|
| Backup | <1 min | Quick file copy |
| Delete | <10 sec | Remove files |
| Init DB | <10 sec | Create schema |
| Import 20 tracks | 5-10 min | Depends on Notion API speed |
| Generate embeddings | 2-5 min | For 700+ songs |
| Backfill usage | 1-2 min | Scan track folders |
| Verification | 1-2 min | Run checks |
| **Total** | **10-20 min** | Full process |

---

## Best Practices

### 1. **Always Backup First**
Never delete the database without a timestamped backup.

### 2. **Verify Before Proceeding**
Check each step completes successfully before moving to the next.

### 3. **Use Dry Run**
Always run batch operations with `--dry-run` first.

### 4. **Keep Track URLs**
Maintain a list of all track Notion URLs for easy re-import.

### 5. **Monitor Disk Space**
Embeddings and database can be 100+ MB. Ensure sufficient space.

### 6. **Test Queries**
After rebuild, test queries on a known track to verify similarity scores.

---

## Related Documentation

- **[04-WORKFLOW.md](./04-WORKFLOW.md)** - Standard workflow after reset
- **[08-DATABASE.md](./08-DATABASE.md)** - Database schema reference
- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - All command details
- **[AGENT_CONTEXT.md](./AGENT_CONTEXT.md)** - System overview

---

**Last Updated:** 2025-12-22
