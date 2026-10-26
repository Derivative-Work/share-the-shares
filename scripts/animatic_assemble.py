"""Assemble the C4 animatic: the rendered frames (scenes/blender/animatic.py), black placeholder cards for the shots
that aren't rendered (live, screen, graphics), the Suno mix, and burned-in review captions (ASS via libass, in the
certificate's fonts):
  - each lyric line, its words lighting as sung (karaoke timing from the aligned words);
  - the shot ID top right;
  - S36's and S06's notes for C5.
The graphics layer (overlays/graphics.html, rendered by scripts/render_graphics.py) is composited per frame: the
S02 title, the LIVE bug (S13; blinking on S25-S25c; brief: never on the live shots) and S30's "Post-filter: no
change" tab over the picture, and full-frame cards for S01 (a stand-in for the screen capture), the live slates, the
S47 fact card and S48 (the real announcement page, then the Derived from credits). S01 comes before the music and
S45-S48 after it (their lengths are placeholders until the live footage exists).

Timeline: S01's pre-roll, then the song from 0 s, then the post-roll. The audio is delayed by the pre-roll.
Frames may be every k'th frame (blender --step k): they play at fps / k, so timing is exact and motion is coarser.

Usage: .venv/bin/python -I scripts/animatic_assemble.py <frames dir> <step> <out.mp4>
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

TM = json.loads(Path("timing/timing_map.json").read_text())
PLAN = json.loads(Path("config/c4_shots.json").read_text())
FPS = TM["fps"]
DUR = TM["duration_s"]
PH = PLAN["placeholders"]
PRE = PH["S01"]["before_s"]
POST_IDS = [i for i in ("S45", "S46", "S47", "S48")]
POST = sum(PH[i]["after_s"] for i in POST_IDS)
SHOTS = [s for s in TM["shots"] if s["t"] is not None]
SPAN = {s["id"]: (s["t"], SHOTS[k + 1]["t"] if k + 1 < len(SHOTS) else DUR) for k, s in enumerate(SHOTS)}


def ts(t):
    h, r = divmod(max(t, 0.0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ev(layer, a, b, style, txt):
    return f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{txt}"


def ass(w, h):
    L = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
         "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
         "MarginR, MarginV, Encoding",
         # karaoke: SecondaryColour before a word is sung, PrimaryColour after (paper cream over a dark outline)
         "Style: Cap,IM FELL English,22,&H00CCE5EE,&H80A0A0A0,&H001E2C3E,&H64000000,0,0,0,0,100,100,0,0,1,1.6,0,2,20,20,16,1",
         "Style: Id,IM FELL English SC,16,&H00CCE5EE,&H00CCE5EE,&H001E2C3E,&H64000000,0,0,0,0,100,100,0,0,1,1.2,0,9,10,10,8,1",
         "Style: Card,IM FELL English,19,&H00CCE5EE,&H00CCE5EE,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,30,1",
         "Style: Title,Abril Fatface,46,&H001E2C3E,&H001E2C3E,&H00CCE5EE,&H00000000,0,0,0,0,100,100,6,0,1,1.5,0,5,20,20,20,1",
         "Style: Bug,IM FELL English SC,15,&H00FFFFFF,&H00FFFFFF,&H001616C8,&H001616C8,0,0,0,0,100,100,2,0,3,3,0,7,14,14,12,1",
         "Style: Note,IM FELL English,14,&H00CCE5EE,&H00CCE5EE,&H001E2C3E,&H64000000,0,1,0,0,100,100,0,0,1,1,0,1,12,12,10,1",
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for ln in TM["lines"]:
        a, b = ln["start"] - 0.4 + PRE, ln["end"] + 0.6 + PRE
        parts, t = [], ln["start"] - 0.4
        for wd in ln["words"]:
            parts.append(f"{{\\k{max(0, int(round((wd['start'] - t) * 100)))}}}")
            parts.append(wd["w"] + " ")
            t = wd["start"]
        L.append(ev(0, a, b, "Cap", "".join(parts)))
    for sid, (a, b) in SPAN.items():
        L.append(ev(1, a + PRE, b + PRE, "Id", sid))
    # the shot IDs of the pre- and post-roll (their pictures are the graphics layer's cards)
    L.append(ev(1, 0, PRE, "Id", "S01"))
    t = PRE + DUR
    for sid in POST_IDS:
        L.append(ev(1, t, t + PH[sid]["after_s"], "Id", sid))
        t += PH[sid]["after_s"]
    a, b = SPAN["S36"]
    L.append(ev(3, a + PRE, b + 2.5 + PRE, "Note", "S36 (C5): the certificate re-inks brighter, gold creeping into the green"))
    a, b = SPAN["S06"]
    L.append(ev(3, a + PRE, a + 4 + PRE, "Note", "C5 engraves the studio, mics and door; grey cards stand in for them here"))
    return "\n".join(L) + "\n"


def graphics(w, h):
    """The graphics layer (scripts/render_graphics.py): per job, its frames and video-time span."""
    G = Path("renders/c4/graphics")
    meta = json.loads((G / "jobs.json").read_text())
    if tuple(meta["size"]) != (w, h):
        raise SystemExit(f"graphics are {meta['size']}, frames are {w}x{h}: re-run render_graphics.py")
    return G, meta


def main():
    frames, step, out = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    pngs = {int(p.stem[2:]): p for p in frames.glob("f_*.png")}
    w, h = Image.open(next(iter(pngs.values()))).size
    total = PRE + DUR + POST
    n_out = int(total * FPS / step) + 1
    G, meta = graphics(w, h)
    gfps = meta["fps"]
    cache = {}

    def gframe(job, tt):
        k = 0 if job["still"] else min(job["frames"] - 1, max(0, int(round((tt - job["start"]) * gfps))))
        key = (job["name"], k)
        if key not in cache:
            cache.clear() if len(cache) > 64 else None
            cache[key] = Image.open(G / job["name"] / f"{k:05d}.png").convert("RGBA")
        return cache[key]

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        seq = td / "seq"
        seq.mkdir()
        black = Image.new("RGB", (w, h), (12, 10, 8))
        for k in range(n_out):
            tt = k * step / FPS - PRE  # song time shown at output frame k
            f = round(tt * FPS)
            active = [j for j in meta["jobs"] if j["start"] <= tt < j["start"] + j["dur"]]
            full = [j for j in active if j["full"]]
            if f in pngs and not full and not active:
                os.symlink(pngs[f].resolve(), seq / f"{k:06d}.png")
                continue
            im = (Image.open(pngs[f]).convert("RGB") if f in pngs else black.copy()) if not full else \
                gframe(full[0], tt).convert("RGB")
            for j in active:
                if not j["full"]:
                    g = gframe(j, tt)
                    im.paste(g, (0, 0), g)
            im.save(seq / f"{k:06d}.png")
        sub = td / "c4.ass"
        sub.write_text(ass(w, h))
        ms = int(round(PRE * 1000))
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", f"{FPS / step}", "-i", str(seq / "%06d.png"),
               "-i", TM["audio"], "-filter_complex",
               f"[0:v]ass={sub}:fontsdir=assets/fonts[v];[1:a]adelay={ms}|{ms},apad[a]",
               "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
               "-pix_fmt", "yuv420p", "-r", f"{FPS}", "-c:a", "aac", "-b:a", "160k", out]
        subprocess.run(cmd, check=True)
    print(out, f"{total:.1f} s, {len(pngs)} rendered frames")


if __name__ == "__main__":
    main()
