"""Embedding storage and similarity search."""

from typing import List, Tuple, Dict, Optional
from pathlib import Path
import pickle
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ..core.models import Song
from ..core.config import get_config

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """Store and search embeddings using numpy and cosine similarity."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize embedding store.

        Args:
            cache_dir: Directory for caching embeddings (if None, loads from config)
        """
        if cache_dir is None:
            config = get_config()
            cache_dir = config.embeddings_cache

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage
        self.embeddings: List[Tuple[str, np.ndarray]] = []  # (song_id, embedding)
        self.song_map: Dict[str, Song] = {}  # song_id -> Song

        logger.info(f"Initialized embedding store with cache: {self.cache_dir}")

    def add_song(self, song: Song, embedding: np.ndarray):
        """
        Add a song and its embedding to the store.

        Args:
            song: Song model
            embedding: Embedding vector
        """
        # Check if already exists
        for i, (existing_id, _) in enumerate(self.embeddings):
            if existing_id == song.id:
                # Update existing
                self.embeddings[i] = (song.id, embedding)
                self.song_map[song.id] = song
                return

        # Add new
        self.embeddings.append((song.id, embedding))
        self.song_map[song.id] = song
        logger.debug(f"Added embedding for song: {song.filename}")

    def add_songs_batch(self, songs: List[Song], embeddings: Dict[str, np.ndarray]):
        """
        Add multiple songs and embeddings.

        Args:
            songs: List of Song models
            embeddings: Dictionary mapping song IDs to embeddings
        """
        for song in songs:
            if song.id in embeddings:
                self.add_song(song, embeddings[song.id])

        logger.info(f"Added {len(songs)} songs to embedding store")

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 20,
        min_similarity: float = 0.0
    ) -> List[Tuple[Song, float]]:
        """
        Search for most similar songs.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of (Song, similarity_score) tuples, sorted by score descending
        """
        if not self.embeddings:
            logger.warning("Embedding store is empty")
            return []

        # Extract all embeddings
        song_ids = [sid for sid, _ in self.embeddings]
        embedding_matrix = np.array([emb for _, emb in self.embeddings])

        # Compute cosine similarity
        query_embedding = query_embedding.reshape(1, -1)
        similarities = cosine_similarity(query_embedding, embedding_matrix)[0]

        # Filter by minimum similarity
        valid_indices = np.where(similarities >= min_similarity)[0]

        if len(valid_indices) == 0:
            logger.warning(f"No embeddings above similarity threshold {min_similarity}")
            return []

        # Get top K indices
        valid_similarities = similarities[valid_indices]
        sorted_indices = np.argsort(valid_similarities)[::-1][:top_k]

        # Map back to original indices
        top_indices = valid_indices[sorted_indices]

        # Return songs with scores
        results = [
            (self.song_map[song_ids[idx]], float(similarities[idx]))
            for idx in top_indices
        ]

        logger.debug(f"Found {len(results)} similar songs (top_k={top_k})")
        return results

    def get_song_count(self) -> int:
        """Get number of songs in the store."""
        return len(self.embeddings)

    def clear(self):
        """Clear all embeddings from the store."""
        self.embeddings = []
        self.song_map = {}
        logger.info("Cleared embedding store")

    def save(self, filepath: Optional[Path] = None):
        """
        Save embeddings to disk.

        Args:
            filepath: Path to save file (if None, uses default cache location)
        """
        if filepath is None:
            filepath = self.cache_dir / "embeddings.pkl"

        data = {
            'embeddings': self.embeddings,
            'song_map': self.song_map
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        logger.info(f"Saved {len(self.embeddings)} embeddings to {filepath}")

    def load(self, filepath: Optional[Path] = None) -> bool:
        """
        Load embeddings from disk.

        Args:
            filepath: Path to load file (if None, uses default cache location)

        Returns:
            True if loaded successfully, False otherwise
        """
        if filepath is None:
            filepath = self.cache_dir / "embeddings.pkl"

        if not filepath.exists():
            logger.warning(f"Embedding cache file not found: {filepath}")
            return False

        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            self.embeddings = data['embeddings']
            self.song_map = data['song_map']

            logger.info(f"Loaded {len(self.embeddings)} embeddings from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load embeddings from {filepath}: {e}")
            return False

    def get_embedding_by_song_id(self, song_id: str) -> Optional[np.ndarray]:
        """Get embedding for a specific song ID."""
        for sid, embedding in self.embeddings:
            if sid == song_id:
                return embedding
        return None

    def get_statistics(self) -> Dict:
        """Get statistics about the embedding store."""
        if not self.embeddings:
            return {
                'total_songs': 0,
                'embedding_dimension': 0
            }

        # Get embedding dimension from first embedding
        _, first_embedding = self.embeddings[0]

        return {
            'total_songs': len(self.embeddings),
            'embedding_dimension': first_embedding.shape[0]
        }
