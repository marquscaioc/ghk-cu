"""
GHK-Cu Glow — Blender 5.1 Studio Script  (v3 — smooth base.obj)
Run: blender --background --python blender_studio.py
"""
import bpy
import bmesh
import math
import os
import mathutils

BASE_DIR   = r"C:\Users\Caio\Desktop\GHK CU GLOW\3d"
VIAL_OBJ   = r"C:\Users\Caio\Downloads\base.obj"
LABEL_TEX  = os.path.join(BASE_DIR, "label_texture.png")
RENDER_OUT = os.path.join(BASE_DIR, "render_product.png")
OBJ_OUT    = os.path.join(BASE_DIR, "vial_clean.obj")
BLEND_OUT  = os.path.join(BASE_DIR, "vial_studio.blend")

# ── 1. Reset ─────────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Render settings ────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine            = 'CYCLES'
scene.cycles.samples           = 256
scene.cycles.use_denoising     = True
scene.cycles.denoiser          = 'OPENIMAGEDENOISE'

try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dt in ('OPTIX', 'CUDA', 'METAL'):
        try:
            prefs.compute_device_type = dt
            prefs.get_devices()
            if any(d.type != 'CPU' for d in prefs.devices):
                for d in prefs.devices: d.use = True
                scene.cycles.device = 'GPU'
                print(f"GPU: {dt}"); break
        except Exception: continue
except Exception as e:
    print(f"CPU mode: {e}")

scene.render.resolution_x                      = 800
scene.render.resolution_y                      = 1000
scene.render.film_transparent                  = True
scene.render.filepath                          = RENDER_OUT
scene.render.image_settings.file_format        = 'PNG'
scene.render.image_settings.color_mode         = 'RGBA'
scene.render.image_settings.compression        = 10

try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look           = 'AgX - High Contrast'
except Exception:
    try:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look           = 'High Contrast'
    except Exception: pass
scene.view_settings.exposure = -0.3
scene.view_settings.gamma    = 1.0

# ── 3. Import base.obj (Blender 4.3.2 export — Y-up) ─────────────────────────
bpy.ops.wm.obj_import(filepath=VIAL_OBJ, forward_axis='NEGATIVE_Z', up_axis='Y')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
print("Imported:", [o.name for o in meshes])

# ── 4. Center at world origin (per-vertex world-space) ────────────────────────
all_verts_w = []
for o in meshes:
    for v in o.data.vertices:
        all_verts_w.append(o.matrix_world @ mathutils.Vector(v.co))

cx = sum(v.x for v in all_verts_w) / len(all_verts_w)
cy = sum(v.y for v in all_verts_w) / len(all_verts_w)
cz = (min(v.z for v in all_verts_w) + max(v.z for v in all_verts_w)) / 2.0

vial_z_min_raw = min(v.z for v in all_verts_w)
vial_z_max_raw = max(v.z for v in all_verts_w)
vial_height    = vial_z_max_raw - vial_z_min_raw

for o in meshes:
    o.location.x -= cx
    o.location.y -= cy
    o.location.z -= cz

vial_z_min = vial_z_min_raw - cz   # ≈ -height/2
vial_z_max = vial_z_max_raw - cz   # ≈ +height/2
print(f"Centered. Height: {vial_height:.4f}  Z: {vial_z_min:.4f} → {vial_z_max:.4f}")

# ── 5. Materials ──────────────────────────────────────────────────────────────
def make_glass():
    m = bpy.data.materials.new("VialGlass")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out  = nt.nodes.new('ShaderNodeOutputMaterial'); out.location  = (400, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.055, 0.087, 0.127, 1)
    bsdf.inputs['Metallic'].default_value   = 0.0
    bsdf.inputs['Roughness'].default_value  = 0.04
    bsdf.inputs['IOR'].default_value        = 1.47
    try:
        bsdf.inputs['Coat Weight'].default_value    = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.0
    except KeyError: pass
    return m

def make_cap():
    m = bpy.data.materials.new("VialCap")
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.96, 0.95, 0.94, 1)
    b.inputs['Roughness'].default_value  = 0.55
    b.inputs['Metallic'].default_value   = 0.0
    return m

mat_glass = make_glass()
mat_cap   = make_cap()

# ── 6. Assign cap / glass by face Z-position ──────────────────────────────────
# Cap = top 22 % of vial height (faces above 78th percentile)
cap_z_threshold = vial_z_min + vial_height * 0.78

vial_obj = meshes[0]
bpy.context.view_layer.objects.active = vial_obj
vial_obj.select_set(True)

vial_obj.data.materials.clear()
vial_obj.data.materials.append(mat_glass)   # slot 0
vial_obj.data.materials.append(mat_cap)     # slot 1

bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(vial_obj.data)
bm.faces.ensure_lookup_table()

for face in bm.faces:
    wc = vial_obj.matrix_world @ face.calc_center_median()
    face.material_index = 1 if wc.z > cap_z_threshold else 0

bmesh.update_edit_mesh(vial_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print(f"Cap/glass split at Z={cap_z_threshold:.4f}")

# ── 7. Body radius (lower 70 % of height, tight fit for label) ────────────────
body_z_limit = vial_z_min + vial_height * 0.70
body_r_raw   = 0.0
for v in vial_obj.data.vertices:
    wv = vial_obj.matrix_world @ mathutils.Vector(v.co)
    if wv.z < body_z_limit:
        body_r_raw = max(body_r_raw, abs(wv.x), abs(wv.y))

# Minimal offset: just enough to avoid z-fighting (0.05 %)
body_r = body_r_raw * 1.0005
print(f"Body radius: raw={body_r_raw:.5f}  label={body_r:.5f}")

# ── 8. Label cylinder ─────────────────────────────────────────────────────────
VIAL_H_MM    = 36.0
VIAL_DIAM_MM = 12.0
LABEL_W_MM   = 45.0
LABEL_H_MM   = 20.0

label_h    = vial_height * (LABEL_H_MM / VIAL_H_MM)
uv_scale_u = (math.pi * VIAL_DIAM_MM) / LABEL_W_MM   # 0.8378

label_bottom = vial_z_min + vial_height * (3.0 / VIAL_H_MM)
label_z      = label_bottom + label_h / 2

print(f"Label: h={label_h:.4f}  z_center={label_z:.4f}  uv_u={uv_scale_u:.4f}")

bpy.ops.mesh.primitive_cylinder_add(
    vertices=256,
    radius=body_r,
    depth=label_h,
    end_fill_type='NOTHING',
    location=(0, 0, label_z),
)
lbl_obj      = bpy.context.active_object
lbl_obj.name = "VialLabelWrap"

if not lbl_obj.data.uv_layers:
    lbl_obj.data.uv_layers.new(name="UVMap")

# Label material with real gráfica texture
mat_lbl = bpy.data.materials.new("VialLabelMat")
mat_lbl.use_nodes = True
nt_l = mat_lbl.node_tree
nl, ll = nt_l.nodes, nt_l.links
for n in list(nl): nl.remove(n)

out_l  = nl.new('ShaderNodeOutputMaterial'); out_l.location  = (700, 0)
bsdf_l = nl.new('ShaderNodeBsdfPrincipled'); bsdf_l.location = (400, 0)
tex_l  = nl.new('ShaderNodeTexImage');       tex_l.location  = (  0, 100)
map_n  = nl.new('ShaderNodeMapping');        map_n.location  = (-300, 100)
uvm_n  = nl.new('ShaderNodeUVMap');          uvm_n.location  = (-550, 100)
uvm_n.uv_map = "UVMap"

map_n.inputs['Location'].default_value = (-0.10, 0.0, 0.0)
map_n.inputs['Scale'].default_value    = (uv_scale_u, 1.0, 1.0)

lbl_img = bpy.data.images.load(LABEL_TEX)
lbl_img.colorspace_settings.name = 'sRGB'
tex_l.image     = lbl_img
tex_l.extension = 'REPEAT'

ll.new(uvm_n.outputs['UV'],     map_n.inputs['Vector'])
ll.new(map_n.outputs['Vector'], tex_l.inputs['Vector'])
ll.new(tex_l.outputs['Color'],  bsdf_l.inputs['Base Color'])
bsdf_l.inputs['Roughness'].default_value = 0.35
bsdf_l.inputs['Metallic'].default_value  = 0.0
try:
    bsdf_l.inputs['Specular IOR Level'].default_value = 0.15
except KeyError: pass
ll.new(bsdf_l.outputs['BSDF'], out_l.inputs['Surface'])

lbl_obj.data.materials.append(mat_lbl)

# ── 9. World ──────────────────────────────────────────────────────────────────
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value    = (0.028, 0.031, 0.053, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.18

# ── 10. Camera ────────────────────────────────────────────────────────────────
cam_d = bpy.data.cameras.new("ProductCam"); cam_d.lens = 85
cam_o = bpy.data.objects.new("Camera", cam_d)
bpy.context.collection.objects.link(cam_o)
dist             = max(vial_height * 2.8, 5.5)
cam_o.location       = (0, -dist, 0)
cam_o.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam_o

# ── 11. Studio lights (warm copper — no blue) ─────────────────────────────────
def area_light(name, energy, color, size, loc, rot_deg):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy, d.color, d.size = energy, color, size
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location       = loc
    o.rotation_euler = tuple(math.radians(r) for r in rot_deg)

h = vial_height
area_light("Key",    4500, (1.00, 0.79, 0.47), 1.2, (h*1.2, -h*0.8,  h*1.8), (-35, 0,  35))
area_light("Fill",    550, (0.88, 0.91, 0.93), 5.0, (-h*2,  -h*0.4,  h*0.6), (-10, 0, -15))
area_light("Rim",    1800, (1.00, 0.74, 0.38), 0.8, (  0,    h*1.8,  h*1.0), ( 55, 0,   5))
area_light("Bounce",  200, (0.92, 0.80, 0.60), 4.0, (  0,    0,     -h*1.8), (  0, 0,   0))

# ── 12. Render ────────────────────────────────────────────────────────────────
print("=== Starting render ===")
bpy.ops.render.render(write_still=True)
print(f"=== Render saved: {RENDER_OUT} ===")

# ── 13. Export OBJ for Three.js ───────────────────────────────────────────────
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH': o.select_set(True)

bpy.ops.wm.obj_export(
    filepath=OBJ_OUT,
    export_selected_objects=True,
    export_uv=True,
    export_normals=True,
    export_materials=True,
    path_mode='COPY',
    export_pbr_extensions=False,
)
print(f"=== OBJ exported: {OBJ_OUT} ===")

bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("DONE")
