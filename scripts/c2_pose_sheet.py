"""C2 pose sheet: each puppet's rest pose beside its three extremes (renders/c2/poses, scenes/blender/c2_poses.py).
Usage: c2_pose_sheet.py <poses dir> <out.jpg>"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENsc28P.ttf"), 30)
d_in, out = Path(sys.argv[1]), sys.argv[2]
poses = json.loads((d_in / "poses.json").read_text())
tw, th = 800, 450
sheet = Image.new("RGB", (tw * 4 + 50, (th + 46) * len(poses) + 10), "#F4F1EA")
d = ImageDraw.Draw(sheet)
for r, (name, labels) in enumerate(poses.items()):
    for c, label in enumerate(labels):
        im = Image.open(d_in / f"{name}_{c}.png").convert("RGB").resize((tw, th))
        x, y = 10 + c * (tw + 10), 44 + r * (th + 46)
        sheet.paste(im, (x, y))
        d.text((x + 4, y - 36), f"{name}: {label}", font=FONT, fill="#222" if c else "#777")
sheet.save(out, quality=86)
print(out, sheet.size)
