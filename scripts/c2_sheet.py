"""C2 review sheet: four frames from each cast-test view (renders/c2/frames_cast_<view>), one row per view.
Usage: c2_sheet.py <out.jpg> [frame ...]  (default frames 1 25 49 73)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENsc28P.ttf"), 30)
views = ["wide", "progress", "prudence", "mercury", "cherubs"]
frames = [int(f) for f in sys.argv[2:]] or [1, 25, 49, 73]
tw, th = 640, 360
sheet = Image.new("RGB", (tw * len(frames) + 20, (th + 40) * len(views) + 10), "#F4F1EA")
d = ImageDraw.Draw(sheet)
for r, v in enumerate(views):
    for c, f in enumerate(frames):
        im = Image.open(ROOT / f"renders/c2/frames_cast_{v}/f_{f:04d}.png").convert("RGB").resize((tw, th))
        sheet.paste(im, (10 + c * tw, 40 + r * (th + 40)))
        d.text((14 + c * tw, 6 + r * (th + 40)), f"{v}  f{f}", font=FONT, fill="#222")
sheet.save(sys.argv[1], quality=86)
print(sys.argv[1], sheet.size)
