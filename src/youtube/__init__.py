"""YouTube upload and management functionality."""

from .auth import YouTubeAuthenticator
from .uploader import YouTubeUploader
from .metadata import MetadataParser
from .thumbnail import ThumbnailHandler

# Phase 2 modules (imported only when needed to avoid import errors)
# from .scheduler import ScheduleParser
# from .playlists import PlaylistManager

__all__ = [
    # Phase 1: MVP
    'YouTubeAuthenticator',
    'YouTubeUploader',
    'MetadataParser',
    'ThumbnailHandler',
    # Phase 2 (uncomment when implementing)
    # 'ScheduleParser',
    # 'PlaylistManager',
]
