#!/usr/bin/env python3
"""
Static Dreamscapes - Track Template Creator
--------------------------------------------
Creates folder structure for new tracks with auto-incrementing track numbers.

Usage:
    python3 agent/create_track_template.py
    python3 agent/create_track_template.py --track-number 20
    python3 agent/create_track_template.py --flow-id 04
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"
TRACK_FLOWS_DIR = PROJECT_ROOT / "track_flows"


def get_next_track_number() -> int:
    """
    Auto-detect the next track number by finding the highest existing track.

    Returns:
        int: Next available track number (e.g., 16 if 15 exists)
    """
    if not TRACKS_DIR.exists():
        return 1

    existing_tracks = []
    for item in TRACKS_DIR.iterdir():
        if item.is_dir() and item.name.isdigit():
            existing_tracks.append(int(item.name))

    if not existing_tracks:
        return 1

    return max(existing_tracks) + 1


def load_track_flow(flow_id: str) -> dict:
    """
    Load track flow document to pre-fill template.

    Args:
        flow_id: Track flow ID (e.g., "04")

    Returns:
        dict: Track flow metadata if found, empty dict otherwise
    """
    if not flow_id:
        return {}

    flow_files = list(TRACK_FLOWS_DIR.glob(f"{flow_id}_*.md"))
    if not flow_files:
        print(f"⚠️  Warning: Track flow '{flow_id}' not found in {TRACK_FLOWS_DIR}")
        return {}

    flow_file = flow_files[0]
    print(f"✓ Found track flow: {flow_file.name}")

    # Parse YAML frontmatter if present
    content = flow_file.read_text()
    if content.startswith("---"):
        # Basic YAML parsing (could use PyYAML for more robust parsing)
        lines = content.split("\n")
        metadata = {}
        in_frontmatter = False
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip('"')
        return metadata

    return {}


def create_track_flow_md(track_number: int, flow_id: str = None) -> str:
    """
    Generate track_flow.md content.

    Args:
        track_number: Track number
        flow_id: Optional track flow ID to reference

    Returns:
        str: Markdown content for track_flow.md
    """
    timestamp = datetime.now().isoformat()

    content = f"""---
track_number: {track_number}
track_flow_id: {flow_id if flow_id else 'null'}
title: "Track {track_number}"
created: {timestamp}
status: in_progress
---

# Track {track_number} Flow

## Instructions

1. Update `track_flow_id` to reference a track flow (e.g., "04" for track_flows/04_current_flow.md)
2. OR define custom flow below
3. Add songs to half_1/ and half_2/ folders as you create them

## Phase 1 - Calm Intro

Songs for half_1:
- Song #1: [Prompt from track flow or custom]
- Song #2: [Prompt from track flow or custom]

## Phase 2 - Flow Focus

Songs for half_1 or half_2:
- Song #3: [Prompt from track flow or custom]
- Song #4: [Prompt from track flow or custom]

## Phase 3 - Uplift Clarity

Songs for half_2:
- Song #7: [Prompt from track flow or custom]
- Song #8: [Prompt from track flow or custom]

## Phase 4 - Reflective Fade

Songs for half_2:
- Song #12: [Prompt from track flow or custom]
- Song #13: [Prompt from track flow or custom]

## Notes

Add any notes about this track here (theme, special considerations, etc.)
"""

    return content


def create_metadata_json(track_number: int, flow_id: str = None) -> dict:
    """
    Generate metadata.json structure.

    Args:
        track_number: Track number
        flow_id: Optional track flow ID

    Returns:
        dict: Metadata structure
    """
    return {
        "track_number": track_number,
        "track_flow_id": flow_id,
        "title": f"Track {track_number}",
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "half_1": {
            "songs": [],
            "total_duration": 0,
            "song_count": 0
        },
        "half_2": {
            "songs": [],
            "total_duration": 0,
            "song_count": 0
        },
        "render_history": [],
        "notes": ""
    }


def create_readme(track_number: int) -> str:
    """
    Generate README.md with instructions.

    Args:
        track_number: Track number

    Returns:
        str: README content
    """
    return f"""# Track {track_number}

## Folder Structure

- **image/** - Add cover image as `{track_number}.jpg`
- **video/** - Add background video as `{track_number}.mp4`
- **half_1/** - Add songs for first half of mix (no A_ prefix needed)
- **half_2/** - Add songs for second half of mix (no B_ prefix needed)
- **track_flow.md** - Reference to track flow and prompts used
- **metadata.json** - Track metadata (auto-updated by scripts)

## Workflow

### 1. Add Background Assets
```bash
# Add video
cp /path/to/video.mp4 tracks/{track_number}/video/{track_number}.mp4

# Add cover image
cp /path/to/image.jpg tracks/{track_number}/image/{track_number}.jpg
```

### 2. Select Songs from Bank (Optional)
```bash
# By count (get 8 songs)
./venv/bin/python3 agent/select_bank_songs.py \\
  --track-number {track_number} \\
  --flow-id 04 \\
  --count 8 \\
  --output tracks/{track_number}/bank_selection.json

# By duration (get 30 minutes)
./venv/bin/python3 agent/select_bank_songs.py \\
  --track-number {track_number} \\
  --flow-id 04 \\
  --duration 30 \\
  --output tracks/{track_number}/bank_selection.json
```

### 3. Add Songs Manually
```bash
# Copy bank songs (from bank_selection.json)
cp song_bank/by_phase/phase_1/A_1_1_007a.mp3 tracks/{track_number}/half_1/

# Add new songs from Suno
mv ~/Downloads/new_song.mp3 tracks/{track_number}/half_1/
mv ~/Downloads/another_song.mp3 tracks/{track_number}/half_2/
```

### 4. Build Track
```bash
# Build 3-hour mix (applies A_/B_ prefixes automatically)
./venv/bin/python3 agent/build_track.py \\
  --track-number {track_number} \\
  --duration 3 \\
  --output rendered/{track_number}/

# Build 5-minute test
./venv/bin/python3 agent/build_track.py \\
  --track-number {track_number} \\
  --duration test \\
  --output rendered/{track_number}/
```

### 5. Add to Bank (After successful render)
```bash
# Add all songs to bank for future reuse
./venv/bin/python3 agent/add_to_bank.py \\
  --track-number {track_number} \\
  --flow-id 04
```

## Status

- [ ] Video added
- [ ] Cover image added
- [ ] Songs added to half_1/
- [ ] Songs added to half_2/
- [ ] Track built
- [ ] Songs added to bank
"""


def create_track_template(track_number: int = None, flow_id: str = None) -> bool:
    """
    Create complete track template with all folders and files.

    Args:
        track_number: Track number (auto-detected if None)
        flow_id: Optional track flow ID to reference

    Returns:
        bool: True if successful, False otherwise
    """
    # Auto-detect track number if not provided
    if track_number is None:
        track_number = get_next_track_number()
        print(f"🔢 Auto-detected next track number: {track_number}")
    else:
        print(f"🔢 Using specified track number: {track_number}")

    # Check if track already exists
    track_dir = TRACKS_DIR / str(track_number).zfill(3)
    if track_dir.exists():
        print(f"❌ Error: Track {track_number} already exists at {track_dir}")
        return False

    # Load track flow if specified
    flow_metadata = {}
    if flow_id:
        flow_metadata = load_track_flow(flow_id)

    # Create directory structure
    print(f"\n📁 Creating track template: {track_dir.name}/")

    try:
        # Create main directories
        track_dir.mkdir(parents=True, exist_ok=True)
        (track_dir / "image").mkdir(exist_ok=True)
        (track_dir / "video").mkdir(exist_ok=True)
        (track_dir / "half_1").mkdir(exist_ok=True)
        (track_dir / "half_2").mkdir(exist_ok=True)

        print("  ✓ Created image/")
        print("  ✓ Created video/")
        print("  ✓ Created half_1/")
        print("  ✓ Created half_2/")

        # Create track_flow.md
        track_flow_content = create_track_flow_md(track_number, flow_id)
        (track_dir / "track_flow.md").write_text(track_flow_content)
        print("  ✓ Created track_flow.md")

        # Create metadata.json
        metadata = create_metadata_json(track_number, flow_id)
        (track_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        print("  ✓ Created metadata.json")

        # Create README.md
        readme_content = create_readme(track_number)
        (track_dir / "README.md").write_text(readme_content)
        print("  ✓ Created README.md")

        # Success message
        print(f"\n✅ Successfully created track template: tracks/{track_dir.name}/")
        print("\n📋 Next steps:")
        print(f"  1. Add background video: tracks/{track_dir.name}/video/{track_number}.mp4")
        print(f"  2. Add cover image: tracks/{track_dir.name}/image/{track_number}.jpg")
        print(f"  3. Select songs from bank OR add new songs to half_1/ and half_2/")
        print(f"\n💡 See tracks/{track_dir.name}/README.md for detailed instructions")

        return True

    except Exception as e:
        print(f"❌ Error creating track template: {e}")
        # Clean up partial creation
        if track_dir.exists():
            import shutil
            shutil.rmtree(track_dir)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Create track template with folder structure for new tracks"
    )
    parser.add_argument(
        "--track-number",
        type=int,
        help="Track number to create (auto-detects next if not specified)"
    )
    parser.add_argument(
        "--flow-id",
        type=str,
        help="Track flow ID to reference (e.g., '04' for track_flows/04_*.md)"
    )

    args = parser.parse_args()

    # Ensure tracks directory exists
    TRACKS_DIR.mkdir(exist_ok=True)

    # Create template
    success = create_track_template(
        track_number=args.track_number,
        flow_id=args.flow_id
    )

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
