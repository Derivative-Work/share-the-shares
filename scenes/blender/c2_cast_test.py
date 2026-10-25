"""Cast test: every puppet on the certificate, moving through the gestures its shots need, on twos, lines boiling.

Not a shot. A check that the cuts hinge cleanly, that what a swing uncovers reads as engraving, and that the paper
reads as cut paper under the document camera's light.
  Progress   spear arm swings (the torch raise, S03/S05), head turns, jaw talks (the intro), body sways
  Prudence   scales arm weighs (S18), sword arm shifts (the pen, scissors), head tilts, jaw sings (verse 2)
  Mercury    legs scissor and the wing flaps (the sprint, S10), arm and caduceus point, head turns
  Cherubs    the group sways (the chorus), heads turn (S04), the left arm lifts (pointing, S17)
Usage: blender -b --factory-startup --python scenes/blender/c2_cast_test.py -- <certificate dir> <out dir> <width> <height> <samples> <view> [frames]
  view: wide | progress | prudence | mercury | cherubs
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import puppet as P  # noqa: E402
import sheet as S  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
cert, out = Path(args[0]), Path(args[1])
w, h, samples = (int(a) for a in args[2:5])
view = args[5]
frames = int(args[6]) if len(args) > 6 else 96
layout = json.loads((cert / "layout.json").read_text())["boxes"]

scene = S.setup(w, h, samples, frames)
S.sheet(cert)
S.desk()
S.lights()
P.print_piece("laborer", layout["laborer"])
pup = {name: P.build(name, layout[name]) for name in ("progress", "prudence", "mercury", "cherubs")}
pup["cherubs_mirror"] = P.build("cherubs", layout["cherubs_mirror"], mirror=True)

T = lambda f: (f - 1) / S.LOOK["fps"]  # noqa: E731  seconds
sin = lambda hz, ph=0.0: (lambda f: math.sin(2 * math.pi * hz * T(f) + ph))  # noqa: E731
F0, F1 = 1, frames

g = pup["progress"]
P.hinge(g["arm"], lambda f: -14 * math.sin(math.pi * T(f) / 2) ** 2, F0, F1)
P.hinge(g["head"], lambda f: 5 * sin(0.5)(f), F0, F1)
P.hinge(g["jaw"], lambda f: -9 * max(0.0, sin(3.0)(f)), F0, F1)
P.hinge(g["body"], lambda f: 1.5 * sin(0.4)(f), F0, F1)

g = pup["prudence"]
P.hinge(g["scales_arm"], lambda f: 6 * sin(0.7)(f), F0, F1)
P.hinge(g["sword_arm"], lambda f: 4 * sin(0.5, 1.0)(f), F0, F1)
P.hinge(g["head"], lambda f: 4 * sin(0.4)(f), F0, F1)
P.hinge(g["jaw"], lambda f: -9 * max(0.0, sin(2.5)(f)), F0, F1)

g = pup["mercury"]
P.hinge(g["leg_back"], lambda f: 14 * sin(1.5)(f), F0, F1)
P.hinge(g["leg_front"], lambda f: -14 * sin(1.5)(f), F0, F1)
P.hinge(g["wing"], lambda f: 12 * sin(2.0)(f), F0, F1)
P.hinge(g["arm"], lambda f: 6 * sin(0.8)(f), F0, F1)
P.hinge(g["head"], lambda f: 4 * sin(0.6)(f), F0, F1)
P.hinge(g["body"], lambda f: 3 * sin(1.5, 0.5)(f), F0, F1)

for k, ph in (("cherubs", 0.0), ("cherubs_mirror", 0.6)):
    g = pup[k]
    P.hinge(g["body"], lambda f, ph=ph: 3 * sin(0.5, ph)(f), F0, F1)
    for i, hd in enumerate(("head_top", "head_left", "head_center")):
        P.hinge(g[hd], lambda f, i=i, ph=ph: 7 * sin(0.45, ph + 1.3 * i)(f), F0, F1)
    P.hinge(g["arm_left"], lambda f, ph=ph: -18 * max(0.0, sin(0.5, ph)(f)), F0, F1)

if view == "wide":
    S.camera((0.0, -0.20, 0.42), (0, 0.004, 0), 40)
else:
    boxes = [layout[view]] + ([layout["cherubs_mirror"]] if view == "cherubs" else [])
    if view == "cherubs":
        boxes = [layout["cherubs"]]
    x0, y0, x1, y1 = boxes[0]
    c = S.px_to_world((x0 + x1) / 2, (y0 + y1) / 2)
    c.z = S.curl(c.x, c.y)
    span = (x1 - x0) / S.PW * S.SW
    S.camera(c + Vector((0.0, -0.35 * span * 1.6, span * 1.6)), c, 50, 16.0)

out.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(out / "f_")
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(animation=True)
print("wrote", out)
