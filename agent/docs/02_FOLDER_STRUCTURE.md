# 📁 Static Dreamscapes — Folder Structure & Conventions

## Base Directory

Root: `~/Dev/personal/ffmpeg-lofi`

```
ffmpeg-lofi/
├── Arc_Library/             # Master track bank (sorted by arc phase)
│   ├── Phase_1_Calm_Intro/
│   │   ├── Ambient_Warmth/
│   │   ├── Early_Dawn/
│   │   └── Nostalgic_Haze/
│   ├── Phase_2_Flow_Focus/
│   │   ├── Midtempo_Groove/
│   │   ├── Analog_Pulse/
│   │   └── Deep_Work/
│   ├── Phase_3_Uplift_Clarity/
│   │   ├── Bright_Pads/
│   │   ├── Optimistic_Melodies/
│   │   └── Creative_Energy/
│   └── Phase_4_Reflective_Fade/
│       ├── Tape_Hiss/
│       ├── Vapor_Trails/
│       └── Closing_Ambience/
│
├── Mixes/                   # All released or WIP track folders
│   ├── 09_Neon_Arcade_Memories/
│   │   ├── Image/
│   │   ├── Songs/
│   │   └── Video/
│   ├── 10_Dawn_Drive/
│   ├── 11_Winter_Nights/
│   └── 12_City_Signals/
│
├── metadata/                # JSON metadata for each song
│   ├── Phase_1_Calm_Intro.json
│   ├── Phase_2_Flow_Focus.json
│   ├── Phase_3_Uplift_Clarity.json
│   ├── Phase_4_Reflective_Fade.json
│   └── song_index.json
│
├── scripts/                 # Shell utilities
│   ├── rename_by_mod_time.sh
│   ├── prepend_tracks.sh
│   ├── track_length_report.sh
│   ├── build_mix.sh         # Calls FFmpeg + crossfade logic
│   └── verify_length.sh
│
├── Rendered/                # Final exported audio/video
│   ├── Track_09_NeonArcade.mp3
│   ├── Track_10_DawnDrive.mp3
│   └── ...
│
└── backup_songs/            # Original generated stems
```

---

## File Naming Conventions

**Audio Tracks:**

```
<Prefix>_<ArcID>_<Index>-<ShortTitle>.mp3
```

**Example:**

```
A_02_05-CityDreams.mp3
```

| Segment      | Meaning                             |
| :----------- | :---------------------------------- |
| `A_` / `B_`  | Arc run-through (first/second pass) |
| `02`         | Arc phase ID                        |
| `05`         | Track index within phase            |
| `CityDreams` | Descriptive label                   |

**Rendered Output:**

```
<TrackNumber>_<ShortTitle>_LoFi_Synthwave_Mix.mp3
```

Example:

```
09_Neon_Arcade_Memories_LoFi_Synthwave_Mix.mp3
```

---

## Integration Notes

- Shell scripts handle sequencing and crossfade consistency.
- FFmpeg pulls from track order validated by prefixes (`A_` then `B_`).
- The AI agent monitors `/Arc_Library/` for new files and updates corresponding metadata.
- Song JSON entries are indexed by filename hash to prevent duplicates.

---

## Expected Automation Behavior

1. **File Import** → AI detects new `.mp3` additions.
2. **Metadata Lookup** → Checks if song exists in `song_index.json`.
3. **Classification** → Assigns Phase + Mood folders.
4. **Renaming** → Calls `rename_by_mod_time.sh` to enforce proper arc order.
5. **Length Verification** → Runs `track_length_report.sh` to confirm total time before rendering.
6. **Final Render** → `build_mix.sh` executes FFmpeg crossfades and saves result in `/Rendered/`.

---

## Example FFmpeg Command

```bash
ffmpeg -f concat -safe 0 -i input.txt \
-filter_complex \
"[0:a]afade=t=in:ss=0:d=5[a0]; [a0][1:a]acrossfade=d=3" \
-c:a mp3 -b:a 320k output.mp3
```

Where `input.txt` contains:

```
file 'A_01_01-RainyAfterHours.mp3'
file 'A_02_01-SleeplessStatic.mp3'
file 'A_03_01-NightDrive.mp3'
```

---

## Agent Interaction Points

- **Observe:** `/Arc_Library/` for new files.
- **Tag:** Write metadata JSON entries.
- **Assist:** Build `input.txt` lists for FFmpeg.
- **Verify:** Compare summed durations to 3-hour target.
- **Log:** Store summaries in `metadata/logs/` for each build.
