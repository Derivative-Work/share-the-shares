"""C2 pose test: each puppet at rest and in three extreme poses, as stills, so the cuts can be judged at full swing.

What to judge: the hinge edges stay clean; what a moved part uncovers reads as engraving; the paper reads as cut
paper. Angles are the largest each shot plausibly needs, larger than the cast test's (which was too small to see).\nSince the re-cut (every moving part traced by hand), the hinges are new: Progress's arm bends at the elbow, Mercury\nhas a third leg layer, and each cherub sways on its own body while the scrollwork stays put.
Usage: blender -b --factory-startup --python scenes/blender/c2_poses.py -- <certificate dir> <out dir> <width> <height> <samples>
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
layout = json.loads((cert / "layout.json").read_text())["boxes"]

# pose name -> {layer: degrees about its hinge}; positive = counter-clockwise on the page
POSES = {
    "progress": [("rest", {}),
                 ("torch raised", {"arm": 22}),
                 ("head turned, jaw open", {"head": 14, "jaw": -14}),
                 ("forearm in, body leaning", {"arm": -18, "body": 6})],
    "prudence": [("rest", {}),
                 ("scales up", {"scales_arm": 24}),
                 ("scales down, head tilted", {"scales_arm": -14, "head": -12}),
                 ("sword arm out, jaw open", {"sword_arm": -20, "jaw": -8})],
    "mercury": [("rest", {}),
                ("stride, wing up", {"leg_back": 30, "leg_front": -30, "leg_bent": -25, "wing": 25}),
                ("stride the other way, wing down", {"leg_back": -28, "leg_front": 28, "leg_bent": 25, "wing": -20}),
                ("caduceus raised, head up", {"arm": 22, "head": 14})],
    "cherubs": [("rest", {}),
                ("heads turned left", {"head_top": 20, "head_left": 20, "head_center": 20}),
                ("heads turned right", {"head_top": -20, "head_left": -20, "head_center": -20}),
                ("swaying, arm lifted", {"body_top": 6, "body_left": -8, "body_center": 8, "arm_left": -40})],
}

scene = S.setup(w, h, samples, 1)
S.sheet(cert)
S.desk()
S.lights()
P.print_piece("laborer", layout["laborer"], src=S.LOOK["laborer_ink"])
pup = {n: P.build(n, layout[n]) for n in POSES}
P.build("cherubs", layout["cherubs_mirror"], mirror=True)
scene.render.image_settings.file_format = "PNG"
out.mkdir(parents=True, exist_ok=True)
for name, poses in POSES.items():
    x0, y0, x1, y1 = layout[name]
    c = S.px_to_world((x0 + x1) / 2, (y0 + y1) / 2)
    c.z = S.curl(c.x, c.y)
    span = (x1 - x0) / S.PW * S.SW
    cam = S.camera(c + Vector((0.0, -0.25 * span * 1.7, span * 1.7)), c, 50)
    for i, (label, angles) in enumerate(poses):
        for ln, ob in pup[name].items():
            ob.rotation_euler[2] = math.radians(angles.get(ln, 0.0))
        scene.render.filepath = str(out / f"{name}_{i}.png")
        bpy.ops.render.render(write_still=True)
    for ob in pup[name].values():
        ob.rotation_euler[2] = 0.0
    bpy.data.objects.remove(cam)
(out / "poses.json").write_text(json.dumps({n: [p[0] for p in ps] for n, ps in POSES.items()}, indent=1))
print("wrote", out)
