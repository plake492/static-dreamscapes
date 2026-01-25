#!/usr/bin/env python3
"""
Auto-rename staged audio files.

Scans Tracks/{number}/Staging/ for unformatted audio files,
determines the next arc_prompt combination, and renames files
in place following the pattern: arc_prompt_song[letter].ext

Usage:
    python scripts/stage_and_rename.py --track 31 [--dry-run]
"""

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import sys
import json

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingest.filename_parser import FilenameParser


class LetterSequence:
    """Handle letter sequence generation (a, b, ..., z, aa, ab, ...)"""

    @staticmethod
    def next_letter(current: str) -> str:
        """
        Get next letter in sequence.

        Examples:
            a -> b
            z -> aa
            az -> ba
            zz -> aaa
        """
        if not current:
            return 'a'

        chars = list(current.lower())
        i = len(chars) - 1

        # Increment from right to left with carry
        while i >= 0:
            if chars[i] != 'z':
                chars[i] = chr(ord(chars[i]) + 1)
                return ''.join(chars)
            else:
                chars[i] = 'a'
                i -= 1

        # All were 'z', prepend 'a'
        return 'a' + ''.join(chars)

    @staticmethod
    def get_max_letter(letters: List[str]) -> str:
        """
        Find maximum letter from list.

        Sort by length first (longer = higher), then alphabetically.
        """
        if not letters:
            return ''

        sorted_letters = sorted(letters, key=lambda x: (len(x), x))
        return sorted_letters[-1]


class NextArcPromptFinder:
    """Determine the next arc_prompt combination for a track."""

    def __init__(self, track_number: int, base_dir: Path = Path("./Tracks")):
        self.track_number = track_number
        self.track_dir = base_dir / str(track_number)
        self.songs_dir = self.track_dir / "Songs"
        self.staging_dir = self.track_dir / "Staging"
        self.metadata_file = self.track_dir / "metadata" / "track_info.json"
        self.parser = FilenameParser()

    def find_next_arc_prompt(self) -> Tuple[int, int]:
        """
        Find next (arc, prompt) combination.

        Returns:
            Tuple of (arc_number, prompt_number)

        Raises:
            ValueError if cannot determine next prompt
            FileNotFoundError if metadata missing
        """
        # 1. Scan existing Songs/ and staging/ for highest arc_prompt
        max_arc, max_prompt = self._scan_existing_songs(staging_dir=self.staging_dir)

        # 2. Load Notion metadata to validate
        notion_metadata = self._load_notion_metadata()

        # 3. Determine next prompt
        next_arc, next_prompt = self._calculate_next(
            max_arc, max_prompt, notion_metadata
        )

        # 4. Validate it exists in Notion doc
        self._validate_prompt_exists(next_arc, next_prompt, notion_metadata)

        return next_arc, next_prompt

    def _scan_existing_songs(self, staging_dir: Optional[Path] = None) -> Tuple[int, int]:
        """
        Scan Songs/ and optionally staging/ for highest (arc, prompt).

        Args:
            staging_dir: Optional staging directory to also scan for formatted files
        """
        max_arc = 0
        max_prompt = 0

        # Scan Songs/ directory
        if self.songs_dir.exists():
            valid_files = self.parser.scan_directory(self.songs_dir, recursive=False)

            for file_path in valid_files:
                components = self.parser.parse(file_path.name)
                if components:
                    if (components.arc_number > max_arc or
                        (components.arc_number == max_arc and
                         components.prompt_number > max_prompt)):
                        max_arc = components.arc_number
                        max_prompt = components.prompt_number

        # Also scan staging/ for already-formatted files
        if staging_dir and staging_dir.exists():
            staging_files = self.parser.scan_directory(staging_dir, recursive=False)

            for file_path in staging_files:
                components = self.parser.parse(file_path.name)
                if components:
                    if (components.arc_number > max_arc or
                        (components.arc_number == max_arc and
                         components.prompt_number > max_prompt)):
                        max_arc = components.arc_number
                        max_prompt = components.prompt_number

        return max_arc, max_prompt

    def _load_notion_metadata(self) -> dict:
        """Load track metadata from JSON and parse actual Notion doc for arc structure."""
        if not self.metadata_file.exists():
            raise FileNotFoundError(
                f"Track metadata not found: {self.metadata_file}\n"
                "Run scaffold-track first to create track structure."
            )

        with open(self.metadata_file) as f:
            metadata = json.load(f)

        # Extract Notion page ID from URL and load cached markdown
        notion_url = metadata.get('notion_url', '')
        if notion_url:
            # Extract page ID from URL (last segment before query params)
            page_id = notion_url.split('/')[-1].split('?')[0].split('-')[-1]
            notion_cache_path = Path(f"./data/cache/notion_docs/{page_id}.md")

            if notion_cache_path.exists():
                # Parse the actual Notion doc to get accurate arc/prompt counts
                arc_structure = self._parse_notion_arc_structure(notion_cache_path)
                if arc_structure:
                    metadata['arcs'] = arc_structure

        return metadata

    def _parse_notion_arc_structure(self, notion_file: Path) -> Optional[list]:
        """
        Parse Notion markdown to extract arc structure with prompt number ranges.

        Returns:
            List of arc dictionaries with arc_number, arc_name, min_prompt, max_prompt
        """
        import re

        arcs = []
        current_arc = None
        arc_number = 0

        with open(notion_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Detect arc/phase headers (e.g., "### Phase 1 — Pre-Dawn Stillness")
                phase_match = re.match(r'^###\s+Phase\s+(\d+)\s+[—-]\s+(.+)$', line, re.IGNORECASE)
                if phase_match:
                    # Save previous arc if exists
                    if current_arc:
                        arcs.append(current_arc)

                    arc_number = int(phase_match.group(1))
                    arc_name = phase_match.group(2).strip()
                    current_arc = {
                        'arc_number': arc_number,
                        'arc_name': arc_name,
                        'min_prompt': None,
                        'max_prompt': None
                    }
                    continue

                # Extract prompt numbers (lines starting with "- [ ]" or "- [x]" followed by a number)
                if current_arc:
                    prompt_match = re.match(r'^-\s+\[(x| )\]\s+(\d+)\.', line)
                    if prompt_match:
                        prompt_num = int(prompt_match.group(2))
                        if current_arc['min_prompt'] is None:
                            current_arc['min_prompt'] = prompt_num
                        current_arc['max_prompt'] = prompt_num

        # Don't forget the last arc
        if current_arc:
            arcs.append(current_arc)

        # Convert to the format expected by the rest of the code
        # Add 'prompts' field as max_prompt for compatibility
        for arc in arcs:
            if arc['max_prompt'] is not None:
                arc['prompts'] = arc['max_prompt']

        return arcs if arcs else None

    def _calculate_next(self, max_arc: int, max_prompt: int,
                        metadata: dict) -> Tuple[int, int]:
        """Calculate next (arc, prompt) from current maximum."""

        # If no files exist, start at first arc, first prompt
        if max_arc == 0:
            if metadata['arcs']:
                first_arc = metadata['arcs'][0]
                # Use min_prompt if available, otherwise 1
                start_prompt = first_arc.get('min_prompt', 1)
                return first_arc['arc_number'], start_prompt
            return 1, 1

        # Find current arc info
        current_arc = None
        for arc in metadata['arcs']:
            if arc['arc_number'] == max_arc:
                current_arc = arc
                break

        if not current_arc:
            raise ValueError(f"Arc {max_arc} not found in metadata")

        # Check if we can increment prompt in current arc
        # Use max_prompt from arc if available, otherwise fall back to prompts count
        arc_max_prompt = current_arc.get('max_prompt', current_arc.get('prompts'))

        if arc_max_prompt and max_prompt < arc_max_prompt:
            return max_arc, max_prompt + 1

        # Move to next arc
        next_arc_num = max_arc + 1
        next_arc = None
        for arc in metadata['arcs']:
            if arc['arc_number'] == next_arc_num:
                next_arc = arc
                break

        if not next_arc:
            raise ValueError(
                f"All prompts completed for track {self.track_number}. "
                f"Last: Arc {max_arc}, Prompt {max_prompt}"
            )

        # Start at the first prompt of the next arc
        next_prompt = next_arc.get('min_prompt', 1)
        return next_arc_num, next_prompt

    def _validate_prompt_exists(self, arc: int, prompt: int, metadata: dict):
        """Validate that the arc/prompt exists in Notion doc."""
        for arc_data in metadata['arcs']:
            if arc_data['arc_number'] == arc:
                # Use max_prompt if available, otherwise fall back to prompts
                arc_max_prompt = arc_data.get('max_prompt', arc_data.get('prompts'))
                arc_min_prompt = arc_data.get('min_prompt', 1)

                if arc_max_prompt and arc_min_prompt:
                    if arc_min_prompt <= prompt <= arc_max_prompt:
                        return True
                    raise ValueError(
                        f"Prompt {prompt} does not exist in Arc {arc} "
                        f"(valid range: {arc_min_prompt}-{arc_max_prompt})"
                    )
                elif arc_max_prompt:
                    if prompt <= arc_max_prompt:
                        return True
                    raise ValueError(
                        f"Prompt {prompt} does not exist in Arc {arc} "
                        f"(max: {arc_max_prompt})"
                    )

        raise ValueError(f"Arc {arc} not found in metadata")


class StagingProcessor:
    """Process files from staging directory."""

    AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac']

    def __init__(self, track_number: int, dry_run: bool = False):
        self.track_number = track_number
        self.dry_run = dry_run
        self.track_dir = Path(f"./Tracks/{track_number}")
        self.staging_dir = self.track_dir / "Staging"
        self.songs_dir = self.track_dir / "Songs"
        self.parser = FilenameParser()
        self.finder = NextArcPromptFinder(track_number)

    def process(self):
        """Main processing workflow."""
        # 1. Validate directories
        self._validate_directories()

        # 2. Find audio files in staging, separated by formatted/unformatted
        unformatted_files, formatted_files = self._find_audio_files()

        # Report on formatted files that will be skipped
        if formatted_files:
            print(f"Found {len(formatted_files)} already-formatted file(s) in Staging/ (will be skipped):")
            for f in formatted_files:
                print(f"  ✓ {f.name}")
            print()

        # Check if there are any unformatted files to process
        if not unformatted_files:
            if formatted_files:
                print("No unformatted files to process. All files in Staging/ are already properly formatted.")
            else:
                print(f"No audio files found in {self.staging_dir}")
            return

        print(f"Found {len(unformatted_files)} unformatted file(s) to process:")

        # 3. Determine next arc_prompt
        try:
            arc, prompt = self.finder.find_next_arc_prompt()
        except Exception as e:
            print(f"Error determining next arc_prompt: {e}")
            raise

        print(f"Next arc_prompt: {arc}_{prompt}")

        # 4. Find next available letter for this arc_prompt
        next_letter = self._find_next_letter(arc, prompt)

        print(f"Starting letter: {next_letter}")

        # 5. Generate rename plan
        rename_plan = self._generate_rename_plan(
            unformatted_files, arc, prompt, next_letter
        )

        # 6. Display plan
        self._display_plan(rename_plan)

        # 7. Execute (or dry-run)
        if self.dry_run:
            print("\n[DRY RUN] No files were renamed.")
        else:
            confirm = input("\nProceed with rename? [y/N]: ")
            if confirm.lower() == 'y':
                self._execute_rename(rename_plan)
                print(f"\n✅ Successfully renamed {len(rename_plan)} file(s) in Staging/")
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

    def _find_audio_files(self) -> Tuple[List[Path], List[Path]]:
        """
        Find all audio files in staging directory.

        Returns:
            Tuple of (unformatted_files, formatted_files)
        """
        unformatted = []
        formatted = []

        for ext in self.AUDIO_EXTENSIONS:
            for file_path in self.staging_dir.glob(f"*{ext}"):
                # Check if file is already properly formatted
                if self.parser.is_valid_filename(file_path.name):
                    formatted.append(file_path)
                else:
                    unformatted.append(file_path)

        return sorted(unformatted), sorted(formatted)

    def _find_next_letter(self, arc: int, prompt: int) -> str:
        """Find next available letter for this arc_prompt combination."""
        pattern = f"{arc}_{prompt}_{self.track_number}"
        letters = []

        # Scan both Songs/ and Staging/ for existing files with this arc_prompt
        for directory in [self.songs_dir, self.staging_dir]:
            if directory.exists():
                for file_path in directory.iterdir():
                    if file_path.is_file() and file_path.name.startswith(pattern):
                        components = self.parser.parse(file_path.name)
                        if components:
                            letters.append(components.order_marker)

        # Find max and increment
        if letters:
            max_letter = LetterSequence.get_max_letter(letters)
            return LetterSequence.next_letter(max_letter)
        else:
            return 'a'

    def _generate_rename_plan(self, files: List[Path], arc: int,
                              prompt: int, start_letter: str) -> List[Tuple[Path, str]]:
        """Generate list of (source_path, dest_filename) tuples."""
        plan = []
        current_letter = start_letter

        for file_path in files:
            ext = file_path.suffix
            new_name = f"{arc}_{prompt}_{self.track_number}{current_letter}{ext}"
            plan.append((file_path, new_name))
            current_letter = LetterSequence.next_letter(current_letter)

        return plan

    def _display_plan(self, plan: List[Tuple[Path, str]]):
        """Display the rename plan."""
        print("\nRename Plan:")
        print("=" * 70)
        for source, dest_name in plan:
            print(f"  {source.name:<30} -> {dest_name}")
        print("=" * 70)

    def _execute_rename(self, plan: List[Tuple[Path, str]]):
        """Execute the rename operations in place."""
        for source_path, dest_name in plan:
            dest_path = self.staging_dir / dest_name

            # Check for collisions
            if dest_path.exists():
                print(f"⚠️  WARNING: {dest_name} already exists, skipping")
                continue

            # Rename file in place
            source_path.rename(dest_path)
            print(f"✓ Renamed: {source_path.name} -> {dest_name}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Auto-rename and move staged audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview rename for track 31
  python scripts/stage_and_rename.py --track 31 --dry-run

  # Actually rename and move files
  python scripts/stage_and_rename.py --track 31
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
        processor = StagingProcessor(args.track, dry_run=args.dry_run)
        processor.process()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
