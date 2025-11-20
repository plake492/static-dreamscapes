# Loading Existing Tracks to Song Bank

Guide for bulk importing songs from previous/existing tracks into the song bank.

---

## Overview

New streamlined workflow for importing legacy tracks:

1. **Dump all MP3s** into a single folder (`import_tracks/songs/`)
2. **Provide track flow documents** in `import_tracks/track_flows/`
3. **Auto-create track folders** from track flow files
4. **Auto-organize songs** into correct tracks and halves
5. **Add to bank** with interactive metadata prompts

The system handles:
- Songs with `A_`/`B_` prefixes (automatically normalized)
- Songs with special characters (cleaned automatically)
- Multiple tracks at once
- Automatic track detection from filenames

---

## Quick Start

### Complete Workflow

```bash
# 1. Place files in import folder
cp ~/OldTracks/*.mp3 import_tracks/songs/
cp ~/TrackFlows/*.md import_tracks/track_flows/

# 2. Prepare track folders (auto-creates from track flow files)
./venv/bin/python3 agent/import_legacy_tracks.py --prepare

# 3. Import songs (auto-organizes into track folders)
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04

# 4. Add to bank (for each track)
./venv/bin/python3 agent/add_to_bank.py --track 1 --flow-id 04
./venv/bin/python3 agent/add_to_bank.py --track 2 --flow-id 04
# ... etc
```

---

## Key Features

### 1. Automatic Filename Cleaning

Songs with special characters are automatically cleaned:

**Cleaned:**
```
1_1_16_a!.mp3       → 1_1_16_a.mp3 (removed '!')
song_name!@#.mp3    → song_name.mp3 (removed !@#)
track_b@.mp3        → track_b.mp3 (removed '@')
```

### 2. Automatic Prefix Handling

Songs with `A_` or `B_` prefixes are automatically normalized:

**Examples:**
```
A_001_song.mp3      → normalized to: 001_song.mp3
B_song_name.mp3     → normalized to: song_name.mp3
A_2_5_016a.mp3      → normalized to: 2_5_016a.mp3
```

**Why this matters:**
- Prevents duplicates even with different prefixes
- Works regardless of naming convention
- Handles songs from previous builds

### 3. Automatic Track Detection

The system detects track numbers from filenames:

**Patterns:**
```
A_1_2_001a.mp3      → Track 1 (from bank naming)
B_3_5_015b.mp3      → Track 15 (from bank naming)
A_001_song.mp3      → Track 1 (from prefix)
song_015.mp3        → Track 15 (from number)
```

---

## Detailed Workflow

### Step 1: Prepare Import Folder

```bash
# Create import structure (if it doesn't exist)
mkdir -p import_tracks/songs import_tracks/track_flows

# Copy ALL your MP3 files to songs folder
cp ~/OldProjects/Track1/*.mp3 import_tracks/songs/
cp ~/OldProjects/Track2/*.mp3 import_tracks/songs/
cp ~/OldProjects/Track3/*.mp3 import_tracks/songs/
# ... etc

# Copy track flow markdown files
cp ~/TrackFlowDocs/track_001_flow.md import_tracks/track_flows/
cp ~/TrackFlowDocs/track_002_flow.md import_tracks/track_flows/
```

**Track Flow File Naming:**
- `track_001_flow.md` (for Track 1)
- `track_002_flow.md` (for Track 2)
- `track_015_flow.md` (for Track 15)
- etc.

**Track Flow Content:**
Each markdown file should have metadata at the top:
```markdown
# Track 1 - Production Flow

**Track Number**: 1
**Created**: 2025-11-20
**Title**: Neon Rain Calm

[rest of your track flow document...]
```

---

### Step 2: Auto-Create Track Folders

```bash
./venv/bin/python3 agent/import_legacy_tracks.py --prepare
```

**What happens:**
1. Scans `import_tracks/track_flows/` for markdown files
2. Extracts track numbers from filenames or content
3. Creates track folders: `tracks/1/`, `tracks/2/`, etc.
4. Creates folder structure (half_1/, half_2/, video/, image/)
5. Copies track flow files to respective track folders
6. Creates metadata.json for each track

**Output:**
```
🔍 Scanning track flow files in import_tracks/track_flows/...
   ✅ Created track 1: tracks/1/
   ✅ Created track 2: tracks/2/
   ✅ Created track 15: tracks/15/

✅ Successfully created 3 track folders!

📋 Created tracks: 1, 2, 15

🎯 Next steps:
   1. Place all MP3 files in import_tracks/songs
   2. Run import: ./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

---

### Step 3: Auto-Organize Songs

```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

**What happens:**
1. Scans `import_tracks/songs/` for MP3 files
2. Detects track numbers from filenames
3. Groups songs by track and half (A/B)
4. Copies songs to correct track folders

**Output:**
```
🔍 Scanning MP3 files in import_tracks/songs/...
📋 Found 45 songs

📊 Song distribution:
   Track 1: 10 songs (half_1), 8 songs (half_2)
   Track 2: 12 songs (half_1), 10 songs (half_2)
   Track 15: 3 songs (half_1), 2 songs (half_2)

📦 Copying songs to track folders...
   ✅ Track 1: 18 songs copied
   ✅ Track 2: 22 songs copied
   ✅ Track 15: 5 songs copied

✅ Successfully copied 45 songs!

🎯 Next steps:
   For each track, run:
   ./venv/bin/python3 agent/add_to_bank.py --track 1 --flow-id 04
   ./venv/bin/python3 agent/add_to_bank.py --track 2 --flow-id 04
   ./venv/bin/python3 agent/add_to_bank.py --track 15 --flow-id 04
```

**Dry Run:**
```bash
# Preview what would happen without making changes
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04 --dry-run
```

---

### Step 4: Add to Bank

For each track, run add_to_bank.py:

```bash
./venv/bin/python3 agent/add_to_bank.py --track 1 --flow-id 04
```

**What happens:**
1. Scans `tracks/1/half_1/` and `tracks/1/half_2/`
2. Cleans filenames (removes special characters)
3. Normalizes for deduplication (removes A_/B_ prefixes)
4. Prompts for metadata for each song
5. Copies to song_bank with proper naming

**Interactive Prompts:**
```
🔍 Searching for new songs in Track 1...

🧹 Cleaned 2 filenames (removed special characters):
   - A_001_song!.mp3 → A_001_song.mp3
   - B_002_track@.mp3 → B_002_track.mp3

📋 Found 18 new songs:
   - A_001_song.mp3 (half_1)
   - A_002_song.mp3 (half_1)
   ...

🎯 Adding songs to bank...
   Flow ID: 04

🎵 Song: A_001_song.mp3
   Suggested half: A

   Half (A/B) [default: A]: A
   Phase (1=Calm, 2=Flow, 3=Uplift, 4=Reflect): 1
   Song number within phase (e.g., 5): 1
   Order letter (a-z, e.g., 'a' for first, 'b' for second): a

   ✅ Added to bank: A_1_1_001a.mp3

[continues for each song...]

✅ Successfully added 18 songs to bank!
📁 Catalog updated: song_bank/metadata/song_catalog.json
📊 Total songs in bank: 18
```

---

## Example: Complete Migration

### Scenario: Importing 3 legacy tracks (50 total songs)

```bash
# === Step 1: Prepare Files ===

# Copy all MP3s to import folder
cp ~/OldTracks/Track1/*.mp3 import_tracks/songs/
cp ~/OldTracks/Track2/*.mp3 import_tracks/songs/
cp ~/OldTracks/Track15/*.mp3 import_tracks/songs/

# Copy track flow documents
cp ~/Flows/track_001_flow.md import_tracks/track_flows/
cp ~/Flows/track_002_flow.md import_tracks/track_flows/
cp ~/Flows/track_015_flow.md import_tracks/track_flows/

# Verify
ls import_tracks/songs/ | wc -l
# Output: 50

ls import_tracks/track_flows/
# Output: track_001_flow.md  track_002_flow.md  track_015_flow.md


# === Step 2: Auto-Create Track Folders ===

./venv/bin/python3 agent/import_legacy_tracks.py --prepare

# Output:
# 🔍 Scanning track flow files in import_tracks/track_flows/...
#    ✅ Created track 1: tracks/1/
#    ✅ Created track 2: tracks/2/
#    ✅ Created track 15: tracks/15/
#
# ✅ Successfully created 3 track folders!


# === Step 3: Auto-Organize Songs ===

./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04

# Output:
# 🔍 Scanning MP3 files in import_tracks/songs/...
# 📋 Found 50 songs
#
# 📊 Song distribution:
#    Track 1: 10 songs (half_1), 8 songs (half_2)
#    Track 2: 12 songs (half_1), 10 songs (half_2)
#    Track 15: 5 songs (half_1), 5 songs (half_2)
#
# 📦 Copying songs to track folders...
#    ✅ Track 1: 18 songs copied
#    ✅ Track 2: 22 songs copied
#    ✅ Track 15: 10 songs copied
#
# ✅ Successfully copied 50 songs!


# === Step 4: Add to Bank (Each Track) ===

# Track 1
./venv/bin/python3 agent/add_to_bank.py --track 1 --flow-id 04
# [Interactive prompts for 18 songs...]
# ✅ Successfully added 18 songs to bank!

# Track 2
./venv/bin/python3 agent/add_to_bank.py --track 2 --flow-id 04
# [Interactive prompts for 22 songs...]
# ✅ Successfully added 22 songs to bank!

# Track 15
./venv/bin/python3 agent/add_to_bank.py --track 15 --flow-id 04
# [Interactive prompts for 10 songs...]
# ✅ Successfully added 10 songs to bank!


# === Verify ===

yarn bank:status
# Output:
# === Song Bank Status ===
# Total songs: 50
# Files on disk: 50

find song_bank/tracks -name "*.mp3" | wc -l
# Output: 50
```

---

## Troubleshooting

### Track Folders Not Created

**Problem:** No track folders created after `--prepare`

**Cause:** Track flow files not found or incorrectly named

**Solution:**
```bash
# Check track flow files exist
ls import_tracks/track_flows/

# Ensure naming matches pattern: track_XXX_flow.md
# Correct: track_001_flow.md, track_015_flow.md
# Wrong: track1_flow.md, 001_flow.md

# Add **Track Number**: field to markdown content
echo "**Track Number**: 1" >> import_tracks/track_flows/track_001_flow.md
```

---

### Songs Not Detected

**Problem:** `Found 0 songs` after `--import`

**Cause:** No MP3 files in import_tracks/songs/

**Solution:**
```bash
# Verify MP3 files exist
ls import_tracks/songs/*.mp3

# Ensure files have .mp3 extension (lowercase)
# Wrong: song.MP3, song.Mp3
# Correct: song.mp3
```

---

### Unassigned Songs

**Problem:** Some songs listed as "Unassigned"

**Cause:** Track number couldn't be detected from filename

**Solution:**
```bash
# Rename files to include track number
# Option 1: Add track number prefix
mv import_tracks/songs/song.mp3 import_tracks/songs/A_001_song.mp3

# Option 2: Add track number in filename
mv import_tracks/songs/song.mp3 import_tracks/songs/song_001.mp3

# Option 3: Use bank naming format
mv import_tracks/songs/song.mp3 import_tracks/songs/A_1_2_001a.mp3

# Re-run import
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

---

### Special Characters in Filenames

**Problem:** Songs have special characters like `!`, `@`, `#`

**Solution:** The system automatically cleans these:
```
1_1_16_a!.mp3 → 1_1_16_a.mp3 (cleaned automatically)
```

You'll see a report:
```
🧹 Cleaned 3 filenames (removed special characters):
   - 1_1_16_a!.mp3 → 1_1_16_a.mp3
   - song@.mp3 → song.mp3
   - track#.mp3 → track.mp3
```

---

## Folder Structure After Import

```
static-dreamwaves/
├── import_tracks/              # Import staging area
│   ├── track_flows/            # Track flow markdown files
│   │   ├── track_001_flow.md
│   │   ├── track_002_flow.md
│   │   └── track_015_flow.md
│   └── songs/                  # All MP3s to import
│       ├── A_001_song.mp3
│       ├── B_002_song.mp3
│       └── ...
│
├── tracks/                     # Track folders (auto-created)
│   ├── 1/
│   │   ├── half_1/             # Songs copied here
│   │   ├── half_2/             # Songs copied here
│   │   ├── video/
│   │   ├── image/
│   │   ├── metadata.json
│   │   └── track_001_flow.md   # Copied from import_tracks/
│   ├── 2/
│   │   └── ...
│   └── 15/
│       └── ...
│
└── song_bank/                  # Final destination
    ├── tracks/
    │   ├── 1/
    │   │   ├── A_1_1_001a.mp3
    │   │   ├── A_1_2_001b.mp3
    │   │   └── ...
    │   ├── 2/
    │   └── 15/
    └── metadata/
        └── song_catalog.json
```

---

## Tips & Best Practices

1. **Use Dry Run First**: Test with `--dry-run` before importing
   ```bash
   ./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04 --dry-run
   ```

2. **Batch Import**: Import all tracks at once, then add to bank one by one

3. **Consistent Naming**: Use consistent track flow file naming (track_XXX_flow.md)

4. **Backup First**: Keep copies of original files before importing

5. **Verify Counts**: Check song counts match before and after
   ```bash
   ls import_tracks/songs/*.mp3 | wc -l
   find tracks/*/half_*/*.mp3 | wc -l
   ```

6. **Clean Up**: After successful import, you can archive import_tracks/
   ```bash
   mkdir ~/Archive
   cp -r import_tracks ~/Archive/import_$(date +%Y%m%d)
   rm -rf import_tracks/songs/*.mp3
   ```

---

## Related Documentation

- [README.md](../README.md) - Project overview
- [MANUAL_STEPS.md](MANUAL_STEPS.md) - Complete workflow
- [YARN_COMMANDS.md](YARN_COMMANDS.md) - Command reference

---

**© 2025 Static Dreamscapes Lo-Fi**
