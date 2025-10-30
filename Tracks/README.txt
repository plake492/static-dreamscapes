This directory structure is for build_mix.sh which expects:
- Tracks/<track_number>/Video/<track_number>.mp4
- Tracks/<track_number>/Songs/*.mp3

Example:
  Tracks/5/Video/5.mp4
  Tracks/5/Songs/01_track1.mp3
  Tracks/5/Songs/02_track2.mp3

Note: The automated pipeline (orchestrator.py) works with Arc_Library instead.
This Tracks/ structure is for manual video+audio rendering only.
