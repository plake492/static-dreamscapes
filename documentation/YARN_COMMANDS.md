# 🧶 Yarn Commands Reference

Complete reference for all yarn/npm scripts available in the Static Dreamscapes project.

---

## 🚀 Quick Start

```bash
# First time setup
yarn setup

# Show all available commands
yarn run help

# Start watching for new files
yarn watch
```

---

## 📋 Complete Command List

### 🛠️ Setup & Installation

```bash
# Full setup (venv + dependencies + permissions)
yarn setup

# Install/update Python dependencies only
yarn setup:deps

# Fix script permissions
yarn setup:permissions
```

**What `yarn setup` does:**
1. Creates Python virtual environment (`venv/`)
2. Upgrades pip to latest version
3. Installs all dependencies from `requirements.txt`
4. Makes all scripts executable (`chmod +x`)

---

### 🎯 Main Pipeline (Orchestrator)

```bash
# Watch mode - continuously monitor for new MP3 files
yarn watch
# Alias: yarn orchestrator:watch

# Run pipeline once immediately
yarn run
# Alias: yarn orchestrator:run

# Analyze audio only (skip rename/prepend/build)
yarn analyze
# Alias: yarn orchestrator:analyze
```

**Watch Mode Details:**
- Monitors `/arc_library/` for new `.mp3` files
- 60-second cooldown after last file before triggering
- Automatically runs full pipeline when ready
- Press `Ctrl+C` to stop

**Run Once Details:**
- Executes complete pipeline immediately
- No file watching
- Returns exit code 0 on success
- Good for scheduled/cron jobs

---

### 🔧 Manual Pipeline Steps

#### Step 1: Rename Tracks by Date

```bash
# Rename all phases at once
yarn rename:all

# Rename individual phases
yarn rename:phase1    # Phase 1: Calm Intro
yarn rename:phase2    # Phase 2: Flow Focus
yarn rename:phase3    # Phase 3: Uplift Clarity
yarn rename:phase4    # Phase 4: Reflective Fade

# Preview changes without actually renaming (dry run)
yarn rename:all:dry
yarn rename:phase1:dry
yarn rename:phase2:dry
yarn rename:phase3:dry
yarn rename:phase4:dry
```

**What it does:**
- Sorts files by modification time (oldest first)
- Renames to `001_filename.mp3`, `002_filename.mp3`, etc.
- Skips files already numbered
- Preserves original modification dates

#### Step 2: Add Phase Prefixes

```bash
yarn prepend
```

**What it does:**
- Adds `A_` or `B_` prefixes based on arc logic
- Example: `001_track.mp3` → `A_001_track.mp3`
- Maintains proper playback order for rendering

#### Step 3: Analyze Audio

```bash
# Run audio analysis (manual, not via orchestrator)
yarn analyze:manual
```

**What it does:**
- Extracts BPM, key, brightness, RMS, zero-crossing rate
- Updates `/metadata/Phase_X.json` files
- Refreshes `/metadata/song_index.json`
- Uses librosa for feature extraction

#### Step 4: Verify Total Length

```bash
yarn verify:length
```

**What it does:**
- Calculates total duration of all MP3s
- Outputs to `total_length.txt`
- Checks against 3-hour target (10,800s ± 60s)

---

### 🎬 Build Final Mix

```bash
# Quick 5-minute test render
yarn build:test

# 1-hour mix
yarn build:1h

# 2-hour mix
yarn build:2h

# 3-hour full mix
yarn build:3h
```

**Note:** These commands use track number `1` by default. To use a different track number:

```bash
# Custom track number (requires manual command)
bash scripts/build_mix.sh 5 3    # Track 5, 3 hours
bash scripts/build_mix.sh 9 test # Track 9, 5 min test
```

**What it does:**
- Combines all MP3s with crossfades
- Loops song sequence to fill duration
- Applies volume boost (1.75x default)
- Outputs to `rendered/<track_num>/output_<timestamp>/output.mp4`
- Saves FFmpeg command and filter for debugging

---

### ✅ Validation & Verification

```bash
# Validate metadata consistency
yarn verify:metadata

# Validate and fix orphaned entries
yarn verify:metadata:fix

# Check total track duration
yarn verify:length
```

**`verify:metadata` checks for:**
- Orphaned entries (metadata exists but file missing)
- Missing entries (file exists but no metadata)
- Phase mismatches (file in Phase 1 but metadata says Phase 2)

**`verify:metadata:fix` will:**
- Remove orphaned metadata entries automatically
- Show summary of fixes applied

---

### 📊 Monitoring & Status

```bash
# Show system status (file counts, builds)
yarn status

# Follow logs in real-time
yarn logs

# Show last 50 log lines
yarn logs:last

# Search logs for errors
yarn logs:errors
```

**Status Output Example:**
```
=== MP3 Files ===
24
=== Metadata Entries ===
24
=== Build History ===
3 builds
```

---

### 🧹 Cleanup Commands

```bash
# Reset all metadata files (CAUTION: deletes data)
yarn clean:metadata

# Clear all log files
yarn clean:logs

# Delete all rendered mixes
yarn clean:rendered

# Clean everything (metadata + logs + rendered)
yarn clean:all
```

**⚠️ Warning:** These commands are destructive! Use with caution.

**What gets cleaned:**
- `clean:metadata` - Resets phase JSON files, song_index.json, build_history.json
- `clean:logs` - Removes all `*.log` files from `/logs/`
- `clean:rendered` - Deletes all content in `/rendered/`
- `clean:all` - All of the above

---

## 📖 Common Workflows

### Workflow 1: New Batch of Suno Tracks

```bash
# 1. Add MP3 files to arc_library/phase_X folders
# (manually organize by phase)

# 2. Start auto-processing
yarn watch

# 3. Wait for pipeline to complete (will auto-trigger after 60s cooldown)

# 4. Check results
yarn status
yarn logs:last
```

### Workflow 2: Manual Step-by-Step

```bash
# 1. Preview renaming first (dry run)
yarn rename:all:dry

# 2. Actually rename
yarn rename:all

# 3. Add prefixes
yarn prepend

# 4. Analyze audio
yarn analyze:manual

# 5. Verify length
yarn verify:length
cat total_length.txt

# 6. Build 5-min test
yarn build:test

# 7. If test looks good, build full mix
yarn build:3h
```

### Workflow 3: Quick Validation

```bash
# Check if metadata is in sync with files
yarn verify:metadata

# Check file counts
yarn status

# Review recent activity
yarn logs:last
```

### Workflow 4: Fresh Start

```bash
# Reset everything (CAUTION)
yarn clean:all

# Re-analyze all tracks
yarn analyze:manual

# Verify metadata
yarn verify:metadata
```

---

## 🎓 Examples

### Example 1: Process Phase 1 Only

```bash
# Rename Phase 1 tracks by date
yarn rename:phase1

# View what would happen (dry run)
yarn rename:phase1:dry

# Add prefixes
yarn prepend

# Analyze
yarn analyze:manual
```

### Example 2: Create Test Mix Quickly

```bash
# 1. Ensure you have some MP3s in arc_library
# 2. Run quick pipeline
yarn run

# 3. Build 5-minute test
yarn build:test

# 4. Check output
ls -lh rendered/1/output_*/
```

### Example 3: Monitor Live Processing

```bash
# Terminal 1: Start watching
yarn watch

# Terminal 2: Follow logs
yarn logs

# Add files to arc_library in file explorer
# Watch both terminals for real-time updates
```

### Example 4: Fix Metadata Issues

```bash
# Find issues
yarn verify:metadata

# Output might show:
#   ❌ old_track.mp3 (in phase_1_calm_intro)
#   ⚠️  new_track.mp3 (file exists but not in metadata)

# Fix orphans automatically
yarn verify:metadata:fix

# Re-analyze to add missing entries
yarn analyze:manual

# Verify again
yarn verify:metadata
# Should now show: ✅ Validation passed
```

---

## 🔍 Troubleshooting

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

### Permission Errors

```bash
# Fix all script permissions
yarn setup:permissions

# Or manually
chmod +x scripts/*.sh
chmod +x agent/*.py
```

### Logs Not Showing

```bash
# Create logs directory if missing
mkdir -p logs

# Run pipeline to generate logs
yarn run

# Then check
yarn logs:last
```

---

## 📚 Related Documentation

- [GETTING_STARTED.md](GETTING_STARTED.md) - Initial setup guide
- [CLAUDE.md](../CLAUDE.md) - Architecture and technical details
- [README.md](../README.md) - Project overview
- [agent/README_AGENT.md](../agent/README_AGENT.md) - Python agent documentation
- [metadata/README_METADATA.md](../metadata/README_METADATA.md) - Metadata system guide

---

## 💡 Tips

1. **Always use dry run first**: `yarn rename:all:dry` before `yarn rename:all`
2. **Monitor logs**: Keep `yarn logs` running in a separate terminal during processing
3. **Validate often**: Run `yarn verify:metadata` after making changes
4. **Use test builds**: Test with `yarn build:test` before full 3-hour renders
5. **Check status**: Use `yarn status` to get quick overview of system state

---

**© 2025 Static Dreamscapes Lo-Fi**
