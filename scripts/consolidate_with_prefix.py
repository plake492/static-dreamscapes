#!/usr/bin/env python3
"""
Script to consolidate songs from Tracks/*/1 and Tracks/*/2 into Tracks/*/Songs with prefixes.

- Files from Tracks/*/1 → prepend A_ → MOVE to Tracks/*/Songs (deletes originals)
- Files from Tracks/*/2 → prepend B_ → MOVE to Tracks/*/Songs (deletes originals)

Default behavior: MOVES files (deletes from 1/ and 2/ after prefixing)
Use --copy flag to keep originals in 1/ and 2/ folders.

This is useful for organizing pre-render audio files into the main Songs folder
with proper prefixes for identification.

Usage:
    python scripts/consolidate_with_prefix.py [--dry-run] [--track N] [--copy]
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


def find_track_folders(base_dir: Path, track_number: int = None) -> List[Path]:
    """Find all track folders in the base directory.

    Args:
        base_dir: Base directory containing track folders
        track_number: Optional specific track number to process

    Returns:
        List of track folder paths
    """
    if track_number is not None:
        track_path = base_dir / str(track_number)
        if track_path.exists() and track_path.is_dir():
            return [track_path]
        else:
            console.print(f"[yellow]Warning: Track folder '{track_number}' not found[/yellow]")
            return []

    # Find all numeric directories (track folders)
    track_folders = []
    for item in base_dir.iterdir():
        if item.is_dir() and item.name.isdigit():
            track_folders.append(item)

    return sorted(track_folders, key=lambda x: int(x.name))


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


def consolidate_with_prefix(
    base_dir: str,
    dry_run: bool = False,
    track_number: int = None,
    move: bool = True
) -> Tuple[int, int, int]:
    """Consolidate songs from numbered subdirectories with prefixes.

    Args:
        base_dir: Base directory containing track folders
        dry_run: If True, only show what would be processed
        track_number: Optional specific track number to process
        move: If True, move files instead of copying

    Returns:
        Tuple of (total_processed, total_skipped, total_errors)
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        console.print(f"[red]Error: Base directory '{base_dir}' does not exist[/red]")
        return 0, 0, 0

    if not base_path.is_dir():
        console.print(f"[red]Error: '{base_dir}' is not a directory[/red]")
        return 0, 0, 0

    # Find all track folders
    track_folders = find_track_folders(base_path, track_number)

    if not track_folders:
        console.print(f"[yellow]No track folders found in '{base_dir}'[/yellow]")
        return 0, 0, 0

    action = "move" if move else "copy"
    console.print(f"\n[bold blue]📦 Consolidate Songs with Prefix[/bold blue]\n")
    console.print(f"Base directory: {base_dir}")
    console.print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'} ({action})")
    console.print(f"Tracks to process: {len(track_folders)}\n")

    total_processed = 0
    total_skipped = 0
    total_errors = 0

    # Process each track
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:

        task = progress.add_task(
            "[cyan]Processing tracks...",
            total=len(track_folders)
        )

        for track_folder in track_folders:
            track_name = track_folder.name
            songs_dir = track_folder / "Songs"

            progress.update(
                task,
                description=f"[cyan]Processing Track {track_name}..."
            )

            # Ensure Songs directory exists
            if not songs_dir.exists():
                if not dry_run:
                    songs_dir.mkdir(parents=True, exist_ok=True)

            # Define subdirectories and their prefixes
            subdirs_config = [
                (track_folder / "1", "A_"),
                (track_folder / "2", "B_")
            ]

            track_processed = 0
            track_skipped = 0
            track_errors = 0

            for subdir, prefix in subdirs_config:
                if not subdir.exists():
                    continue

                audio_files = get_audio_files(subdir)

                if not audio_files:
                    continue

                for source_file in audio_files:
                    # Check if filename already has the prefix
                    if source_file.name.startswith(prefix):
                        dest_filename = source_file.name
                    else:
                        dest_filename = f"{prefix}{source_file.name}"

                    dest_file = songs_dir / dest_filename

                    # Check if file already exists in destination
                    if dest_file.exists():
                        console.print(
                            f"  [yellow]⏭️  Track {track_name}: "
                            f"Skip {dest_filename} (already exists)[/yellow]"
                        )
                        track_skipped += 1
                        continue

                    # Display action
                    symbol = "→" if dry_run else ("📦" if move else "📋")
                    console.print(
                        f"  [green]{symbol} Track {track_name}: "
                        f"{subdir.name}/{source_file.name} → Songs/{dest_filename}[/green]"
                    )

                    if not dry_run:
                        try:
                            if move:
                                shutil.move(str(source_file), str(dest_file))
                            else:
                                shutil.copy2(source_file, dest_file)
                            track_processed += 1
                        except Exception as e:
                            console.print(
                                f"  [red]❌ Error processing '{source_file.name}': {e}[/red]"
                            )
                            track_errors += 1
                    else:
                        track_processed += 1

            total_processed += track_processed
            total_skipped += track_skipped
            total_errors += track_errors

            progress.advance(task)

    # Summary
    console.print(f"\n[bold blue]📊 Summary[/bold blue]\n")

    summary = Table()
    summary.add_column("Metric", style="cyan")
    summary.add_column("Count", style="green", justify="right")

    summary.add_row("Tracks Processed", str(len(track_folders)))
    summary.add_row(
        f"Files {'Would Be ' if dry_run else ''}{action.capitalize()}d",
        str(total_processed)
    )
    summary.add_row("Files Skipped", str(total_skipped))
    if total_errors > 0:
        summary.add_row("Errors", str(total_errors))

    console.print(summary)
    console.print()

    if dry_run and total_processed > 0:
        console.print(
            "[bold yellow]💡 This was a dry run. "
            "Run without --dry-run to actually process files[/bold yellow]\n"
        )
    elif total_processed == 0 and total_skipped == 0:
        console.print("[yellow]No files found to process[/yellow]\n")
    elif not dry_run:
        console.print(f"[bold green]✅ Successfully {action}ed {total_processed} files![/bold green]\n")

    return total_processed, total_skipped, total_errors


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate songs from Tracks/*/1 and Tracks/*/2 into Tracks/*/Songs with prefixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would happen (recommended first step)
  python scripts/consolidate_with_prefix.py --dry-run

  # Move files from subdirectories with prefixes (default - deletes originals)
  python scripts/consolidate_with_prefix.py

  # Copy files instead of moving (keeps originals in 1/ and 2/)
  python scripts/consolidate_with_prefix.py --copy

  # Process only Track 24
  python scripts/consolidate_with_prefix.py --track 24

  # Process specific track with dry run
  python scripts/consolidate_with_prefix.py --track 24 --dry-run

What it does:
  - Files from Tracks/*/1/ → prepend A_ → move to Tracks/*/Songs/
  - Files from Tracks/*/2/ → prepend B_ → move to Tracks/*/Songs/
  - Deletes original files from 1/ and 2/ by default (use --copy to keep them)
  - Skips files that already exist in Songs/
        """
    )

    parser.add_argument(
        "--base-dir",
        "-b",
        default="./Tracks",
        help="Base directory containing track folders (default: ./Tracks)"
    )

    parser.add_argument(
        "--track",
        "-t",
        type=int,
        help="Optional: Process only a specific track number"
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Preview what would be processed without actually processing files"
    )

    parser.add_argument(
        "--copy",
        "-c",
        action="store_true",
        help="Copy files instead of moving (keeps originals in 1/ and 2/)"
    )

    args = parser.parse_args()

    consolidate_with_prefix(
        args.base_dir,
        args.dry_run,
        args.track,
        not args.copy  # Invert: --copy flag means move=False
    )


if __name__ == "__main__":
    main()
