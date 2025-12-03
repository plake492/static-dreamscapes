"""Filename parser for song files."""

import re
from typing import Optional
from pathlib import Path
import logging

from ..core.models import FilenameComponents

logger = logging.getLogger(__name__)


class FilenameParser:
    """Parse song filenames matching pattern: arc_prompt_song[order].mp3"""

    # Pattern: 2_6_19a.mp3 -> arc=2, prompt=6, song=19, order=a
    PATTERN = r'^(\d+)_(\d+)_(\d+)([a-z]+)\.(?:mp3|wav|m4a|flac)$'

    @classmethod
    def parse(cls, filename: str) -> Optional[FilenameComponents]:
        """
        Parse filename into components.

        Args:
            filename: Filename to parse (e.g., "2_6_19a.mp3")

        Returns:
            FilenameComponents if valid, None otherwise

        Examples:
            >>> parser = FilenameParser()
            >>> components = parser.parse("2_6_19a.mp3")
            >>> components.arc_number
            2
            >>> components.prompt_number
            6
            >>> components.song_number
            19
            >>> components.order_marker
            'a'
        """
        match = re.match(cls.PATTERN, filename.lower())

        if not match:
            logger.warning(f"Filename does not match pattern: {filename}")
            return None

        try:
            arc_number = int(match.group(1))
            prompt_number = int(match.group(2))
            song_number = int(match.group(3))
            order_marker = match.group(4)

            # Validate arc number (1-4)
            if arc_number < 1 or arc_number > 4:
                logger.warning(f"Invalid arc number ({arc_number}) in: {filename}")
                return None

            return FilenameComponents(
                arc_number=arc_number,
                prompt_number=prompt_number,
                song_number=song_number,
                order_marker=order_marker,
                original_filename=filename
            )

        except ValueError as e:
            logger.error(f"Error parsing filename {filename}: {e}")
            return None

    @classmethod
    def is_valid_filename(cls, filename: str) -> bool:
        """Check if filename matches expected pattern."""
        return bool(re.match(cls.PATTERN, filename.lower()))

    @classmethod
    def scan_directory(cls, directory: Path, recursive: bool = False) -> list[Path]:
        """
        Scan directory for valid song files.

        Args:
            directory: Directory to scan
            recursive: Scan subdirectories recursively

        Returns:
            List of Paths to valid song files
        """
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return []

        if not directory.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return []

        pattern = "**/*" if recursive else "*"
        valid_files = []

        for ext in [".mp3", ".wav", ".m4a", ".flac"]:
            for file_path in directory.glob(f"{pattern}{ext}"):
                if file_path.is_file() and cls.is_valid_filename(file_path.name):
                    valid_files.append(file_path)

        logger.info(f"Found {len(valid_files)} valid song files in {directory}")
        return sorted(valid_files)


def parse_filename(filename: str) -> Optional[FilenameComponents]:
    """Convenience function for parsing filenames."""
    return FilenameParser.parse(filename)
