"""Assemble the C4 animatic: the rendered frames (scenes/blender/animatic.py), black placeholder cards for the shots
that aren't rendered (live, screen, graphics), the Suno mix, and burned-in review captions (ASS via libass, in the
certificate's fonts):
  - each lyric line, its words lighting as sung (karaoke timing from the aligned words);
  - the shot ID top right.
The graphics layer (overlays/graphics.html, rendered by scripts/render_graphics.py) is composited per frame: the
S02 title, the LIVE bug (S13; blinking on S25-S25c; brief: never on the live shots) and S30's "Post-filter: no
change" tab over the picture, and full-frame cards for S01 (a stand-in for the screen capture), the live slates, the
S47 fact card and S48 (the real announcement page, then the Derived from credits). S01 comes before the music and
S45-S48 after it (their lengths are placeholders until the live footage exists).

Timeline: S01's pre-roll (none since S01 was retired), then the song from 0 s, then the post-roll, whose sound is
audio/postroll/postroll.wav (scripts/postroll_audio.py). The audio is delayed by the pre-roll.
Frames may be every k'th frame (blender --step k): they play at fps / k, so timing is exact and motion is coarser.

Usage: .venv/bin/python -I scripts/animatic_assemble.py <frames dir> <step> <out.mp4> [--graphics DIR]
       [--from S] [--to S] [--captions full|ids|none] [--master] [--no-audio] [--tmp DIR]
  --graphics: the graphics layer's renders (default renders/c4/graphics, the animatic's)
  --from/--to: a section, in song seconds (C5's review cuts, config/c5_sections.json); the pre-roll belongs to a
               section from 0, the post-roll to one running to the end
  --captions: full (karaoke lyrics, shot IDs: the animatic), ids (shot IDs only: C5's review cuts) or none (the finals)
  --master: ProRes 422 HQ (10-bit 4:2:2) in a .mov, with 24-bit PCM audio, for compositing in Resolve
  --no-audio: picture only (the 4K sections, joined and given the full mix afterwards)
  --tmp: where the composited frames are written (default the system's; /tmp is a RAM disk on the 5090 box)
"""
import argparse
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


def ass(w, h, captions="full", only=None):
    """captions: full (lyrics and shot IDs), ids, or lyrics (lyrics alone: scripts/captions_layer.py); only: the line
    IDs to caption (default all)"""
    # the styles are sized for the 640x360 animatic; libass scales them to the frame (the C5 cuts are 1080p)
    # YCbCr Matrix: None: without it ffmpeg takes the script as TV.601 and squeezes its colours into 16-235
    L = ["[Script Info]", "ScriptType: v4.00+", "YCbCr Matrix: None", "PlayResX: 640", "PlayResY: 360", "",
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
    for ln in (TM["lines"] if captions in ("full", "lyrics") else []):
        if only is not None and ln["id"] not in only:
            continue
        a, b = ln["start"] - 0.4 + PRE, ln["end"] + 0.6 + PRE
        parts, t = [], ln["start"] - 0.4
        for wd in ln["words"]:
            parts.append(f"{{\\k{max(0, int(round((wd['start'] - t) * 100)))}}}")
            parts.append(wd["w"] + " ")
            t = wd["start"]
        L.append(ev(0, a, b, "Cap", "".join(parts)))
    if captions == "lyrics":
        return "\n".join(L) + "\n"
    for sid, (a, b) in SPAN.items():
        L.append(ev(1, a + PRE, b + PRE, "Id", sid))
    # the shot IDs of the pre- and post-roll (their pictures are the graphics layer's cards)
    if PRE:
        L.append(ev(1, 0, PRE, "Id", "S01"))
    t = PRE + DUR
    for sid in POST_IDS:
        L.append(ev(1, t, t + PH[sid]["after_s"], "Id", sid))
        t += PH[sid]["after_s"]
    return "\n".join(L) + "\n"


def graphics(w, h, G):
    """The graphics layer (scripts/render_graphics.py): per job, its frames and video-time span."""
    G = Path(G)
    meta = json.loads((G / "jobs.json").read_text())
    if tuple(meta["size"]) != (w, h):
        raise SystemExit(f"graphics are {meta['size']}, frames are {w}x{h}: re-run render_graphics.py")
    return G, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frames")
    ap.add_argument("step", type=int)
    ap.add_argument("out")
    ap.add_argument("--graphics", default="renders/c4/graphics")
    ap.add_argument("--from", dest="t0", type=float, default=None)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--captions", default="full", choices=["full", "ids", "none"])
    ap.add_argument("--master", action="store_true")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    frames, step, out = Path(a.frames), a.step, a.out
    pngs = {int(p.stem[2:]): p for p in frames.glob("f_*.png")}
    w, h = Image.open(next(iter(pngs.values()))).size
    total = PRE + DUR + POST
    # the cut's span in video time: a section from 0 takes the pre-roll, one to the end the post-roll
    v0 = 0.0 if not a.t0 else a.t0 + PRE
    v1 = total if a.t1 is None or a.t1 >= DUR else a.t1 + PRE
    k0, k1 = int(round(v0 * FPS / step)), int(round(v1 * FPS / step))
    G, meta = graphics(w, h, a.graphics)
    gfps = meta["fps"]
    cache = {}

    def gframe(job, tt):
        k = 0 if job["still"] else min(job["frames"] - 1, max(0, int(round((tt - job["start"]) * gfps))))
        key = (job["name"], k)
        if key not in cache:
            cache.clear() if len(cache) > 64 else None
            cache[key] = Image.open(G / job["name"] / f"{k:05d}.png").convert("RGBA")
        return cache[key]

    with tempfile.TemporaryDirectory(dir=a.tmp) as td:
        td = Path(td)
        seq = td / "seq"
        seq.mkdir()
        black = Image.new("RGB", (w, h), (12, 10, 8))
        for k in range(k0, k1):
            tt = k * step / FPS - PRE  # song time shown at output frame k
            f = round(tt * FPS)
            active = [j for j in meta["jobs"] if j["start"] <= tt < j["start"] + j["dur"]]
            full = [j for j in active if j["full"]]
            if f in pngs and not full and not active:
                os.symlink(pngs[f].resolve(), seq / f"{k - k0:06d}.png")
                continue
            im = (Image.open(pngs[f]).convert("RGB") if f in pngs else black.copy()) if not full else \
                gframe(full[0], tt).convert("RGB")
            for j in active:
                if not j["full"]:
                    g = gframe(j, tt)
                    im.paste(g, (0, 0), g)
            im.save(seq / f"{k - k0:06d}.png")
        sub = td / "c4.ass"
        # the captions, shifted to the cut's start (libass drops events that end before 0)
        script = ass(w, h, a.captions)
        if v0:
            head, ev_ = script.split("[Events]\n", 1)
            rows = []
            for row in ev_.splitlines():
                if row.startswith("Dialogue:"):
                    f_ = row.split(",", 9)
                    t_a, t_b = (sum(float(x) * m for x, m in zip(c.split(":"), (3600, 60, 1))) - v0 for c in f_[1:3])
                    if t_b <= 0:
                        continue
                    f_[1], f_[2] = ts(max(t_a, 0)), ts(t_b)
                    row = ",".join(f_)
                rows.append(row)
            script = head + "[Events]\n" + "\n".join(rows) + "\n"
        sub.write_text(script)
        if a.captions == "none":
            vf = "[0:v]null[v]"
        else:
            vf = f"[0:v]ass={sub}:fontsdir=assets/fonts[v]"
        if a.master:
            vcodec = ["-c:v", "prores_ks", "-profile:v", "3", "-vendor", "apl0", "-pix_fmt", "yuv422p10le"]
        else:
            vcodec = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p"]
        # the audio is encoded on its own and muxed in as is: encoded in the same graph as the slow video, the
        # delayed audio came out with broken packet timestamps (a 1.6 s packet at the pre-roll's end), which
        # players that ignore timestamps played ~1.5 s early (v1-v3)
        ms = int(round(PRE * 1000))
        aud = td / ("audio.wav" if a.master else "audio.m4a")
        acodec = ["-c:a", "pcm_s24le"] if a.master else ["-c:a", "aac", "-b:a", "160k"]
        # the post-roll's sound (scripts/postroll_audio.py: the dialling, the ring, the hold music) follows the song
        post = Path("audio/postroll/postroll.wav")
        srcs = ["-i", TM["audio"]] + (["-i", str(post)] if post.exists() else [])
        chain = ("[0:a][1:a]concat=n=2:v=0:a=1," if post.exists() else "[0:a]") + f"adelay={ms}|{ms},apad[a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *srcs, "-filter_complex", chain, "-map", "[a]",
                        "-ss", f"{v0:.3f}", "-t", f"{v1 - v0:.3f}", *acodec, str(aud)], check=True)
        audio = [] if a.no_audio else ["-i", str(aud)]
        amap = [] if a.no_audio else ["-map", "1:a", "-c:a", "copy"]
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", f"{FPS / step}", "-i", str(seq / "%06d.png"), *audio,
               "-filter_complex", vf, "-map", "[v]", *amap, "-t", f"{v1 - v0:.3f}", *vcodec, "-r", f"{FPS}", out]
        subprocess.run(cmd, check=True)
    print(out, f"{v1 - v0:.1f} s (video {v0:.2f}-{v1:.2f}), {len(pngs)} rendered frames on disk")


if __name__ == "__main__":
    main()
