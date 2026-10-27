#!/usr/bin/env bash
# The 4K finals on the RTX 5090 box (config/render_profiles.json "final"), in three lanes run side by side:
#   graphics  the graphics layer at 3840x2160, every frame (scripts/render_graphics.py) -> renders/final/graphics
#   a         sections 1-3
#   b         the live plates (S26, S29, S31, S40), then sections 4-6
#   join      after all three: the sections joined, with the post-filtered preview mix -> deliverables/final_4k/
# A section is rendered to PNG frames, assembled to a ProRes 422 HQ intermediate (no captions, no audio), and once
# that holds every frame, its PNGs are removed: the disk can't hold all of them at once (about 12 MB a frame), and
# frame sequences regenerate from this script and are never archived (CLAUDE.md).
# Usage: scripts/final_queue.sh graphics|a|b|join   (progress in renders/final/logs/queue.log)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
LOG=renders/final/logs
mkdir -p "$LOG" renders/final/sections renders/final/tmp
W=3840 H=2160
SAMPLES=$(.venv/bin/python -I -c "import json; print(json.load(open('config/render_profiles.json'))['final']['samples'])")
FPS=24
HANDLE=0.5  # seconds of plate before and after each live shot, for the edit
MIX=audio/master/postfilter_preview/share_the_shares_postfilter_preview_mix.wav
OUT=deliverables/final_4k
PLATES=deliverables/live_plates

mark() { echo "$(date -Iseconds) $*" >> "$LOG/queue.log"; }
wait_for() { until grep -q "$1" "$LOG/queue.log" 2>/dev/null; do sleep 30; done; }

# section n -> "name from to" in song seconds (config/c5_sections.json on timing/timing_map.json's shot times)
section() {
  .venv/bin/python -I - "$1" <<'E'
import json, sys
tm = json.load(open("timing/timing_map.json"))
T = {s["id"]: s["t"] for s in tm["shots"] if s["t"] is not None}
s = json.load(open("config/c5_sections.json"))["sections"][int(sys.argv[1]) - 1]
a = 0.0 if s["from"] == "start" else T[s["from"]]
b = tm["duration_s"] if s["to"] == "end" else T[s["to"]]
print(s["name"], a, b)
E
}

render_section() {
  local n=$1 name t0 t1
  read -r name t0 t1 < <(section "$n")
  local frames=renders/final/frames/s$n mov=renders/final/sections/final_${n}_${name}.mov
  mark "S${n}_START $name $t0-$t1"
  blender -b --factory-startup --python scenes/blender/animatic.py -- --out "$frames" --size $W $H \
    --samples "$SAMPLES" --step 1 --from "$t0" --to "$t1" > "$LOG/section$n.log" 2>&1
  mark "S${n}_RENDERED $(ls "$frames" | wc -l) frames"
  wait_for GRAPHICS_DONE
  .venv/bin/python -I scripts/animatic_assemble.py "$frames" 1 "$mov" --graphics renders/final/graphics \
    --from "$t0" $([ "$n" = 6 ] || echo --to "$t1") --captions none --master --no-audio --tmp renders/final/tmp \
    >> "$LOG/section$n.log" 2>&1
  # the intermediate must hold the section's every frame before its PNGs go
  local want got
  want=$(.venv/bin/python -I -c "
import json; tm = json.load(open('timing/timing_map.json'))
ph = json.load(open('config/c4_shots.json'))['placeholders']
v1 = $t1 + (sum(ph[i]['after_s'] for i in ('S45', 'S46', 'S47', 'S48')) if $n == 6 else 0)
print(round(v1 * $FPS) - round($t0 * $FPS))")
  got=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of csv=p=0 "$mov")
  if [ "$got" != "$want" ]; then mark "S${n}_FAILED $mov has $got frames, wants $want; PNGs kept"; exit 1; fi
  rm -r "$frames"
  mark "S${n}_DONE $mov ($got frames)"
}

plates() {
  mkdir -p "$PLATES"
  echo '{"_doc": "Flat plates of the whole sheet for the live shots (scripts/final_queue.sh): straight down, orthographic, at the print resolution (4400x3400, the sheet edge to edge). sheet: the whole certificate as rendered, figures moving; figures: the figures and props alone, on transparency. ProRes 4444 with alpha. first_frame_s: the video time of the first frame (song time; there is no pre-roll), including the handle before the shot.", "fps": 24, "plates": [' > "$PLATES/plates.json.tmp"
  local first=1
  for sid in S26 S29 S31 S40; do
    local t0 t1
    read -r t0 t1 < <(.venv/bin/python -I -c "
import json; tm = json.load(open('timing/timing_map.json')); S = [s for s in tm['shots'] if s['t'] is not None]
k = [s['id'] for s in S].index('$sid'); print(S[k]['t'], S[k + 1]['t'])")
    local a b
    a=$(.venv/bin/python -I -c "print(f'{max(0, $t0 - $HANDLE):.3f}')")
    b=$(.venv/bin/python -I -c "print(f'{$t1 + $HANDLE:.3f}')")
    for pass in sheet figures; do
      local dir=renders/final/plates/${sid}_$pass
      mark "PLATE_START $sid $pass $a-$b"
      blender -b --factory-startup --python scenes/blender/animatic.py -- --out "$dir" --size 4400 3400 \
        --samples "$SAMPLES" --step 1 --flat $([ $pass = figures ] && echo --figures-only) --from "$a" --to "$b" \
        > "$LOG/plate_${sid}_$pass.log" 2>&1
      ffmpeg -v error -y -framerate $FPS -pattern_type glob -i "$dir/f_*.png" -c:v prores_ks -profile:v 4 \
        -vendor apl0 -pix_fmt yuva444p10le -alpha_bits 16 "$PLATES/${sid}_$pass.mov"
      mark "PLATE_DONE $sid $pass $(ls "$dir" | wc -l) frames"
    done
    local f0
    f0=$(ls renders/final/plates/${sid}_sheet | head -1 | sed 's/f_0*\([0-9]*\).png/\1/')
    [ $first = 1 ] || echo ',' >> "$PLATES/plates.json.tmp"
    first=0
    printf ' {"shot": "%s", "shot_s": [%s, %s], "first_frame_s": %s, "files": ["%s_sheet.mov", "%s_figures.mov"]}' \
      "$sid" "$t0" "$t1" "$(.venv/bin/python -I -c "print(round(${f0:-0} / $FPS, 3))")" "$sid" "$sid" >> "$PLATES/plates.json.tmp"
  done
  echo ']}' >> "$PLATES/plates.json.tmp"
  .venv/bin/python -I -c "import json,sys; d=json.load(open(sys.argv[1])); json.dump(d, open(sys.argv[2], 'w'), indent=1)" \
    "$PLATES/plates.json.tmp" "$PLATES/plates.json"
  rm "$PLATES/plates.json.tmp"
  mark PLATES_DONE
}

case "${1:-}" in
  graphics)
    mark GRAPHICS_START
    .venv/bin/python -I scripts/render_graphics.py $W $H 1 renders/final/graphics > "$LOG/graphics.log" 2>&1
    # S30's "Post-filter: no change" tab, alone with its alpha, for the human's live take
    mkdir -p "$PLATES"
    ffmpeg -v error -y -framerate $FPS -i renders/final/graphics/postfilter/%05d.png -c:v prores_ks -profile:v 4 \
      -vendor apl0 -pix_fmt yuva444p10le -alpha_bits 16 "$PLATES/S30_postfilter_tab.mov"
    mark GRAPHICS_DONE
    ;;
  a) for n in 1 2 3; do render_section $n; done; mark LANE_A_DONE ;;
  b) plates; for n in 4 5 6; do render_section $n; done; mark LANE_B_DONE ;;
  join)
    wait_for LANE_A_DONE; wait_for LANE_B_DONE
    mkdir -p "$OUT"
    ls renders/final/sections/final_*.mov | sort -t_ -k2n | sed "s|^|file '$PWD/|; s|$|'|" > renders/final/tmp/concat.txt
    ffmpeg -v error -y -f concat -safe 0 -i renders/final/tmp/concat.txt -i "$MIX" -map 0:v -map 1:a -c:v copy \
      -c:a pcm_s24le -shortest "$OUT/share_the_shares_4k_postfilter_preview.mov"
    # a light copy to listen to: 1080p H.264, AAC 320k
    ffmpeg -v error -y -i "$OUT/share_the_shares_4k_postfilter_preview.mov" -vf scale=1920:1080:flags=lanczos \
      -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 320k "$OUT/share_the_shares_1080p_postfilter_preview.mp4"
    mark JOIN_DONE
    ;;
  *) echo "usage: $0 graphics|a|b|join" >&2; exit 2 ;;
esac
