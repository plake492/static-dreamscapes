# 🧾 Static Dreamscapes — Metadata Schema

This schema defines how each song, phase, and mix is described and indexed for use by the AI agent. Metadata is stored as individual JSON files per phase and consolidated in `song_index.json`.

---

## 1. Individual Song Object

Example (stored in `/metadata/Phase_2_Flow_Focus.json`):

```json
{
  "id": "a02_05_city_dreams",
  "filename": "A_02_05-CityDreams.mp3",
  "title": "City Dreams",
  "phase": 2,
  "phase_name": "Flow Focus",
  "bpm": 84,
  "key": "A Minor",
  "duration_sec": 312,
  "mood_tags": ["rainy", "analog", "steady", "productive"],
  "theme": "Rainy Night Coding Desk",
  "used_in": ["Track_09_NeonArcadeMemories"],
  "ai_confidence": 0.94,
  "audio_features": {
    "energy": 0.53,
    "valence": 0.42,
    "warmth": 0.78,
    "analog_noise_level": 0.12
  },
  "file_path": "~/Dev/personal/ffmpeg-lofi/Arc_Library/Phase_2_Flow_Focus/Midtempo_Groove/A_02_05-CityDreams.mp3",
  "last_modified": "2025-10-28T18:35:00Z"
}
```

---

## 2. Phase-Level Metadata Files

Each phase file aggregates all songs belonging to that arc stage.

```json
{
  "phase": 2,
  "name": "Flow Focus",
  "description": "Midtempo synthwave and lo-fi beats for focused energy and momentum.",
  "songs": ["a02_05_city_dreams", "a02_07_steady_signal", "a02_09_analog_shift"]
}
```

These files are referenced by the AI agent to build structured playlists for rendering.

---

## 3. Global Song Index (`song_index.json`)

This file acts as a lookup table linking all track IDs to metadata locations.

```json
{
  "a01_01_rainy_after_hours": {
    "phase": 1,
    "path": "metadata/Phase_1_Calm_Intro.json"
  },
  "a02_05_city_dreams": {
    "phase": 2,
    "path": "metadata/Phase_2_Flow_Focus.json"
  }
}
```

---

## 4. Mix Metadata Object

Each finished mix also gets a metadata record summarizing source material, runtime, and composition decisions.

Example (stored in `/metadata/mixes/Track_09_Neon_Arcade.json`):

```json
{
  "track_number": 9,
  "title": "Neon Arcade Memories",
  "duration_sec": 10800,
  "phases": [
    {
      "phase": 1,
      "songs": ["a01_01_rainy_after_hours", "a01_02_sleepless_static"]
    },
    { "phase": 2, "songs": ["a02_05_city_dreams", "a02_07_steady_signal"] },
    { "phase": 3, "songs": ["a03_03_daylight_reflect"] },
    { "phase": 4, "songs": ["a04_06_twilight_static"] }
  ],
  "themes": ["Retro Nostalgia", "City Night", "Arcade Glow"],
  "rendered_output": "Rendered/Track_09_NeonArcadeMemories.mp3",
  "render_date": "2025-10-29T10:00:00Z",
  "ai_notes": {
    "mix_balance": "Good warm/cool ratio, smooth pacing",
    "suggested_improvements": "Add brighter Phase 3 element next iteration"
  }
}
```

---

## 5. AI Agent Interaction

| Function                  | File               | Operation                                      |
| :------------------------ | :----------------- | :--------------------------------------------- |
| **Register Song**         | `Phase_X.json`     | Append new entry and update `song_index.json`. |
| **Update Usage**          | `song_index.json`  | Increment usage count after each mix.          |
| **Query by Mood/Phase**   | `Phase_X.json`     | Retrieve list of matching songs.               |
| **Generate Mix Metadata** | `/metadata/mixes/` | Create summary after FFmpeg render.            |

---

## 6. Tag Standardization

| Tag Type    | Example Values                                                                                      |
| :---------- | :-------------------------------------------------------------------------------------------------- |
| `mood_tags` | `rainy`, `sunrise`, `focus`, `nostalgic`, `bright`, `reflective`, `vapor`, `analog`, `calm`, `flow` |
| `theme`     | `Winter Nights`, `Dawn Drive`, `Neon Arcade`, `City Signals`                                        |
| `phase`     | 1 = Calm Intro, 2 = Flow Focus, 3 = Uplift Clarity, 4 = Reflective Fade                             |

---

## 7. Versioning & Sync

- Each metadata file should include a `last_modified` timestamp.
- The agent periodically validates hashes between `/Arc_Library/` and `/metadata/`.
- Stale entries trigger an alert or automatic cleanup.

---

This schema ensures that the AI agent can quickly:

- Index all available songs.
- Retrieve compatible tracks by phase or mood.
- Assemble coherent 3-hour mixes that preserve arc logic and sonic continuity.
