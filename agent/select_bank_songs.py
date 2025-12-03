#!/usr/bin/env python3
"""
Select Bank Songs
-----------------
Query song bank and select songs for a track by count OR duration.

Usage:
    # Select by count
    python3 agent/select_bank_songs.py --track 16 --count 5 --flow-id 04

    # Select by duration
    python3 agent/select_bank_songs.py --track 16 --duration 30 --flow-id 04

    # Execute the selection (copy files)
    python3 agent/select_bank_songs.py --track 16 --execute
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"
SONG_BANK_DIR = PROJECT_ROOT / "song_bank"
CATALOG_FILE = SONG_BANK_DIR / "metadata" / "song_catalog.json"

def load_catalog():
    """Load song catalog from JSON."""
    if not CATALOG_FILE.exists():
        return {"tracks": {}}

    with open(CATALOG_FILE, 'r') as f:
        return json.load(f)

def load_track_metadata(track_number):
    """Load metadata for a specific track."""
    metadata_file = TRACKS_DIR / str(track_number) / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, 'r') as f:
        return json.load(f)

def load_bank_selection(track_number):
    """Load existing bank selection for a track."""
    selection_file = TRACKS_DIR / str(track_number) / "bank_selection.json"
    if not selection_file.exists():
        return None

    with open(selection_file, 'r') as f:
        return json.load(f)

def save_bank_selection(track_number, selection_data):
    """Save bank selection to track folder."""
    selection_file = TRACKS_DIR / str(track_number) / "bank_selection.json"
    with open(selection_file, 'w') as f:
        json.dump(selection_data, f, indent=2)
    return selection_file

def select_songs_by_count(catalog, count, flow_id=None, theme=None):
    """
    Select N songs from the bank.

    Args:
        catalog: Song catalog dictionary
        count: Number of songs to select
        flow_id: Optional track flow ID to filter by
        theme: Optional theme to filter by

    Returns:
        List of selected song entries
    """
    tracks = catalog.get("tracks", {})

    if not tracks:
        print("⚠️  Song bank is empty. No songs to select.")
        return []

    # For now, simple selection (can be enhanced with smart matching)
    # TODO: Implement flow_id and theme filtering when track flows are populated
    selected = []
    for track_id, track_data in sorted(tracks.items()):
        if len(selected) >= count:
            break
        selected.append({
            "track_id": track_id,
            "filename": track_data.get("filename"),
            "source": track_data.get("path"),
            "phase": track_data.get("naming_breakdown", {}).get("phase"),
            "half": track_data.get("naming_breakdown", {}).get("half"),
            "duration": track_data.get("audio_analysis", {}).get("duration", 0),
            "bpm": track_data.get("audio_analysis", {}).get("bpm"),
            "prompt": track_data.get("track_flow", {}).get("prompt", ""),
        })

    return selected

def select_songs_by_duration(catalog, target_duration_minutes, flow_id=None, theme=None):
    """
    Select songs totaling approximately target_duration minutes.

    Args:
        catalog: Song catalog dictionary
        target_duration_minutes: Target total duration in minutes
        flow_id: Optional track flow ID to filter by
        theme: Optional theme to filter by

    Returns:
        List of selected song entries
    """
    tracks = catalog.get("tracks", {})

    if not tracks:
        print("⚠️  Song bank is empty. No songs to select.")
        return []

    target_seconds = target_duration_minutes * 60
    selected = []
    total_duration = 0

    # TODO: Implement smart selection (phase balance, flow_id, theme)
    for track_id, track_data in sorted(tracks.items()):
        duration = track_data.get("audio_analysis", {}).get("duration", 0)

        if total_duration + duration > target_seconds + 120:  # +2 min tolerance
            # Would exceed target too much
            continue

        selected.append({
            "track_id": track_id,
            "filename": track_data.get("filename"),
            "source": track_data.get("path"),
            "phase": track_data.get("naming_breakdown", {}).get("phase"),
            "half": track_data.get("naming_breakdown", {}).get("half"),
            "duration": duration,
            "bpm": track_data.get("audio_analysis", {}).get("bpm"),
            "prompt": track_data.get("track_flow", {}).get("prompt", ""),
        })

        total_duration += duration

        if total_duration >= target_seconds - 120:  # Within 2 min of target
            break

    return selected, total_duration / 60  # Return duration in minutes

def create_selection(track_number, method, selection_criteria, selected_songs, total_duration=None):
    """Create bank selection data structure."""
    return {
        "track_number": track_number,
        "created": datetime.now().isoformat(),
        "selection_method": method,
        "selection_criteria": selection_criteria,
        "selected_songs": selected_songs,
        "total_songs": len(selected_songs),
        "total_duration": total_duration if total_duration else sum(s.get("duration", 0) for s in selected_songs),
        "executed": False
    }

def execute_selection(track_number):
    """Execute the bank selection - copy files to track folders."""
    selection = load_bank_selection(track_number)

    if not selection:
        print(f"❌ Error: No bank selection found for track {track_number}")
        print(f"   Run selection first: python3 agent/select_bank_songs.py --track {track_number} --count 5")
        return False

    if selection.get("executed"):
        print(f"⚠️  Bank selection for track {track_number} already executed.")
        response = input("   Re-execute? This will overwrite existing files. (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled.")
            return False

    track_folder = TRACKS_DIR / str(track_number)
    half_1_folder = track_folder / "half_1"
    half_2_folder = track_folder / "half_2"

    print(f"\n🎵 Executing bank selection for Track {track_number}...")
    print(f"   Copying {selection['total_songs']} songs ({selection['total_duration']/60:.1f} minutes)...")

    copied_count = 0
    for song in selection["selected_songs"]:
        source_path = Path(song["source"])

        if not source_path.exists():
            print(f"   ⚠️  Skipping {song['filename']} - source file not found")
            continue

        # Determine destination based on half
        half = song.get("half", "A")
        if half == "A":
            dest_folder = half_1_folder
        else:
            dest_folder = half_2_folder

        dest_path = dest_folder / song["filename"]

        # Copy file
        shutil.copy2(source_path, dest_path)
        print(f"   ✓ Copied {song['filename']} → {dest_folder.name}/")
        copied_count += 1

    # Update selection as executed
    selection["executed"] = True
    selection["executed_at"] = datetime.now().isoformat()
    save_bank_selection(track_number, selection)

    print(f"\n✅ Successfully copied {copied_count} songs to track {track_number}")
    print(f"   half_1/: Check {half_1_folder}")
    print(f"   half_2/: Check {half_2_folder}")
    print(f"\n🎯 Next step: Add new songs manually, then build track")
    print(f"   ./venv/bin/python3 agent/build_track.py --track {track_number}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Select songs from bank for a track"
    )
    parser.add_argument(
        '--track',
        type=int,
        required=True,
        help='Track number'
    )
    parser.add_argument(
        '--count',
        type=int,
        help='Number of songs to select from bank'
    )
    parser.add_argument(
        '--duration',
        type=float,
        help='Target duration in minutes (e.g., 30 for 30 minutes)'
    )
    parser.add_argument(
        '--flow-id',
        type=str,
        help='Track flow ID to filter songs (e.g., "04")'
    )
    parser.add_argument(
        '--theme',
        type=str,
        help='Theme to filter songs (e.g., "neon rain calm")'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the selection (copy files to track folder)'
    )

    args = parser.parse_args()

    # If --execute flag, run execution and exit
    if args.execute:
        execute_selection(args.track)
        return

    # Validate arguments
    if not args.count and not args.duration:
        print("❌ Error: Must specify either --count or --duration")
        print("   Examples:")
        print("     python3 agent/select_bank_songs.py --track 16 --count 5")
        print("     python3 agent/select_bank_songs.py --track 16 --duration 30")
        return

    if args.count and args.duration:
        print("❌ Error: Cannot specify both --count and --duration. Choose one.")
        return

    # Check if track exists
    track_folder = TRACKS_DIR / str(args.track)
    if not track_folder.exists():
        print(f"❌ Error: Track {args.track} does not exist")
        print(f"   Create it first: python3 agent/create_track_template.py --track-number {args.track}")
        return

    # Load catalog
    catalog = load_catalog()

    if not catalog.get("tracks"):
        print(f"\n⚠️  Song bank is currently empty.")
        print(f"   Songs will be added to the bank after you build and run:")
        print(f"   ./venv/bin/python3 agent/add_to_bank.py --track {args.track}")
        print(f"\n   For now, you'll need to add all songs manually to:")
        print(f"   - {track_folder}/half_1/")
        print(f"   - {track_folder}/half_2/")
        return

    # Perform selection
    print(f"\n🔍 Selecting songs from bank for Track {args.track}...")

    if args.count:
        print(f"   Method: By count ({args.count} songs)")
        selected = select_songs_by_count(catalog, args.count, args.flow_id, args.theme)
        selection_data = create_selection(
            args.track,
            "count",
            {"count": args.count, "flow_id": args.flow_id, "theme": args.theme},
            selected
        )
    else:  # args.duration
        print(f"   Method: By duration ({args.duration} minutes)")
        selected, actual_duration = select_songs_by_duration(
            catalog, args.duration, args.flow_id, args.theme
        )
        selection_data = create_selection(
            args.track,
            "duration",
            {"target_duration": args.duration, "flow_id": args.flow_id, "theme": args.theme},
            selected,
            total_duration=actual_duration * 60
        )

    if not selected:
        print(f"\n⚠️  No songs selected. Bank may be empty or no matches found.")
        return

    # Save selection
    selection_file = save_bank_selection(args.track, selection_data)

    # Display selection
    print(f"\n✅ Selected {len(selected)} songs:")
    for i, song in enumerate(selected, 1):
        duration_min = song.get("duration", 0) / 60
        phase = song.get("phase", "?")
        half = song.get("half", "?")
        print(f"   {i}. {song['filename']} ({duration_min:.1f} min, Phase {phase}, Half {half})")

    total_duration = selection_data["total_duration"]
    print(f"\n📊 Total duration: {total_duration/60:.1f} minutes")
    print(f"📁 Selection saved to: {selection_file}")

    print(f"\n🎯 Next steps:")
    print(f"   1. Review selection in {selection_file}")
    print(f"   2. Execute copy: ./venv/bin/python3 agent/select_bank_songs.py --track {args.track} --execute")
    print(f"   3. Add new songs manually to half_1/ and half_2/")
    print(f"   4. Build track: ./venv/bin/python3 agent/build_track.py --track {args.track}")

if __name__ == "__main__":
    main()
