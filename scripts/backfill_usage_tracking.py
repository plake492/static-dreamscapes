#!/usr/bin/env python3
"""
Backfill usage tracking data by scanning existing track folders.

Scans /Tracks/*/Songs/ directories and updates database with:
- times_used (incremented for each track the song appears in)
- last_used_track_id (most recent track number)
- last_used_at (timestamp of last usage)

Assumes every song in a track's Songs folder has been used for that track's rendered video.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from dotenv import load_dotenv

from src.core.database import Database
from src.core.config import get_config

console = Console()
load_dotenv()


def get_track_folders(base_dir: Path) -> List[Tuple[int, Path]]:
    """Get all track folders in /Tracks/ directory.

    Returns:
        List of (track_number, path) tuples, sorted by track number
    """
    tracks = []

    if not base_dir.exists():
        console.print(f"[yellow]Warning: Tracks directory not found: {base_dir}[/yellow]")
        return tracks

    for item in base_dir.iterdir():
        if item.is_dir() and item.name.isdigit():
            track_num = int(item.name)
            tracks.append((track_num, item))

    return sorted(tracks, key=lambda x: x[0])


def get_songs_in_track(track_dir: Path) -> List[str]:
    """Get all song filenames in a track's Songs directory.

    Args:
        track_dir: Path to track directory (e.g., /Tracks/24/)

    Returns:
        List of song filenames (e.g., ['A_1_1_24a.mp3', ...])
    """
    songs_dir = track_dir / "Songs"
    if not songs_dir.exists():
        return []

    songs = []
    for file in songs_dir.iterdir():
        if file.is_file() and file.suffix.lower() in ['.mp3', '.wav', '.flac']:
            songs.append(file.name)

    return sorted(songs)


def get_track_timestamp(track_dir: Path) -> datetime:
    """Get creation timestamp for a track folder.

    Uses the folder's creation time or current time if not available.
    """
    try:
        # Get folder creation time
        stat = track_dir.stat()
        return datetime.fromtimestamp(stat.st_ctime)
    except Exception:
        # Fallback to current time
        return datetime.now()


def backfill_usage_data(
    db: Database,
    base_dir: Path,
    specific_tracks: Optional[List[int]] = None,
    dry_run: bool = False
) -> Dict[str, any]:
    """Backfill usage tracking data from existing track folders.

    Args:
        db: Database instance
        base_dir: Path to Tracks directory
        specific_tracks: Optional list of track numbers to process (None = all)
        dry_run: If True, don't actually update database

    Returns:
        Statistics dictionary
    """
    stats = {
        'tracks_scanned': 0,
        'songs_found': 0,
        'songs_matched': 0,
        'songs_not_found': 0,
        'updates': {},  # track_num -> list of (filename, found_in_db)
    }

    # Get all track folders
    all_tracks = get_track_folders(base_dir)

    # Filter if specific tracks requested
    if specific_tracks:
        all_tracks = [(num, path) for num, path in all_tracks if num in specific_tracks]

    if not all_tracks:
        console.print("[yellow]No track folders found to process[/yellow]\n")
        return stats

    console.print(f"\n[bold blue]📂 Found {len(all_tracks)} track folder(s) to scan[/bold blue]\n")

    # Process each track
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Scanning tracks...", total=len(all_tracks))

        for track_num, track_dir in all_tracks:
            progress.update(task, description=f"[cyan]Scanning Track {track_num}...")

            # Get songs in this track
            song_files = get_songs_in_track(track_dir)
            stats['tracks_scanned'] += 1
            stats['songs_found'] += len(song_files)
            stats['updates'][track_num] = []

            if not song_files:
                progress.advance(task)
                continue

            # Get timestamp for this track
            track_timestamp = get_track_timestamp(track_dir)

            # Process each song
            for filename in song_files:
                # Find song in database
                song = db.get_song_by_filename(filename)

                if song:
                    stats['songs_matched'] += 1
                    stats['updates'][track_num].append((filename, True))

                    if not dry_run:
                        # Update usage tracking
                        db.update_song_usage_on_prepare(
                            song_id=song.id,
                            track_id=str(track_num),
                            timestamp=track_timestamp
                        )
                else:
                    stats['songs_not_found'] += 1
                    stats['updates'][track_num].append((filename, False))

            progress.advance(task)

    return stats


def print_statistics(stats: Dict[str, any], dry_run: bool):
    """Print backfill statistics in a nice table."""

    console.print(f"\n[bold blue]📊 Backfill Statistics[/bold blue]\n")

    # Summary table
    summary = Table(title="Summary")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Count", style="green", justify="right")

    summary.add_row("Tracks Scanned", str(stats['tracks_scanned']))
    summary.add_row("Song Files Found", str(stats['songs_found']))
    summary.add_row("Songs Matched in DB", str(stats['songs_matched']))
    summary.add_row("Songs Not Found in DB", str(stats['songs_not_found']))

    if stats['songs_found'] > 0:
        match_rate = (stats['songs_matched'] / stats['songs_found']) * 100
        summary.add_row("Match Rate", f"{match_rate:.1f}%")

    console.print(summary)
    console.print()

    # Per-track breakdown if there are unmatched songs
    if stats['songs_not_found'] > 0:
        console.print("[bold yellow]⚠️  Songs Not Found in Database:[/bold yellow]\n")

        for track_num, updates in sorted(stats['updates'].items()):
            not_found = [filename for filename, found in updates if not found]
            if not_found:
                console.print(f"  [bold]Track {track_num}:[/bold]")
                for filename in not_found:
                    console.print(f"    [red]✗[/red] {filename}")
                console.print()

    # Mode indicator
    if dry_run:
        console.print("[bold yellow]📋 DRY RUN MODE - No changes were made to the database[/bold yellow]\n")
    else:
        console.print("[bold green]✅ Database updated successfully![/bold green]\n")

    # Next steps
    if not dry_run and stats['songs_matched'] > 0:
        console.print("[bold blue]🔍 Verify Results:[/bold blue]")
        console.print("  Run: [cyan]yarn stats[/cyan] to see updated usage counts\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Backfill usage tracking data from existing track folders"
    )
    parser.add_argument(
        "--tracks-dir",
        default="./Tracks",
        help="Path to Tracks directory (default: ./Tracks)"
    )
    parser.add_argument(
        "--db-path",
        default="./data/tracks.db",
        help="Path to database file (default: ./data/tracks.db)"
    )
    parser.add_argument(
        "--tracks",
        type=str,
        help="Comma-separated list of specific track numbers to process (e.g., '24,25,26')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database"
    )

    args = parser.parse_args()

    # Parse specific tracks if provided
    specific_tracks = None
    if args.tracks:
        try:
            specific_tracks = [int(t.strip()) for t in args.tracks.split(',')]
            console.print(f"[dim]Processing specific tracks: {specific_tracks}[/dim]\n")
        except ValueError:
            console.print("[bold red]Error: Invalid track numbers. Use format: --tracks '24,25,26'[/bold red]\n")
            sys.exit(1)

    # Setup
    base_dir = Path(args.tracks_dir)
    if not base_dir.exists():
        console.print(f"[bold red]Error: Tracks directory not found: {base_dir}[/bold red]\n")
        sys.exit(1)

    try:
        config = get_config("./config/settings.yaml")
        db = Database(config.database_path)
    except Exception as e:
        console.print(f"[bold red]Error: Failed to connect to database: {e}[/bold red]\n")
        sys.exit(1)

    # Run backfill
    console.print(f"\n[bold blue]🔄 Backfill Usage Tracking Data[/bold blue]")
    console.print(f"Tracks Directory: {base_dir}")
    console.print(f"Database: {config.database_path}")
    console.print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}\n")

    try:
        stats = backfill_usage_data(
            db=db,
            base_dir=base_dir,
            specific_tracks=specific_tracks,
            dry_run=args.dry_run
        )

        print_statistics(stats, args.dry_run)

    except Exception as e:
        console.print(f"\n[bold red]❌ Error during backfill: {e}[/bold red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)
