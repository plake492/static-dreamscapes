🔧 Script Name

rename_by_mod_time.sh

🗂️ Location

scripts/rename_by_mod_time.sh

🧠 Purpose

Sort all .mp3 files in /Arc_Library/ and rename them sequentially based on their modification time.
Ensures track order matches the order of creation/export from Suno, preserving intended arc flow.

⚙️ Execution Context

Called by: agent/orchestrator.py

When: Immediately after detecting new .mp3 files in /Arc_Library/

Prerequisites: All Suno tracks are fully downloaded.

Command:

bash scripts/rename_by_mod_time.sh

📥 Inputs
Name Type Description
/Arc_Library/Phase_X/ Folder Contains .mp3 tracks per arc phase
File modification time System attribute Used for chronological sort
📤 Outputs
Name Type Description
Renamed .mp3 files Files Renamed sequentially (e.g., 001_track.mp3, 002_track.mp3)
Log entries Text Added to logs/orchestrator.log
🪢 Dependencies

Uses bash, find, sort, and mv.

Must complete successfully before prepend_tracks.sh.

🧩 Agent Integration Notes

Return code 0 = success; otherwise, stop the pipeline.

Typical runtime: 2–4 seconds for 20–30 files.

🔧 Script Name

prepend_tracks.sh

🗂️ Location

scripts/prepend_tracks.sh

🧠 Purpose

Prepends phase identifiers (A* / B*) to filenames based on arc grouping.
Ensures consistent naming for later processing and visual organization of song order within the final 3-hour mix.

⚙️ Execution Context

Called by: agent/orchestrator.py

When: After rename_by_mod_time.sh

Prerequisites: Files must be already sorted and renamed chronologically.

Command:

bash scripts/prepend_tracks.sh

📥 Inputs
Name Type Description
/Arc*Library/Phase_X/ Folder Contains renamed .mp3 files
Arc mapping Internal rule e.g., first half = A*, second half = B\_
📤 Outputs
Name Type Description
Updated filenames Files e.g., A_001_track.mp3, B_002_track.mp3
Log entries Text Added to logs/orchestrator.log
🪢 Dependencies

Requires bash and mv.

Must run before analysis or render stages.

🧩 Agent Integration Notes

Return code 0 = success; otherwise halt pipeline.

Expected runtime: 1–2 seconds.

🔧 Script Name

track_length_report.sh

🗂️ Location

scripts/track_length_report.sh

🧠 Purpose

Analyzes all .mp3 files in /Arc_Library/ and calculates total duration.
Used to ensure cumulative runtime aligns with the target mix length (approximately 3 hours / 10,800 seconds).

⚙️ Execution Context

Called by: agent/orchestrator.py

When: After analyze_audio.py completes (metadata populated).

Prerequisites: All tracks are ready and named properly.

Command:

bash scripts/track_length_report.sh

📥 Inputs
Name Type Description
/Arc_Library/Phase_X/ Folder All processed .mp3 files
📤 Outputs
Name Type Description
total_length.txt File Contains total duration in seconds and formatted HH:MM:SS
Log entries Text Summary appended to logs/orchestrator.log
🪢 Dependencies

Requires bash, ffprobe (from FFmpeg), awk.

Must run before build_mix.sh.

🧩 Agent Integration Notes

Return code 0 = success; otherwise, stop and alert user.

Should confirm total duration within ±60 seconds of target 3h.

Expected runtime: 3–5 seconds depending on track count.

🔧 Script Name

build_mix.sh

🗂️ Location

scripts/build_mix.sh

🧠 Purpose

Combines all processed .mp3 tracks into a single continuous mix using FFmpeg.
Applies crossfades and ensures normalized audio levels for a professional, seamless listening experience.

⚙️ Execution Context

Called by: agent/orchestrator.py

When: After verifying track count and total length.

Prerequisites:

Metadata and naming complete.

Crossfade parameters defined in script or config.

Command:

bash scripts/build_mix.sh

📥 Inputs
Name Type Description
/Arc_Library/Phase_X/ Folder Final track list in play order
/metadata/song_index.json File Used to tag songs in the mix
Crossfade duration Variable Typically 2–3 seconds
📤 Outputs
Name Type Description
Rendered/Final_Mix.mp3 File 3-hour rendered mix
Rendered/final_mix.log File FFmpeg operation log
🪢 Dependencies

Requires FFmpeg with crossfade support.

Depends on all prior steps completing successfully.

🧩 Agent Integration Notes

Return code 0 = success; otherwise, pipeline stops and logs error.

Expected runtime: proportional to final mix duration (3h mix = ~2–3min render).

After completion, agent should trigger verify_length.sh or perform a duration check via FFprobe.

🧠 Agent Pipeline Summary
Step Script Purpose Continue on Fail
1 rename_by_mod_time.sh Sort and rename tracks by modified time ❌
2 prepend_tracks.sh Add phase prefixes ❌
3 analyze_audio.py Extract metadata for each track ✅
4 track_length_report.sh Verify cumulative duration ❌
5 build_mix.sh Render final audio mix ❌
