#!/usr/bin/env python3
"""Update file paths in the database after moving the project."""

import sqlite3
import sys
from pathlib import Path


def update_file_paths(db_path: str, old_base: str, new_base: str):
    """Update all file paths in the database.

    Args:
        db_path: Path to the SQLite database
        old_base: Old base path (e.g., '/Users/patricklake/Desktop/static-dreamwaves')
        new_base: New base path (e.g., '/Users/patricklake/Dev/static-dreamwaves')
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all songs with file paths
    cursor.execute("SELECT id, filename, file_path FROM songs")
    songs = cursor.fetchall()

    updated_count = 0
    not_found_count = 0

    print(f"\nUpdating file paths in database...")
    print(f"Old base: {old_base}")
    print(f"New base: {new_base}\n")

    for song_id, filename, old_path in songs:
        if old_path and old_path.startswith(old_base):
            # Replace old base with new base
            new_path = old_path.replace(old_base, new_base, 1)

            # Verify the new path exists
            if Path(new_path).exists():
                cursor.execute(
                    "UPDATE songs SET file_path = ? WHERE id = ?",
                    (new_path, song_id)
                )
                updated_count += 1
                print(f"✓ Updated: {filename}")
            else:
                print(f"⚠️  File not found at new location: {new_path}")
                not_found_count += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Updated: {updated_count} songs")
    print(f"  Not found: {not_found_count} songs")
    print(f"{'='*60}\n")

    if not_found_count > 0:
        print("⚠️  Some files were not found at the new location.")
        print("   Make sure all Tracks folders were moved correctly.\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update file paths in database")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    parser.add_argument("--old-base", help="Old base path (default: auto-detect)")
    parser.add_argument("--new-base", help="New base path (default: current directory)")
    args = parser.parse_args()

    # Automatic detection
    db_path = "./data/tracks.db"
    old_base = args.old_base or "/Users/patricklake/Desktop/static-dreamwaves"
    new_base = args.new_base or str(Path.cwd().absolute())

    print("File Path Updater")
    print("="*60)
    print(f"Database: {db_path}")
    print(f"Old base: {old_base}")
    print(f"New base: {new_base}")
    print("="*60)

    if not args.yes:
        response = input("\nProceed with update? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    update_file_paths(db_path, old_base, new_base)
