"""C1 review sheet: the engraving sources and layout references beside the flat print and the two test frames.

Usage: c1_sheet.py <certificate dir> <wide.png> <close.png> <out.jpg>
"""
import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENrm28P.ttf"), 26)
BOLD = ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENsc28P.ttf"), 34)


def rows(tsv):
    lines = [l for l in Path(tsv).read_text().splitlines() if not l.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def tile(path, box):
    im = Image.open(path).convert("RGB")
    im.thumbnail(box)
    return im


def main(cert, wide, close, out):
    W = 3000
    sheet = Image.new("RGB", (W, 3350), "#F4F1EA")
    d = ImageDraw.Draw(sheet)
    d.text((40, 30), "C1 — the look: test frames (top), the flat print, and its sources", font=BOLD, fill="#222")
    x = 40
    for p, label in ((wide, "Test frame: wide (S02's framing)"), (close, "Test frame: close (S07's framing)")):
        im = tile(p, (1440, 810))
        sheet.paste(im, (x, 90))
        d.text((x, 90 + im.height + 8), label, font=FONT, fill="#222")
        x += 1480
    flat = tile(Path(cert) / "sheet.png", (1440, 1120))
    sheet.paste(flat, (40, 980))
    d.text((40, 980 + flat.height + 8), "The flat print (the prop): static art and the figures at rest", font=FONT, fill="#222")
    # sources: the engravings used (Met, Durand) and the layout references (never composited)
    y0, x0 = 980, 1520
    d.text((x0, y0 - 2), "Engravings used (A. B. & C. Durand, ca. 1824–42; Met Open Access)", font=FONT, fill="#222")
    used = [r for r in rows(ROOT / "assets/engravings/sources.tsv")]
    for i, r in enumerate(used):
        im = tile(ROOT / "assets/engravings/source" / r["file"], (340, 230))
        cx, cy = x0 + (i % 4) * 360, y0 + 40 + (i // 4) * 270
        sheet.paste(im, (cx, cy))
        d.text((cx, cy + im.height + 2), r["file"][4:40], font=FONT, fill="#555")
    y1 = y0 + 40 + 4 * 270 + 20
    d.text((x0, y1), "Layout and palette references only (Commons)", font=FONT, fill="#222")
    for i, r in enumerate(rows(ROOT / "reference/certificates/sources.tsv")):
        im = tile(ROOT / "reference/certificates" / r["file"], (340, 260))
        cx, cy = x0 + (i % 4) * 360, y1 + 40 + (i // 4) * 300
        sheet.paste(im, (cx, cy))
        d.text((cx, cy + im.height + 2), r["file"][:36], font=FONT, fill="#555")
    sheet = sheet.crop((0, 0, W, min(3350, y1 + 40 + 2 * 300 + 40)))
    sheet.save(out, quality=88)
    print(out, sheet.size)


if __name__ == "__main__":
    main(*sys.argv[1:5])
