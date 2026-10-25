"""Cut ink pieces from the public-domain engravings (config/engravings.json) as clean ink-coverage maps.

The scans carry foxing, stains and each sheet's own paper tone. Dividing by a paper-level estimate (a grey closing,
which removes the lines, then a blur) flattens the paper to white, so every piece prints in one ink on the
certificate's own paper. Usage: ink_extract.py [name ...]  (default: every piece)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/engravings/source"
OUT = ROOT / "assets/engravings/ink"


def ink_map(gray, levels):
    g = gray.astype(np.float32) / 255.0
    # Paper level: a closing wider than any engraved line erases the ink, the blur smooths the stains' edges.
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    paper = cv2.GaussianBlur(cv2.morphologyEx(g, cv2.MORPH_CLOSE, k), (0, 0), 25)
    ink = np.clip(1.0 - g / np.maximum(paper, 1e-3), 0.0, 1.0)
    lo, hi = levels
    return np.clip((ink - lo) / (hi - lo), 0.0, 1.0)


def ellipse_mask(h, w, feather):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - (w - 1) / 2) / (w / 2)) ** 2 + ((yy - (h - 1) / 2) / (h / 2)) ** 2)
    f = feather * min(h, w) / (min(h, w) / 2)  # feather in normalised radius units
    t = np.clip((1.0 - r) / f, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def main(names):
    cfg = json.loads((ROOT / "config/engravings.json").read_text())["pieces"]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or cfg:
        p = cfg[name]
        im = cv2.imread(str(SRC / p["source"]), cv2.IMREAD_GRAYSCALE)
        h, w = im.shape
        x0, y0, x1, y1 = (int(round(v * s)) for v, s in zip(p["box"], (w, h, w, h)))
        ink = ink_map(im, p["levels"])[y0:y1, x0:x1]
        if p.get("mask") == "ellipse":
            ink *= ellipse_mask(*ink.shape, p["feather"])
        cv2.imwrite(str(OUT / f"{name}.png"), np.round(ink * 255).astype(np.uint8))
        print(name, ink.shape[1], "x", ink.shape[0], "mean ink", round(float(ink.mean()), 3))


if __name__ == "__main__":
    main(sys.argv[1:])
