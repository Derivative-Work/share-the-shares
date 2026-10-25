"""C1 test frame: the certificate as a printed sheet on a desk, under a document camera's light.

The sheet is scripts/certificate.py's static print (11 x 8.5 in, no figures), raised ink (intaglio) as a bump from
its two plates, with a slight curl at the edges. Each figure is its own ink layer laid on the paper at its layout
box, at the ink piece's source resolution, following the same curl: the layers later shots animate.
Views: "wide" (S02's push, early: the whole sheet on the desk) and "close" (the laborer's corner, S07's framing).
Usage: blender -b --factory-startup --python scenes/blender/c1_test_frame.py -- <certificate dir> <out.png> [width height samples [wide|close]]
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
LOOK = json.loads((ROOT / "config/look.json").read_text())
args = sys.argv[sys.argv.index("--") + 1:]
cert, out_path = Path(args[0]), args[1]
w, h, samples = (int(a) for a in args[2:5]) if len(args) >= 5 else (1280, 720, 32)
view = args[5] if len(args) >= 6 else "wide"

SW, SH = (v * 0.0254 for v in LOOK["sheet"]["size_in"])  # sheet size in metres
layout = json.loads((cert / "layout.json").read_text())
PW, PH = layout["size"]
FIGURES = ["progress", "cherubs", "cherubs_mirror", "prudence", "mercury", "laborer"]


def srgb(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def px_to_world(x, y):
    return Vector(((x / PW - 0.5) * SW, (0.5 - y / PH) * SH, 0.0))


def curl(x, y):
    """The sheet's height (m) at world x, y: the long edges lift more than the short ones."""
    return 0.0035 * abs(2 * y / SH) ** 3 + 0.0012 * abs(2 * x / SW) ** 4


def image(path, non_color=False):
    im = bpy.data.images.load(str(path))
    if non_color:
        im.colorspace_settings.name = "Non-Color"
    return im


def patch(name, x0, y0, x1, y1, lift, nx=48, ny=48):
    """A grid over the pixel box (x0, y0)-(x1, y1) of the sheet, bent to the curl, `lift` metres above the paper."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=1.0)
    ob = bpy.context.object
    ob.name = name
    a, b = px_to_world(x0, y1), px_to_world(x1, y0)  # world min and max corners
    for v in ob.data.vertices:
        u, t = v.co.x + 0.5, v.co.y + 0.5
        v.co.x, v.co.y = a.x + u * (b.x - a.x), a.y + t * (b.y - a.y)
        v.co.z = curl(v.co.x, v.co.y) + lift
    bpy.ops.object.shade_smooth()
    return ob


def ink_bump(nodes, links, height_socket, bsdf, strength):
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.00015
    links.new(height_socket, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


# ---- scene ------------------------------------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = w, h, 100
scene.render.fps = LOOK["fps"]
scene.eevee.taa_render_samples = samples
scene.eevee.use_shadows = True
scene.eevee.shadow_pool_size = "2048"
# Standard, not AgX: paper and inks should read as the printed colours under a neutral document-camera light.
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0.0

world = bpy.data.worlds.new("room")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = srgb("#3A332C")
bg.inputs["Strength"].default_value = 0.35
scene.world = world

# ---- the sheet: static art ----------------------------------------------------------------------------------------
sheet = patch("certificate", 0, 0, PW, PH, 0.0, 96, 76)
mat = bpy.data.materials.new("paper")
nodes, links = mat.node_tree.nodes, mat.node_tree.links
bsdf = nodes["Principled BSDF"]
tex = nodes.new("ShaderNodeTexImage")
tex.image = image(cert / "static/sheet.png")
tex.interpolation = "Cubic"
links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.82
bsdf.inputs["Specular IOR Level"].default_value = 0.25
gp, kp = nodes.new("ShaderNodeTexImage"), nodes.new("ShaderNodeTexImage")
gp.image, kp.image = image(cert / "static/plate_green.png", True), image(cert / "static/plate_sepia.png", True)
mx = nodes.new("ShaderNodeMath")
mx.operation = "MAXIMUM"
links.new(gp.outputs["Color"], mx.inputs[0])
links.new(kp.outputs["Color"], mx.inputs[1])
ink_bump(nodes, links, mx.outputs["Value"], bsdf, 0.35)  # raised ink
sheet.data.materials.append(mat)

# ---- the figures: sepia ink layers on the paper ---------------------------------------------------------------------
for i, name in enumerate(FIGURES):
    piece = name.removesuffix("_mirror")
    ob = patch(name, *layout["boxes"][name], lift=0.0002 + 0.00002 * i)
    if name.endswith("_mirror"):
        for loop in ob.data.uv_layers.active.data:
            loop.uv.x = 1.0 - loop.uv.x
    m = bpy.data.materials.new(f"ink_{name}")
    m.surface_render_method = "BLENDED"
    m.use_transparency_overlap = False
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    t = n.new("ShaderNodeTexImage")
    t.image = image(ROOT / "assets/engravings/ink" / f"{piece}.png", True)
    t.interpolation = "Cubic"
    ink = n.new("ShaderNodeBsdfPrincipled")
    # ink x paper: a layer composites over the paper, the press multiplies into it; this makes the two agree
    ink.inputs["Base Color"].default_value = [i * p for i, p in zip(srgb(LOOK["palette"]["ink_sepia"]), srgb(LOOK["palette"]["paper"]))]
    ink.inputs["Roughness"].default_value = 0.82  # the paper's: matte ink, no grey sheen at low angles
    ink.inputs["Specular IOR Level"].default_value = 0.25
    ink_bump(n, l, t.outputs["Color"], ink, 0.35)
    clear = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    l.new(t.outputs["Color"], mix.inputs["Fac"])
    l.new(clear.outputs["BSDF"], mix.inputs[1])
    l.new(ink.outputs["BSDF"], mix.inputs[2])
    l.new(mix.outputs["Shader"], out.inputs["Surface"])
    ob.data.materials.append(m)

# ---- the desk: dark wood ----------------------------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.0005))
desk = bpy.context.object
dm = bpy.data.materials.new("desk")
dn, dl = dm.node_tree.nodes, dm.node_tree.links
db = dn["Principled BSDF"]
wave = dn.new("ShaderNodeTexWave")
wave.wave_type, wave.bands_direction = "BANDS", "X"
wave.inputs["Scale"].default_value = 3.0
wave.inputs["Distortion"].default_value = 9.0
wave.inputs["Detail"].default_value = 4.0
ramp = dn.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = srgb(LOOK["palette"]["desk"])
ramp.color_ramp.elements[1].color = srgb(LOOK["palette"]["desk_light"])
dl.new(wave.outputs["Fac"], ramp.inputs["Fac"])
dl.new(ramp.outputs["Color"], db.inputs["Base Color"])
db.inputs["Roughness"].default_value = 0.45
desk.data.materials.append(dm)

# ---- light: a document camera's soft overhead box, plus a low warm fill from the room ------------------------------
bpy.ops.object.light_add(type="AREA", location=(0.05, -0.08, 0.75))
key = bpy.context.object
key.data.shape, key.data.size, key.data.size_y = "RECTANGLE", 0.7, 0.5
key.data.energy = float(LOOK["light"]["key_w"])
key.data.color = (1.0, 0.98, 0.95)
key.rotation_euler = (math.radians(8), 0, 0)
bpy.ops.object.light_add(type="AREA", location=(-0.6, 0.5, 0.35))
fill = bpy.context.object
fill.data.size, fill.data.energy, fill.data.color = 0.8, float(LOOK["light"]["fill_w"]), (1.0, 0.85, 0.7)
fill.rotation_euler = (math.radians(-50), math.radians(-45), 0)

# ---- camera -----------------------------------------------------------------------------------------------------
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
scene.camera = cam
if view == "wide":
    target = Vector((0, 0.004, 0))
    cam.location = Vector((0.0, -0.20, 0.42))
    cam.data.lens = 40
else:  # the laborer's corner: a document camera leaning in
    x0, y0, x1, y1 = layout["boxes"]["laborer"]
    target = px_to_world((x0 + x1) / 2, (y0 + y1) / 2)
    target.z = curl(target.x, target.y)
    cam.location = target + Vector((0.015, -0.055, 0.10))
    cam.data.lens = 60
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (cam.location - target).length
    cam.data.dof.aperture_fstop = 16.0
d = target - cam.location
cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

scene.render.filepath = out_path
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print("wrote", out_path)
