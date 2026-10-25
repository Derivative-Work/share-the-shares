"""Assemble the C4 animatic: the rendered frames (scenes/blender/animatic.py), black placeholder cards for the shots
that aren't rendered (live, screen, graphics), the Suno mix, and burned-in review captions (ASS via libass, in the
certificate's fonts):
  - each lyric line, its words lighting as sung (karaoke timing from the aligned words);
  - the shot ID top right;
  - the graphics layer (G) as review stand-ins: the SHARE THE SHARES title on S02, the LIVE bug on rendered chorus
    shots (S13, S25 blinking; brief: never on the live shots), S36's re-ink note;
  - a card for each live (L), screen (S) and graphics-only shot (config/c4_shots.json placeholders), with S01 before
    the music and S45-S48 after it (their lengths are placeholders until the live footage and the fact card exist).

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
    # placeholder cards
    L.append(ev(2, 0, PRE, "Card", PH["S01"]["text"]))
    L.append(ev(1, 0, PRE, "Id", "S01"))
    for sid in ("S26", "S29", "S30", "S31", "S40"):
        a, b = SPAN[sid]
        L.append(ev(2, a + PRE, b + PRE, "Card", PH[sid]["text"]))
    t = PRE + DUR
    for sid in POST_IDS:
        L.append(ev(2, t, t + PH[sid]["after_s"], "Card", PH[sid]["text"]))
        L.append(ev(1, t, t + PH[sid]["after_s"], "Id", sid))
        t += PH[sid]["after_s"]
    # the graphics layer, as review stand-ins (built in Remotion at C5)
    a, b = SPAN["S02"]
    L.append(ev(3, a + 0.6 + PRE, SPAN["S03"][0] + 1.2 + PRE, "Title", "{\\fad(900,500)}SHARE THE SHARES"))
    for sid, blink in (("S13", False), ("S25", True)):
        a, b = SPAN[sid]
        if blink:
            k = a
            while k < b:
                L.append(ev(3, k + PRE, min(b, k + 0.5) + PRE, "Bug", "● LIVE"))
                k += 1.0
        else:
            L.append(ev(3, a + PRE, b + PRE, "Bug", "● LIVE"))
    a, b = SPAN["S36"]
    L.append(ev(3, a + PRE, b + 2.5 + PRE, "Note", "S36 (C5): the certificate re-inks brighter, gold creeping into the green"))
    a, b = SPAN["S06"]
    L.append(ev(3, a + PRE, a + 4 + PRE, "Note", "C5 engraves the studio, mics and door; grey cards stand in for them here"))
    return "\n".join(L) + "\n"


def main():
    frames, step, out = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    pngs = {int(p.stem[2:]): p for p in frames.glob("f_*.png")}
    w, h = Image.open(next(iter(pngs.values()))).size
    total = PRE + DUR + POST
    n_out = int(total * FPS / step) + 1
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        black = td / "black.png"
        Image.new("RGB", (w, h), (12, 10, 8)).save(black)
        seq = td / "seq"
        seq.mkdir()
        for k in range(n_out):
            f = round(k * step - PRE * FPS)  # the song frame shown at output frame k
            src = pngs.get(f, black)
            os.symlink(src.resolve(), seq / f"{k:06d}.png")
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
