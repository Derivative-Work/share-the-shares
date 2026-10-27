"""The alignment sheet for compositing the live shots: the printed prop, with registration marks the track can lock
to, and a key page giving every mark's position in the plates' pixels (deliverables/live_plates: 4400x3400, the
sheet edge to edge, so a plate pixel is a print pixel at 400 dpi).

The print is the flat render of the sheet during the live verse (scenes/blender/animatic.py --flat at 170.0 s),
when nothing on it moves: the figures in their rest poses, the world gold since S36, so it matches the plates
exactly. Five marks are added on clean paper away from everything that moves (brief, "Tracking and compositing":
the corner denominations double as tracking marks, with registration marks added if the track needs more); the four
corner discs' centres are listed too. Each mark's spot is the emptiest window in its zone, clear of the moving
figures and the corner discs, and is checked against every frame of the sheet plates.

Writes deliverables/alignment_sheet/: alignment_sheet.pdf (page 1 the print, 11 x 8.5 in landscape; page 2 the key),
the print as a PNG, and marks.json.
Usage: .venv/bin/python -I scripts/alignment_sheet.py
"""
import json
import subprocess
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PRINT = Path("renders/final/alignment/t_0170.00.png")  # blender ... --flat --size 4400 3400 --samples 64 --times 170.0
LAYOUT = json.loads(Path("renders/c1/certificate_v05/layout.json").read_text())["boxes"]
LOOK = json.loads(Path("config/look.json").read_text())
OUT = Path("deliverables/alignment_sheet")
DPI = LOOK["sheet"]["dpi"]
SEPIA = LOOK["palette"]["ink_sepia"]
MOVING = ("progress", "cherubs", "cherubs_mirror", "prudence", "mercury", "laborer",
          "counter_0", "counter_1", "counter_2", "counter_3")
R, PAD = 55, 40  # a mark's half footprint, and its clearance from anything that moves (px)
# numbered clockwise from the top left: (x0, y0, x1, y1) in sheet pixels
# Only where the paper is truly clean in every plate: not on the coupons (cut away in the final chorus, S37, so
# S40's plate has a hole there), nor under the signature lines (faint ink everywhere). The corner discs, which no
# plate changes, cover the bottom corners.
ZONES = {1: (640, 600, 1500, 1300), 2: (3300, 600, 4300, 1300), 3: (3700, 1100, 4320, 1550),
         4: (20, 1500, 540, 2800), 5: (20, 280, 540, 900)}
WHERE = {1: "left of the company banner", 2: "right of the company banner", 3: "between the share box and Prudence",
         4: "stub, lower", 5: "stub, upper"}
FONT = "assets/fonts/IMFeENrm28P.ttf"
FONT_SC = "assets/fonts/IMFeENsc28P.ttf"


def write_pdf(pages, path, dpi):
    """A PDF with each page one image, Flate-compressed (lossless: Pillow's PDF writer stores RGB as JPEG)."""
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", None]
    kids = []
    for im in pages:
        w, h = im.size
        pw, ph = w / dpi * 72, h / dpi * 72
        data = zlib.compress(im.convert("RGB").tobytes(), 6)
        objs.append(b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB "
                    b"/BitsPerComponent 8 /Filter /FlateDecode /Length %d >>\nstream\n" % (w, h, len(data))
                    + data + b"\nendstream")
        img = len(objs)
        content = b"q %.3f 0 0 %.3f 0 0 cm /Im0 Do Q" % (pw, ph)
        objs.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
        objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.3f %.3f] /Resources << /XObject << /Im0 %d 0 R >> >> "
                    b"/Contents %d 0 R >>" % (pw, ph, img, img + 1))
        kids.append(len(objs))
    objs[1] = b"<< /Type /Pages /Kids [%s] /Count %d >>" % (b" ".join(b"%d 0 R" % k for k in kids), len(kids))
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1) + b"".join(b"%010d 00000 n \n" % o for o in offs)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    Path(path).write_bytes(out)


def ink_map(im):
    lum = np.asarray(im.convert("L")).astype(float)
    paper = np.median(lum)
    return np.clip((paper - lum) / paper, 0, 1)


def window_mean(ink):
    ii = np.pad(ink.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    return lambda cx, cy, r: (ii[cy + r, cx + r] - ii[cy - r, cx + r] - ii[cy + r, cx - r] + ii[cy - r, cx - r]) / (4 * r * r)


def clear(cx, cy):
    return all(not (b[0] - PAD < cx + R and cx - R < b[2] + PAD and b[1] - PAD < cy + R and cy - R < b[3] + PAD)
               for b in (LAYOUT[k] for k in MOVING))


def find_marks(im):
    mean = window_mean(ink_map(im))
    marks = {}
    for n, (x0, y0, x1, y1) in ZONES.items():
        best = min(((mean(cx, cy, R), cx, cy) for cy in range(y0 + R, y1 - R, 5) for cx in range(x0 + R, x1 - R, 5)
                    if clear(cx, cy)), default=None)
        if best is None:
            raise SystemExit(f"mark {n}: no clear spot in its zone")
        marks[n] = (best[1], best[2])
    return marks


def plate_check(marks):
    """The largest ink in any mark's window over every frame of the sheet plates (the marks must sit on paper that
    nothing ever crosses)."""
    worst = {n: 0.0 for n in marks}
    for mov in sorted(Path("deliverables/live_plates").glob("S*_sheet.mov")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mov), "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                             capture_output=True, check=True).stdout
        frames = np.frombuffer(raw, np.uint8).reshape(-1, 3400, 4400)
        for f in frames[::2]:
            paper = np.median(f)
            for n, (cx, cy) in marks.items():
                w = f[cy - R:cy + R, cx - R:cx + R].astype(float)
                worst[n] = max(worst[n], float(np.clip((paper - w) / paper, 0, 1).mean()))
    return worst


def draw_mark(d, cx, cy, n, font):
    r, w = 40, 5
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=SEPIA, width=w)
    d.line((cx - R, cy, cx - 8, cy), fill=SEPIA, width=w - 2)
    d.line((cx + 8, cy, cx + R, cy), fill=SEPIA, width=w - 2)
    d.line((cx, cy - R, cx, cy - 8), fill=SEPIA, width=w - 2)
    d.line((cx, cy + 8, cx, cy + R), fill=SEPIA, width=w - 2)
    d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=SEPIA)
    d.text((cx + r + 6, cy - r - 4), str(n), font=font, fill=SEPIA, anchor="ls")


def corner_points():
    return {f"disc {i + 1}": [round((b[0] + b[2]) / 2), round((b[1] + b[3]) / 2)]
            for i, b in enumerate(LAYOUT[f"counter_{k}"] for k in (0, 1, 3, 2))}  # clockwise from the top left


def key_page(sheet, marks, discs):
    W, H = int(11 * DPI / 2), int(8.5 * DPI / 2)  # drawn at 200 dpi, then doubled to the print's 400
    pg = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(pg)
    big, mid, small = (ImageFont.truetype(FONT_SC, s) for s in (64, 40, 30))
    body = ImageFont.truetype(FONT, 30)
    d.text((100, 90), "Share the Shares · alignment key", font=big, fill="black")
    thumb_w = 1100
    k = thumb_w / sheet.width
    th = sheet.resize((thumb_w, round(sheet.height * k)), Image.LANCZOS)
    pg.paste(th, (100, 200))
    td = ImageDraw.Draw(pg)
    for n, (x, y) in marks.items():
        px, py = 100 + x * k, 200 + y * k
        td.ellipse((px - 14, py - 14, px + 14, py + 14), outline=(200, 30, 30), width=4)
        td.text((px + 18, py - 18), str(n), font=mid, fill=(200, 30, 30))
    for name, (x, y) in discs.items():
        px, py = 100 + x * k, 200 + y * k
        td.rectangle((px - 12, py - 12, px + 12, py + 12), outline=(30, 90, 200), width=4)
        td.text((px + 16, py - 18), name.split()[1], font=small, fill=(30, 90, 200))
    x0, y = 1290, 210
    d.text((x0, y), "Mark      plate px (x, y)      where", font=small, fill="black")
    y += 48
    for n, (x, yy) in marks.items():
        d.text((x0, y), f"{n}", font=body, fill=(200, 30, 30))
        d.text((x0 + 120, y), f"{x}, {yy}", font=body, fill="black")
        d.text((x0 + 400, y), WHERE[n], font=body, fill="black")
        y += 42
    y += 20
    for name, (x, yy) in discs.items():
        d.text((x0, y), name, font=body, fill=(30, 90, 200))
        d.text((x0 + 120, y), f"{x}, {yy}", font=body, fill="black")
        d.text((x0 + 400, y), "corner denomination, centre", font=body, fill="black")
        y += 42
    notes = [
        "The plates (deliverables/live_plates) are 4400 x 3400: the whole sheet, edge to edge, so a plate pixel is a "
        "print pixel at 400 dpi, and these coordinates are both.",
        "Print page 1 in landscape. Fit to page is fine: the track locks to the marks, so the print's scale and "
        "margins don't matter. Print on white stock: the paper's tone is already in the art, as in the plates.",
        "In Resolve (Fusion): track four or more points spread over the sheet (a Planar Tracker on the paper, or "
        "point trackers on the marks and discs), then pin the plate's same points to them (Corner Positioner, or "
        "the Planar Transform) and blend with Multiply (brief). The sheet plate covers the marks; with the figures "
        "plate they stay visible, small, like a printer's registration marks.",
        "The marks sit on paper nothing in any plate ever crosses, and the discs never change in the live shots "
        "(checked on the plates). No marks on the coupons: they are cut away in the final chorus, so S40's plate "
        "has a hole there.",
    ]
    y += 40
    for para in notes:
        line = ""
        for word in para.split():
            if d.textlength(f"{line} {word}".strip(), font=body) > W - x0 - 60:
                d.text((x0, y), line, font=body, fill="black")
                y += 38
                line = word
            else:
                line = f"{line} {word}".strip()
        d.text((x0, y), line, font=body, fill="black")
        y += 58
    return pg.resize((pg.width * 2, pg.height * 2), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(PRINT).convert("RGB")
    marks = find_marks(sheet)
    per = plate_check(marks)
    bad = {n: round(v, 3) for n, v in per.items() if v > 0.02}
    if bad:
        raise SystemExit(f"marks whose windows take ink in the plates: {bad}")
    worst = max(per.values())
    discs = corner_points()
    art = sheet.copy()
    d = ImageDraw.Draw(art)
    font = ImageFont.truetype(FONT, 34)
    for n, (x, y) in marks.items():
        draw_mark(d, x, y, n, font)
    art.save(OUT / "alignment_print_4400x3400.png", dpi=(DPI, DPI))
    key = key_page(sheet, marks, discs)
    write_pdf([art, key], OUT / "alignment_sheet.pdf", DPI)
    (OUT / "marks.json").write_text(json.dumps({
        "_doc": "Registration marks on the alignment print (scripts/alignment_sheet.py), and the corner discs' centres, "
                "in plate pixels (the live plates are 4400x3400, the sheet edge to edge; print pixels at 400 dpi).",
        "plate_size": [sheet.width, sheet.height], "dpi": DPI,
        "marks": {str(n): {"xy": list(xy), "where": WHERE[n]} for n, xy in marks.items()},
        "corner_discs": discs, "worst_plate_ink_in_a_mark_window": round(worst, 4)}, indent=1) + "\n")
    print(f"{OUT}: marks {marks}; worst ink under a mark across the plates {worst:.4f}")


if __name__ == "__main__":
    main()
