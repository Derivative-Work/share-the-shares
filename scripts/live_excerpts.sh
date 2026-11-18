#!/usr/bin/env bash
# The two files the screen recording plays (brief rev 50, "The screen recording": "Play the actual final render, so
# the music in the recording is real playback"), cut from the 4K master and sent in the Claude Code session that made
# it, so the session reveal (S29) shows the real file in the real conversation:
#   share_the_shares_chorus2.mp4         a lead-in, the second chorus (S25) through S26's flicker to the downbeat
#                                          after it (S29), where the file ends: the player exits and the music stops
#   share_the_shares_bridge_on.mp4       from "And it's real" (S31), where the file is reopened and the music comes
#                                          back mid-phrase, through S40's swipe to the call and back, with a tail
# H.264 High at 2560x1440 (the Mac's screen; the edit cuts to the master itself after S31's zoom), AAC 256k.
# Usage: scripts/live_excerpts.sh   ->  deliverables/live_excerpts/ (+ excerpts.json: each file's song-time span)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
M=deliverables/final_4k/share_the_shares_4k_postfilter_preview.mov
OUT=deliverables/live_excerpts
mkdir -p "$OUT"
t() { .venv/bin/python -I -c "
import json; tm = json.load(open('timing/timing_map.json')); print({s['id']: s['t'] for s in tm['shots'] if s['t'] is not None}['$1'])"; }
LEAD=3.0   # before S25, so the chorus doesn't start the instant play is pressed
TAIL=3.0   # after S41's cut back to the render
A0=$(.venv/bin/python -I -c "print(round($(t S25) - $LEAD, 3))"); A1=$(t S30)
B0=$(t S31); B1=$(.venv/bin/python -I -c "print(round($(t S41) + $TAIL, 3))")
cut() {  # name from to [fade-out]
  ffmpeg -v error -y -ss "$2" -to "$3" -i "$M" -vf scale=2560:1440:flags=lanczos -c:v libx264 -profile:v high \
    -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k ${4:+-af afade=t=out:st=$(.venv/bin/python -I -c "print($3 - $2 - $4)"):d=$4} \
    -movflags +faststart "$OUT/$1"
}
cut share_the_shares_chorus2.mp4 "$A0" "$A1"          # ends on the downbeat: no fade, the music stops there
cut share_the_shares_bridge_on.mp4 "$B0" "$B1" 0.5     # its tail is never used: a short fade so it doesn't click off
cat > "$OUT/excerpts.json" <<E
{"_doc": "The files the screen recording plays (scripts/live_excerpts.sh): song-time spans in the master (song time = video time).",
 "share_the_shares_chorus2.mp4": {"from_s": $A0, "to_s": $A1, "covers": "S25 (from $LEAD s before it) to S29's end, the downbeat"},
 "share_the_shares_bridge_on.mp4": {"from_s": $B0, "to_s": $B1, "covers": "S31 to S41 + $TAIL s (S40, the swipe to the call, inside)"}}
E
for f in "$OUT"/*.mp4; do
  echo "$f $(ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$f")"
done
# The session's file upload takes at most 30 MiB: a two-pass copy under that, same name, in sendable/ (the name shows
# on screen). Only the bridge file needs it (the chorus is 21 MiB).
mkdir -p "$OUT/sendable"
for f in "$OUT"/*.mp4; do
  [ "$(stat -c %s "$f")" -gt 29000000 ] || continue
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  vb=$(.venv/bin/python -I -c "print(int((27.5 * 8 * 1048576 / $d - 192000) / 1000))")k   # 27.5 MiB minus the audio
  P=$(mktemp -d)
  ffmpeg -v error -y -i "$f" -c:v libx264 -profile:v high -preset slow -b:v $vb -pass 1 -passlogfile "$P/p" -an -f null /dev/null
  ffmpeg -v error -y -i "$f" -c:v libx264 -profile:v high -preset slow -b:v $vb -pass 2 -passlogfile "$P/p" -pix_fmt yuv420p \
    -c:a aac -b:a 192k -movflags +faststart "$OUT/sendable/$(basename "$f")"
  rm -rf "$P"
  echo "$OUT/sendable/$(basename "$f") $(stat -c %s "$OUT/sendable/$(basename "$f")") bytes, video $vb"
done
