#!/usr/bin/env python3
"""
Script to import all tracks that have songs in their Songs folder.

This script will:
1. Find all tracks with Songs folders containing audio files
2. Look for Notion URLs in metadata or README files
3. Import each track using the import-songs command

Usage:
    python scripts/import_all_tracks.py [--dry-run]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
import re


def find_notion_url(track_path: Path) -> str:
    """Find Notion URL for a track from metadata or README."""

    # Check metadata/notion_url.txt
    notion_url_file = track_path / "metadata" / "notion_url.txt"
    if notion_url_file.exists():
        return notion_url_file.read_text().strip()

    # Check README.md
    readme = track_path / "README.md"
    if readme.exists():
        content = readme.read_text()
        # Look for Notion URL in markdown link
        match = re.search(r'https://www\.notion\.so/[^\s\)]+', content)
        if match:
            return match.group(0)

    # Check metadata/track_metadata.json
    metadata_json = track_path / "metadata" / "track_metadata.json"
    if metadata_json.exists():
        try:
            data = json.loads(metadata_json.read_text())
            if 'notion_url' in data:
                return data['notion_url']
        except:
            pass

    return None


def get_audio_file_count(songs_dir: Path) -> int:
    """Count audio files in a directory."""
    extensions = ['.mp3', '.wav', '.m4a', '.flac']
    count = 0
    for ext in extensions:
        count += len(list(songs_dir.glob(f'*{ext}')))
    return count


def import_track(track_number: str, notion_url: str, songs_dir: Path, dry_run: bool = False):
    """Import a track using the yarn import-songs command."""
    cmd = [
        'yarn', 'import-songs',
        '--notion-url', notion_url,
        '--songs-dir', str(songs_dir)
    ]

    if dry_run:
        print(f"  Would run: {' '.join(cmd)}")
        return True
    else:
        print(f"  Running import for track {track_number}...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error importing track {track_number}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Import all tracks with songs into the database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be imported without actually importing"
    )

    parser.add_argument(
        "--base-dir",
        "-b",
        default="./Tracks",
        help="Base directory containing track folders (default: ./Tracks)"
    )

    parser.add_argument(
        "--tracks",
        "-t",
        help="Comma-separated list of track numbers to import (e.g., '10,11,12'). If not provided, imports all."
    )

    args = parser.parse_args()

    base_dir = Path(args.base_dir)

    if not base_dir.exists():
        print(f"❌ Error: Base directory '{base_dir}' does not exist")
        sys.exit(1)

    # Get specific tracks or all tracks
    if args.tracks:
        track_numbers = args.tracks.split(',')
        track_dirs = [base_dir / num.strip() for num in track_numbers]
    else:
        track_dirs = sorted([d for d in base_dir.iterdir() if d.is_dir()])

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Scanning for tracks with songs...\n")

    tracks_to_import = []
    tracks_without_url = []

    for track_dir in track_dirs:
        track_number = track_dir.name
        songs_dir = track_dir / "Songs"

        # Skip if no Songs directory
        if not songs_dir.exists():
            continue

        # Count audio files
        audio_count = get_audio_file_count(songs_dir)
        if audio_count == 0:
            continue

        # Find Notion URL
        notion_url = find_notion_url(track_dir)

        if notion_url:
            tracks_to_import.append({
                'number': track_number,
                'path': track_dir,
                'songs_dir': songs_dir,
                'notion_url': notion_url,
                'song_count': audio_count
            })
            print(f"✓ Track {track_number}: {audio_count} songs, Notion URL found")
        else:
            tracks_without_url.append({
                'number': track_number,
                'song_count': audio_count
            })
            print(f"⚠️  Track {track_number}: {audio_count} songs, NO Notion URL")

    print(f"\n{'=' * 60}")
    print(f"Found {len(tracks_to_import)} track(s) ready to import")
    print(f"Found {len(tracks_without_url)} track(s) without Notion URLs")
    print(f"{'=' * 60}\n")

    if tracks_without_url:
        print("Tracks without Notion URLs (will be skipped):")
        for track in tracks_without_url:
            print(f"  - Track {track['number']}: {track['song_count']} songs")
        print()

    if not tracks_to_import:
        print("No tracks to import.")
        return

    if args.dry_run:
        print("Tracks that would be imported:")
        for track in tracks_to_import:
            print(f"\n  Track {track['number']}:")
            print(f"    Songs: {track['song_count']}")
            print(f"    Notion URL: {track['notion_url']}")
            print(f"    Songs dir: {track['songs_dir']}")
        print(f"\nRun without --dry-run to actually import these tracks\n")
        return

    # Ask for confirmation
    print(f"Ready to import {len(tracks_to_import)} track(s).")
    response = input("Continue? [y/N]: ")

    if response.lower() != 'y':
        print("Import cancelled.")
        return

    print()

    # Import each track
    success_count = 0
    failed_count = 0

    for i, track in enumerate(tracks_to_import, 1):
        print(f"\n[{i}/{len(tracks_to_import)}] Importing Track {track['number']}...")
        print(f"  Songs: {track['song_count']}")
        print(f"  Notion: {track['notion_url'][:50]}...")

        success = import_track(
            track['number'],
            track['notion_url'],
            track['songs_dir'],
            dry_run=False
        )

        if success:
            success_count += 1
            print(f"  ✅ Track {track['number']} imported successfully")
        else:
            failed_count += 1
            print(f"  ❌ Track {track['number']} import failed")

    print(f"\n{'=' * 60}")
    print(f"Import Summary:")
    print(f"  ✅ Successful: {success_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
