# 👤 Manual Steps Required

This document outlines **what YOU need to do manually** vs. what the automation handles.

---

## 🎯 The Big Picture

**You do:** Create music and organize files
**System does:** Everything else (rename, analyze, render, track metadata)

---

## 📋 Complete Manual Workflow

### Step 1: Initial Setup (One-Time Only)

```bash
# Clone/navigate to project
cd /path/to/static-dreamwaves

# Run setup
yarn setup
```

**What this does:**
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Makes scripts executable

**You need to do this:** Once per machine/installation

---

### Step 2: Generate Music (Suno)

**What YOU do:**
1. Go to Suno AI
2. Generate your songs with prompts matching the 4 phases:
   - **Phase 1 (Calm Intro)**: Ambient, nostalgic, warm (70-80 BPM)
   - **Phase 2 (Flow Focus)**: Steady, focused, rhythmic (80-90 BPM)
   - **Phase 3 (Uplift Clarity)**: Bright, optimistic, energetic (90-100 BPM)
   - **Phase 4 (Reflective Fade)**: Slow, reflective, closing (60-75 BPM)
3. Download all MP3 files to your Downloads folder

**Example Suno Prompts:**
```
Phase 1: "ambient lo-fi synthwave, warm analog pads, nostalgic atmosphere, 75 bpm"
Phase 2: "steady synthwave beat, focused energy, analog pulse, 85 bpm"
Phase 3: "bright synthwave melody, optimistic uplifting, creative energy, 95 bpm"
Phase 4: "slow reflective synthwave, tape hiss, warm fadeout, 65 bpm"
```

**Target:** ~24 songs total (6 per phase) for a 3-hour mix

---

### Step 3: Organize Files by Phase

> **🎯 NEW: Auto-Sort Feature!** You can now automatically sort tracks into phases based on BPM and audio analysis. See below for both options.

#### Option A: Auto-Sort (Recommended for Lots of Tracks)

**What YOU do:**
```bash
# Preview what will happen (safe)
yarn sort:downloads:dry

# Actually sort and move files
yarn sort:downloads
```

**What the system does:**
- ✅ Analyzes BPM, brightness, and energy for each track
- ✅ Scores each track against all 4 phases
- ✅ Moves files to best-matching phase folder
- ✅ Shows confidence scores and reasoning

See [AUTO_SORT_GUIDE.md](AUTO_SORT_GUIDE.md) for complete guide!

#### Option B: Manual Organization

**What YOU do:**
Manually move/copy downloaded MP3s into the correct phase folders:

```bash
# Option A: Using Finder/File Explorer
# Drag and drop files into:
arc_library/phase_1_calm_intro/ambient_warmth/
arc_library/phase_2_flow_focus/midtempo_groove/
arc_library/phase_3_uplift_clarity/bright_pads/
arc_library/phase_4_reflective_fade/vapor_trails/

# Option B: Using terminal
mv ~/Downloads/calm_track_*.mp3 arc_library/phase_1_calm_intro/ambient_warmth/
mv ~/Downloads/focus_track_*.mp3 arc_library/phase_2_flow_focus/midtempo_groove/
mv ~/Downloads/bright_track_*.mp3 arc_library/phase_3_uplift_clarity/bright_pads/
mv ~/Downloads/fade_track_*.mp3 arc_library/phase_4_reflective_fade/vapor_trails/
```

**Tips:**
- You can organize into any subfolder within each phase
- The system will find all MP3s regardless of subfolder
- Original filenames don't matter - they'll be renamed automatically
- Organize by mood/vibe within each phase if you want

**Example Organization:**
```
arc_library/
├── phase_1_calm_intro/
│   ├── ambient_warmth/
│   │   ├── rainy_morning.mp3
│   │   └── soft_glow.mp3
│   ├── early_dawn/
│   │   └── sunrise_haze.mp3
│   └── nostalgic_haze/
│       └── memory_drift.mp3
├── phase_2_flow_focus/
│   └── midtempo_groove/
│       ├── city_flow.mp3
│       ├── desk_work.mp3
│       └── steady_pulse.mp3
...
```

---

### Step 4: Start Automation

**Option A: Automatic Watch Mode (Recommended)**

```bash
yarn watch
```

**What happens:**
- ✅ System watches for file changes
- ✅ Waits 60 seconds after you add the last file
- ✅ Automatically runs entire pipeline
- ✅ You can walk away!

**When to use:** When you're done adding all files and want hands-off processing

---

**Option B: Manual Trigger**

```bash
yarn run
```

**What happens:**
- ✅ Runs pipeline immediately (no waiting)
- ✅ Good for testing or scheduled runs

**When to use:** When you want immediate processing or running via cron/scheduler

---

### Step 5: Wait for Processing

**What the system does automatically:**

1. **Rename** (2-5 seconds)
   - Sorts files by modification time
   - Renames to `001_track.mp3`, `002_track.mp3`, etc.

2. **Prefix** (1-2 seconds)
   - Adds `A_` or `B_` prefixes
   - Example: `A_001_track.mp3`

3. **Analyze** (30-60 seconds)
   - Extracts BPM, key, brightness, RMS
   - Updates metadata JSON files

4. **Verify** (3-5 seconds)
   - Checks total duration ≈ 3 hours
   - Warns if too short/long

5. **Build** (2-3 minutes)
   - Renders final mix with crossfades
   - Saves to `rendered/` folder

**Total time:** ~3-5 minutes for 24 songs

---

### Step 6: Review Output

**What YOU do:**

1. **Check the logs:**
   ```bash
   yarn logs:last
   ```

2. **Find your rendered mix:**
   ```bash
   ls -lh rendered/1/output_*/output.mp4
   ```

3. **Play it back:**
   - Open the MP4 file in your video/audio player
   - Verify quality, crossfades, and flow

4. **Check metadata:**
   ```bash
   yarn status
   cat metadata/build_history.json
   ```

---

## 🔄 Quick Reference: What's Manual vs Automated

### ✋ YOU Do Manually:

1. ✅ **Generate songs** in Suno
2. ✅ **Download MP3s** to your computer
3. ✅ **Organize files** into phase folders
4. ✅ **Run command** (`yarn watch` or `yarn run`)
5. ✅ **Review output** and decide if satisfied

### 🤖 System Does Automatically:

1. ✅ Rename files chronologically
2. ✅ Add phase prefixes
3. ✅ Extract audio features
4. ✅ Validate total length
5. ✅ Render with crossfades
6. ✅ Update metadata
7. ✅ Track build history

---

## 📖 Common Scenarios

### Scenario 1: First Time Creating a Mix

```bash
# 1. Setup (one time only)
yarn setup

# 2. Generate music in Suno (6 songs per phase = 24 total)

# 3. Organize downloaded files
mv ~/Downloads/*.mp3 Arc_Library/Phase_X_*/

# 4. Start automation
yarn watch

# 5. Wait ~5 minutes

# 6. Review output
ls rendered/
```

---

### Scenario 2: Adding More Tracks Later

```bash
# 1. Generate new songs in Suno

# 2. Add to existing folders
mv ~/Downloads/new_track*.mp3 arc_library/phase_1_calm_intro/ambient_warmth/

# 3. Re-run pipeline
yarn run

# 4. New analysis and metadata updates happen automatically
```

---

### Scenario 3: Testing with Existing Files

```bash
# 1. Already have some test MP3s?
cp ~/Music/test*.mp3 arc_library/phase_1_calm_intro/ambient_warmth/

# 2. Quick test run
yarn run

# 3. Build 5-minute test mix
yarn build:test

# 4. Check output
open rendered/1/output_*/output.mp4
```

---

### Scenario 4: Manual Step-by-Step (More Control)

```bash
# 1. Organize files (you do this)

# 2. Preview what will happen (optional)
yarn rename:all:dry

# 3. Rename manually
yarn rename:all

# 4. Add prefixes
yarn prepend

# 5. Analyze
yarn analyze:manual

# 6. Check length
yarn verify:length
cat total_length.txt

# 7. Build test (5 min)
yarn build:test

# 8. If good, build full (3 hours)
yarn build:3h
```

---

## ⚠️ Important Notes

### File Naming

**You DON'T need to:**
- ❌ Name files in any specific format
- ❌ Add numbers or prefixes yourself
- ❌ Sort files manually
- ❌ Rename anything

**The system handles all naming automatically!**

### File Organization

**You DO need to:**
- ✅ Put files in correct phase folders
- ✅ Ensure files are actually MP3 format
- ✅ Use subfolders within phases if you want (optional)

### Duration

**Target:** ~3 hours total (10,800 seconds)

**Typical breakdown:**
- Phase 1: 45 minutes (4-6 songs)
- Phase 2: 60 minutes (6-8 songs)
- Phase 3: 45 minutes (4-6 songs)
- Phase 4: 30 minutes (3-5 songs)

**System will warn you if:**
- Total is less than 2h 59m
- Total is more than 3h 01m

### Adding Video

If you want video with your audio (for YouTube):

**What YOU do:**
1. Create/find a background video
2. Place at: `tracks/<number>/video/<number>.mp4`
3. Copy MP3s to: `tracks/<number>/songs/`
4. Run: `bash scripts/build_mix.sh <number> 3`

**Example:**
```bash
# Setup
mkdir -p tracks/5/video tracks/5/songs
cp background.mp4 tracks/5/video/5.mp4
cp arc_library/phase_*/*.mp3 tracks/5/songs/

# Build
bash scripts/build_mix.sh 5 3

# Output
ls rendered/5/output_*/output.mp4
```

---

## 🆘 Troubleshooting

### "No files found"
**Problem:** System says 0 MP3 files
**Solution:**
```bash
# Check if files are actually there
find arc_library -name "*.mp3"

# Should show your files
```

### "Duration too short"
**Problem:** Total mix is under 3 hours
**Solution:** Generate and add more songs, then re-run

### "ModuleNotFoundError"
**Problem:** Python packages not found
**Solution:**
```bash
# Re-run setup
yarn setup

# Or manually
source venv/bin/activate
pip install -r requirements.txt
```

### "Permission denied"
**Problem:** Scripts won't execute
**Solution:**
```bash
yarn setup:permissions
# Or manually: chmod +x scripts/*.sh agent/*.py
```

---

## ✅ Minimal Checklist

To create a 3-hour mix, you need to:

- [ ] Run `yarn setup` (first time only)
- [ ] Generate ~24 songs in Suno
- [ ] Download MP3 files
- [ ] Move files to `arc_library/phase_X_*/` folders
- [ ] Run `yarn watch` or `yarn run`
- [ ] Wait ~5 minutes
- [ ] Find output in `rendered/` folder

**That's it!** Everything else is automated.

---

## 💡 Pro Tips

1. **Batch Process:** Generate all 24 songs at once in Suno, then add them all at once
2. **Use Watch Mode:** Start `yarn watch` before adding files, system will auto-detect
3. **Test First:** Use `yarn build:test` for 5-minute test before full 3-hour render
4. **Validate Often:** Run `yarn verify:metadata` to ensure everything is in sync
5. **Monitor Logs:** Keep `yarn logs` running in another terminal to watch progress
6. **Backup Metadata:** The `metadata/` folder is valuable - back it up occasionally

---

## 🎓 Example: Complete First Mix

Here's a real-world example of creating your first mix from scratch:

```bash
# Day 1: Setup
cd ~/Projects/static-dreamwaves
yarn setup

# Day 2: Generate Music
# - Go to Suno
# - Generate 6 calm tracks (Phase 1)
# - Generate 8 focus tracks (Phase 2)
# - Generate 6 bright tracks (Phase 3)
# - Generate 4 fade tracks (Phase 4)
# - Download all 24 MP3s

# Day 3: Process
# Start watch mode first
yarn watch

# In another terminal or Finder, organize files
mv ~/Downloads/*calm*.mp3 arc_library/phase_1_calm_intro/ambient_warmth/
mv ~/Downloads/*focus*.mp3 arc_library/phase_2_flow_focus/midtempo_groove/
mv ~/Downloads/*bright*.mp3 arc_library/phase_3_uplift_clarity/bright_pads/
mv ~/Downloads/*fade*.mp3 arc_library/phase_4_reflective_fade/vapor_trails/

# Wait 60 seconds... system auto-processes!
# Check logs
yarn logs:last

# Day 4: Review & Upload
open rendered/1/output_*/output.mp4
# Upload to YouTube if satisfied!
```

---

**Questions?** See [GETTING_STARTED.md](GETTING_STARTED.md) and [YARN_COMMANDS.md](YARN_COMMANDS.md)
