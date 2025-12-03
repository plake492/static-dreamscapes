#!/usr/bin/env python3
"""
Build Track
-----------
Build final mix from half_1/ and half_2/ folders with automatic A_/B_ prefixing.

Usage:
    python3 agent/build_track.py --track 16 --duration 3
    python3 agent/build_track.py --track 16 --duration 1  # 1 hour test
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
RENDERED_DIR = PROJECT_ROOT / "rendered"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

def get_songs_from_half(half_folder):
    """Get all MP3 files from a half folder, sorted alphabetically."""
    if not half_folder.exists():
        return []

    mp3_files = sorted(half_folder.glob("*.mp3"))
    return mp3_files

def create_temp_prefixed_songs(track_number, half_1_songs, half_2_songs):
    """
    Create temporary folder with A_/B_ prefixed songs for rendering.

    Args:
        track_number: Track number
        half_1_songs: List of Path objects from half_1/
        half_2_songs: List of Path objects from half_2/

    Returns:
        Path to temp songs folder
    """
    track_folder = TRACKS_DIR / str(track_number)
    temp_songs_folder = track_folder / "temp_songs"

    # Clean up any existing temp folder
    if temp_songs_folder.exists():
        shutil.rmtree(temp_songs_folder)

    temp_songs_folder.mkdir()

    print(f"\n📝 Creating temporary prefixed songs for render...")

    tracklist = []
    position = 1

    # Process half_1 songs with A_ prefix
    for i, song_path in enumerate(half_1_songs, 1):
        # Create A_ prefixed name: A_001_original_name.mp3
        prefixed_name = f"A_{i:03d}_{song_path.name}"
        dest_path = temp_songs_folder / prefixed_name

        # Copy (not move - preserve originals)
        shutil.copy2(song_path, dest_path)

        tracklist.append({
            "position": position,
            "prefix": "A",
            "index_in_half": i,
            "source": str(song_path.relative_to(track_folder)),
            "render_name": prefixed_name,
            "from_bank": "_" in song_path.stem and song_path.stem.count("_") >= 3  # Has bank naming format
        })

        print(f"   A_{i:03d} ← {song_path.name}")
        position += 1

    # Process half_2 songs with B_ prefix
    for i, song_path in enumerate(half_2_songs, 1):
        # Create B_ prefixed name: B_001_original_name.mp3
        prefixed_name = f"B_{i:03d}_{song_path.name}"
        dest_path = temp_songs_folder / prefixed_name

        # Copy (not move - preserve originals)
        shutil.copy2(song_path, dest_path)

        tracklist.append({
            "position": position,
            "prefix": "B",
            "index_in_half": i,
            "source": str(song_path.relative_to(track_folder)),
            "render_name": prefixed_name,
            "from_bank": "_" in song_path.stem and song_path.stem.count("_") >= 3
        })

        print(f"   B_{i:03d} ← {song_path.name}")
        position += 1

    print(f"\n✅ Created {len(tracklist)} prefixed songs in temp_songs/")

    return temp_songs_folder, tracklist

def build_mix(track_number, duration_hours):
    """
    Build final mix using FFmpeg directly.

    Args:
        track_number: Track number
        duration_hours: Target duration in hours (or 'test' for 5 min)

    Returns:
        Path to output folder, or None on failure
    """
    track_folder = TRACKS_DIR / str(track_number)
    video_file = track_folder / "video" / f"{track_number}.mp4"
    temp_songs_folder = track_folder / "temp_songs"

    # Validate video exists
    if not video_file.exists():
        print(f"❌ Error: Background video not found: {video_file}")
        print(f"   Add video: cp background.mp4 {video_file}")
        return None

    # Validate temp_songs exists and has files
    if not temp_songs_folder.exists() or not list(temp_songs_folder.glob("*.mp3")):
        print(f"❌ Error: No songs in temp_songs/ folder")
        return None

    # Get sorted list of songs
    songs = sorted(temp_songs_folder.glob("*.mp3"))

    if not songs:
        print(f"❌ Error: No MP3 files found in temp_songs/")
        return None

    # Create timestamped output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = RENDERED_DIR / str(track_number) / f"output_{timestamp}"
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 Building mix with FFmpeg...")
    print(f"   Video: {video_file.name}")
    print(f"   Songs: {len(songs)} tracks")
    print(f"   Duration: {duration_hours} hours" if duration_hours != "test" else f"   Duration: 5 minutes (test mode)")
    print(f"   Output: {output_folder}")

    # Use existing build_mix.sh script
    # We'll call it with modified environment to use our temp structure
    build_script = SCRIPTS_DIR / "build_mix.sh"

    if not build_script.exists():
        print(f"❌ Error: build_mix.sh not found at {build_script}")
        return None

    # Create temporary structure that build_mix.sh expects
    # build_mix.sh looks for: tracks/<num>/video/<num>.mp4 and tracks/<num>/songs/*.mp3
    temp_songs_target = track_folder / "songs"

    # Clean up any existing songs folder
    if temp_songs_target.exists():
        shutil.rmtree(temp_songs_target)

    temp_songs_target.mkdir()

    # Copy prefixed songs to songs/ folder
    for song in songs:
        shutil.copy2(song, temp_songs_target / song.name)

    print(f"\n📋 Copied {len(songs)} prefixed songs to songs/ folder")

    # Call build_mix.sh
    try:
        result = subprocess.run(
            ["bash", str(build_script), str(track_number), str(duration_hours)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"\n✅ FFmpeg render complete!")
        print(f"   Output: {output_folder}")

        # Clean up temp songs folder in tracks/
        if temp_songs_target.exists():
            shutil.rmtree(temp_songs_target)

        return output_folder

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running build_mix.sh:")
        print(f"   {e.stderr}")

        # Clean up temp songs folder
        if temp_songs_target.exists():
            shutil.rmtree(temp_songs_target)

        return None

def save_tracklist(output_folder, track_number, tracklist, duration_hours):
    """Save tracklist metadata to output folder."""
    tracklist_file = output_folder / "tracklist.json"

    tracklist_data = {
        "track_number": track_number,
        "build_timestamp": datetime.now().isoformat(),
        "duration_hours": duration_hours,
        "total_tracks": len(tracklist),
        "tracks": tracklist
    }

    with open(tracklist_file, 'w') as f:
        json.dump(tracklist_data, f, indent=2)

    print(f"   ✓ Saved tracklist: {tracklist_file}")

def cleanup_temp_songs(track_number):
    """Clean up temporary prefixed songs folder."""
    temp_songs_folder = TRACKS_DIR / str(track_number) / "temp_songs"

    if temp_songs_folder.exists():
        shutil.rmtree(temp_songs_folder)
        print(f"   ✓ Cleaned up temp_songs/")

def main():
    parser = argparse.ArgumentParser(
        description="Build track from half_1/ and half_2/ with automatic A_/B_ prefixing"
    )
    parser.add_argument(
        '--track',
        type=int,
        required=True,
        help='Track number to build'
    )
    parser.add_argument(
        '--duration',
        default='3',
        help='Duration in hours (1, 2, 3) or "test" for 5 minutes'
    )
    parser.add_argument(
        '--keep-temp',
        action='store_true',
        help='Keep temporary prefixed songs folder (for debugging)'
    )

    args = parser.parse_args()

    track_folder = TRACKS_DIR / str(args.track)

    # Validate track exists
    if not track_folder.exists():
        print(f"❌ Error: Track {args.track} does not exist")
        print(f"   Create it first: python3 agent/create_track_template.py")
        return

    # Get songs from half folders
    half_1_folder = track_folder / "half_1"
    half_2_folder = track_folder / "half_2"

    half_1_songs = get_songs_from_half(half_1_folder)
    half_2_songs = get_songs_from_half(half_2_folder)

    if not half_1_songs and not half_2_songs:
        print(f"❌ Error: No songs found in half_1/ or half_2/")
        print(f"   Add songs to:")
        print(f"   - {half_1_folder}")
        print(f"   - {half_2_folder}")
        return

    print(f"\n🎵 Building Track {args.track}")
    print(f"   Half 1: {len(half_1_songs)} songs")
    print(f"   Half 2: {len(half_2_songs)} songs")
    print(f"   Total: {len(half_1_songs) + len(half_2_songs)} songs")

    # Create temporary prefixed songs
    temp_songs_folder, tracklist = create_temp_prefixed_songs(
        args.track,
        half_1_songs,
        half_2_songs
    )

    # Build mix
    output_folder = build_mix(args.track, args.duration)

    if output_folder:
        # Save tracklist
        save_tracklist(output_folder, args.track, tracklist, args.duration)

        print(f"\n✅ Build complete!")
        print(f"   Output: {output_folder}")

        # Cleanup temp songs unless --keep-temp
        if not args.keep_temp:
            cleanup_temp_songs(args.track)
        else:
            print(f"   ℹ️  Kept temp_songs/ folder (--keep-temp flag)")

        print(f"\n🎯 Next step: Add new songs to bank")
        print(f"   ./venv/bin/python3 agent/add_to_bank.py --track {args.track} --flow-id 04")
    else:
        print(f"\n❌ Build failed. Check errors above.")

if __name__ == "__main__":
    main()
