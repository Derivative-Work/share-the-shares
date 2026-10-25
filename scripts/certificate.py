"""Compose the certificate's static art: two ink plates (green, sepia) and the printed sheet.

Everything that doesn't move, plus the figures in their rest poses (brief, "The prop"). The guilloche and rosettes
are generated here from sums of sine waves, as a geometric lathe cut them; the vignettes are the ink pieces from
scripts/ink_extract.py; the type is set in the OFL fonts in assets/fonts. Writes, into <out dir>:
  plate_green.png, plate_sepia.png   8-bit ink coverage (255 = full ink), the sheet's size
  sheet.png                          the plates printed on the paper colour (multiply), with paper grain: the prop
  static/                            the same without the figures, for renders: the figures are their own layers
                                     there, at their source resolution, so they can move (and hold up in close-ups)
  layout.json                        every element's box in pixels, for the render and later shots
Usage: certificate.py <out dir>
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOOK = json.loads((ROOT / "config/look.json").read_text())
SEEDS = json.loads((ROOT / "config/seeds.json").read_text())
W, H = (int(v * LOOK["sheet"]["dpi"]) for v in LOOK["sheet"]["size_in"])
AA = cv2.LINE_AA
layout = {}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0


def font(role, size):
    return ImageFont.truetype(str(ROOT / LOOK["fonts"][role]), size)


# ---- geometry ---------------------------------------------------------------------------------------------------

def rounded_rect_path(x0, y0, x1, y1, r, n=6000):
    """Points and outward normals along a rounded rectangle, evenly spaced by arc length."""
    pts, nrm = [], []
    straight = [(x1 - x0 - 2 * r), (y1 - y0 - 2 * r)] * 2
    total = sum(straight) + 2 * np.pi * r
    for s in np.linspace(0, total, n, endpoint=False):
        # walk: top edge (left->right), TR corner, right edge, BR, bottom (right->left), BL, left edge, TL
        segs = [("line", (x0 + r, y0), (1, 0), straight[0]), ("arc", (x1 - r, y0 + r), -np.pi / 2, None),
                ("line", (x1, y0 + r), (0, 1), straight[1]), ("arc", (x1 - r, y1 - r), 0.0, None),
                ("line", (x1 - r, y1), (-1, 0), straight[2]), ("arc", (x0 + r, y1 - r), np.pi / 2, None),
                ("line", (x0, y1 - r), (0, -1), straight[3]), ("arc", (x0 + r, y0 + r), np.pi, None)]
        for kind, a, b, ln in segs:
            ln = ln if kind == "line" else np.pi * r / 2
            if s <= ln:
                if kind == "line":
                    p = (a[0] + b[0] * s, a[1] + b[1] * s)
                    q = (b[1], -b[0])  # outward normal for a clockwise walk in image coords
                else:
                    t = b + s / r
                    p = (a[0] + r * np.cos(t), a[1] + r * np.sin(t))
                    q = (np.cos(t), np.sin(t))
                pts.append(p)
                nrm.append(q)
                break
            s -= ln
    return np.array(pts), np.array(nrm), total


def poly(img, pts, width=1, closed=True, value=255):
    p = np.round(pts * 4).astype(np.int32).reshape(-1, 1, 2)  # 2 bits of sub-pixel precision
    cv2.polylines(img, [p], closed, value, width, AA, shift=2)


def guilloche_band(img, box, r, inner, outer, waves, freq, lines, width=2, phase=0.0):
    """Lathe-work band between two offsets from a rounded rectangle: `lines` sine strands per wave set."""
    pts, nrm, total = rounded_rect_path(*box, r)
    s = np.linspace(0, 1, len(pts), endpoint=False)
    mid, amp = (inner + outer) / 2, (outer - inner) / 2
    for w in range(waves):
        for k in range(lines):
            ph = phase + 2 * np.pi * (k / lines) + w * np.pi / waves
            d = mid + amp * (0.82 * np.sin(2 * np.pi * freq * s + ph) + 0.18 * np.sin(2 * np.pi * freq * 3 * s - ph))
            poly(img, pts + nrm * d[:, None], width)


def rosette(img, cx, cy, r0, r1, petals, lines, width=2, inner_scale=0.55):
    """A lathe rosette: concentric strands r(t) = r0..r1 modulated by `petals` lobes, phase-shifted per strand."""
    t = np.linspace(0, 2 * np.pi, 2400, endpoint=False)
    for k in range(lines):
        ph = 2 * np.pi * k / lines
        for base, amp, n in ((r1 * 0.80, r1 * 0.18, petals), (r1 * inner_scale, r1 * 0.12, petals * 2)):
            r = base + amp * np.sin(n * t + ph) * np.cos(t * 0 + ph / 2)
            r = np.maximum(r, r0)
            poly(img, np.stack([cx + r * np.cos(t), cy + r * np.sin(t)], 1), width)
    cv2.circle(img, (int(cx), int(cy)), int(r1 * 1.0), 255, 5, AA)
    cv2.circle(img, (int(cx), int(cy)), int(r1 * 1.04), 255, 2, AA)


# ---- type -------------------------------------------------------------------------------------------------------

def text(img, xy, s, role, size, anchor="mm", fill=255, spacing=0):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    f = font(role, size)
    if spacing:
        # letter-spaced capitals, as engravers set them
        widths = [d.textlength(c, font=f) + spacing for c in s]
        x = xy[0] - sum(widths) / 2 + spacing / 2 if anchor[0] == "m" else xy[0]
        for c, wd in zip(s, widths):
            d.text((x, xy[1]), c, font=f, fill=fill, anchor="l" + anchor[1])
            x += wd
    else:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
    img[:] = np.array(pil)
    return d.textbbox(xy, s, font=f, anchor=anchor)


FIGURES = True  # False: lay out the figures' boxes without printing them (the static plates)


def piece(plate, name, cx, cy, width, mirror=False):
    if not FIGURES:
        ink = cv2.imread(str(ROOT / "assets/engravings/ink" / f"{name}.png"), cv2.IMREAD_GRAYSCALE)
        h = int(round(ink.shape[0] * width / ink.shape[1]))
        x0, y0 = int(cx - width / 2), int(cy - h / 2)
        layout[name + ("_mirror" if mirror else "")] = [x0, y0, x0 + width, y0 + h]
        return
    ink = cv2.imread(str(ROOT / "assets/engravings/ink" / f"{name}.png"), cv2.IMREAD_GRAYSCALE)
    h = int(round(ink.shape[0] * width / ink.shape[1]))
    ink = cv2.resize(ink, (width, h), interpolation=cv2.INTER_AREA)
    if mirror:
        ink = ink[:, ::-1]
    x0, y0 = int(cx - width / 2), int(cy - h / 2)
    sub = plate[y0:y0 + h, x0:x0 + width]
    np.maximum(sub, ink, out=sub)
    layout[name + ("_mirror" if mirror else "")] = [x0, y0, x0 + width, y0 + h]


def perforation(img, p0, p1, pitch=28, rad=5):
    n = int(np.hypot(p1[0] - p0[0], p1[1] - p0[1]) // pitch)
    for i in range(n + 1):
        t = i / max(n, 1)
        cv2.circle(img, (int(p0[0] + (p1[0] - p0[0]) * t), int(p0[1] + (p1[1] - p0[1]) * t)), rad, 255, -1, AA)


# ---- the sheet --------------------------------------------------------------------------------------------------

def build():
    g = np.zeros((H, W), np.uint8)  # green plate
    k = np.zeros((H, W), np.uint8)  # sepia plate
    STUB, COUP = 560, 2830          # stub's right edge (x), coupon strip's top edge (y)
    main = (STUB + 60, 70, W - 70, COUP - 50)
    layout.update(sheet=[0, 0, W, H], stub=[0, 0, STUB, COUP], main=list(main), coupons=[0, COUP, W, H])

    # Border: two lathe bands and fine rules
    x0, y0, x1, y1 = main
    guilloche_band(g, (x0 + 95, y0 + 95, x1 - 95, y1 - 95), 60, -88, -10, 2, 210, 7, 2)
    guilloche_band(g, (x0 + 95, y0 + 95, x1 - 95, y1 - 95), 60, 6, 40, 1, 420, 5, 2, phase=0.7)
    for off, wd in ((0, 6), (14, 2), (182, 2), (192, 5)):
        cv2.rectangle(g, (x0 + off, y0 + off), (x1 - off, y1 - off), 255, wd, AA)

    # Corner counters: rosettes with the denomination
    for i, (cx, cy) in enumerate(((x0 + 300, y0 + 300), (x1 - 300, y0 + 300), (x0 + 300, y1 - 300), (x1 - 300, y1 - 300))):
        rosette(g, cx, cy, 40, 205, 12, 9, 2)
        cv2.circle(g, (cx, cy), 120, 255, -1, AA)
        cv2.circle(k, (cx, cy), 120, 0, -1)
        text(g, (cx, cy + 8), "5", "display", 210, fill=0)
        layout[f"counter_{i}"] = [cx - 210, cy - 210, cx + 210, cy + 210]

    # Top vignette: Progress, flanked by the cherub choir
    cx = (x0 + x1) // 2
    piece(k, "progress", cx, 720, 1500)
    piece(k, "cherubs", cx - 1060, 640, 560)
    piece(k, "cherubs", cx + 1060, 640, 560, mirror=True)

    # Company name, letter-spaced fat-face capitals, with a green underprint panel behind
    name = LOOK["company"]
    under = np.zeros_like(g)
    guilloche_band(under, (x0 + 560, 1285, x1 - 560, 1475), 80, -60, 60, 1, 60, 9, 1)
    g[:] = np.maximum(g, (under * 0.55).astype(np.uint8))
    b = text(k, (cx, 1380), name, "display", 150, spacing=10)
    layout["company"] = list(b)
    text(k, (cx, 1520), "ORGANIZED AS A LIMITED LIABILITY COMPANY  ·  WHOLLY OWNED", "small_caps", 56, spacing=6)

    # Body
    text(k, (cx, 1680), "This Certifies that", "script", 150)
    cv2.line(k, (cx - 900, 1830), (cx + 900, 1830), 255, 3, AA)
    text(k, (cx, 1915), "is the owner of", "body_italic", 72)
    text(k, (cx, 2020), "fully paid and non-assessable Shares of the Capital Stock of the above-named", "body_italic", 60)
    text(k, (cx, 2100), "Company, transferable only on the books of the Company in person or by duly", "body_italic", 60)
    text(k, (cx, 2180), "authorized attorney upon surrender of this Certificate properly endorsed.", "body_italic", 60)

    # Number-of-shares box (right, below the corner counter)
    bx0, by0, bx1, by1 = x1 - 560, 900, x1 - 230, 1080
    cv2.rectangle(k, (bx0, by0), (bx1, by1), 255, 4, AA)
    cv2.rectangle(k, (bx0 + 12, by0 + 12), (bx1 - 12, by1 - 12), 255, 2, AA)
    text(k, ((bx0 + bx1) // 2, by0 - 110), "NUMBER", "small_caps", 50, spacing=6)
    text(k, ((bx0 + bx1) // 2, by0 - 45), "OF SHARES", "small_caps", 50, spacing=6)
    layout["shares_box"] = [bx0, by0, bx1, by1]
    # Certificate number (left, below the corner counter)
    text(k, (x0 + 395, 930), "No.", "body_italic", 80)
    text(k, (x0 + 395, 1040), "0042", "display", 110)

    # Prudence (right) and Mercury (left, in the fine print above the signatures); the laborer, lower left corner
    piece(k, "prudence", x1 - 470, 1880, 540)
    piece(k, "mercury", x0 + 520, 1660, 470)
    piece(k, "laborer", x0 + 560, y1 - 770, 500)

    # Signature lines: President, Secretary and a blank one for the Recipient
    sy = y1 - 360
    for i, label in enumerate(("PRESIDENT", "SECRETARY", "RECIPIENT")):
        sx = cx - 950 + i * 950
        cv2.line(k, (sx - 340, sy), (sx + 340, sy), 255, 3, AA)
        text(k, (sx, sy + 55), label, "small_caps", 52, spacing=8)
        layout[f"sig_{label.lower()}"] = [sx - 340, sy - 120, sx + 340, sy + 90]
    text(k, (cx, y1 - 230), "Shares fully paid and non-assessable", "small_caps", 46, spacing=4)

    # Stub, with its perforation (the bridge's thermometer)
    perforation(k, (STUB + 30, 60), (STUB + 30, COUP - 40))
    text(k, (STUB // 2, 300), "No. 0042", "display", 84)
    for j, s in enumerate(("Issued to", "", "Shares", "", "Date")):
        y = 520 + j * 170
        if s:
            text(k, (70, y), s, "body_italic", 62, anchor="lm")
        cv2.line(k, (70, y + 70), (STUB - 50, y + 70), 255, 2, AA)
    guilloche_band(g, (40, 40, STUB - 20, COUP - 60), 30, -18, 0, 1, 90, 4, 1)

    # Coupons along the bottom, each its own small lathe panel and perforations between
    perforation(k, (40, COUP - 10), (W - 40, COUP - 10))
    n = 7
    cw = (W - 80) / n
    for i in range(n):
        cx0 = int(40 + i * cw)
        cx1 = int(40 + (i + 1) * cw)
        guilloche_band(g, (cx0 + 30, COUP + 40, cx1 - 30, H - 120), 24, -22, 0, 1, 40, 4, 1)
        text(k, ((cx0 + cx1) // 2, COUP + 170), f"COUPON  No. {i + 1}", "small_caps", 46, spacing=4)
        text(k, ((cx0 + cx1) // 2, COUP + 290), "5", "display", 130)
        text(k, ((cx0 + cx1) // 2, COUP + 400), "per hundred", "body_italic", 40)
        if i:
            perforation(k, (cx0, COUP + 20), (cx0, H - 100), pitch=24, rad=4)
        layout[f"coupon_{i + 1}"] = [cx0, COUP, cx1, H - 90]
    # The pledge number along the bottom edge (brief: 555-0100 to 555-0199, set aside for fiction)
    text(k, (W // 2, H - 50), f"PLEDGE LINE   {LOOK['pledge_number']}", "small_caps", 40, spacing=10)
    return g, k


def print_sheet(g, k):
    rng = np.random.default_rng(SEEDS["paper_grain"])
    paper = np.ones((H, W, 3), np.float32) * hexrgb(LOOK["palette"]["paper"])
    grain = cv2.GaussianBlur(rng.standard_normal((H // 4, W // 4)).astype(np.float32), (0, 0), 1.2)
    grain = cv2.resize(grain, (W, H), interpolation=cv2.INTER_CUBIC)
    paper *= (1 + 0.018 * grain)[..., None]
    out = paper
    for plate, col in ((g, LOOK["palette"]["ink_green"]), (k, LOOK["palette"]["ink_sepia"])):
        a = (plate.astype(np.float32) / 255.0)[..., None]
        out = out * (1 - a + a * hexrgb(col))  # inks multiply, as on the press
    return np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    global FIGURES
    for figures, d in ((True, out), (False, out / "static")):
        FIGURES = figures
        d.mkdir(parents=True, exist_ok=True)
        g, k = build()
        cv2.imwrite(str(d / "plate_green.png"), g)
        cv2.imwrite(str(d / "plate_sepia.png"), k)
        Image.fromarray(print_sheet(g, k)).save(d / "sheet.png")
    (out / "layout.json").write_text(json.dumps({"size": [W, H], "boxes": layout}, indent=1))
    print(out, W, "x", H)


if __name__ == "__main__":
    main(sys.argv[1])
