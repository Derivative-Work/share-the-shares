"""The certificate's back, the transfer form, as a print for the prop (brief, "The prop": "Print the transfer form on the
back"). Shaded as the render shades it (scenes/blender/lib/puppet.py layer_material): the paper printed with the sepia
plate, paper x (1 - a + a x sepia), and the lathe plate multiplied over it in gold, as the back is from S36 on
(scenes/blender/animatic.py S24), which covers every live shot. Mixed in linear light, written as sRGB.

Writes deliverables/transfer_form/: transfer_form.pdf (the back alone, 11 x 8.5 in landscape), prop_duplex.pdf (page 1
the face, the alignment print with its marks; page 2 the back) and the back as a PNG.
Usage: .venv/bin/python -I scripts/transfer_form_print.py   (after scripts/alignment_sheet.py)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from alignment_sheet import write_pdf  # noqa: E402

LOOK = json.loads(Path("config/look.json").read_text())
PROPS = Path("assets/engravings/ink/props")
FACE = Path("deliverables/alignment_sheet/alignment_print_4400x3400.png")
OUT = Path("deliverables/transfer_form")
DPI = LOOK["sheet"]["dpi"]


def linear(hx):
    c = np.array([int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)


def main():
    pal = LOOK["palette"]
    paper, sepia, gold = (linear(pal[k]) for k in ("paper", "ink_sepia", "ink_gold"))
    a = np.asarray(Image.open(PROPS / "transfer_form.png").convert("L"), np.float32)[..., None] / 255
    g = np.asarray(Image.open(PROPS / "transfer_form_green.png").convert("L"), np.float32)[..., None] / 255
    col = paper * (1 - a + a * sepia)
    col = col * (1 - g + g * gold)
    back = Image.fromarray((to_srgb(col) * 255 + 0.5).astype(np.uint8))
    w, h = (int(round(v * DPI)) for v in LOOK["sheet"]["size_in"])
    assert back.size == (w, h), back.size
    OUT.mkdir(parents=True, exist_ok=True)
    back.save(OUT / f"transfer_form_{w}x{h}.png", dpi=(DPI, DPI))
    write_pdf([back], OUT / "transfer_form.pdf", DPI)
    face = Image.open(FACE)
    assert face.size == back.size, face.size
    write_pdf([face, back], OUT / "prop_duplex.pdf", DPI)
    print(f"{OUT}: transfer_form.pdf, prop_duplex.pdf, transfer_form_{w}x{h}.png ({w / DPI} x {h / DPI} in at {DPI} dpi)")


if __name__ == "__main__":
    main()
