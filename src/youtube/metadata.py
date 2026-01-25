"""Parse and validate YouTube metadata from Notion and render files."""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..core.models import Track
from ..ingest.notion_parser import NotionParser

logger = logging.getLogger(__name__)


class MetadataParser:
    """Parse YouTube metadata from various sources."""

    # YouTube limits
    MAX_TITLE_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TAGS_LENGTH = 500
    MAX_TAG_COUNT = 30
    MAX_INDIVIDUAL_TAG_LENGTH = 30

    def __init__(self, track: Track, notion_parser: NotionParser):
        """
        Initialize metadata parser.

        Args:
            track: Track database record
            notion_parser: Notion parser instance
        """
        self.track = track
        self.notion_parser = notion_parser
        self.notion_metadata = None

    def load_notion_metadata(self):
        """Load fresh metadata from Notion."""
        if not self.track.notion_url:
            raise ValueError(f"Track {self.track.track_number} has no Notion URL")

        logger.info(f"Loading metadata from Notion: {self.track.notion_url}")
        self.notion_metadata = self.notion_parser.parse_notion_doc(self.track.notion_url)

    def get_title(self) -> str:
        """
        Get video title.

        Returns:
            Title string (max 100 chars)
        """
        if not self.notion_metadata:
            self.load_notion_metadata()

        title = self.notion_metadata.title

        if len(title) > self.MAX_TITLE_LENGTH:
            logger.warning(f"Title exceeds {self.MAX_TITLE_LENGTH} chars, truncating")
            title = title[:self.MAX_TITLE_LENGTH - 3] + "..."

        return title

    def get_description(self, render_dir: Path) -> str:
        """
        Get video description from render folder.

        Args:
            render_dir: Path to render output directory

        Returns:
            Description string (max 5000 chars)
        """
        desc_file = render_dir / "youtube-description.txt"

        if not desc_file.exists():
            logger.warning(f"Description file not found: {desc_file}")
            return self._generate_fallback_description()

        description = desc_file.read_text(encoding='utf-8')

        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            logger.warning(f"Description exceeds {self.MAX_DESCRIPTION_LENGTH} chars, truncating")
            description = description[:self.MAX_DESCRIPTION_LENGTH - 3] + "..."

        return description

    def get_tags(self) -> List[str]:
        """
        Get tags from Notion "Hidden Tags" section.

        Returns:
            List of tags (max 30 tags, 500 chars total)
        """
        if not self.notion_metadata:
            self.load_notion_metadata()

        tags = self.notion_metadata.hidden_tags

        # Validate individual tag length
        validated_tags = []
        for tag in tags:
            tag = tag.strip()
            if len(tag) > self.MAX_INDIVIDUAL_TAG_LENGTH:
                logger.warning(f"Tag too long, truncating: {tag}")
                tag = tag[:self.MAX_INDIVIDUAL_TAG_LENGTH]
            if tag:
                validated_tags.append(tag)

        # Enforce max count
        if len(validated_tags) > self.MAX_TAG_COUNT:
            logger.warning(f"Too many tags ({len(validated_tags)}), keeping first {self.MAX_TAG_COUNT}")
            validated_tags = validated_tags[:self.MAX_TAG_COUNT]

        # Enforce total length
        total_length = sum(len(tag) for tag in validated_tags)
        if total_length > self.MAX_TAGS_LENGTH:
            logger.warning(f"Tags total length exceeds {self.MAX_TAGS_LENGTH}, trimming")
            # Keep removing tags until under limit
            while total_length > self.MAX_TAGS_LENGTH and validated_tags:
                removed = validated_tags.pop()
                total_length -= len(removed)

        return validated_tags

    def get_category_id(self) -> str:
        """
        Get YouTube category ID.

        Returns:
            Category ID (default: "10" for Music)
        """
        # TODO: Make this configurable in Notion if needed
        return "10"  # Music

    def get_visible_hashtags(self) -> List[str]:
        """
        Get visible hashtags from Notion.

        Returns:
            List of hashtags (with # prefix)
        """
        if not self.notion_metadata:
            self.load_notion_metadata()

        return self.notion_metadata.visible_hashtags

    def _generate_fallback_description(self) -> str:
        """Generate basic description if file not found."""
        if not self.notion_metadata:
            self.load_notion_metadata()

        lines = []

        if self.notion_metadata.vibe_description:
            lines.append(self.notion_metadata.vibe_description)
            lines.append("")

        lines.append(f"A {self.track.duration_target}-minute focus music mix.")
        lines.append("")

        # Add visible hashtags
        hashtags = " ".join(self.notion_metadata.visible_hashtags)
        lines.append(hashtags)

        return "\n".join(lines)

    def validate_metadata(self, render_dir: Path) -> Tuple[bool, List[str]]:
        """
        Validate all metadata before upload.

        Args:
            render_dir: Path to render output directory

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        try:
            # Validate title
            title = self.get_title()
            if not title:
                errors.append("Title is empty")
            elif len(title) > self.MAX_TITLE_LENGTH:
                errors.append(f"Title exceeds {self.MAX_TITLE_LENGTH} characters")

            # Validate description
            description = self.get_description(render_dir)
            if not description:
                errors.append("Description is empty")
            elif len(description) > self.MAX_DESCRIPTION_LENGTH:
                errors.append(f"Description exceeds {self.MAX_DESCRIPTION_LENGTH} characters")

            # Validate tags
            tags = self.get_tags()
            if len(tags) > self.MAX_TAG_COUNT:
                errors.append(f"Too many tags: {len(tags)} (max {self.MAX_TAG_COUNT})")

            total_tag_length = sum(len(tag) for tag in tags)
            if total_tag_length > self.MAX_TAGS_LENGTH:
                errors.append(f"Tags total length: {total_tag_length} (max {self.MAX_TAGS_LENGTH})")

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_metadata_dict(self, render_dir: Path) -> Dict:
        """
        Get all metadata as dictionary for display/logging.

        Args:
            render_dir: Path to render output directory

        Returns:
            Dictionary of metadata
        """
        return {
            'title': self.get_title(),
            'description_length': len(self.get_description(render_dir)),
            'tags': self.get_tags(),
            'tag_count': len(self.get_tags()),
            'category_id': self.get_category_id(),
            'visible_hashtags': self.get_visible_hashtags(),
        }
