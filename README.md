# 🌌 Static Dreamscapes - Track Production System

> A streamlined pipeline for creating 3-hour Synthwave / Lo-Fi / Vaporwave mixes for the **Static Dreamscapes Lo-Fi YouTube Channel**.
> This system provides a song bank architecture for efficient track creation with reusable songs and automated rendering.

---

## 🎯 Project Purpose

Static Dreamscapes provides a **flexible, efficient workflow** for producing long-form ambient music mixes with:

1. **Song Bank:** Centralized repository of reusable tracks with metadata
2. **Track Templates:** Auto-generated project structure for new mixes
3. **Flexible Selection:** Choose songs by count or duration from the bank
4. **Manual Curation:** Organize songs into first/second halves manually
5. **Automatic Rendering:** Build mixes with crossfades and automatic A_/B_ prefixing
6. **Bank Growth:** Add new songs back to the bank for future reuse

---

## 🧱 Folder Structure

```
static-dreamwaves/
├── agent/                      # Python automation scripts
│   ├── create_track_template.py   # Generate new track folders
│   ├── select_bank_songs.py       # Query and select from bank
│   ├── build_track.py             # Build mix with auto-prefixing
│   ├── build_mix.py               # Python FFmpeg renderer
│   └── add_to_bank.py             # Add songs to bank
│
├── scripts/                    # Shell utilities
│   ├── build_mix.sh               # Shell FFmpeg renderer (fast)
│   └── ...
│
├── tracks/                     # Track projects (working directories)
│   └── <number>/
│       ├── half_1/                # Songs for first half (no prefixes)
│       ├── half_2/                # Songs for second half (no prefixes)
│       ├── video/                 # Background video (<number>.mp4)
│       ├── image/                 # Cover art (<number>.jpg)
│       ├── metadata.json          # Track metadata
│       └── bank_selection.json    # Selected songs (auto-generated)
│
├── song_bank/                  # Centralized song repository
│   ├── tracks/                    # Songs organized by source track
│   │   └── <number>/              # Named: A_2_5_016a.mp3
│   ├── track_flows/               # Flow documents (prompts/themes)
│   └── metadata/
│       ├── song_catalog.json      # Master song index
│       └── prompt_index.json      # Prompt references
│
├── rendered/                   # Final rendered mixes
│   └── <number>/
│       └── output_<timestamp>/
│           └── output.mp4
│
└── documentation/              # User-facing guides
    ├── GETTING_STARTED.md
    ├── MANUAL_STEPS.md
    └── ...
```

---

## 🎵 Complete Workflow

### Step 1: Create Track Template

Generate a new track project folder:

```bash
# Auto-increment (if last is 15, creates 16)
./venv/bin/python3 agent/create_track_template.py

# Or specify number
./venv/bin/python3 agent/create_track_template.py --track-number 20
```

**Creates:**
- `tracks/<number>/half_1/` - Songs for first half
- `tracks/<number>/half_2/` - Songs for second half
- `tracks/<number>/video/` - Background video
- `tracks/<number>/image/` - Cover art
- `tracks/<number>/metadata.json` - Track metadata

---

### Step 2: Select Songs from Bank (Optional)

Pull songs from the bank by count or duration:

```bash
# Select 5 songs from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04

# Or select ~30 minutes of songs
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04

# Execute the selection (copies files)
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

---

### Step 3: Add New Songs Manually

Generate songs in Suno and add to track folders:

```bash
# Add songs to first half
mv ~/Downloads/new_song_*.mp3 tracks/16/half_1/

# Add songs to second half
mv ~/Downloads/other_song_*.mp3 tracks/16/half_2/
```

**Important:** Songs do NOT need A_/B_ prefixes at this stage. Organize them into half_1/ and half_2/ as desired.

---

### Step 4: Add Video and Image

```bash
# Copy background video
cp ~/path/to/background.mp4 tracks/16/video/16.mp4

# Copy cover art
cp ~/path/to/cover.jpg tracks/16/image/16.jpg
```

---

### Step 5: Build Track

Build the final mix with automatic A_/B_ prefixing:

```bash
# Python version (recommended)
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# Or shell version (faster startup)
bash scripts/build_mix.sh 16 3

# Test mode (5 minutes)
./venv/bin/python3 agent/build_track.py --track 16 --duration test
```

**What happens:**
- Songs from `half_1/` get A_ prefixes (A_001, A_002, etc.)
- Songs from `half_2/` get B_ prefixes (B_001, B_002, etc.)
- FFmpeg renders with crossfades
- Output saved to `rendered/16/output_<timestamp>/output.mp4`

---

### Step 6: Add New Songs to Bank

After a successful render, add new songs to the bank:

```bash
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

**Interactive prompts:**
- Half (A/B)
- Phase (1-4: Calm, Flow, Uplift, Reflect)
- Song number within phase
- Order letter (a, b, c...)

**Output:** Songs copied to `song_bank/tracks/16/` with proper naming (e.g., `A_2_5_016a.mp3`)

---

## 🎯 Song Naming Convention

Bank songs use the format: **`A_2_5_016a.mp3`**

- `A` = Half (A = first half, B = second half)
- `2` = Phase (1=Calm, 2=Flow, 3=Uplift, 4=Reflect)
- `5` = Song number within phase
- `016` = Source track number (zero-padded)
- `a` = Order letter (a, b, c... for variations)

---

## 🔧 Quick Start

### Initial Setup (One-Time)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make scripts executable
chmod +x scripts/*.sh agent/*.py
```

### Create Your First Track

```bash
# 1. Create track template
./venv/bin/python3 agent/create_track_template.py

# 2. Add songs (from Suno downloads)
mv ~/Downloads/*.mp3 tracks/16/half_1/

# 3. Add video
cp background.mp4 tracks/16/video/16.mp4

# 4. Build (auto duration = total songs length)
./venv/bin/python3 agent/build_track.py --track 16

# 5. Add to bank for future use
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [GETTING_STARTED.md](documentation/GETTING_STARTED.md) | Complete setup and first track guide |
| [MANUAL_STEPS.md](documentation/MANUAL_STEPS.md) | What YOU do vs what's automated |
| [WORKFLOW_COMPLETE.md](agent/song_sorting_update-11-16-25/WORKFLOW_COMPLETE.md) | Complete workflow reference |
| [BUILD_MIX_COMPARISON.md](documentation/BUILD_MIX_COMPARISON.md) | Shell vs Python build scripts |
| [YARN_COMMANDS.md](documentation/YARN_COMMANDS.md) | Yarn/NPM command reference |

---

## 🎨 Four-Phase Emotional Arc

Each track can follow a four-phase structure:

| Phase | Description | BPM Range |
|-------|-------------|-----------|
| **1: Calm Intro** | Ambient, nostalgic, warm opening | 70-80 |
| **2: Flow/Focus** | Steady mid-tempo, sustained attention | 80-90 |
| **3: Uplift/Clarity** | Bright, optimistic, creative momentum | 90-100 |
| **4: Reflective Fade** | Slow, analog-warm closing | 60-75 |

This structure is optional and tracked via the `phase` metadata when adding songs to the bank.

---

## 🚀 Key Features

### Song Bank System
- ✅ Centralized repository of reusable tracks
- ✅ Metadata tracking (BPM, phase, theme, prompts)
- ✅ Query by count, duration, flow ID, or theme
- ✅ Prevents duplication via catalog

### Flexible Workflow
- ✅ Mix bank songs with new songs
- ✅ Manual organization (half_1/ and half_2/)
- ✅ No prefixes needed until render
- ✅ Auto-incrementing track numbers

### Intelligent Rendering
- ✅ Automatic A_/B_ prefixing during build
- ✅ FFmpeg crossfades (5s overlap)
- ✅ Volume boost (1.75x)
- ✅ Fade in/out
- ✅ Auto or custom duration

### Metadata Tracking
- ✅ Track metadata (metadata.json)
- ✅ Song catalog (song_catalog.json)
- ✅ Prompt index for themes
- ✅ Build history and tracklists

---

## 🔄 Build Options

### Duration Modes

```bash
# Auto: Use total song duration
./venv/bin/python3 agent/build_track.py --track 16

# Custom: Specify in hours
./venv/bin/python3 agent/build_track.py --track 16 --duration 3

# Test: 5 minutes
./venv/bin/python3 agent/build_track.py --track 16 --duration test
```

### Shell vs Python

**Python** (`agent/build_mix.py`):
- More readable code
- Better error handling
- Easy to extend

**Shell** (`scripts/build_mix.sh`):
- Faster startup
- Minimal dependencies
- Direct FFmpeg control

See [BUILD_MIX_COMPARISON.md](documentation/BUILD_MIX_COMPARISON.md) for details.

---

## 🧰 Development Notes

- **Track numbers auto-increment** - System finds highest number and creates next
- **Songs stay unprefixed** until render - Easier to reorganize and modify
- **Bank songs are immutable** - Once in bank, they're preserved with metadata
- **Flexible selection** - Pull any number of songs or specific duration
- **Metadata is key** - Track themes, flows, and prompts for smart selection

---

## 🎯 Example: Complete Workflow

```bash
# === Setup (one time) ===
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x scripts/*.sh agent/*.py

# === Create Track 16 ===
./venv/bin/python3 agent/create_track_template.py
# Output: Created tracks/16/

# === Select from Bank (if bank has songs) ===
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
# Copied 5 songs to half_1/ and half_2/

# === Add New Songs ===
# Generate in Suno, download to ~/Downloads/
mv ~/Downloads/new_*.mp3 tracks/16/half_1/
mv ~/Downloads/other_*.mp3 tracks/16/half_2/

# === Add Media ===
cp background.mp4 tracks/16/video/16.mp4
cp cover.jpg tracks/16/image/16.jpg

# === Build ===
./venv/bin/python3 agent/build_track.py --track 16 --duration 3
# Output: rendered/16/output_20251119_103000/output.mp4

# === Add to Bank ===
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
# Prompts for metadata, copies to song_bank/

# === Create Next Track ===
./venv/bin/python3 agent/create_track_template.py
# Output: Created tracks/17/ (auto-incremented)
```

---

## 🛠️ Script Reference

| Script | Purpose |
|--------|---------|
| `create_track_template.py` | Generate new track folder |
| `select_bank_songs.py` | Query and select from bank |
| `build_track.py` | Build mix (Python) |
| `build_mix.sh` | Build mix (Shell) |
| `add_to_bank.py` | Add songs to bank |

---

## 🌟 Future Enhancements

- [ ] Smart song selection (BPM matching, phase balance)
- [ ] Theme-based filtering
- [ ] Automatic emotional arc generation
- [ ] Web UI for bank management
- [ ] Track flow document parser
- [ ] YouTube auto-upload integration

---

**© 2025 Static Dreamscapes Lo-Fi**
Developed by Patrick Lake — Track Production System
