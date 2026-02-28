#!/usr/bin/env bash
# =============================================================================
# HoneyAegis Session Video Converter
# Converts Cowrie ttylog recordings to MP4 or GIF
#
# Usage:
#   ./scripts/video_converter.sh <ttylog_file> <output_file> [format]
#
#   format: mp4 (default) or gif
#
# Requirements: Python 3, ffmpeg
# =============================================================================
set -euo pipefail

TTYLOG="${1:?Usage: video_converter.sh <ttylog_file> <output_file> [format]}"
OUTPUT="${2:?Usage: video_converter.sh <ttylog_file> <output_file> [format]}"
FORMAT="${3:-mp4}"

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "[*] Converting ttylog to asciicast..."

# Convert ttylog (ttyrec format) to asciicast v2 using Python
python3 -c "
import struct
import json
import sys

ttylog_path = sys.argv[1]
output_path = sys.argv[2]

events = []
with open(ttylog_path, 'rb') as f:
    first_sec = None
    while True:
        header = f.read(12)
        if len(header) < 12:
            break
        sec, usec, length = struct.unpack('<III', header)
        data = f.read(length)
        if len(data) < length:
            break
        if first_sec is None:
            first_sec = sec + usec / 1_000_000
        offset = (sec + usec / 1_000_000) - first_sec
        text = data.decode('utf-8', errors='replace')
        events.append([round(offset, 6), 'o', text])

duration = events[-1][0] if events else 0

with open(output_path, 'w') as f:
    header = {'version': 2, 'width': 120, 'height': 36, 'duration': duration}
    f.write(json.dumps(header) + '\n')
    for event in events:
        f.write(json.dumps(event) + '\n')

print(f'Converted {len(events)} frames, duration: {duration:.1f}s')
" "$TTYLOG" "$TEMP_DIR/recording.cast"

ASCIICAST="$TEMP_DIR/recording.cast"

echo "[*] Rendering to SVG frames..."

# Use agg (asciinema gif generator) if available, otherwise use a text-based approach
if command -v agg >/dev/null 2>&1; then
    if [ "$FORMAT" = "gif" ]; then
        echo "[*] Using agg to create GIF..."
        agg "$ASCIICAST" "$OUTPUT"
        echo "[+] GIF saved to $OUTPUT"
        exit 0
    fi
fi

# Fallback: use Python + SVG rendering + ffmpeg
echo "[*] Rendering via ffmpeg..."

# Generate a simple terminal-style video using ffmpeg with text overlay
python3 -c "
import json
import sys
import os

cast_path = sys.argv[1]
frames_dir = sys.argv[2]

with open(cast_path, 'r') as f:
    lines = f.readlines()

header = json.loads(lines[0])
events = [json.loads(line) for line in lines[1:] if line.strip()]

# Build frame snapshots at 10fps
fps = 10
duration = header.get('duration', events[-1][0] if events else 0)
total_frames = int(duration * fps) + 1

screen_text = ''
event_idx = 0

for frame_num in range(total_frames):
    current_time = frame_num / fps
    while event_idx < len(events) and events[event_idx][0] <= current_time:
        screen_text += events[event_idx][2]
        event_idx += 1

    # Keep last 36 lines
    display_lines = screen_text.split('\n')[-36:]
    frame_text = '\n'.join(display_lines)

    with open(os.path.join(frames_dir, f'frame_{frame_num:06d}.txt'), 'w') as f:
        f.write(frame_text)

print(f'Generated {total_frames} frames at {fps}fps')
" "$ASCIICAST" "$TEMP_DIR"

# Create a simple video by converting text frames to images via ffmpeg
# Use the lavfi text source for terminal-style rendering
DURATION=$(python3 -c "
import json
with open('$ASCIICAST') as f:
    h = json.loads(f.readline())
    print(h.get('duration', 10))
")

# Simple approach: create video from asciicast using drawtext
ffmpeg -y -f lavfi -i "color=c=black:s=1280x720:d=$DURATION:r=10" \
    -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:textfile=$TEMP_DIR/frame_000000.txt:fontcolor=green:fontsize=14:x=10:y=10" \
    -c:v libx264 -preset fast -crf 28 \
    "$TEMP_DIR/output.mp4" 2>/dev/null || true

if [ -f "$TEMP_DIR/output.mp4" ]; then
    if [ "$FORMAT" = "gif" ]; then
        echo "[*] Converting to GIF..."
        ffmpeg -y -i "$TEMP_DIR/output.mp4" \
            -vf "fps=5,scale=800:-1:flags=lanczos" \
            -loop 0 "$OUTPUT" 2>/dev/null
    else
        cp "$TEMP_DIR/output.mp4" "$OUTPUT"
    fi
    echo "[+] Video saved to $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
else
    # Ultimate fallback: just copy the asciicast file
    cp "$ASCIICAST" "${OUTPUT%.${FORMAT}}.cast"
    echo "[!] ffmpeg rendering failed. Asciicast saved instead."
    echo "[*] You can play it with: asciinema play ${OUTPUT%.${FORMAT}}.cast"
fi
