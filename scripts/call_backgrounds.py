"""Virtual backgrounds for the call page (the live verse, S30), two to compare (the human, 2026-11-18):

  boardroom   the empty boardroom (scenes/blender/boardroom.py), engraved: line hatching that follows each surface in
              perspective (a world coordinate's iso-lines, thickened with shadow, crossed in the darks, thinned to
              stay a few pixels apart at any distance), contour lines at creases and depth jumps, ruled sky in the
              windows; sepia ink on the certificate's paper. "Board (not joined)", in a picture.
  slide       the fund's own branded background, as companies hand them out: plain paper, a gold lathe-work frame,
              the company mark top left, the session's name and its promise bottom left. The middle stays empty,
              behind the head.

Both are printed as the certificate is: each ink multiplies the paper (linear light), as in scripts/gold_sheet.py.
Usage:
  call_backgrounds.py boardroom <pass dir> <out.png> [out width]
  call_backgrounds.py slide <out.png> [width height]
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certificate as C  # noqa: E402  (its lathe-work and type helpers)

ROOT = Path(__file__).resolve().parent.parent
LOOK = json.loads((ROOT / "config/look.json").read_text())
PAL = LOOK["palette"]
SEED = 20261118


def lin(hx):
    c = np.array([int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def paper(h, w, rng, shade=0.0):
    """The cream sheet, linear: a soft grain and an optional darkening toward the corners."""
    g = cv2.resize(rng.normal(0, 1, (h // 8 + 1, w // 8 + 1)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
    g += 0.5 * rng.normal(0, 1, (h, w)).astype(np.float32)
    p = lin(PAL["paper"])[None, None] * (1 + 0.018 * g[..., None])
    if shade:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)) / np.sqrt(2)
        p *= (1 - shade * r ** 2)[..., None]
    return p


def print_inks(p, plates):
    """Multiply each ink into the paper: plates = [(coverage 0..1, hex)]."""
    out = p.copy()
    for cov, hx in plates:
        out *= 1 - cov[..., None] * (1 - lin(hx)[None, None])
    return out


def save(path, lin_rgb, size=None):
    img = to_srgb(lin_rgb)
    if size and (img.shape[1], img.shape[0]) != size:
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), np.round(img * 255).astype(np.uint8)[..., ::-1])
    print(path, img.shape[1], "x", img.shape[0])


# ---- the boardroom -----------------------------------------------------------------------------------------------

def read16(p):
    a = cv2.imread(str(p), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
    return a[..., [2, 1, 0]], (a[..., 3] if a.shape[2] == 4 else np.ones(a.shape[:2], np.float32))


def grad_px(u):
    """|grad u| in units per pixel, one-sided where that's smaller (so a surface's edge doesn't see its neighbour)."""
    def d(axis):
        f = np.abs(np.diff(u, axis=axis, append=np.take(u, [-1], axis=axis)))
        b = np.abs(np.diff(u, axis=axis, prepend=np.take(u, [0], axis=axis)))
        return np.minimum(f, b)
    return np.hypot(d(0), d(1)) + 1e-9


def hatch(coord, cov, spacing, base=0.004):
    """Ink of the iso-lines of a world coordinate (m), `spacing` px apart on screen (between spacing/2 and spacing:
    every other line fades out as the surface recedes, so the lines never crowd), covering `cov` of the surface."""
    u0 = coord / base
    g = grad_px(u0)
    kf = np.log2(spacing * g)
    k = np.floor(kf)
    w = 1 - (kf - k)                         # the odd lines' weight in this octave
    p = 2 ** k / g                           # line pitch in px
    u = u0 / 2 ** k
    n = np.round(u)
    d = np.abs(u - n) * p                    # distance to the nearest line, px
    odd = (np.mod(n, 2) == 1)
    hw_even = cov * p / 2 * 2 / (1 + w)
    hw = np.where(odd, hw_even * w, hw_even)
    hw = np.minimum(hw, 0.48 * p)
    return np.clip(hw - d + 0.5, 0, 1) * np.clip(hw * 1.5, 0, 1)  # a line thinner than a pixel fades, not a hairline


def boardroom(src, out, out_w=None):
    src = Path(src)
    tone, a = read16(src / "tone.png")
    nrm = np.load(src / "normal.npy")
    pos = np.load(src / "position.npy")
    h, w = a.shape
    s = w / 5120                              # pixel scale against the 5120-wide design
    sky = a < 0.5
    N = nrm * 2 - 1
    P = pos * 32 - 16
    L = tone.mean(2)
    L = np.where(sky, 1.0, L / np.maximum(a, 1e-3))  # un-premultiply the edge pixels

    # tone -> ink coverage: the walls stay light, the leather and wood go dark; the far wall (behind the head) lightest
    L = L ** 0.8
    cov = np.clip((0.95 - L) / 0.85, 0, 1) ** 1.25
    ax = np.argmax(np.abs(N), 2)
    # primary lines: horizontal on walls and on anything facing the camera; along the room on floors and table tops
    prim = np.where(ax == 2, P[..., 0], P[..., 2])
    # cross lines (the darks): vertical on walls, across the room on floors
    cross = np.where(ax == 0, P[..., 1], np.where(ax == 1, P[..., 0], P[..., 1]))
    sp = 18 * s  # 9 px at 2560 wide: coarse enough not to moire when the call tile is scaled down for video
    ink = hatch(prim, np.minimum(cov, 0.6), sp)
    ink = np.maximum(ink, hatch(cross, np.clip((cov - 0.55) / 0.45, 0, 1) * 0.3, sp * 1.3))
    # the deepest shadows: a third set, diagonal in the picture plane
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    diag = (xx + yy) / np.sqrt(2)
    c3 = np.clip((cov - 0.85) / 0.15, 0, 1) * 0.3
    d3 = np.abs(diag / sp - np.round(diag / sp)) * sp
    ink = np.maximum(ink, np.clip(c3 * sp / 2 - d3 + 0.5, 0, 1) * np.clip(c3 * sp * 0.75, 0, 1))

    # contours: creases (normals turn) and depth jumps, two pixels at the design scale
    cam = np.array([0, -1.05, 1.22], np.float32)
    depth = np.linalg.norm(P - cam, axis=2)
    depth = np.where(sky, 60, depth)
    edge = np.zeros((h, w), bool)
    for dy, dx in ((0, 1), (1, 0)):
        Nn = np.roll(N, (-dy, -dx), (0, 1))
        dn = (N * Nn).sum(2) < 0.85
        dd = np.abs(np.log(np.roll(depth, (-dy, -dx), (0, 1)) / depth)) > 0.03
        edge |= dn | dd
    edge = cv2.dilate(edge.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
                      iterations=max(1, round(s)))
    edge = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 0.6 * s)
    ink = np.maximum(ink, np.clip(edge * 1.2, 0, 1) * 0.92)

    # sky through the windows: a few ruled lines, as engravers drew a sky
    ruled = np.abs(yy / (sp * 1.4) - np.round(yy / (sp * 1.4))) * sp * 1.4
    ink = np.where(sky, np.clip(0.9 * s - ruled + 0.5, 0, 1) * 0.6, ink)

    rng = np.random.default_rng(SEED)
    pp = paper(h, w, rng, shade=0.10)
    img = print_inks(pp, [(ink.astype(np.float32), PAL["ink_sepia"])])
    W = out_w or w // 2
    save(out, img, (W, W * h // w))


# ---- the slide ---------------------------------------------------------------------------------------------------

def slide(out, W=3840, H=2160):
    rng = np.random.default_rng(SEED)
    g = np.zeros((H, W), np.uint8)  # gold plate
    k = np.zeros((H, W), np.uint8)  # sepia plate
    m = 70
    box = (m, m, W - m, H - m)
    # the frame: a lathe band between fine rules, as on the certificate's border, kept to the edge
    C.guilloche_band(g, (m + 70, m + 70, W - m - 70, H - m - 70), 40, -46, -6, 2, 160, 6, 2)
    for off, wd in ((0, 5), (10, 2), (98, 2), (106, 4)):
        cv2.rectangle(g, (box[0] + off, box[1] + off), (box[2] - off, box[3] - off), 255, wd, C.AA)
    # the mark, top left: a small rosette and the company
    cx, cy = 330, 330
    C.rosette(g, cx, cy, 20, 92, 10, 7, 2)
    C.text(k, (cx, cy + 4), "AB", "display", 72)  # the company's initials (a lone A could be read as a real mark)
    C.text(k, (cx + 150, cy - 26), LOOK["company"], "small_caps", 64, anchor="lm", spacing=7)
    C.text(k, (cx + 152, cy + 44), "Public Benefit Fund", "body_italic", 52, anchor="lm")
    f = C.font("small_caps", 64)
    wd = sum(f.getlength(ch) + 7 for ch in LOOK["company"])
    cv2.line(k, (cx + 150, cy + 6), (int(cx + 150 + wd), cy + 6), 255, 2, C.AA)
    # bottom left: the session and its promise, with the footnote the certificate's seal taught us to read
    x, y = 250, H - 400
    C.text(k, (x, y), "STAKEHOLDER INPUT SESSION", "small_caps", 46, anchor="lm", spacing=6)
    cv2.line(g, (x, y + 40), (x + 860, y + 40), 255, 3, C.AA)
    C.text(k, (x, y + 112), "Your input matters.*", "body_italic", 74, anchor="lm")
    C.text(k, (x, y + 200), "*Input is advisory and non-binding.", "body", 34, anchor="lm")
    # the middle: nothing but paper (the head goes there); a faint underprint rosette, bottom right, to balance the mark
    under = np.zeros((H, W), np.uint8)
    C.rosette(under, W - 520, H - 520, 60, 300, 16, 12, 2)
    gc = g.astype(np.float32) / 255
    kc = k.astype(np.float32) / 255
    uc = under.astype(np.float32) / 255 * 0.35
    img = print_inks(paper(H, W, rng, shade=0.06), [(np.maximum(gc, uc), PAL["ink_gold"]), (kc, PAL["ink_sepia"])])
    save(out, img)


if __name__ == "__main__":
    if sys.argv[1] == "boardroom":
        boardroom(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        slide(sys.argv[2], *(int(v) for v in sys.argv[3:5]))
