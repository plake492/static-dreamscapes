# 🚀 Getting Started with Static Dreamscapes

A quick-start guide for setting up and running the Static Dreamscapes automation system.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed
- **FFmpeg** with crossfade support (`brew install ffmpeg` on macOS)
- **Bash** shell (macOS/Linux native, or WSL on Windows)
- **Git** for version control

---

## Initial Setup

### 1. Clone and Navigate

```bash
cd /path/to/static-dreamwaves
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all Python packages
pip install -r requirements.txt
```

**Packages installed:**
- `librosa` - Audio analysis
- `numpy` - Numerical operations
- `ffmpeg-python` - FFmpeg integration
- `watchdog` - File system monitoring

### 4. Make Scripts Executable

```bash
chmod +x scripts/*.sh
chmod +x agent/*.py
```

### 5. Verify Installation

```bash
# Check orchestrator loads correctly
./venv/bin/python3 agent/orchestrator.py --help

# Should show:
# usage: orchestrator.py [-h] [--watch] [--run-once] [--analyze-only] [--track-num TRACK_NUM]
```

---

## Directory Structure Overview

After setup, your project should look like this:

```
static-dreamwaves/
├── Arc_Library/                   # Audio library organized by phase
│   ├── Phase_1_Calm_Intro/
│   │   ├── Ambient_Warmth/
│   │   ├── Early_Dawn/
│   │   └── Nostalgic_Haze/
│   ├── Phase_2_Flow_Focus/
│   ├── Phase_3_Uplift_Clarity/
│   └── Phase_4_Reflective_Fade/
│
├── metadata/                      # Structured JSON metadata
│   ├── Phase_1_Calm_Intro.json
│   ├── Phase_2_Flow_Focus.json
│   ├── Phase_3_Uplift_Clarity.json
│   ├── Phase_4_Reflective_Fade.json
│   ├── song_index.json            # Global track index
│   ├── build_history.json         # Build records
│   └── mixes/                     # Per-mix metadata
│
├── scripts/                       # Shell utilities
│   ├── rename_by_mod_time.sh
│   ├── prepend_tracks.sh
│   ├── track_length_report.sh
│   └── build_mix.sh
│
├── agent/                         # Python automation
│   ├── orchestrator.py            # Main pipeline controller
│   ├── analyze_audio.py           # Audio feature extraction
│   ├── validate_metadata.py       # Validation tool
│   └── docs/                      # Technical documentation
│
├── Rendered/                      # Output directory for mixes
├── logs/                          # Orchestrator logs
├── venv/                          # Python virtual environment
└── requirements.txt               # Python dependencies
```

---

## Quick Start Guide

### Option 1: Automated Pipeline (Recommended)

**Use Case:** Hands-off automation for batch processing Suno downloads

1. **Add MP3 files** to `/Arc_Library/Phase_X_*/` folders
2. **Run watch mode:**
   ```bash
   source venv/bin/activate
   ./venv/bin/python3 agent/orchestrator.py --watch
   ```
3. **Wait for cooldown** (60 seconds after last file)
4. **Pipeline auto-executes** and renders final mix

**What happens:**
- Files renamed chronologically by modification time
- Phase prefixes added (A*/B*)
- Audio features extracted (BPM, key, brightness, etc.)
- Total duration verified (~3 hours)
- Final mix rendered with crossfades
- Metadata and build history updated

### Option 2: Manual One-Time Run

**Use Case:** Single execution for testing or scheduled builds

```bash
source venv/bin/activate
./venv/bin/python3 agent/orchestrator.py --run-once
```

**With track number** (for build_mix.sh):
```bash
./venv/bin/python3 agent/orchestrator.py --run-once --track-num 5
```

### Option 3: Analysis Only

**Use Case:** Update metadata without full pipeline

```bash
source venv/bin/activate
./venv/bin/python3 agent/orchestrator.py --analyze-only
```

---

## Workflow Example

### Scenario: Creating Track 9 "Neon Arcade Memories"

1. **Generate songs** using Suno (24 tracks total)

2. **Organize by phase:**
   ```bash
   # Move files to appropriate phase folders
   mv *calm*.mp3 Arc_Library/Phase_1_Calm_Intro/Ambient_Warmth/
   mv *focus*.mp3 Arc_Library/Phase_2_Flow_Focus/Midtempo_Groove/
   mv *bright*.mp3 Arc_Library/Phase_3_Uplift_Clarity/Bright_Pads/
   mv *fade*.mp3 Arc_Library/Phase_4_Reflective_Fade/Vapor_Trails/
   ```

3. **Run orchestrator:**
   ```bash
   source venv/bin/activate
   ./venv/bin/python3 agent/orchestrator.py --run-once --track-num 9
   ```

4. **Check output:**
   ```bash
   # View logs
   tail -50 logs/orchestrator.log

   # Check rendered mix
   ls -lh Rendered/9/output_*/output.mp4

   # Review metadata
   cat metadata/build_history.json | tail -20
   ```

---

## Manual Script Usage

### Rename Tracks by Date

```bash
# Preview changes (dry run)
bash scripts/rename_by_mod_time.sh Arc_Library/Phase_1_Calm_Intro --dry-run

# Actually rename
bash scripts/rename_by_mod_time.sh Arc_Library/Phase_1_Calm_Intro
```

### Add Phase Prefixes

```bash
bash scripts/prepend_tracks.sh
```

### Analyze Audio

```bash
python3 agent/analyze_audio.py --input ./Arc_Library --output ./metadata
```

### Verify Total Length

```bash
bash scripts/track_length_report.sh
cat total_length.txt
```

### Build Final Mix

```bash
# 1 hour test
bash scripts/build_mix.sh 5 1

# 3 hours production
bash scripts/build_mix.sh 5 3

# 5 minutes quick test
bash scripts/build_mix.sh 5 test
```

---

## Validation and Troubleshooting

### Validate Metadata

Check for orphaned entries, missing files, or phase mismatches:

```bash
source venv/bin/activate
./venv/bin/python3 agent/validate_metadata.py
```

**Fix orphaned entries:**
```bash
./venv/bin/python3 agent/validate_metadata.py --fix-orphans
```

### Common Issues

**Problem: ModuleNotFoundError for watchdog/librosa**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
which python3  # Should show: .../venv/bin/python3

# Reinstall if needed
pip install -r requirements.txt
```

**Problem: Permission denied on scripts**
```bash
chmod +x scripts/*.sh
chmod +x agent/*.py
```

**Problem: FFmpeg not found**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Check installation
which ffmpeg
ffmpeg -version
```

**Problem: Pipeline stops at specific script**
```bash
# Check logs
tail -100 logs/orchestrator.log

# Run script manually to see full error
bash scripts/rename_by_mod_time.sh Arc_Library/Phase_1_Calm_Intro
```

---

## Next Steps

### Learn the System

1. Read [README.md](README.md) for project overview
2. Review [CLAUDE.md](CLAUDE.md) for architecture details
3. Explore [agent/docs/](agent/docs/) for deep technical documentation
4. Check [scripts/README_SCRIPTS.md](scripts/README_SCRIPTS.md) for script reference

### Customize

- Modify phase descriptions in `metadata/Phase_X.json`
- Adjust duration tolerance in `agent/orchestrator.py` (line 35)
- Change FFmpeg settings in `scripts/build_mix.sh`
- Add custom mood tags to metadata schema

### Extend

- Create curation logic based on BPM/key compatibility
- Add theme-aware playlist generation
- Integrate YouTube upload automation
- Build performance analytics tracking

---

## Support

For issues, questions, or contributions:
- Review [agent/docs/04_AI_AGENT_WORKFLOW.md](agent/docs/04_AI_AGENT_WORKFLOW.md)
- Check [metadata/README_METADATA.md](metadata/README_METADATA.md)
- Consult [agent/README_AGENT.md](agent/README_AGENT.md)

---

**© 2025 Static Dreamscapes Lo-Fi**
Developed by Patrick Lake
