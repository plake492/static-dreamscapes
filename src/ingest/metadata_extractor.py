"""Metadata extraction orchestrator."""

from pathlib import Path
from typing import List, Optional, Dict
import logging

from ..core.models import Song, Track, NotionTrackMetadata
from ..core.database import Database
from .filename_parser import FilenameParser
from .notion_parser import NotionParser
from .audio_analyzer import AudioAnalyzer

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Orchestrate metadata extraction from multiple sources."""

    def __init__(
        self,
        database: Database,
        notion_parser: Optional[NotionParser] = None,
        audio_analyzer: Optional[AudioAnalyzer] = None
    ):
        """
        Initialize metadata extractor.

        Args:
            database: Database instance
            notion_parser: Notion parser instance (creates new if None)
            audio_analyzer: Audio analyzer instance (creates new if None)
        """
        self.db = database
        self.notion_parser = notion_parser or NotionParser()
        self.audio_analyzer = audio_analyzer or AudioAnalyzer()
        self.filename_parser = FilenameParser()

    def import_track_from_notion(
        self,
        notion_url: str,
        songs_dir: Path,
        force_reanalyze: bool = False
    ) -> tuple[Track, List[Song]]:
        """
        Import a complete track from Notion doc and audio files.

        Args:
            notion_url: URL to Notion document
            songs_dir: Directory containing audio files
            force_reanalyze: Force re-analysis of existing songs

        Returns:
            Tuple of (Track, List[Song])
        """
        logger.info(f"Starting import for track: {notion_url}")

        # 1. Parse Notion document
        logger.info("Parsing Notion document...")
        notion_metadata = self.notion_parser.parse_notion_doc(notion_url)

        # 2. Extract track number and folder from path
        # Expected path format: "./Tracks/22/Songs" -> track_number=22, track_folder="Tracks/22"
        track_number, track_folder = self._extract_track_info_from_path(songs_dir)

        # 3. Create Track record
        track = self._create_track_from_notion(notion_metadata, track_number, track_folder)

        # Check if track already exists
        existing_track = self.db.get_track_by_notion_url(notion_url)
        if existing_track:
            logger.info(f"Track already exists in database: {existing_track.title}")
            track = existing_track
        else:
            self.db.insert_track(track)
            logger.info(f"Created track record: {track.title}")

        # 3. Scan for audio files
        logger.info(f"Scanning directory: {songs_dir}")
        audio_files = self.filename_parser.scan_directory(songs_dir, recursive=True)
        logger.info(f"Found {len(audio_files)} valid audio files")

        # 4. Process each audio file
        songs = []
        for i, audio_path in enumerate(audio_files, 1):
            logger.info(f"Processing file {i}/{len(audio_files)}: {audio_path.name}")

            try:
                song = self._process_audio_file(
                    audio_path=audio_path,
                    track=track,
                    notion_metadata=notion_metadata,
                    force_reanalyze=force_reanalyze
                )

                if song:
                    songs.append(song)

            except Exception as e:
                logger.error(f"Error processing {audio_path.name}: {e}")
                continue

        logger.info(f"Successfully imported {len(songs)} songs for track: {track.title}")

        return track, songs

    def _extract_track_info_from_path(self, songs_dir: Path) -> tuple[Optional[int], Optional[str]]:
        """
        Extract track number and folder from songs directory path.

        Args:
            songs_dir: Path to songs directory (e.g., "./Tracks/22/Songs")

        Returns:
            Tuple of (track_number, track_folder)
            Example: (22, "Tracks/22")
        """
        try:
            # Convert to absolute path and get parts
            parts = songs_dir.resolve().parts

            # Look for "Tracks" directory in the path
            for i, part in enumerate(parts):
                if part == "Tracks" and i + 1 < len(parts):
                    # Next part should be the track number
                    track_num_str = parts[i + 1]
                    try:
                        track_number = int(track_num_str)
                        # Build track folder path (e.g., "Tracks/22")
                        track_folder = f"Tracks/{track_num_str}"
                        logger.info(f"Extracted track info: number={track_number}, folder={track_folder}")
                        return track_number, track_folder
                    except ValueError:
                        logger.warning(f"Could not parse track number from path part: {track_num_str}")
                        return None, None

            logger.warning(f"Could not find Tracks directory in path: {songs_dir}")
            return None, None

        except Exception as e:
            logger.error(f"Error extracting track info from path {songs_dir}: {e}")
            return None, None

    def _create_track_from_notion(
        self,
        notion_metadata: NotionTrackMetadata,
        track_number: Optional[int] = None,
        track_folder: Optional[str] = None
    ) -> Track:
        """Create Track model from Notion metadata."""
        import json

        return Track(
            notion_url=notion_metadata.notion_url,
            title=notion_metadata.title,
            output_filename=notion_metadata.output_filename,
            upload_schedule=notion_metadata.upload_schedule,
            duration_target=notion_metadata.duration_target_minutes,
            overall_theme=notion_metadata.overall_theme,
            mood_arc=notion_metadata.mood_arc,
            vibe_description=notion_metadata.vibe_description,
            visible_hashtags=notion_metadata.visible_hashtags,
            hidden_tags=notion_metadata.hidden_tags,
            ctr_target=notion_metadata.ctr_target,
            retention_target=notion_metadata.retention_target,
            track_number=track_number,
            track_folder=track_folder,
            notion_content_json=json.dumps(notion_metadata.raw_notion_content) if notion_metadata.raw_notion_content else None
        )

    def _process_audio_file(
        self,
        audio_path: Path,
        track: Track,
        notion_metadata: NotionTrackMetadata,
        force_reanalyze: bool = False
    ) -> Optional[Song]:
        """
        Process single audio file.

        Args:
            audio_path: Path to audio file
            track: Track this song belongs to
            notion_metadata: Notion metadata for matching prompts
            force_reanalyze: Force re-analysis

        Returns:
            Song model or None if processing failed
        """
        # Check if song already exists
        existing_song = self.db.get_song_by_filename(audio_path.name)
        if existing_song and not force_reanalyze:
            logger.debug(f"Song already in database: {audio_path.name}")
            return existing_song

        # Parse filename
        components = self.filename_parser.parse(audio_path.name)
        if not components:
            logger.warning(f"Could not parse filename: {audio_path.name}")
            return None

        # Find matching prompt from Notion
        prompt_info = self._find_matching_prompt(components, notion_metadata)

        # Analyze audio
        audio_analysis = self.audio_analyzer.analyze(audio_path)

        # Build combined text for embedding
        combined_text = self._build_combined_text(components, prompt_info, track, audio_analysis)

        # Extract vibe tags and mood keywords
        vibe_tags, mood_keywords = self._extract_tags_and_moods(prompt_info)

        # Create Song model
        song = Song(
            filename=audio_path.name,
            file_path=str(audio_path.absolute()),
            arc_number=components.arc_number,
            prompt_number=components.prompt_number,
            song_number=components.song_number,
            order_marker=components.order_marker,
            track_id=track.id,
            track_title=track.title,
            arc_name=prompt_info.get('arc_name'),
            arc_phase=components.arc_number,
            prompt_text=prompt_info.get('prompt_text'),
            anchor_phrase=prompt_info.get('anchor_phrase'),
            duration_seconds=audio_analysis.duration_seconds,
            bpm=audio_analysis.bpm,
            key=audio_analysis.key,
            energy_level=audio_analysis.energy_level,
            tempo_category=audio_analysis.tempo_category,
            vibe_tags=vibe_tags,
            mood_keywords=mood_keywords,
            combined_text=combined_text
        )

        # Insert into database
        if existing_song:
            # Update existing
            logger.info(f"Updating existing song: {song.filename}")
            # Note: We should implement an update method, but for now just log
        else:
            self.db.insert_song(song)
            logger.debug(f"Inserted song: {song.filename}")

        return song

    def _find_matching_prompt(
        self,
        components: 'FilenameComponents',
        notion_metadata: NotionTrackMetadata
    ) -> Dict:
        """Find matching prompt from Notion metadata."""
        result = {}

        # Find matching arc
        for arc in notion_metadata.arcs:
            if arc.arc_number == components.arc_number:
                result['arc_name'] = arc.arc_name

                # Find matching prompt
                for prompt in arc.prompts:
                    if prompt.prompt_number == components.prompt_number:
                        result['prompt_text'] = prompt.prompt_text
                        result['anchor_phrase'] = prompt.anchor_phrase
                        result['tempo_hints'] = prompt.tempo_hints
                        result['instrument_hints'] = prompt.instrument_hints
                        result['vibe_hints'] = prompt.vibe_hints
                        break

                break

        return result

    def _build_combined_text(
        self,
        components: 'FilenameComponents',
        prompt_info: Dict,
        track: Track,
        audio_analysis: 'AudioAnalysis'
    ) -> str:
        """Build combined text for embedding generation."""
        parts = []

        # Prompt text (highest priority)
        if prompt_info.get('prompt_text'):
            parts.append(prompt_info['prompt_text'])

        # Arc info
        if prompt_info.get('arc_name'):
            parts.append(f"Arc: {prompt_info['arc_name']}")

        # Track theme
        parts.append(f"Track: {track.overall_theme}")

        # Tempo
        if audio_analysis.tempo_category:
            parts.append(f"Tempo: {audio_analysis.tempo_category.value}")

        # BPM
        if audio_analysis.bpm:
            parts.append(f"BPM: {audio_analysis.bpm:.0f}")

        # Vibe hints
        if prompt_info.get('vibe_hints'):
            parts.append(f"Vibes: {', '.join(prompt_info['vibe_hints'])}")

        return " | ".join(parts)

    def _extract_tags_and_moods(self, prompt_info: Dict) -> tuple[List[str], List[str]]:
        """Extract vibe tags and mood keywords from prompt info."""
        vibe_tags = prompt_info.get('vibe_hints', [])
        mood_keywords = []

        # Combine tempo and instrument hints as mood keywords
        mood_keywords.extend(prompt_info.get('tempo_hints', []))
        mood_keywords.extend(prompt_info.get('instrument_hints', []))

        return vibe_tags, mood_keywords
