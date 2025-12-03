"""Embedding generation using sentence-transformers."""

from typing import List, Dict
from pathlib import Path
import logging
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available")

from ..core.models import Song, NotionPrompt
from ..core.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for songs and prompts using sentence-transformers."""

    def __init__(self, model_name: str = None):
        """
        Initialize embedding generator.

        Args:
            model_name: Model to use (if None, loads from config)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required. "
                "Install with: pip install sentence-transformers"
            )

        if model_name is None:
            config = get_config()
            model_name = config.embedding_model_name

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def generate_for_song(self, song: Song) -> np.ndarray:
        """
        Generate embedding for a song.

        Args:
            song: Song model

        Returns:
            Embedding vector (numpy array)
        """
        text = song.embedding_text
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,  # For cosine similarity
            show_progress_bar=False
        )
        return embedding

    def generate_for_songs_batch(self, songs: List[Song]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for multiple songs (batch processing).

        Args:
            songs: List of Song models

        Returns:
            Dictionary mapping song IDs to embeddings
        """
        logger.info(f"Generating embeddings for {len(songs)} songs")

        # Extract texts
        texts = [song.embedding_text for song in songs]

        # Generate embeddings in batch
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        )

        # Map to song IDs
        result = {
            song.id: embeddings[i]
            for i, song in enumerate(songs)
        }

        logger.info(f"Generated {len(result)} embeddings")
        return result

    def generate_for_prompt(
        self,
        prompt: NotionPrompt,
        arc_name: str,
        track_theme: str
    ) -> np.ndarray:
        """
        Generate embedding for a new track's prompt.

        Args:
            prompt: NotionPrompt model
            arc_name: Name of the arc
            track_theme: Overall track theme

        Returns:
            Embedding vector
        """
        # Build combined text
        text_parts = [
            prompt.prompt_text,
            f"Arc: {arc_name}",
            f"Theme: {track_theme}"
        ]

        if prompt.tempo_hints:
            text_parts.append(f"Tempo: {', '.join(prompt.tempo_hints)}")

        if prompt.vibe_hints:
            text_parts.append(f"Vibes: {', '.join(prompt.vibe_hints)}")

        combined_text = " | ".join(text_parts)

        # Generate embedding
        embedding = self.model.encode(
            combined_text,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embedding

    def generate_for_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for arbitrary text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding
