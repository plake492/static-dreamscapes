#!/usr/bin/env python3
"""
Add to Bank
-----------
Adds new (non-banked) songs from a track to the song bank with proper naming.

Auto-detects metadata from filenames in bank format (A_[phase]_[song]_[track][order].mp3).
Handles songs with A_/B_ prefixes automatically (strips them for deduplication).
Cleans songs with special characters (removes them automatically).

Usage:
    # Single track
    python3 agent/add_to_bank.py --track 16 --flow-id 04
    python3 agent/add_to_bank.py --track 16 --flow-id 04 --analyze

    # Bulk processing (all tracks) - NO PROMPTS if filenames are properly formatted
    python3 agent/add_to_bank.py --bulk --flow-id 04
    python3 agent/add_to_bank.py --flow-id 04  # --bulk is optional, triggers if --track omitted

Auto-Detection:
    # Songs in bank format are processed automatically without prompts
    A_2_6_12a.mp3 -> Auto-detected: Half A, Phase 2, Song 6, Order a
    B_1_3_15b.mp3 -> Auto-detected: Half B, Phase 1, Song 3, Order b

    # Only prompts if filename doesn't match format
    random_song.mp3 -> Prompts for metadata interactively

Examples:
    # Songs with A_/B_ prefixes are handled automatically
    A_001_song.mp3 -> normalized to 001_song.mp3 for deduplication
    B_song.mp3 -> normalized to song.mp3 for deduplication

    # Songs with special characters are cleaned
    1_1_16_a!.mp3 -> cleaned to 1_1_16_a.mp3
    song_name!@#.mp3 -> cleaned to song_name.mp3

    # Bulk processing skips tracks that are already fully in bank
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

def normalize_filename(filename):
    """
    Normalize filename by removing A_/B_ prefixes if present.

    Examples:
        A_001_song.mp3 -> 001_song.mp3
        B_song.mp3 -> song.mp3
        song.mp3 -> song.mp3
    """
    # Remove A_ or B_ prefix if present at the start
    if filename.startswith("A_") or filename.startswith("B_"):
        return filename[2:]
    return filename

def clean_filename(filename):
    """
    Clean filename by removing special characters.

    Examples:
        1_1_16_a!.mp3 -> 1_1_16_a.mp3
        song_name!@#.mp3 -> song_name.mp3
        track_b@.mp3 -> track_b.mp3

    Returns:
        Cleaned filename with extension
    """
    # Split extension
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
    else:
        name = filename
        ext = ""

    # Remove special characters (keep alphanumeric, underscore, hyphen)
    cleaned_name = ''.join(c for c in name if c.isalnum() or c in ['_', '-'])

    # Reconstruct filename
    if ext:
        return f"{cleaned_name}.{ext}"
    return cleaned_name

def is_song_in_bank(filename, catalog):
    """Check if a song (by original filename) is already in the bank."""
    # Clean and normalize the filename to compare
    cleaned = clean_filename(filename)
    normalized_filename = normalize_filename(cleaned)

    for track_id, track_data in catalog.get("tracks", {}).items():
        original_name = track_data.get("original_filename")
        if original_name:
            normalized_original = normalize_filename(original_name)
            if normalized_original == normalized_filename:
                return True
    return False

def get_new_songs_from_track(track_number):
    """
    Identify new (non-banked) songs from a track's half_1/ and half_2/ folders.

    Returns:
        List of tuples: [(path, half, cleaned_name), ...]
    """
    catalog = load_catalog()
    track_folder = TRACKS_DIR / str(track_number)

    new_songs = []
    cleaned_songs = []

    # Check half_1
    half_1_folder = track_folder / "half_1"
    if half_1_folder.exists():
        for song_path in half_1_folder.glob("*.mp3"):
            # Clean filename if needed
            cleaned_name = clean_filename(song_path.name)
            if cleaned_name != song_path.name:
                cleaned_songs.append((song_path.name, cleaned_name))

            if not is_song_in_bank(song_path.name, catalog):
                new_songs.append((song_path, "A", cleaned_name))

    # Check half_2
    half_2_folder = track_folder / "half_2"
    if half_2_folder.exists():
        for song_path in half_2_folder.glob("*.mp3"):
            # Clean filename if needed
            cleaned_name = clean_filename(song_path.name)
            if cleaned_name != song_path.name:
                cleaned_songs.append((song_path.name, cleaned_name))

            if not is_song_in_bank(song_path.name, catalog):
                new_songs.append((song_path, "B", cleaned_name))

    # Report cleaned songs
    if cleaned_songs:
        print(f"\n🧹 Cleaned {len(cleaned_songs)} filenames (removed special characters):")
        for original, cleaned in cleaned_songs:
            print(f"   - {original} → {cleaned}")

    return new_songs

def extract_metadata_from_filename(filename):
    """
    Extract metadata from bank-formatted filename.

    Format: A_[phase]_[song]_[track][order].mp3
    Example: A_2_6_12a.mp3 -> {half: A, phase: 2, song_num: 6, order: a}

    Handles filenames with special characters (cleans them first).
    Example: A_2_6_13a*.mp3 -> {half: A, phase: 2, song_num: 6, order: a}

    Returns:
        Dict with metadata if successful, None if format doesn't match
    """
    import re

    # Clean filename first (remove special characters)
    cleaned = clean_filename(filename)

    # Remove extension
    name_without_ext = cleaned.rsplit('.', 1)[0]

    # Pattern: A_[phase]_[song]_[track][order]
    # We need to extract: half, phase, song_num, order
    # track is embedded in position 3 but we don't need it here
    parts = name_without_ext.split('_')

    if len(parts) >= 4 and parts[0] in ['A', 'B']:
        try:
            half = parts[0]
            phase = int(parts[1])
            song_num = int(parts[2])

            # Extract order letter from fourth part (e.g., "12a" -> "a", "13a" -> "a")
            fourth_part = parts[3]
            match = re.search(r'([a-z])$', fourth_part)
            if match:
                order = match.group(1)

                # Validate phase
                if 1 <= phase <= 4:
                    return {
                        "half": half,
                        "phase": phase,
                        "song_num": song_num,
                        "order": order
                    }
        except (ValueError, IndexError):
            pass

    return None

def prompt_for_metadata(song_path, suggested_half):
    """
    Extract metadata from filename or interactively prompt user if needed.

    Args:
        song_path: Path to the song file
        suggested_half: "A" or "B" based on folder location

    Returns:
        Dict with metadata: {half, phase, song_num, order}
    """
    # Try to extract from filename first
    auto_metadata = extract_metadata_from_filename(song_path.name)

    if auto_metadata:
        print(f"\n🎵 Song: {song_path.name}")
        print(f"   ✅ Auto-detected: Half {auto_metadata['half']}, Phase {auto_metadata['phase']}, Song {auto_metadata['song_num']}, Order {auto_metadata['order']}")
        return auto_metadata

    # Fall back to interactive prompts
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

def extract_prompts_from_track_flow(track_number):
    """
    Extract prompts from track flow markdown file.

    Looks for track_XXX_flow.md in the track folder and extracts
    any Suno prompts or theme information.

    Returns:
        Dict with prompts by phase, or None if not found
    """
    import re

    track_folder = TRACKS_DIR / str(track_number)
    flow_file = track_folder / f"track_{track_number:03d}_flow.md"

    if not flow_file.exists():
        return None

    try:
        with open(flow_file, 'r') as f:
            content = f.read()

        prompts = {}

        # Look for phase-specific prompts
        # Pattern: ## Phase X or ### Phase X
        phase_pattern = r'##\s*Phase\s*(\d+)[^\n]*\n(.*?)(?=##\s*Phase|\Z)'
        matches = re.finditer(phase_pattern, content, re.DOTALL | re.IGNORECASE)

        for match in matches:
            phase_num = int(match.group(1))
            phase_content = match.group(2)

            # Extract prompt text (look for code blocks or quoted sections)
            prompt_text = None

            # Try to find code blocks
            code_block = re.search(r'```(?:text|prompt)?\n(.*?)\n```', phase_content, re.DOTALL)
            if code_block:
                prompt_text = code_block.group(1).strip()
            else:
                # Try to find quoted sections
                quote = re.search(r'>\s*(.+)', phase_content, re.MULTILINE)
                if quote:
                    prompt_text = quote.group(1).strip()

            if prompt_text:
                prompts[phase_num] = prompt_text

        return prompts if prompts else None

    except Exception as e:
        print(f"   ⚠️  Could not extract prompts from track flow: {e}")
        return None

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

def add_song_to_bank(song_path, metadata, track_number, flow_id, catalog, prompt_index, auto_skip=False):
    """
    Add a song to the bank with proper naming and metadata.

    Args:
        song_path: Path to original song file
        metadata: Dict with {half, phase, song_num, order}
        track_number: Track number this song came from
        flow_id: Flow ID (e.g., "04")
        catalog: Song catalog dictionary
        prompt_index: Prompt index dictionary
        auto_skip: If True, automatically skip duplicates without prompting

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
        if auto_skip:
            print("      Auto-skipped (duplicate).")
            return False
        else:
            response = input("      Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print("      Skipped.")
                return False

    # Copy file
    shutil.copy2(song_path, dest_path)

    # Run audio analysis
    audio_features = run_audio_analysis(dest_path)

    # Extract prompts from track flow file
    track_prompts = extract_prompts_from_track_flow(track_number)
    phase_prompt = None
    if track_prompts and metadata["phase"] in track_prompts:
        phase_prompt = track_prompts[metadata["phase"]]

        # Update prompt index
        prompt_key = f"track_{track_number:03d}_phase_{metadata['phase']}"
        if prompt_key not in prompt_index.get("prompts", {}):
            prompt_index.setdefault("prompts", {})[prompt_key] = {
                "track_number": track_number,
                "flow_id": flow_id,
                "phase": metadata["phase"],
                "prompt_text": phase_prompt,
                "songs": []
            }
        # Add this song to the prompt's song list
        prompt_index["prompts"][prompt_key]["songs"].append(track_id)

    # Generate track ID
    track_id = f"{metadata['half']}_{metadata['phase']}_{metadata['song_num']}_{track_number:03d}{metadata['order']}"

    # Store normalized filename (without A_/B_ prefix, with special chars cleaned) for deduplication
    cleaned = clean_filename(song_path.name)
    normalized_original = normalize_filename(cleaned)

    # Update catalog
    catalog.setdefault("tracks", {})[track_id] = {
        "filename": bank_filename,
        "path": str(dest_path),
        "original_filename": normalized_original,
        "original_filename_raw": song_path.name,  # Keep raw name for reference
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
            "prompt": phase_prompt if phase_prompt else ""
        }
    }

    print(f"   ✅ Added to bank: {bank_filename}")
    if phase_prompt:
        print(f"   📝 Linked prompt: {phase_prompt[:60]}..." if len(phase_prompt) > 60 else f"   📝 Linked prompt: {phase_prompt}")

    return True

def get_all_tracks_with_songs():
    """
    Find all track folders that contain songs.

    Returns:
        List of track numbers
    """
    if not TRACKS_DIR.exists():
        return []

    track_numbers = []
    for track_folder in TRACKS_DIR.iterdir():
        if not track_folder.is_dir():
            continue

        # Check if folder name is numeric
        if not track_folder.name.isdigit():
            continue

        track_num = int(track_folder.name)

        # Check if track has songs
        half_1 = track_folder / "half_1"
        half_2 = track_folder / "half_2"

        has_songs = False
        if half_1.exists() and any(half_1.glob("*.mp3")):
            has_songs = True
        if half_2.exists() and any(half_2.glob("*.mp3")):
            has_songs = True

        if has_songs:
            track_numbers.append(track_num)

    return sorted(track_numbers)

def main():
    parser = argparse.ArgumentParser(
        description="Add new songs from a track to the song bank"
    )
    parser.add_argument(
        '--track',
        type=int,
        help='Track number to process (omit for bulk processing)'
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
    parser.add_argument(
        '--bulk',
        action='store_true',
        help='Process all tracks in /tracks folder'
    )

    args = parser.parse_args()

    # Bulk mode: process all tracks
    if args.bulk or args.track is None:
        print(f"\n🔍 Scanning for tracks with songs...")
        track_numbers = get_all_tracks_with_songs()

        if not track_numbers:
            print(f"❌ No tracks with songs found in {TRACKS_DIR}")
            return

        print(f"📋 Found {len(track_numbers)} track(s) with songs: {', '.join(map(str, track_numbers))}")

        if not args.auto:
            response = input(f"\n   Process all {len(track_numbers)} tracks? (y/n): ").strip().lower()
            if response != 'y':
                print("   Cancelled.")
                return

        total_added = 0
        total_skipped = 0

        for track_num in track_numbers:
            print(f"\n{'=' * 70}")
            print(f"Processing Track {track_num}")
            print(f"{'=' * 70}")

            track_folder = TRACKS_DIR / str(track_num)

            if not track_folder.exists():
                print(f"⚠️  Track {track_num} folder doesn't exist, skipping")
                continue

            # Find new songs
            new_songs = get_new_songs_from_track(track_num)

            if not new_songs:
                print(f"✅ No new songs found. All songs already in bank.")
                total_skipped += 1
                continue

            print(f"\n📋 Found {len(new_songs)} new songs:")
            for song_path, half, cleaned_name in new_songs:
                display_name = cleaned_name if cleaned_name != song_path.name else song_path.name
                print(f"   - {display_name} (half_{1 if half == 'A' else 2})")

            # Load catalog and prompt index
            catalog = load_catalog()
            prompt_index = load_prompt_index()

            added_count = 0

            for song_path, suggested_half, cleaned_name in new_songs:
                if args.auto:
                    # Auto mode: use defaults
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
                    track_num,
                    args.flow_id,
                    catalog,
                    prompt_index,
                    auto_skip=True  # Auto-skip duplicates in bulk mode
                )

                if success:
                    added_count += 1

            # Save catalog
            save_catalog(catalog)
            save_prompt_index(prompt_index)

            print(f"\n✅ Added {added_count} songs from Track {track_num}")
            total_added += added_count

        print(f"\n{'=' * 70}")
        print(f"🎉 Bulk processing complete!")
        print(f"{'=' * 70}")
        print(f"✅ Total songs added: {total_added}")
        print(f"⏭️  Tracks skipped (no new songs): {total_skipped}")
        print(f"📊 Total tracks processed: {len(track_numbers)}")

        return

    # Single track mode
    if not args.track:
        print("❌ Error: --track is required for single track mode")
        print("   Use --bulk to process all tracks")
        return

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
    for song_path, half, cleaned_name in new_songs:
        display_name = cleaned_name if cleaned_name != song_path.name else song_path.name
        print(f"   - {display_name} (half_{1 if half == 'A' else 2})")

    print(f"\n🎯 Adding songs to bank...")
    print(f"   Flow ID: {args.flow_id}")

    # Load catalog and prompt index
    catalog = load_catalog()
    prompt_index = load_prompt_index()

    added_count = 0

    for song_path, suggested_half, cleaned_name in new_songs:
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
