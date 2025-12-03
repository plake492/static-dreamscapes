"""Database module for SQLite operations."""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import Song, Track, TrackStatus, TempoCategory

logger = logging.getLogger(__name__)


class Database:
    """SQLite database interface for the LoFi Track Manager."""

    def __init__(self, db_path: str = "./data/tracks.db"):
        """Initialize database connection."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        logger.info(f"Connected to database: {self.db_path}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def init_schema(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()

        # Songs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,
                filename TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,

                -- Parsed from filename
                arc_number INTEGER,
                prompt_number INTEGER,
                song_number INTEGER,
                order_marker TEXT,

                -- From Notion doc
                track_id TEXT,
                track_title TEXT,
                arc_name TEXT,
                arc_phase INTEGER,
                prompt_text TEXT,
                anchor_phrase TEXT,

                -- Audio analysis
                duration_seconds REAL,
                bpm REAL,
                key TEXT,
                energy_level REAL,
                tempo_category TEXT,

                -- For search
                vibe_tags TEXT,
                mood_keywords TEXT,
                combined_text TEXT,

                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                times_used INTEGER DEFAULT 0,

                FOREIGN KEY (track_id) REFERENCES tracks(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_arc_number ON songs(arc_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bpm ON songs(bpm)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_key ON songs(key)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_track_id ON songs(track_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename ON songs(filename)
        """)

        # Tracks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                notion_url TEXT UNIQUE,
                title TEXT NOT NULL,
                output_filename TEXT,
                upload_schedule TEXT,
                duration_target INTEGER DEFAULT 180,

                -- Theme/vibe
                overall_theme TEXT,
                mood_arc TEXT,
                vibe_description TEXT,

                -- SEO
                visible_hashtags TEXT,
                hidden_tags TEXT,

                -- Metrics targets
                ctr_target TEXT,
                retention_target TEXT,

                -- Track management
                track_number INTEGER,
                track_folder TEXT,

                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft',

                -- Rendering
                rendered_at TIMESTAMP,
                youtube_url TEXT,

                -- Cached notion content
                notion_content_json TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_track_number ON tracks(track_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tracks(status)
        """)

        self.conn.commit()
        logger.info("Database schema initialized")

    # ========================================================================
    # SONG OPERATIONS
    # ========================================================================

    def insert_song(self, song: Song) -> bool:
        """Insert a new song into the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO songs (
                    id, filename, file_path,
                    arc_number, prompt_number, song_number, order_marker,
                    track_id, track_title, arc_name, arc_phase, prompt_text, anchor_phrase,
                    duration_seconds, bpm, key, energy_level, tempo_category,
                    vibe_tags, mood_keywords, combined_text,
                    created_at, updated_at, times_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song.id, song.filename, song.file_path,
                song.arc_number, song.prompt_number, song.song_number, song.order_marker,
                song.track_id, song.track_title, song.arc_name, song.arc_phase,
                song.prompt_text, song.anchor_phrase,
                song.duration_seconds, song.bpm, song.key, song.energy_level,
                song.tempo_category.value if song.tempo_category else None,
                json.dumps(song.vibe_tags), json.dumps(song.mood_keywords), song.combined_text,
                song.created_at, song.updated_at, song.times_used
            ))
            self.conn.commit()
            logger.debug(f"Inserted song: {song.filename}")
            return True
        except sqlite3.IntegrityError as e:
            logger.warning(f"Song already exists: {song.filename}")
            return False
        except Exception as e:
            logger.error(f"Error inserting song: {e}")
            return False

    def get_song_by_id(self, song_id: str) -> Optional[Song]:
        """Retrieve a song by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        return self._row_to_song(row) if row else None

    def get_song_by_filename(self, filename: str) -> Optional[Song]:
        """Retrieve a song by filename."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM songs WHERE filename = ?", (filename,))
        row = cursor.fetchone()
        return self._row_to_song(row) if row else None

    def get_all_songs(self, limit: Optional[int] = None) -> List[Song]:
        """Retrieve all songs."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM songs ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        return [self._row_to_song(row) for row in cursor.fetchall()]

    def search_songs(
        self,
        arc_number: Optional[int] = None,
        bpm_min: Optional[float] = None,
        bpm_max: Optional[float] = None,
        tempo_category: Optional[TempoCategory] = None,
        limit: int = 100
    ) -> List[Song]:
        """Search songs with filters."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM songs WHERE 1=1"
        params = []

        if arc_number is not None:
            query += " AND arc_number = ?"
            params.append(arc_number)

        if bpm_min is not None:
            query += " AND bpm >= ?"
            params.append(bpm_min)

        if bpm_max is not None:
            query += " AND bpm <= ?"
            params.append(bpm_max)

        if tempo_category is not None:
            query += " AND tempo_category = ?"
            params.append(tempo_category.value)

        query += f" LIMIT {limit}"
        cursor.execute(query, params)
        return [self._row_to_song(row) for row in cursor.fetchall()]

    def update_song_usage(self, song_id: str):
        """Increment the times_used counter for a song."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE songs SET times_used = times_used + 1, updated_at = ?
            WHERE id = ?
        """, (datetime.now(), song_id))
        self.conn.commit()

    def _row_to_song(self, row: sqlite3.Row) -> Song:
        """Convert database row to Song model."""
        return Song(
            id=row['id'],
            filename=row['filename'],
            file_path=row['file_path'],
            arc_number=row['arc_number'],
            prompt_number=row['prompt_number'],
            song_number=row['song_number'],
            order_marker=row['order_marker'],
            track_id=row['track_id'],
            track_title=row['track_title'],
            arc_name=row['arc_name'],
            arc_phase=row['arc_phase'],
            prompt_text=row['prompt_text'],
            anchor_phrase=row['anchor_phrase'],
            duration_seconds=row['duration_seconds'],
            bpm=row['bpm'],
            key=row['key'],
            energy_level=row['energy_level'],
            tempo_category=TempoCategory(row['tempo_category']) if row['tempo_category'] else None,
            vibe_tags=json.loads(row['vibe_tags']) if row['vibe_tags'] else [],
            mood_keywords=json.loads(row['mood_keywords']) if row['mood_keywords'] else [],
            combined_text=row['combined_text'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now(),
            times_used=row['times_used'] or 0
        )

    # ========================================================================
    # TRACK OPERATIONS
    # ========================================================================

    def insert_track(self, track: Track) -> bool:
        """Insert a new track into the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO tracks (
                    id, notion_url, title, output_filename, upload_schedule, duration_target,
                    overall_theme, mood_arc, vibe_description,
                    visible_hashtags, hidden_tags,
                    ctr_target, retention_target,
                    track_number, track_folder,
                    created_at, updated_at, status,
                    rendered_at, youtube_url,
                    notion_content_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track.id, track.notion_url, track.title, track.output_filename,
                track.upload_schedule, track.duration_target,
                track.overall_theme, track.mood_arc, track.vibe_description,
                json.dumps(track.visible_hashtags), json.dumps(track.hidden_tags),
                track.ctr_target, track.retention_target,
                track.track_number, track.track_folder,
                track.created_at, track.updated_at, track.status.value,
                track.rendered_at, track.youtube_url,
                track.notion_content_json
            ))
            self.conn.commit()
            logger.debug(f"Inserted track: {track.title}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Track already exists: {track.notion_url}")
            return False
        except Exception as e:
            logger.error(f"Error inserting track: {e}")
            return False

    def get_track_by_id(self, track_id: str) -> Optional[Track]:
        """Retrieve a track by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE id = ?", (track_id,))
        row = cursor.fetchone()
        return self._row_to_track(row) if row else None

    def get_track_by_notion_url(self, notion_url: str) -> Optional[Track]:
        """Retrieve a track by Notion URL."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE notion_url = ?", (notion_url,))
        row = cursor.fetchone()
        return self._row_to_track(row) if row else None

    def get_track_by_number(self, track_number: int) -> Optional[Track]:
        """Retrieve a track by track number."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tracks WHERE track_number = ?", (track_number,))
        row = cursor.fetchone()
        return self._row_to_track(row) if row else None

    def get_all_tracks(self, status: Optional[TrackStatus] = None) -> List[Track]:
        """Retrieve all tracks, optionally filtered by status."""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM tracks WHERE status = ? ORDER BY created_at DESC", (status.value,))
        else:
            cursor.execute("SELECT * FROM tracks ORDER BY created_at DESC")
        return [self._row_to_track(row) for row in cursor.fetchall()]

    def update_track_status(self, track_id: str, status: TrackStatus):
        """Update track status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tracks SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status.value, datetime.now(), track_id))
        self.conn.commit()

    def _row_to_track(self, row: sqlite3.Row) -> Track:
        """Convert database row to Track model."""
        return Track(
            id=row['id'],
            notion_url=row['notion_url'],
            title=row['title'],
            output_filename=row['output_filename'],
            upload_schedule=row['upload_schedule'],
            duration_target=row['duration_target'],
            overall_theme=row['overall_theme'],
            mood_arc=row['mood_arc'],
            vibe_description=row['vibe_description'],
            visible_hashtags=json.loads(row['visible_hashtags']) if row['visible_hashtags'] else [],
            hidden_tags=json.loads(row['hidden_tags']) if row['hidden_tags'] else [],
            ctr_target=row['ctr_target'],
            retention_target=row['retention_target'],
            track_number=row['track_number'],
            track_folder=row['track_folder'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now(),
            status=TrackStatus(row['status']) if row['status'] else TrackStatus.DRAFT,
            rendered_at=datetime.fromisoformat(row['rendered_at']) if row['rendered_at'] else None,
            youtube_url=row['youtube_url'],
            notion_content_json=row['notion_content_json']
        )

    # ========================================================================
    # STATISTICS
    # ========================================================================

    def get_song_count(self) -> int:
        """Get total number of songs in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM songs")
        return cursor.fetchone()[0]

    def get_track_count(self) -> int:
        """Get total number of tracks in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tracks")
        return cursor.fetchone()[0]

    def get_most_used_songs(self, limit: int = 10) -> List[Song]:
        """Get most frequently used songs."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM songs
            WHERE times_used > 0
            ORDER BY times_used DESC
            LIMIT ?
        """, (limit,))
        return [self._row_to_song(row) for row in cursor.fetchall()]

    def get_unused_songs(self, limit: int = 10) -> List[Song]:
        """Get songs that have never been used."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM songs
            WHERE times_used = 0
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [self._row_to_song(row) for row in cursor.fetchall()]
