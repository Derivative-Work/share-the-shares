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


CELL, PAD, SEARCH = 24, 14, 280  # synthesis cell, overlap border and search radius, in piece pixels


def synth(ink, hole, valid, seed):
    """Fill `hole` with real engraving copied from `valid` pixels nearby (exemplar-based texture synthesis, after
    Efros and Leung 1999 / Criminisi et al. 2004, simplified). Cells of CELL px are filled from the hole's edge
    inward; each takes the patch, within SEARCH px, whose already-known surround (a PAD-px border) best matches by
    masked squared difference, so hatching runs on across the seam with its own line, tone and direction. Sources
    are whole patches of untouched pixels only, so nothing synthesised is ever copied again."""
    rng = np.random.default_rng(seed)
    h, w = ink.shape
    out = ink.copy()
    known = ~hole
    win = CELL + 2 * PAD
    src_ok = cv2.erode(valid.astype(np.uint8), np.ones((win, win), np.uint8)) > 0  # patch centres fully in `valid`
    if not src_ok.any():
        return out
    ys, xs = np.nonzero(hole)
    gy0, gx0 = ys.min() // CELL * CELL, xs.min() // CELL * CELL
    todo = {(y, x) for y in range(gy0, ys.max() + 1, CELL) for x in range(gx0, xs.max() + 1, CELL)
            if hole[y:y + CELL, x:x + CELL].any()}
    tries = {}
    while todo:
        # the cells with the most known surround go first (onion peel)
        scored = []
        for (y, x) in todo:
            k = known[max(0, y - PAD):y + CELL + PAD, max(0, x - PAD):x + CELL + PAD]
            scored.append((k.mean(), (y, x)))
        scored.sort(reverse=True)
        batch = [c for f, c in scored[:max(1, len(scored) // 8)] if f > 0.05] or [scored[0][1]]
        for (y, x) in batch:
            tries[(y, x)] = tries.get((y, x), 0) + 1
            if tries[(y, x)] > 6:
                todo.discard((y, x))  # unreachable (no valid source near it): left to the mean-tone pass below
                continue
            wy0, wx0 = y - PAD, x - PAD
            if wy0 < 0 or wx0 < 0 or wy0 + win > h or wx0 + win > w:
                # at the piece's edge: fall back to the nearest valid pixel's value (the vignette fades out there)
                sel = hole[y:y + CELL, x:x + CELL] & ~known[y:y + CELL, x:x + CELL]
                out[y:y + CELL, x:x + CELL][sel] = 0.0
                known[y:y + CELL, x:x + CELL] |= sel
                todo.discard((y, x))
                continue
            tmpl = out[wy0:wy0 + win, wx0:wx0 + win].astype(np.float32)
            m = known[wy0:wy0 + win, wx0:wx0 + win].astype(np.float32)
            sy0, sx0 = max(0, wy0 - SEARCH), max(0, wx0 - SEARCH)
            sy1, sx1 = min(h, wy0 + win + SEARCH), min(w, wx0 + win + SEARCH)
            area = ink[sy0:sy1, sx0:sx1].astype(np.float32)
            ok = src_ok[sy0 + win // 2:sy1 - win + win // 2 + 1, sx0 + win // 2:sx1 - win + win // 2 + 1]
            if not ok.any() or m.sum() < 1:
                continue  # retried next round once more of its surround is known
            score = cv2.matchTemplate(area, tmpl, cv2.TM_SQDIFF, mask=m)
            # tone: a source whose mean ink is far from the known surround's can't win on line placement alone (bare
            # paper otherwise "matches" faint sky: its error is only the dashes it lacks)
            tm = float((tmpl * m).sum() / m.sum())
            am = cv2.boxFilter(area, -1, (win, win), normalize=True, anchor=(0, 0),
                               borderType=cv2.BORDER_CONSTANT)[:score.shape[0], :score.shape[1]]
            tone_ok = (np.abs(am - tm) <= 0.3 * tm + 0.01) & (am >= 0.7 * tm)
            score = np.where(ok[:score.shape[0], :score.shape[1]] & tone_ok, score, np.inf)
            # pick among the best few, so a large hole isn't one patch repeated
            flat = np.argsort(score, axis=None)[:4]
            flat = flat[np.isfinite(score.ravel()[flat])]
            if not len(flat):
                continue
            py, px = np.unravel_index(rng.choice(flat), score.shape)
            patch = area[py + PAD:py + PAD + CELL, px + PAD:px + PAD + CELL]
            cell_hole = ~known[y:y + CELL, x:x + CELL]
            out[y:y + CELL, x:x + CELL][cell_hole] = patch[:cell_hole.shape[0], :cell_hole.shape[1]][cell_hole]
            known[y:y + CELL, x:x + CELL] = True
            todo.discard((y, x))
        todo = {c for c in todo if (~known[c[0]:c[0] + CELL, c[1]:c[1] + CELL] & hole[c[0]:c[0] + CELL, c[1]:c[1] + CELL]).any()}
    rest = hole & ~known
    if rest.any():  # cells no source could reach: the local mean tone, as a flat tint (the background only; a
        out[rest] = local_tone(ink, valid)[rest]  # cutout drops them from its mask instead: see build)
    return np.where(hole, out, ink), rest


def fill(ink, hole, valid, seed, horizontal=False):
    """Texture synthesis from the surrounding engraving (synth): the filled ink and the cells it couldn't reach."""
    return synth(ink, hole, valid, seed)


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
    # SAM's slivers along the traced cuts (a limb's outline stroke, a spear's edge) would stay behind on the body as
    # thin paper strips: each goes to the part it touches most, or, touching none, to the background's static print
    rest = (fig & ~taken).astype(np.uint8)
    own["body"] = cv2.morphologyEx(rest, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))) > 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(((rest > 0) & ~own["body"]).astype(np.uint8), connectivity=8)
    grown = {pn: cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0 for pn, m in own.items() if pn != "body"}
    for i in range(1, n):
        x, y, w, h = st[i, :4]
        sl = lab[y:y + h, x:x + w] == i
        touch = {pn: int((g[y:y + h, x:x + w] & sl).sum()) for pn, g in grown.items()}
        best = max(touch, key=touch.get) if touch else None
        if best and touch[best] > 0:
            own[best][y:y + h, x:x + w] |= sl
    fig = own["body"] | np.any([own[pn] for pn in parts], axis=0)
    seed = 41
    layers = {}
    # background: the vignette minus the figure, the figure's area filled
    bg = np.where(fig, fill(ink, fig, ~fig, seed)[0], ink)
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
            filled, unreached = fill(ink, holes, own[ln], seed)
            layer = np.where(holes, filled, layer)
            mask &= ~unreached  # no flat tint on a cutout: what lies under the cell (the background's fill) shows
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
