#!/usr/bin/env python3
"""
Script to remove a matching prefix from all filenames in a folder.

Usage:
    python scripts/remove_prefix.py --folder ./path/to/folder --prefix "A_" [--dry-run]
"""

import argparse
import os
from pathlib import Path


def remove_prefix_from_files(folder: str, prefix: str, dry_run: bool = False):
    """
    Remove a matching prefix from all filenames in a folder.

    Args:
        folder: Path to the folder containing files
        prefix: Prefix text to remove from each filename
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

    # Filter files that actually have the prefix
    files_with_prefix = [f for f in files if f.name.startswith(prefix)]

    if not files_with_prefix:
        print(f"No files found with prefix '{prefix}' in '{folder}'")
        return

    print(f"{'[DRY RUN] ' if dry_run else ''}Removing prefix '{prefix}' from {len(files_with_prefix)} file(s) in '{folder}':\n")

    renamed_count = 0
    skipped_count = 0

    for file_path in sorted(files_with_prefix):
        old_name = file_path.name
        new_name = old_name[len(prefix):]  # Remove prefix
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

    # Show files without the prefix (if any)
    files_without_prefix = [f for f in files if not f.name.startswith(prefix)]
    if files_without_prefix:
        print(f"\nNote: {len(files_without_prefix)} file(s) in folder don't have the prefix '{prefix}' and were not affected")


def main():
    parser = argparse.ArgumentParser(
        description="Remove a matching prefix from all filenames in a folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/remove_prefix.py --folder ./Tracks/123456/Songs --prefix "A_"
  python scripts/remove_prefix.py --folder ./Songs --prefix "B_" --dry-run
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
        help="Prefix text to remove from each filename"
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be renamed without actually renaming files"
    )

    args = parser.parse_args()

    remove_prefix_from_files(args.folder, args.prefix, args.dry_run)


if __name__ == "__main__":
    main()
