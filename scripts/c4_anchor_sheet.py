"""C4: the anchor stills (animatic.py --anchors) as one labelled contact sheet, in shot order.

Usage: .venv/bin/python -I scripts/c4_anchor_sheet.py <anchors dir> <out.jpg> [cols]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TM = json.loads(Path("timing/timing_map.json").read_text())
FONT = "assets/fonts/IMFeENsc28P.ttf"


def main():
    d, out = Path(sys.argv[1]), sys.argv[2]
    cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    shots = [s for s in TM["shots"] if (d / f"anchor_{s['id']}.png").exists()]
    ims = [Image.open(d / f"anchor_{s['id']}.png").convert("RGB") for s in shots]
    w, h = ims[0].size
    cap = 34
    sheet = Image.new("RGB", (w * cols, (h + cap) * ((len(ims) + cols - 1) // cols)), (244, 241, 234))
    f = ImageFont.truetype(FONT, 20)
    for k, (s, im) in enumerate(zip(shots, ims)):
        x, y = (k % cols) * w, (k // cols) * (h + cap)
        sheet.paste(im, (x, y + cap))
        cue = s["cue"].strip('"')
        ImageDraw.Draw(sheet).text((x + 6, y + 6), f"{s['id']}  {s['t']:.1f} s  {cue[:44]}", fill=(40, 30, 20), font=f)
    sheet.save(out, quality=85)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
