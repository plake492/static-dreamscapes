# 📜 Yarn Commands Reference

Complete reference for all Yarn/NPM commands in the Static Dreamscapes track production system.

---

## 🚀 Quick Start

```bash
# First time setup
yarn setup

# Show all available commands
yarn help

# Create a new track
yarn track:create
```

---

## 📋 Complete Command List

### 🛠️ Setup & Installation

#### `yarn setup`
Complete one-time setup for the project.

**Usage:**
```bash
yarn setup
```

**What it does:**
1. Creates Python virtual environment (`venv/`)
2. Upgrades pip to latest version
3. Installs all dependencies from `requirements.txt`
4. Makes all scripts executable (`chmod +x`)

**When to run:**
- First time setting up project
- After cloning repository
- After major dependency updates

---

#### `yarn setup:deps`
Reinstall Python dependencies only.

**Usage:**
```bash
yarn setup:deps
```

**When to use:**
- After updating `requirements.txt`
- If dependencies are corrupted
- After Python version upgrade

---

#### `yarn setup:permissions`
Fix script permissions.

**Usage:**
```bash
yarn setup:permissions
```

**When to use:**
- If you get "Permission denied" errors
- After pulling new scripts from git

---

## 🏗️ Track Creation

### `yarn track:create`
Create a new track with auto-incrementing number.

**Usage:**
```bash
yarn track:create
```

**What it does:**
- Scans `tracks/` folder for highest track number
- Creates next track folder (e.g., if 15 exists, creates 16)
- Generates folder structure: `half_1/`, `half_2/`, `video/`, `image/`
- Creates `metadata.json` and `README.md`

**Example:**
```bash
$ yarn track:create
✅ Track 16 template created successfully!
```

---

### `yarn track:create:num <number>`
Create a track with a specific number.

**Usage:**
```bash
yarn track:create:num 20
```

**When to use:**
- Creating non-sequential track numbers
- Recreating a deleted track
- Starting with a specific number

---

## 🏦 Song Bank Management

### Select Songs from Bank

**Select by count:**
```bash
./venv/bin/python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04
```

**Select by duration:**
```bash
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04
```

**What it does:**
- Queries `song_catalog.json` for available songs
- Filters by flow ID (if specified)
- Selects N songs OR ~X minutes of songs
- Saves selection to `tracks/<number>/bank_selection.json`

---

### Execute Bank Selection

```bash
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute
```

**What it does:**
- Reads `bank_selection.json`
- Copies selected songs to `half_1/` or `half_2/` based on song metadata
- Marks selection as executed

---

### Add Songs to Bank

```bash
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

**What it does:**
- Scans `half_1/` and `half_2/` for new songs
- Prompts interactively for metadata
- Generates bank filenames (e.g., `A_2_5_016a.mp3`)
- Copies to `song_bank/tracks/<number>/`
- Updates `song_catalog.json`

**Optional flags:**
- `--analyze`: Run audio analysis (requires librosa)
- `--auto`: Use default metadata (for testing)

---

### `yarn bank:status`
Show song bank statistics.

**Usage:**
```bash
yarn bank:status
```

**Example output:**
```bash
=== Song Bank Status ===
Total songs: 25

Files on disk: 25
```

---

## 🎬 Building & Rendering

### `yarn render:auto <track>`
Build mix with auto duration (uses total song length).

**Usage:**
```bash
yarn render:auto 16
```

**What it does:**
- Calculates total duration of all songs
- Builds mix exactly that long (no looping or truncation)
- Best for variable-length content

---

### `yarn render:test <track>`
Build 5-minute test mix.

**Usage:**
```bash
yarn render:test 16
```

**When to use:**
- Quick quality check
- Testing crossfades
- Verifying song order
- Before full 3-hour render

---

### `yarn render:1h <track>`
### `yarn render:2h <track>`
### `yarn render:3h <track>`
Build mix with specific duration.

**Usage:**
```bash
yarn render:1h 16    # 1 hour
yarn render:2h 16    # 2 hours
yarn render:3h 16    # 3 hours
```

**What it does:**
- Loops songs if total duration < target
- Truncates if total duration > target
- Good for fixed-length requirements

---

### `yarn build:py <track> [options]`
Build mix using Python script (recommended).

**Usage:**
```bash
yarn build:py 16                    # Auto duration
yarn build:py 16 --duration 3       # 3 hours
yarn build:py 16 --duration test    # 5 minutes
```

**Features:**
- More readable code
- Better error handling
- Python-native integration
- Easy to extend

---

### `yarn build:sh <track> <duration>`
Build mix using shell script (faster startup).

**Usage:**
```bash
yarn build:sh 16 3       # 3 hours
yarn build:sh 16 test    # 5 minutes
yarn build:sh 16         # Auto duration
```

**Features:**
- Faster startup (~50ms vs ~100ms for Python)
- Minimal dependencies
- Direct FFmpeg control

---

## 📊 Status & Monitoring

### `yarn status`
Show overall system status.

**Usage:**
```bash
yarn status
```

**Example output:**
```bash
=== Tracks ===
Track folders: 3

=== Song Bank ===
Songs in bank: 25

=== Rendered ===
Rendered mixes: 5
```

---

### `yarn status:tracks`
List all track folders and MP3 counts.

**Usage:**
```bash
yarn status:tracks
```

**Example output:**
```bash
tracks/16
tracks/17
tracks/18

Total MP3 files in tracks: 45
```

---

### `yarn status:bank`
Show detailed bank status (alias for `yarn bank:status`).

---

## 🧹 Cleanup Commands

### `yarn clean:rendered`
Clear all rendered output.

**Usage:**
```bash
yarn clean:rendered
```

**⚠️ Caution:** This deletes all files in `rendered/` folder. Backup important mixes first.

---

### `yarn clean:bank`
Reset song bank to empty state.

**Usage:**
```bash
yarn clean:bank
```

**What it does:**
- Deletes all songs from `song_bank/tracks/`
- Resets `song_catalog.json` to empty
- Resets `prompt_index.json` to empty

**⚠️ Caution:** This is destructive! Backup your bank first.

---

### `yarn clean:track <number>`
Delete a specific track folder (manual).

**Usage:**
```bash
rm -rf tracks/16
```

---

## 📖 Complete Workflow Examples

### Example 1: First Track (Empty Bank)

```bash
# 1. Setup (one time)
yarn setup

# 2. Create track
yarn track:create
# Output: Created tracks/16/

# 3. Generate music in Suno, download to ~/Downloads/

# 4. Organize songs (no prefixes!)
mv ~/Downloads/calm*.mp3 tracks/16/half_1/
mv ~/Downloads/bright*.mp3 tracks/16/half_2/

# 5. Add video
cp background.mp4 tracks/16/video/16.mp4

# 6. Build
yarn render:3h 16

# 7. Review
open rendered/16/output_*/output.mp4

# 8. Add to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

### Example 2: Second Track (Using Bank)

```bash
# 1. Create track
yarn track:create
# Output: Created tracks/17/

# 2. Select from bank
./venv/bin/python3 agent/select_bank_songs.py --track 17 --count 10 --flow-id 04
./venv/bin/python3 agent/select_bank_songs.py --track 17 --execute
# Copied 10 songs

# 3. Generate NEW music, add to track
mv ~/Downloads/new*.mp3 tracks/17/half_1/

# 4. Add video
cp background.mp4 tracks/17/video/17.mp4

# 5. Build
yarn render:auto 17

# 6. Add NEW songs to bank
./venv/bin/python3 agent/add_to_bank.py --track 17 --flow-id 04
```

---

### Example 3: Quick Test

```bash
# 1. Create track
yarn track:create

# 2. Add a few test songs
cp ~/Music/test*.mp3 tracks/16/half_1/

# 3. Add video
cp background.mp4 tracks/16/video/16.mp4

# 4. Test build (5 minutes)
yarn render:test 16

# 5. Review
open rendered/16/output_*/output.mp4
```

---

### Example 4: Select by Duration

```bash
# 1. Create track
yarn track:create

# 2. Select 90 minutes from bank
./venv/bin/python3 agent/select_bank_songs.py --track 16 --duration 90 --flow-id 04
./venv/bin/python3 agent/select_bank_songs.py --track 16 --execute

# 3. Generate 90 more minutes in Suno

# 4. Add new songs
mv ~/Downloads/*.mp3 tracks/16/half_1/

# 5. Build with auto duration (total = ~3 hours)
yarn render:auto 16

# 6. Add to bank
./venv/bin/python3 agent/add_to_bank.py --track 16 --flow-id 04
```

---

## 🆘 Troubleshooting

### Commands Not Working

```bash
# Make sure you've run setup first
yarn setup

# Check if venv exists
ls -la venv/

# Verify Python is accessible
./venv/bin/python3 --version

# Re-run setup if needed
yarn setup
```

---

### Permission Errors

```bash
# Fix all script permissions
yarn setup:permissions

# Or manually
chmod +x scripts/*.sh agent/*.py
```

---

### Check Track Structure

```bash
# List tracks
ls -la tracks/

# Check specific track
find tracks/16 -name "*.mp3"
ls tracks/16/video/
ls tracks/16/image/
```

---

### Check Bank Health

```bash
# List bank songs
find song_bank/tracks -name "*.mp3"

# View catalog
cat song_bank/metadata/song_catalog.json

# Count songs
yarn bank:status
```

---

### Check Rendered Output

```bash
# List all renders
find rendered -name "output.mp4"

# Check specific track renders
ls -lh rendered/16/
```

---

## 💡 Pro Tips

**1. Use `yarn help` for quick reference:**
```bash
yarn help
```

**2. Chain commands for efficient workflow:**
```bash
yarn track:create && \
mv ~/Downloads/*.mp3 tracks/16/half_1/ && \
cp background.mp4 tracks/16/video/16.mp4 && \
yarn render:auto 16
```

**3. Test before full render:**
```bash
yarn render:test 16 && open rendered/16/output_*/output.mp4
```

**4. Check status frequently:**
```bash
yarn status && yarn status:tracks && yarn bank:status
```

**5. Backup before cleanup:**
```bash
cp -r song_bank /path/to/backup/
yarn clean:bank
```

**6. Use descriptive filenames:**
```bash
# Name files to control order within each half
mv ~/Downloads/song1.mp3 tracks/16/half_1/01_calm_intro.mp3
mv ~/Downloads/song2.mp3 tracks/16/half_1/02_building_energy.mp3
```

---

## 🔍 Command Syntax Reference

### Track Creation
```bash
yarn track:create                        # Auto-increment
yarn track:create:num 20                 # Specific number
```

### Bank Operations
```bash
# Select (no yarn alias - use Python directly)
./venv/bin/python3 agent/select_bank_songs.py --track N --count X
./venv/bin/python3 agent/select_bank_songs.py --track N --duration M
./venv/bin/python3 agent/select_bank_songs.py --track N --execute

# Add (no yarn alias - use Python directly)
./venv/bin/python3 agent/add_to_bank.py --track N --flow-id ID

# Status
yarn bank:status
```

### Building
```bash
yarn render:auto 16                      # Auto duration
yarn render:test 16                      # 5 minutes
yarn render:1h 16                        # 1 hour
yarn render:2h 16                        # 2 hours
yarn render:3h 16                        # 3 hours

yarn build:py 16 --duration 3            # Python builder
yarn build:sh 16 3                       # Shell builder
```

### Status
```bash
yarn status                              # Overall status
yarn status:tracks                       # Track folders
yarn status:bank                         # Bank status
```

### Cleanup
```bash
yarn clean:rendered                      # Clear rendered output
yarn clean:bank                          # Reset song bank
```

---

## 📚 Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [MANUAL_STEPS.md](MANUAL_STEPS.md) - What you do vs what's automated
- [GETTING_STARTED.md](GETTING_STARTED.md) - Complete setup guide
- [WORKFLOW_COMPLETE.md](../agent/song_sorting_update-11-16-25/WORKFLOW_COMPLETE.md) - Detailed workflow reference
- [BUILD_MIX_COMPARISON.md](BUILD_MIX_COMPARISON.md) - Shell vs Python build scripts

---

## 📝 Notes

- **Yarn vs NPM:** All commands work with both `yarn` and `npm run`
- **Python activation:** Yarn scripts automatically use `./venv/bin/python3`
- **Error codes:** Scripts exit with code 0 on success, non-zero on failure
- **Logs:** FFmpeg output goes to console, commands save to files in `rendered/`

---

**Need help?** Run `yarn help` or see [MANUAL_STEPS.md](MANUAL_STEPS.md)

**© 2025 Static Dreamscapes Lo-Fi**
