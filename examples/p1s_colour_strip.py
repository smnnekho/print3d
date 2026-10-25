"""Two-colour inlay for verifying a single-nozzle P1S project (AMS required).

One Blender unit is one mm. White 40 x 16 x 3 mm plate, blue 30 x 4 x 1 mm
strip flush with its top. This checks grouping and filament changes, not fit.
"""
import bpy


def box(name, size, z):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


body = box("body", (40, 16, 3), 1.5)
cutter = box("pocket", (30, 4, 2), 3)
modifier = body.modifiers.new("open pocket", "BOOLEAN")
modifier.operation = "DIFFERENCE"
modifier.solver = "EXACT"
modifier.object = cutter
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier=modifier.name)
bpy.data.objects.remove(cutter, do_unlink=True)
stripe = box("stripe", (30, 4, 1), 2.5)
part(body, "body", color="white", group="plate")
part(stripe, "stripe", color="blue", group="plate")
