"""Handle YouTube thumbnail validation and upload."""

import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class ThumbnailHandler:
    """Handle thumbnail validation and selection."""

    # YouTube thumbnail requirements
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    RECOMMENDED_WIDTH = 1280
    RECOMMENDED_HEIGHT = 720
    ALLOWED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    def __init__(self, render_dir: Path, track_number: int):
        """
        Initialize thumbnail handler.

        Args:
            render_dir: Path to render output directory
            track_number: Track number
        """
        self.render_dir = render_dir
        self.track_number = track_number

    def find_thumbnail(self) -> Optional[Path]:
        """
        Find thumbnail image in render directory.

        Priority order:
        1. thumbnail.jpg/png in render dir
        2. {track}.jpg/png in Image folder
        3. First image file in Image folder

        Returns:
            Path to thumbnail file, or None if not found
        """
        image_dir = self.render_dir / "Image"

        if not image_dir.exists():
            logger.warning(f"Image directory not found: {image_dir}")
            return None

        # Priority 1: thumbnail.jpg/png
        for ext in ['.jpg', '.jpeg', '.png']:
            thumbnail_path = image_dir / f"thumbnail{ext}"
            if thumbnail_path.exists():
                logger.info(f"Found thumbnail: {thumbnail_path}")
                return thumbnail_path

        # Priority 2: {track}.jpg/png
        for ext in ['.jpg', '.jpeg', '.png']:
            track_thumbnail = image_dir / f"{self.track_number}{ext}"
            if track_thumbnail.exists():
                logger.info(f"Found track thumbnail: {track_thumbnail}")
                return track_thumbnail

        # Priority 3: First image file
        for image_file in image_dir.iterdir():
            if image_file.suffix.lower() in self.ALLOWED_FORMATS:
                logger.info(f"Using first image found: {image_file}")
                return image_file

        logger.warning("No thumbnail image found in Image directory")
        return None

    def validate_thumbnail(self, thumbnail_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate thumbnail meets YouTube requirements.

        Args:
            thumbnail_path: Path to thumbnail file

        Returns:
            (is_valid, error_message)
        """
        if not thumbnail_path.exists():
            return False, f"File not found: {thumbnail_path}"

        # Check file extension
        if thumbnail_path.suffix.lower() not in self.ALLOWED_FORMATS:
            return False, f"Invalid format: {thumbnail_path.suffix} (allowed: {', '.join(self.ALLOWED_FORMATS)})"

        # Check file size
        file_size = thumbnail_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.2f}MB (max 2MB)"

        # Check image dimensions
        try:
            with Image.open(thumbnail_path) as img:
                width, height = img.size

                # Warn if not recommended size
                if width != self.RECOMMENDED_WIDTH or height != self.RECOMMENDED_HEIGHT:
                    logger.warning(
                        f"Thumbnail size {width}x{height} differs from recommended "
                        f"{self.RECOMMENDED_WIDTH}x{self.RECOMMENDED_HEIGHT}"
                    )

                # Validate minimum size (YouTube requirement)
                if width < 640 or height < 360:
                    return False, f"Thumbnail too small: {width}x{height} (min 640x360)"

        except Exception as e:
            return False, f"Failed to read image: {str(e)}"

        return True, None

    def get_thumbnail_info(self, thumbnail_path: Path) -> dict:
        """
        Get thumbnail information for display.

        Args:
            thumbnail_path: Path to thumbnail file

        Returns:
            Dictionary with thumbnail info
        """
        if not thumbnail_path.exists():
            return {'error': 'File not found'}

        info = {
            'path': str(thumbnail_path),
            'size_bytes': thumbnail_path.stat().st_size,
            'size_mb': thumbnail_path.stat().st_size / (1024 * 1024),
            'format': thumbnail_path.suffix,
        }

        try:
            with Image.open(thumbnail_path) as img:
                info['width'] = img.size[0]
                info['height'] = img.size[1]
                info['aspect_ratio'] = f"{img.size[0]}:{img.size[1]}"
        except Exception as e:
            info['error'] = str(e)

        return info
