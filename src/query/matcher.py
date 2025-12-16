"""Semantic matcher orchestrator."""

from typing import List, Optional
import logging

from ..core.models import Song, SongMatch, NotionPrompt, NotionArc, NotionTrackMetadata, TempoCategory
from ..embeddings.generator import EmbeddingGenerator
from ..embeddings.store import EmbeddingStore
from .filters import SearchFilters, SongFilter
from .scorer import SongScorer
from ..core.config import get_config

logger = logging.getLogger(__name__)


class SongMatcher:
    """High-level matching orchestrator."""

    def __init__(
        self,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        embedding_store: Optional[EmbeddingStore] = None,
        scorer: Optional[SongScorer] = None
    ):
        """
        Initialize song matcher.

        Args:
            embedding_generator: EmbeddingGenerator instance (creates new if None)
            embedding_store: EmbeddingStore instance (creates new if None)
            scorer: SongScorer instance (creates new if None)
        """
        self.embeddings = embedding_generator or EmbeddingGenerator()
        self.store = embedding_store or EmbeddingStore()
        self.scorer = scorer or SongScorer()

        config = get_config()
        self.default_min_similarity = config.min_similarity
        self.default_bpm_tolerance = config.bpm_tolerance

    def find_matches_for_prompt(
        self,
        prompt: NotionPrompt,
        arc: NotionArc,
        track_metadata: NotionTrackMetadata,
        count: int = 5,
        min_similarity: Optional[float] = None
    ) -> List[SongMatch]:
        """
        Find best matching songs for a single prompt.

        Args:
            prompt: NotionPrompt to match
            arc: Arc this prompt belongs to
            track_metadata: Overall track metadata
            count: Number of matches to return
            min_similarity: Minimum similarity threshold (uses default if None)

        Returns:
            List of SongMatch objects, sorted by final score
        """
        if min_similarity is None:
            min_similarity = self.default_min_similarity

        logger.info(f"Finding matches for prompt {arc.arc_number}.{prompt.prompt_number}")

        # 1. Generate query embedding
        query_embedding = self.embeddings.generate_for_prompt(
            prompt=prompt,
            arc_name=arc.arc_name,
            track_theme=track_metadata.overall_theme
        )

        # 2. Semantic search (cast wide net)
        candidates = self.store.search(
            query_embedding,
            top_k=50,  # Get more than needed for filtering
            min_similarity=min_similarity * 0.8  # Slightly lower threshold for candidates
        )

        if not candidates:
            logger.warning(f"No candidates found for prompt {arc.arc_number}.{prompt.prompt_number}")
            return []

        logger.debug(f"Found {len(candidates)} candidates")

        # 3. Build filters based on prompt characteristics
        filters = self._build_filters_from_prompt(prompt, arc)

        # 4. Apply filters
        filtered = SongFilter.apply_filters(candidates, filters)

        if not filtered:
            logger.warning(f"No candidates passed filters for prompt {arc.arc_number}.{prompt.prompt_number}")
            return []

        logger.debug(f"{len(filtered)} candidates passed filters")

        # 5. Score and rank
        scored_matches = []
        for song, similarity in filtered:
            if similarity < min_similarity:
                continue

            match = self.scorer.compute_final_score(
                song=song,
                similarity_score=similarity,
                filters=filters
            )
            scored_matches.append(match)

        # 6. Sort by final score (highest first)
        scored_matches.sort(key=lambda m: m.final_score, reverse=True)

        # 7. Return top N
        top_matches = scored_matches[:count]

        logger.info(
            f"Found {len(top_matches)} matches for prompt {arc.arc_number}.{prompt.prompt_number} "
            f"(best score: {top_matches[0].final_score:.3f})" if top_matches else "Found 0 matches"
        )

        return top_matches

    def _build_filters_from_prompt(
        self,
        prompt: NotionPrompt,
        arc: NotionArc
    ) -> SearchFilters:
        """Infer filters from prompt characteristics."""

        # Infer BPM from tempo hints
        target_bpm = None
        tempo_category = None

        for hint in prompt.tempo_hints:
            if hint == 'very_slow':
                target_bpm = 50
                tempo_category = TempoCategory.VERY_SLOW
                break
            elif hint == 'slow':
                target_bpm = 70
                tempo_category = TempoCategory.SLOW
                break
            elif hint == 'mid_tempo':
                target_bpm = 95
                tempo_category = TempoCategory.MID_TEMPO
                break
            elif hint == 'upbeat':
                target_bpm = 120
                tempo_category = TempoCategory.UPBEAT
                break
            elif hint == 'fast':
                target_bpm = 150
                tempo_category = TempoCategory.FAST
                break

        # Also check prompt text directly for tempo keywords
        if target_bpm is None:
            text_lower = prompt.prompt_text.lower()
            if 'slow' in text_lower:
                target_bpm = 70
                tempo_category = TempoCategory.SLOW
            elif 'mid-tempo' in text_lower or 'mid tempo' in text_lower:
                target_bpm = 95
                tempo_category = TempoCategory.MID_TEMPO
            elif 'upbeat' in text_lower or 'energetic' in text_lower:
                target_bpm = 120
                tempo_category = TempoCategory.UPBEAT

        return SearchFilters(
            target_bpm=target_bpm,
            bpm_tolerance=self.default_bpm_tolerance,
            tempo_category=tempo_category,
            target_arc_number=arc.arc_number,
            min_duration=60,    # At least 1 minute
            max_duration=300,   # At most 5 minutes
            max_times_used=10   # Don't overuse songs
        )

    def get_statistics(self) -> dict:
        """Get matcher statistics."""
        store_stats = self.store.get_statistics()

        return {
            'total_songs_indexed': store_stats['total_songs'],
            'embedding_dimension': store_stats.get('embedding_dimension', 0),
            'min_similarity_threshold': self.default_min_similarity,
            'bpm_tolerance': self.default_bpm_tolerance
        }
