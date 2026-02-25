"""YouTube playlist management functionality."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

from .auth import YouTubeAuthenticator

logger = logging.getLogger(__name__)


class PlaylistManager:
    """Manage YouTube playlists - add/remove videos, list playlists."""

    def __init__(
        self,
        authenticator: YouTubeAuthenticator,
        playlists_config_path: Optional[str] = None
    ):
        """
        Initialize playlist manager.

        Args:
            authenticator: YouTubeAuthenticator instance
            playlists_config_path: Path to playlist configuration YAML
        """
        self.authenticator = authenticator
        self.playlists_config_path = Path(playlists_config_path) if playlists_config_path else None
        self._youtube: Optional[Resource] = None
        self._playlists_config: Optional[Dict] = None

    @property
    def youtube(self) -> Resource:
        """Get authenticated YouTube service."""
        if self._youtube is None:
            self._youtube = self.authenticator.get_youtube_service()
        return self._youtube

    @property
    def playlists_config(self) -> Dict:
        """Load playlists configuration."""
        if self._playlists_config is None:
            if self.playlists_config_path and self.playlists_config_path.exists():
                with open(self.playlists_config_path) as f:
                    self._playlists_config = yaml.safe_load(f)
            else:
                self._playlists_config = {'playlists': []}
        return self._playlists_config

    def list_channel_playlists(self) -> List[Dict]:
        """
        List all playlists on the authenticated channel.

        Returns:
            List of playlist info dicts
        """
        playlists = []

        try:
            request = self.youtube.playlists().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=50
            )

            while request:
                response = request.execute()

                for item in response.get('items', []):
                    playlists.append({
                        'id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'video_count': item['contentDetails']['itemCount'],
                        'privacy': item['status']['privacyStatus'] if 'status' in item else 'unknown',
                    })

                request = self.youtube.playlists().list_next(request, response)

        except HttpError as e:
            logger.error(f"Failed to list playlists: {e}")

        return playlists

    def add_video_to_playlist(
        self,
        video_id: str,
        playlist_id: str,
        position: Optional[int] = None
    ) -> bool:
        """
        Add video to a playlist.

        Args:
            video_id: YouTube video ID
            playlist_id: YouTube playlist ID
            position: Position in playlist (None = end)

        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }

            if position is not None:
                body["snippet"]["position"] = position

            self.youtube.playlistItems().insert(
                part="snippet",
                body=body
            ).execute()

            logger.info(f"Added video {video_id} to playlist {playlist_id}")
            return True

        except HttpError as e:
            if e.resp.status == 409:
                logger.warning(f"Video {video_id} already in playlist {playlist_id}")
                return True  # Already exists is considered success
            logger.error(f"Failed to add video to playlist: {e}")
            return False

    def remove_video_from_playlist(
        self,
        video_id: str,
        playlist_id: str
    ) -> bool:
        """
        Remove video from a playlist.

        Args:
            video_id: YouTube video ID
            playlist_id: YouTube playlist ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, find the playlist item ID
            request = self.youtube.playlistItems().list(
                part="id,snippet",
                playlistId=playlist_id,
                videoId=video_id
            )
            response = request.execute()

            if not response.get('items'):
                logger.warning(f"Video {video_id} not found in playlist {playlist_id}")
                return False

            playlist_item_id = response['items'][0]['id']

            # Delete the playlist item
            self.youtube.playlistItems().delete(id=playlist_item_id).execute()

            logger.info(f"Removed video {video_id} from playlist {playlist_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to remove video from playlist: {e}")
            return False

    def get_matching_playlists(
        self,
        track_metadata: Dict
    ) -> List[str]:
        """
        Get playlist IDs that match the track based on config criteria.

        Args:
            track_metadata: Dict with track info (tags, duration_target, etc.)

        Returns:
            List of playlist IDs to add the video to
        """
        matching_ids = []

        for playlist_config in self.playlists_config.get('playlists', []):
            playlist_id = playlist_config.get('id')
            if not playlist_id:
                continue

            match_criteria = playlist_config.get('match_criteria', {})

            # Empty criteria = match all
            if not match_criteria:
                matching_ids.append(playlist_id)
                continue

            # Check duration_target
            if 'duration_target' in match_criteria:
                track_duration = track_metadata.get('duration_target', 0)
                if track_duration != match_criteria['duration_target']:
                    continue

            # Check tags_include (any tag matches)
            if 'tags_include' in match_criteria:
                track_tags = set(t.lower() for t in track_metadata.get('tags', []))
                required_tags = set(t.lower() for t in match_criteria['tags_include'])
                if not track_tags.intersection(required_tags):
                    continue

            # Check tags_exclude (none of these tags)
            if 'tags_exclude' in match_criteria:
                track_tags = set(t.lower() for t in track_metadata.get('tags', []))
                excluded_tags = set(t.lower() for t in match_criteria['tags_exclude'])
                if track_tags.intersection(excluded_tags):
                    continue

            # Passed all criteria
            matching_ids.append(playlist_id)
            logger.debug(f"Track matches playlist: {playlist_config.get('name', playlist_id)}")

        return matching_ids

    def auto_add_to_playlists(
        self,
        video_id: str,
        track_metadata: Dict
    ) -> List[str]:
        """
        Automatically add video to matching playlists based on config.

        Args:
            video_id: YouTube video ID
            track_metadata: Track metadata for matching

        Returns:
            List of playlist IDs the video was added to
        """
        added_to = []
        matching_playlists = self.get_matching_playlists(track_metadata)

        for playlist_id in matching_playlists:
            if self.add_video_to_playlist(video_id, playlist_id):
                added_to.append(playlist_id)

        if added_to:
            logger.info(f"Video {video_id} added to {len(added_to)} playlist(s)")
        else:
            logger.warning(f"Video {video_id} not added to any playlists")

        return added_to

    def get_playlist_videos(self, playlist_id: str) -> List[Dict]:
        """
        Get all videos in a playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            List of video info dicts
        """
        videos = []

        try:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50
            )

            while request:
                response = request.execute()

                for item in response.get('items', []):
                    videos.append({
                        'video_id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'position': item['snippet']['position'],
                        'added_at': item['snippet']['publishedAt'],
                    })

                request = self.youtube.playlistItems().list_next(request, response)

        except HttpError as e:
            logger.error(f"Failed to get playlist videos: {e}")

        return videos

    def create_playlist(
        self,
        title: str,
        description: str = "",
        privacy_status: str = "private"
    ) -> Optional[str]:
        """
        Create a new playlist.

        Args:
            title: Playlist title
            description: Playlist description
            privacy_status: public/private/unlisted

        Returns:
            Playlist ID if successful, None otherwise
        """
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }

            response = self.youtube.playlists().insert(
                part="snippet,status",
                body=body
            ).execute()

            playlist_id = response['id']
            logger.info(f"Created playlist: {title} ({playlist_id})")
            return playlist_id

        except HttpError as e:
            logger.error(f"Failed to create playlist: {e}")
            return None
