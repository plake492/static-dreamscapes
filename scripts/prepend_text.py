#!/usr/bin/env python3
"""
Script to prepend text to all filenames in a folder.

Usage:
    python scripts/prepend_text.py --folder ./path/to/folder --prefix "A_" [--dry-run]
"""

import argparse
import os
from pathlib import Path


def prepend_text_to_files(folder: str, prefix: str, dry_run: bool = False):
    """
    Prepend text to all filenames in a folder.

    Args:
        folder: Path to the folder containing files
        prefix: Text to prepend to each filename
        dry_run: If True, only show what would be renamed without actually renaming
    """
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"Error: Folder '{folder}' does not exist")
        return

    if not folder_path.is_dir():
        print(f"Error: '{folder}' is not a directory")
        return

    # Get all files (not directories) in the folder
    files = [f for f in folder_path.iterdir() if f.is_file() and not f.name.startswith('.')]

    if not files:
        print(f"No files found in '{folder}'")
        return

    print(f"{'[DRY RUN] ' if dry_run else ''}Prepending '{prefix}' to {len(files)} file(s) in '{folder}':\n")

    renamed_count = 0
    skipped_count = 0

    for file_path in sorted(files):
        old_name = file_path.name
        new_name = f"{prefix}{old_name}"
        new_path = file_path.parent / new_name

        # Check if target file already exists
        if new_path.exists():
            print(f"  ⚠️  SKIP: '{old_name}' -> '{new_name}' (target already exists)")
            skipped_count += 1
            continue

        print(f"  {'✓' if not dry_run else '→'} '{old_name}' -> '{new_name}'")

        if not dry_run:
            try:
                file_path.rename(new_path)
                renamed_count += 1
            except Exception as e:
                print(f"    ❌ Error renaming '{old_name}': {e}")
        else:
            renamed_count += 1

    print(f"\n{'[DRY RUN] Would rename' if dry_run else 'Renamed'} {renamed_count} file(s)")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} file(s) (target already exists)")

    if dry_run:
        print("\nRun without --dry-run to actually rename the files")


def main():
    parser = argparse.ArgumentParser(
        description="Prepend text to all filenames in a folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/prepend_text.py --folder ./Tracks/123456/Songs --prefix "A_"
  python scripts/prepend_text.py --folder ./Songs --prefix "B_" --dry-run
        """
    )

    parser.add_argument(
        "--folder",
        "-f",
        required=True,
        help="Path to the folder containing files to rename"
    )

    parser.add_argument(
        "--prefix",
        "-p",
        required=True,
        help="Text to prepend to each filename"
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )

    args = parser.parse_args()

    prepend_text_to_files(args.folder, args.prefix, args.dry_run)


if __name__ == "__main__":
    main()
