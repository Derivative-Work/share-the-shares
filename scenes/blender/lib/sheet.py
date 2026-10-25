"""The certificate world shared by every shot: render settings, the sheet, the desk, the document-camera light.

Same values as C1 (scenes/blender/c1_test_frame.py, approved): Standard view, the sheet's curl, raised ink, matte
paper, the calibrated key and fill. Coordinates: the sheet lies in the XY plane, centred, +Y up the page; sheet
pixels (4400 x 3400) map to metres with px_to_world.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
LOOK = json.loads((ROOT / "config/look.json").read_text())
SW, SH = (v * 0.0254 for v in LOOK["sheet"]["size_in"])
PW, PH = (int(v * LOOK["sheet"]["dpi"]) for v in LOOK["sheet"]["size_in"])


def srgb(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


def px_to_world(x, y):
    return Vector(((x / PW - 0.5) * SW, (0.5 - y / PH) * SH, 0.0))


def curl(x, y):
    """The sheet's height (m) at world x, y: the long edges lift more than the short ones."""
    return 0.0035 * abs(2 * y / SH) ** 3 + 0.0012 * abs(2 * x / SW) ** 4


def image(path, non_color=False):
    im = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        im.colorspace_settings.name = "Non-Color"
    return im


def setup(w, h, samples, frames=1):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = w, h, 100
    scene.render.fps = LOOK["fps"]
    scene.frame_start, scene.frame_end = 1, frames
    scene.eevee.taa_render_samples = samples
    scene.eevee.use_shadows = True
    scene.eevee.shadow_pool_size = "2048"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    world = bpy.data.worlds.new("room")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb("#3A332C")
    bg.inputs["Strength"].default_value = 0.35
    scene.world = world
    return scene


def patch(name, x0, y0, x1, y1, lift, nx=48, ny=48, bend=True):
    """A grid over the sheet-pixel box (x0, y0)-(x1, y1), `lift` metres above the paper, bent to the curl."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=1.0)
    ob = bpy.context.object
    ob.name = name
    a, b = px_to_world(x0, y1), px_to_world(x1, y0)
    for v in ob.data.vertices:
        u, t = v.co.x + 0.5, v.co.y + 0.5
        v.co.x, v.co.y = a.x + u * (b.x - a.x), a.y + t * (b.y - a.y)
        v.co.z = (curl(v.co.x, v.co.y) if bend else 0.0) + lift
    bpy.ops.object.shade_smooth()
    return ob


def ink_bump(nodes, links, height_socket, bsdf, strength=0.35):
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = 0.00015
    links.new(height_socket, bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def sheet(cert):
    """The static print (no figures) as the paper."""
    ob = patch("certificate", 0, 0, PW, PH, 0.0, 96, 76)
    mat = bpy.data.materials.new("paper")
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image(Path(cert) / "static/sheet.png")
    tex.interpolation = "Cubic"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.82
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    gp, kp = nodes.new("ShaderNodeTexImage"), nodes.new("ShaderNodeTexImage")
    gp.image = image(Path(cert) / "static/plate_green.png", True)
    kp.image = image(Path(cert) / "static/plate_sepia.png", True)
    mx = nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    links.new(gp.outputs["Color"], mx.inputs[0])
    links.new(kp.outputs["Color"], mx.inputs[1])
    ink_bump(nodes, links, mx.outputs["Value"], bsdf)
    ob.data.materials.append(mat)
    return ob


def desk():
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0, -0.0005))
    ob = bpy.context.object
    m = bpy.data.materials.new("desk")
    n, l = m.node_tree.nodes, m.node_tree.links
    b = n["Principled BSDF"]
    wave = n.new("ShaderNodeTexWave")
    wave.wave_type, wave.bands_direction = "BANDS", "X"
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 9.0
    wave.inputs["Detail"].default_value = 4.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(LOOK["palette"]["desk"])
    ramp.color_ramp.elements[1].color = srgb(LOOK["palette"]["desk_light"])
    l.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.45
    ob.data.materials.append(m)
    return ob


def lights():
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
    return key, fill


def camera(location, target, lens, fstop=None):
    scene = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    cam.location = Vector(location)
    cam.data.lens = lens
    cam.data.clip_start = 0.002  # document-camera close-ups sit under the 0.1 m default
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = (cam.location - Vector(target)).length
        cam.data.dof.aperture_fstop = fstop
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    return cam
