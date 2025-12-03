# 👤 Manual Steps Required

This document outlines **what YOU need to do manually** vs. what the automation handles in the new song bank workflow.

---

## 🎯 The Big Picture

**You do:** Generate music, organize songs, choose which to use
**System does:** Template creation, selection from bank, rendering with A_/B_ prefixes, metadata tracking

---

## 📋 Complete Manual Workflow

### Step 1: Initial Setup (One-Time Only)

```bash
# Navigate to project
cd /path/to/static-dreamwaves

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.sh agent/*.py
```

**What this does:**
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies (librosa, numpy, etc.)
- ✅ Makes all scripts executable

**You need to do this:** Once per machine/installation

---

### Step 2: Create Track Template

**What YOU do:**
```bash
# Create next track (auto-increments)
./venv/bin/python3 agent/create_track_template.py

# Or specify track number
./venv/bin/python3 agent/create_track_template.py --track-number 20
```

**What the system does:**
- ✅ Finds highest existing track number
- ✅ Creates next track folder (e.g., 16 → 17)
- ✅ Generates folder structure:
  - `tracks/<number>/half_1/` - Songs for first half
  - `tracks/<number>/half_2/` - Songs for second half
  - `tracks/<number>/video/` - Background video
  - `tracks/<number>/image/` - Cover art
- ✅ Creates `metadata.json` with track info
- ✅ Creates `README.md` with instructions

**Output Example:**
```
✅ Track 16 template created successfully!

📋 Folder structure:
   tracks/16/
   ├── half_1/          (empty - add first half songs here)
   ├── half_2/          (empty - add second half songs here)
   ├── video/           (empty - add 16.mp4)
   ├── image/           (empty - add 16.jpg)
   ├── metadata.json    (track metadata template)
   └── README.md        (workflow instructions)
```

---

### Step 3: Select Songs from Bank (Optional)

> **Note:** Skip this step if your bank is empty or you want all new songs

**What YOU do:**

#### Option A: Select by Count
```bash
# Select 5 songs from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04

# Review the selection
cat tracks/16/bank_selection.json

# If satisfied, execute (copies files)
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

#### Option B: Select by Duration
```bash
# Select ~30 minutes of songs from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04

# Execute the selection
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

**What the system does:**
- ✅ Queries `song_catalog.json` for available songs
- ✅ Filters by flow ID (if specified)
- ✅ Selects N songs or ~X minutes of songs
- ✅ Saves selection to `bank_selection.json` (preview)
- ✅ On execute: Copies songs to `half_1/` or `half_2/` based on song metadata

**Important:** Selected songs are automatically placed in the correct half (A songs → half_1/, B songs → half_2/)

---

### Step 4: Generate Music (Suno)

**What YOU do:**
1. Go to Suno AI
2. Generate your songs with appropriate prompts
3. Download all MP3 files to your Downloads folder

**Example Suno Prompts:**
```
"ambient lo-fi synthwave, warm analog pads, nostalgic atmosphere, 75 bpm"
"steady synthwave beat, focused energy, analog pulse, 85 bpm"
"bright synthwave melody, optimistic uplifting, creative energy, 95 bpm"
"slow reflective synthwave, tape hiss, warm fadeout, 65 bpm"
```

**How many songs?**
- **3-hour mix:** ~20-30 songs (depends on song length)
- **Average song:** 3-5 minutes
- **Mix new + bank songs** for variety

**Tip:** Generate songs in batches based on theme/mood for each half

---

### Step 5: Add New Songs Manually

**What YOU do:**

```bash
# Move downloaded songs to track folders
# Organize however you want - no prefixes needed!

# Add songs to first half
mv ~/Downloads/calm_*.mp3 tracks/16/half_1/
mv ~/Downloads/focus_*.mp3 tracks/16/half_1/

# Add songs to second half
mv ~/Downloads/bright_*.mp3 tracks/16/half_2/
mv ~/Downloads/fade_*.mp3 tracks/16/half_2/
```

**Important Notes:**
- ❌ **NO prefixes needed** - Don't add A_ or B_ yourself
- ✅ Songs will be alphabetically sorted within each half
- ✅ You can rename files to control order (e.g., `01_song.mp3`, `02_song.mp3`)
- ✅ Any filename is fine - system will handle it

**Organization Tips:**
```
half_1/                          half_2/
├── 01_calm_intro.mp3           ├── 01_bright_start.mp3
├── 02_steady_focus.mp3         ├── 02_uplift.mp3
├── 03_midtempo_groove.mp3      ├── 03_reflective_fade.mp3
└── 04_building_energy.mp3      └── 04_closing.mp3
```

**The half_1 and half_2 concept:**
- **half_1**: Usually calm → building energy (A_ prefix at render)
- **half_2**: Usually peak → wind down (B_ prefix at render)
- Organize by emotional arc within each half

---

### Step 6: Add Video and Image

**What YOU do:**

```bash
# Copy background video (required for rendering)
cp ~/path/to/background.mp4 tracks/16/video/16.mp4

# Copy cover art (optional, for YouTube thumbnail)
cp ~/path/to/cover.jpg tracks/16/image/16.jpg
```

**Video Requirements:**
- Format: MP4 (H.264)
- Resolution: Any (will be scaled)
- Duration: Any (will be looped infinitely)
- Typical: 1920x1080, static background or slow animation

**Tip:** Use the same background video for consistency across tracks

---

### Step 7: Build Track

**What YOU do:**

```bash
# Build with auto duration (uses total song length)
./venv/bin/python3 agent/build_track.py --track 16

# Or specify duration in hours
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# Test mode (5 minutes)
./venv/bin/python3 agent/build_track.py --track 16 --duration test
```

**What the system does:**
1. ✅ Reads all songs from `half_1/` (alphabetically sorted)
2. ✅ Reads all songs from `half_2/` (alphabetically sorted)
3. ✅ Creates temporary `temp_songs/` folder
4. ✅ Copies songs with **automatic A_/B_ prefixes**:
   - `half_1/song1.mp3` → `A_001_song1.mp3`
   - `half_1/song2.mp3` → `A_002_song2.mp3`
   - `half_2/song1.mp3` → `B_001_song1.mp3`
   - `half_2/song2.mp3` → `B_002_song2.mp3`
5. ✅ Calls FFmpeg to render with crossfades
6. ✅ Generates `tracklist.json` with render metadata
7. ✅ Cleans up temporary folders

**Build Output:**
```
rendered/16/output_20251119_103000/
├── output.mp4          # Final video
├── ffmpeg_command.txt  # FFmpeg command used
├── filter_complex.txt  # FFmpeg filter chain
└── tracklist.json      # Song order and metadata
```

**Duration Options:**
- **auto** (default): Uses total length of all songs
- **1, 2, 3**: Specific hours (songs loop if needed)
- **test**: 5 minutes for quick testing

---

### Step 8: Review Output

**What YOU do:**

```bash
# Find your rendered mix
ls -lh rendered/16/output_*/output.mp4

# Play it back
open rendered/16/output_20251119_103000/output.mp4

# Check tracklist
cat rendered/16/output_20251119_103000/tracklist.json
```

**Quality Check:**
- ✅ Crossfades are smooth (5-second overlaps)
- ✅ Volume is consistent (1.75x boost applied)
- ✅ No gaps or clicks between songs
- ✅ Fade-in at start (3 seconds)
- ✅ Fade-out at end (10 seconds)
- ✅ Video loops seamlessly

---

### Step 9: Add New Songs to Bank

**What YOU do:**

```bash
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

**What the system does:**
1. ✅ Scans `half_1/` and `half_2/` for songs not already in bank
2. ✅ For each new song, prompts you for metadata:

**Interactive Prompts:**
```
🎵 Song: epic_synthwave_beat.mp3
   Suggested half: A
   Half (A/B) [default: A]: A
   Phase (1=Calm, 2=Flow, 3=Uplift, 4=Reflect): 2
   Song number within phase (e.g., 5): 5
   Order letter (a-z, e.g., 'a' for first, 'b' for second): a

   ✅ Added to bank: A_2_5_016a.mp3
```

**What the system does after prompts:**
3. ✅ Generates bank filename (e.g., `A_2_5_016a.mp3`)
4. ✅ Copies to `song_bank/tracks/16/`
5. ✅ Updates `song_catalog.json` with metadata
6. ✅ Links to flow ID and prompt

**Metadata Captured:**
- Half (A/B)
- Phase (1-4)
- Song number within phase
- Source track
- Flow ID
- Original filename

**Result:**
```
✅ Successfully added 10 songs to bank!
📁 Catalog updated: song_bank/metadata/song_catalog.json
📊 Total songs in bank: 25
```

---

## 🔄 Quick Reference: What's Manual vs Automated

### ✋ YOU Do Manually:

1. ✅ **Create track template** (1 command)
2. ✅ **Select from bank** (optional, 2 commands)
3. ✅ **Generate songs** in Suno
4. ✅ **Download MP3s** to your computer
5. ✅ **Organize files** into half_1/ and half_2/
6. ✅ **Add video and image** files
7. ✅ **Run build command** (1 command)
8. ✅ **Add to bank** (1 command with interactive prompts)
9. ✅ **Review output** and decide if satisfied

### 🤖 System Does Automatically:

1. ✅ Auto-increment track numbers
2. ✅ Create folder structure
3. ✅ Query song bank
4. ✅ Copy selected songs to correct halves
5. ✅ Apply A_/B_ prefixes (during render only)
6. ✅ Sort songs alphabetically
7. ✅ Render with FFmpeg crossfades
8. ✅ Generate tracklist metadata
9. ✅ Rename songs for bank storage
10. ✅ Update song catalog

---

## 📖 Common Scenarios

### Scenario 1: First Track (Empty Bank)

```bash
# 1. Setup (one time only)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
chmod +x scripts/*.sh agent/*.py

# 2. Create track
./venv/bin/python3 agent/create_track_template.py
# Output: Created tracks/16/

# 3. Generate music in Suno (20-30 songs)

# 4. Organize downloaded files (no prefixes!)
mv ~/Downloads/calm*.mp3 tracks/16/half_1/
mv ~/Downloads/bright*.mp3 tracks/16/half_2/

# 5. Add media
cp background.mp4 tracks/16/video/16.mp4

# 6. Build
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# 7. Review
open rendered/16/output_*/output.mp4

# 8. Add to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

### Scenario 2: Second Track (Using Bank)

```bash
# 1. Create track
./venv/bin/python3 agent/create_track_template.py
# Output: Created tracks/17/

# 2. Select from bank
./venv/bin/python3 agent/select_bank_songs.py --track 17 --count 10 --flow-id 04
./venv/bin/python3 agent/select_bank_songs.py --track 17 --execute
# Copied 10 songs to half_1/ and half_2/

# 3. Generate NEW music in Suno (10-15 songs)

# 4. Add new songs
mv ~/Downloads/new*.mp3 tracks/17/half_1/
mv ~/Downloads/other*.mp3 tracks/17/half_2/

# 5. Add media
cp background.mp4 tracks/17/video/17.mp4

# 6. Build
./venv/bin/python3 agent/build_track.py --track 17 --duration 3

# 7. Add NEW songs to bank (not the ones from bank)
./venv/bin/python3 agent/add_to_bank.py --track 17 --flow-id 04
```

---

### Scenario 3: Quick Test

```bash
# 1. Create track
./venv/bin/python3 agent/create_track_template.py

# 2. Add a few test songs
cp ~/Music/test*.mp3 tracks/16/half_1/

# 3. Add video
cp background.mp4 tracks/16/video/16.mp4

# 4. Build 5-minute test
./venv/bin/python3 agent/build_track.py --track 16 --duration test

# 5. Review
open rendered/16/output_*/output.mp4
```

---

### Scenario 4: Select by Duration

```bash
# 1. Create track
./venv/bin/python3 agent/create_track_template.py

# 2. Select 90 minutes from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 90 --flow-id 04
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute

# 3. Generate 90 more minutes in Suno

# 4. Add new songs
mv ~/Downloads/*.mp3 tracks/16/half_1/  # or half_2/

# 5. Build with auto duration (total = ~3 hours)
./venv/bin/python3 agent/build_track.py --track 16

# 6. Add to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

## ⚠️ Important Notes

### File Naming in Track Folders

**You DON'T need to:**
- ❌ Add A_ or B_ prefixes yourself
- ❌ Use any specific naming format
- ❌ Number files (unless you want to control order)

**You CAN:**
- ✅ Use descriptive names: `calm_intro.mp3`, `bright_finale.mp3`
- ✅ Number if desired: `01_song.mp3`, `02_song.mp3`
- ✅ Use Suno's default names
- ✅ Rename to control alphabetical order

### half_1 vs half_2

**Think of it as:**
- **half_1**: Build-up, introduction, setting the mood
- **half_2**: Peak, resolution, wind-down

**Not strict rules:**
- You can organize however makes sense for your track
- The A_/B_ prefixes are just for render order
- half_1 plays first, half_2 plays second

### Bank Songs vs New Songs

**Bank songs:**
- Already have metadata (phase, BPM, etc.)
- Get copied to tracks, not moved
- Original stays in bank

**New songs:**
- Generated fresh in Suno
- Added to track folders
- Can be added to bank after render
- Then become available for future tracks

### Duration

**Auto mode (recommended):**
- Uses total duration of all songs
- No looping needed
- Exact length of your content

**Custom duration:**
- Loops songs if total < target
- Truncates if total > target
- Good for fixed-length requirements

---

## 🆘 Troubleshooting

### "Track already exists"
**Problem:** Template creation says track exists
**Solution:**
```bash
# Check existing tracks
ls tracks/

# Delete if needed, or specify different number
rm -rf tracks/16
./venv/bin/python3 agent/create_track_template.py --track-number 16
```

### "No songs in half_1/ or half_2/"
**Problem:** Build says no songs found
**Solution:**
```bash
# Check if files are there
ls tracks/16/half_1/
ls tracks/16/half_2/

# Make sure they're MP3s
find tracks/16 -name "*.mp3"
```

### "Background video not found"
**Problem:** Build can't find video
**Solution:**
```bash
# Check video location
ls tracks/16/video/

# Make sure named correctly: <number>.mp4
cp background.mp4 tracks/16/video/16.mp4
```

### "Song already in bank"
**Problem:** add_to_bank says song already exists
**Solution:** This is correct! The system detected a duplicate. It won't add songs that are already in the bank.

### "ModuleNotFoundError"
**Problem:** Python packages not found
**Solution:**
```bash
# Re-activate venv and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ Minimal Checklist

To create a 3-hour mix, you need to:

- [ ] Run setup (first time only)
- [ ] Create track template (1 command)
- [ ] Select from bank OR skip if empty
- [ ] Generate songs in Suno
- [ ] Download and organize into half_1/ and half_2/
- [ ] Add background video
- [ ] Run build command
- [ ] Review output
- [ ] Add new songs to bank

**Total commands:** 4-6 depending on bank usage
**Total time:** ~20 minutes (excluding Suno generation)

---

## 💡 Pro Tips

1. **Batch Generate:** Generate all songs at once in Suno before starting
2. **Name for Order:** Use `01_`, `02_` prefixes if you want specific order
3. **Test First:** Always test with `--duration test` before full 3-hour render
4. **Bank Strategically:** Only add songs you'd reuse (high quality, good for themes)
5. **Use Flow IDs:** Consistent flow IDs help with themed track selection
6. **Backup Bank:** The `song_bank/` folder is valuable - back it up
7. **Track Metadata:** Update `tracks/<num>/metadata.json` with notes about theme/mood

---

## 🎓 Complete Example: Track 16

```bash
# === Day 1: Setup ===
cd ~/Projects/static-dreamwaves
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x scripts/*.sh agent/*.py

# === Day 2: Create & Plan ===
./venv/bin/python3 agent/create_track_template.py
# Created tracks/16/

# Decide: "Neon Rain Calm" theme
# - 20 songs total
# - half_1: Calm intro → building energy (10 songs)
# - half_2: Peak energy → reflective fade (10 songs)

# === Day 3: Generate Music ===
# Go to Suno:
# - 10 songs: "ambient synthwave, neon rain, calm atmosphere"
# - 10 songs: "bright synthwave, neon rain, reflective fade"
# Download all to ~/Downloads/

# === Day 4: Organize & Build ===
source venv/bin/activate

# Organize songs
mv ~/Downloads/Ambient*.mp3 tracks/16/half_1/
mv ~/Downloads/Bright*.mp3 tracks/16/half_2/

# Add media
cp ~/Videos/neon_rain_bg.mp4 tracks/16/video/16.mp4
cp ~/Images/neon_cover.jpg tracks/16/image/16.jpg

# Build
./venv/bin/python3 agent/build_track.py --track 16 --duration 3
# Wait 5-10 minutes for render...

# === Day 5: Review & Bank ===
# Review output
open rendered/16/output_*/output.mp4

# If satisfied, add to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
# Answer prompts for each song...

# Done! Bank now has 20 songs for future tracks
```

---

**Questions?** See [GETTING_STARTED.md](GETTING_STARTED.md) and [WORKFLOW_COMPLETE.md](../agent/song_sorting_update-11-16-25/WORKFLOW_COMPLETE.md)
