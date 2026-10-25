#!/usr/bin/env bash
# C2 cast test: every view as a PNG sequence, then an H.264 clip per view (renders/c2/cast_<view>.mp4).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
CERT=${CERT:-renders/c1/certificate_v04}
W=${W:-1280} H=${H:-720} SAMPLES=${SAMPLES:-24} FRAMES=${FRAMES:-96}
for v in ${VIEWS:-wide progress prudence mercury cherubs}; do
  blender -b --factory-startup --python scenes/blender/c2_cast_test.py -- "$CERT" "renders/c2/frames_cast_$v" "$W" "$H" "$SAMPLES" "$v" "$FRAMES" > "renders/c2/render_$v.log" 2>&1
  ffmpeg -y -loglevel error -framerate 24 -i "renders/c2/frames_cast_$v/f_%04d.png" -c:v libx264 -crf 16 -pix_fmt yuv420p "renders/c2/cast_$v.mp4"
  echo "$v done $(date +%T)"
done
