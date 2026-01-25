"""
Filename generation and sanitization utilities for rendered track outputs.
"""
import re
from pathlib import Path
from typing import Optional


def sanitize_for_filename(text: str, max_length: int = 80) -> str:
    """
    Sanitize text for use in a filename.

    Args:
        text: The text to sanitize
        max_length: Maximum length for the sanitized filename (default: 80)

    Returns:
        Sanitized string safe for use in filenames

    Examples:
        >>> sanitize_for_filename("Track 25: Hello World! 🎵")
        'track-25-hello-world'

        >>> sanitize_for_filename("Midnight Neon CRT Desk 🌧️ 3HR LoFi")
        'midnight-neon-crt-desk-3hr-lofi'
    """
    # Remove emojis and special characters
    text = re.sub(r'[^\w\s-]', '', text)

    # Convert to lowercase
    text = text.lower()

    # Replace whitespace and multiple dashes with single dash
    text = re.sub(r'[-\s]+', '-', text)

    # Remove leading/trailing dashes
    text = text.strip('-')

    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]  # Cut at word boundary

    return text


def generate_track_filename(
    track_number: int,
    track_title: Optional[str] = None,
    output_filename: Optional[str] = None,
    extension: str = "mp4"
) -> str:
    """
    Generate a filename for a rendered track.

    Priority:
    1. Use output_filename if provided (from Notion doc)
    2. Generate from track_number + sanitized track_title
    3. Fall back to track-{number}.{extension}

    Args:
        track_number: The track number
        track_title: The full track title (will be sanitized)
        output_filename: Pre-formatted filename from Notion (optional)
        extension: File extension (default: "mp4")

    Returns:
        Generated filename

    Examples:
        >>> generate_track_filename(25, "Midnight Neon CRT Desk 🌧️ 3HR LoFi")
        'track-25-midnight-neon-crt-desk-3hr-lofi.mp4'

        >>> generate_track_filename(25, output_filename="my-custom-name")
        'my-custom-name.mp4'

        >>> generate_track_filename(25)
        'track-25.mp4'
    """
    # Ensure extension doesn't have leading dot
    extension = extension.lstrip('.')

    # Option 1: Use provided output_filename
    if output_filename:
        # Ensure it has correct extension
        if not output_filename.endswith(f'.{extension}'):
            # Remove any existing extension and add correct one
            base = output_filename.rsplit('.', 1)[0] if '.' in output_filename else output_filename
            return f"{base}.{extension}"
        return output_filename

    # Option 2: Generate from track number + title
    if track_title:
        sanitized_title = sanitize_for_filename(track_title)
        return f"track-{track_number}-{sanitized_title}.{extension}"

    # Option 3: Fall back to just track number
    return f"track-{track_number}.{extension}"


def get_output_path(
    track_number: int,
    track_title: Optional[str] = None,
    output_filename: Optional[str] = None,
    custom_output: Optional[str] = None,
    output_dir: str = "output"
) -> Path:
    """
    Get the full output path for a rendered track.

    Args:
        track_number: The track number
        track_title: The full track title (will be sanitized)
        output_filename: Pre-formatted filename from Notion (optional)
        custom_output: User-specified custom output path (overrides everything)
        output_dir: Base output directory (default: "output")

    Returns:
        Path object for the output file

    Examples:
        >>> get_output_path(25, "Midnight Neon CRT Desk")
        Path('output/track-25-midnight-neon-crt-desk.mp4')

        >>> get_output_path(25, custom_output="./custom/my-video.mp4")
        Path('custom/my-video.mp4')
    """
    # If custom output provided, use it directly
    if custom_output:
        return Path(custom_output)

    # Generate filename
    filename = generate_track_filename(
        track_number=track_number,
        track_title=track_title,
        output_filename=output_filename
    )

    # Combine with output directory
    output_path = Path(output_dir) / filename

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path
