#!/usr/bin/env python3
"""
Build Mix (Python Version)
---------------------------
Build final video mix with background video and crossfaded audio from songs.
Python alternative to scripts/build_mix.sh with the same functionality.

Usage:
    python3 agent/build_mix.py --track 5                    # Auto duration (total songs)
    python3 agent/build_mix.py --track 5 --duration 0.5     # 30 minutes
    python3 agent/build_mix.py --track 5 --duration 1       # 1 hour
    python3 agent/build_mix.py --track 5 --duration 2       # 2 hours
    python3 agent/build_mix.py --track 5 --duration test    # 5 minutes
"""

import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
import sys

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TRACKS_DIR = PROJECT_ROOT / "tracks"
RENDERED_DIR = PROJECT_ROOT / "rendered"

# FFmpeg settings
FADEOUT_DUR = 10          # Final fade-out duration (seconds)
XFADE_DUR = 3             # Crossfade overlap duration (seconds)
SONG_FADEOUT_START = 5    # Start fading out this many seconds before song ends
VOLUME_BOOST = 1.75       # Volume multiplier (1.0 = no change, 2.0 = double)
FADE_IN_DUR = 3           # Initial fade-in duration (seconds)

def get_audio_duration(audio_file):
    """Get duration of an audio file in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_file)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        return int(round(duration))
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting duration for {audio_file}: {e}")
        return 0

def find_songs(songs_dir):
    """
    Find all MP3 files in the songs directory, sorted alphabetically.

    Returns:
        List of tuples: [(path, duration_in_seconds), ...]
    """
    if not songs_dir.exists():
        return []

    songs = sorted(songs_dir.glob("*.mp3"))
    songs_with_durations = []

    print(f"📊 Analyzing song durations...")
    for song in songs:
        duration = get_audio_duration(song)
        songs_with_durations.append((song, duration))
        print(f"   {song.name}: {duration}s")

    return songs_with_durations

def calculate_duration(duration_arg, total_songs_duration):
    """
    Calculate target duration in seconds based on argument.

    Args:
        duration_arg: "auto", "test", or number (hours as float)
        total_songs_duration: Total duration of all songs in seconds

    Returns:
        (duration_seconds, description_string)
    """
    if duration_arg == "test":
        return 300, "5 minutes (test mode)"
    elif duration_arg == "auto":
        hours = total_songs_duration // 3600
        minutes = (total_songs_duration % 3600) // 60
        seconds = total_songs_duration % 60
        desc = f"{hours}h {minutes}m {seconds}s (total songs duration: {total_songs_duration} seconds)"
        return total_songs_duration, desc
    else:
        # Convert hours to seconds
        try:
            hours_float = float(duration_arg)
            duration_seconds = int(hours_float * 3600)
            desc = f"{hours_float} hours ({duration_seconds} seconds)"
            return duration_seconds, desc
        except ValueError:
            raise ValueError(f"Invalid duration: {duration_arg}")

def build_filter_complex(songs_with_durations, target_duration):
    """
    Build the FFmpeg filter_complex string for crossfading songs.

    Args:
        songs_with_durations: List of (path, duration) tuples
        target_duration: Target duration in seconds

    Returns:
        filter_complex string
    """
    num_songs = len(songs_with_durations)

    # Calculate total duration of one pass through all songs
    total_sequence_duration = sum(
        duration - SONG_FADEOUT_START
        for _, duration in songs_with_durations
    ) + SONG_FADEOUT_START  # Add back the fadeout time from last song

    # Calculate how many times we need to repeat to exceed target duration
    num_repeats = (target_duration // total_sequence_duration) + 2

    print(f"\n📐 Filter complex calculation:")
    print(f"   Total sequence duration: {total_sequence_duration}s")
    print(f"   Will repeat sequence {num_repeats} times to fill {target_duration}s")

    filter_parts = []

    # First, prepare all songs with volume boost for each repeat
    for repeat in range(num_repeats):
        for i, (song, duration) in enumerate(songs_with_durations):
            stream_index = i + 1  # Stream 0 is video, audio starts at 1
            label = f"a{stream_index}_r{repeat}"

            filter_parts.append(
                f"[{stream_index}:a]volume={VOLUME_BOOST},"
                f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[{label}]"
            )

    # Now chain crossfades together
    previous_label = "a1_r0"
    segment_count = 0

    for repeat in range(num_repeats):
        for i, (song, duration) in enumerate(songs_with_durations):
            stream_index = i + 1

            # Skip the very first song as it's already our starting point
            if segment_count == 0:
                segment_count += 1
                continue

            current_input = f"a{stream_index}_r{repeat}"
            crossfade_label = f"xf{segment_count}"

            # Use acrossfade to create overlapping crossfade
            filter_parts.append(
                f"[{previous_label}][{current_input}]"
                f"acrossfade=d={SONG_FADEOUT_START}:c1=tri:c2=tri[{crossfade_label}]"
            )

            previous_label = crossfade_label
            segment_count += 1

    # Trim to final duration and add final fades
    filter_parts.append(
        f"[{previous_label}]atrim=0:{target_duration},"
        f"afade=t=in:st=0:d={FADE_IN_DUR},"
        f"afade=t=out:st={target_duration - FADEOUT_DUR}:d={FADEOUT_DUR}[a]"
    )

    # Scale the video and set the pixel format
    filter_parts.append(
        "[0:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p[v]"
    )

    return ";".join(filter_parts)

def build_mix(track_number, duration_arg="auto"):
    """
    Build the final video mix with FFmpeg.

    Args:
        track_number: Track number to build
        duration_arg: "auto", "test", or duration in hours (float)

    Returns:
        Path to output file, or None on failure
    """
    track_folder = TRACKS_DIR / str(track_number)
    video_file = track_folder / "video" / f"{track_number}.mp4"
    songs_dir = track_folder / "songs"

    # Validate inputs
    if not video_file.exists():
        print(f"❌ Error: Background video not found: {video_file}")
        return None

    if not songs_dir.exists():
        print(f"❌ Error: Songs directory not found: {songs_dir}")
        return None

    # Find songs
    songs_with_durations = find_songs(songs_dir)

    if not songs_with_durations:
        print(f"❌ Error: No MP3 files found in {songs_dir}")
        return None

    # Calculate total songs duration
    total_songs_duration = sum(duration for _, duration in songs_with_durations)

    # Calculate target duration
    try:
        target_duration, duration_desc = calculate_duration(duration_arg, total_songs_duration)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print(f"   Duration must be a number (in hours), 'auto', or 'test'")
        print(f"   Examples: 0.5 (30 min), 1 (1 hour), 2 (2 hours), test (5 min)")
        return None

    # Create timestamped output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = RENDERED_DIR / str(track_number) / f"output_{timestamp}"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "output.mp4"

    print(f"\n🎬 Building Track {track_number}")
    print(f"   Background video: {video_file.name}")
    print(f"   Songs directory: {songs_dir}")
    print(f"   Number of songs: {len(songs_with_durations)}")
    print(f"   Total songs duration: {total_songs_duration}s")
    print(f"   Target duration: {duration_desc}")
    print(f"   Output: {output_folder}")

    # Build filter complex
    filter_complex = build_filter_complex(songs_with_durations, target_duration)

    # Save filter complex for debugging
    filter_file = output_folder / "filter_complex.txt"
    with open(filter_file, 'w') as f:
        f.write(filter_complex)
    print(f"\n   ✓ Filter complex saved: {filter_file}")

    # Build FFmpeg command
    ffmpeg_args = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-stream_loop", "-1",  # Loop video infinitely
        "-i", str(video_file)  # Input: background video
    ]

    # Add each song as an input
    for song, _ in songs_with_durations:
        ffmpeg_args.extend(["-i", str(song)])

    # Add filter complex
    ffmpeg_args.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]",  # Map video output
        "-map", "[a]",  # Map audio output
        "-c:v", "libx264",  # Video codec
        "-c:a", "aac",  # Audio codec
        "-b:a", "192k",  # Audio bitrate
        "-t", str(target_duration),  # Duration
        str(output_file)
    ])

    # Save command for debugging
    command_file = output_folder / "ffmpeg_command.txt"
    with open(command_file, 'w') as f:
        f.write(" ".join(ffmpeg_args))
    print(f"   ✓ FFmpeg command saved: {command_file}")

    # Execute FFmpeg
    print(f"\n🎥 Running FFmpeg...")
    print(f"   (This may take a while...)")

    try:
        subprocess.run(ffmpeg_args, check=True)
        print(f"\n✅ Build complete!")
        print(f"   Output: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FFmpeg error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Build video mix with crossfaded audio (Python version)"
    )
    parser.add_argument(
        '--track',
        type=int,
        required=True,
        help='Track number to build'
    )
    parser.add_argument(
        '--duration',
        default='auto',
        help='Duration: auto (default), test (5 min), or hours (e.g., 1, 2, 3)'
    )

    args = parser.parse_args()

    # Validate track exists
    track_folder = TRACKS_DIR / str(args.track)
    if not track_folder.exists():
        print(f"❌ Error: Track {args.track} does not exist")
        print(f"   Create it first: ./venv/bin/python3 agent/create_track_template.py")
        sys.exit(1)

    # Build mix
    result = build_mix(args.track, args.duration)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
