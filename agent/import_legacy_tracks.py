#!/usr/bin/env python3
"""
Import Legacy Tracks
--------------------
Bulk import existing tracks from a single folder into the song bank.

Step 1: Auto-create track folders based on track flow markdown files
Step 2: Process all songs from import folder and organize into track folders

Usage:
    # Step 1: Scan track flow docs and create track folders
    python3 agent/import_legacy_tracks.py --prepare

    # Step 2: Process songs from import folder
    python3 agent/import_legacy_tracks.py --import --flow-id 04

    # Dry run (see what would happen)
    python3 agent/import_legacy_tracks.py --import --flow-id 04 --dry-run

Structure:
    import_tracks/
    ├── track_flows/
    │   ├── track_001_flow.md
    │   ├── track_002_flow.md
    │   └── track_003_flow.md
    └── songs/
        ├── A_001_song.mp3
        ├── A_002_song.mp3
        ├── B_001_song.mp3
        └── ...
"""

import argparse
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"
IMPORT_DIR = PROJECT_ROOT / "import_tracks"
IMPORT_FLOWS_DIR = IMPORT_DIR / "track_flows"
IMPORT_SONGS_DIR = IMPORT_DIR / "songs"
SONG_BANK_DIR = PROJECT_ROOT / "song_bank"

def ensure_import_structure():
    """Ensure import_tracks/ structure exists."""
    IMPORT_DIR.mkdir(exist_ok=True)
    IMPORT_FLOWS_DIR.mkdir(exist_ok=True)
    IMPORT_SONGS_DIR.mkdir(exist_ok=True)

    # Create README
    readme_path = IMPORT_DIR / "README.md"
    if not readme_path.exists():
        readme_content = """# Import Tracks

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
"""
        with open(readme_path, 'w') as f:
            f.write(readme_content)

def extract_track_number_from_flow(flow_file):
    """
    Extract track number from track flow markdown file.

    Looks for:
    - Filename pattern: track_001_flow.md → 1
    - **Track Number**: X in content
    """
    # Try filename first
    filename = flow_file.name
    match = re.match(r'track_(\d+)_flow\.md', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Try content
    try:
        with open(flow_file, 'r') as f:
            content = f.read()
            match = re.search(r'\*\*Track Number\*\*:\s*(\d+)', content)
            if match:
                return int(match.group(1))
    except Exception:
        pass

    return None

def prepare_track_folders():
    """
    Step 1: Scan track flow files and create track folders.
    """
    ensure_import_structure()

    if not IMPORT_FLOWS_DIR.exists() or not any(IMPORT_FLOWS_DIR.glob("*.md")):
        print(f"❌ No track flow files found in {IMPORT_FLOWS_DIR}")
        print(f"\n📋 Next steps:")
        print(f"   1. Place track flow markdown files in {IMPORT_FLOWS_DIR}")
        print(f"   2. Name them: track_001_flow.md, track_002_flow.md, etc.")
        print(f"   3. Run this command again")
        return

    print(f"\n🔍 Scanning track flow files in {IMPORT_FLOWS_DIR}...")

    flow_files = sorted(IMPORT_FLOWS_DIR.glob("*.md"))
    created_tracks = []

    for flow_file in flow_files:
        track_num = extract_track_number_from_flow(flow_file)

        if track_num is None:
            print(f"   ⚠️  Could not extract track number from {flow_file.name}, skipping")
            continue

        track_folder = TRACKS_DIR / str(track_num)

        # Check if track exists
        if track_folder.exists():
            print(f"   ℹ️  Track {track_num} already exists, skipping")
            continue

        # Create track folder structure
        track_folder.mkdir(parents=True, exist_ok=True)
        (track_folder / "half_1").mkdir(exist_ok=True)
        (track_folder / "half_2").mkdir(exist_ok=True)
        (track_folder / "video").mkdir(exist_ok=True)
        (track_folder / "image").mkdir(exist_ok=True)

        # Copy track flow file
        dest_flow = track_folder / f"track_{track_num:03d}_flow.md"
        shutil.copy2(flow_file, dest_flow)

        # Create metadata.json
        metadata = {
            "track_number": track_num,
            "created": datetime.now().isoformat(),
            "status": "importing",
            "track_flow_id": None,
            "title": f"Track {track_num}",
            "theme": None,
            "duration_target_hours": 3,
            "notes": "Legacy track import",
            "bank_songs": {
                "count": 0,
                "total_duration": 0,
                "sources": []
            },
            "new_songs": {
                "count": 0,
                "total_duration": 0,
                "files": []
            }
        }

        metadata_file = track_folder / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"   ✅ Created track {track_num}: {track_folder}")
        created_tracks.append(track_num)

    if created_tracks:
        print(f"\n✅ Successfully created {len(created_tracks)} track folders!")
        print(f"\n📋 Created tracks: {', '.join(map(str, created_tracks))}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Place all MP3 files in {IMPORT_SONGS_DIR}")
        print(f"   2. Run import: ./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04")
    else:
        print(f"\n✅ All track folders already exist!")

def extract_track_number_from_filename(filename):
    """
    Extract track number from song filename.

    Patterns:
    - A_1_2_001a.mp3 → 1 (from naming convention)
    - B_3_5_015b.mp3 → 15
    - A_001_song.mp3 → 1 (from prefix)
    - song_name.mp3 → None (needs manual assignment)
    """
    # Pattern 1: Bank naming (A_phase_song_TRACKorder.mp3)
    match = re.match(r'[AB]_\d+_\d+_(\d+)[a-z]', filename)
    if match:
        return int(match.group(1))

    # Pattern 2: Simple prefix (A_001_song.mp3)
    match = re.match(r'[AB]_(\d+)', filename)
    if match:
        return int(match.group(1))

    # Pattern 3: Generic number (song_015.mp3)
    match = re.search(r'_(\d+)', filename)
    if match:
        return int(match.group(1))

    return None

def import_songs(flow_id, dry_run=False):
    """
    Step 2: Import songs from import_tracks/songs/ into track folders.
    """
    ensure_import_structure()

    if not IMPORT_SONGS_DIR.exists() or not any(IMPORT_SONGS_DIR.glob("*.mp3")):
        print(f"❌ No MP3 files found in {IMPORT_SONGS_DIR}")
        print(f"\n📋 Next steps:")
        print(f"   1. Place all MP3 files in {IMPORT_SONGS_DIR}")
        print(f"   2. Run this command again")
        return

    print(f"\n🔍 Scanning MP3 files in {IMPORT_SONGS_DIR}...")

    songs = sorted(IMPORT_SONGS_DIR.glob("*.mp3"))
    print(f"📋 Found {len(songs)} songs")

    # Group songs by track number
    tracks = {}
    unassigned = []

    for song_path in songs:
        track_num = extract_track_number_from_filename(song_path.name)

        if track_num is None:
            unassigned.append(song_path.name)
            continue

        if track_num not in tracks:
            tracks[track_num] = {"A": [], "B": []}

        # Determine half from filename
        if song_path.name.startswith("A_"):
            tracks[track_num]["A"].append(song_path)
        elif song_path.name.startswith("B_"):
            tracks[track_num]["B"].append(song_path)
        else:
            # Default to A if no prefix
            tracks[track_num]["A"].append(song_path)

    print(f"\n📊 Song distribution:")
    for track_num in sorted(tracks.keys()):
        a_count = len(tracks[track_num]["A"])
        b_count = len(tracks[track_num]["B"])
        print(f"   Track {track_num}: {a_count} songs (half_1), {b_count} songs (half_2)")

    if unassigned:
        print(f"\n⚠️  Unassigned songs ({len(unassigned)}):")
        for name in unassigned[:10]:
            print(f"   - {name}")
        if len(unassigned) > 10:
            print(f"   ... and {len(unassigned) - 10} more")

    if dry_run:
        print(f"\n🔍 DRY RUN - No changes made")
        return

    # Copy songs to track folders
    print(f"\n📦 Copying songs to track folders...")
    copied_count = 0

    for track_num, halves in tracks.items():
        track_folder = TRACKS_DIR / str(track_num)

        if not track_folder.exists():
            print(f"   ⚠️  Track {track_num} folder doesn't exist, skipping songs")
            continue

        # Copy half_1 songs
        for song_path in halves["A"]:
            dest = track_folder / "half_1" / song_path.name
            shutil.copy2(song_path, dest)
            copied_count += 1

        # Copy half_2 songs
        for song_path in halves["B"]:
            dest = track_folder / "half_2" / song_path.name
            shutil.copy2(song_path, dest)
            copied_count += 1

        a_count = len(halves["A"])
        b_count = len(halves["B"])
        print(f"   ✅ Track {track_num}: {a_count + b_count} songs copied")

    print(f"\n✅ Successfully copied {copied_count} songs!")
    print(f"\n🎯 Next steps:")
    print(f"   For each track, run:")
    for track_num in sorted(tracks.keys()):
        print(f"   ./venv/bin/python3 agent/add_to_bank.py --track {track_num} --flow-id {flow_id}")

def main():
    parser = argparse.ArgumentParser(
        description="Bulk import legacy tracks into song bank"
    )
    parser.add_argument(
        '--prepare',
        action='store_true',
        help='Step 1: Scan track flow files and create track folders'
    )
    parser.add_argument(
        '--import',
        dest='import_songs',
        action='store_true',
        help='Step 2: Import songs from import_tracks/songs/'
    )
    parser.add_argument(
        '--flow-id',
        type=str,
        help='Flow ID for imported tracks (e.g., "04")'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    if args.prepare:
        prepare_track_folders()
    elif args.import_songs:
        if not args.flow_id:
            print("❌ Error: --flow-id is required for import")
            print("   Example: --flow-id 04")
            return
        import_songs(args.flow_id, dry_run=args.dry_run)
    else:
        parser.print_help()
        print("\n📋 Quick start:")
        print("   1. ./venv/bin/python3 agent/import_legacy_tracks.py --prepare")
        print("   2. ./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04")

if __name__ == "__main__":
    main()
