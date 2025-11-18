# 🎯 Auto-Sort Guide

**Intelligent automatic phase sorting for your tracks!**

The auto-sort feature analyzes your tracks and automatically moves them to the correct phase folder based on BPM, brightness, and energy characteristics.

---

## 🚀 Quick Start

### Option 1: Sort from Downloads Folder

```bash
# Preview what would happen (safe)
yarn sort:downloads:dry

# Actually sort and move files
yarn sort:downloads
```

### Option 2: Sort from Custom Folder

```bash
# 1. Put all your unsorted tracks in unsorted_tracks/
cp ~/Music/*.mp3 unsorted_tracks/

# 2. Preview sorting
yarn sort:unsorted:dry

# 3. Actually sort
yarn sort:unsorted
```

---

## 🧠 How It Works

The system analyzes each track and scores it against all 4 phases based on:

### Phase 1: Calm Intro (70-80 BPM)
- **BPM:** 60-80
- **Tone:** Warm/dark (low brightness)
- **Energy:** Low (calm, ambient)
- **Keywords:** calm, ambient, warm, nostalgic, slow, intro

### Phase 2: Flow Focus (80-90 BPM)
- **BPM:** 80-90
- **Tone:** Balanced
- **Energy:** Moderate (steady groove)
- **Keywords:** focus, steady, work, flow, groove, midtempo

### Phase 3: Uplift Clarity (90-105 BPM)
- **BPM:** 90-105
- **Tone:** Bright (high brightness)
- **Energy:** High (energetic, uplifting)
- **Keywords:** bright, uplift, optimistic, energetic, clarity

### Phase 4: Reflective Fade (55-75 BPM)
- **BPM:** 55-75
- **Tone:** Warm/dark (low brightness)
- **Energy:** Low (slow, reflective)
- **Keywords:** fade, slow, reflective, ending, outro, tape

---

## 📊 Example Output

```
================================================================================
📀 morning_ambient_track.mp3
================================================================================
  Analyzing: morning_ambient_track.mp3

  🎯 Best Match: Calm Intro
  📊 Confidence: 95%
  💡 Reasoning: BPM 72 in range [60-80], warm/dark tone, low energy
  📈 Features: BPM=72, Brightness=1847, Energy=0.045
  📁 Destination: arc_library/phase_1_calm_intro/ambient_warmth/
  ✅ Moved successfully

================================================================================
📀 energetic_bright_synth.mp3
================================================================================
  Analyzing: energetic_bright_synth.mp3

  🎯 Best Match: Uplift Clarity
  📊 Confidence: 88%
  💡 Reasoning: BPM 98 in range [90-105], bright tone, high energy
  📈 Features: BPM=98, Brightness=3421, Energy=0.782
  📁 Destination: arc_library/phase_3_uplift_clarity/bright_pads/
  ✅ Moved successfully
```

---

## 🎮 Usage Examples

### Example 1: Sort Everything from Downloads

```bash
# Step 1: Download all your Suno tracks to ~/Downloads

# Step 2: Preview what will happen
yarn sort:downloads:dry

# Step 3: Review the output, check confidence scores

# Step 4: If satisfied, run for real
yarn sort:downloads

# Step 5: Continue with normal pipeline
yarn run
```

### Example 2: Sort from Custom Folder

```bash
# Step 1: Create folder and add tracks
mkdir -p unsorted_tracks
cp ~/Music/my_tracks/*.mp3 unsorted_tracks/

# Step 2: Preview
yarn sort:unsorted:dry

# Step 3: Sort
yarn sort:unsorted

# Step 4: Run pipeline
yarn run
```

### Example 3: Manual Sort with Custom Path

```bash
# Direct command for any folder
./venv/bin/python3 agent/auto_sort.py --input /path/to/tracks --dry-run
./venv/bin/python3 agent/auto_sort.py --input /path/to/tracks
```

---

## 🔍 Understanding Confidence Scores

**90-100%:** Excellent match
- All criteria align perfectly
- Filename keywords match
- Very confident placement

**80-89%:** Good match
- Most criteria align
- Minor deviation in one metric
- Likely correct placement

**70-79%:** Fair match
- Some criteria don't align perfectly
- Worth manually reviewing
- May need adjustment

**<70%:** Weak match
- Significant deviation from phase criteria
- Definitely review manually
- May be edge case or unusual track

---

## 🎯 Smart Features

### Filename Keyword Detection

If your filename contains phase-related keywords, the system boosts confidence:

```
calm_ambient_track.mp3        → Likely Phase 1 (keyword: calm)
focused_work_beats.mp3        → Likely Phase 2 (keyword: focus, work)
bright_optimistic_synth.mp3   → Likely Phase 3 (keyword: bright, optimistic)
slow_fade_outro.mp3           → Likely Phase 4 (keyword: slow, fade, outro)
```

### Multi-Factor Analysis

The system combines multiple factors:
1. **BPM matching** (primary factor)
2. **Brightness** (spectral centroid - tone quality)
3. **Energy** (RMS - loudness/intensity)
4. **Filename keywords** (contextual hints)

### Intelligent Scoring

- Tracks are scored against ALL phases
- Best match wins
- Tolerances allow for flexibility
- Close scores indicate boundary tracks

---

## ⚠️ Important Notes

### What Gets Moved

- ✅ Only `.mp3` files
- ✅ Searches recursively in subdirectories
- ✅ Preserves original filename

### What Doesn't Get Moved

- ❌ Files already in arc_library phase folders
- ❌ Files with names that already exist at destination
- ❌ Files that fail audio analysis

### Safety Features

- **Dry run mode** always available
- **No overwrites** - skips if file exists
- **Error handling** - continues on individual failures
- **Summary report** - see exactly what happened

---

## 🛠️ Troubleshooting

### "No MP3 files found"

**Problem:** Command says 0 files found

**Solution:**
```bash
# Check directory exists and has MP3s
ls -la unsorted_tracks/*.mp3
# or
ls -la ~/Downloads/*.mp3
```

### "Analysis failed"

**Problem:** Track fails to analyze

**Possible causes:**
- Corrupted MP3 file
- Unusual format/encoding
- Very short duration

**Solution:**
- Skip that file
- Try re-downloading from Suno
- Convert to standard MP3 format

### Low Confidence Scores

**Problem:** All tracks getting <70% confidence

**Solution:**
- These might be unusual/experimental tracks
- Review the reasoning output
- Consider manual placement
- Tracks with unusual BPM/style may not fit cleanly

### Files Not Moving

**Problem:** Dry run looks good but real run doesn't work

**Solution:**
```bash
# Check permissions
chmod +x agent/auto_sort.py

# Check venv is activated
./venv/bin/python3 --version

# Run with verbose output
./venv/bin/python3 agent/auto_sort.py --input unsorted_tracks
```

---

## 📊 After Sorting

Once tracks are sorted, continue with normal workflow:

```bash
# Option 1: Watch mode (auto-trigger)
yarn watch

# Option 2: Manual run
yarn run

# Option 3: Step by step
yarn rename:all
yarn prepend
yarn analyze:manual
yarn verify:length
yarn build:3h
```

---

## 💡 Pro Tips

1. **Use dry run first** - Always preview before moving
2. **Check confidence** - Review tracks with <80% confidence
3. **Filename matters** - Name tracks with phase hints if possible
4. **Batch process** - Sort all tracks at once for consistency
5. **Review boundaries** - Tracks at phase boundaries (80 BPM, 90 BPM) may vary
6. **Trust the system** - 85%+ confidence is usually correct
7. **Manual override** - You can always move files manually if needed

---

## 🎓 Understanding the Phases

### Phase Transitions

The system handles boundary cases intelligently:

- **78-82 BPM:** Could be Phase 1 or Phase 2
  - Warmer tone → Phase 1
  - More energy → Phase 2

- **88-92 BPM:** Could be Phase 2 or Phase 3
  - Balanced tone → Phase 2
  - Brighter tone → Phase 3

- **73-77 BPM:** Could be Phase 1 or Phase 4
  - Earlier in mix (calm intro) → Phase 1
  - Later in mix (reflective) → Phase 4

### Edge Cases

Some tracks don't fit neatly:

**Very slow (<60 BPM):**
- Usually goes to Phase 4
- Could be ambient intro for Phase 1

**Very fast (>100 BPM):**
- Usually still Phase 3
- Consider if it matches the "uplift" vibe

**Mid-tempo experimental:**
- System will choose best match
- Lower confidence score
- Good candidate for manual review

---

## 🧪 Testing

Want to test with a few files first?

```bash
# Create test folder
mkdir -p test_sort
cp path/to/3-tracks.mp3 test_sort/

# Test sort
./venv/bin/python3 agent/auto_sort.py --input test_sort --dry-run

# If good, run for real
./venv/bin/python3 agent/auto_sort.py --input test_sort
```

---

## 📚 Related Documentation

- [MANUAL_STEPS.md](MANUAL_STEPS.md) - What to do manually
- [YARN_COMMANDS.md](YARN_COMMANDS.md) - All available commands
- [GETTING_STARTED.md](GETTING_STARTED.md) - Initial setup
- [CLAUDE.md](../CLAUDE.md) - Technical architecture

---

**Questions?** The auto-sorter analyzes 60 seconds of each track to determine BPM, brightness, and energy. This is fast and accurate for most tracks!
