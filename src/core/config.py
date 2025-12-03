"""Configuration loader for the LoFi Track Manager."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager."""

    def __init__(self, config_path: str = "./config/settings.yaml"):
        """Load configuration from YAML file."""
        # Load environment variables
        load_dotenv()

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Replace environment variable placeholders
        self._resolve_env_vars(self._config)
        logger.info(f"Loaded configuration from {self.config_path}")

    def _resolve_env_vars(self, data: Any):
        """Recursively replace ${VAR} placeholders with environment variables."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    data[key] = os.getenv(env_var, value)
                elif isinstance(value, (dict, list)):
                    self._resolve_env_vars(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and item.startswith("${") and item.endswith("}"):
                    env_var = item[2:-1]
                    data[i] = os.getenv(env_var, item)
                elif isinstance(item, (dict, list)):
                    self._resolve_env_vars(item)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    @property
    def database_path(self) -> str:
        """Get database path."""
        return self.get('paths.database', './data/tracks.db')

    @property
    def tracks_directory(self) -> str:
        """Get tracks directory."""
        return self.get('paths.tracks_directory', './Tracks')

    @property
    def embeddings_cache(self) -> str:
        """Get embeddings cache directory."""
        return self.get('paths.embeddings_cache', './data/embeddings')

    @property
    def notion_api_token(self) -> Optional[str]:
        """Get Notion API token."""
        return self.get('notion.api_token')

    @property
    def embedding_model_name(self) -> str:
        """Get embedding model name."""
        return self.get('embeddings.model_name', 'sentence-transformers/all-MiniLM-L6-v2')

    @property
    def min_similarity(self) -> float:
        """Get minimum similarity threshold."""
        return self.get('matching.min_similarity', 0.6)

    @property
    def bpm_tolerance(self) -> float:
        """Get BPM tolerance."""
        return self.get('matching.bpm_tolerance', 10.0)

    @property
    def scoring_weights(self) -> Dict[str, float]:
        """Get scoring weights."""
        return self.get('matching.weights', {
            'similarity': 0.50,
            'arc_bonus': 0.20,
            'bpm_proximity': 0.15,
            'key_compatibility': 0.10,
            'usage_penalty': 0.05
        })

    @property
    def target_duration(self) -> int:
        """Get default target duration in minutes."""
        return self.get('tracks.target_duration', 180)

    @property
    def songs_per_arc(self) -> int:
        """Get default songs per arc."""
        return self.get('tracks.songs_per_arc', 11)


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: str = "./config/settings.yaml") -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
