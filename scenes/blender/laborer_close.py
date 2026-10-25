"""A still of the laborer's corner, S07's framing (as C1's close test frame), to check the raised hammer.
Usage: blender -b --factory-startup --python scenes/blender/laborer_close.py -- <certificate dir> <out.png> <width> <height> <samples>
"""
import json
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
box = json.loads((cert / "layout.json").read_text())["boxes"]["laborer"]
scene = S.setup(w, h, samples, 1)
S.sheet(cert)
S.desk()
S.lights()
P.print_piece("laborer", box, src=S.LOOK["laborer_ink"])
x0, y0, x1, y1 = box
c = S.px_to_world((x0 + x1) / 2, (y0 + y1) / 2)
c.z = S.curl(c.x, c.y)
span = (x1 - x0) / S.PW * S.SW
S.camera(c + Vector((0.0, -0.3 * span * 1.6, span * 1.6)), c, 50)
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
