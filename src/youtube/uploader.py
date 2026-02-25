"""YouTube video upload functionality with resumable upload support."""

import logging
import os
import time
from pathlib import Path
from typing import Dict, Optional, List

from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from .auth import YouTubeAuthenticator
from .metadata import MetadataParser
from .thumbnail import ThumbnailHandler

logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Handle YouTube video uploads with resumable upload support."""

    # Maximum file size (256GB)
    MAX_FILE_SIZE = 256 * 1024 * 1024 * 1024

    # Chunk size for resumable uploads (10MB)
    CHUNK_SIZE = 10 * 1024 * 1024

    # Retry configuration
    MAX_RETRIES = 5
    RETRY_DELAY_BASE = 2  # Base delay in seconds (exponential backoff)

    def __init__(
        self,
        authenticator: YouTubeAuthenticator,
        default_category: str = "10",
        default_privacy: str = "private"
    ):
        """
        Initialize uploader.

        Args:
            authenticator: YouTubeAuthenticator instance
            default_category: Default category ID (10 = Music)
            default_privacy: Default privacy status
        """
        self.authenticator = authenticator
        self.default_category = default_category
        self.default_privacy = default_privacy
        self._youtube: Optional[Resource] = None

    @property
    def youtube(self) -> Resource:
        """Get authenticated YouTube service."""
        if self._youtube is None:
            self._youtube = self.authenticator.get_youtube_service()
        return self._youtube

    def validate_video_file(self, video_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate video file before upload.

        Args:
            video_path: Path to video file

        Returns:
            (is_valid, error_message)
        """
        if not video_path.exists():
            return False, f"Video file not found: {video_path}"

        if video_path.suffix.lower() != '.mp4':
            return False, f"Only MP4 files supported, got: {video_path.suffix}"

        file_size = video_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            size_gb = file_size / (1024 ** 3)
            return False, f"File too large: {size_gb:.2f}GB (max 256GB)"

        if file_size == 0:
            return False, "Video file is empty"

        return True, None

    def upload_video(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: List[str],
        category_id: Optional[str] = None,
        privacy_status: Optional[str] = None,
        publish_at: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Upload video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (default: Music)
            privacy_status: public/private/unlisted
            publish_at: ISO 8601 datetime for scheduled publish (requires private status)
            progress_callback: Callback function(percent, status) for progress updates

        Returns:
            Dict with video_id, url, and other response data

        Raises:
            FileNotFoundError: If video file not found
            ValueError: If validation fails
            HttpError: If YouTube API returns error
        """
        # Validate video file
        is_valid, error = self.validate_video_file(video_path)
        if not is_valid:
            raise ValueError(error)

        # Use defaults
        category_id = category_id or self.default_category
        privacy_status = privacy_status or self.default_privacy

        # If scheduling, must be private
        if publish_at and privacy_status != "private":
            logger.warning("Scheduled videos must be private, overriding privacy status")
            privacy_status = "private"

        # Build request body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            }
        }

        # Add publish schedule if provided
        if publish_at:
            body["status"]["publishAt"] = publish_at

        logger.info(f"Starting upload: {video_path.name}")
        logger.info(f"  Title: {title}")
        logger.info(f"  Privacy: {privacy_status}")
        if publish_at:
            logger.info(f"  Scheduled: {publish_at}")

        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=self.CHUNK_SIZE,
            resumable=True,
            mimetype='video/mp4'
        )

        # Create insert request
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        # Execute with resumable upload
        response = self._resumable_upload(request, progress_callback)

        if response:
            video_id = response['id']
            result = {
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'title': response['snippet']['title'],
                'status': response['status']['privacyStatus'],
                'publish_at': response['status'].get('publishAt'),
            }
            logger.info(f"Upload successful: {result['url']}")
            return result
        else:
            raise RuntimeError("Upload failed: No response from YouTube API")

    def _resumable_upload(
        self,
        request,
        progress_callback: Optional[callable] = None
    ) -> Optional[Dict]:
        """
        Execute resumable upload with retry logic.

        Args:
            request: YouTube API insert request
            progress_callback: Callback(percent, status) for progress

        Returns:
            API response dict or None
        """
        response = None
        retry = 0

        while response is None:
            try:
                if progress_callback:
                    progress_callback(0, "Starting upload...")

                status, response = request.next_chunk()

                while response is None:
                    if status:
                        percent = int(status.progress() * 100)
                        if progress_callback:
                            progress_callback(percent, f"Uploading... {percent}%")
                        logger.debug(f"Upload progress: {percent}%")

                    status, response = request.next_chunk()

                if progress_callback:
                    progress_callback(100, "Upload complete!")

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    # Retryable error
                    retry += 1
                    if retry > self.MAX_RETRIES:
                        logger.error(f"Max retries exceeded: {e}")
                        raise

                    delay = self.RETRY_DELAY_BASE ** retry
                    logger.warning(f"Retryable error {e.resp.status}, retrying in {delay}s...")
                    if progress_callback:
                        progress_callback(-1, f"Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    # Non-retryable error
                    logger.error(f"Upload failed: {e}")
                    raise

            except Exception as e:
                logger.error(f"Unexpected error during upload: {e}")
                raise

        return response

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> bool:
        """
        Set custom thumbnail for uploaded video.

        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image

        Returns:
            True if successful, False otherwise
        """
        if not thumbnail_path.exists():
            logger.error(f"Thumbnail not found: {thumbnail_path}")
            return False

        try:
            media = MediaFileUpload(
                str(thumbnail_path),
                mimetype=self._get_image_mimetype(thumbnail_path)
            )

            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            ).execute()

            logger.info(f"Thumbnail set for video {video_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to set thumbnail: {e}")
            return False

    def _get_image_mimetype(self, path: Path) -> str:
        """Get MIME type for image file."""
        suffix = path.suffix.lower()
        mimetypes = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
        }
        return mimetypes.get(suffix, 'image/jpeg')

    def upload_with_metadata(
        self,
        video_path: Path,
        metadata_parser: MetadataParser,
        thumbnail_handler: ThumbnailHandler,
        render_dir: Path,
        privacy_status: Optional[str] = None,
        publish_at: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Upload video with metadata from parsers.

        Args:
            video_path: Path to video file
            metadata_parser: MetadataParser instance
            thumbnail_handler: ThumbnailHandler instance
            render_dir: Path to render directory
            privacy_status: Override privacy status
            publish_at: Override publish schedule
            progress_callback: Progress callback function

        Returns:
            Dict with upload results
        """
        # Get metadata
        title = metadata_parser.get_title()
        description = metadata_parser.get_description(render_dir)
        tags = metadata_parser.get_tags()
        category_id = metadata_parser.get_category_id()

        # Upload video
        result = self.upload_video(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status,
            publish_at=publish_at,
            progress_callback=progress_callback
        )

        # Set thumbnail
        thumbnail_path = thumbnail_handler.find_thumbnail()
        if thumbnail_path:
            is_valid, error = thumbnail_handler.validate_thumbnail(thumbnail_path)
            if is_valid:
                self.set_thumbnail(result['video_id'], thumbnail_path)
                result['thumbnail_set'] = True
            else:
                logger.warning(f"Thumbnail validation failed: {error}")
                result['thumbnail_set'] = False
                result['thumbnail_error'] = error
        else:
            logger.warning("No thumbnail found")
            result['thumbnail_set'] = False

        return result

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """
        Get information about an uploaded video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with video info or None
        """
        try:
            response = self.youtube.videos().list(
                part="snippet,status,statistics",
                id=video_id
            ).execute()

            if 'items' in response and len(response['items']) > 0:
                return response['items'][0]
            return None

        except HttpError as e:
            logger.error(f"Failed to get video info: {e}")
            return None
