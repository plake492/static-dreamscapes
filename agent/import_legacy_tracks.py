#!/usr/bin/env python3
"""
Import Legacy Tracks
--------------------
Bulk import existing tracks from a single folder into the song bank.

Step 1: Auto-create track folders based on track flow markdown files
Step 2: Process all songs from import folder and organize into track folders

Usage:
    # Step 1: Scan songs and auto-create track flow templates
    python3 agent/import_legacy_tracks.py --prepare

    # Step 2: Import songs (flow ID auto-detected from filenames)
    python3 agent/import_legacy_tracks.py --import

    # Override flow ID if needed
    python3 agent/import_legacy_tracks.py --import --flow-id 04

    # Dry run (see what would happen)
    python3 agent/import_legacy_tracks.py --import --dry-run

Flow Detection:
    - Automatically detects flow ID from filename position 1
    - Example: A_1_2_015a.mp3 → flow "01"
    - Example: B_3_5_007b.mp3 → flow "03"
    - Uses most common flow ID per track if mixed

Structure:
    import_tracks/
    ├── track_flows/
    │   ├── track_001_flow.md
    │   ├── track_002_flow.md
    │   └── track_003_flow.md
    └── songs/
        ├── A_1_2_001a.mp3
        ├── A_1_3_001b.mp3
        ├── B_1_1_001a.mp3
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
    ├── A_1_2_001a.mp3
    ├── A_1_3_001b.mp3
    ├── B_1_1_001a.mp3
    └── ...
```

## Workflow

### Step 1: Prepare

**Option A: Auto-Detection (Recommended)**

Place all MP3 files in `songs/` first, then run:

```bash
cp ~/OldTracks/*.mp3 songs/
./venv/bin/python3 agent/import_legacy_tracks.py --prepare
```

This will:
- Scan all MP3 files and auto-detect track numbers
- Generate track flow template files in `track_flows/`

**Option B: Manual Specification**

If songs aren't ready yet:

```bash
./venv/bin/python3 agent/import_legacy_tracks.py --prepare --tracks 1 2 15
```

Then edit the generated files and paste your track flow content:
```bash
nano track_flows/track_001_flow.md    # Paste your content here
```

### Step 2: Import Songs

Place ALL your MP3 files in `songs/` folder.

Run import (flow ID auto-detected):
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import
```

This will:
- Auto-detect flow ID from filenames (e.g., A_**1**_2_001a.mp3 → flow "01")
- Detect track numbers from filenames (e.g., A_1_2_**001**a.mp3 → track 1)
- Auto-detect half from A_/B_ prefix
- Organize songs into correct track folders (half_1/ or half_2/)
- Create track folders with metadata

Override flow ID if needed:
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04
```

### Dry Run

Test without making changes:
```bash
./venv/bin/python3 agent/import_legacy_tracks.py --import --dry-run
```

## Filename Format

**Bank naming format:** `A_[FLOW]_[SONG]_[TRACK][ORDER].mp3`

- **Position 0**: Half (A or B)
- **Position 1**: Flow number (e.g., 1, 3, 4) → auto-detected
- **Position 2**: Song number within phase
- **Position 3**: Track number + order letter (e.g., 001a, 015b) → auto-detected

**Examples:**
- `A_1_2_001a.mp3` → Half A, Flow 01, Track 1
- `B_3_5_015b.mp3` → Half B, Flow 03, Track 15
- `A_4_1_007a.mp3` → Half A, Flow 04, Track 7

**Auto-Detection:**
- Flow ID uses **most common** value per track (handles mixed flows gracefully)
- Track number extracted from third NUMBER in format
- Half detected from A_/B_ prefix
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

def create_track_flow_template(track_num):
    """
    Create a track flow markdown template.
    """
    content = f"""# Track {track_num} - Production Flow

**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Track Number**: {track_num}

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

"""
    return content

def detect_tracks_from_songs():
    """
    Scan import_tracks/songs/ and detect unique track numbers from filenames.

    Returns:
        Set of track numbers found
    """
    if not IMPORT_SONGS_DIR.exists() or not any(IMPORT_SONGS_DIR.glob("*.mp3")):
        return set()

    track_numbers = set()
    for song_path in IMPORT_SONGS_DIR.glob("*.mp3"):
        track_num = extract_track_number_from_filename(song_path.name)
        if track_num is not None:
            track_numbers.add(track_num)

    return track_numbers

def prepare_track_folders(track_numbers=None):
    """
    Step 1: Create track flow markdown templates ONLY in import_tracks/track_flows/.
    Does NOT create track folders in /tracks.

    Args:
        track_numbers: List of track numbers to prepare (e.g., [1, 2, 15])
                      If None, auto-detects from songs in import_tracks/songs/
    """
    ensure_import_structure()

    # Auto-detect from songs if no track numbers provided
    if track_numbers is None or len(track_numbers) == 0:
        print(f"\n🔍 No track numbers specified, auto-detecting from songs...")

        detected_tracks = detect_tracks_from_songs()

        if not detected_tracks:
            print(f"❌ No songs found in {IMPORT_SONGS_DIR} to detect track numbers")
            print(f"\n📋 Options:")
            print(f"   1. Place MP3 files in {IMPORT_SONGS_DIR} and run again")
            print(f"   2. Manually specify track numbers:")
            print(f"      ./venv/bin/python3 agent/import_legacy_tracks.py --prepare --tracks 1 2 15")
            return

        track_numbers = sorted(detected_tracks)
        print(f"   ✅ Detected {len(track_numbers)} track(s) from songs: {', '.join(map(str, track_numbers))}")
        print(f"")

    print(f"\n📝 Creating track flow templates for {len(track_numbers)} track(s)...")

    created_flows = []
    skipped_flows = []

    for track_num in track_numbers:
        # Create track flow template in import_tracks/track_flows/
        import_flow = IMPORT_FLOWS_DIR / f"track_{track_num:03d}_flow.md"

        # Check if flow file already exists
        if import_flow.exists():
            print(f"   ℹ️  Track flow {track_num} already exists, skipping")
            skipped_flows.append(track_num)
            continue

        # Create track flow template
        flow_content = create_track_flow_template(track_num)
        with open(import_flow, 'w') as f:
            f.write(flow_content)

        print(f"   ✅ Created track flow template: track_{track_num:03d}_flow.md")
        created_flows.append(track_num)

    if created_flows:
        print(f"\n✅ Successfully created {len(created_flows)} track flow template(s)!")
        print(f"\n📋 Created templates for tracks: {', '.join(map(str, created_flows))}")
        print(f"\n📝 Files created in: {IMPORT_FLOWS_DIR}")
        for track_num in created_flows:
            print(f"   - track_{track_num:03d}_flow.md")
        print(f"\n🎯 Next steps:")
        print(f"   1. Edit track flow files and paste your content:")
        for track_num in created_flows:
            print(f"      nano {IMPORT_FLOWS_DIR}/track_{track_num:03d}_flow.md")
        print(f"   2. Run import to create track folders and organize songs:")
        print(f"      ./venv/bin/python3 agent/import_legacy_tracks.py --import --flow-id 04")

    if skipped_flows:
        print(f"\n⚠️  Skipped {len(skipped_flows)} existing flow file(s): {', '.join(map(str, skipped_flows))}")

    if not created_flows and not skipped_flows:
        print(f"\n✅ All track flow templates already exist!")

def extract_track_number_from_filename(filename):
    """
    Extract track number from song filename.

    The track number is the THIRD NUMBER in the filename format:
    - A_1_2_015a.mp3 → 15 (third number: "015")
    - B_3_5_007b.mp3 → 7 (third number: "007")

    Format: A_[phase]_[song]_[TRACK][order]
    """
    # Remove extension
    name_without_ext = filename.rsplit('.', 1)[0]

    # Split by underscore
    parts = name_without_ext.split('_')

    # Pattern 1: Bank naming format A_x_x_TRACKa (fourth position, third number)
    # Example: A_1_2_015a → parts[3] = "015a" → extract "015"
    if len(parts) >= 4:
        fourth_part = parts[3]
        # Extract leading digits from fourth part (handles "015a", "007b", etc.)
        match = re.match(r'(\d+)', fourth_part)
        if match:
            return int(match.group(1))

    # Pattern 2: Three-part format (fallback)
    # Example: A_phase_015 → parts[2] = "015"
    if len(parts) >= 3:
        third_part = parts[2]
        match = re.match(r'(\d+)', third_part)
        if match:
            return int(match.group(1))

    # Pattern 3: Simple prefix (A_015)
    # Example: A_015 → parts[1] = "015"
    if len(parts) >= 2 and parts[0] in ['A', 'B']:
        match = re.match(r'(\d+)', parts[1])
        if match:
            return int(match.group(1))

    # Pattern 4: Any numeric part (fallback)
    for part in parts:
        match = re.match(r'(\d+)', part)
        if match:
            return int(match.group(1))

    return None

def extract_flow_id_from_filename(filename):
    """
    Extract flow ID from song filename.

    Format: A_[FLOW]_[song]_[TRACK][order]
    - A_1_2_015a.mp3 → "01" (first number, zero-padded)
    - B_3_5_007b.mp3 → "03"

    Returns:
        Flow ID as zero-padded string (e.g., "01", "03") or None
    """
    # Remove extension
    name_without_ext = filename.rsplit('.', 1)[0]

    # Split by underscore
    parts = name_without_ext.split('_')

    # Pattern: A_FLOW_x_x format (flow is in position 1)
    if len(parts) >= 2 and parts[0] in ['A', 'B']:
        match = re.match(r'(\d+)', parts[1])
        if match:
            flow_num = int(match.group(1))
            return f"{flow_num:02d}"  # Zero-pad to 2 digits

    return None

def import_songs(flow_id=None, dry_run=False):
    """
    Step 2: Import songs from import_tracks/songs/ into track folders.

    Args:
        flow_id: Optional flow ID. If not provided, will auto-detect from filenames.
        dry_run: If True, show what would be done without making changes.
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

    # Group songs by track number and detect flow IDs
    tracks = {}
    track_flow_ids = {}  # Track number -> detected flow ID
    unassigned = []

    for song_path in songs:
        track_num = extract_track_number_from_filename(song_path.name)

        if track_num is None:
            unassigned.append(song_path.name)
            continue

        if track_num not in tracks:
            tracks[track_num] = {"A": [], "B": []}
            track_flow_ids[track_num] = []

        # Determine half from filename
        if song_path.name.startswith("A_"):
            tracks[track_num]["A"].append(song_path)
        elif song_path.name.startswith("B_"):
            tracks[track_num]["B"].append(song_path)
        else:
            # Default to A if no prefix
            tracks[track_num]["A"].append(song_path)

        # Extract flow ID from filename
        detected_flow = extract_flow_id_from_filename(song_path.name)
        if detected_flow:
            track_flow_ids[track_num].append(detected_flow)

    # Determine most common flow ID per track
    track_resolved_flows = {}
    for track_num, flow_ids in track_flow_ids.items():
        if flow_ids:
            # Find most common flow ID
            from collections import Counter
            flow_counter = Counter(flow_ids)
            most_common_flow = flow_counter.most_common(1)[0][0]
            track_resolved_flows[track_num] = most_common_flow
        else:
            track_resolved_flows[track_num] = flow_id if flow_id else None

    print(f"\n📊 Song distribution:")
    for track_num in sorted(tracks.keys()):
        a_count = len(tracks[track_num]["A"])
        b_count = len(tracks[track_num]["B"])
        detected_flow = track_resolved_flows.get(track_num)
        flow_info = f" (flow: {detected_flow})" if detected_flow else ""
        print(f"   Track {track_num}: {a_count} songs (half_1), {b_count} songs (half_2){flow_info}")

    if unassigned:
        print(f"\n⚠️  Unassigned songs ({len(unassigned)}):")
        for name in unassigned[:10]:
            print(f"   - {name}")
        if len(unassigned) > 10:
            print(f"   ... and {len(unassigned) - 10} more")

    if dry_run:
        print(f"\n🔍 DRY RUN - No changes made")
        return

    # Create track folders and organize songs
    print(f"\n📦 Creating track folders and organizing songs...")
    copied_count = 0

    for track_num, halves in tracks.items():
        track_folder = TRACKS_DIR / str(track_num)
        track_flow_id = track_resolved_flows.get(track_num)

        # Create track folder if it doesn't exist
        if not track_folder.exists():
            track_folder.mkdir(parents=True, exist_ok=True)
            (track_folder / "half_1").mkdir(exist_ok=True)
            (track_folder / "half_2").mkdir(exist_ok=True)
            (track_folder / "video").mkdir(exist_ok=True)
            (track_folder / "image").mkdir(exist_ok=True)

            # Copy track flow file if it exists
            import_flow = IMPORT_FLOWS_DIR / f"track_{track_num:03d}_flow.md"
            if import_flow.exists():
                dest_flow = track_folder / f"track_{track_num:03d}_flow.md"
                shutil.copy2(import_flow, dest_flow)

            # Create metadata.json with detected flow ID
            metadata = {
                "track_number": track_num,
                "created": datetime.now().isoformat(),
                "status": "importing",
                "track_flow_id": track_flow_id,
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
        track_flow = track_resolved_flows.get(track_num)
        if track_flow:
            print(f"   ./venv/bin/python3 agent/add_to_bank.py --track {track_num} --flow-id {track_flow}")
        else:
            print(f"   ./venv/bin/python3 agent/add_to_bank.py --track {track_num} --flow-id <FLOW_ID>")

def main():
    parser = argparse.ArgumentParser(
        description="Bulk import legacy tracks into song bank"
    )
    parser.add_argument(
        '--prepare',
        action='store_true',
        help='Step 1: Create track folders and flow templates'
    )
    parser.add_argument(
        '--tracks',
        nargs='+',
        type=int,
        help='Track numbers to prepare (e.g., 1 2 15)'
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
        help='Flow ID for imported tracks (e.g., "04"). If not provided, will auto-detect from filenames.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    args = parser.parse_args()

    if args.prepare:
        prepare_track_folders(track_numbers=args.tracks)
    elif args.import_songs:
        import_songs(flow_id=args.flow_id, dry_run=args.dry_run)
    else:
        parser.print_help()
        print("\n📋 Quick start:")
        print("   1. ./venv/bin/python3 agent/import_legacy_tracks.py --prepare")
        print("   2. Edit track flow files and paste your content")
        print("   3. ./venv/bin/python3 agent/import_legacy_tracks.py --import")
        print("\n💡 Flow ID is auto-detected from filenames (e.g., A_1_2_015a.mp3 → flow 01)")

if __name__ == "__main__":
    main()
