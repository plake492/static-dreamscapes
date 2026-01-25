#!/usr/bin/env python3
"""
Copy matched songs from query results to a track's Songs folder.
"""
import json
import shutil
from pathlib import Path
import sys

def parse_track_from_filename(filename: str) -> str:
    """Extract track number from filename like A_1_1_22a.mp3 -> 22"""
    # Remove .mp3 extension
    name_without_ext = filename.replace('.mp3', '')
    parts = name_without_ext.split('_')

    if len(parts) >= 4:
        # Last component contains track number + variant letter (e.g., "22a" or "999d")
        last_part = parts[3]
        # Extract just the numeric part
        track_num = ''.join(c for c in last_part if c.isdigit())
        return track_num if track_num else None

    return None

def copy_matches(query_file: str, target_track: str, base_dir: Path):
    """Copy all matched songs to target track's Songs folder."""

    # Load query results
    with open(query_file, 'r') as f:
        data = json.load(f)

    # Collect all unique filenames
    filenames = set()
    total_duration = 0

    for arc_key, arc_data in data['results'].items():
        for prompt_data in arc_data:
            for match in prompt_data['matches']:
                filenames.add(match['filename'])
                total_duration += match['duration']

    print(f"Found {len(filenames)} unique matched songs")
    print(f"Total duration: {total_duration} seconds ({total_duration / 60:.1f} minutes)")

    # Create target directory
    target_dir = base_dir / target_track / "Songs"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy each file
    copied = 0
    not_found = []

    for filename in sorted(filenames):
        # Determine source track
        track_num = parse_track_from_filename(filename)
        if not track_num:
            print(f"⚠️  Could not parse track number from: {filename}")
            continue

        source_path = base_dir / track_num / "Songs" / filename
        target_path = target_dir / filename

        if not source_path.exists():
            not_found.append(filename)
            print(f"❌ Not found: {source_path}")
            continue

        # Copy file
        shutil.copy2(source_path, target_path)
        copied += 1
        print(f"✅ Copied: {filename} (from Track {track_num})")

    print(f"\n{'='*60}")
    print(f"✅ Successfully copied {copied}/{len(filenames)} files")
    print(f"📁 Target: {target_dir}")
    print(f"⏱️  Total duration: {total_duration} seconds ({total_duration / 60:.1f} minutes / {total_duration / 3600:.2f} hours)")

    if not_found:
        print(f"\n⚠️  {len(not_found)} files not found:")
        for fn in not_found:
            print(f"   - {fn}")

    return copied, total_duration

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 copy_matches_to_track.py <query_file.json> <target_track_number>")
        sys.exit(1)

    query_file = sys.argv[1]
    target_track = sys.argv[2]
    base_dir = Path("Tracks")

    copy_matches(query_file, target_track, base_dir)
