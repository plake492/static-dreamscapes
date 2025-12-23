"""Pydantic data models for the LoFi Track Manager system."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class TempoCategory(str, Enum):
    """Tempo categories for songs."""
    VERY_SLOW = "very_slow"      # < 60 BPM
    SLOW = "slow"                 # 60-80 BPM
    MID_TEMPO = "mid_tempo"       # 80-110 BPM
    UPBEAT = "upbeat"             # 110-140 BPM
    FAST = "fast"                 # > 140 BPM


class TrackStatus(str, Enum):
    """Status of a track."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    READY_TO_RENDER = "ready_to_render"
    RENDERED = "rendered"
    PUBLISHED = "published"


# ============================================================================
# FILENAME COMPONENTS
# ============================================================================

class FilenameComponents(BaseModel):
    """Parsed components from filename like '2_6_19a.mp3'."""
    arc_number: int = Field(..., ge=1, le=4, description="Arc number (1-4)")
    prompt_number: int = Field(..., ge=1, description="Prompt number within arc")
    song_number: int = Field(..., ge=1, description="Unique song identifier")
    order_marker: str = Field(..., min_length=1, max_length=2, description="Ordering marker (a, b, c, etc)")
    original_filename: str = Field(..., description="Original filename")

    @field_validator('order_marker')
    @classmethod
    def validate_order_marker(cls, v: str) -> str:
        if not v.isalpha():
            raise ValueError("Order marker must be alphabetic")
        return v.lower()


# ============================================================================
# AUDIO ANALYSIS
# ============================================================================

class AudioAnalysis(BaseModel):
    """Results from audio analysis (librosa)."""
    duration_seconds: float = Field(..., gt=0)
    bpm: Optional[float] = Field(None, ge=30, le=200, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key (e.g., 'C minor')")
    energy_level: Optional[float] = Field(None, ge=0, le=1, description="Energy level 0-1")
    tempo_category: Optional[TempoCategory] = None
    spectral_centroid: Optional[float] = None
    zero_crossing_rate: Optional[float] = None

    @staticmethod
    def tempo_category_from_bpm(bpm: float) -> TempoCategory:
        """Determine tempo category from BPM."""
        if bpm < 60:
            return TempoCategory.VERY_SLOW
        elif bpm < 80:
            return TempoCategory.SLOW
        elif bpm < 110:
            return TempoCategory.MID_TEMPO
        elif bpm < 140:
            return TempoCategory.UPBEAT
        else:
            return TempoCategory.FAST


# ============================================================================
# NOTION PARSING
# ============================================================================

class NotionPrompt(BaseModel):
    """A single Suno prompt from Notion doc."""
    prompt_number: int = Field(..., description="Sequential number in the arc")
    prompt_text: str = Field(..., min_length=10, description="Full Suno prompt text")
    anchor_phrase: str = Field(..., description="Common anchor phrase")
    completed: bool = Field(default=False, description="Checkbox state in Notion")

    tempo_hints: List[str] = Field(default_factory=list)
    instrument_hints: List[str] = Field(default_factory=list)
    vibe_hints: List[str] = Field(default_factory=list)


class NotionArc(BaseModel):
    """One of 4 arcs in a track."""
    arc_number: int = Field(..., ge=1, le=4)
    arc_name: str = Field(..., description="e.g., 'VHS Static Haze'")
    description: Optional[str] = None
    prompts: List[NotionPrompt] = Field(..., min_length=1)
    target_duration_minutes: Optional[int] = None

    @property
    def prompt_count(self) -> int:
        return len(self.prompts)


class NotionTrackMetadata(BaseModel):
    """Parsed metadata from a Notion track document."""
    notion_url: str
    title: str = Field(..., description="Full track title")
    output_filename: str = Field(..., description="Filename for final video")
    upload_schedule: Optional[str] = None
    duration_target_minutes: int = Field(default=180)

    overall_theme: str
    mood_arc: Optional[str] = None
    vibe_description: Optional[str] = None

    visible_hashtags: List[str] = Field(default_factory=list)
    hidden_tags: List[str] = Field(default_factory=list)

    ctr_target: Optional[str] = None
    retention_target: Optional[str] = None

    arcs: List[NotionArc] = Field(..., min_length=1, max_length=4)

    raw_notion_content: Optional[Dict[str, Any]] = None


# ============================================================================
# SONG DATABASE MODEL
# ============================================================================

class Song(BaseModel):
    """Complete song metadata - mirrors database schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_path: str

    # Parsed from filename
    arc_number: Optional[int] = None
    prompt_number: Optional[int] = None
    song_number: Optional[int] = None
    order_marker: Optional[str] = None

    # From Notion doc
    track_id: Optional[str] = None
    track_title: Optional[str] = None
    arc_name: Optional[str] = None
    arc_phase: Optional[int] = Field(None, ge=1, le=4)
    prompt_text: Optional[str] = None
    anchor_phrase: Optional[str] = None

    # Audio analysis
    duration_seconds: Optional[float] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy_level: Optional[float] = None
    tempo_category: Optional[TempoCategory] = None

    # For search
    vibe_tags: List[str] = Field(default_factory=list)
    mood_keywords: List[str] = Field(default_factory=list)
    combined_text: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    times_used: int = Field(default=0)

    # Usage tracking
    last_used_track_id: Optional[str] = Field(None, description="Track ID where song was last used")
    last_used_at: Optional[datetime] = Field(None, description="Timestamp of last usage")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @property
    def embedding_text(self) -> str:
        """Generate text for embedding if combined_text not set."""
        if self.combined_text:
            return self.combined_text

        parts = []
        if self.prompt_text:
            # Strip surrounding quotes for consistent embeddings
            clean_prompt = self.prompt_text.strip().strip('"').strip("'")
            parts.append(clean_prompt)
        if self.arc_name:
            parts.append(f"Arc: {self.arc_name}")
        if self.track_title:
            parts.append(f"Track: {self.track_title}")
        if self.vibe_tags:
            parts.append(f"Vibes: {', '.join(self.vibe_tags)}")
        if self.mood_keywords:
            parts.append(f"Mood: {', '.join(self.mood_keywords)}")

        return " | ".join(parts)


# ============================================================================
# TRACK DATABASE MODEL
# ============================================================================

class Track(BaseModel):
    """Complete track metadata - mirrors database schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    notion_url: str
    title: str
    output_filename: str
    upload_schedule: Optional[str] = None
    duration_target: int = Field(default=180)

    overall_theme: str
    mood_arc: Optional[str] = None
    vibe_description: Optional[str] = None

    visible_hashtags: List[str] = Field(default_factory=list)
    hidden_tags: List[str] = Field(default_factory=list)

    ctr_target: Optional[str] = None
    retention_target: Optional[str] = None

    # Track management
    track_number: Optional[int] = None
    track_folder: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: TrackStatus = Field(default=TrackStatus.DRAFT)

    rendered_at: Optional[datetime] = None
    youtube_url: Optional[str] = None

    notion_content_json: Optional[str] = None

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


# ============================================================================
# SEARCH & MATCHING
# ============================================================================

class SongMatch(BaseModel):
    """Result from similarity search."""
    song: Song
    similarity_score: float = Field(..., ge=0, le=1)
    arc_match_bonus: float = Field(default=0, ge=0, le=1)
    bpm_proximity: float = Field(default=0, ge=0, le=1)
    usage_penalty: float = Field(default=0, ge=0, le=1)
    final_score: float = Field(..., ge=0, le=1)

    @property
    def confidence_level(self) -> str:
        """Human-readable confidence."""
        if self.final_score >= 0.8:
            return "excellent"
        elif self.final_score >= 0.6:
            return "good"
        elif self.final_score >= 0.4:
            return "fair"
        else:
            return "poor"


class PlaylistSlot(BaseModel):
    """A slot in the generated playlist."""
    position: int
    arc_number: int
    arc_name: str

    existing_song: Optional[Song] = None
    match_info: Optional[SongMatch] = None

    needs_generation: bool = False
    suggested_prompt: Optional[str] = None
    target_bpm: Optional[float] = None
    target_key: Optional[str] = None


class GeneratedPlaylist(BaseModel):
    """Complete playlist for a track."""
    track_title: str
    track_id: str
    notion_url: str

    slots: List[PlaylistSlot] = Field(..., description="All slots in order")

    total_slots: int
    existing_songs_count: int
    songs_to_generate_count: int
    coverage_percentage: float = Field(..., ge=0, le=100)
    estimated_duration_minutes: float

    generated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    @property
    def is_complete(self) -> bool:
        """Can we generate video without creating new songs?"""
        return self.songs_to_generate_count == 0


# ============================================================================
# VIDEO GENERATION
# ============================================================================

class VideoGenerationResult(BaseModel):
    """Result of video generation."""
    success: bool
    output_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    error_message: Optional[str] = None

    songs_concatenated: int
    ffmpeg_command: Optional[str] = None
    generation_time_seconds: Optional[float] = None

    generated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


# ============================================================================
# TRACK MANIFEST (track.yaml)
# ============================================================================

class TrackManifest(BaseModel):
    """Track manifest stored in track.yaml."""
    track_id: str
    track_number: int
    title: str
    slug: str
    notion_url: str

    output_filename: str
    upload_schedule: Optional[str] = None

    overall_theme: str
    mood_arc: Optional[str] = None

    arcs: List[Dict[str, Any]] = Field(default_factory=list)

    status: TrackStatus = Field(default=TrackStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    songs_in_half_1: int = 0
    songs_in_half_2: int = 0
    total_songs: int = 0
    songs_from_bank: int = 0
    songs_newly_generated: int = 0

    video_loop: Optional[str] = None
    thumbnail: Optional[str] = None
    rendered_at: Optional[datetime] = None
    render_duration_seconds: Optional[float] = None

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
