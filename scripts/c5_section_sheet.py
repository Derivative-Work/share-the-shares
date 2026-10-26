"""C5 contact sheet: one still per shot of a section cut (scripts/animatic_assemble.py --from/--to), taken 0.5 s into
the shot (or at its middle, if shorter than 1 s), labelled with the shot ID and its song time.

Usage: .venv/bin/python -I scripts/c5_section_sheet.py <cut.mp4> <from s> <to s> <out.jpg>
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TM = json.loads((ROOT / "timing/timing_map.json").read_text())
PH = json.loads((ROOT / "config/c4_shots.json").read_text())["placeholders"]
PRE = PH["S01"]["before_s"]
DUR = TM["duration_s"]


def main(cut, t0, t1, out):
    t0, t1 = float(t0), float(t1)
    shots = sorted([s for s in TM["shots"] if s["t"] is not None], key=lambda s: s["t"])
    spans = [(s["id"], s["t"], shots[k + 1]["t"] if k + 1 < len(shots) else DUR) for k, s in enumerate(shots)]
    v0 = 0.0 if not t0 else t0 + PRE  # the cut's video start, as the assembler sets it
    picks = []
    if not t0 and PRE:
        picks.append(("S01", -PRE + min(2.0, PRE / 2)))
    picks += [(i, a + (0.5 if b - a >= 1 else (b - a) / 2)) for i, a, b in spans if t0 <= a < t1]
    if t1 >= DUR:
        t = DUR
        for sid in ("S45", "S46", "S47", "S48"):
            picks.append((sid, t + PH[sid]["after_s"] / 2))
            t += PH[sid]["after_s"]
    tiles = []
    f = ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENsc28P.ttf"), 26)
    with tempfile.TemporaryDirectory() as td:
        for sid, t in picks:
            png = Path(td) / f"{sid}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t + PRE - v0:.3f}", "-i", cut, "-frames:v", "1",
                            "-vf", "scale=640:-2", str(png)], check=True)
            im = Image.open(png).convert("RGB")
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 200, 36], fill=(20, 16, 12))
            d.text((8, 4), f"{sid}  {t:6.1f} s", font=f, fill=(238, 229, 204))
            tiles.append(im)
    cols = 4
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (40, 33, 26))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    sheet.save(out, quality=90)
    print(out, len(tiles), "shots")


if __name__ == "__main__":
    main(*sys.argv[1:5])
