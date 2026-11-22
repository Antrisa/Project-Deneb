#!/bin/sh
# Convert the title screen's .mp4 clips to Ogg Theora for Godot (it plays no other video format).
#   sh tools/dev/encode_intro.sh path/to/01_opening.mp4 path/to/02_station_loop.mp4   (run from the repo root)
# - Quality 10, Theora's best.
# - One keyframe per clip, on its first frame. Every keyframe throws the compression noise away and starts
#   it afresh, which shows as a flicker over the whole picture. ffmpeg's default of a keyframe every
#   12 frames made the picture "fizz" five times a second; a keyframe every 5 s still blinked faintly
#   every 5 s. With one keyframe the only refresh comes when the loop restarts.
# - The clips are BT.709 video. Theora only has BT.601 colours, so they are converted on the way.
# - No sound track: the theme plays separately.
set -e
VF="scale=in_color_matrix=bt709:out_color_matrix=bt601:in_range=tv:out_range=tv,format=yuv420p"
encode() {
	frames=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$1")
	ffmpeg -y -i "$1" -an -vf "$VF" -c:v libtheora -q:v 10 -g "$frames" "$2"
}
encode "$1" title/intro/opening.ogv
encode "$2" title/intro/station_loop.ogv
