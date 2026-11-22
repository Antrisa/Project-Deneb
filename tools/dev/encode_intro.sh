#!/bin/sh
# Convert the title screen's .mp4 clips to Ogg Theora for Godot (it plays no other video format).
#   sh tools/dev/encode_intro.sh path/to/opening.mp4 path/to/station_loop.mp4
# Quality 10 (Theora's best) and a keyframe every 300 frames (5 s at 60 fps). ffmpeg's default is a
# keyframe every 12 frames: each one resets the compression noise, so the picture visibly "fizzes"
# five times a second. Long gaps between keyframes also make the files far smaller. No sound track.
set -e
ffmpeg -y -i "$1" -an -c:v libtheora -q:v 10 -g 300 -pix_fmt yuv420p title/intro/opening.ogv
ffmpeg -y -i "$2" -an -c:v libtheora -q:v 10 -g 300 -pix_fmt yuv420p title/intro/station_loop.ogv
