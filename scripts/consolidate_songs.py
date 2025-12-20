#!/usr/bin/env python3
"""
Script to copy song files from Tracks/*/1 and Tracks/*/2 into Tracks/*/Songs.

This consolidates songs from numbered subdirectories into the main Songs folder
for each track.

Usage:
    python scripts/consolidate_songs.py --base-dir ./Tracks [--dry-run] [--track-id 123456]
"""

import argparse
import shutil
from pathlib import Path
from typing import List


def find_track_folders(base_dir: Path, track_id: str = None) -> List[Path]:
    """
    Find all track folders in the base directory.

    Args:
        base_dir: Base directory containing track folders
        track_id: Optional specific track ID to process

    Returns:
        List of track folder paths
    """
    if track_id:
        track_path = base_dir / track_id
        if track_path.exists() and track_path.is_dir():
            return [track_path]
        else:
            print(f"Warning: Track folder '{track_id}' not found")
            return []

    # Find all numeric directories (track folders)
    track_folders = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.isdigit():
            track_folders.append(item)

    return sorted(track_folders)


def get_audio_files(directory: Path) -> List[Path]:
    """Get all audio files from a directory."""
    audio_extensions = ['.mp3', '.wav', '.m4a', '.flac']
    audio_files = []

    if not directory.exists():
        return []

    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            audio_files.append(file_path)

    return sorted(audio_files)


def consolidate_songs(base_dir: str, dry_run: bool = False, track_id: str = None):
    """
    Copy songs from Tracks/*/1 and Tracks/*/2 into Tracks/*/Songs.

    Args:
        base_dir: Base directory containing track folders
        dry_run: If True, only show what would be copied
        track_id: Optional specific track ID to process
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"Error: Base directory '{base_dir}' does not exist")
        return

    if not base_path.is_dir():
        print(f"Error: '{base_dir}' is not a directory")
        return

    # Find all track folders
    track_folders = find_track_folders(base_path, track_id)

    if not track_folders:
        print(f"No track folders found in '{base_dir}'")
        return

    print(f"{'[DRY RUN] ' if dry_run else ''}Processing {len(track_folders)} track folder(s)...\n")

    total_copied = 0
    total_skipped = 0

    for track_folder in track_folders:
        track_name = track_folder.name
        songs_dir = track_folder / "Songs"

        # Ensure Songs directory exists
        if not songs_dir.exists():
            print(f"  Creating Songs directory for track {track_name}")
            if not dry_run:
                songs_dir.mkdir(parents=True, exist_ok=True)

        # Check subdirectories 1 and 2
        subdirs = [track_folder / "1", track_folder / "2"]

        track_copied = 0
        track_skipped = 0

        for subdir in subdirs:
            if not subdir.exists():
                continue

            audio_files = get_audio_files(subdir)

            if not audio_files:
                continue

            print(f"Track {track_name} - Found {len(audio_files)} file(s) in {subdir.name}/")

            for source_file in audio_files:
                dest_file = songs_dir / source_file.name

                # Check if file already exists in destination
                if dest_file.exists():
                    print(f"  ⚠️  SKIP: {source_file.name} (already exists in Songs/)")
                    track_skipped += 1
                    continue

                print(f"  {'→' if dry_run else '✓'} Copy {subdir.name}/{source_file.name} -> Songs/{source_file.name}")

                if not dry_run:
                    try:
                        shutil.copy2(source_file, dest_file)
                        track_copied += 1
                    except Exception as e:
                        print(f"    ❌ Error copying '{source_file.name}': {e}")
                else:
                    track_copied += 1

        if track_copied > 0 or track_skipped > 0:
            print(f"  Track {track_name}: {'Would copy' if dry_run else 'Copied'} {track_copied}, Skipped {track_skipped}\n")

        total_copied += track_copied
        total_skipped += track_skipped

    print(f"{'=' * 60}")
    print(f"{'[DRY RUN] Would copy' if dry_run else 'Copied'} {total_copied} file(s) total")
    if total_skipped > 0:
        print(f"Skipped {total_skipped} file(s) (already exist in destination)")

    if dry_run and total_copied > 0:
        print("\nRun without --dry-run to actually copy the files")
    elif total_copied == 0 and total_skipped == 0:
        print("\nNo files found to copy")


def main():
    parser = argparse.ArgumentParser(
        description="Copy song files from Tracks/*/1 and Tracks/*/2 into Tracks/*/Songs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview consolidation for all tracks
  python scripts/consolidate_songs.py --base-dir ./Tracks --dry-run

  # Actually consolidate all tracks
  python scripts/consolidate_songs.py --base-dir ./Tracks

  # Consolidate only a specific track
  python scripts/consolidate_songs.py --base-dir ./Tracks --track-id 123456
        """
    )

    parser.add_argument(
        "--base-dir",
        "-b",
        default="./Tracks",
        help="Base directory containing track folders (default: ./Tracks)"
    )

    parser.add_argument(
        "--track-id",
        "-t",
        help="Optional: Process only a specific track ID"
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be copied without actually copying files"
    )

    args = parser.parse_args()

    consolidate_songs(args.base_dir, args.dry_run, args.track_id)


if __name__ == "__main__":
    main()
