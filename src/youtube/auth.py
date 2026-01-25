"""YouTube OAuth authentication handler."""

import os
import json
import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class YouTubeAuthenticator:
    """Handle YouTube OAuth 2.0 authentication."""

    # YouTube API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]

    def __init__(
        self,
        client_secrets_file: str = "./config/client_secrets.json",
        credentials_file: str = "./config/youtube_credentials.json"
    ):
        """
        Initialize authenticator.

        Args:
            client_secrets_file: Path to OAuth client secrets JSON
            credentials_file: Path to store credentials
        """
        self.client_secrets_file = Path(client_secrets_file)
        self.credentials_file = Path(credentials_file)
        self.credentials: Optional[Credentials] = None

    def authenticate(self, force_reauth: bool = False) -> Credentials:
        """
        Authenticate with YouTube API.

        Args:
            force_reauth: Force re-authentication even if credentials exist

        Returns:
            Google OAuth2 credentials

        Raises:
            FileNotFoundError: If client_secrets.json not found
            Exception: If authentication fails
        """
        # Check if client secrets exist
        if not self.client_secrets_file.exists():
            raise FileNotFoundError(
                f"Client secrets not found: {self.client_secrets_file}\n"
                "Please follow setup guide: docs/YOUTUBE_SETUP.md"
            )

        # Load existing credentials
        if not force_reauth and self.credentials_file.exists():
            logger.info(f"Loading credentials from {self.credentials_file}")
            self.credentials = Credentials.from_authorized_user_file(
                str(self.credentials_file),
                self.SCOPES
            )

        # Refresh if expired
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            logger.info("Refreshing expired credentials")
            try:
                self.credentials.refresh(Request())
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")
                self.credentials = None

        # New authentication flow
        if not self.credentials or not self.credentials.valid:
            logger.info("Starting OAuth authentication flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secrets_file),
                self.SCOPES
            )
            self.credentials = flow.run_local_server(port=8080)

            # Save credentials
            self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.credentials_file, 'w') as f:
                f.write(self.credentials.to_json())
            logger.info(f"Credentials saved to {self.credentials_file}")

        return self.credentials

    def get_youtube_service(self):
        """
        Get authenticated YouTube API service.

        Returns:
            YouTube API service object
        """
        if not self.credentials or not self.credentials.valid:
            self.authenticate()

        return build('youtube', 'v3', credentials=self.credentials)

    def test_authentication(self) -> bool:
        """
        Test if authentication works by fetching channel info.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            youtube = self.get_youtube_service()
            request = youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()

            if 'items' in response and len(response['items']) > 0:
                channel = response['items'][0]
                logger.info(f"✓ Authenticated as: {channel['snippet']['title']}")
                logger.info(f"  Channel ID: {channel['id']}")
                logger.info(f"  Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}")
                return True
            else:
                logger.error("No channel found for authenticated user")
                return False

        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            return False

    def revoke_credentials(self):
        """Revoke and delete stored credentials."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()
            logger.info(f"Credentials deleted: {self.credentials_file}")
        self.credentials = None
