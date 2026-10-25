"""Build each figure's puppet layers from its ink piece and masks (scripts/segment.py, config/puppets.json).

Every pixel of the figure belongs to exactly one layer: a part keeps its own pixels (a child's are removed from its
parent; siblings stack by z), the body keeps the rest. Wherever a layer lost pixels to a layer above it, the hole is
filled with an engraved line screen at the local tone, running along the local hatching direction (structure
tensor), so a limb that swings away uncovers engraving, not paper. The vignette behind the figure ("background") is
filled the same way, for shots where the figure steps out (S03).

Writes assets/puppets/<figure>/layers/<layer>_ink.png (8-bit ink coverage) and <layer>_mask.png (the cut; the
background's is the whole piece), and assets/puppets/<figure>/puppet.json: layer order, parents, pivots, boxes.
Usage: puppet_build.py [figure ...]
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config/puppets.json").read_text())["figures"]
PERIOD = 9.0  # px between fill lines, close to Durand's sky ruling at the pieces' resolution


def local_tone(ink, valid, sigma=22):
    """Tone around a hole, from the pixels outside it (normalised convolution), widened until it reaches."""
    v = valid.astype(np.float32)
    tone = np.zeros_like(ink)
    got = np.zeros(ink.shape, bool)
    for s in (sigma, sigma * 3, sigma * 9, sigma * 27):
        den = cv2.GaussianBlur(v, (0, 0), s)
        t = cv2.GaussianBlur(ink * v, (0, 0), s) / (den + 1e-6)
        new = ~got & (den > 0.02)
        tone[new] = t[new]
        got |= new
    return np.clip(tone, 0, 1)


def ring_angle(ink, hole, valid, width=30):
    """The dominant hatching direction in a ring around a hole: one angle per hole, so the fill can't swirl."""
    ring = (cv2.dilate(hole.astype(np.uint8), np.ones((width, width), np.uint8)) > 0) & ~hole & valid
    gx, gy = cv2.Sobel(ink, cv2.CV_32F, 1, 0, ksize=5), cv2.Sobel(ink, cv2.CV_32F, 0, 1, ksize=5)
    jxx, jyy, jxy = (float((a * ring).sum()) for a in (gx * gx, gy * gy, gx * gy))
    return 0.5 * np.arctan2(2 * jxy, jxx - jyy) if ring.any() else np.pi / 2  # gradient direction


def fill(ink, hole, valid, seed, horizontal=False):
    tone = local_tone(ink, valid)
    out = np.zeros_like(ink)
    n, lab = cv2.connectedComponents(hole.astype(np.uint8))
    for i in range(1, n):
        comp = lab == i
        theta = np.pi / 2 if horizontal else ring_angle(ink, comp, valid)
        out[comp] = line_screen(ink.shape, tone, np.full(ink.shape, theta, np.float32), seed + i)[comp]
    return out


def line_screen(shape, tone, theta, seed):
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # coordinate across the lines: the gradient direction (lines lie along the hatching)
    u = xx * np.cos(theta) + yy * np.sin(theta)
    rng = np.random.default_rng(seed)
    u += 1.4 * np.sin(xx / 41.0 + rng.uniform(0, 6.28)) + 1.1 * np.sin(yy / 53.0 + rng.uniform(0, 6.28))
    v = np.abs((u / PERIOD) % 1.0 - 0.5) * 2.0  # 0 at a line's centre, 1 midway between lines
    t = np.clip(tone * 0.8, 0, 1)  # a little lighter than its surround: a fill should recede, not compete
    return np.clip((t - v) / 0.18 + 0.5, 0, 1)  # coverage of each period ≈ tone; soft, engraved line edges


def build(name):
    f = CFG[name]
    d = ROOT / "assets/puppets" / name
    ink = cv2.imread(str(ROOT / "assets/engravings/ink" / f"{f['piece']}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    fig = cv2.imread(str(d / "masks/figure.png"), cv2.IMREAD_GRAYSCALE) > 0
    parts = f["parts"]
    own = {}
    taken = np.zeros_like(fig)
    # children before parents, higher z first: each pixel goes to the frontmost, innermost layer
    depth = lambda pn: 0 if parts[pn]["parent"] == "figure" else 1 + depth(parts[pn]["parent"])
    for pn in sorted(parts, key=lambda pn: (-depth(pn), -parts[pn]["z"])):
        m = (cv2.imread(str(d / f"masks/{pn}.png"), cv2.IMREAD_GRAYSCALE) > 0) & ~taken
        own[pn] = m
        taken |= m
    own["body"] = fig & ~taken
    seed = 41
    layers = {}
    # background: the vignette minus the figure, the figure's area filled
    bg = np.where(fig, fill(ink, fig, ~fig, seed, horizontal=True), ink)  # Durand's skies are ruled horizontally
    layers["background"] = (bg, np.ones_like(fig))
    # body and parts: each one's own pixels, plus filled holes where a layer in front of it was cut out
    covers = {"body": [pn for pn in parts if parts[pn]["parent"] == "figure"]}
    for pn in parts:
        covers[pn] = [c for c in parts if parts[c]["parent"] == pn]
    for ln in ["body"] + list(parts):
        holes = np.zeros_like(fig)
        for c in covers[ln]:
            holes |= own[c] | np.any([own[g] for g in covers.get(c, [])] or [np.zeros_like(fig)], axis=0)
        # only the part of a hole near this layer's own pixels: a head over the sky must not grow the body a
        # head-shaped paper patch; what a swing uncovers farther out is the background's fill
        near = cv2.dilate(own[ln].astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))) > 0
        holes &= near
        mask = own[ln] | holes
        layer = ink * own[ln]
        if holes.any():
            seed += 100
            layer = np.where(holes, fill(ink, holes, own[ln], seed), layer)
        layers[ln] = (layer, mask)
    out = d / "layers"
    out.mkdir(parents=True, exist_ok=True)
    spec = {"piece": f["piece"], "size": [ink.shape[1], ink.shape[0]], "layers": {}}
    for ln, (li, m) in layers.items():
        cv2.imwrite(str(out / f"{ln}_ink.png"), np.round(li * 255).astype(np.uint8))
        soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 0.8)  # a clean scissor edge, not a stair-step
        cv2.imwrite(str(out / f"{ln}_mask.png"), np.round(soft * 255).astype(np.uint8))
        if ln == "background":
            entry = {"parent": None, "z": 0, "pivot": None, "cutout": False}
        elif ln == "body":
            ys, xs = np.nonzero(m)
            entry = {"parent": "background", "z": 1, "pivot": [int(xs.mean()), int(ys.max())], "cutout": True}
        else:
            p = parts[ln]
            entry = {"parent": "body" if p["parent"] == "figure" else p["parent"], "z": 2 + p["z"] + 2 * depth(ln),
                     "pivot": p["pivot"], "cutout": True}
        spec["layers"][ln] = entry
    (d / "puppet.json").write_text(json.dumps(spec, indent=1))
    print(name, {ln: int(m.sum()) for ln, (_, m) in layers.items()})


def main(names):
    for n in names or CFG:
        build(n)


if __name__ == "__main__":
    main(sys.argv[1:])
