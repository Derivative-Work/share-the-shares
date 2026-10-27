"""C4 animatic (inherited checkpoint: "the whole camera move in grey-box at final timing, every anchor hit, low-res").

The certificate world (certificate v05's static print, the desk, the C1 light), the five figures as the C2 puppets,
the laborer printed with his hammer raised, and every prop the shot list names. Props the engraving will carry at C5
(the studio, the calendar, the thermometer, the seal...) are set here in the certificate's own type and inks where
the brief gives their words, and as grey labelled cards where it doesn't (quill, pen, scissors, coins, ledger...).

Nothing is keyed by hand: every frame is a function of song time, from timing/timing_map.json (beats, words, shot
anchors) and config/c4_shots.json (the agent's framing per shot). The puppets move on twos (their pose is sampled at
the even frame below); the camera, a document camera, moves smoothly and cuts between shots.
  - Mouths follow the voice: inside the figure's own lines (the Founder: Progress; the Board: Prudence; the Lawyer:
    Mercury, who has no jaw cut and nods instead; the choir: the cherubs, who nod; "everyone": all of them), the jaw
    opens with the stem's loudness against its local peaks and dips (C3's envelopes), so it opens on each syllable
    and shuts in each dip, a frame ahead of the sound, in three positions (shut, half, open).
  - The cherubs sway on the beat through every chorus (at the extreme on each beat, one side then the other), and
    fade out with the outro; Mercury's feet reach on the beats.
  - Shot actions are in ACTIONS below, each tied to its shot's anchor.

Modes:
  --anchors   one still per rendered shot, at its midpoint -> <out>/anchor_<ID>.png
  --times     stills at the given song seconds -> <out>/t_<seconds>.png
  default     every --step'th frame of the rendered shots between --from and --to (song seconds)
              -> <out>/f_<frame>.png (song frame numbers at the video's fps); live and screen shots are left to the
              assembly's placeholders (scripts/animatic_assemble.py)
  --flat      every --step'th frame between --from and --to whatever the shot, seen straight down on the whole sheet
              through an orthographic camera, the desk left out (transparent): the plates the human composites onto
              the printed sheet in the live shots (brief: "warp a flat render onto the track"). Use the sheet's own
              aspect (--size 4400 3400 is its print resolution). --figures-only also leaves out the static print, so
              only the figures and props remain, on transparency.

Usage: blender -b --factory-startup --python scenes/blender/animatic.py -- --out DIR [--cert DIR] [--size W H]
       [--samples N] [--step K] [--from S] [--to S] [--anchors | --times S ... | --flat [--figures-only]]
"""
import argparse
import bisect
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import puppet as P  # noqa: E402
import sheet as S  # noqa: E402

ROOT = S.ROOT
TM = json.loads((ROOT / "timing/timing_map.json").read_text())
PLAN = json.loads((ROOT / "config/c4_shots.json").read_text())
FPS = TM["fps"]
TWOS = S.LOOK["animation_on"]
BEATS = TM["beats"]
BACK_DX = 0.40  # the certificate's back (S24) lies on the desk this far to the right (m)

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--cert", default=str(ROOT / "renders/c1/certificate_v05"))
ap.add_argument("--size", nargs=2, type=int, default=[640, 360])
ap.add_argument("--samples", type=int, default=8)
ap.add_argument("--step", type=int, default=2)
ap.add_argument("--from", dest="t0", type=float, default=0.0)
ap.add_argument("--to", dest="t1", type=float, default=None)
ap.add_argument("--anchors", action="store_true")
ap.add_argument("--times", nargs="+", type=float)
ap.add_argument("--flat", action="store_true")
ap.add_argument("--figures-only", action="store_true")
ap.add_argument("--debug-cam", type=float, default=None, help="print the camera and the sheet corners' projection at t")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
cert = Path(args.cert)
LAYOUT = json.loads((cert / "layout.json").read_text())["boxes"]
BOXES = {**LAYOUT, **PLAN["boxes"]}

# ---- time ------------------------------------------------------------------------------------------------------

SHOTS = [s for s in TM["shots"] if s["t"] is not None]
SPAN = {}
for k, s in enumerate(SHOTS):
    SPAN[s["id"]] = (s["t"], SHOTS[k + 1]["t"] if k + 1 < len(SHOTS) else TM["duration_s"])
T = {sid: t0 for sid, (t0, _) in SPAN.items()}


def shot_at(t):
    cur = None
    for s in SHOTS:
        if s["t"] <= t:
            cur = s["id"]
    return cur or "S02"


def beat_pos(t):
    """Fractional beat index at time t."""
    i = bisect.bisect_right(BEATS, t) - 1
    if i < 0:
        return 0.0
    if i >= len(BEATS) - 1:
        return float(i)
    return i + (t - BEATS[i]) / (BEATS[i + 1] - BEATS[i])


def beat_t(t0, n):
    """The time of the n'th beat at or after t0."""
    i = bisect.bisect_left(BEATS, t0 - 1e-3) + n
    return BEATS[min(i, len(BEATS) - 1)]


def ramp(t, a, b):
    if b <= a:
        return 1.0 if t >= a else 0.0
    u = min(1.0, max(0.0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


def within(t, a, b):
    return a <= t < b


def section_of(t):
    cur = None
    for s in TM["sections"]:
        if s["start"] - 0.5 <= t:
            cur = s
    return cur


FIG_SINGERS = {"progress": ("the Founder",), "prudence": ("the Board",), "mercury": ("the Lawyer",),
               "cherubs": ("choir",)}
# C3's per-frame loudness envelopes (scripts/stem_envelopes.py): the soloists on the lead stem, the choir on backing
import numpy as np  # noqa: E402

ENV = {"Vocals": np.load(ROOT / "timing/envelopes/vocals.npy"),
       "Backing Vocals": np.load(ROOT / "timing/envelopes/backing.npy")}
LEAD_F = 1         # the jaw leads the sound by a frame
GATE_PRE = 0.17    # a word's mouth may open this early (the aligner's word starts can come a few frames late)
JAW_STEPS = 2      # shut, half, open: a cut-paper jaw pops between positions


def _jaws():
    """Per figure, the jaw opening (0..1) for every video frame: inside the figure's own words (gated), the stem's
    loudness against its local peaks and dips (+-5 frames), so each syllable opens it and each dip closes it."""
    n = len(ENV["Vocals"])
    out = {}
    for fig, who in FIG_SINGERS.items():
        jaw = np.zeros(n)
        for ln in TM["lines"]:
            if not (ln["singer"].startswith(who) or ln["singer"] == "everyone"):
                continue
            stem = "Backing Vocals" if fig == "cherubs" and ln["singer"] == "everyone" else ln["stem"]
            e = ENV[stem]
            frames = set()
            for w in ln["words"]:  # gated per word: the reverb between words must not hold the mouth open
                frames.update(range(max(0, int((w["start"] - GATE_PRE) * FPS)), min(n - 1, int(w["end"] * FPS) + 2)))
            for f in sorted(frames):
                g = min(n - 1, f + LEAD_F)
                win = e[max(0, g - 5):g + 6]
                lo, hi = float(win.min()), float(win.max())
                if e[g] < 0.25:
                    continue
                rel = (e[g] - lo) / (hi - lo + 0.05)
                jaw[f] = max(jaw[f], round((0.35 + 0.65 * rel) * JAW_STEPS) / JAW_STEPS)
        out[fig] = jaw
    return out


JAW = _jaws()


def mouth(fig, t):
    """The figure's jaw opening (0, 0.5 or 1) at song time t."""
    f = int(round(t * FPS))
    return float(JAW[fig][f]) if 0 <= f < len(JAW[fig]) else 0.0


def chorus(t):
    s = section_of(t)
    return s is not None and ("Chorus" in s["name"] or s["name"] == "Outro") and "Pre" not in s["name"]


# ---- the world ---------------------------------------------------------------------------------------------------

def mat(name, rgb, rough=0.8, emit=None, alpha=None):
    m = bpy.data.materials.new(name)
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = list(rgb) + [1.0]
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = list(emit) + [1.0]
        b.inputs["Emission Strength"].default_value = 0.0
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    return m


PAPER = S.srgb(S.LOOK["palette"]["paper"])[:3]
SEPIA = S.srgb(S.LOOK["palette"]["ink_sepia"])[:3]
GREEN = S.srgb(S.LOOK["palette"]["ink_green"])[:3]
GOLD = S.srgb(S.LOOK["palette"]["ink_gold"])[:3]
M = {}


def materials():
    M["grey"] = mat("c4.grey", (0.42, 0.42, 0.42))
    M["grey_dark"] = mat("c4.grey_dark", (0.16, 0.16, 0.16))
    M["label"] = mat("c4.label", (0.95, 0.95, 0.95))
    M["sepia"] = mat("c4.sepia", [p * s for p, s in zip(PAPER, SEPIA)])
    M["green"] = mat("c4.green", [p * g for p, g in zip(PAPER, GREEN)])
    M["paper"] = mat("c4.paper", PAPER, 0.85)
    M["red"] = mat("c4.red", (0.45, 0.04, 0.03))
    M["desk_hole"] = mat("c4.hole", (0.05, 0.035, 0.025))
    M["wood"] = mat("c4.wood", (0.10, 0.06, 0.035), 0.55)
    M["seal"] = mat("c4.seal", (0.62, 0.62, 0.60), 0.5)
    M["glow"] = mat("c4.glow", GOLD, 0.6, emit=(1.0, 0.82, 0.38), alpha=0.0)


def sheet_xyz(px, py, lift, dx=0.0):
    """A point `lift` above the curled page (texts, which don't bend); on the back (dx), above the flat desk."""
    v = S.px_to_world(px, py)
    return Vector((v.x + dx, v.y, (0.0 if dx else S.curl(v.x, v.y)) + lift))


def pxyz(px, py, lift, dx=0.0):
    """A bending prop's origin: its curl comes from the sheet_curl modifier, so only the lift goes in z."""
    v = S.px_to_world(px, py)
    return Vector((v.x + dx, v.y, lift))


def px_len(n):
    return n / S.PW * S.SW


def plane(name, box, lift, material, dx=0.0):
    """A card over the sheet-pixel box, bent to the page's curl (P.curl_group) unless it lies on the back (dx)."""
    x0, y0, x1, y1 = box
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=16, size=1.0)
    ob = bpy.context.object
    ob.name = name
    ob.location = pxyz((x0 + x1) / 2, (y0 + y1) / 2, lift, dx)
    ob.scale = (px_len(x1 - x0), px_len(y1 - y0), 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if not dx:
        ob.modifiers.new("curl", "NODES").node_group = P.curl_group()
    if material:
        ob.data.materials.append(material)
    return ob


def text(name, s, role, size_px, at, lift, material, align="CENTER", dx=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = s
    cu.font = bpy.data.fonts.load(str(ROOT / S.LOOK["fonts"][role]), check_existing=True)
    cu.size = px_len(size_px)
    cu.align_x, cu.align_y = align, "CENTER"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = sheet_xyz(at[0], at[1], lift, dx)
    ob.data.materials.append(material)
    return ob


def grey_card(name, box, label, lift=0.0016, size_px=None):
    """A grey-box prop: a grey card with its name on it."""
    ob = plane(name, box, lift, M["grey"])
    x0, y0, x1, y1 = box
    t = text(name + ".label", label, "small_caps", size_px or min(y1 - y0, (x1 - x0) / max(4, len(label) * 0.6)) * 0.55,
             ((x0 + x1) / 2, (y0 + y1) / 2), lift + 0.00005, M["label"])
    parent_keep(t, ob)
    return ob


def tex_card(name, box, img, uv=(0, 0, 1, 1), lift=0.0003, dx=0.0):
    """A card printed with (part of) an image: the tiny certificates, the clipped coupons."""
    ob = plane(name, box, lift, None, dx)
    m = bpy.data.materials.new(name)
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.82
    tx = n.new("ShaderNodeTexImage")
    tx.image = S.image(img)
    tx.interpolation = "Cubic"
    l.new(tx.outputs["Color"], b.inputs["Base Color"])
    ob.data.materials.append(m)
    u0, v0, u1, v1 = uv
    for loop in ob.data.uv_layers.active.data:
        loop.uv.x = u0 + loop.uv.x * (u1 - u0)
        loop.uv.y = v0 + loop.uv.y * (v1 - v0)
    return ob


PROPS = ROOT / "assets/engravings/ink/props"  # the C5 props (scripts/props.py)
FLAT = 1e-6  # a dx that leaves a card unbent (no page curl), for cards that ride on moving props


def prop_box(prop, cx, cy, w=None, h=None):
    """The sheet-pixel box for a prop at its own aspect, centred on (cx, cy), `w` or `h` wide/high."""
    iw, ih = S.image(PROPS / f"{prop}.png", True).size
    w = w if w is not None else h * iw / ih
    h = h if h is not None else w * ih / iw
    return [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]


def prop_card(name, box, prop, lift, cutout=True, mask=None, dx=0.0, green_ink="ink_green"):
    """An engraved prop: printed on the sheet (cutout False: ink only), or a paper cutout floating over it (its
    silhouette from scripts/props.py, or `mask`: 'full' for a whole sheet of paper); a second plate prints in green."""
    ob = plane(name, box, lift, None, dx)
    ink = PROPS / f"{prop}.png"
    mk = (PROPS / ("full_mask.png" if mask == "full" else (mask or f"{prop}_mask.png"))) if cutout else ink
    green = PROPS / f"{prop}_green.png"
    ob.data.materials.append(P.layer_material(name, ink, mk, tuple(S.image(ink, True).size), cutout,
                                              green if cutout and green.exists() else None, green_ink))
    return ob


def emboss_card(name, box, height, mask, lift):
    """A blind emboss: paper raised in relief from a height map, no ink (the seal's impression)."""
    ob = plane(name, box, lift, None)
    m = bpy.data.materials.new(name)
    m.surface_render_method = "DITHERED"
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    b.inputs["Base Color"].default_value = S.srgb(S.LOOK["palette"]["paper"])
    b.inputs["Roughness"].default_value = 0.82
    hx = n.new("ShaderNodeTexImage")
    hx.image = S.image(PROPS / f"{height}.png", True)
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.9
    bump.inputs["Distance"].default_value = 0.0004
    l.new(hx.outputs["Color"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], b.inputs["Normal"])
    mx = n.new("ShaderNodeTexImage")
    mx.image = S.image(PROPS / f"{mask}.png", True)
    l.new(mx.outputs["Color"], b.inputs["Alpha"])
    ob.data.materials.append(m)
    return ob


def parent_keep(child, parent):
    bpy.context.view_layer.update()
    mw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = mw


def piece_to_sheet(fig_box, piece_size, px, py, mirror=False):
    x0, y0, x1, y1 = fig_box
    s = (x1 - x0) / piece_size[0]
    if mirror:
        px = piece_size[0] - px
    return x0 + px * s, y0 + py * s


scene = S.setup(args.size[0], args.size[1], args.samples, 1)
scene.render.image_settings.file_format = "PNG"
materials()
SHEET = S.sheet(cert)


def gold_reink(sheet_ob):
    """S36: the green plate re-inks in gold, creeping in from the sheet's edges (a noisy front from the border inward);
    the gold ink catches a little light. Returns the reveal's value node (0: all green, 1: all gold)."""
    m = sheet_ob.data.materials[0]
    n, l = m.node_tree.nodes, m.node_tree.links
    bsdf = n["Principled BSDF"]
    base = bsdf.inputs["Base Color"].links[0].from_socket
    green = next(x for x in n if x.type == "TEX_IMAGE" and x.image and "plate_green" in x.image.name)
    uv = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(uv.outputs["UV"], sep.inputs["Vector"])
    # distance to the nearest edge, 0 at the edge .. 0.5 at the centre, roughened with noise
    edge = None
    for comp in ("X", "Y"):
        for flip in (False, True):
            d = n.new("ShaderNodeMath")
            if flip:
                d.operation = "SUBTRACT"
                d.inputs[0].default_value = 1.0
                l.new(sep.outputs[comp], d.inputs[1])
            else:
                d.operation = "ADD"
                d.inputs[1].default_value = 0.0
                l.new(sep.outputs[comp], d.inputs[0])
            if edge is None:
                edge = d
            else:
                mn = n.new("ShaderNodeMath")
                mn.operation = "MINIMUM"
                l.new(edge.outputs[0], mn.inputs[0])
                l.new(d.outputs[0], mn.inputs[1])
                edge = mn
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 7.0
    noise.inputs["Detail"].default_value = 6.0
    l.new(uv.outputs["UV"], noise.inputs["Vector"])
    nz = n.new("ShaderNodeMath")
    nz.operation = "MULTIPLY_ADD"  # field = edge + 0.22 * (noise - 0.5) ... (noise * 0.22 + (edge - 0.11))
    nz.inputs[1].default_value = 0.22
    l.new(noise.outputs["Fac"], nz.inputs[0])
    off = n.new("ShaderNodeMath")
    off.operation = "SUBTRACT"
    off.inputs[1].default_value = 0.11
    l.new(edge.outputs[0], off.inputs[0])
    l.new(off.outputs[0], nz.inputs[2])
    reveal = n.new("ShaderNodeValue")
    reveal.name = "gold_reveal"
    front = n.new("ShaderNodeMath")  # (reveal * 0.75 - field) * 14, clamped: a soft creeping front
    front.operation = "MULTIPLY"
    front.inputs[1].default_value = 0.75
    l.new(reveal.outputs[0], front.inputs[0])
    dif = n.new("ShaderNodeMath")
    dif.operation = "SUBTRACT"
    l.new(front.outputs[0], dif.inputs[0])
    l.new(nz.outputs[0], dif.inputs[1])
    sharp = n.new("ShaderNodeMath")
    sharp.operation = "MULTIPLY"
    sharp.use_clamp = True
    sharp.inputs[1].default_value = 14.0
    l.new(dif.outputs[0], sharp.inputs[0])
    fac = n.new("ShaderNodeMath")  # gold only where the green plate printed
    fac.operation = "MULTIPLY"
    l.new(sharp.outputs[0], fac.inputs[0])
    l.new(green.outputs["Color"], fac.inputs[1])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = [p * g for p, g in zip(S.srgb(S.LOOK["palette"]["paper"]),
                                                          S.srgb(S.LOOK["palette"]["ink_gold"]))][:3] + [1.0]
    l.new(fac.outputs[0], mix.inputs["Factor"])
    l.new(base, mix.inputs["A"])
    l.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    met = n.new("ShaderNodeMath")
    met.operation = "MULTIPLY"
    met.inputs[1].default_value = 0.55
    l.new(fac.outputs[0], met.inputs[0])
    l.new(met.outputs[0], bsdf.inputs["Metallic"])
    rough = n.new("ShaderNodeMath")  # 0.82 on paper, 0.45 on the gold
    rough.operation = "MULTIPLY_ADD"
    rough.inputs[1].default_value = -0.37
    rough.inputs[2].default_value = 0.82
    l.new(fac.outputs[0], rough.inputs[0])
    l.new(rough.outputs[0], bsdf.inputs["Roughness"])
    return reveal


GOLD = gold_reink(SHEET)
GREEN_BSDF = M["green"].node_tree.nodes["Principled BSDF"]
GREEN_RGB = list(GREEN_BSDF.inputs["Base Color"].default_value)
GOLD_RGB = [p * g for p, g in zip(S.srgb(S.LOOK["palette"]["paper"]), S.srgb(S.LOOK["palette"]["ink_gold"]))][:3] + [1.0]
GOLD_SPAN = (None, 2.2)  # the creep's length (s) from the key change (S36): 2.6 until 2026-10-27, now done 0.4 s before S18
DESK = S.desk()
KEY, FILL = S.lights()
KEY_E, KEY_C = KEY.data.energy, tuple(KEY.data.color)
P.print_piece("laborer", LAYOUT["laborer"], src=S.LOOK["laborer_ink"])
PUP = {n: P.build(n, LAYOUT[n]) for n in ("progress", "prudence", "mercury", "cherubs")}
PUP["cherubs_mirror"] = P.build("cherubs", LAYOUT["cherubs_mirror"], mirror=True)
SIZE = {n: json.loads((ROOT / "assets/puppets" / n / "puppet.json").read_text())["size"]
        for n in ("progress", "prudence", "mercury", "cherubs")}
BASE = {}
for obs in PUP.values():
    for ob in obs.values():
        BASE[ob.name] = (ob.location.copy(), ob.rotation_euler.copy(), ob.scale.copy())

VIS = []    # (object, t0, t1): rendered only inside [t0, t1)
MOVES = []  # fn(t) per frame, for props


def show(ob, a, b):
    VIS.append((ob, a, b))
    return ob


def attach(ob, fig, layer, piece_xy):
    """Put a prop on a puppet layer (it then moves with the hinge), at a point given in piece pixels."""
    host = PUP[fig][layer]
    sx, sy = piece_to_sheet(LAYOUT[fig], SIZE[fig.split("_")[0]], *piece_xy, mirror=fig.endswith("mirror"))
    lift = ob.location.z if ob.modifiers else ob.location.z - S.curl(ob.location.x, ob.location.y)
    ob.location = (pxyz if ob.modifiers else sheet_xyz)(sx, sy, lift)
    parent_keep(ob, host)
    return ob


def card_at(name, cx, cy, w, h, label, lift=0.0016):
    return grey_card(name, [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], label, lift)


# ---- props, by shot ------------------------------------------------------------------------------------------------

end = TM["duration_s"]
sheet_img = cert / "sheet.png"

# S05: a "%" glyph engraves itself into the torch flame (the spear tip, piece px 1093,55, rides on the forearm)
pct = text("S05.pct", "%", "display", 70, (0, 0), 0.0018, M["sepia"])
attach(pct, "progress", "arm", (1093, 40))
MOVES.append(lambda t: setattr(pct, "scale", [max(1e-4, ramp(t, T["S05"] + 0.4, T["S05"] + 1.6))] * 3))
show(pct, T["S05"], T["S10"])

# S06-S09: the vignette behind Progress becomes an engraved recording studio, a microphone either side of her (one
# print: overlapping prints would hide each other); right of it, the studio door, its WHOLLY OWNED plaque centred in
# S08's PLAQUE framing
show(prop_card("S06.studio", prop_box("studio_print", 2475, 700, w=1020), "studio_print", 0.00026, cutout=False),
     T["S06"], T["S10"])
show(prop_card("S08.door", [2990, 571, 3190, 971], "door_print", 0.00026, cutout=False), T["S06"], T["S10"])
# S09: a tiny certificate drawn inside the first, and a tinier one inside that (the same print, smaller)
tx0, ty0, tx1, ty1 = BOXES["TINY"]
show(tex_card("S09.tiny", BOXES["TINY"], sheet_img, lift=0.00028), T["S09"], T["S10"])  # from its own shot: before it, it would hide the left microphone
fx0, fy0 = tx0 + (tx1 - tx0) * tx0 / S.PW, ty0 + (ty1 - ty0) * ty0 / S.PH
fw = (tx1 - tx0) * (tx1 - tx0) / S.PW
show(tex_card("S09.tinier", [fx0, fy0, fx0 + fw, fy0 + fw * S.PH / S.PW], sheet_img, lift=0.00031), T["S09"], T["S10"])

# S10: the fine print scrolls under Mercury's feet like a ticker
tick = text("S10.ticker", "FINE PRINT · SUBJECT TO CHANGE · NOT A CHARITY, PER SE · TERMS APPLY · FINE PRINT · " * 2,
            "small_caps", 34, (900, 1830), 0.0009, M["sepia"], align="LEFT")
tick_x = tick.location.x
MOVES.append(lambda t: setattr(tick.location, "x", tick_x - 0.02 * max(0.0, t - T["S10"])))
show(tick, T["S10"], T["S11"])
# S39: the line of fine print he pops up out of
show(text("S39.fineprint", "BASELINE TO BE ANNOUNCED · SUBJECT TO THE BOARD'S DISCRETION · TERMS APPLY", "small_caps", 30,
          (1140, 1820), 0.0009, M["sepia"]), T["S39"], SPAN["S39"][1])

# S11: the guilloche, looked at closely, is the letters LLC repeated
llc = text("S11.llc", "LLC LLC LLC LLC LLC", "small_caps", 22, (1240, 1358), 0.0006, M["green"])
MOVES.append(lambda t: setattr(llc, "scale", [max(1e-4, ramp(t, T["S11"] + 1.0, T["S11"] + 3.0))] * 3))
show(llc, T["S11"], T["S12"])

# S12: an engraved calendar in the margin flips pages and never lands
cal = prop_card("S12.calendar", prop_box("calendar", 3980, 1270, w=300), "calendar", 0.0004, cutout=False)
show(cal, T["S12"], T["S13"])
MONTHS = ["NOV", "DEC", "JAN", "Q1", "Q2", "SOON", "H2", "TBD", "NEXT", "SOON"]  # the pages (scripts/props.py)
PAGE_W, PAGE_H, PAGE_AT = 110, 136, (3925, 1262)
for i, mname in enumerate(MONTHS):
    a = T["S12"] + i * (SPAN["S12"][1] - T["S12"]) / len(MONTHS)
    b = a + (SPAN["S12"][1] - T["S12"]) / len(MONTHS)
    pg = prop_card(f"S12.page{i}", [PAGE_AT[0] - PAGE_W / 2, PAGE_AT[1] - PAGE_H / 2, PAGE_AT[0] + PAGE_W / 2,
                                    PAGE_AT[1] + PAGE_H / 2], f"calendar_page_{i}", 0.0013 - 0.00002 * i)
    home = pg.location.copy()

    def flip(t, pg=pg, home=home, a=a, b=b):
        u = ramp(t, b - 0.18, b)  # the page flips up over its binding, and the next lands under it
        pg.scale.y = max(1e-4, 1 - u)
        pg.location = home + Vector((0, px_len(PAGE_H) * u / 2, 0.002 * math.sin(math.pi * u)))
    MOVES.append(flip)
    show(pg, a, b)

# S14: the corner denominations flip from 5 to 5% (and stay)
for i in range(4):
    x0, y0, x1, y1 = LAYOUT[f"counter_{i}"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # a round green face over the counter's centre and inner rosette (r 180 px of its 210), the 5 as large as the printed
    # one and the % beside it, smaller, so "5%" reads in the wide shots (human, C4: "the 5% in the corners is hard to read")
    bpy.ops.mesh.primitive_cylinder_add(radius=px_len(180), depth=0.0002, vertices=96, location=sheet_xyz(cx, cy, 0.0008))
    disc = bpy.context.object
    disc.name = f"S14.disc{i}"
    disc.data.materials.append(M["green"])
    five = text(f"S14.five{i}", "5", "display", 205, (cx - 40, cy + 12), 0.0013, M["paper"])
    pc = text(f"S14.pct{i}", "%", "display", 118, (cx + 68, cy - 22), 0.0013, M["paper"])
    for o in (five, pc):
        parent_keep(o, disc)
    a = T["S14"] + 0.25 + 0.18 * i
    MOVES.append(lambda t, d=disc, a=a: setattr(d, "scale", (max(1e-4, ramp(t, a, a + 0.2)), 1, 1)))  # the flip
    show(disc, a, end)

# S15: a "+2%" stamp hovers over the page and is pulled back unstamped
stamp = prop_card("S15.stamp", prop_box("stamp", 3300, 1850, h=224), "stamp", 0.03)
s15a, s15b = SPAN["S15"]
st_loc = stamp.location.copy()
MOVES.append(lambda t: setattr(stamp, "location", st_loc + Vector((0.03 * ramp(t, s15b - 1.0, s15b), 0,
                                                                   -0.022 * ramp(t, s15a, s15a + 1.2) * (1 - ramp(t, s15b - 1.2, s15b - 0.6))))))
show(stamp, s15a, s15b)

# S16: the Number of Shares box fills with figures that keep changing (to the end of the chorus)
FIGS = ["5,000,000", "5,000,250", "4,999,875", "5,001,000", "5,000,005", "4,998,500", "5,000,500", "5,000,000?"]
bx0, by0, bx1, by1 = LAYOUT["shares_box"]
FIG_WINDOWS = [(T["S16"], SPAN["S17b"][1]), SPAN["S25c"]]  # through chorus 1 (S16-S17b), and again in S25c
for i, s in enumerate(FIGS):
    o = text(f"S16.fig{i}", s, "display", 52, ((bx0 + bx1) / 2, (by0 + by1) / 2), 0.0004, M["sepia"])
    VIS.append((o, None, i))  # resolved per frame: one figure per beat


def shares_fig(t):
    return int(beat_pos(t)) % len(FIGS) if any(a <= t < b for a, b in FIG_WINDOWS) else -1


# S18-S19: Prudence weighs coins on her scales, which never settle (the coins ride on her hand)
coins = prop_card("S18.coins", prop_box("coins", 60, 48, w=120), "coins", 0.0016)
attach(coins, "prudence", "scales_arm", (905, 1160))
show(coins, T["S18"], T["S20"])

# S19: a quill hovers over the blank Recipient line
q = prop_card("S19.quill", prop_box("quill", 3360, 2285, h=210), "quill", 0.012)
q_loc = q.location.copy()
MOVES.append(lambda t: setattr(q, "location", q_loc + Vector((0.002 * math.sin(2.1 * t), 0, 0.002 * math.sin(3.3 * t)))))
show(q, T["S19"], T["S20"])

# S20-S22: she rules a baseline across the page, studies it, erases it, draws it again as a faint dotted line
LINE_Y, LINE_X0, LINE_X1 = 2255, 1150, 3560
line = plane("S20.baseline", [LINE_X0, LINE_Y - 5, LINE_X1, LINE_Y + 5], 0.0005, M["sepia"])
line_full = line.matrix_world.copy()
pen = prop_card("S20.pen", prop_box("quill", 0, 0, h=260), "quill", 0.006)  # the quill rules it
PEN_W = prop_box("quill", 0, 0, h=260)[2] * 2
eraser = prop_card("S21.eraser", prop_box("eraser", 0, 0, w=180), "eraser", 0.004)
s20a, s20b = SPAN["S20"]
s21a, s21b = SPAN["S21"]
s22a, s22b = SPAN["S22"]
erase_a = s21a + 3.0


def line_u(t):
    """How much of the line is drawn (right to left) and how much erased (left to right)."""
    drawn = ramp(t, s20a + 0.2, s20b - 0.2)
    erased = ramp(t, erase_a, s21b - 0.6)
    return drawn, erased


def move_line(t):
    drawn, erased = line_u(t)
    xa = LINE_X1 - drawn * (LINE_X1 - LINE_X0)  # the pen's end
    xb = LINE_X0 + erased * (LINE_X1 - LINE_X0) if erased > 0 else LINE_X0
    lo, hi = max(xa, xb), LINE_X1
    w = max(1.0, hi - lo) / (LINE_X1 - LINE_X0)
    line.scale.x = w if drawn > 0 and hi - lo > 1 else 1e-4
    line.location = pxyz((lo + hi) / 2, LINE_Y, 0.0005)
    pen.location = pxyz(xa - (0.92 - 0.5) * PEN_W, LINE_Y - (0.97 - 0.5) * 260, 0.006)  # its nib (at 0.92, 0.97) on the line
    eraser.location = pxyz(xb, LINE_Y, 0.004)


line.scale.x = 1e-4
MOVES.append(move_line)
show(line, s20a, s22a)
show(pen, s20a, s21a)
show(eraser, erase_a, s21b)
for i in range(10):
    crumb = plane(f"S21.crumb{i}", [0, 0, 14, 14], 0.002, M["grey"])
    r = random.Random(i)
    cx0, dly = LINE_X0 + r.random() * (LINE_X1 - LINE_X0), r.random() * 2.5
    MOVES.append(lambda t, c=crumb, cx0=cx0, dly=dly: setattr(c, "location", pxyz(
        cx0 + 30 * math.sin(3 * t + cx0), LINE_Y + 20 + 260 * max(0.0, t - erase_a - dly), 0.002)))
    show(crumb, erase_a + dly, s21b + 1.0)
for i in range(24):
    x = LINE_X1 - (i + 0.5) * (LINE_X1 - LINE_X0) / 24
    d = plane(f"S22.dash{i}", [x - 22, LINE_Y - 3, x + 22, LINE_Y + 3], 0.0005, M["sepia"])
    show(d, s22a + 0.2 + 1.6 * i / 24, s22b)

# S23: Mercury reads from an unrolled scroll (it rides on his arm)
scroll = prop_card("S23.scroll", prop_box("scroll", 65, 94, w=130), "scroll", 0.0018)
attach(scroll, "mercury", "arm", (1120, 560))
show(scroll, T["S23"], T["S24"])

# S24: the certificate flips to its back: the transfer form, and a second document face down underneath
back = prop_card("S24.back", [0, 0, S.PW, S.PH], "transfer_form", 0.0006, mask="full", dx=BACK_DX,
                 green_ink="ink_gold")  # the same sheet: after S36 its lathe work is gold on both sides
under = prop_card("S24.under", [260, 180, S.PW + 260, S.PH + 180], "face_down", 0.0002, mask="full", dx=BACK_DX)
for o in (back, under):
    show(o, T["S24"], T["S25"])

# S32-S33: the stub becomes a thermometer, its perforations marked in +50% steps; the bulb reads BASELINE: TBA
TH_BOX = [0, 280, 560, 2680]  # the stub's thermometer (scripts/props.py): 560 x 2400 px, drawn at 1 px per sheet px
TH = json.loads((PROPS / "thermometer_geom.json").read_text())
TH_X, TH_Y0, TH_Y1 = TH["cx"], TH_BOX[1] + TH["foot"], TH_BOX[1] + TH["top"] + 40
merc = plane("S32.mercury", [TH_X - TH["col_w"] / 2, TH_Y1, TH_X + TH["col_w"] / 2, TH_Y0], 0.0005, M["sepia"])
glass = prop_card("S32.glass", TH_BOX, "thermometer_glass", 0.00045, mask="full")  # a paper card over the stub's fields
s32a, s33b = T["S32"], SPAN["S33"][1]


def move_merc(t):
    u = ramp(t, s32a + 0.3, s33b - 1.5)
    top = TH_Y0 - u * (TH_Y0 - TH_Y1)
    merc.scale.y = max(1e-4, (TH_Y0 - top) / (TH_Y0 - TH_Y1))
    merc.location = pxyz(TH_X, (TH_Y0 + top) / 2, 0.0005)


MOVES.append(move_merc)
show(merc, s32a, end)
show(glass, s32a, end)
show(prop_card("S33.ribbon", TH_BOX, "thermometer_ribbon", 0.0006, mask="thermometer_ribbon_mask.png"), T["S33"] + 1.0, end)

# S34: the corporate seal stamps down and embosses the page (and stays)
bpy.ops.mesh.primitive_cylinder_add(radius=px_len(170), depth=0.003, vertices=64)
seal = bpy.context.object
seal.name = "S34.seal"
seal.data.materials.append(M["seal"])
seal_down = sheet_xyz(1650, 2100, 0.0016)
seal.location = seal_down
seal_face = prop_card("S34.seal_face", [1480, 1930, 1820, 2270], "seal", 0.0016 + 0.0015 + 0.0004, dx=FLAT)  # clear of the die's top
parent_keep(seal_face, seal)
SEAL_HIT = beat_t(T["S34"] + 0.2, 0)
SEAL_UP = (SEAL_HIT + 0.8, SEAL_HIT + 1.6)  # it lifts away, leaving the impression


def move_seal(t):
    z = 0.06 * (1 - ramp(t, SEAL_HIT - 0.35, SEAL_HIT)) + 0.08 * ramp(t, *SEAL_UP)
    seal.location = seal_down + Vector((0, 0, z))


MOVES.append(move_seal)
show(seal, T["S34"], SEAL_UP[1])
show(seal_face, T["S34"], SEAL_UP[1])
show(emboss_card("S34.emboss", [1480, 1930, 1820, 2270], "seal_emboss", "seal_mask", 0.00012), SEAL_HIT, end)

# S37: Prudence clips the coupons one by one; each flutters into her ledger (on the desk, right of the sheet)
ledger = prop_card("S37.ledger", prop_box("ledger", 4730, 2700, w=500), "ledger", 0.004)
show(ledger, T["S37"], SPAN["S38"][1])
scis = prop_card("S37.scissors", prop_box("scissors", 0, 0, h=228), "scissors", 0.008)
CLIP = [beat_t(T["S37"] + 0.4, 2 * i) for i in range(7)]
coupons = []
for i in range(7):
    x0, y0, x1, y1 = LAYOUT[f"coupon_{i + 1}"]
    uv = (x0 / S.PW, 1 - y1 / S.PH, x1 / S.PW, 1 - y0 / S.PH)
    c = tex_card(f"S37.coupon{i}", [x0, y0, x1, y1], cert / "sheet_gold.png", uv, lift=0.0007)  # after S36's re-ink
    hole = plane(f"S37.hole{i}", [x0 + 4, y0 + 4, x1 - 4, y1 - 4], 0.00066, M["desk_hole"])
    show(hole, CLIP[i] + 0.15, end)
    show(c, T["S37"], CLIP[i] + 0.95)
    coupons.append((c, c.location.copy(), (x0 + x1) / 2, (y0 + y1) / 2))
L_AT = pxyz(4730, 2700, 0.005)


def move_coupons(t):
    for i, (c, home, cx, cy) in enumerate(coupons):
        u = ramp(t, CLIP[i] + 0.15, CLIP[i] + 0.9)
        p = home.lerp(L_AT, u)
        p.z += 0.02 * math.sin(math.pi * u)
        c.location = p
        c.rotation_euler.z = 0.6 * math.sin(9 * u) * (1 - u)
        c.scale = [1 - 0.55 * u] * 3
    k = max([i for i in range(7) if CLIP[i] - 0.5 <= t] or [0])
    _, _, cx, cy = coupons[k]
    scis.location = pxyz(cx + 200, cy - 300 + 60 * math.sin(14 * t) * (abs(t - CLIP[k]) < 0.3), 0.008)


MOVES.append(move_coupons)
show(scis, T["S37"], T["S38"])
# S38: close on Prudence, scissors raised (in her sword hand)
scis2 = prop_card("S38.scissors", prop_box("scissors", 21, 60, h=120), "scissors", 0.0018)
attach(scis2, "prudence", "sword_arm", (300, 540))
show(scis2, T["S38"], SPAN["S38"][1])

# S43: "fully paid and non-assessable" glows as the choir fades
for nm, bx in (("body", [1700, 1995, 3260, 2048]), ("foot", [1880, 2532, 3070, 2568])):
    g = plane(f"S43.glow_{nm}", bx, 0.0005, M["glow"])
    show(g, T["S43"], end)
glow_b = M["glow"].node_tree.nodes["Principled BSDF"]
MOVES.append(lambda t: (glow_b.inputs["Alpha"].__setattr__("default_value", 0.55 * ramp(t, T["S43"] + 1, T["S43"] + 8)),
                        glow_b.inputs["Emission Strength"].__setattr__("default_value", 2.5 * ramp(t, T["S43"] + 1, T["S43"] + 8))))

# S44: Progress leans out of a filing-cabinet drawer labeled WHOLLY OWNED, and the drawer slides shut
DR = 0.06  # drawer wall height (m)
walls = []
for nm, (cx, cy, sx, sy) in {"n": (0, S.SH / 2 + 0.01, S.SW + 0.04, 0.02), "s": (0, -S.SH / 2 - 0.01, S.SW + 0.04, 0.02),
                             "w": (-S.SW / 2 - 0.01, 0, 0.02, S.SH + 0.04), "e": (S.SW / 2 + 0.01, 0, 0.02, S.SH + 0.04)}.items():
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, DR / 2))
    w = bpy.context.object
    w.name = f"S44.wall_{nm}"
    w.scale = (sx, sy, DR)
    w.data.materials.append(M["wood"])
    walls.append(show(w, T["S44"], end))
bpy.ops.mesh.primitive_cube_add(size=1.0)
lid = bpy.context.object
lid.name = "S44.lid"
lid.scale = (S.SW + 0.06, S.SH + 0.06, 0.008)
lid.data.materials.append(M["wood"])
lid_lab = prop_card("S44.drawer_front", [0, 0, S.PW, S.PH], "drawer_front", 0.0, cutout=False, dx=FLAT)
show(lid, T["S44"], end)
show(lid_lab, T["S44"], end)
# the drawer shuts once Progress has said the whole line (the human, C5: so "Phone lines open at the IPO." is seen
# with the mouth moving), over 2 s
SHUT = (TM["sections"][-1]["end"] + 0.25, TM["sections"][-1]["end"] + 2.25)


def move_lid(t):
    y = -(S.SH + 0.08) * (1 - ramp(t, *SHUT))
    lid.location = (0, y, DR + 0.004)
    lid_lab.location = (0, y, DR + 0.0085)


MOVES.append(move_lid)

# ---- the puppets' performance ---------------------------------------------------------------------------------


def progress_pose(t):
    out = {}
    stepped = ramp(t, T["S03"], T["S03"] + 1.0) * (1 - ramp(t, T["S10"] - 0.01, T["S10"]))
    lean = ramp(t, T["S44"], T["S44"] + 1.2)
    torch = 22 * ramp(t, T["S03"] + 0.3, T["S03"] + 0.9)
    if within(t, T["S05"], T["S06"]):
        torch += -18 * math.sin(math.pi * ramp(t, T["S05"] + 0.1, T["S05"] + 1.4))  # the gesture
    if t >= T["S06"]:
        torch = 10 if t < T["S44"] else 14
    out["arm"] = torch
    out["jaw"] = -14 * mouth("progress", t)
    out["head"] = 4 * math.sin(0.7 * t)
    out["body"] = -6 * lean
    out["_lift"] = 0.003 * max(stepped, lean)
    out["_scale"] = 1 + 0.10 * max(stepped, 1.2 * lean)
    return out


def prudence_pose(t):
    out = {"jaw": -8 * mouth("prudence", t)}
    sa = 0.0
    if within(t, T["S18"], T["S20"]):
        sa = 6 * math.sin(2 * math.pi * 0.9 * t) + 2 * math.sin(2 * math.pi * 2.3 * t)  # never settle
    out["scales_arm"] = sa
    sw = 0.0
    if within(t, T["S15"], SPAN["S15"][1]):
        sw = -10 * ramp(t, T["S15"], T["S15"] + 0.4)  # the raised finger
    if within(t, T["S20"], SPAN["S22"][1]):
        sw = -8
    if within(t, T["S38"], SPAN["S38"][1]):
        sw = -18 * ramp(t, T["S38"], T["S38"] + 0.5)
    out["sword_arm"] = sw
    hd = 0.0
    if within(t, T["S21"], erase_a):
        hd = -8 * ramp(t, T["S21"], T["S21"] + 0.6)  # studies it
    if within(t, T["S22"], SPAN["S22"][1]):
        hd = 4 * ramp(t, T["S22"], T["S22"] + 0.5)  # and smiles
        out["jaw"] = -4
    out["head"] = hd
    return out


def mercury_pose(t):
    out = {"wing": 4 * math.sin(2 * math.pi * 0.5 * t), "head": 5 * mouth("mercury", t)}
    if within(t, T["S10"], T["S11"]):
        ph = 2 * math.pi * 2 * beat_pos(t) + math.pi / 2  # two strides a beat, a foot at full reach on each
        out.update({"leg_back": 28 * math.sin(ph), "leg_front": -28 * math.sin(ph), "leg_bent": 20 * math.sin(ph),
                    "wing": 15 * math.sin(2 * ph), "arm": 6 * math.sin(ph)})
    if within(t, T["S23"], T["S24"]):
        out["head"] = -8 + 3 * mouth("mercury", t)
        out["arm"] = -10
    if within(t, T["S39"], SPAN["S39"][1]):
        # S39: he pops up out of the fine print: from below the text line, with an overshoot, then a wave of the caduceus
        u = (t - T["S39"]) / 0.45
        rise = 1.0 if u >= 1 else (0.0 if u <= 0.15 else 1.15 * math.sin(math.pi / 2 * (u - 0.15) / 0.85))
        if u > 1:
            rise = 1.0 + 0.15 * math.exp(-4 * (u - 1)) * math.cos(6 * (u - 1))
        out["_offset"] = (0.0, -px_len(90) * (1 - min(rise, 1.0)), 0.0)  # up out of the fine-print line at his feet
        out["_scale"] = max(0.02, rise)
        out["arm"] = 18 * ramp(t, T["S39"] + 0.6, T["S39"] + 1.0) * (1 + 0.3 * math.sin(9 * t))
    return out


def cherub_pose(t, mirror):
    out = {}
    s = section_of(t)
    sway = 6.0 if chorus(t) else 0.0
    if s and s["name"] == "Outro":
        sway *= 1 - ramp(t, s["start"], s["end"])
    if within(t, T["S35"], SPAN["S35"][1]):
        sway = 12.0
    b = beat_pos(t)
    sw = sway * math.cos(math.pi * b)  # at the extreme on each beat, one side then the other
    out.update({"body_top": sw * 0.6, "body_left": -sw, "body_center": sw})
    nod = 4 * mouth("cherubs", t)
    look = 0.0
    if within(t, T["S04"], T["S06"]):
        look = 16 * ramp(t, T["S04"], T["S04"] + 0.35)  # turn to camera, in unison
    for h in ("head_top", "head_left", "head_center"):
        out[h] = look + nod
    if within(t, T["S12"], T["S13"]):  # they shout
        for h in ("head_top", "head_left", "head_center"):
            out[h] = 10 + 4 * math.sin(40 * t)
    if within(t, T["S35"], SPAN["S35"][1]):  # the crescendo
        r = random.Random(int(t * FPS))
        for h in ("head_top", "head_left", "head_center"):
            out[h] = r.uniform(-10, 10)
    point = 0.0
    for sid in ("S17", "S27", "S42"):
        a = T[sid]
        point = max(point, ramp(t, a, a + 0.3) * (1 - ramp(t, a + 3.8, a + 4.3)))
    out["arm_left"] = -40 * point
    out["arm_top"] = 30 * point     # C5: the other two point too (brief: "every cherub points")
    out["arm_center"] = 55 * point
    return out


def apply_pose(t):
    tt = math.floor(t * FPS / TWOS) * TWOS / FPS  # on twos
    poses = {"progress": progress_pose(tt), "prudence": prudence_pose(tt), "mercury": mercury_pose(tt),
             "cherubs": cherub_pose(tt, False), "cherubs_mirror": cherub_pose(tt, True)}
    for fig, pose in poses.items():
        obs = PUP[fig]
        sign = -1.0 if fig.endswith("mirror") else 1.0
        for ln, ob in obs.items():
            loc, rot, sc = BASE[ob.name]
            ob.rotation_euler.z = rot.z + sign * math.radians(pose.get(ln, 0.0))
            ob.location = loc
            ob.scale = sc
        if "_lift" in pose or "_offset" in pose:
            body = obs["body"]
            loc, _, sc = BASE[body.name]
            body.location = loc + Vector((0, 0, pose.get("_lift", 0.0))) + Vector(pose.get("_offset", (0, 0, 0)))
            body.scale = sc * pose.get("_scale", 1.0)


# ---- the camera -------------------------------------------------------------------------------------------------

CAM = S.camera((0, 0, 1), (0, 0, 0), 50)
FOV = 2 * math.atan(18 / 50)
ASPECT = args.size[0] / args.size[1]
if args.flat:
    CAM.data.type = "ORTHO"
    CAM.data.ortho_scale = max(S.SW, S.SH * ASPECT)  # the frame's wider side
    CAM.location, CAM.rotation_euler = (0, 0, 1), (0, 0, 0)  # straight down, north up
    DESK.hide_render = True
    scene.render.film_transparent = True
    if args.figures_only:
        SHEET.hide_render = True


def frame_box(b, back=False):
    """Centre (on the page) and height for a document camera framing sheet-pixel box b."""
    if isinstance(b, str):
        b = BOXES[b]
    x0, y0, x1, y1 = b
    c = sheet_xyz((x0 + x1) / 2, (y0 + y1) / 2, 0.0, BACK_DX if back else 0.0)
    span = max(px_len(x1 - x0), px_len(y1 - y0) * ASPECT)  # the page's pixels are square
    return c, span / 2 / math.tan(FOV / 2)


def camera_at(t):
    sid = shot_at(t)
    plan = PLAN["shots"].get(sid)
    if plan is None:
        return None
    a, b = SPAN[sid]
    u = ramp(t, a, b) if plan.get("ease", "smooth") == "smooth" else min(1.0, max(0.0, (t - a) / (b - a)))
    back = plan.get("back", False)
    (c0, d0), (c1, d1) = frame_box(plan["cam"][0], back), frame_box(plan["cam"][1], back)
    if plan.get("ease") == "exp":
        d = d0 * (d1 / d0) ** u  # a push at a constant rate of magnification
        w = (d0 - d) / (d0 - d1) if d0 != d1 else u
    else:
        d, w = d0 + (d1 - d0) * u, u
    c = c0.lerp(c1, w)
    lean = plan.get("lean", 0.15)
    loc = c + Vector((0, -lean * d, d))
    target = c.copy()
    if plan.get("turn_away"):
        k = ramp(t, a + 0.35 * (b - a), b)
        target += Vector((0.35 * d * k, 0.2 * d * k, 0))
    if plan.get("shake"):
        r = random.Random(int(t * FPS / TWOS))
        j = px_len(plan["shake"])
        loc += Vector((r.uniform(-j, j), r.uniform(-j, j), 0))
        target += Vector((r.uniform(-j, j) * 0.5, r.uniform(-j, j) * 0.5, 0))
    if within(t, SEAL_HIT, SEAL_HIT + 0.12):
        loc.z -= 0.04 * d  # the stamp's thump
    return loc, target, d


def look_at(loc, target):
    """A camera rotation looking from loc at target with the page's north (+Y) up on screen. (to_track_quat's up axis
    is world +Z, which is almost the view direction for a camera looking down, so it rolls the frame.)"""
    from mathutils import Matrix
    z = (loc - target).normalized()  # the camera looks down its -Z
    y = (Vector((0, 1, 0)) - z * z.y).normalized()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed().to_euler()


def apply(t):
    for ob, a, b in VIS:
        if a is None:
            vis = shares_fig(t) == b
        else:
            vis = a <= t < b
        for o in [ob] + list(ob.children_recursive):
            o.hide_render = not vis
    for fn in MOVES:
        fn(t)
    apply_pose(t)
    # S36: at the key change the certificate re-inks brighter: the green plate turns gold, creeping in from the edges
    # (and stays), the corner discs follow, and the light lifts a little
    g = ramp(t, T["S36"], T["S36"] + GOLD_SPAN[1])
    GOLD.outputs[0].default_value = g
    GREEN_BSDF.inputs["Base Color"].default_value = [a * (1 - g) + b_ * g for a, b_ in zip(GREEN_RGB, GOLD_RGB)]
    k = ramp(t, T["S36"], T["S36"] + 1.0)
    KEY.data.energy = KEY_E * (1 + 0.10 * k)
    KEY.data.color = tuple(c0 * (1 - k) + c1 * k for c0, c1 in zip(KEY_C, (1.0, 0.95, 0.86)))
    if args.flat:
        return True
    pose = camera_at(t)
    if pose:
        loc, target, d = pose
        CAM.location = loc
        CAM.rotation_euler = look_at(loc, target)
        CAM.data.clip_start = max(0.0004, min(0.01, 0.25 * d))
    return pose is not None


def render(t, path):
    f = int(round(t * FPS))
    scene.frame_set(max(f, 1))
    if not apply(t):
        return False
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return True


out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
t_start = time.time()
n = 0
if args.anchors:
    for sid in PLAN["shots"]:
        a, b = SPAN[sid]
        n += render(a + min(0.6 * (b - a), 1.2 if sid == "S44" else 3.0), out / f"anchor_{sid}.png")
elif args.debug_cam is not None:
    from bpy_extras.object_utils import world_to_camera_view
    apply(args.debug_cam)
    bpy.context.view_layer.update()
    print("CAM", tuple(CAM.location), tuple(CAM.rotation_euler), CAM.data.lens, CAM.data.sensor_width, CAM.data.sensor_fit)
    for px, py in ((0, 0), (S.PW, 0), (0, S.PH), (S.PW, S.PH), (S.PW / 2, S.PH / 2)):
        print("PROJ", px, py, tuple(round(v, 3) for v in world_to_camera_view(scene, CAM, sheet_xyz(px, py, 0))))
elif args.times:
    for t in args.times:
        n += render(t, out / f"t_{t:07.2f}.png")
else:
    t1 = args.t1 if args.t1 is not None else TM["duration_s"]
    for f in range(int(args.t0 * FPS) // args.step * args.step, int(t1 * FPS) + 1, args.step):
        t = f / FPS
        if (args.flat or shot_at(t) in PLAN["shots"]) and render(t, out / f"f_{f:05d}.png"):
            n += 1
            if n % 100 == 0:
                print(f"{n} frames, {time.time() - t_start:.0f} s", flush=True)
print(f"rendered {n} in {time.time() - t_start:.0f} s -> {out}")
