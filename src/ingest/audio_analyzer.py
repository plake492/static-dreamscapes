"""Audio analysis using librosa."""

from pathlib import Path
from typing import Optional
import logging
import json

try:
    import librosa
    import soundfile as sf
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logging.warning("librosa not available. Audio analysis will be limited.")

from ..core.models import AudioAnalysis, TempoCategory

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyze audio files to extract features like BPM, key, duration."""

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize audio analyzer.

        Args:
            cache_enabled: Cache analysis results to avoid reprocessing
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa is required for audio analysis. Install with: pip install librosa soundfile")

        self.cache_enabled = cache_enabled
        self.cache_dir = Path("./data/cache/audio_analysis")
        if cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, audio_path: Path) -> AudioAnalysis:
        """
        Analyze audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioAnalysis with extracted features
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Check cache
        if self.cache_enabled:
            cached = self._load_from_cache(audio_path)
            if cached:
                logger.debug(f"Loaded cached analysis for {audio_path.name}")
                return cached

        logger.info(f"Analyzing audio file: {audio_path.name}")

        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None, mono=True)

            # Duration
            duration_seconds = float(librosa.get_duration(y=y, sr=sr))

            # BPM detection
            bpm = self._detect_bpm(y, sr)

            # Key detection (simplified - can be improved)
            key = self._detect_key(y, sr)

            # Energy level
            energy_level = self._calculate_energy(y)

            # Tempo category
            tempo_category = None
            if bpm:
                tempo_category = AudioAnalysis.tempo_category_from_bpm(bpm)

            # Spectral features
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))

            analysis = AudioAnalysis(
                duration_seconds=duration_seconds,
                bpm=bpm,
                key=key,
                energy_level=energy_level,
                tempo_category=tempo_category,
                spectral_centroid=spectral_centroid,
                zero_crossing_rate=zero_crossing_rate
            )

            # Cache result
            if self.cache_enabled:
                self._save_to_cache(audio_path, analysis)

            logger.info(f"Analysis complete: {audio_path.name} | Duration: {duration_seconds:.1f}s | BPM: {bpm}")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {audio_path}: {e}")
            # Return basic analysis with just duration
            try:
                y, sr = librosa.load(str(audio_path), sr=None, mono=True)
                duration_seconds = float(librosa.get_duration(y=y, sr=sr))
                return AudioAnalysis(duration_seconds=duration_seconds)
            except:
                # Fallback to file metadata
                duration_seconds = self._get_duration_from_metadata(audio_path)
                return AudioAnalysis(duration_seconds=duration_seconds)

    def _detect_bpm(self, y: np.ndarray, sr: int) -> Optional[float]:
        """Detect BPM using beat tracking."""
        try:
            # Use onset strength for BPM detection
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

            # tempo is returned as numpy.float64
            bpm = float(tempo)

            # Validate BPM range
            if 30 <= bpm <= 200:
                return round(bpm, 1)
            else:
                logger.warning(f"Detected BPM {bpm} out of range, returning None")
                return None

        except Exception as e:
            logger.warning(f"BPM detection failed: {e}")
            return None

    def _detect_key(self, y: np.ndarray, sr: int) -> Optional[str]:
        """
        Detect musical key (simplified approach).

        This is a basic implementation. For better results, consider using
        specialized libraries like essentia or madmom.
        """
        try:
            # Get chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

            # Average across time
            chroma_mean = np.mean(chroma, axis=1)

            # Find dominant pitch class
            dominant_pitch = int(np.argmax(chroma_mean))

            # Map to note names
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note = note_names[dominant_pitch]

            # Simple major/minor detection based on energy distribution
            # This is very simplified and not highly accurate
            major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
            minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])

            # Rotate profiles to match detected key
            major_profile = np.roll(major_profile, dominant_pitch)
            minor_profile = np.roll(minor_profile, dominant_pitch)

            # Correlate with chroma
            major_corr = np.corrcoef(chroma_mean, major_profile)[0, 1]
            minor_corr = np.corrcoef(chroma_mean, minor_profile)[0, 1]

            mode = "major" if major_corr > minor_corr else "minor"

            return f"{note} {mode}"

        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            return None

    def _calculate_energy(self, y: np.ndarray) -> float:
        """Calculate overall energy level (RMS)."""
        try:
            rms = librosa.feature.rms(y=y)
            energy = float(np.mean(rms))

            # Normalize to 0-1 range (approximate)
            energy_normalized = min(1.0, energy * 10)  # Scale factor

            return round(energy_normalized, 3)

        except Exception as e:
            logger.warning(f"Energy calculation failed: {e}")
            return 0.5  # Default mid-energy

    def _get_duration_from_metadata(self, audio_path: Path) -> float:
        """Get duration from file metadata (fallback)."""
        try:
            if LIBROSA_AVAILABLE:
                # Use soundfile to get duration without loading entire file
                info = sf.info(str(audio_path))
                return float(info.duration)
            else:
                # Very rough estimate based on file size
                # This is not accurate but better than nothing
                file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                # Assume ~1 MB per minute for MP3 at 128kbps
                estimated_duration = file_size_mb * 60
                return estimated_duration

        except Exception as e:
            logger.error(f"Could not get duration from metadata: {e}")
            return 120.0  # Default 2 minutes

    def _load_from_cache(self, audio_path: Path) -> Optional[AudioAnalysis]:
        """Load cached analysis result."""
        cache_file = self.cache_dir / f"{audio_path.stem}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            # Convert tempo_category back to enum
            if data.get('tempo_category'):
                data['tempo_category'] = TempoCategory(data['tempo_category'])

            return AudioAnalysis(**data)

        except Exception as e:
            logger.warning(f"Failed to load cache for {audio_path.name}: {e}")
            return None

    def _save_to_cache(self, audio_path: Path, analysis: AudioAnalysis):
        """Save analysis result to cache."""
        cache_file = self.cache_dir / f"{audio_path.stem}.json"

        try:
            # Convert to dict
            data = analysis.model_dump()

            # Convert enum to string for JSON
            if data.get('tempo_category'):
                data['tempo_category'] = data['tempo_category'].value

            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved analysis cache: {cache_file}")

        except Exception as e:
            logger.warning(f"Failed to save cache for {audio_path.name}: {e}")


def analyze_audio(audio_path: Path, cache_enabled: bool = True) -> AudioAnalysis:
    """Convenience function for audio analysis."""
    analyzer = AudioAnalyzer(cache_enabled=cache_enabled)
    return analyzer.analyze(audio_path)
