"""
GHK-Cu Glow — Blender 5.1 Studio Script
Imports clean Vial.obj, applies real label texture, renders product shot,
exports vial_clean.obj for Three.js viewer.
Run: blender --background --python blender_studio.py
"""
import bpy
import math
import os
import mathutils

BASE_DIR = r"C:\Users\Caio\Desktop\GHK CU GLOW\3d"
VIAL_OBJ  = r"C:\Users\Caio\Downloads\vial_extract\source\Vial.obj"
LABEL_TEX = os.path.join(BASE_DIR, "label_texture.png")
RENDER_OUT = os.path.join(BASE_DIR, "render_product.png")
OBJ_OUT    = os.path.join(BASE_DIR, "vial_clean.obj")
BLEND_OUT  = os.path.join(BASE_DIR, "vial_studio.blend")

# ── 1. Reset ────────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Render settings ───────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# GPU setup
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for device_type in ('OPTIX', 'CUDA', 'METAL'):
        try:
            prefs.compute_device_type = device_type
            prefs.get_devices()
            devices = [d for d in prefs.devices if d.type != 'CPU']
            if devices:
                for d in prefs.devices:
                    d.use = True
                scene.cycles.device = 'GPU'
                print(f"GPU: {device_type}")
                break
        except Exception:
            continue
except Exception as e:
    print(f"GPU unavailable, using CPU: {e}")

scene.render.resolution_x = 800
scene.render.resolution_y = 1000
scene.render.film_transparent = True
scene.render.filepath = RENDER_OUT
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 10

# Color management
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
except Exception:
    try:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'High Contrast'
    except Exception:
        pass
scene.view_settings.exposure = -0.3
scene.view_settings.gamma = 1.0

# ── 3. Import Vial OBJ (Maya Y-up) ──────────────────────────────────────────
bpy.ops.wm.obj_import(
    filepath=VIAL_OBJ,
    forward_axis='NEGATIVE_Z',
    up_axis='Y',
)
print("Imported:", [o.name for o in bpy.data.objects if o.type == 'MESH'])

# ── 4. Identify body / cap ────────────────────────────────────────────────────
body_obj = None
cap_obj  = None

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    n = obj.name.lower()
    if 'cap' in n:
        cap_obj = obj
    elif 'body' in n or 'surface' in n or 'vial' in n:
        if body_obj is None:
            body_obj = obj

# Fallback: topmost Z = cap, others = body
if not (body_obj and cap_obj):
    meshes = sorted([o for o in bpy.data.objects if o.type == 'MESH'],
                    key=lambda o: o.matrix_world.translation.z)
    if len(meshes) >= 2:
        cap_obj  = meshes[-1]
        body_obj = meshes[0]
    elif len(meshes) == 1:
        body_obj = meshes[0]

print(f"Body: {body_obj and body_obj.name} | Cap: {cap_obj and cap_obj.name}")

# ── 5. Center vial at world origin ────────────────────────────────────────────
all_meshes = [o for o in bpy.data.objects if o.type == 'MESH']

min_z = float('inf')
max_z = float('-inf')
for o in all_meshes:
    for v in o.bound_box:
        wv = o.matrix_world @ mathutils.Vector(v)
        min_z = min(min_z, wv.z)
        max_z = max(max_z, wv.z)

vial_height = max_z - min_z
center_z = (min_z + max_z) / 2.0

for o in all_meshes:
    o.location.z -= center_z

print(f"Vial height: {vial_height:.3f} units | centered")

# ── 6. Glass material ─────────────────────────────────────────────────────────
mat_glass = bpy.data.materials.new("VialGlass")
mat_glass.use_nodes = True
nt = mat_glass.node_tree
nodes = nt.nodes
links = nt.links

for n in list(nodes):
    nodes.remove(n)

out_n  = nodes.new('ShaderNodeOutputMaterial'); out_n.location  = (400, 0)
bsdf_g = nodes.new('ShaderNodeBsdfPrincipled'); bsdf_g.location = (0, 0)
links.new(bsdf_g.outputs['BSDF'], out_n.inputs['Surface'])

bsdf_g.inputs['Base Color'].default_value         = (0.88, 0.93, 0.97, 1)
bsdf_g.inputs['Metallic'].default_value           = 0.0
bsdf_g.inputs['Roughness'].default_value          = 0.0
bsdf_g.inputs['IOR'].default_value                = 1.47
try:
    bsdf_g.inputs['Transmission Weight'].default_value = 0.96
except KeyError:
    bsdf_g.inputs['Transmission'].default_value = 0.96
# Clear coat makes glass edges catch specular highlights (visible glass effect)
try:
    bsdf_g.inputs['Coat Weight'].default_value    = 0.5
    bsdf_g.inputs['Coat Roughness'].default_value = 0.0
except KeyError:
    pass

# ── 7. Cap material — white rubber stopper ────────────────────────────────────
mat_cap = bpy.data.materials.new("VialCap")
mat_cap.use_nodes = True
cap_bsdf = mat_cap.node_tree.nodes['Principled BSDF']
cap_bsdf.inputs['Base Color'].default_value = (0.96, 0.95, 0.94, 1)
cap_bsdf.inputs['Roughness'].default_value  = 0.55
cap_bsdf.inputs['Metallic'].default_value   = 0.0

# Assign materials by original MTL slot name:
# aiStandardSurface1SG = VialBody (glass)
# aiStandardSurface2SG = VialCap  (rubber stopper)
# aiStandardSurface3SG = other    (glass)
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    for slot in o.material_slots:
        if not slot.material:
            continue
        orig = slot.material.name
        if 'Surface2SG' in orig or orig.endswith('2SG'):
            slot.material = mat_cap
            print(f"  Slot '{orig}' → VialCap (rubber)")
        else:
            slot.material = mat_glass
            print(f"  Slot '{orig}' → VialGlass")

# ── 8. Label cylinder ─────────────────────────────────────────────────────────
if body_obj:
    bpy.ops.object.select_all(action='DESELECT')

    # Get body world bounding box (after centering)
    bb_world = [body_obj.matrix_world @ mathutils.Vector(v) for v in body_obj.bound_box]
    b_min_z  = min(v.z for v in bb_world)
    b_max_z  = max(v.z for v in bb_world)
    b_min_x  = min(v.x for v in bb_world)
    b_max_x  = max(v.x for v in bb_world)
    b_min_y  = min(v.y for v in bb_world)
    b_max_y  = max(v.y for v in bb_world)

    body_h = b_max_z - b_min_z

    # Real-world dimensions: vial 36mm tall × 12mm diameter; label 45mm × 20mm
    VIAL_H_MM    = 36.0
    VIAL_DIAM_MM = 12.0
    LABEL_W_MM   = 45.0
    LABEL_H_MM   = 20.0

    label_h = vial_height * (LABEL_H_MM / VIAL_H_MM)   # 55.6 % of total height

    # UV Scale.X = circumference / label_width = (π×12) / 45 ≈ 0.838
    uv_scale_u = (math.pi * VIAL_DIAM_MM) / LABEL_W_MM

    # Position: leave 3mm gap from body bottom
    label_bottom = b_min_z + vial_height * (3.0 / VIAL_H_MM)
    label_z      = label_bottom + label_h / 2

    # Radius: use only vertices in the BODY region (lower 70 % of Z range)
    # to avoid the cap flange inflating the radius
    body_z_limit = b_min_z + body_h * 0.70
    body_r_raw   = 0.0
    for o in all_meshes:
        for v in o.data.vertices:
            wv = o.matrix_world @ mathutils.Vector(v.co)
            if wv.z < body_z_limit:
                body_r_raw = max(body_r_raw, abs(wv.x), abs(wv.y))
    body_r = body_r_raw * 1.003

    print(f"Label: h={label_h:.3f} r={body_r:.3f} uv_scale_u={uv_scale_u:.3f} z={label_z:.3f}")

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=256,
        radius=body_r,
        depth=label_h,
        end_fill_type='NOTHING',
        location=(0, 0, label_z),
    )
    lbl_obj = bpy.context.active_object
    lbl_obj.name = "VialLabelWrap"

    # Cylinder primitive already has correct UV — U wraps 0→1 around, V 0→1 top→bottom
    # We just need to confirm the UVs are present
    if not lbl_obj.data.uv_layers:
        lbl_obj.data.uv_layers.new(name="UVMap")

    # Label material
    mat_lbl = bpy.data.materials.new("VialLabelMat")
    mat_lbl.use_nodes = True
    nt_l = mat_lbl.node_tree
    nl   = nt_l.nodes
    ll   = nt_l.links
    for n in list(nl): nl.remove(n)

    out_l  = nl.new('ShaderNodeOutputMaterial'); out_l.location  = (700, 0)
    bsdf_l = nl.new('ShaderNodeBsdfPrincipled'); bsdf_l.location = (400, 0)
    tex_l  = nl.new('ShaderNodeTexImage');       tex_l.location  = (  0, 100)
    map_n  = nl.new('ShaderNodeMapping');        map_n.location  = (-300, 100)
    uvm_n  = nl.new('ShaderNodeUVMap');          uvm_n.location  = (-550, 100)
    uvm_n.uv_map = "UVMap"

    # Front face native UV ≈0.5; center content (Purity 98%+) ≈ U=0.40
    # Offset = target - native = 0.40 - 0.50 = -0.10
    # Scale.X = circumference/label_width = 0.838 → fits exactly one circumference of label
    map_n.inputs['Location'].default_value = (-0.10, 0.0, 0.0)
    map_n.inputs['Scale'].default_value    = (uv_scale_u, 1.0, 1.0)

    lbl_img = bpy.data.images.load(LABEL_TEX)
    lbl_img.colorspace_settings.name = 'sRGB'
    tex_l.image = lbl_img
    tex_l.extension = 'REPEAT'

    ll.new(uvm_n.outputs['UV'],    map_n.inputs['Vector'])
    ll.new(map_n.outputs['Vector'], tex_l.inputs['Vector'])
    ll.new(tex_l.outputs['Color'], bsdf_l.inputs['Base Color'])
    bsdf_l.inputs['Roughness'].default_value = 0.35
    bsdf_l.inputs['Metallic'].default_value  = 0.0
    try:
        bsdf_l.inputs['Specular IOR Level'].default_value = 0.15
    except KeyError:
        pass
    ll.new(bsdf_l.outputs['BSDF'], out_l.inputs['Surface'])

    lbl_obj.data.materials.append(mat_lbl)

# ── 9. World (dark brand background) ─────────────────────────────────────────
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value    = (0.028, 0.031, 0.053, 1)
bg_node.inputs['Strength'].default_value = 0.18

# ── 10. Camera ────────────────────────────────────────────────────────────────
cam_d = bpy.data.cameras.new("ProductCam")
cam_d.lens = 85
cam_o = bpy.data.objects.new("Camera", cam_d)
bpy.context.collection.objects.link(cam_o)

dist   = max(vial_height * 2.8, 5.5)
cam_o.location       = (0, -dist, 0)
cam_o.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam_o

# ── 11. Studio lights (no blue fill — warm copper palette) ────────────────────
def area_light(name, energy, color, size, location, rot_deg):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.color  = color
    d.size   = size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location       = location
    o.rotation_euler = tuple(math.radians(r) for r in rot_deg)
    return o

h = vial_height
# Key — warm copper, upper-right front
area_light("Key",    energy=4500, color=(1.00, 0.79, 0.47),
           size=1.2, location=(h*1.2, -h*0.8,  h*1.8), rot_deg=(-35, 0,  35))
# Fill — neutral white (NOT blue), left, large + soft
area_light("Fill",   energy=550,  color=(0.88, 0.91, 0.93),
           size=5.0, location=(-h*2,  -h*0.4,  h*0.6), rot_deg=(-10, 0, -15))
# Rim — copper backlight
area_light("Rim",    energy=1800, color=(1.00, 0.74, 0.38),
           size=0.8, location=( 0,     h*1.8,  h*1.0), rot_deg=( 55, 0,   5))
# Bounce — warm ground
area_light("Bounce", energy=200,  color=(0.92, 0.80, 0.60),
           size=4.0, location=( 0,     0,     -h*1.8), rot_deg=(  0, 0,   0))

# ── 12. Render ────────────────────────────────────────────────────────────────
print("=== Starting render ===")
bpy.ops.render.render(write_still=True)
print(f"=== Saved render: {RENDER_OUT} ===")

# ── 13. Export OBJ for Three.js ───────────────────────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.select_set(True)

bpy.ops.wm.obj_export(
    filepath=OBJ_OUT,
    export_selected_objects=True,
    export_uv=True,
    export_normals=True,
    export_materials=True,
    path_mode='COPY',
    export_pbr_extensions=False,
)
print(f"=== Exported OBJ: {OBJ_OUT} ===")

# ── 14. Save .blend ───────────────────────────────────────────────────────────
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print(f"=== Saved blend: {BLEND_OUT} ===")
print("DONE")
