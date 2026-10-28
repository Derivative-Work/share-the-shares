"""S11's microprint: the company banner's green underprint, where the camera pushes in, redrawn at K times the sheet's
resolution with each lathe strand set as a line of tiny letters, LLC LLC LLC (brief: "the guilloche pattern, looked
at closely, is the letters LLC repeated"). At the sheet's own scale the letters read as the strand they replace; as
the push closes in they resolve into type. The sepia type over it is redrawn at the same resolution, and the paper's
grain is the sheet's own (scripts/certificate.py print_sheet), so the patch matches the sheet around it.

The strands are the banner underprint's (scripts/certificate.py build: guilloche_band(under, (x0 + 560, 1285,
x1 - 560, 1475), 80, -60, 60, 1, 60, 9, 1) at 55%), computed from the same formula, finer.

Writes renders/c1/microprint/: color.png (paper and inks, as the print), green.png and sepia.png (the plates, for the
ink's relief), region.json (the sheet-pixel box and K); checks the patch, reduced to the sheet's scale, against the
static print (scenes/blender/animatic.py shows it over the sheet in S11 only).
Usage: .venv/bin/python -I scripts/microprint.py
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certificate as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CERT = ROOT / "renders/c1/certificate_v05"
OUT = ROOT / "renders/c1/microprint"
REGION = (870, 1100, 1710, 1600)   # sheet px: S11's opening framing (GUILLOCHE), with a margin for the camera's lean
K = 16                             # patch px per sheet px (13440 x 8000; GPU textures stop at 16384)
WORD = "LLC "
CAP = 2.4                          # the letters' cap height, sheet px (the strand they replace is 1 px)
MAIN_X = (620, C.W - 70)        # the main panel's sides (scripts/certificate.py build: STUB + 60, W - 70)
INK = 0.75                         # the strands' ink (the underprint prints at 0.55; the letters cover less of the line)


def strands():
    """The underprint's nine strands as dense polylines (sheet px)."""
    x0, x1 = MAIN_X
    box, r, inner, outer, freq, lines = (x0 + 560, 1285, x1 - 560, 1475), 80, -60, 60, 60, 9
    pts, nrm, _ = C.rounded_rect_path(*box, r, n=240000)
    s = np.linspace(0, 1, len(pts), endpoint=False)
    mid, amp = (inner + outer) / 2, (outer - inner) / 2
    for k in range(lines):
        ph = 2 * np.pi * (k / lines)
        d = mid + amp * (0.82 * np.sin(2 * np.pi * freq * s + ph) + 0.18 * np.sin(2 * np.pi * freq * 3 * s - ph))
        yield pts + nrm * d[:, None]


def glyphs():
    """Each letter at the patch's scale, white on black, with its advance (patch px)."""
    f = C.font("small_caps", 10)
    cap = f.getbbox("L")[3] - f.getbbox("L")[1]
    f = C.font("small_caps", int(round(10 * CAP * K / cap)))
    out = {}
    for ch in set(WORD):
        adv = f.getlength(ch)
        w, h = int(adv) + 8, int(CAP * K * 2.2)
        im = Image.new("L", (w, h), 0)
        ImageDraw.Draw(im).text((w / 2, h / 2), ch, font=f, fill=255, anchor="mm")
        out[ch] = (im, adv)
    return out


def green_plate():
    x0, y0, x1, y1 = REGION
    W, H = (x1 - x0) * K, (y1 - y0) * K
    g = Image.new("L", (W, H), 0)
    gl = glyphs()
    for line in strands():
        inside = ((line[:, 0] > x0 - 10) & (line[:, 0] < x1 + 10) & (line[:, 1] > y0 - 10) & (line[:, 1] < y1 + 10))
        seg = np.diff(line, axis=0)
        arc = np.concatenate([[0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
        a, i = 0.0, 0
        while a < arc[-1]:
            ch = WORD[i % len(WORD)]
            im, adv = gl[ch]
            c = a + adv / K / 2
            j = min(np.searchsorted(arc, c), len(line) - 2)
            if inside[j] and ch != " ":
                t = line[j + 1] - line[j]
                ang = np.degrees(np.arctan2(t[1], t[0]))
                rot = im.rotate(-ang, resample=Image.BICUBIC, expand=True)
                px, py = (line[j, 0] - x0) * K, (line[j, 1] - y0) * K
                box = (int(round(px - rot.width / 2)), int(round(py - rot.height / 2)))
                sub = g.crop((*box, box[0] + rot.width, box[1] + rot.height))
                g.paste(Image.fromarray(np.maximum(np.asarray(sub), np.asarray(rot))), box)
            a += adv / K
            i += 1
    return (np.asarray(g, np.float32) * INK).astype(np.uint8)


def sepia_plate():
    """The sheet's sepia type in the region, set again at K times the size (scripts/certificate.py build)."""
    x0, y0, x1, y1 = REGION
    W, H = (x1 - x0) * K, (y1 - y0) * K
    big = np.zeros((H, W), np.uint8)
    cx = sum(MAIN_X) // 2
    for (x, y), s, role, size, spacing in (((cx, 1380), C.LOOK["company"], "display", 150, 10),
                                           ((cx, 1520), "ORGANIZED AS A LIMITED LIABILITY COMPANY  ·  WHOLLY OWNED",
                                            "small_caps", 56, 6)):
        C.text(big, ((x - x0) * K, (y - y0) * K), s, role, size * K, spacing=spacing * K)
    return big


def paper():
    """The sheet's paper and grain over the region, from the same seed and recipe as print_sheet, finer."""
    rng = np.random.default_rng(C.SEEDS["paper_grain"])
    grain = cv2.GaussianBlur(rng.standard_normal((C.H // 4, C.W // 4)).astype(np.float32), (0, 0), 1.2)
    x0, y0, x1, y1 = REGION
    # the sheet resizes grain (W/4) to W with INTER_CUBIC: sample the same cubic at the patch's finer pixel centres
    W, H = (x1 - x0) * K, (y1 - y0) * K
    xs = ((np.arange(W) + 0.5) / K + x0) / 4 - 0.5
    ys = ((np.arange(H) + 0.5) / K + y0) / 4 - 0.5
    mx, my = np.meshgrid(xs.astype(np.float32), ys.astype(np.float32))
    g = cv2.remap(grain, mx, my, cv2.INTER_CUBIC)
    return np.ones((H, W, 3), np.float32) * C.hexrgb(C.LOOK["palette"]["paper"]) * (1 + 0.018 * g)[..., None]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    g, k = green_plate(), sepia_plate()
    out = paper()
    for plate, col in ((g, C.LOOK["palette"]["ink_green"]), (k, C.LOOK["palette"]["ink_sepia"])):
        a = (plate.astype(np.float32) / 255.0)[..., None]
        out = out * (1 - a + a * C.hexrgb(col))
    color = np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(color).save(OUT / "color.png")
    cv2.imwrite(str(OUT / "green.png"), g)
    cv2.imwrite(str(OUT / "sepia.png"), k)
    (OUT / "region.json").write_text(json.dumps({"box": REGION, "k": K, "word": WORD, "cap_px": CAP}) + "\n")
    # the check: reduced to the sheet's scale, the patch should match the static print it covers
    x0, y0, x1, y1 = REGION
    ref = np.asarray(Image.open(CERT / "static/sheet.png").convert("RGB"))[y0:y1, x0:x1].astype(np.float32)
    small = cv2.resize(color, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32)
    kref = cv2.imread(str(CERT / "static/plate_sepia.png"), 0)[y0:y1, x0:x1].astype(np.float32)
    ksm = cv2.resize(k, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32)
    blur = lambda x: cv2.GaussianBlur(x, (0, 0), 3)  # noqa: E731  the tone at a glance, not the strands' exact pixels
    print(f"{OUT}: {color.shape[1]} x {color.shape[0]} (K {K}); sepia vs sheet: mean |diff| {np.abs(ksm - kref).mean():.2f}"
          f" (of 255); print vs sheet, blurred 3 px: mean |diff| {np.abs(blur(small) - blur(ref)).mean():.2f}, max "
          f"{np.abs(blur(small) - blur(ref)).max():.1f}")


if __name__ == "__main__":
    main()
