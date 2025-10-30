# 🧠 Static Dreamscapes — System Overview

## Purpose

This system provides a structured framework for automating the production pipeline of the **Static Dreamscapes Lo‑Fi / Synthwave Channel**. It ensures continuity in sound and visual identity while enabling fast assembly of new mixes using an organized library of reusable tracks.

The AI agent’s responsibilities fall into two major domains:

1. **Organization** — Catalog and tag newly created songs according to emotional arc phases.
2. **Curation & Production** — Assemble new 3‑hour mixes from existing material following established arc structures, prepare metadata, and coordinate with shell scripts to render the final audio output.

---

## Goals

- Build a scalable, phase‑based library of Lo‑Fi/Synthwave tracks for consistent continuity across videos.
- Reduce dependence on per‑video credits by reusing internally created content.
- Maintain 3‑hour runtime precision through AI‑assisted track selection and crossfade automation.
- Preserve brand tone: analog warmth, nostalgic energy, and cinematic cohesion.

---

## System Components

| Component           | Description                                                                                                                                     |
| :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Arc Library**     | A curated collection of songs organized by emotional / structural phase. Each song carries metadata for phase, BPM, mood, key, and prior usage. |
| **Shell Scripts**   | Utility scripts that assist with track renaming, prefixing (A*, B*), and verifying total length for 3‑hour builds.                              |
| **FFmpeg Pipeline** | Performs automated concatenation, crossfades, and final render to a single `.mp3` or `.mp4`.                                                    |
| **AI Agent**        | A Node/Python‑based process that tags new tracks, recommends playlist compositions, and ensures arc integrity.                                  |
| **Metadata Files**  | JSON objects describing each song’s attributes, stored alongside audio assets for indexing and recall.                                          |

---

## Workflow Summary

1. **Track Generation**

   - New songs are created via AI or DAW and saved into a staging folder.
   - Shell scripts handle renaming, timestamp sorting, and prefix logic (`A_`, `B_`).

2. **Tagging**

   - AI agent analyzes each new song’s tonal/mood features and assigns phase category (1–4).
   - Metadata JSON created or updated accordingly.

3. **Curation**

   - AI agent selects 3–4 songs per phase to create a balanced 3‑hour arc.
   - Adjusts selections based on target runtime and desired theme (e.g., _Winter Nights_, _Dawn Drive_).

4. **Assembly & Rendering**

   - Selected songs are passed to shell scripts for order verification and prefix consistency.
   - FFmpeg merges files using preconfigured crossfade and normalization settings.

5. **Archival & Analytics**

   - Completed tracks are moved to `/Rendered/`.
   - Metadata updated to reflect new usage.
   - Optional performance analytics logged (CTR, retention, theme success).

---

## Future Capabilities

- Automated thumbnail selection based on phase/theme palette.
- Auto‑balancing of mix EQ and loudness normalization via FFmpeg filters.
- Smart sequencing that considers BPM/key matching.
- AI‑assisted discovery of new sonic gaps (underrepresented moods or tempos).

---

## Integration Map

```
/Dev/personal/ffmpeg-lofi
│
├── Arc_Library/          # Curated reusable tracks per phase
├── Mixes/                # Individual releases
├── backup_songs/         # Legacy stems
├── scripts/              # Helper shell utilities
├── agent/                # AI logic and config
├── metadata/             # Centralized track metadata JSONs
└── Rendered/             # Final exported mixes
```

The AI agent references all components under `/Arc_Library/` and `/metadata/` to plan each release cycle.
