"""Bake the laborer's raised hammer into a new ink piece (config/laborer.json).

The forearm and the hammer are cut by hand (scripts/segment.py's cut_by_hand), the hole they leave is filled by
texture synthesis from the engraving around it (scripts/puppet_build.py's fill), and the two pieces are pasted back
turned: the forearm about the elbow, the hammer about the fist and then with the forearm. Pasted pieces are opaque
(cut paper over the print), with the puppets' soft scissor edge.
Usage: laborer_raise.py  ->  assets/engravings/ink/laborer_raised.png, assets/puppets/laborer/raise_preview.jpg
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from puppet_build import fill  # noqa: E402
from segment import cut_by_hand  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/laborer.json").read_text())


def rot(pivot, deg):
    return np.vstack([cv2.getRotationMatrix2D(tuple(float(v) for v in pivot), deg, 1.0), [0, 0, 1]])


def main():
    raw = cv2.imread(str(ROOT / "assets/engravings/ink/laborer.png"), cv2.IMREAD_GRAYSCALE)
    ink = raw.astype(np.float32) / 255
    h, w = ink.shape
    fa, hm = (cut_by_hand(raw, CFG[k]["cut"]) for k in ("forearm", "hammer"))
    hm &= ~fa
    hole = fa | hm
    # a tight search keeps the shirt's hatching on the shirt and the forge's glow on the forge; cells it can't reach
    # get a second pass with the usual radius (sources are still original ink only)
    base, unreached = fill(ink, hole, ~hole, 41, search=CFG["search"])
    if unreached.any():
        base, unreached = fill(np.where(unreached, 0, base), unreached, ~hole, 42)
    # cv2 angles are counter-clockwise with y down, i.e. counter-clockwise on the page, as in the config
    A_fa = rot(CFG["forearm"]["pivot"], CFG["forearm"]["angle"])
    A_hm = A_fa @ rot(CFG["hammer"]["pivot"], CFG["hammer"]["angle"])
    out = base.copy()
    for m, A in ((hm, A_hm), (fa, A_fa)):  # hammer first: the fist closes over its handle
        M = A[:2]
        pi = cv2.warpAffine(ink * m, M, (w, h), flags=cv2.INTER_LINEAR)
        pm = cv2.warpAffine(m.astype(np.float32), M, (w, h), flags=cv2.INTER_LINEAR)
        pm = cv2.GaussianBlur(pm, (0, 0), 0.8)
        out = np.where(pm > 1e-3, pi / np.maximum(pm, 1e-3) * pm + out * (1 - pm), out)
    cv2.imwrite(str(ROOT / "assets/engravings/ink/laborer_raised.png"), np.round(np.clip(out, 0, 1) * 255).astype(np.uint8))
    d = ROOT / "assets/puppets/laborer"
    d.mkdir(parents=True, exist_ok=True)
    prev = np.hstack([255 - raw, np.round((1 - np.clip(out, 0, 1)) * 255).astype(np.uint8)])
    cv2.imwrite(str(d / "raise_preview.jpg"), cv2.resize(prev, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA))
    print("hole", int(hole.sum()), "unreached", int(unreached.sum()))


if __name__ == "__main__":
    main()
