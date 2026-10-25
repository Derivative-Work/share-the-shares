"""C3 timing preview: the timing map drawn against the Suno mix, for checking sync by ear.

960x540 at the video's fps. Lanes scroll right to left past a "now" line (3 s visible each side): drum hits (the
drum stem's onsets), every aligned word start, and the lead and choir vocal envelopes. Top: section, singer,
bar.beat (4/4; a bar that is not 4 beats is marked), key, the shot ID (it flashes at its cue), the beat square
(downbeats bright). Bottom: the line being sung, each word lighting at its aligned start. The key change and the
live verse's window (the human's take replaces it) are marked. Adapted from Not Yet's c3_preview.py.

Usage: .venv/bin/python -I scripts/c3_preview.py [start_s end_s]  ->  renders/c3/c3_preview.mp4
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TM = json.loads(Path("timing/timing_map.json").read_text())
LOOK = json.loads(Path("config/look.json").read_text())
P = LOOK["palette"]
FPS = TM["fps"]
W, H = 960, 540
SPAN = 3.0
NOW_X = W // 2
OUT = Path("renders/c3")
CAP = "assets/fonts/IMFeENrm28P.ttf"
SC = "assets/fonts/IMFeENsc28P.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BG, INK, GREEN, GOLD, DIM = "#1E1A16", P["paper"], "#6FA58C", P["ink_gold"], "#5A5248"


def rgb(h, k=1.0):
    h = h.lstrip("#")
    return tuple(min(255, int(int(h[i:i + 2], 16) * k)) for i in (0, 2, 4))


def main():
    t0, t1 = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) >= 3 else (0.0, TM["duration_s"])
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / ("c3_preview.mp4" if len(sys.argv) < 3 else f"c3_preview_{t0:.0f}-{t1:.0f}.mp4")
    beats = np.array(TM["beats"])
    down = set(TM["downbeat_beats"])
    bars = TM["bars"]
    drums = np.array(TM["drum_onsets"])
    words = np.array(sorted(w["start"] for ln in TM["lines"] for w in ln["words"]))
    env = {k: np.load(f"timing/envelopes/{k}.npy") for k in ("vocals", "backing")}
    shots = [s for s in TM["shots"] if s.get("t") is not None]
    keys = TM["keys"]
    live = TM["live_verse"]
    kc = TM["key_change"]
    lanes = [("drums", drums, GREEN), ("words", words, INK)]
    f_lab, f_cap, f_big = ImageFont.truetype(MONO, 13), ImageFont.truetype(CAP, 28), ImageFont.truetype(SC, 22)
    top, lane_h = 96, 44
    bg = Image.new("RGB", (W, H), rgb(BG))
    d0 = ImageDraw.Draw(bg)
    for k, (lab, _, col) in enumerate(lanes):
        y = top + k * lane_h
        d0.text((8, y + 14), lab, font=f_lab, fill=rgb(col, 0.8))
        d0.line([(120, y + lane_h // 2), (W - 8, y + lane_h // 2)], fill=rgb(DIM), width=1)
    d0.line([(NOW_X, top - 6), (NOW_X, top + len(lanes) * lane_h + 4)], fill=rgb(INK, 0.6), width=1)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", TM["audio"], "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        t = f / FPS
        im = bg.copy()
        d = ImageDraw.Draw(im)
        px = lambda x: NOW_X + (x - t) / SPAN * (NOW_X - 124)  # noqa: E731
        bi = np.searchsorted(beats, [t - SPAN, t + SPAN])
        for i in range(bi[0], bi[1]):
            x = px(beats[i])
            d.line([(x, top - 4), (x, top + len(lanes) * lane_h)], fill=rgb(DIM, 1.9 if i in down else 1.0))
        for k, (_, ev, col) in enumerate(lanes):
            y = top + k * lane_h + lane_h // 2
            a, b = np.searchsorted(ev, [t - SPAN, t + SPAN])
            for e in ev[a:b]:
                x = px(e)
                hot = 0 <= t - e < 0.12
                r = 7 if hot else 3
                d.ellipse([x - r, y - r, x + r, y + r], fill=rgb(col, 1.0 if hot or e > t else 0.45))
        # vocal envelopes
        ey = top + len(lanes) * lane_h + 12
        for j, (k, col) in enumerate((("vocals", INK), ("backing", GOLD))):
            v = float(env[k][min(f, len(env[k]) - 1)])
            d.text((8, ey + j * 16 - 3), "lead" if k == "vocals" else "choir", font=f_lab, fill=rgb(col, 0.8))
            d.rectangle([124, ey + j * 16, 124 + int(v * (W - 140)), ey + j * 16 + 7], fill=rgb(col, 0.8))
        # header
        sec = next((s for s in reversed(TM["sections"]) if s["start"] <= t + 1e-6), TM["sections"][0])
        bar = next((b for b in reversed(bars) if b["start"] <= t + 1e-6), bars[0])
        bnum = int(np.searchsorted(beats, t + 1e-6)) - 1
        odd = f"  ({bar['beats']}-beat bar)" if bar["beats"] != 4 else ""
        key = next((k["key"] for k in reversed(keys) if k["t"] <= t), keys[0]["key"])
        d.text((10, 8), sec["name"], font=f_big, fill=rgb(INK))
        d.text((10, 36), sec.get("singer", ""), font=f_lab, fill=rgb(GOLD))
        d.text((10, 56), f"bar {bar['n']}.{bnum - bar['beat'] + 1}{odd}  {bar['bpm'] or 0:.0f} bpm  key {key}  "
                         f"t={t:7.2f}s  f={f}", font=f_lab, fill=rgb(GOLD) if odd else rgb(INK, 0.7))
        shot = next((s for s in reversed(shots) if s["t"] <= t + 1e-6), None)
        if shot:
            flash = 0 <= t - shot["t"] < 0.25
            d.rectangle([W - 200, 8, W - 60, 40], fill=rgb(GREEN) if flash else rgb(BG), outline=rgb(GREEN))
            d.text((W - 192, 13), shot["id"], font=f_big, fill=rgb(BG) if flash else rgb(GREEN))
        if bnum >= 0 and t - beats[bnum] < 0.1:
            d.rectangle([W - 48, 8, W - 16, 40], fill=rgb(GOLD) if bnum in down else rgb(DIM, 1.6))
        if kc and 0 <= t - kc["t"] < 2.0:
            d.text((W // 2 - 70, 70), "KEY CHANGE", font=f_lab, fill=rgb(GOLD))
        if live["start"] <= t < live["end"]:
            d.text((W // 2 - 190, 70), "LIVE VERSE: the human's take replaces this", font=f_lab, fill=rgb(GREEN))
        # caption
        cur = [ln for ln in TM["lines"] if ln["start"] - 1.5 <= t <= ln["end"] + 0.6]
        y = H - 46 - 36 * (len(cur[-3:]) - 1)
        for ln in cur[-3:]:
            x = 40
            for w in ln["words"]:
                lit = t >= w["start"]
                d.text((x, y), w["w"], font=f_cap, fill=rgb(GOLD) if lit else rgb(INK, 0.45))
                x += d.textlength(w["w"] + " ", font=f_cap)
            y += 36
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    ff.wait()
    print(out)


if __name__ == "__main__":
    main()
