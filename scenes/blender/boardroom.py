"""The empty boardroom: a virtual background for the call page (the live verse, S30), as the human's webcam sees it.

Seen from the head of a long board table, at a seated webcam's height, down the room: high-backed chairs on both
sides, all empty; tall windows on the left with the sun coming in, panelled walls, portraits and a fireplace on the
right, a clock on the far wall. The human sits where the chairman would, in front of the far wall (kept plain behind
the head, so the key has a quiet edge to work against). The joke is the side panel's "Board (not joined)".

Writes four passes for scripts/call_backgrounds.py, which engraves them (line hatching that follows each surface):
  tone.png       16-bit grey: the lit scene (Eevee), the windows' sky transparent
  normal.npy     float32 H x W x 3: world normals, (n + 1) / 2 (and normal.exr, the same)
  position.npy   float32 H x W x 3: world position, (p + 16) / 32 m (and position.exr)
  alpha is 0 where the camera sees sky (through the windows)
Usage: blender -b --factory-startup --python scenes/blender/boardroom.py -- <out dir> [width height]
"""
import math
import sys
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0] if argv else "renders/call_backgrounds/boardroom")
W, H = (int(argv[1]), int(argv[2])) if len(argv) > 2 else (5120, 2880)
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---- materials ---------------------------------------------------------------------------------------------------
MATS = {}


def mat(name, grey, spec=0.1):
    if name not in MATS:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (grey, grey, grey, 1)
        b.inputs["Roughness"].default_value = 0.85
        b.inputs["Specular IOR Level"].default_value = spec
        MATS[name] = m
    return MATS[name]


def box(name, c, s, m, rz=0.0):
    """A box centred at c with size s, turned rz about Z."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=c, rotation=(0, 0, rz))
    o = bpy.context.object
    o.name = name
    o.scale = s
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o.data.materials.append(m)
    return o


def cyl(name, c, r, h, m, verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=c)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    return o


WALL, PANEL, WOOD, LEATHER = mat("wall", 0.72), mat("panel", 0.42), mat("wood", 0.13, 0.3), mat("leather", 0.09)
CARPET, BORDER, CEIL, FRAME = mat("carpet", 0.38), mat("carpet_border", 0.16), mat("ceiling", 0.8), mat("frame", 0.3)
CANVAS, STONE, DARK, PAPER = mat("canvas", 0.07), mat("stone", 0.62), mat("dark", 0.02), mat("blotter", 0.55)

# ---- the room: x across (-3.6..3.6), y down its length (0..11.5), z up (0..4.4) -----------------------------------
X0, X1, Y1, Z1 = -3.6, 3.6, 11.5, 4.4
T = 0.3  # wall thickness
box("floor", (0, Y1 / 2, -0.05), (X1 - X0, Y1 + 2, 0.1), CARPET)
box("carpet_border", (0, 5.0, 0.002), (5.2, 9.6, 0.004), BORDER)
box("carpet_field", (0, 5.0, 0.004), (4.7, 9.1, 0.004), CARPET)
box("ceiling", (0, Y1 / 2, Z1 + 0.05), (X1 - X0, Y1 + 2, 0.1), CEIL)
box("far_wall", (0, Y1 + T / 2, Z1 / 2), (X1 - X0 + 2 * T, T, Z1), WALL)
box("near_wall", (0, -1.5 - T / 2, Z1 / 2), (X1 - X0 + 2 * T, T, Z1), WALL)
# the right wall, whole; the left wall in piers, with tall windows between (sill 0.9, head 3.5)
box("right_wall", (X1 + T / 2, Y1 / 2 - 0.75, Z1 / 2), (T, Y1 + 1.5, Z1), WALL)
WIN = [(1.6, 2.8), (4.6, 5.8), (7.6, 8.8)]  # window spans in y
edges = [-1.5] + [v for w in WIN for v in w] + [Y1]
for i in range(0, len(edges), 2):
    a, b = edges[i], edges[i + 1]
    box(f"left_pier_{i}", (X0 - T / 2, (a + b) / 2, Z1 / 2), (T, b - a, Z1), WALL)
for i, (a, b) in enumerate(WIN):
    box(f"left_sill_{i}", (X0 - T / 2, (a + b) / 2, 0.45), (T, b - a, 0.9), WALL)
    box(f"left_head_{i}", (X0 - T / 2, (a + b) / 2, (3.5 + Z1) / 2), (T, b - a, Z1 - 3.5), WALL)
    # sash bars: a frame, one mullion, three transoms
    for z in (0.92, 1.55, 2.2, 2.85, 3.48):
        box(f"win_{i}_tr_{z}", (X0 - 0.08, (a + b) / 2, z), (0.05, b - a, 0.045), FRAME)
    for y in (a + 0.02, (a + b) / 2, b - 0.02):
        box(f"win_{i}_mu_{y:.2f}", (X0 - 0.08, y, 2.2), (0.05, 0.045, 2.6), FRAME)
    box(f"win_{i}_seat", (X0 + 0.06, (a + b) / 2, 0.88), (0.22, b - a + 0.1, 0.06), WOOD)
    # curtains, drawn back to each side
    for j, y in enumerate((a - 0.16, b + 0.16)):
        box(f"curtain_{i}_{j}", (X0 + 0.1, y, 2.05), (0.12, 0.32, 3.1), mat("curtain", 0.22))

# wainscot (dado to 1.1 m) with raised panels, on the far and right walls and the left piers
DADO = 1.1
box("dado_far", (0, Y1 - 0.02, DADO / 2), (X1 - X0, 0.04, DADO), PANEL)
box("dado_right", (X1 - 0.02, Y1 / 2 - 0.75, DADO / 2), (0.04, Y1 + 1.5, DADO), PANEL)
box("rail_far", (0, Y1 - 0.05, DADO), (X1 - X0, 0.08, 0.07), WOOD)
box("rail_right", (X1 - 0.05, Y1 / 2 - 0.75, DADO), (0.08, Y1 + 1.5, 0.07), WOOD)
box("base_far", (0, Y1 - 0.04, 0.09), (X1 - X0, 0.06, 0.18), WOOD)
box("base_right", (X1 - 0.04, Y1 / 2 - 0.75, 0.09), (0.06, Y1 + 1.5, 0.18), WOOD)
for k in range(6):
    x = X0 + 0.3 + k * (X1 - X0 - 0.6) / 6 + (X1 - X0 - 0.6) / 12
    box(f"dpanel_far_{k}", (x, Y1 - 0.05, 0.6), ((X1 - X0 - 0.6) / 6 - 0.2, 0.03, 0.62), WOOD)
for k in range(11):
    y = -1.0 + k * 1.15 + 0.5
    box(f"dpanel_right_{k}", (X1 - 0.05, y, 0.6), (0.03, 0.95, 0.62), WOOD)
for i in range(0, len(edges), 2):
    a, b = edges[i], edges[i + 1]
    box(f"dado_left_{i}", (X0 + 0.02, (a + b) / 2, DADO / 2), (0.04, b - a, DADO), PANEL)
    box(f"rail_left_{i}", (X0 + 0.05, (a + b) / 2, DADO), (0.08, b - a, 0.07), WOOD)
# cornice and a coffered ceiling
for nm, c, s in (("cornice_far", (0, Y1 - 0.15, Z1 - 0.15), (X1 - X0, 0.3, 0.3)),
                 ("cornice_right", (X1 - 0.15, Y1 / 2 - 0.75, Z1 - 0.15), (0.3, Y1 + 1.5, 0.3)),
                 ("cornice_left", (X0 + 0.15, Y1 / 2 - 0.75, Z1 - 0.15), (0.3, Y1 + 1.5, 0.3))):
    box(nm, c, s, mat("cornice", 0.66))
for k in range(1, 6):
    box(f"beam_{k}", (0, -1.5 + k * 2.15, Z1 - 0.12), (X1 - X0, 0.22, 0.24), mat("cornice", 0.66))
box("beam_long", (0, Y1 / 2 - 0.75, Z1 - 0.1), (0.22, Y1 + 1.5, 0.2), mat("cornice", 0.66))
# pilasters on the right wall, between the portraits
for k, y in enumerate((0.4, 3.4, 6.4, 9.4)):
    box(f"pilaster_{k}", (X1 - 0.06, y, (DADO + Z1 - 0.3) / 2), (0.12, 0.34, Z1 - 0.3 - DADO), mat("cornice", 0.66))

# the right wall: portraits of the board (dark canvases in gilt frames) and a fireplace
for k, y in enumerate((1.9, 7.9)):
    box(f"portrait_frame_{k}", (X1 - 0.04, y, 2.55), (0.06, 1.25, 1.6), FRAME)
    box(f"portrait_{k}", (X1 - 0.08, y, 2.55), (0.04, 1.0, 1.35), CANVAS)
box("chimney_breast", (X1 - 0.2, 4.9, 2.2), (0.4, 1.9, 4.4), WALL)
box("mantel", (X1 - 0.45, 4.9, 1.25), (0.32, 2.0, 0.09), STONE)
for y in (4.15, 5.65):
    box(f"jamb_{y}", (X1 - 0.43, y, 0.6), (0.12, 0.28, 1.2), STONE)
box("hearth_open", (X1 - 0.39, 4.9, 0.5), (0.02, 1.2, 1.0), DARK)
box("over_mantel", (X1 - 0.42, 4.9, 2.6), (0.04, 1.3, 1.2), FRAME)
box("over_mantel_glass", (X1 - 0.45, 4.9, 2.6), (0.02, 1.1, 1.0), mat("mirror", 0.5))

# the far wall: a double door (behind the head) and a clock above it, two portraits either side
box("door_case", (0, Y1 - 0.05, 1.35), (1.8, 0.1, 2.7), FRAME)
box("door", (0, Y1 - 0.08, 1.3), (1.5, 0.06, 2.55), WOOD)
box("door_pediment", (0, Y1 - 0.1, 2.85), (2.1, 0.2, 0.18), mat("cornice", 0.66))
cyl("clock_case", (0, Y1 - 0.08, 3.55), 0.42, 0.12, FRAME, 48).rotation_euler = (math.pi / 2, 0, 0)
cyl("clock_face", (0, Y1 - 0.15, 3.55), 0.36, 0.04, mat("clock_face", 0.85), 48).rotation_euler = (math.pi / 2, 0, 0)
for k, x in enumerate((-2.3, 2.3)):
    box(f"far_portrait_frame_{k}", (x, Y1 - 0.04, 2.45), (1.1, 0.06, 1.45), FRAME)
    box(f"far_portrait_{k}", (x, Y1 - 0.08, 2.45), (0.88, 0.04, 1.2), CANVAS)

# ---- the table and the chairs ------------------------------------------------------------------------------------
TY0, TY1, TW, TZ = 0.25, 8.6, 1.7, 0.76
box("table_top", (0, (TY0 + TY1) / 2, TZ - 0.03), (TW, TY1 - TY0, 0.06), WOOD)
box("table_apron", (0, (TY0 + TY1) / 2, TZ - 0.13), (TW - 0.12, TY1 - TY0 - 0.12, 0.14), WOOD)
for y in (TY0 + 0.15, (TY0 + TY1) / 2, TY1 - 0.15):
    for x in (-TW / 2 + 0.15, TW / 2 - 0.15):
        box(f"table_leg_{x}_{y}", (x, y, (TZ - 0.2) / 2), (0.1, 0.1, TZ - 0.2), WOOD)


def chair(name, ox, oy, face, scale=1.0):
    """A high-backed board chair at (ox, oy), facing `face` radians (0 = toward -y)."""
    c, s = math.cos(face), math.sin(face)

    def part(nm, lx, ly, lz, sx, sy, sz, m):
        box(f"{name}_{nm}", (ox + lx * c - ly * s, oy + lx * s + ly * c, lz), (sx, sy, sz), m, rz=face)

    k = scale
    part("seat", 0, 0, 0.48, 0.52 * k, 0.5, 0.09, LEATHER)
    for lx in (-0.22 * k, 0.22 * k):
        for ly in (-0.21, 0.21):
            part(f"leg{lx}{ly}", lx, ly, 0.22, 0.05, 0.05, 0.44, WOOD)
        part(f"stile{lx}", lx, 0.23, 0.48 + 0.42 * k, 0.06, 0.06, 0.84 * k, WOOD)
        part(f"arm{lx}", lx, 0.0, 0.71, 0.06, 0.46, 0.05, WOOD)
        part(f"armpost{lx}", lx, -0.2, 0.6, 0.05, 0.05, 0.22, WOOD)
    part("back", 0, 0.24, 0.5 + 0.4 * k, 0.4 * k, 0.07, 0.62 * k, LEATHER)
    part("crest", 0, 0.24, 0.5 + 0.84 * k, 0.56 * k, 0.07, 0.07, WOOD)


SEATS = [1.45 + 1.0 * i for i in range(7)]
for i, y in enumerate(SEATS):
    chair(f"chair_L{i}", -TW / 2 - 0.42, y, -math.pi / 2)   # facing +x
    chair(f"chair_R{i}", TW / 2 + 0.42, y, math.pi / 2)     # facing -x
    for side, x in (("L", -TW / 2 + 0.28), ("R", TW / 2 - 0.28)):
        box(f"blotter_{side}{i}", (x, y, TZ + 0.003), (0.36, 0.48, 0.006), PAPER)
        box(f"folder_{side}{i}", (x, y + 0.02, TZ + 0.012), (0.22, 0.31, 0.012), mat("folder", 0.78))
chair("chair_head", 0, TY1 + 0.45, math.pi, 1.25)            # the far end, facing the camera, also empty
for k, y in enumerate((2.7, 6.2)):
    cyl(f"inkstand_{k}", (0, y, TZ + 0.03), 0.09, 0.06, FRAME)
    cyl(f"carafe_{k}", (0.12, y, TZ + 0.13), 0.06, 0.26, mat("carafe", 0.6))

# ---- light: sun through the left windows, the sky, a dim fill from the near end -------------------------------------
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 5.0
sun.angle = math.radians(1.5)
so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(58), 0, math.radians(-118))  # from the left and a little behind
scene.collection.objects.link(so)
for i, (a, b) in enumerate(WIN):  # sky light through each window
    al = bpy.data.lights.new(f"window_{i}", "AREA")
    al.shape, al.size, al.size_y, al.energy = "RECTANGLE", b - a, 2.6, 900
    ao = bpy.data.objects.new(f"window_{i}", al)
    ao.location = (X0 - 0.35, (a + b) / 2, 2.2)
    ao.rotation_euler = (0, math.radians(90), 0)  # pointing +x, into the room
    scene.collection.objects.link(ao)
fl = bpy.data.lights.new("fill", "AREA")
fl.size, fl.energy = 5.0, 450
fo = bpy.data.objects.new("fill", fl)
fo.location = (0.5, -1.2, 3.6)
fo.rotation_euler = (math.radians(-65), 0, 0)
scene.collection.objects.link(fo)

world = bpy.data.worlds.new("sky")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.85, 0.88, 0.95, 1)
bg.inputs[1].default_value = 0.35
scene.world = world

# ---- the webcam: at the head of the table, seated eye height, level, a webcam's field of view -------------------
cam = bpy.data.cameras.new("webcam")
cam.lens, cam.sensor_width, cam.sensor_fit = 24, 36, "HORIZONTAL"  # ~74 degrees across
co = bpy.data.objects.new("webcam", cam)
co.location = (0, -1.05, 1.22)
co.rotation_euler = (math.radians(90), 0, 0)  # looking +y, level: verticals stay vertical
scene.collection.objects.link(co)
scene.camera = co

r = scene.render
r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y, r.resolution_percentage = W, H, 100
r.film_transparent = True
r.image_settings.file_format = "PNG"
r.image_settings.color_depth = "16"
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = 1.0  # a bright room: the engraving keeps the walls mostly paper
scene.eevee.taa_render_samples = 64
try:
    scene.eevee.use_raytracing = True
    scene.eevee.use_shadows = True
except AttributeError:
    pass


def emission_override(name, build):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(em.outputs[0], out.inputs[0])
    build(nt, em.inputs[0])
    return m


def normal_colour(nt, sock):
    g = nt.nodes.new("ShaderNodeNewGeometry")
    v = nt.nodes.new("ShaderNodeVectorMath")
    v.operation = "MULTIPLY_ADD"
    v.inputs[1].default_value = (0.5, 0.5, 0.5)
    v.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(g.outputs["Normal"], v.inputs[0])
    nt.links.new(v.outputs[0], sock)


def position_colour(nt, sock):
    g = nt.nodes.new("ShaderNodeNewGeometry")
    v = nt.nodes.new("ShaderNodeVectorMath")
    v.operation = "MULTIPLY_ADD"
    v.inputs[1].default_value = (1 / 32, 1 / 32, 1 / 32)
    v.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(g.outputs["Position"], v.inputs[0])
    nt.links.new(v.outputs[0], sock)


vl = scene.view_layers[0]
r.filepath = str(OUT / "tone.png")
bpy.ops.render.render(write_still=True)
# the data passes: flat emission, no light, no anti-aliasing blur across edges beyond the filter
# in Cycles: Eevee's film is half float (position steps of 1/2048), Cycles' is full; one sample, no filter
r.engine = "CYCLES"
scene.cycles.samples = 1
scene.cycles.use_denoising = False
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    scene.cycles.device = "GPU"
except Exception as e:  # CPU is fine at one sample
    print("cycles on CPU:", e)
r.filter_size = 0.01
bg.inputs[1].default_value = 0.0
scene.view_settings.view_transform = "Raw"  # the data passes are written as they are
scene.view_settings.exposure = 0.0
# float EXR, then a .npy of it (16-bit PNG steps every 0.5 mm of position, too coarse for the hatching's spacing)
import numpy as np  # noqa: E402  (Blender's own)
r.image_settings.file_format = "OPEN_EXR"
r.image_settings.color_depth = "32"
for nm, fn in (("normal", normal_colour), ("position", position_colour)):
    vl.material_override = emission_override(nm, fn)
    r.filepath = str(OUT / f"{nm}.exr")
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(str(OUT / f"{nm}.exr"))
    buf = np.empty(W * H * 4, np.float32)
    img.pixels.foreach_get(buf)
    np.save(OUT / f"{nm}.npy", buf.reshape(H, W, 4)[::-1, :, :3])
    bpy.data.images.remove(img)
print("BOARDROOM_DONE", OUT)
