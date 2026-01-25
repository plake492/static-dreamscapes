#!/usr/bin/env python3
"""
Reset a track by clearing songs and files.

Removes songs from database and deletes files from track folders.
Useful for test tracks or starting over.

Usage:
    python scripts/reset_track.py --track 9999 [--dry-run]
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple
import sys
import sqlite3

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TrackResetter:
    """Reset a track by clearing database and files."""

    def __init__(self, track_number: int, dry_run: bool = False):
        self.track_number = track_number
        self.dry_run = dry_run
        self.track_dir = Path(f"./Tracks/{track_number}")
        self.rendered_dir = Path(f"./Rendered/{track_number}")
        self.db_path = Path("./data/tracks.db")

    def process(self):
        """Main reset workflow."""
        print(f"🔄 Resetting Track {self.track_number}")
        print("=" * 70)

        # 1. Check what exists
        stats = self._analyze_track()

        if not stats['has_anything']:
            print(f"\n✅ Track {self.track_number} is already clean (nothing to reset)")
            return

        # 2. Display what will be deleted
        self._display_reset_plan(stats)

        # 3. Confirm or dry-run
        if self.dry_run:
            print("\n[DRY RUN] No files or database entries were deleted.")
            return

        print("\n⚠️  WARNING: This action cannot be undone!")
        confirm = input(f"Reset track {self.track_number}? [y/N]: ")

        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        # 4. Execute reset
        self._execute_reset(stats)
        print(f"\n✅ Track {self.track_number} has been reset")

    def _analyze_track(self) -> dict:
        """Analyze what exists for this track."""
        stats = {
            'db_songs': 0,
            'files': {
                'Songs': [],
                'Staging': [],
                '1': [],
                '2': [],
                'Rendered': []
            },
            'has_anything': False
        }

        # Check database
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Count songs with this track number in filename
                cursor.execute("""
                    SELECT COUNT(*) FROM songs
                    WHERE filename LIKE ?
                """, (f'%_{self.track_number}%',))

                stats['db_songs'] = cursor.fetchone()[0]
                conn.close()
            except Exception as e:
                print(f"⚠️  Warning: Could not check database: {e}")

        # Check files
        for folder_name in ['Songs', 'Staging', '1', '2']:
            folder = self.track_dir / folder_name
            if folder.exists():
                files = list(folder.glob('*.mp3')) + list(folder.glob('*.wav')) + \
                        list(folder.glob('*.m4a')) + list(folder.glob('*.flac'))
                stats['files'][folder_name] = files

        # Check renders
        if self.rendered_dir.exists():
            # Count subdirectories (each render session is a folder)
            render_sessions = [d for d in self.rendered_dir.iterdir() if d.is_dir()]
            stats['files']['Rendered'] = render_sessions

        # Check if anything exists
        stats['has_anything'] = (
            stats['db_songs'] > 0 or
            any(len(files) > 0 for files in stats['files'].values())
        )

        return stats

    def _display_reset_plan(self, stats: dict):
        """Display what will be deleted."""
        print("\nReset Plan:")
        print("=" * 70)

        # Database
        if stats['db_songs'] > 0:
            print(f"\n📊 Database:")
            print(f"   {stats['db_songs']} song(s) will be removed from database")

        # Files
        has_files = False
        for folder_name, files in stats['files'].items():
            if files:
                has_files = True
                if folder_name == 'Rendered':
                    print(f"\n📁 {self.rendered_dir}/")
                    print(f"   {len(files)} render session(s) will be deleted")
                    for session in files[:3]:  # Show first 3
                        print(f"      • {session.name}/")
                    if len(files) > 3:
                        print(f"      • ... and {len(files) - 3} more")
                else:
                    print(f"\n📁 {self.track_dir}/{folder_name}/")
                    print(f"   {len(files)} file(s) will be deleted")
                    for file_path in files[:5]:  # Show first 5
                        print(f"      • {file_path.name}")
                    if len(files) > 5:
                        print(f"      • ... and {len(files) - 5} more")

        if not has_files and stats['db_songs'] == 0:
            print("\n(Nothing to delete)")

        print("=" * 70)

    def _execute_reset(self, stats: dict):
        """Execute the reset operations."""

        # 1. Remove from database
        if stats['db_songs'] > 0:
            self._remove_from_database()
            print(f"✓ Removed {stats['db_songs']} song(s) from database")

        # 2. Delete files
        file_count = 0

        for folder_name in ['Songs', 'Staging', '1', '2']:
            files = stats['files'][folder_name]
            if files:
                for file_path in files:
                    file_path.unlink()
                    file_count += 1
                print(f"✓ Deleted {len(files)} file(s) from {folder_name}/")

        # 3. Delete render sessions
        render_sessions = stats['files']['Rendered']
        if render_sessions:
            for session_dir in render_sessions:
                shutil.rmtree(session_dir)
            print(f"✓ Deleted {len(render_sessions)} render session(s)")

        # 4. Optionally remove empty Rendered directory
        if self.rendered_dir.exists() and not any(self.rendered_dir.iterdir()):
            self.rendered_dir.rmdir()
            print(f"✓ Removed empty Rendered/{self.track_number}/ directory")

    def _remove_from_database(self):
        """Remove songs from database that belong to this track."""
        if not self.db_path.exists():
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Delete songs where filename contains track number
            # Pattern: anything with _{track_number}{letter}. (e.g., _9999a., _9999b.)
            cursor.execute("""
                DELETE FROM songs
                WHERE filename LIKE ?
            """, (f'%_{self.track_number}%',))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Error removing from database: {e}")
            raise


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Reset a track by clearing database and files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will be deleted
  python scripts/reset_track.py --track 9999 --dry-run

  # Actually reset the track
  python scripts/reset_track.py --track 9999

What gets deleted:
  • Songs from database (where filename contains track number)
  • Files from Tracks/{N}/Songs/
  • Files from Tracks/{N}/Staging/
  • Files from Tracks/{N}/1/
  • Files from Tracks/{N}/2/
  • All render sessions from Rendered/{N}/

What is preserved:
  • Track folder structure (Tracks/{N}/)
  • Metadata files (track_info.json, etc.)
  • Video and Image folders
  • README.md and other docs
        """
    )

    parser.add_argument(
        "--track", "-t",
        type=int,
        required=True,
        help="Track number to reset"
    )

    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview without deleting anything"
    )

    args = parser.parse_args()

    try:
        resetter = TrackResetter(args.track, dry_run=args.dry_run)
        resetter.process()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
