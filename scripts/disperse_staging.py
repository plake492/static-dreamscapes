#!/usr/bin/env python3
"""
Disperse staged audio files into folders 1 and 2.

Scans Tracks/{number}/Staging/ for formatted audio files and distributes
them evenly between folders 1/ and 2/ based on prompt number groupings.

Usage:
    python scripts/disperse_staging.py --track 31 [--dry-run]
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import sys
from collections import defaultdict

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingest.filename_parser import FilenameParser


class StagingDisperser:
    """Disperse files from Staging/ into folders 1/ and 2/."""

    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac']

    def __init__(self, track_number: int, dry_run: bool = False):
        self.track_number = track_number
        self.dry_run = dry_run
        self.track_dir = Path(f"./Tracks/{track_number}")
        self.staging_dir = self.track_dir / "Staging"
        self.folder_1 = self.track_dir / "1"
        self.folder_2 = self.track_dir / "2"
        self.parser = FilenameParser()

    def process(self):
        """Main processing workflow."""
        # 1. Validate directories
        self._validate_directories()

        # 2. Find all formatted audio files in Staging/
        formatted_files = self._find_formatted_files()

        if not formatted_files:
            print(f"No formatted audio files found in {self.staging_dir}")
            return

        print(f"Found {len(formatted_files)} formatted file(s) in Staging/")

        # 3. Group files by (arc, prompt)
        grouped_files = self._group_by_prompt(formatted_files)

        print(f"Grouped into {len(grouped_files)} prompt(s)\n")

        # 4. Generate dispersion plan
        dispersion_plan = self._generate_dispersion_plan(grouped_files)

        # 5. Display plan
        self._display_plan(dispersion_plan, grouped_files)

        # 6. Execute (or dry-run)
        if self.dry_run:
            print("\n[DRY RUN] No files were moved.")
        else:
            confirm = input("\nProceed with dispersion? [y/N]: ")
            if confirm.lower() == 'y':
                self._execute_dispersion(dispersion_plan)
                print(f"\n✅ Successfully dispersed {len(formatted_files)} file(s)")
            else:
                print("Cancelled.")

    def _validate_directories(self):
        """Ensure required directories exist."""
        if not self.track_dir.exists():
            raise FileNotFoundError(f"Track directory not found: {self.track_dir}")

        if not self.staging_dir.exists():
            raise FileNotFoundError(
                f"Staging directory not found: {self.staging_dir}\n"
                f"Create it with: mkdir -p {self.staging_dir}"
            )

        # Create folders 1/ and 2/ if they don't exist
        for folder in [self.folder_1, self.folder_2]:
            if not folder.exists():
                print(f"Creating directory: {folder}")
                folder.mkdir(parents=True, exist_ok=True)

    def _find_formatted_files(self) -> List[Path]:
        """Find all formatted audio files in Staging/ directory."""
        formatted = []

        for ext in self.AUDIO_EXTENSIONS:
            for file_path in self.staging_dir.glob(f"*{ext}"):
                # Only include properly formatted files
                if self.parser.is_valid_filename(file_path.name):
                    formatted.append(file_path)

        return sorted(formatted)

    def _group_by_prompt(self, files: List[Path]) -> Dict[Tuple[int, int], List[Path]]:
        """
        Group files by (arc_number, prompt_number).

        Returns:
            Dictionary mapping (arc, prompt) -> list of file paths
        """
        groups = defaultdict(list)

        for file_path in files:
            components = self.parser.parse(file_path.name)
            if components:
                key = (components.arc_number, components.prompt_number)
                groups[key].append(file_path)

        # Sort files within each group by order_marker (a, b, c, ...)
        for key in groups:
            groups[key] = sorted(
                groups[key],
                key=lambda p: self.parser.parse(p.name).order_marker
            )

        return dict(groups)

    def _generate_dispersion_plan(
        self, grouped_files: Dict[Tuple[int, int], List[Path]]
    ) -> Dict[Path, Path]:
        """
        Generate dispersion plan: source_path -> destination_path.

        For each prompt group, split files evenly:
        - First half (rounded up if odd) → folder 1/
        - Second half → folder 2/
        """
        plan = {}

        for (arc, prompt), files in grouped_files.items():
            count = len(files)
            # If odd count, folder 1 gets the extra
            split_point = (count + 1) // 2

            # First half to folder 1
            for file_path in files[:split_point]:
                plan[file_path] = self.folder_1 / file_path.name

            # Second half to folder 2
            for file_path in files[split_point:]:
                plan[file_path] = self.folder_2 / file_path.name

        return plan

    def _display_plan(
        self,
        plan: Dict[Path, Path],
        grouped_files: Dict[Tuple[int, int], List[Path]]
    ):
        """Display the dispersion plan grouped by prompt."""
        print("Dispersion Plan:")
        print("=" * 70)

        # Group plan by (arc, prompt) for better display
        for (arc, prompt), files in sorted(grouped_files.items()):
            count = len(files)
            split_point = (count + 1) // 2
            folder_1_count = split_point
            folder_2_count = count - split_point

            print(f"\nPrompt {arc}_{prompt} ({count} files):")
            print(f"  → Folder 1: {folder_1_count} file(s)")
            print(f"  → Folder 2: {folder_2_count} file(s)")

            for file_path in files:
                dest = plan[file_path]
                folder_num = "1" if dest.parent.name == "1" else "2"
                print(f"    {file_path.name:<30} → {folder_num}/")

        print("=" * 70)

    def _execute_dispersion(self, plan: Dict[Path, Path]):
        """Execute the file dispersion."""
        for source_path, dest_path in plan.items():
            # Check for collisions
            if dest_path.exists():
                print(f"⚠️  WARNING: {dest_path} already exists, skipping {source_path.name}")
                continue

            # Move file
            shutil.move(str(source_path), str(dest_path))
            folder_num = dest_path.parent.name
            print(f"✓ Moved: {source_path.name} → {folder_num}/")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Disperse staged audio files into folders 1 and 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview dispersion for track 31
  python scripts/disperse_staging.py --track 31 --dry-run

  # Actually disperse files
  python scripts/disperse_staging.py --track 31
        """
    )

    parser.add_argument(
        "--track", "-t",
        type=int,
        required=True,
        help="Track number"
    )

    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview without moving files"
    )

    args = parser.parse_args()

    try:
        disperser = StagingDisperser(args.track, dry_run=args.dry_run)
        disperser.process()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
