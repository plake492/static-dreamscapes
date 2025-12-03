"""Scoring algorithm for song matching."""

from typing import Optional, Dict
import logging
import numpy as np

from ..core.models import Song, SongMatch
from .filters import SearchFilters
from ..core.config import get_config

logger = logging.getLogger(__name__)


class SongScorer:
    """Compute final scores for song matches."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize scorer.

        Args:
            weights: Custom weights (if None, loads from config)
        """
        if weights is None:
            config = get_config()
            weights = config.scoring_weights

        self.similarity_weight = weights.get('similarity', 0.50)
        self.arc_bonus_weight = weights.get('arc_bonus', 0.20)
        self.bpm_weight = weights.get('bpm_proximity', 0.15)
        self.key_weight = weights.get('key_compatibility', 0.10)
        self.usage_penalty_weight = weights.get('usage_penalty', 0.05)

        # Validate weights sum to 1.0
        total = (
            self.similarity_weight +
            self.arc_bonus_weight +
            self.bpm_weight +
            self.key_weight +
            self.usage_penalty_weight
        )

        if abs(total - 1.0) > 0.01:
            logger.warning(f"Scoring weights sum to {total}, not 1.0. Normalizing...")
            norm_factor = 1.0 / total
            self.similarity_weight *= norm_factor
            self.arc_bonus_weight *= norm_factor
            self.bpm_weight *= norm_factor
            self.key_weight *= norm_factor
            self.usage_penalty_weight *= norm_factor

    def compute_final_score(
        self,
        song: Song,
        similarity_score: float,
        filters: SearchFilters
    ) -> SongMatch:
        """
        Compute comprehensive match score.

        Args:
            song: Song to score
            similarity_score: Embedding similarity (0-1)
            filters: Search filters with target values

        Returns:
            SongMatch with all score components
        """
        # 1. Semantic similarity (already 0-1)
        semantic_score = similarity_score

        # 2. Arc bonus (0-1)
        arc_bonus = self._compute_arc_bonus(song, filters)

        # 3. BPM proximity (0-1)
        bpm_proximity = self._compute_bpm_proximity(song, filters)

        # 4. Key compatibility (0-1)
        key_compat = self._compute_key_compatibility(song, filters)

        # 5. Usage penalty (0-1, inverted)
        usage_penalty = self._compute_usage_penalty(song)
        usage_score = 1.0 - usage_penalty

        # Compute weighted final score
        final_score = (
            self.similarity_weight * semantic_score +
            self.arc_bonus_weight * arc_bonus +
            self.bpm_weight * bpm_proximity +
            self.key_weight * key_compat +
            self.usage_penalty_weight * usage_score
        )

        return SongMatch(
            song=song,
            similarity_score=semantic_score,
            arc_match_bonus=arc_bonus,
            bpm_proximity=bpm_proximity,
            usage_penalty=usage_penalty,
            final_score=final_score
        )

    def _compute_arc_bonus(self, song: Song, filters: SearchFilters) -> float:
        """Compute arc matching bonus."""
        if filters.target_arc_number is None or song.arc_number is None:
            return 0.0

        if song.arc_number == filters.target_arc_number:
            return 1.0
        else:
            # Partial bonus for nearby arcs
            arc_diff = abs(song.arc_number - filters.target_arc_number)
            if arc_diff == 1:
                return 0.5
            else:
                return 0.0

    def _compute_bpm_proximity(self, song: Song, filters: SearchFilters) -> float:
        """Compute BPM proximity score."""
        if filters.target_bpm is None or song.bpm is None:
            return 0.0

        bpm_diff = abs(song.bpm - filters.target_bpm)

        # Linear falloff: 0 diff = 1.0, tolerance diff = 0.0
        bpm_proximity = max(0.0, 1.0 - (bpm_diff / filters.bpm_tolerance))

        return bpm_proximity

    def _compute_key_compatibility(self, song: Song, filters: SearchFilters) -> float:
        """Compute key compatibility score."""
        if filters.preferred_key is None or song.key is None:
            return 0.0

        song_key = song.key.lower()
        target_key = filters.preferred_key.lower()

        # Exact match
        if song_key == target_key:
            return 1.0

        # Compatible keys (simplified)
        if self._are_compatible_keys(song_key, target_key):
            return 0.5

        return 0.0

    def _compute_usage_penalty(self, song: Song) -> float:
        """Compute usage penalty (higher usage = higher penalty)."""
        if song.times_used == 0:
            return 0.0

        # Logarithmic penalty
        penalty = min(1.0, np.log1p(song.times_used) / np.log1p(10))
        return penalty

    def _are_compatible_keys(self, key1: str, key2: str) -> bool:
        """Check if two keys are musically compatible (simplified)."""
        # Parse keys
        note1, mode1 = self._parse_key(key1)
        note2, mode2 = self._parse_key(key2)

        # Parallel keys (e.g., C major and C minor)
        if note1 == note2:
            return True

        # Relative keys (e.g., C major and A minor)
        if self._are_relative_keys(note1, mode1, note2, mode2):
            return True

        # Perfect fifth (e.g., C and G)
        if self._is_perfect_fifth(note1, note2):
            return True

        return False

    def _parse_key(self, key: str) -> tuple[str, str]:
        """Parse 'C major' -> ('C', 'major')."""
        parts = key.split()
        note = parts[0] if parts else "C"
        mode = parts[1] if len(parts) > 1 else "major"
        return note, mode

    def _are_relative_keys(self, note1: str, mode1: str, note2: str, mode2: str) -> bool:
        """Check if keys are relative (e.g., C major and A minor)."""
        if mode1 == mode2:
            return False

        # Note mapping (simplified)
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        try:
            idx1 = notes.index(note1)
            idx2 = notes.index(note2)

            # Relative minor is 3 semitones down from major
            if mode1 == 'major' and mode2 == 'minor':
                return (idx1 - 3) % 12 == idx2
            elif mode1 == 'minor' and mode2 == 'major':
                return (idx2 - 3) % 12 == idx1

        except ValueError:
            return False

        return False

    def _is_perfect_fifth(self, note1: str, note2: str) -> bool:
        """Check if notes are a perfect fifth apart."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        try:
            idx1 = notes.index(note1)
            idx2 = notes.index(note2)

            # Perfect fifth is 7 semitones
            return abs(idx1 - idx2) % 12 == 7

        except ValueError:
            return False
