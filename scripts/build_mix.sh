#!/bin/bash

# Check if track number argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <track_number> [duration]"
    echo "Examples:"
    echo "  $0 5           # Use total duration of all songs (default)"
    echo "  $0 5 0.5       # 30 minutes (0.5 hours)"
    echo "  $0 5 1         # 1 hour"
    echo "  $0 5 2         # 2 hours"
    echo "  $0 5 test      # 5 minutes for testing"
    echo ""
    echo "This will process tracks/5/video/5.mp4 and tracks/5/songs/"
    exit 1
fi

TRACK_NUM="$1"
DURATION_ARG="${2:-auto}"  # Default to auto (use total song duration)

# Validate that the track number is numeric
if ! [[ "$TRACK_NUM" =~ ^[0-9]+$ ]]; then
    echo "Error: Track number must be a numeric value"
    echo "Usage: $0 <track_number> [duration]"
    exit 1
fi

# Create timestamped output folder
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="rendered/${TRACK_NUM}/output_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# Input values (using the provided track number)
BG_VIDEO="tracks/${TRACK_NUM}/video/${TRACK_NUM}.mp4"
SONG_DIR="tracks/${TRACK_NUM}/songs"
OUTPUT="${OUTPUT_DIR}/output.mp4"

# Check if required files exist
if [ ! -f "$BG_VIDEO" ]; then
    echo "Error: Background video not found: $BG_VIDEO"
    exit 1
fi

if [ ! -d "$SONG_DIR" ]; then
    echo "Error: Songs directory not found: $SONG_DIR"
    exit 1
fi

echo "Processing Track $TRACK_NUM"
echo "Background video: $BG_VIDEO"
echo "Songs directory: $SONG_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Find all mp3 files in the song directory, sorted alphabetically
# The null delimiter is used to handle filenames with spaces or special characters
SONGS=()
SONG_DURATIONS=()

# Create a temporary file to store the file list
temp_songs=$(mktemp)
find "$SONG_DIR" -name "*.mp3" -print0 | sort -z > "$temp_songs"

while IFS= read -r -d $'\0'; do
    SONGS+=("$REPLY")
    # Get the actual duration of each song using ffprobe
    duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$REPLY")
    # Round to integer seconds
    duration_int=$(printf "%.0f" "$duration")
    SONG_DURATIONS+=("$duration_int")
done < "$temp_songs"

# Clean up temporary file
rm -f "$temp_songs"

# Check if songs were found
if [ ${#SONGS[@]} -eq 0 ]; then
    echo "No mp3 files found in $SONG_DIR"
    exit 1
fi

# Calculate total duration of all songs
TOTAL_SONGS_DURATION=0
for i in "${!SONGS[@]}"; do
    song_dur=${SONG_DURATIONS[$i]}
    TOTAL_SONGS_DURATION=$((TOTAL_SONGS_DURATION + song_dur))
done

# Calculate duration in seconds based on the argument
if [ "$DURATION_ARG" = "test" ]; then
    DURATION=300      # 5 minutes for testing
    echo "Duration: 5 minutes (test mode)"
elif [ "$DURATION_ARG" = "auto" ]; then
    DURATION=$TOTAL_SONGS_DURATION
    hours=$((DURATION / 3600))
    minutes=$(( (DURATION % 3600) / 60 ))
    seconds=$((DURATION % 60))
    echo "Duration: ${hours}h ${minutes}m ${seconds}s (total songs duration: ${DURATION} seconds)"
elif [[ "$DURATION_ARG" =~ ^[0-9]*\.?[0-9]+$ ]]; then
    # Convert hours to seconds (multiply by 3600)
    DURATION=$(echo "$DURATION_ARG * 3600" | bc)
    DURATION=${DURATION%.*}  # Remove decimal part if any
    hours_display=$(echo "scale=1; $DURATION_ARG" | bc)
    echo "Duration: ${hours_display} hours (${DURATION} seconds)"
else
    echo "Error: Duration must be a number (in hours) or 'test'"
    echo "Examples: 0.5 (30 min), 1 (1 hour), 2 (2 hours), test (5 min)"
    exit 1
fi
echo ""
FADEOUT_START=410   # fade out starts 10 seconds before end
FADEOUT_DUR=10      # fade-out duration
XFADE_DUR=3         # crossfade overlap duration (seconds)
SONG_FADEOUT_START=5 # start fading out this many seconds before song ends (should be >= XFADE_DUR)
VOLUME_BOOST=1.75    # Volume multiplier (1.0 = no change, 2.0 = double volume)

# --- Build the ffmpeg command ---

# Start with the base command and the background video input
ffmpeg_args=(-y -stream_loop -1 -i "$BG_VIDEO")

# Add each song as an input
for song in "${SONGS[@]}"; do
    ffmpeg_args+=(-i "$song")
done

# --- Build the filter_complex string ---

# Calculate total duration of one pass through all songs
total_sequence_duration=0
for i in "${!SONGS[@]}"; do
    song_dur=${SONG_DURATIONS[$i]}
    total_sequence_duration=$((total_sequence_duration + song_dur - SONG_FADEOUT_START))
done
# Add back the fadeout time from the last song
total_sequence_duration=$((total_sequence_duration + SONG_FADEOUT_START))

# Calculate how many times we need to repeat to exceed the target duration
num_repeats=$(( (DURATION / total_sequence_duration) + 2 ))

echo "Total sequence duration: ${total_sequence_duration}s"
echo "Will repeat sequence ${num_repeats} times to fill ${DURATION}s"

filter_complex=""
num_songs=${#SONGS[@]}

# Build the crossfade chain - each song crossfades with the next using acrossfade filter
# First, prepare all songs with volume boost
for repeat in $(seq 0 $((num_repeats - 1))); do
    for i in "${!SONGS[@]}"; do
        stream_index=$((i + 1))
        song_dur=${SONG_DURATIONS[$i]}
        
        filter_complex+="[${stream_index}:a]volume=${VOLUME_BOOST},aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a${stream_index}_r${repeat}];"
    done
done

# Now chain crossfades together
# Start with the first song
previous_label="a1_r0"
crossfade_label=""

segment_count=0
for repeat in $(seq 0 $((num_repeats - 1))); do
    for i in "${!SONGS[@]}"; do
        stream_index=$((i + 1))
        song_dur=${SONG_DURATIONS[$i]}
        
        # Skip the very first song as it's already our starting point
        if [ $segment_count -eq 0 ]; then
            segment_count=$((segment_count + 1))
            continue
        fi
        
        current_input="a${stream_index}_r${repeat}"
        crossfade_label="xf${segment_count}"
        
        # Use acrossfade to create overlapping crossfade - both inputs before the filter
        filter_complex+="[${previous_label}][${current_input}]acrossfade=d=${SONG_FADEOUT_START}:c1=tri:c2=tri[${crossfade_label}];"
        previous_label="$crossfade_label"
        
        segment_count=$((segment_count + 1))
    done
done

# Trim to final duration and add final fades
filter_complex+="[${previous_label}]atrim=0:$DURATION,afade=t=in:st=0:d=3,afade=t=out:st=$((DURATION - FADEOUT_DUR)):d=$FADEOUT_DUR[a];"

# Scale the video and set the pixel format
filter_complex+="[0:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p[v]"

# Add the filter_complex to the ffmpeg arguments
ffmpeg_args+=(-filter_complex "$filter_complex")

# Map the final video and audio streams and set encoding options
ffmpeg_args+=(-map "[v]" -map "[a]" -c:v libx264 -c:a aac -b:a 192k -t "$DURATION" "$OUTPUT")

# --- Execute the ffmpeg command ---

# For debugging, uncomment the following line to see the full command
echo "ffmpeg ${ffmpeg_args[*]}" > "${OUTPUT_DIR}/ffmpeg_command.txt"
echo "Filter complex saved to ${OUTPUT_DIR}/filter_complex.txt"
echo "$filter_complex" > "${OUTPUT_DIR}/filter_complex.txt"

# Execute the command
ffmpeg "${ffmpeg_args[@]}"
