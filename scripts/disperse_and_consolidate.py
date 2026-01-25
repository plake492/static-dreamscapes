#!/usr/bin/env python3
"""
Disperse and consolidate in one command.

1. Disperses files from Staging/ to folders 1/ and 2/
2. Consolidates files from 1/ and 2/ to Songs/ with A_/B_ prefixes

Usage:
    python scripts/disperse_and_consolidate.py --track 31 [--dry-run]
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


class DisperseAndConsolidator:
    """Disperse from Staging/ then consolidate to Songs/ in one workflow."""

    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac']

    def __init__(self, track_number: int, dry_run: bool = False):
        self.track_number = track_number
        self.dry_run = dry_run
        self.track_dir = Path(f"./Tracks/{track_number}")
        self.staging_dir = self.track_dir / "Staging"
        self.folder_1 = self.track_dir / "1"
        self.folder_2 = self.track_dir / "2"
        self.songs_dir = self.track_dir / "Songs"
        self.parser = FilenameParser()

    def process(self):
        """Main processing workflow."""
        print(f"🔄 Disperse & Consolidate for Track {self.track_number}")
        print("=" * 70)

        # Phase 1: Disperse
        print("\n📦 Phase 1: Dispersing from Staging/ → 1/ and 2/")
        print("-" * 70)

        disperse_count = self._disperse_phase()

        if disperse_count == 0:
            print("   No files in Staging/ to disperse")

        # Phase 2: Consolidate
        print("\n📦 Phase 2: Consolidating from 1/ and 2/ → Songs/")
        print("-" * 70)

        consolidate_count = self._consolidate_phase()

        if consolidate_count == 0:
            print("   No files in 1/ or 2/ to consolidate")

        # Summary
        print("\n" + "=" * 70)
        if self.dry_run:
            print("\n[DRY RUN] No files were moved.")
        else:
            print(f"\n✅ Complete!")
            if disperse_count > 0:
                print(f"   Dispersed {disperse_count} file(s)")
            if consolidate_count > 0:
                print(f"   Consolidated {consolidate_count} file(s)")

    def _disperse_phase(self) -> int:
        """Disperse files from Staging/ to 1/ and 2/. Returns count of files moved."""
        # 1. Validate directories
        self._validate_disperse_directories()

        # 2. Find formatted files in Staging/
        formatted_files = self._find_formatted_files()

        if not formatted_files:
            return 0

        print(f"   Found {len(formatted_files)} formatted file(s) in Staging/")

        # 3. Group files by (arc, prompt)
        grouped_files = self._group_by_prompt(formatted_files)

        # 4. Generate dispersion plan
        dispersion_plan = self._generate_dispersion_plan(grouped_files)

        # 5. Display plan
        self._display_dispersion_plan(dispersion_plan, grouped_files)

        # 6. Execute (or dry-run)
        if not self.dry_run:
            self._execute_dispersion(dispersion_plan)

        return len(formatted_files)

    def _consolidate_phase(self) -> int:
        """Consolidate files from 1/ and 2/ to Songs/. Returns count of files moved."""
        # 1. Find files in 1/ and 2/
        files_1 = self._find_audio_files(self.folder_1)
        files_2 = self._find_audio_files(self.folder_2)

        total_files = len(files_1) + len(files_2)

        if total_files == 0:
            return 0

        print(f"   Found {len(files_1)} file(s) in 1/")
        print(f"   Found {len(files_2)} file(s) in 2/")

        # 2. Generate consolidation plan
        consolidation_plan = self._generate_consolidation_plan(files_1, files_2)

        # 3. Display plan
        self._display_consolidation_plan(consolidation_plan)

        # 4. Execute (or dry-run)
        if not self.dry_run:
            self._execute_consolidation(consolidation_plan)

        return total_files

    # ===== DISPERSE METHODS =====

    def _validate_disperse_directories(self):
        """Ensure required directories exist for dispersion."""
        if not self.track_dir.exists():
            raise FileNotFoundError(f"Track directory not found: {self.track_dir}")

        if not self.staging_dir.exists():
            # Staging doesn't exist, that's ok - means no files to disperse
            return

        # Create folders 1/ and 2/ if they don't exist
        for folder in [self.folder_1, self.folder_2]:
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)

    def _find_formatted_files(self) -> List[Path]:
        """Find all formatted audio files in Staging/ directory."""
        if not self.staging_dir.exists():
            return []

        formatted = []
        for ext in self.AUDIO_EXTENSIONS:
            for file_path in self.staging_dir.glob(f"*{ext}"):
                # Only include properly formatted files
                if self.parser.is_valid_filename(file_path.name):
                    formatted.append(file_path)

        return sorted(formatted)

    def _group_by_prompt(self, files: List[Path]) -> Dict[Tuple[int, int], List[Path]]:
        """Group files by (arc_number, prompt_number)."""
        groups = defaultdict(list)

        for file_path in files:
            components = self.parser.parse(file_path.name)
            if components:
                key = (components.arc_number, components.prompt_number)
                groups[key].append(file_path)

        # Sort files within each group by order_marker
        for key in groups:
            groups[key] = sorted(
                groups[key],
                key=lambda p: self.parser.parse(p.name).order_marker
            )

        return dict(groups)

    def _generate_dispersion_plan(
        self, grouped_files: Dict[Tuple[int, int], List[Path]]
    ) -> Dict[Path, Path]:
        """Generate dispersion plan: source_path -> destination_path."""
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

    def _display_dispersion_plan(
        self,
        plan: Dict[Path, Path],
        grouped_files: Dict[Tuple[int, int], List[Path]]
    ):
        """Display the dispersion plan grouped by prompt."""
        for (arc, prompt), files in sorted(grouped_files.items()):
            count = len(files)
            split_point = (count + 1) // 2
            folder_1_count = split_point
            folder_2_count = count - split_point

            print(f"\n   Prompt {arc}_{prompt} ({count} files):")
            print(f"      → Folder 1: {folder_1_count} file(s)")
            print(f"      → Folder 2: {folder_2_count} file(s)")

    def _execute_dispersion(self, plan: Dict[Path, Path]):
        """Execute the file dispersion."""
        for source_path, dest_path in plan.items():
            # Check for collisions
            if dest_path.exists():
                print(f"      ⚠️  WARNING: {dest_path.name} already exists in {dest_path.parent.name}/, skipping")
                continue

            # Move file
            shutil.move(str(source_path), str(dest_path))

    # ===== CONSOLIDATE METHODS =====

    def _find_audio_files(self, directory: Path) -> List[Path]:
        """Find all audio files in a directory."""
        if not directory.exists():
            return []

        files = []
        for ext in self.AUDIO_EXTENSIONS:
            files.extend(directory.glob(f"*{ext}"))

        return sorted(files)

    def _generate_consolidation_plan(
        self, files_1: List[Path], files_2: List[Path]
    ) -> Dict[Path, Tuple[Path, str]]:
        """Generate consolidation plan: source -> (destination, prefix)."""
        plan = {}

        # Files from folder 1/ get A_ prefix
        for file_path in files_1:
            new_name = f"A_{file_path.name}"
            dest_path = self.songs_dir / new_name
            plan[file_path] = (dest_path, 'A')

        # Files from folder 2/ get B_ prefix
        for file_path in files_2:
            new_name = f"B_{file_path.name}"
            dest_path = self.songs_dir / new_name
            plan[file_path] = (dest_path, 'B')

        return plan

    def _display_consolidation_plan(
        self, plan: Dict[Path, Tuple[Path, str]]
    ):
        """Display the consolidation plan."""
        # Group by prefix
        a_files = [src for src, (dest, prefix) in plan.items() if prefix == 'A']
        b_files = [src for src, (dest, prefix) in plan.items() if prefix == 'B']

        if a_files:
            print(f"\n   From 1/ (A_ prefix): {len(a_files)} file(s)")
        if b_files:
            print(f"   From 2/ (B_ prefix): {len(b_files)} file(s)")

    def _execute_consolidation(self, plan: Dict[Path, Tuple[Path, str]]):
        """Execute the consolidation."""
        # Ensure Songs/ exists
        self.songs_dir.mkdir(parents=True, exist_ok=True)

        skipped = 0
        moved = 0

        for source_path, (dest_path, prefix) in plan.items():
            # Check for collisions
            if dest_path.exists():
                skipped += 1
                continue

            # Move file
            shutil.move(str(source_path), str(dest_path))
            moved += 1

        if skipped > 0:
            print(f"\n   ⚠️  Skipped {skipped} file(s) that already exist in Songs/")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Disperse and consolidate in one command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview the complete workflow
  python scripts/disperse_and_consolidate.py --track 31 --dry-run

  # Execute disperse + consolidate
  python scripts/disperse_and_consolidate.py --track 31

Workflow:
  1. Disperses files from Staging/ → 1/ and 2/ (split evenly per prompt)
  2. Consolidates files from 1/ and 2/ → Songs/ (with A_/B_ prefixes)

This combines two separate commands into one streamlined workflow.
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
        processor = DisperseAndConsolidator(args.track, dry_run=args.dry_run)
        processor.process()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
