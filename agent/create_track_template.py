#!/usr/bin/env python3
"""
Create Track Template
---------------------
Auto-generates folder structure for new track.
If last track is 15, creates 16, etc.

Usage:
    python3 agent/create_track_template.py
    python3 agent/create_track_template.py --track-number 20
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"

def get_next_track_number():
    """Find the next available track number by scanning tracks/ directory."""
    if not TRACKS_DIR.exists():
        TRACKS_DIR.mkdir(parents=True)
        return 1

    # Find all numeric track folders
    track_numbers = []
    for folder in TRACKS_DIR.iterdir():
        if folder.is_dir() and folder.name.isdigit():
            track_numbers.append(int(folder.name))

    if not track_numbers:
        return 1

    return max(track_numbers) + 1

def create_track_template(track_number=None):
    """
    Create folder structure for a new track.

    Args:
        track_number: Optional specific track number. If None, auto-increments.

    Returns:
        Path to created track folder
    """
    if track_number is None:
        track_number = get_next_track_number()

    track_folder = TRACKS_DIR / str(track_number)

    # Check if track already exists
    if track_folder.exists():
        print(f"❌ Error: Track {track_number} already exists at {track_folder}")
        print(f"   Use --track-number to specify a different number, or delete the existing folder.")
        return None

    # Create folder structure
    print(f"\n🎵 Creating track template for Track {track_number}...")
    print(f"📁 Location: {track_folder}")

    folders = {
        "half_1": "Songs for first half (A_ prefix during render)",
        "half_2": "Songs for second half (B_ prefix during render)",
        "video": "Background video for render (e.g., {}.mp4)".format(track_number),
        "image": "Cover art/thumbnail (e.g., {}.jpg)".format(track_number)
    }

    for folder_name, description in folders.items():
        folder_path = track_folder / folder_name
        folder_path.mkdir(parents=True)
        print(f"   ✓ Created {folder_name}/ - {description}")

    # Create metadata template
    metadata = {
        "track_number": track_number,
        "created": datetime.now().isoformat(),
        "status": "in_progress",
        "track_flow_id": None,
        "title": f"Track {track_number}",
        "theme": None,
        "duration_target_hours": 3,
        "notes": "Add notes about this track here",
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
    print(f"   ✓ Created metadata.json - Track metadata template")

    # Create README
    readme_content = f"""# Track {track_number}

## Status: In Progress

### Created: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Workflow

1. **Select songs from bank** (optional):
   ```bash
   # By count (e.g., 5 songs)
   ./venv/bin/python3 agent/select_bank_songs.py --track {track_number} --count 5 --flow-id 04

   # By duration (e.g., 30 minutes)
   ./venv/bin/python3 agent/select_bank_songs.py --track {track_number} --duration 30 --flow-id 04

   # Execute the selection
   ./venv/bin/python3 agent/select_bank_songs.py --track {track_number} --execute
   ```

2. **Add new songs manually**:
   - Generate songs in Suno
   - Download to ~/Downloads/
   - Move to half_1/ or half_2/:
     ```bash
     mv ~/Downloads/new_song*.mp3 {track_folder}/half_1/
     ```

3. **Add video and image**:
   ```bash
   cp ~/path/to/background.mp4 {track_folder}/video/{track_number}.mp4
   cp ~/path/to/cover.jpg {track_folder}/image/{track_number}.jpg
   ```

4. **Build track** (auto A_/B_ prefixing):
   ```bash
   ./venv/bin/python3 agent/build_track.py --track {track_number} --duration 3
   ```

5. **Add new songs to bank** (after successful render):
   ```bash
   ./venv/bin/python3 agent/add_to_bank.py --track {track_number} --flow-id 04
   ```

---

## Folder Structure

- `half_1/` - Songs for first half (A_ prefix applied during render)
- `half_2/` - Songs for second half (B_ prefix applied during render)
- `video/` - Background video ({track_number}.mp4)
- `image/` - Cover art ({track_number}.jpg)
- `metadata.json` - Track metadata
- `bank_selection.json` - Songs selected from bank (auto-generated)

---

## Notes

Add your notes here about theme, mood, track flow references, etc.
"""

    readme_file = track_folder / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"   ✓ Created README.md - Workflow instructions")

    print(f"\n✅ Track {track_number} template created successfully!")
    print(f"\n📋 Folder structure:")
    print(f"   {track_folder}/")
    print(f"   ├── half_1/          (empty - add first half songs here)")
    print(f"   ├── half_2/          (empty - add second half songs here)")
    print(f"   ├── video/           (empty - add {track_number}.mp4)")
    print(f"   ├── image/           (empty - add {track_number}.jpg)")
    print(f"   ├── metadata.json    (track metadata template)")
    print(f"   └── README.md        (workflow instructions)")

    print(f"\n🎯 Next steps:")
    print(f"   1. Select songs from bank:")
    print(f"      ./venv/bin/python3 agent/select_bank_songs.py --track {track_number} --count 5 --flow-id 04")
    print(f"   2. Add new songs to half_1/ and half_2/")
    print(f"   3. Add video: cp background.mp4 {track_folder}/video/{track_number}.mp4")
    print(f"   4. Add image: cp cover.jpg {track_folder}/image/{track_number}.jpg")
    print(f"   5. Build track: ./venv/bin/python3 agent/build_track.py --track {track_number}")

    return track_folder

def main():
    parser = argparse.ArgumentParser(
        description="Create track template with auto-incrementing track number"
    )
    parser.add_argument(
        '--track-number',
        type=int,
        help='Specific track number (optional, auto-increments if not provided)'
    )

    args = parser.parse_args()

    track_folder = create_track_template(track_number=args.track_number)

    if track_folder:
        print(f"\n🎉 Ready to create Track {track_folder.name}!")

if __name__ == "__main__":
    main()
