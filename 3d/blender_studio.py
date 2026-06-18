"""
GHK-Cu Glow — Blender 5.1 Studio Script  (v4 — Maya Vial.obj, 3 materials)
Run: blender --background --python blender_studio.py
"""
import bpy
import math
import os
import mathutils

BASE_DIR   = r"C:\Users\Caio\Desktop\GHK CU GLOW\3d"
VIAL_OBJ   = r"C:\Users\Caio\Downloads\vial_new\source\Vial.obj"
LABEL_TEX  = os.path.join(BASE_DIR, "label_texture.png")
RENDER_OUT = os.path.join(BASE_DIR, "render_product.png")
OBJ_OUT    = os.path.join(BASE_DIR, "vial_clean.obj")
BLEND_OUT  = os.path.join(BASE_DIR, "vial_studio.blend")

# Real-world vial dimensions (cm, matches file units)
VIAL_H_MM    = 30.0   # vial height ≈ 30 mm (file height 3.0006 cm)
VIAL_DIAM_MM = 14.82  # body diameter ≈ 14.82 mm (body radius 0.74076 cm × 2 × 10)
LABEL_W_MM   = 45.0
LABEL_H_MM   = 17.0

# ── 1. Reset ─────────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Render settings ────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine            = 'CYCLES'
scene.cycles.samples           = 512
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

# ── 3. Import Maya Vial.obj (Y-up, cm units) ──────────────────────────────────
bpy.ops.wm.obj_import(filepath=VIAL_OBJ, forward_axis='NEGATIVE_Z', up_axis='Y')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
print("Imported:", [o.name for o in meshes])

# ── 4. Center at world origin ─────────────────────────────────────────────────
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

vial_z_min = vial_z_min_raw - cz
vial_z_max = vial_z_max_raw - cz
print(f"Centered. Height: {vial_height:.4f}  Z: {vial_z_min:.4f} → {vial_z_max:.4f}")

# ── 5. Materials ──────────────────────────────────────────────────────────────
def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out  = nt.nodes.new('ShaderNodeOutputMaterial'); out.location  = (400, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m, bsdf

def make_glass():
    m, b = new_mat("VialGlass")
    b.inputs['Base Color'].default_value = (0.04, 0.20, 0.22, 1)  # teal
    b.inputs['Metallic'].default_value   = 0.0
    b.inputs['Roughness'].default_value  = 0.04
    b.inputs['IOR'].default_value        = 1.50
    try:
        b.inputs['Transmission Weight'].default_value = 0.82
    except KeyError:
        b.inputs['Transmission'].default_value = 0.82
    try:
        b.inputs['Coat Weight'].default_value    = 1.0
        b.inputs['Coat Roughness'].default_value = 0.0
    except KeyError: pass
    m.use_backface_culling = False
    return m

def make_cap():
    m, b = new_mat("VialCap")
    b.inputs['Base Color'].default_value = (0.70, 0.72, 0.74, 1)  # silver aluminum
    b.inputs['Roughness'].default_value  = 0.20
    b.inputs['Metallic'].default_value   = 0.94
    return m

def make_rubber():
    m, b = new_mat("VialRubber")
    b.inputs['Base Color'].default_value = (0.88, 0.88, 0.86, 1)  # off-white rubber stopper
    b.inputs['Roughness'].default_value  = 0.65
    b.inputs['Metallic'].default_value   = 0.0
    return m

mat_glass  = make_glass()
mat_cap    = make_cap()
mat_rubber = make_rubber()

# ── 6. Assign materials by Arnold slot name (no bmesh splitting needed) ────────
# Maya Vial.obj material slots: aiStandardSurface3SG=glass, 1SG=cap, 2SG=rubber stopper
vial_obj = meshes[0]
bpy.context.view_layer.objects.active = vial_obj
vial_obj.select_set(True)

for i in range(len(vial_obj.data.materials)):
    orig = vial_obj.data.materials[i]
    if not orig: continue
    name = orig.name.lower()
    if '3sg' in name:
        vial_obj.data.materials[i] = mat_glass
        print(f"Slot {i}: {orig.name} → VialGlass")
    elif '1sg' in name:
        vial_obj.data.materials[i] = mat_cap
        print(f"Slot {i}: {orig.name} → VialCap")
    elif '2sg' in name:
        vial_obj.data.materials[i] = mat_rubber
        print(f"Slot {i}: {orig.name} → VialRubber")

# ── 7. Body radius — cylindrical zone (10 %–55 %) ────────────────────────────
body_z_lower = vial_z_min + vial_height * 0.10
body_z_upper = vial_z_min + vial_height * 0.55
body_r_raw   = 0.0
for v in vial_obj.data.vertices:
    wv = vial_obj.matrix_world @ mathutils.Vector(v.co)
    if body_z_lower < wv.z < body_z_upper:
        body_r_raw = max(body_r_raw, abs(wv.x), abs(wv.y))

body_r = body_r_raw * 1.0003
print(f"Body radius (10-55 % zone): raw={body_r_raw:.5f}  label={body_r:.5f}")

# ── 8. Label cylinder ─────────────────────────────────────────────────────────
label_h    = vial_height * (LABEL_H_MM / VIAL_H_MM)
uv_scale_u = (math.pi * VIAL_DIAM_MM) / LABEL_W_MM   # π×14.82/45 ≈ 1.034

label_bottom = vial_z_min + vial_height * (4.0 / VIAL_H_MM)
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

# Label material — adesivo metalizado bronze (render Cycles)
mat_lbl = bpy.data.materials.new("VialLabelMat")
mat_lbl.use_nodes = True
nt_l = mat_lbl.node_tree
nl, ll = nt_l.nodes, nt_l.links
for n in list(nl): nl.remove(n)

out_l  = nl.new('ShaderNodeOutputMaterial'); out_l.location  = (800, 0)
mix_n  = nl.new('ShaderNodeMixShader');      mix_n.location  = (550, 0)
bsdf_d = nl.new('ShaderNodeBsdfPrincipled'); bsdf_d.location = (250, 120)  # diffuse label
bsdf_m = nl.new('ShaderNodeBsdfPrincipled'); bsdf_m.location = (250, -120) # metallic bronze
tex_l  = nl.new('ShaderNodeTexImage');       tex_l.location  = (-200, 100)
map_n  = nl.new('ShaderNodeMapping');        map_n.location  = (-480, 100)
uvm_n  = nl.new('ShaderNodeUVMap');          uvm_n.location  = (-720, 100)
uvm_n.uv_map = "UVMap"

map_n.inputs['Location'].default_value = (-0.10, 0.0, 0.0)
map_n.inputs['Scale'].default_value    = (uv_scale_u, 1.0, 1.0)

lbl_img = bpy.data.images.load(LABEL_TEX)
lbl_img.colorspace_settings.name = 'sRGB'
tex_l.image     = lbl_img
tex_l.extension = 'REPEAT'

# Diffuse shader (label texture)
ll.new(uvm_n.outputs['UV'],    map_n.inputs['Vector'])
ll.new(map_n.outputs['Vector'], tex_l.inputs['Vector'])
ll.new(tex_l.outputs['Color'], bsdf_d.inputs['Base Color'])
bsdf_d.inputs['Roughness'].default_value = 0.30

# Metallic bronze shader
bsdf_m.inputs['Base Color'].default_value = (0.72, 0.45, 0.20, 1)  # bronze/copper
bsdf_m.inputs['Metallic'].default_value   = 1.0
bsdf_m.inputs['Roughness'].default_value  = 0.08

# Mix: 40% metallic bronze over diffuse (simulates hot stamp foil on dark label)
mix_n.inputs['Fac'].default_value = 0.40
ll.new(bsdf_d.outputs['BSDF'], mix_n.inputs[1])
ll.new(bsdf_m.outputs['BSDF'], mix_n.inputs[2])
ll.new(mix_n.outputs['Shader'], out_l.inputs['Surface'])

lbl_obj.data.materials.append(mat_lbl)

# ── 9. Blue powder content (render only — excluded from OBJ export) ──────────
powder_r = body_r_raw * 0.78
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=powder_r, segments=64, ring_count=32,
    location=(0, 0, vial_z_min + vial_height * 0.12)
)
pow_obj      = bpy.context.active_object
pow_obj.name = "VialContent"
pow_obj.scale.z = 0.42

mat_pow = bpy.data.materials.new("VialContent")
mat_pow.use_nodes = True
pnt = mat_pow.node_tree
for n in list(pnt.nodes): pnt.nodes.remove(n)
out_p  = pnt.nodes.new('ShaderNodeOutputMaterial'); out_p.location  = (400, 0)
bsdf_p = pnt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf_p.location = (0, 0)
pnt.links.new(bsdf_p.outputs['BSDF'], out_p.inputs['Surface'])
bsdf_p.inputs['Base Color'].default_value = (0.02, 0.12, 0.92, 1)
bsdf_p.inputs['Roughness'].default_value  = 0.90
try:
    bsdf_p.inputs['Emission Color'].default_value    = (0.05, 0.20, 1.00, 1)
    bsdf_p.inputs['Emission Strength'].default_value = 0.8
except KeyError: pass
pow_obj.data.materials.append(mat_pow)
print(f"Powder sphere: r={powder_r:.4f}")

# ── 10. World ─────────────────────────────────────────────────────────────────
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value    = (0.028, 0.031, 0.053, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.18

# ── 11. Camera ────────────────────────────────────────────────────────────────
cam_d = bpy.data.cameras.new("ProductCam"); cam_d.lens = 85
cam_o = bpy.data.objects.new("Camera", cam_d)
bpy.context.collection.objects.link(cam_o)
dist             = max(vial_height * 2.8, 5.5)
cam_o.location       = (0, -dist, 0)
cam_o.rotation_euler = (math.radians(90), 0, 0)
scene.camera = cam_o

# ── 12. Studio lights ─────────────────────────────────────────────────────────
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

# ── 13. Render ────────────────────────────────────────────────────────────────
print("=== Starting render ===")
bpy.ops.render.render(write_still=True)
print(f"=== Render saved: {RENDER_OUT} ===")

# ── 14. Export OBJ (exclude VialContent powder sphere) ───────────────────────
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'VialContent':
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
print(f"=== OBJ exported: {OBJ_OUT} ===")

bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
print("DONE")
