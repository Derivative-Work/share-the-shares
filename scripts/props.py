"""C5 props: the C4 animatic's grey cards as engraved ink pieces (config/props.json).

Cut props are crops of public-domain sources (assets/engravings/sources.tsv): patent drawings (bilevel scans) and
engravings (toned scans, through ink_extract's paper-flattening), cleared of reference numerals and lead lines, with
any lettering re-set in the certificate's type. Generated props are drawn here in the certificate's own type,
guilloche and line hatching.

Usage: .venv/bin/python -I scripts/props.py [name ...]  ->  assets/engravings/ink/props/<name>.png (+ _green.png)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certificate as C  # noqa: E402
from ink_extract import ink_map  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/engravings/source"
OUT = ROOT / "assets/engravings/ink/props"
CFG = json.loads((ROOT / "config/props.json").read_text())["props"]
AA = cv2.LINE_AA


# ---- type in a frame -----------------------------------------------------------------------------------------------

FITS = []  # every line set with fit(): (piece, text, requested size, set size, fits)
CURRENT = [""]


def fit(img, box, s, role, size, spacing=0, align="c", fill=255, margin=0.06):
    """Set `s` inside `box` (x0, y0, x1, y1, px): the largest size up to `size` whose inked extent (ascenders,
    descenders and all, measured on the rendered glyphs) clears the box by `margin` of its height on every side,
    centred on the ink (or aligned left / right). Every line is recorded in FITS, so overflow is reported."""
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    bw, bh = x1 - x0, y1 - y0
    pad = max(2, int(bh * margin))
    sz = size
    while True:
        tw, th = int(bw * 2 + sz * 4), int(sz * 3)
        tmp = np.zeros((th, tw), np.uint8)
        C.text(tmp, (tw / 2, th / 2), s, role, sz, spacing=spacing)
        ys, xs = np.where(tmp > 40)
        if not len(xs):
            break
        iw, ih = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if (iw <= bw - 2 * pad and ih <= bh - 2 * pad) or sz <= 6:
            break
        sz = max(6, int(sz * 0.95))
    glyph = tmp[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    gx = {"c": x0 + (bw - iw) // 2, "l": x0 + pad, "r": x1 - pad - iw}[align]
    gy = y0 + (bh - ih) // 2
    ok = iw <= bw - 2 * pad and ih <= bh - 2 * pad and gx >= 0 and gy >= 0 and gx + iw <= img.shape[1] and gy + ih <= img.shape[0]
    FITS.append((CURRENT[0], s, size, sz, ok))
    sub = img[max(0, gy):gy + ih, max(0, gx):gx + iw]
    g = glyph[max(0, -gy):max(0, -gy) + sub.shape[0], max(0, -gx):max(0, -gx) + sub.shape[1]].astype(np.float32) / 255
    sub[:] = np.round(sub * (1 - g) + fill * g).astype(np.uint8) if fill != 255 else np.maximum(sub, glyph[:sub.shape[0], :sub.shape[1]])
    return sz


# ---- cut props -------------------------------------------------------------------------------------------------

def frac_box(b, w, h):
    return int(round(b[0] * w)), int(round(b[1] * h)), int(round(b[2] * w)), int(round(b[3] * h))


def load_ink(p):
    im = cv2.imread(str(SRC / p["source"]), cv2.IMREAD_GRAYSCALE)
    h, w = im.shape
    x0, y0, x1, y1 = frac_box(p["box"], w, h)
    if "levels" in p:  # a toned engraving: flatten the paper first, as for the figures
        return ink_map(im, p["levels"])[y0:y1, x0:x1]
    crop = im[y0:y1, x0:x1].astype(np.float32) / 255.0
    return 1.0 - crop  # a bilevel line drawing: black is ink


def despeckle(ink, min_px):
    if not min_px:
        return ink
    n, lab, stats, _ = cv2.connectedComponentsWithStats((ink > 0.35).astype(np.uint8), 8)
    small = np.isin(lab, np.where(stats[:, cv2.CC_STAT_AREA] < min_px)[0])
    small &= lab > 0
    out = ink.copy()
    out[cv2.dilate(small.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0] = 0
    return out


def clear(ink, shape, value=0.0):
    h, w = ink.shape
    if isinstance(shape[0], (int, float)):
        x0, y0, x1, y1 = frac_box(shape, w, h)
        ink[y0:y1, x0:x1] = value
    else:
        pts = np.array([[x * w, y * h] for x, y in shape], np.int32)
        cv2.fillPoly(ink, [pts], value)


def label(img, box, s, size_frac=0.62, frame=False):
    """A label holder's text, re-set in the certificate's small capitals, fitted to the box (fractions); `frame`
    rules a double border round it (a paper label pasted on)."""
    h, w = img.shape
    x0, y0, x1, y1 = frac_box(box, w, h)
    if frame:
        lw = max(2, (y1 - y0) // 28)
        cv2.rectangle(img, (x0, y0), (x1, y1), 255, lw * 2, AA)
        g = lw * 4
        cv2.rectangle(img, (x0 + g, y0 + g), (x1 - g, y1 - g), 255, lw, AA)
    g = max(2, (y1 - y0) // 28) * 6 if frame else 2
    fit(img, (x0 + g, y0 + g, x1 - g, y1 - g), s, "small_caps", int((y1 - y0) * size_frac), margin=0.1)


def cut(name, p):
    ink = load_ink(p)
    if p.get("upscale"):  # a small figure: enlarged before its labels are set, so they print at a readable size
        k = p["upscale"]
        ink = cv2.resize(ink, (ink.shape[1] * k, ink.shape[0] * k), interpolation=cv2.INTER_CUBIC)
        ink = np.clip((ink - 0.5) * 1.6 + 0.5, 0, 1)  # re-sharpen the line edges
    for e in p.get("erase", []):
        clear(ink, e)
    if "keep" in p:
        h, w = ink.shape
        m = np.zeros_like(ink)
        cv2.fillPoly(m, [np.array([[x * w, y * h] for x, y in p["keep"]], np.int32)], 1.0)
        ink *= m
    ink = despeckle(ink, p.get("despeckle", 0))
    img = np.round(np.clip(ink, 0, 1) * 255).astype(np.uint8)
    for x0, y0, x1, y1, s in p.get("labels", []):
        label(img, (x0, y0, x1, y1), s, frame=p.get("label_frame", False))
    if "trim" in p:
        h, w = img.shape
        x0, y0, x1, y1 = frac_box(p["trim"], w, h)
        img = img[y0:y1, x0:x1]
    if p.get("flip") == "v":
        img = img[::-1].copy()
    elif p.get("flip") == "h":
        img = img[:, ::-1].copy()
    return {name: img}


# ---- engraving helpers ----------------------------------------------------------------------------------------------

def canvas(w, h):
    return np.zeros((h, w), np.uint8)


def hatch(img, mask, angle, pitch, width=2, wave=0.0):
    """Parallel engraved lines at `angle` (degrees) and `pitch` (px), clipped to `mask` (bool); `wave` bends them
    slightly, as a burin does over a curved surface."""
    h, w = img.shape
    lines = canvas(w, h)
    a = np.deg2rad(angle)
    d, n = np.array([np.cos(a), np.sin(a)]), np.array([-np.sin(a), np.cos(a)])
    c = np.array([w / 2, h / 2])
    R = int(np.hypot(w, h) / 2) + pitch
    t = np.linspace(-R, R, 400)
    for k in np.arange(-R, R, pitch):
        pts = c + np.outer(t, d) + n * k + np.outer(wave * pitch * np.sin(t / 90.0 + k), n)
        C.poly(lines, pts, width, closed=False)
    np.maximum(img, np.where(mask, lines, 0).astype(np.uint8), out=img)


def tone(img, mask, level, angle=0.0, base_pitch=26, width=2):
    """Shade a region in one of the engraver's tones: 1 = light (open lines) .. 3 = dark (crossed)."""
    pitch = {1: base_pitch, 2: base_pitch * 0.55, 3: base_pitch * 0.4}[level]
    hatch(img, mask, angle, max(3, int(pitch)), width)
    if level == 3:
        hatch(img, mask, angle + 62, max(4, int(base_pitch * 0.6)), width)


def poly_mask(shape, pts):
    m = np.zeros(shape, np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts)).astype(np.int32)], 1)
    return m.astype(bool)


def outline(img, pts, width=4, closed=True):
    C.poly(img, np.array(pts, np.float64), width, closed)


def circle_text(img, cx, cy, r, s, role, size, start=-90.0, span=None, fill=255):
    """Type set round a circle (a seal's or a coin's legend), reading clockwise from `start` degrees."""
    from PIL import Image, ImageDraw
    f = C.font(role, size)
    widths = [f.getlength(ch) for ch in s]
    span = span if span is not None else np.rad2deg(sum(widths) / r)
    ang = start - span / 2 + 90
    total = sum(widths)
    for ch, wd in zip(s, widths):
        a = ang + span * (wd / 2) / total
        ang += span * wd / total
        if ch == " ":
            continue
        tile = Image.new("L", (size * 2, size * 2), 0)
        ImageDraw.Draw(tile).text((size, size), ch, font=f, fill=fill, anchor="mm")
        tile = np.array(tile.rotate(-(a - 90 + 90), resample=Image.BICUBIC))
        px, py = cx + r * np.cos(np.deg2rad(a - 90)), cy + r * np.sin(np.deg2rad(a - 90))
        x0, y0 = int(px - size), int(py - size)
        sub = img[max(0, y0):y0 + 2 * size, max(0, x0):x0 + 2 * size]
        t = tile[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]]
        np.maximum(sub, t, out=sub)


def wrap(s, role, size, width):
    f = C.font(role, size)
    lines, cur = [], ""
    for wd in s.split():
        if f.getlength((cur + " " + wd).strip()) > width:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    return lines + [cur]


def paste_max(dst, src, x, y):
    h, w = src.shape
    sub = dst[y:y + h, x:x + w]
    np.maximum(sub, src[:sub.shape[0], :sub.shape[1]], out=sub)


def load_prop(name):
    return cv2.imread(str(OUT / f"{name}.png"), cv2.IMREAD_GRAYSCALE)


def scaled(img, width):
    h = int(round(img.shape[0] * width / img.shape[1]))
    return cv2.resize(img, (width, h), interpolation=cv2.INTER_AREA)


GENERATED = {}


def generated(fn):
    GENERATED[fn.__name__] = fn
    return fn


# ---- generated props ------------------------------------------------------------------------------------------------

@generated
def studio(p):
    """The arched crown over a panelled, hatched studio wall and a floor in perspective; a SILENCE plaque."""
    W, H = 1700, 1500
    img = canvas(W, H)
    arch = scaled(load_prop("studio_arch"), W)
    ah = arch.shape[0]
    yy, xx = np.mgrid[0:H, 0:W]
    # the opening: under the crown's lower edge (per column, the lowest ink of the crown's arc), between its feet
    ink_cols = np.where(arch[int(ah * 0.45):].max(0) > 60)[0]
    fx0, fx1 = int(ink_cols.min() + W * 0.06), int(ink_cols.max() - W * 0.06)
    under = np.full(W, ah, np.int32)
    for x in range(fx0, fx1):
        col = np.where(arch[:, x] > 60)[0]
        under[x] = col.max() + 6 if len(col) else ah
    inside = (xx >= fx0) & (xx < fx1) & (yy > under[None, :])
    floor_y = int(H * 0.80)
    wall = inside & (yy < floor_y)
    floor = inside & (yy >= floor_y) & (yy < H - 40)
    tone(img, wall, 2, angle=0, base_pitch=22)
    ex, rx = (fx0 + fx1) / 2, (fx1 - fx0) / 2
    top = int(under[fx0:fx1].min())
    # acoustic panels: double-ruled rectangles, lighter inside
    for k in range(-2, 3):
        x0 = int(ex + k * rx * 0.38 - rx * 0.16)
        r = (x0, max(top + 140, int(H * 0.42)), x0 + int(rx * 0.32), floor_y - 60)
        m = np.zeros((H, W), bool)
        m[r[1]:r[3], r[0]:r[2]] = True
        m &= wall
        img[m] = 0
        tone(img, m, 1, angle=90, base_pitch=20)
        cv2.rectangle(img, r[:2], r[2:], 255, 4, AA)
        cv2.rectangle(img, (r[0] + 12, r[1] + 12), (r[2] - 12, r[3] - 12), 255, 2, AA)
    # the floor: boards converging on a vanishing point
    vx, vy = ex, floor_y - 420
    fl = canvas(W, H)
    for x in np.linspace(ex - rx * 2.2, ex + rx * 2.2, 25):
        outline(fl, [(vx, vy), (x, H)], 3, closed=False)
    for y in np.geomspace(1, H - 40 - floor_y, 7):
        cv2.line(fl, (0, int(floor_y + y)), (W, int(floor_y + y)), 255, 2, AA)
    img[floor] = np.maximum(img[floor], fl[floor])
    cv2.line(img, (fx0, floor_y), (fx1, floor_y), 255, 6, AA)
    for x in (fx0, fx1):
        cv2.line(img, (x, int(under[min(max(x, fx0), fx1 - 1)])), (x, H - 40), 255, 6, AA)
    cv2.line(img, (fx0, H - 40), (fx1, H - 40), 255, 6, AA)
    np.maximum(img[:ah], arch, out=img[:ah])
    ey, ry = top, 0
    # the plaque over the door to the floor: SILENCE
    py = top + 80
    img[py - 50:py + 50, int(ex - 190):int(ex + 190)] = 0
    cv2.rectangle(img, (int(ex - 190), py - 50), (int(ex + 190), py + 50), 255, 5, AA)
    cv2.rectangle(img, (int(ex - 176), py - 36), (int(ex + 176), py + 36), 255, 2, AA)
    fit(img, (ex - 176, py - 36, ex + 176, py + 36), "SILENCE", "small_caps", 56, spacing=10)
    return {"studio": img}


@generated
def door_plaque(p):
    W, H = 640, 200
    img = canvas(W, H)
    m = np.zeros((H, W), bool)
    m[22:H - 22, 22:W - 22] = True
    tone(img, m, 1, angle=0, base_pitch=10, width=1)  # engraved brass
    img[52:H - 52, 70:W - 70] = 0
    cv2.rectangle(img, (6, 6), (W - 6, H - 6), 255, 6, AA)
    cv2.rectangle(img, (22, 22), (W - 22, H - 22), 255, 2, AA)
    cv2.rectangle(img, (70, 52), (W - 70, H - 52), 255, 2, AA)
    for x, y in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        cv2.circle(img, (x, y), 9, 255, 3, AA)
        cv2.line(img, (x - 6, y - 6), (x + 6, y + 6), 255, 2, AA)
    fit(img, (70, 52, W - 70, H - 52), "WHOLLY OWNED", "small_caps", 58, spacing=4)
    return {"door_plaque": img}


MONTHS = ["NOV", "DEC", "JAN", "Q1", "Q2", "SOON", "H2", "TBD", "NEXT", "SOON"]  # the C4 animatic's pages


@generated
def calendar_pages(p):
    """The pages that lie on the calendar's pad (scenes/blender/animatic.py CAL_PAD), at its drawn proportions (about
    724 x 414 px along and across the engraving's parallelogram), bound along their right edge at its binding strip."""
    out = {}
    for i, m in enumerate(MONTHS):
        W, H = 700, 400
        img = canvas(W, H)
        cv2.rectangle(img, (6, 6), (W - 6, H - 6), 255, 4, AA)
        cv2.rectangle(img, (6, 6), (W - 6, 76), 255, -1, AA)  # the month band, printed solid
        fit(img, (24, 12, W - 60, 76), "IN THE COMING MONTHS", "small_caps", 30, fill=0, margin=0.2)
        fit(img, (40, 92, W - 76, 322), m, "display", 210)
        fit(img, (40, 330, W - 76, 384), "AMALGAMATED BENEFIT, LLC", "small_caps", 24, margin=0.15)
        cv2.line(img, (W - 40, 6), (W - 40, H - 6), 255, 2, AA)  # the fold at the binding
        out[f"calendar_page_{i}"] = img
    return out


@generated
def coins(p):
    """A coin face (reeded rim, lathe rosette, the legend, a 5) and a stack of three seen from above the scales."""
    W = 520
    face = canvas(W, W)
    c = W / 2
    cv2.circle(face, (int(c), int(c)), int(c - 8), 255, 8, AA)
    for a in np.linspace(0, 2 * np.pi, 160, endpoint=False):  # reeding
        r0, r1 = c - 26, c - 12
        cv2.line(face, (int(c + r0 * np.cos(a)), int(c + r0 * np.sin(a))), (int(c + r1 * np.cos(a)), int(c + r1 * np.sin(a))), 255, 3, AA)
    cv2.circle(face, (int(c), int(c)), int(c - 34), 255, 3, AA)
    circle_text(face, c, c, c - 72, "FIVE IN EVERY HUNDRED · ", "small_caps", 40, span=350)
    C.rosette(face, c, c, 30, 150, 10, 6, 2)
    cv2.circle(face, (int(c), int(c)), 92, 0, -1, AA)
    cv2.circle(face, (int(c), int(c)), 92, 255, 3, AA)
    fit(face, (c - 70, c - 78, c + 70, c + 78), "5", "display", 150)
    # the stack: each coin a squashed face over a reeded edge band
    S = canvas(W, 420)
    top = cv2.resize(face, (W - 40, 150), interpolation=cv2.INTER_AREA)
    for k in range(3):
        y = 230 - k * 60
        band = np.zeros(S.shape, bool)
        cv2.ellipse(S, (W // 2, y + 75 + 40), ((W - 40) // 2, 75), 0, 0, 180, 255, 4, AA)
        m = np.zeros(S.shape, np.uint8)
        cv2.ellipse(m, (W // 2, y + 75 + 40), ((W - 40) // 2, 75), 0, 0, 180, 1, -1)
        cv2.rectangle(m, (20, y + 75), (W - 20, y + 115), 1, -1)
        cv2.ellipse(m, (W // 2, y + 75), ((W - 40) // 2, 75), 0, 0, 360, 0, -1)
        band = m.astype(bool)
        S[band] = 0
        hatch(S, band, 90, 9, 2)
        for x in (20, W - 20):
            cv2.line(S, (x, y + 75), (x, y + 115), 255, 4, AA)
        sub = S[y:y + 150, 20:W - 20]
        cover = np.zeros(sub.shape, np.uint8)
        cv2.ellipse(cover, ((W - 40) // 2, 75), ((W - 40) // 2, 75), 0, 0, 360, 1, -1)
        sub[cover > 0] = top[cover > 0]
    return {"coin_face": face, "coins": S}


@generated
def eraser(p):
    W, H = 700, 420
    img = canvas(W, H)
    top = [(120, 60), (640, 60), (560, 160), (40, 160)]
    front = [(40, 160), (560, 160), (560, 380), (40, 380)]
    side = [(560, 160), (640, 60), (640, 280), (560, 380)]
    tone(img, poly_mask(img.shape, top), 1, angle=-8, base_pitch=24)
    tone(img, poly_mask(img.shape, front), 2, angle=0, base_pitch=22)
    tone(img, poly_mask(img.shape, side), 3, angle=-50, base_pitch=20)
    for f in (top, front, side):
        outline(img, f, 5)
    # the maker's panel on the front, knocked out of the hatching
    img[215:325, 110:490] = 0
    cv2.rectangle(img, (110, 215), (490, 325), 255, 3, AA)
    fit(img, (124, 222, 476, 272), "INDIA RUBBER", "small_caps", 36, spacing=3)
    fit(img, (124, 274, 476, 320), "No. 5", "body_italic", 34)
    return {"eraser": img}


SCROLL_LINES = ["Not for lobbying,", "not for campaigns,", "not for politics,", "we swear."]


@generated
def scroll(p):
    W, H = 900, 1300
    img = canvas(W, H)
    x0, x1 = 110, W - 110
    # the sheet, its edges curling into the rollers
    sheet = np.zeros((H, W), bool)
    sheet[150:H - 150, x0:x1] = True
    for x in (x0, x1):
        cv2.line(img, (x, 150), (x, H - 150), 255, 4, AA)
    for y, sgn in ((150, 1), (H - 150, -1)):  # shading where the sheet turns under the roller
        m = np.zeros((H, W), bool)
        m[min(y, y + sgn * 60):max(y, y + sgn * 60), x0:x1] = True
        hatch(img, m, 0, 7, 2)
    fit(img, (x0 + 24, 240, x1 - 24, 340), "RESOLVED", "display", 76, spacing=8)
    cv2.line(img, (x0 + 120, 350), (x1 - 120, 350), 255, 3, AA)
    y = 450
    for s in SCROLL_LINES:
        fit(img, (x0 + 30, y - 46, x1 - 30, y + 46), s, "body_italic" if s == "we swear." else "body", 60)
        y += 92
    # the fine print below: too small to read, as fine print is
    clauses = ["the foregoing subject to the discretion of the board", "the details will be shown in the coming months",
               "terms to be announced"]
    room = int((H - 150 - 60 - 16 - 14 - y) // 28) + 1  # the lines that clear the bottom roller's shading
    n, fine = 1, ""
    while True:  # as many whole clauses as fit, ending on a full stop
        trial = "; ".join(clauses[i % 3] for i in range(n)) + "."
        if len(wrap(trial, "body", 22, x1 - x0 - 100)) > room:
            break
        fine, n = trial, n + 1
    for ln in wrap(fine, "body", 22, x1 - x0 - 100):
        fit(img, (x0 + 30, y - 14, x1 - 30, y + 14), ln, "body", 22, margin=0.0)
        y += 28
    # the rollers: shaded cylinders with turned knobs
    for cy in (100, H - 100):
        m = np.zeros((H, W), bool)
        m[cy - 50:cy + 50, x0 - 30:x1 + 30] = True
        for k, (dy, pitch) in enumerate(((-50, 5), (-30, 9), (10, 14), (30, 7))):
            band = np.zeros((H, W), bool)
            band[cy + dy:cy + dy + 20 + (10 if k == 2 else 0), x0 - 30:x1 + 30] = True
            hatch(img, band & m, 0, pitch, 2)
        cv2.rectangle(img, (x0 - 30, cy - 50), (x1 + 30, cy + 50), 255, 5, AA)
        for cx in (x0 - 62, x1 + 62):
            cv2.ellipse(img, (cx, cy), (32, 64), 0, 0, 360, 255, 5, AA)
            cv2.ellipse(img, (cx, cy), (14, 30), 0, 0, 360, 255, 3, AA)
            m = np.zeros((H, W), np.uint8)
            cv2.ellipse(m, (cx, cy), (32, 64), 0, 0, 360, 1, -1)
            hatch(img, m.astype(bool), 90, 8, 2)
    return {"scroll": img}


TRANSFER = ("For Value Received, ________________________ hereby sell, assign and transfer unto "
            "________________________ ____________ Shares of the Capital Stock represented by the within "
            "Certificate, and do hereby irrevocably constitute and appoint ________________________ Attorney to "
            "transfer the said Stock on the books of the within-named Company, with full power of substitution in "
            "the premises.")


@generated
def transfer_form(p):
    """The certificate's back, at the sheet's size: a green lathe border and the printed assignment form."""
    W, H = int(C.W), int(C.H)
    g, k = canvas(W, H), canvas(W, H)
    x0, y0, x1, y1 = 140, 140, W - 140, H - 140
    C.guilloche_band(g, (x0 + 70, y0 + 70, x1 - 70, y1 - 70), 50, -60, -8, 2, 260, 5, 2)
    for off, wd in ((0, 5), (12, 2), (130, 2), (140, 4)):
        cv2.rectangle(g, (x0 + off, y0 + off), (x1 - off, y1 - off), 255, wd, AA)
    C.rosette(g, W / 2, H / 2 + 120, 60, 760, 16, 5, 1, inner_scale=0.5)  # the faint underprint
    g_under = (g.astype(np.float32) * 1.0).astype(np.uint8)
    fit(k, (400, 420, W - 400, 620), "ASSIGNMENT AND TRANSFER", "display", 150, spacing=18)
    cv2.line(k, (W // 2 - 1300, 640), (W // 2 + 1300, 640), 255, 4, AA)
    cv2.line(k, (W // 2 - 1300, 654), (W // 2 + 1300, 654), 255, 2, AA)
    y = 850
    for ln in wrap(TRANSFER, "body", 84, W - 1100):
        fit(k, (520, y - 64, W - 520, y + 64), ln, "body", 84, margin=0.0)
        y += 128
    y += 110
    for lab, xc in (("Dated", W * 0.3), ("In the presence of", W * 0.68)):
        fit(k, (xc - 760, y - 60, xc - 230, y + 50), lab, "body_italic", 72, align="r")
        cv2.line(k, (int(xc - 220), y + 18), (int(xc + 520), y + 18), 255, 3, AA)
    y += 240
    cv2.line(k, (int(W * 0.5), y), (int(W * 0.82), y), 255, 3, AA)
    fit(k, (W * 0.5, y + 20, W * 0.82, y + 100), "Signature of Holder", "body_italic", 56)
    y += 260
    fit(k, (420, y - 34, W - 420, y + 30), "NOTICE: THE SIGNATURE TO THIS ASSIGNMENT MUST CORRESPOND WITH THE NAME AS WRITTEN UPON",
        "small_caps", 44, margin=0.0)
    fit(k, (420, y + 28, W - 420, y + 92), "THE FACE OF THE CERTIFICATE IN EVERY PARTICULAR, WITHOUT ALTERATION OR ENLARGEMENT.",
        "small_caps", 44, margin=0.0)
    fit(k, (420, y + 135, W - 420, y + 205), "Transfers to the Fund are made at the Company's discretion. Baseline, governance "
           "and valuation milestones to be announced.", "body_italic", 40, margin=0.0)
    return {"transfer_form": k, "transfer_form_green": g_under}


@generated
def face_down(p):
    """The second document's back: its print shows through the paper, reversed and soft, and can't be read."""
    W, H = 2200, 1700
    front = canvas(W, H)
    fit(front, (200, 140, W - 200, 300), "MEMORANDUM", "display", 120, spacing=12)
    y = 420
    body = ("Private and confidential. Re: the arrangements discussed, to be read in conjunction with the "
            "foregoing and not to be circulated. ") * 10
    for ln in wrap(body, "body", 52, W - 500)[:18]:
        fit(front, (200, y - 33, W - 200, y + 33), ln, "body", 52, margin=0.0)
        y += 66
    through = cv2.GaussianBlur(front[:, ::-1], (0, 0), 9).astype(np.float32) * 0.3
    img = through.astype(np.uint8)
    cv2.rectangle(img, (4, 4), (W - 4, H - 4), 120, 3, AA)
    return {"face_down": img}


TICKS = ["+50%", "+100%", "+150%", "+200%", "+250%"]


@generated
def thermometer_scale(p):
    """The stub's thermometer, sized to the stub (560 x 2400 px of sheet): a glass tube shaded as a cylinder, rising
    from a rounded foot to a hatched bulb at the top, its scale in +50% steps; the ribbon across the bulb reads
    BASELINE: TBA. Written as the glass (tube, bulb, scale), the ribbon and the column of spirit, so the scene can
    raise the column and show the ribbon on its own cue, plus all three together for the sheet."""
    W, H = 560, 2400
    glass, ribbon, column = canvas(W, H), canvas(W, H), canvas(W, H)
    cx, tw = TH_GEOM["cx"], TH_GEOM["tw"]
    top, foot = TH_GEOM["top"], TH_GEOM["foot"]
    tube = np.zeros((H, W), np.uint8)
    cv2.rectangle(tube, (cx - tw // 2, top), (cx + tw // 2, foot), 1, -1)
    cv2.circle(tube, (cx, foot), tw // 2, 1, -1)
    tube = tube.astype(bool)
    yy, xx = np.mgrid[0:H, 0:W]
    edge = np.abs(xx - cx) / (tw / 2)         # 0 at the axis, 1 at the glass's edge
    hatch(glass, tube & (edge > 0.62) & (xx < cx), 90, 7, 2)   # the glass's shaded flanks; the axis stays clear
    hatch(glass, tube & (edge > 0.5) & (xx > cx), 90, 6, 2)
    hatch(glass, tube & (edge > 0.8) & (xx > cx), 90, 3, 2)
    cv2.rectangle(glass, (cx - tw // 2, top), (cx + tw // 2, foot), 255, 6, AA)
    cv2.ellipse(glass, (cx, foot), (tw // 2, tw // 2), 0, 0, 180, 255, 6, AA)
    marks = TH_GEOM["marks"]
    for i, y in enumerate(marks):
        cv2.line(glass, (cx + tw // 2 + 6, y), (cx + tw // 2 + 54, y), 255, 6, AA)
        fit(glass, (cx + tw // 2 + 62, y - 56, W - 12, y + 56), TICKS[i], "small_caps", 110, align="l", margin=0.04)
        if i:
            for k in range(1, 5):
                yk = int(y + (marks[i - 1] - y) * k / 5)
                cv2.line(glass, (cx + tw // 2 + 6, yk), (cx + tw // 2 + 28, yk), 255, 3, AA)
    by, r = TH_GEOM["bulb_y"], TH_GEOM["bulb_r"]
    ball = np.zeros((H, W), np.uint8)
    cv2.circle(ball, (cx, by), r, 1, -1)
    ball = ball.astype(bool)
    lit = np.hypot(xx - (cx - r * 0.37), yy - (by - r * 0.37)) / (r * 1.5)
    for lo, ang, pitch in ((0.45, 30, 9), (0.7, -30, 8), (0.9, 90, 6)):
        hatch(glass, ball & (lit > lo), ang, pitch, 2)
    cv2.circle(glass, (cx, by), r, 255, 7, AA)
    for sx in (-1, 1):
        cv2.line(glass, (cx + sx * tw // 2, top), (cx + sx * tw // 2, by + int(r * 0.93)), 255, 6, AA)
    # the column of spirit, full height (the scene scales it from the foot)
    column[top + 40:foot, cx - TH_GEOM["col_w"] // 2:cx + TH_GEOM["col_w"] // 2] = 255
    cv2.circle(column, (cx, foot), 30, 255, -1, AA)
    # the ribbon across the bulb
    rb = [(14, by - 62), (W - 14, by - 62), (W - 64, by), (W - 14, by + 62), (14, by + 62), (64, by)]
    m = poly_mask(ribbon.shape, rb)
    outline(ribbon, rb, 6)
    fit(ribbon, (70, by - 52, W - 70, by + 52), "BASELINE: TBA", "small_caps", 84, spacing=4)
    full = np.maximum(glass, column)
    full[m] = 0
    np.maximum(full, ribbon, out=full)
    g2 = glass.copy()
    g2[m] = 0
    rib = ribbon.copy()
    return {"thermometer_glass": g2, "thermometer_ribbon": rib, "thermometer_column": column, "thermometer_full": full,
            "thermometer_ribbon_mask": (m * 255).astype(np.uint8)}


# the thermometer's geometry in its own pixels, shared with the scene (config written beside the ink)
TH_GEOM = {"cx": 170, "tw": 100, "top": 470, "foot": 2280, "bulb_y": 290, "bulb_r": 150, "col_w": 30,
           "marks": [int(2160 - (2160 - 760) * i / 4) for i in range(5)]}


@generated
def seal(p):
    """The corporate seal's die (its legend round a rosette, THRESHOLD MET* at its centre) and the embossed impression it leaves (a height map)."""
    W = 900
    c = W / 2
    img = canvas(W, W)
    for r, wd in ((c - 10, 8), (c - 30, 3), (c - 150, 3), (c - 166, 6)):
        cv2.circle(img, (int(c), int(c)), int(r), 255, wd, AA)
    for a in np.linspace(0, 2 * np.pi, 220, endpoint=False):
        r0, r1 = c - 28, c - 12
        cv2.line(img, (int(c + r0 * np.cos(a)), int(c + r0 * np.sin(a))), (int(c + r1 * np.cos(a)), int(c + r1 * np.sin(a))), 255, 2, AA)
    circle_text(img, c, c, c - 90, "AMALGAMATED BENEFIT, LLC · CORPORATE SEAL · ", "small_caps", 66, span=352)
    C.rosette(img, c, c, 30, 250, 14, 6, 2)
    cv2.circle(img, (int(c), int(c)), 196, 0, -1, AA)  # 150 until the centre had THRESHOLD to hold
    cv2.circle(img, (int(c), int(c)), 196, 255, 4, AA)
    # brief rev 50: it embosses THRESHOLD MET* (the IPO filing's RSI threshold); the footnote is set in the scene,
    # below the seal (scenes/blender/animatic.py S34). Until 2026-11-17 the centre read WHOLLY OWNED
    # (archive/props/seal_v1_wholly-owned/)
    fit(img, (c - 176, c - 104, c + 176, c - 16), "THRESHOLD", "small_caps", 62, spacing=2)
    fit(img, (c - 130, c - 14, c + 130, c + 84), "MET*", "small_caps", 92, spacing=6)
    fit(img, (c - 86, c + 96, c + 86, c + 144), "MMXXVI", "small_caps", 38, spacing=6)
    emboss = cv2.GaussianBlur(cv2.dilate(img, np.ones((5, 5), np.uint8)), (0, 0), 3)
    return {"seal": img, "seal_emboss": emboss}


@generated
def drawer_front(p):
    """S44's drawer front, at the sheet's size (the lid that slides over the certificate): a WHOLLY OWNED label holder
    ruled like the filing cabinet patent's, on a panel ruled in the same manner, with a cup pull."""
    W, H = int(C.W), int(C.H)
    img = canvas(W, H)
    for off, wd in ((30, 14), (70, 4), (110, 4)):
        cv2.rectangle(img, (off, off), (W - off, H - off), 255, wd, AA)
    m = np.zeros((H, W), bool)
    m[H - 110:H - 70, 110:W - 110] = True
    hatch(img, m, 0, 8, 3)  # the shadow under the panel's lip
    # the label holder, ruled as the cabinet patent draws its holders (a heavy outer frame, a fine inner one, rounded).
    # Placed where S44's closing frame sees the lid: the lid rides 6 cm above the sheet, nearer the camera, so the
    # PROGRESS_TIGHT framing covers only about sheet px 2170-2780 x 593-939 of it (measured on a render)
    hx0, hy0, hx1, hy1 = 2475 - 240, 715 - 85, 2475 + 240, 715 + 85
    rr = 18
    for (x0, y0, x1, y1), wd in (((hx0, hy0, hx1, hy1), 10), ((hx0 + 20, hy0 + 20, hx1 - 20, hy1 - 20), 3)):
        pts = C.rounded_rect_path(x0, y0, x1, y1, rr, 1200)[0]
        C.poly(img, pts, wd)
    m = np.zeros((H, W), bool)
    m[hy1 + 5:hy1 + 18, hx0 + 14:hx1 + 14] = True
    hatch(img, m, 0, 5, 2)  # its shadow
    fit(img, (hx0 + 30, hy0 + 30, hx1 - 30, hy1 - 30), "WHOLLY OWNED", "small_caps", 120, spacing=2)
    # the cup pull, under the label
    px, py, pw, ph = 2475, 868, 220, 80
    cv2.ellipse(img, (px, py), (pw // 2, ph // 2), 0, 0, 180, 255, 8, AA)
    cv2.line(img, (px - pw // 2, py), (px + pw // 2, py), 255, 8, AA)
    cup = np.zeros((H, W), np.uint8)
    cv2.ellipse(cup, (px, py), (pw // 2 - 14, ph // 2 - 14), 0, 0, 180, 1, -1)
    hatch(img, cup.astype(bool), 0, 7, 2)
    for sx in (-1, 1):
        cv2.circle(img, (px + sx * (pw // 2 + 26), py), 9, 255, 3, AA)
    return {"drawer_front": img}


@generated
def ledger(p):
    """Prudence's ledger, open flat: green ruling (the green plate), sepia heads and a few entries in script."""
    W, H = 1500, 1000
    k, g = canvas(W, H), canvas(W, H)
    mid = W // 2
    for side in (-1, 1):
        x_out = mid + side * 700
        top = [(mid, 60), (mid + side * 350, 40), (x_out, 70), (x_out, 950), (mid + side * 350, 930), (mid, 950)]
        outline(k, top, 5)
        for d in (8, 16):  # the page edges beneath
            outline(k, [(x_out + side * d, 70 + d), (x_out + side * d, 950 + d / 2)], 2, closed=False)
        xs = sorted([mid + side * 40, mid + side * 140, mid + side * 470, mid + side * 640])
        for x in xs:
            cv2.line(g, (x, 150), (x, 920), 255, 2, AA)
        for y in range(190, 920, 46):
            cv2.line(g, (min(mid + side * 40, x_out), y), (max(mid + side * 40, x_out), y), 255, 1, AA)
        cv2.line(g, (min(mid, x_out), 150), (max(mid, x_out), 150), 255, 4, AA)
    m = np.zeros((H, W), bool)
    m[60:950, mid - 40:mid + 40] = True
    hatch(k, m, 90, 6, 2)  # the gutter's shadow
    fit(k, (mid - 690, 72, mid - 50, 146), "LEDGER", "display", 70, spacing=10)
    fit(k, (mid + 50, 72, mid + 690, 146), "COUPONS CLIPPED", "small_caps", 46, spacing=4)
    COLS = {"No.": (40, 140), "Coupon": (140, 470), "Date": (470, 640)}
    for side, heads in ((1, ("No.", "Coupon", "Date")), (-1, ("No.", "Account", "Per Hundred"))):
        for h, (a, b_) in zip(heads, (COLS["No."], COLS["Coupon"], COLS["Date"])):
            xa, xb = sorted((mid + side * a, mid + side * b_))
            fit(k, (xa + 4, 152, xb - 4, 189), h, "body_italic", 30, margin=0.08)
    for i in range(4):
        ya, yb = 190 + 46 * i, 236 + 46 * i
        for text_, (a, b_), side in ((str(i + 1), COLS["No."], 1), (f"No. {i + 1}", COLS["Coupon"], 1),
                                     ("TBA", COLS["Date"], 1), ("5", COLS["Date"], -1)):
            xa, xb = sorted((mid + side * a, mid + side * b_))
            fit(k, (xa + 6, ya + 2, xb - 6, yb - 2), text_, "script", 40, margin=0.06)
    return {"ledger": k, "ledger_green": g}


# prints composed for the scene: base -> [(piece, centre x, centre y, width), fractions of the base]
COMPOSE = {"studio": [("mic", 0.135, 0.69, 0.095), ("mic", 0.865, 0.69, 0.095)],  # either side of Progress
           "door": [("door_plaque", 0.5, 0.272, 0.5)]}

# ---- cutout masks -------------------------------------------------------------------------------------------------

# the pieces that are paper cutouts in the scene (they float over the page): each gets <name>_mask.png, its paper
CUTOUTS = ["stamp", "coins", "quill", "eraser", "scroll", "ledger", "scissors", "seal"] + \
    [f"calendar_page_{i}" for i in range(10)]


def silhouette(ink, margin=0.012):
    """The paper a piece is cut from: its ink closed over (so hatching and open line work read as one shape), the
    holes filled, and a narrow paper margin round it, as the puppets are cut."""
    h, w = ink.shape
    k = max(3, int(min(h, w) * 0.04)) | 1
    m = cv2.morphologyEx((ink > 60).astype(np.uint8) * 255, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    ff = cv2.copyMakeBorder(m, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    fill = ff.copy()
    cv2.floodFill(fill, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 255)
    m = m | cv2.bitwise_not(fill)[1:-1, 1:-1]
    d = max(1, int(min(h, w) * margin)) | 1
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)))
    return cv2.GaussianBlur(m, (3, 3), 0)


# ---- main ----------------------------------------------------------------------------------------------------------

def main(names):
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or CFG:
        p = CFG[name]
        CURRENT[0] = name
        maps = cut(name, p) if p["kind"] == "cut" else GENERATED[name](p)
        for k, img in maps.items():
            cv2.imwrite(str(OUT / f"{k}.png"), img)
            print(f"{k}: {img.shape[1]} x {img.shape[0]}, mean ink {img.mean() / 255:.3f}")
    # prints that overlap in the scene are composed into one texture (Eevee draws only the frontmost of overlapping
    # blended surfaces): <name>_print.png
    for base, parts in COMPOSE.items():
        if names and base not in names and not any(n == q for n in names for q, *_ in parts):
            continue
        img = load_prop(base).copy()
        h, w = img.shape
        for q, fx, fy, fw in parts:
            piece = scaled(load_prop(q), int(w * fw))
            x, y = int(w * fx - piece.shape[1] / 2), int(h * fy - piece.shape[0] / 2)
            sub = img[y:y + piece.shape[0], x:x + piece.shape[1]]
            sub[silhouette(piece) > 128] = 0  # knocked out of what's behind it, as a printed vignette is
            np.maximum(sub, piece, out=sub)
        cv2.imwrite(str(OUT / f"{base}_print.png"), img)
        print(f"{base}_print: {w} x {h} ({', '.join(q for q, *_ in parts)} composed in)")
    for k in CUTOUTS:
        f = OUT / f"{k}.png"
        if f.exists() and (not names or any(k == n or k.startswith(n.rstrip("s") + "_") for n in names)):
            cv2.imwrite(str(OUT / f"{k}_mask.png"), silhouette(cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)))
    (OUT / "thermometer_geom.json").write_text(json.dumps(TH_GEOM) + "\n")
    cv2.imwrite(str(OUT / "full_mask.png"), np.full((8, 8), 255, np.uint8))  # a whole sheet of paper
    bad = [f for f in FITS if not f[4]]
    shrunk = [f for f in FITS if f[4] and f[3] < f[2]]
    print(f"type: {len(FITS)} lines set, {len(shrunk)} shrunk to fit, {len(bad)} that don't fit")
    for f in shrunk:
        print(f"  shrunk  {f[0]}: {f[1][:50]!r} {f[2]} -> {f[3]} px")
    for f in bad:
        print(f"  OVERFLOW {f[0]}: {f[1][:50]!r} at {f[3]} px")


if __name__ == "__main__":
    main(sys.argv[1:])
