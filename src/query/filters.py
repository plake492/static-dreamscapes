"""Filtering system for song matching."""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

from ..core.models import Song, TempoCategory

logger = logging.getLogger(__name__)


@dataclass
class SearchFilters:
    """Filters for song matching."""

    # BPM matching
    target_bpm: Optional[float] = None
    bpm_tolerance: float = 10.0

    # Key matching
    preferred_key: Optional[str] = None

    # Tempo category
    tempo_category: Optional[TempoCategory] = None

    # Arc matching
    target_arc_number: Optional[int] = None

    # Duration constraints
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None

    # Usage limits
    max_times_used: Optional[int] = None


class SongFilter:
    """Apply filters to song candidates."""

    @staticmethod
    def apply_filters(
        candidates: List[Tuple[Song, float]],
        filters: SearchFilters
    ) -> List[Tuple[Song, float]]:
        """
        Apply all filters to candidate songs.

        Args:
            candidates: List of (Song, similarity_score) tuples
            filters: Filters to apply

        Returns:
            Filtered list of (Song, similarity_score) tuples
        """
        filtered = []

        for song, similarity in candidates:
            # BPM check
            if filters.target_bpm is not None and song.bpm is not None:
                bpm_diff = abs(song.bpm - filters.target_bpm)
                if bpm_diff > filters.bpm_tolerance:
                    continue

            # Tempo category check
            if filters.tempo_category is not None and song.tempo_category is not None:
                if song.tempo_category != filters.tempo_category:
                    # Allow adjacent categories
                    if not SongFilter._are_adjacent_tempos(song.tempo_category, filters.tempo_category):
                        continue

            # Duration check
            if filters.min_duration and song.duration_seconds:
                if song.duration_seconds < filters.min_duration:
                    continue

            if filters.max_duration and song.duration_seconds:
                if song.duration_seconds > filters.max_duration:
                    continue

            # Usage limit check
            if filters.max_times_used is not None:
                if song.times_used > filters.max_times_used:
                    continue

            # Passed all filters
            filtered.append((song, similarity))

        logger.debug(f"Filtered {len(candidates)} candidates to {len(filtered)}")
        return filtered

    @staticmethod
    def _are_adjacent_tempos(t1: TempoCategory, t2: TempoCategory) -> bool:
        """Check if two tempo categories are adjacent."""
        order = [
            TempoCategory.VERY_SLOW,
            TempoCategory.SLOW,
            TempoCategory.MID_TEMPO,
            TempoCategory.UPBEAT,
            TempoCategory.FAST
        ]

        try:
            idx1 = order.index(t1)
            idx2 = order.index(t2)
            return abs(idx1 - idx2) <= 1
        except ValueError:
            return False
