# Import Tracks

Folder for bulk importing legacy tracks into the song bank.

## Structure

```
import_tracks/
├── track_flows/           # Track flow markdown files
│   ├── track_001_flow.md
│   ├── track_002_flow.md
│   └── ...
└── songs/                 # All MP3 files to import
    ├── A_001_song.mp3
    ├── B_002_song.mp3
    └── ...
```

## Workflow

### Step 1: Prepare

Place your track flow markdown files in `track_flows/` with naming:
- `track_001_flow.md`
- `track_002_flow.md`
- etc.

Each markdown file should contain track metadata at the top:
```markdown
# Track 1 - Production Flow

**Track Number**: 1
**Created**: 2025-11-20
...
```

Run preparation:
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --prepare
```

This will:
- Scan track flow files
- Create track folders (tracks/1/, tracks/2/, etc.)
- Copy track flow files to respective folders

### Step 2: Import Songs

Place ALL your MP3 files in `songs/` folder.

Run import:
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

This will:
- Detect track numbers from filenames (e.g., A_1_2_001a.mp3 → track 1)
- Organize songs into correct track folders (half_1/ or half_2/)
- Add songs to bank with proper metadata

### Dry Run

Test without making changes:
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04 --dry-run
```

## Filename Patterns

The script detects track numbers from various patterns:

**Bank naming format:**
- `A_1_2_001a.mp3` → Track 1
- `B_3_5_015b.mp3` → Track 15

**Prefixed format:**
- `A_001_song.mp3` → Extract track number from context or prompt
- `B_005_song.mp3` → Extract track number from context or prompt

**Generic format:**
- `song_001.mp3` → Extract track number from context or prompt
