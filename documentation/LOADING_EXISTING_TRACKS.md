# Loading Existing Tracks to Song Bank

Guide for bulk importing songs from previous/existing tracks into the song bank.

---

## Overview

New streamlined workflow for importing legacy tracks:

1. **Dump all MP3s** into a single folder (`import_tracks/songs/`)
2. **Auto-generate track flow templates** (auto-detects track numbers from filenames)
3. **Paste your track flow content** into generated files
4. **Auto-organize songs** into correct tracks and halves (auto-detects flow ID and half)
5. **Add to bank** with interactive metadata prompts

The system auto-detects:
- **Track numbers** from filenames (e.g., A_1_2_**015**a.mp3 → track 15)
- **Flow IDs** from filenames (e.g., A_**1**_2_015a.mp3 → flow 01)
- **Half (A/B)** from filename prefix
- Songs with `A_`/`B_` prefixes (automatically normalized for deduplication)
- Songs with special characters (cleaned automatically)

---

## Quick Start

### Complete Workflow

```bash
# 1. Place all MP3 files in import folder
cp ~/OldTracks/*.mp3 import_tracks/songs/

# 2. Generate track flow templates (auto-detects track numbers from filenames)
./venv/bin/python3 agent/import_legacy_tracks.py --prepare

# 3. Paste your track flow content into generated files
nano import_tracks/track_flows/track_015_flow.md

# 4. Import songs (auto-detects flow ID and half, creates track folders, organizes songs)
./venv/bin/python3 agent/import_legacy_tracks.py --import

# 5. Add to bank (bulk processes all tracks, skips already-banked songs)
./venv/bin/python3 agent/add_to_bank.py --bulk --flow-id 04

# OR process single track
./venv/bin/python3 agent/add_to_bank.py --track 15 --flow-id 04
```

**Manual Override Options:**
```bash
# Manually specify track numbers for prepare
./venv/bin/python3 agent/import_legacy_tracks.py --prepare --tracks 1 2 15

# Override auto-detected flow ID
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04

# Dry run to preview changes
./venv/bin/python3 agent/import_legacy_tracks.py --import --dry-run
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

The system detects track numbers from the **third number** in filenames:

**Format:** `A_[phase]_[song]_[TRACK][order]`

**Examples:**
```
A_1_2_015a.mp3      → Track 15 (third number: "015")
B_3_5_007b.mp3      → Track 7 (third number: "007")
A_2_1_001a.mp3      → Track 1 (third number: "001")
B_4_6_100c.mp3      → Track 100 (third number: "100")
```

### 4. Automatic Flow ID Detection

The system auto-detects flow IDs from the **first number** in filenames:

**Format:** `A_[FLOW]_[song]_[track][order]`

**Examples:**
```
A_1_2_015a.mp3      → Flow 01 (first number: "1")
B_3_5_007b.mp3      → Flow 03 (first number: "3")
A_4_1_007a.mp3      → Flow 04 (first number: "4")
```

**Smart Detection:**
- Uses **most common** flow ID per track (handles mixed flows gracefully)
- If all songs in track 15 have flow "1", the track gets flow ID "01"
- If track has mixed flow IDs, uses the most frequent one
- Can be overridden with `--flow-id` parameter if needed

### 5. Automatic Half (A/B) Detection

The system auto-detects which half (first or second) from filename prefix:

**Examples:**
```
A_1_2_015a.mp3      → half_1 (first half)
B_3_5_007b.mp3      → half_2 (second half)
```

**No manual organization needed!**

---

## Detailed Workflow

### Step 1: Auto-Detect and Generate Track Folders

**Option A: Auto-Detection (Recommended)**

First, place your MP3 files in the import folder:

```bash
cp ~/OldTracks/*.mp3 import_tracks/songs/
```

Then run prepare without arguments to auto-detect track numbers:

```bash
./venv/bin/python3 agent/import_legacy_tracks.py --prepare
```

**What happens:**
1. Scans all MP3 files in `import_tracks/songs/`
2. Extracts track numbers from filenames (third number in format `A_x_x_TRACK`)
3. Detects unique track numbers (e.g., if you have 40 songs all with track "5", detects only track 5)
4. Creates track flow template markdown files in `import_tracks/track_flows/`
5. Does NOT create track folders yet (that happens during import)

**Output:**
```
🔍 No track numbers specified, auto-detecting from songs...
   ✅ Detected 1 track(s) from songs: 5

📝 Creating track flow templates for 1 track(s)...
   ✅ Created track flow template: track_005_flow.md

✅ Successfully created 1 track flow template(s)!

📋 Created templates for tracks: 5

📝 Files created in: import_tracks/track_flows
   - track_005_flow.md

🎯 Next steps:
   1. Edit track flow files and paste your content:
      nano import_tracks/track_flows/track_005_flow.md
   2. Run import to create track folders and organize songs:
      ./venv/bin/python3 agent/import_legacy_tracks.py --import
```

---

**Option B: Manual Specification**

If songs aren't ready yet, manually specify track numbers:

```bash
./venv/bin/python3 agent/import_legacy_tracks.py --prepare --tracks 1 2 15
```

This creates track flow templates for tracks 1, 2, and 15 without needing songs present.

---

### Step 2: Paste Your Track Flow Content

Edit the generated template files in `import_tracks/track_flows/` and paste your complete track flow documents:

```bash
nano import_tracks/track_flows/track_005_flow.md
```

The template looks like this:
```markdown
# Track 1 - Production Flow

**Created**: 2025-11-20 10:30
**Track Number**: 1

---

## 📋 Instructions

**Paste your complete track flow document content below this line.**

This should include:
- Track overview (title, filename, duration, mood arc)
- SEO & discovery (hashtags, tags, title formula)
- Description (hook, use cases, vibe, CTA)
- Visual design (prompts, animation instructions)
- Music arc structure (phases, anchor phrase, song descriptions)
- Post-upload checklist
- Brand notes

---

**Your content here:**

```

Simply paste your complete track flow document below the instructions section.

---

### Step 3: Place MP3 Files

Copy all your MP3 files to the import folder:

```bash
cp ~/OldProjects/Track1/*.mp3 import_tracks/songs/
cp ~/OldProjects/Track2/*.mp3 import_tracks/songs/
cp ~/OldProjects/Track15/*.mp3 import_tracks/songs/

# Verify
ls import_tracks/songs/*.mp3 | wc -l
# Output: 45
```

---

### Step 4: Import and Organize

```bash
# Flow ID is auto-detected from filenames
./venv/bin/python3 agent/import_legacy_tracks.py --import

# Or override if needed
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

**What happens:**
1. Scans `import_tracks/songs/` for MP3 files
2. Auto-detects track numbers from filenames (position 3: A_x_x_**TRACK**)
3. Auto-detects flow IDs from filenames (position 1: A_**FLOW**_x_x)
4. Auto-detects half (A_/B_ prefix) for each song
5. Creates track folders in `/tracks` (if they don't exist)
6. Copies track flow MD files from `import_tracks/track_flows/` to track folders
7. Creates metadata.json for each track with detected flow ID
8. Organizes songs into half_1/ and half_2/ based on A_/B_ prefix

**Output:**
```
🔍 Scanning MP3 files in import_tracks/songs/...
📋 Found 45 songs

📊 Song distribution:
   Track 1: 10 songs (half_1), 8 songs (half_2) (flow: 01)
   Track 2: 12 songs (half_1), 10 songs (half_2) (flow: 01)
   Track 15: 3 songs (half_1), 2 songs (half_2) (flow: 04)

📦 Creating track folders and organizing songs...
   ✅ Track 1: 18 songs copied
   ✅ Track 2: 22 songs copied
   ✅ Track 15: 5 songs copied

✅ Successfully copied 45 songs!

🎯 Next steps:
   For each track, run:
   ./venv/bin/python3 agent/add_to_bank.py --track 1 --flow-id 01
   ./venv/bin/python3 agent/add_to_bank.py --track 2 --flow-id 01
   ./venv/bin/python3 agent/add_to_bank.py --track 15 --flow-id 04
```

**Dry Run:**
```bash
# Preview what would happen without making changes
./venv/bin/python3 agent/import_legacy_tracks.py --import --dry-run
```

---

### Step 5: Add to Bank

**Option A: Bulk Processing (Recommended)**

Process all tracks at once:

```bash
./venv/bin/python3 agent/add_to_bank.py --bulk --flow-id 04
```

**What happens:**
1. Scans all track folders in `/tracks`
2. For each track, identifies songs not already in bank
3. Skips tracks that are already fully in bank
4. Prompts for metadata for each new song
5. Processes all tracks sequentially

**Output:**
```
🔍 Scanning for tracks with songs...
📋 Found 3 track(s) with songs: 1, 2, 5

   Process all 3 tracks? (y/n): y

======================================================================
Processing Track 1
======================================================================

📋 Found 18 new songs:
   - A_001_song.mp3 (half_1)
   ...

[Interactive prompts for each song]

✅ Added 18 songs from Track 1

======================================================================
Processing Track 2
======================================================================

✅ No new songs found. All songs already in bank.

======================================================================
Processing Track 5
======================================================================

📋 Found 40 new songs:
   ...

======================================================================
🎉 Bulk processing complete!
======================================================================
✅ Total songs added: 58
⏭️  Tracks skipped (no new songs): 1
📊 Total tracks processed: 3
```

---

**Option B: Single Track**

Process one track at a time:

```bash
./venv/bin/python3 agent/add_to_bank.py --track 5 --flow-id 04
```

**What happens:**
1. Scans `tracks/5/half_1/` and `tracks/5/half_2/`
2. Cleans filenames (removes special characters)
3. Normalizes for deduplication (removes A_/B_ prefixes)
4. Prompts for metadata for each song
5. Copies to song_bank with proper naming

**Interactive Prompts:**
```
🔍 Searching for new songs in Track 5...

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
# === Step 1: Auto-Generate Track Folders and Templates ===

./venv/bin/python3 agent/import_legacy_tracks.py --prepare --tracks 1 2 15

# Output:
# 🔍 Preparing 3 track(s)...
#    ✅ Created track 1: tracks/1/
#    ✅ Created track 2: tracks/2/
#    ✅ Created track 15: tracks/15/
#
# ✅ Successfully created 3 track folder(s)!
# 📝 Track flow templates created:
#    - tracks/1/track_001_flow.md
#    - tracks/2/track_002_flow.md
#    - tracks/15/track_015_flow.md


# === Step 2: Paste Track Flow Content ===

# Edit each file and paste your complete track flow document
nano tracks/1/track_001_flow.md
nano tracks/2/track_002_flow.md
nano tracks/15/track_015_flow.md


# === Step 3: Place All MP3 Files ===

# Copy all MP3s to import folder
cp ~/OldTracks/Track1/*.mp3 import_tracks/songs/
cp ~/OldTracks/Track2/*.mp3 import_tracks/songs/
cp ~/OldTracks/Track15/*.mp3 import_tracks/songs/

# Verify
ls import_tracks/songs/ | wc -l
# Output: 50
`

# === Step 4: Auto-Organize Songs ===

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


# === Step 5: Add to Bank (Bulk) ===

./venv/bin/python3 agent/add_to_bank.py --bulk --flow-id 04

# Output:
# 🔍 Scanning for tracks with songs...
# 📋 Found 3 track(s) with songs: 1, 2, 15
#
#    Process all 3 tracks? (y/n): y
#
# ======================================================================
# Processing Track 1
# ======================================================================
# [Interactive prompts for 18 songs...]
# ✅ Added 18 songs from Track 1
#
# ======================================================================
# Processing Track 2
# ======================================================================
# [Interactive prompts for 22 songs...]
# ✅ Added 22 songs from Track 2
#
# ======================================================================
# Processing Track 15
# ======================================================================
# [Interactive prompts for 10 songs...]
# ✅ Added 10 songs from Track 15
#
# ======================================================================
# 🎉 Bulk processing complete!
# ======================================================================
# ✅ Total songs added: 50
# ⏭️  Tracks skipped (no new songs): 0
# 📊 Total tracks processed: 3


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
