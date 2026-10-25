"""Paper puppets on the certificate: each figure's layers (scripts/puppet_build.py) as hinged planes.

A figure is placed by its box on the sheet (the certificate's layout.json). Its background is ink printed on the
sheet; its body and parts are paper cutouts (opaque paper carrying their ink, alpha from the cut) lifted a hair off
the page, so the key light gives each a thin cast shadow. Every layer's origin is its pivot and it is parented to
its parent layer, so a rotation about local Z is a hinge.

Animation is on twos (look.json `animation_on`): keys are sampled every two frames with constant interpolation.
The hatching boils: each layer's UVs are nudged by a noise field reseeded every two frames (about half a source
pixel), so the lines shimmer as hand-cut paper under a camera does, without the figure moving.
"""
import json
import math

import bpy
from mathutils import Vector

from sheet import LOOK, ROOT, curl, image, ink_bump, px_to_world, srgb

LIFT = {"background": 0.00015, "body": 0.00035}
PART_LIFT, PART_STEP = 0.00050, 0.00012
BOIL_PX = 0.5  # boil amplitude, in source pixels


def boil_uv(nodes, links, size_px):
    """UV + a small noise offset that changes every two frames (a driver on the noise's W)."""
    tc = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 40.0
    noise.inputs["Detail"].default_value = 1.0
    fcurve = noise.inputs["W"].driver_add("default_value")
    fcurve.driver.type = "SCRIPTED"
    fcurve.driver.expression = f"floor(frame / {LOOK['animation_on']}) * 7.31"
    links.new(tc.outputs["UV"], noise.inputs["Vector"])
    centred = nodes.new("ShaderNodeVectorMath")
    centred.operation = "SUBTRACT"
    centred.inputs[1].default_value = (0.5, 0.5, 0.5)
    links.new(noise.outputs["Color"], centred.inputs[0])
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (2 * BOIL_PX / size_px[0], 2 * BOIL_PX / size_px[1], 0.0)
    links.new(centred.outputs["Vector"], scale.inputs[0])
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    links.new(tc.outputs["UV"], add.inputs[0])
    links.new(scale.outputs["Vector"], add.inputs[1])
    return add.outputs["Vector"]


def curl_group():
    """Geometry nodes: z += the sheet's curl at each vertex's WORLD position (sheet.curl), so a layer keeps lying on
    the curved paper however its hinges turn it. Layers only turn about Z and are unscaled, so a world z offset is
    the same as a local one."""
    if "sheet_curl" in bpy.data.node_groups:
        return bpy.data.node_groups["sheet_curl"]
    from sheet import SH, SW
    g = bpy.data.node_groups.new("sheet_curl", "GeometryNodeTree")
    g.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    g.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n, l = g.nodes, g.links
    gin, gout = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    pos = n.new("GeometryNodeInputPosition")
    selfob = n.new("GeometryNodeSelfObject")
    info = n.new("GeometryNodeObjectInfo")
    info.transform_space = "ORIGINAL"
    l.new(selfob.outputs[0], info.inputs["Object"])
    tp = n.new("FunctionNodeTransformPoint")
    l.new(pos.outputs["Position"], tp.inputs["Vector"])
    l.new(info.outputs["Transform"], tp.inputs["Transform"])
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tp.outputs["Vector"], sep.inputs[0])

    def term(sock, half, power, k):
        m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m1.inputs[1].default_value = 1.0 / half
        l.new(sock, m1.inputs[0])
        ab = n.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; l.new(m1.outputs[0], ab.inputs[0])
        pw = n.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = power
        l.new(ab.outputs[0], pw.inputs[0])
        mk = n.new("ShaderNodeMath"); mk.operation = "MULTIPLY"; mk.inputs[1].default_value = k
        l.new(pw.outputs[0], mk.inputs[0])
        return mk.outputs[0]

    ty, tx = term(sep.outputs["Y"], SH / 2, 3.0, 0.0035), term(sep.outputs["X"], SW / 2, 4.0, 0.0012)
    add = n.new("ShaderNodeMath"); add.operation = "ADD"
    l.new(ty, add.inputs[0]); l.new(tx, add.inputs[1])
    comb = n.new("ShaderNodeCombineXYZ")
    l.new(add.outputs[0], comb.inputs["Z"])
    setp = n.new("GeometryNodeSetPosition")
    l.new(gin.outputs[0], setp.inputs["Geometry"])
    l.new(comb.outputs[0], setp.inputs["Offset"])
    l.new(setp.outputs[0], gout.inputs[0])
    return g


def layer_material(name, ink_path, mask_path, size_px, cutout):
    m = bpy.data.materials.new(name)
    # Cutouts: dithered (their alpha is the cut, nearly binary, so the dither only touches edges; dithered surfaces
    # write depth and stack correctly). Print-only layers: blended (smooth partial ink); Eevee draws only the
    # frontmost of several overlapping blended surfaces, so at most one blended layer may sit under any cutout.
    m.surface_render_method = "DITHERED" if cutout else "BLENDED"
    m.use_transparency_overlap = False
    n, l = m.node_tree.nodes, m.node_tree.links
    n.clear()
    out = n.new("ShaderNodeOutputMaterial")
    uv = boil_uv(n, l, size_px)
    ink = n.new("ShaderNodeTexImage")
    ink.image = image(ink_path, True)
    ink.interpolation = "Linear"  # mipmapped: the pieces are minified up to ~12x in wide shots; cubic aliases there
    l.new(uv, ink.inputs["Vector"])
    paper, sepia = srgb(LOOK["palette"]["paper"]), srgb(LOOK["palette"]["ink_sepia"])
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.82
    bsdf.inputs["Specular IOR Level"].default_value = 0.25
    ink_bump(n, l, ink.outputs["Color"], bsdf)
    clear = n.new("ShaderNodeBsdfTransparent")
    mix = n.new("ShaderNodeMixShader")
    if cutout:
        # paper printed with ink, as the press does it: paper x (1 - a + a x ink)
        col = n.new("ShaderNodeMix")
        col.data_type = "RGBA"
        col.inputs["A"].default_value = paper
        col.inputs["B"].default_value = [p * s for p, s in zip(paper, sepia)]
        l.new(ink.outputs["Color"], col.inputs["Factor"])
        l.new(col.outputs["Result"], bsdf.inputs["Base Color"])
        mask = n.new("ShaderNodeTexImage")
        mask.image = image(mask_path, True)
        l.new(uv, mask.inputs["Vector"])
        l.new(mask.outputs["Color"], mix.inputs["Fac"])
    else:
        # ink only, printed on the sheet
        bsdf.inputs["Base Color"].default_value = [p * s for p, s in zip(paper, sepia)]
        l.new(ink.outputs["Color"], mix.inputs["Fac"])
    l.new(clear.outputs["BSDF"], mix.inputs[1])
    l.new(bsdf.outputs["BSDF"], mix.inputs[2])
    l.new(mix.outputs["Shader"], out.inputs["Surface"])
    return m


def build(figure, box, mirror=False, tag=None):
    """Place `figure`'s puppet over the sheet-pixel `box`. Returns {layer name: object}."""
    d = ROOT / "assets/puppets" / figure
    spec = json.loads((d / "puppet.json").read_text())
    W, H = spec["size"]
    x0, y0, x1, y1 = box
    s = (x1 - x0) / W  # piece px -> sheet px
    tag = tag or figure + ("_mirror" if mirror else "")

    def to_sheet(px, py):
        if mirror:
            px = W - px
        return x0 + px * s, y0 + py * s

    obs = {}
    # one base height for the whole figure (the curl at its box's centre): layers then stack by lift alone
    order = sorted(spec["layers"], key=lambda ln: spec["layers"][ln]["z"])
    for i, ln in enumerate(order):
        e = spec["layers"][ln]
        lift = LIFT.get(ln, PART_LIFT + PART_STEP * i)
        # a card subdivided enough to bend; the curl itself is added in world space by the sheet_curl modifier
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=32, y_subdivisions=32, size=1.0)
        ob = bpy.context.object
        ob.name = f"{tag}.{ln}"
        a, b = px_to_world(*to_sheet(0, H)), px_to_world(*to_sheet(W, 0))
        lo, hi = Vector((min(a.x, b.x), min(a.y, b.y), 0)), Vector((max(a.x, b.x), max(a.y, b.y), 0))
        piv = px_to_world(*to_sheet(*(e["pivot"] or (W / 2, H / 2))))
        z = lift
        for v in ob.data.vertices:
            u, t = v.co.x + 0.5, v.co.y + 0.5
            v.co.x, v.co.y, v.co.z = lo.x + u * (hi.x - lo.x) - piv.x, lo.y + t * (hi.y - lo.y) - piv.y, 0.0
        if mirror:
            for loop in ob.data.uv_layers.active.data:
                loop.uv.x = 1.0 - loop.uv.x
        ob.location = (piv.x, piv.y, z)
        ob.modifiers.new("curl", "NODES").node_group = curl_group()
        ob.visible_shadow = e["cutout"]  # cutouts cast a thin paper shadow; printed ink casts none
        ob.data.materials.append(layer_material(f"{tag}.{ln}", d / f"layers/{ln}_ink.png", d / f"layers/{ln}_mask.png",
                                                (W, H), e["cutout"]))
        obs[ln] = ob
    bpy.context.view_layer.update()  # new objects' matrix_world is stale until the depsgraph updates
    for ln, ob in obs.items():
        parent = spec["layers"][ln]["parent"]
        if parent:
            ob.parent = obs[parent]
            ob.matrix_parent_inverse = obs[parent].matrix_world.inverted()
    for ob in obs.values():
        ob["mirror"] = mirror
    return obs


def key_twos(ob, path, index, fn, f0, f1, sign=1.0):
    """Key ob.path[index] = base + fn(frame) every `animation_on` frames from f0 to f1, held (constant) between."""
    bpy.context.preferences.edit.keyframe_new_interpolation_type = "CONSTANT"
    step = LOOK["animation_on"]
    base = getattr(ob, path)[index]
    for f in range(f0, f1 + 1, step):
        getattr(ob, path)[index] = base + sign * fn(f)
        ob.keyframe_insert(path, index=index, frame=f)
    getattr(ob, path)[index] = base


def hinge(ob, degrees_fn, f0, f1):
    """Rotate a layer about its pivot (local Z). Mirrored puppets turn the other way."""
    sign = -1.0 if ob.get("mirror") else 1.0
    key_twos(ob, "rotation_euler", 2, lambda f: math.radians(degrees_fn(f)), f0, f1, sign)


def print_piece(name, box, lift=0.00015):
    """A figure that never moves (the laborer): its ink piece printed on the sheet, boiling like the rest."""
    ink = ROOT / "assets/engravings/ink" / f"{name}.png"
    im = image(ink, True)
    from sheet import patch
    ob = patch(f"{name}.print", *box, lift=lift)
    ob.data.materials.append(layer_material(f"{name}.print", ink, ink, tuple(im.size), False))
    return ob
