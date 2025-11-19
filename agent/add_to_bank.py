#!/usr/bin/env python3
"""
Add to Bank
-----------
Adds new (non-banked) songs from a track to the song bank with proper naming.

Usage:
    python3 agent/add_to_bank.py --track 16 --flow-id 04
    python3 agent/add_to_bank.py --track 16 --flow-id 04 --analyze
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"
SONG_BANK_DIR = PROJECT_ROOT / "song_bank"
CATALOG_FILE = SONG_BANK_DIR / "metadata" / "song_catalog.json"
PROMPT_INDEX_FILE = SONG_BANK_DIR / "metadata" / "prompt_index.json"

def load_catalog():
    """Load song catalog from JSON."""
    if not CATALOG_FILE.exists():
        return {"catalog_version": "1.0", "last_updated": None, "total_tracks": 0, "tracks": {}}

    with open(CATALOG_FILE, 'r') as f:
        return json.load(f)

def save_catalog(catalog):
    """Save catalog to JSON."""
    catalog["last_updated"] = datetime.now().isoformat()
    catalog["total_tracks"] = len(catalog.get("tracks", {}))

    with open(CATALOG_FILE, 'w') as f:
        json.dump(catalog, f, indent=2)

def load_prompt_index():
    """Load prompt index from JSON."""
    if not PROMPT_INDEX_FILE.exists():
        return {"prompts": {}}

    with open(PROMPT_INDEX_FILE, 'r') as f:
        return json.load(f)

def save_prompt_index(index):
    """Save prompt index to JSON."""
    with open(PROMPT_INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

def is_song_in_bank(filename, catalog):
    """Check if a song (by original filename) is already in the bank."""
    for track_id, track_data in catalog.get("tracks", {}).items():
        original_name = track_data.get("original_filename")
        if original_name and original_name == filename:
            return True
    return False

def get_new_songs_from_track(track_number):
    """
    Identify new (non-banked) songs from a track's half_1/ and half_2/ folders.

    Returns:
        List of tuples: [(path, half), ...]
    """
    catalog = load_catalog()
    track_folder = TRACKS_DIR / str(track_number)

    new_songs = []

    # Check half_1
    half_1_folder = track_folder / "half_1"
    if half_1_folder.exists():
        for song_path in half_1_folder.glob("*.mp3"):
            if not is_song_in_bank(song_path.name, catalog):
                new_songs.append((song_path, "A"))

    # Check half_2
    half_2_folder = track_folder / "half_2"
    if half_2_folder.exists():
        for song_path in half_2_folder.glob("*.mp3"):
            if not is_song_in_bank(song_path.name, catalog):
                new_songs.append((song_path, "B"))

    return new_songs

def prompt_for_metadata(song_path, suggested_half):
    """
    Interactively prompt user for song metadata.

    Args:
        song_path: Path to the song file
        suggested_half: "A" or "B" based on folder location

    Returns:
        Dict with metadata: {half, phase, song_num, order}
    """
    print(f"\n🎵 Song: {song_path.name}")
    print(f"   Suggested half: {suggested_half}")

    # Half
    half_input = input(f"   Half (A/B) [default: {suggested_half}]: ").strip().upper()
    half = half_input if half_input in ["A", "B"] else suggested_half

    # Phase
    while True:
        phase_input = input("   Phase (1=Calm, 2=Flow, 3=Uplift, 4=Reflect): ").strip()
        if phase_input in ["1", "2", "3", "4"]:
            phase = int(phase_input)
            break
        print("      ❌ Invalid. Must be 1, 2, 3, or 4")

    # Song number within phase
    while True:
        song_num_input = input("   Song number within phase (e.g., 5): ").strip()
        try:
            song_num = int(song_num_input)
            if song_num > 0:
                break
        except ValueError:
            pass
        print("      ❌ Invalid. Must be a positive integer")

    # Order letter
    while True:
        order_input = input("   Order letter (a-z, e.g., 'a' for first, 'b' for second): ").strip().lower()
        if len(order_input) == 1 and order_input.isalpha():
            order = order_input
            break
        print("      ❌ Invalid. Must be a single letter (a-z)")

    return {
        "half": half,
        "phase": phase,
        "song_num": song_num,
        "order": order
    }

def generate_bank_filename(half, phase, song_num, track_number, order):
    """
    Generate bank filename in format: A_2_5_15a.mp3

    Args:
        half: "A" or "B"
        phase: 1-4
        song_num: Song number within phase
        track_number: Track number this song came from
        order: Order letter (a-z)

    Returns:
        Filename string
    """
    return f"{half}_{phase}_{song_num}_{track_number:03d}{order}.mp3"

def run_audio_analysis(song_path):
    """
    Run audio analysis on a song using analyze_audio.py.

    Returns:
        Dict with audio features, or None on failure
    """
    try:
        # For now, return basic structure
        # TODO: Integrate with analyze_audio.py or use librosa directly
        return {
            "duration": 0,
            "bpm": None,
            "brightness": None,
            "energy": None,
            "key": None
        }
    except Exception as e:
        print(f"   ⚠️  Audio analysis failed: {e}")
        return None

def add_song_to_bank(song_path, metadata, track_number, flow_id, catalog, prompt_index):
    """
    Add a song to the bank with proper naming and metadata.

    Args:
        song_path: Path to original song file
        metadata: Dict with {half, phase, song_num, order}
        track_number: Track number this song came from
        flow_id: Flow ID (e.g., "04")
        catalog: Song catalog dictionary
        prompt_index: Prompt index dictionary

    Returns:
        True if successful, False otherwise
    """
    # Generate bank filename
    bank_filename = generate_bank_filename(
        metadata["half"],
        metadata["phase"],
        metadata["song_num"],
        track_number,
        metadata["order"]
    )

    # Determine destination path
    bank_track_folder = SONG_BANK_DIR / "tracks" / str(track_number)
    bank_track_folder.mkdir(parents=True, exist_ok=True)

    dest_path = bank_track_folder / bank_filename

    # Check if file already exists
    if dest_path.exists():
        print(f"   ⚠️  Warning: {bank_filename} already exists in bank")
        response = input("      Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("      Skipped.")
            return False

    # Copy file
    shutil.copy2(song_path, dest_path)

    # Run audio analysis
    audio_features = run_audio_analysis(dest_path)

    # Generate track ID
    track_id = f"{metadata['half']}_{metadata['phase']}_{metadata['song_num']}_{track_number:03d}{metadata['order']}"

    # Update catalog
    catalog.setdefault("tracks", {})[track_id] = {
        "filename": bank_filename,
        "path": str(dest_path),
        "original_filename": song_path.name,
        "source_track": track_number,
        "flow_id": flow_id,
        "naming_breakdown": {
            "half": metadata["half"],
            "phase": metadata["phase"],
            "song_num": metadata["song_num"],
            "track_num": track_number,
            "order": metadata["order"]
        },
        "audio_analysis": audio_features if audio_features else {},
        "added_to_bank": datetime.now().isoformat(),
        "track_flow": {
            "flow_id": flow_id,
            "prompt": ""  # TODO: Link to prompt index
        }
    }

    print(f"   ✅ Added to bank: {bank_filename}")

    return True

def main():
    parser = argparse.ArgumentParser(
        description="Add new songs from a track to the song bank"
    )
    parser.add_argument(
        '--track',
        type=int,
        required=True,
        help='Track number to process'
    )
    parser.add_argument(
        '--flow-id',
        type=str,
        required=True,
        help='Track flow ID (e.g., "04")'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run audio analysis on songs (requires librosa)'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-mode: use default metadata (for testing)'
    )

    args = parser.parse_args()

    track_folder = TRACKS_DIR / str(args.track)

    # Validate track exists
    if not track_folder.exists():
        print(f"❌ Error: Track {args.track} does not exist")
        return

    # Find new songs
    print(f"\n🔍 Searching for new songs in Track {args.track}...")
    new_songs = get_new_songs_from_track(args.track)

    if not new_songs:
        print(f"✅ No new songs found. All songs already in bank.")
        return

    print(f"\n📋 Found {len(new_songs)} new songs:")
    for song_path, half in new_songs:
        print(f"   - {song_path.name} (half_{1 if half == 'A' else 2})")

    print(f"\n🎯 Adding songs to bank...")
    print(f"   Flow ID: {args.flow_id}")

    # Load catalog and prompt index
    catalog = load_catalog()
    prompt_index = load_prompt_index()

    added_count = 0

    for song_path, suggested_half in new_songs:
        if args.auto:
            # Auto mode: use defaults for testing
            metadata = {
                "half": suggested_half,
                "phase": 1,
                "song_num": 1,
                "order": "a"
            }
        else:
            # Interactive mode
            metadata = prompt_for_metadata(song_path, suggested_half)

        success = add_song_to_bank(
            song_path,
            metadata,
            args.track,
            args.flow_id,
            catalog,
            prompt_index
        )

        if success:
            added_count += 1

    # Save catalog
    save_catalog(catalog)
    save_prompt_index(prompt_index)

    print(f"\n✅ Successfully added {added_count} songs to bank!")
    print(f"📁 Catalog updated: {CATALOG_FILE}")
    print(f"📊 Total songs in bank: {catalog['total_tracks']}")

    print(f"\n🎯 Next steps:")
    print(f"   1. Review catalog: cat {CATALOG_FILE}")
    print(f"   2. Use these songs in future tracks:")
    print(f"      ./venv/bin/python3 agent/select_bank_songs.py --track <num> --flow-id {args.flow_id}")

if __name__ == "__main__":
    main()
