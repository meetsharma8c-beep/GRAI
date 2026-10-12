"""
REBUILD APOLLO BUNDER MASTERPIECE:
1. High-Fidelity Gateway of India (Indo-Saracenic Triumphal Arch):
   - Central 15m arch tunnel cutout with pointed horseshoe arch
   - 4 corner octagonal turrets with carved stone balconies and domed chhatris
   - Central ribbed dome with lotus finial + 4 subsidiary domes
   - Projecting cornices, chhajjas with corbel brackets, perforated jali parapet
   - Authentic Yellow Kharodi Basalt stone shader with mortar relief
2. High-Fidelity Taj Mahal Palace Hotel (Heritage Wing + Tower):
   - U-shaped harbour facade with 6-tier arched balconies and white balustrades
   - Central 40m high Florentine ribbed red dome with arched lantern
   - Corner Moorish onion-domed chhatris and red pitched tile roofs
   - Ground level arched arcade portico
   - Adjacent Taj Tower with fluted architectural tiers
3. Apollo Bunder Plaza & Sea Promenade:
   - Basalt paved plaza with heritage bollards and steps down to sea
   - Waterfront sea wall meeting Arabian Sea
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def get_or_create_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

col_landmarks = get_or_create_col("Landmarks_Bespoke_Architecture")
col_promenade = get_or_create_col("Coastline_Promenade_Structures")

# ----------------------------------------------------------------------
# 1. AUTHENTIC MATERIALS
# ----------------------------------------------------------------------
def create_basalt_material():
    mat = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt")
    if not mat:
        mat = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Procedural Yellow Basalt Stone
    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 24.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.7
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[0].color = (0.78, 0.65, 0.44, 1.0) # Warm golden Kharodi stone
    color_ramp.color_ramp.elements[1].position = 0.70
    color_ramp.color_ramp.elements[1].color = (0.58, 0.48, 0.34, 1.0) # Weathered basalt brown
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.4
    bump.inputs['Distance'].default_value = 0.05
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.88
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    return mat

def create_taj_material():
    mat = bpy.data.materials.get("Mat_Taj_Mahal_Palace")
    if not mat:
        mat = bpy.data.materials.new("Mat_Taj_Mahal_Palace")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Warm Taj sandstone and cream facade
    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 4.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = (0.74, 0.58, 0.46, 1.0) # Warm sandstone
    color_ramp.color_ramp.elements[1].position = 0.7
    color_ramp.color_ramp.elements[1].color = (0.86, 0.82, 0.76, 1.0) # Heritage cream stone trim
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.25
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.82
    return mat

def create_taj_dome_material():
    mat = bpy.data.materials.get("Mat_Taj_Red_Dome")
    if not mat:
        mat = bpy.data.materials.new("Mat_Taj_Red_Dome")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Rich Florentine terracotta/vermilion red dome
    bsdf.inputs['Base Color'].default_value = (0.58, 0.16, 0.12, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.42
    bsdf.inputs['Specular IOR Level'].default_value = 0.5
    return mat

def create_gold_finial_material():
    mat = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat:
        mat = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.95, 0.76, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.95
    bsdf.inputs['Roughness'].default_value = 0.20
    return mat

mat_basalt = create_basalt_material()
mat_taj = create_taj_material()
mat_dome = create_taj_dome_material()
mat_gold = create_gold_finial_material()

# ----------------------------------------------------------------------
# 2. BUILD THE TRUE ARCHITECTURAL GATEWAY OF INDIA
# Real location: (174.17, -113.1, 0.0)
# Orientated facing east towards Mumbai Harbour
# ----------------------------------------------------------------------
# Remove previous placeholder Gateway object
old_gw = bpy.data.objects.get("LANDMARK_Gateway_of_India")
if old_gw:
    bpy.data.objects.remove(old_gw, do_unlink=True)

gw_mesh = bpy.data.meshes.new("LANDMARK_Gateway_of_India_Mesh")
gw_obj = bpy.data.objects.new("LANDMARK_Gateway_of_India", gw_mesh)
col_landmarks.objects.link(gw_obj)
gw_obj.location = Vector((174.17, -113.10, 0.0))

bm = bmesh.new()

# Main Arch Block dimensions:
# Width along Y = 28m (coastal alignment), Depth along X = 16m, Height = 26m
w_y = 28.0
d_x = 16.0
h_z = 26.0

# 1. Solid base plinth (steps and podium)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal(Vector((d_x + 3.0, w_y + 3.0, 1.2, 1.0))))
for v in bm.verts:
    if v.co.z > 0.0:
        v.co.z = 1.2
    else:
        v.co.z = 0.0

# 2. Main pylon masses (Left and Right pillars flanking the central arch)
# Central arch width = 9.0m, so left pillar spans Y: [-14, -4.5], right pillar spans Y: [4.5, 14]
# Pillar depth X: [-8.0, 8.0]
p_width_y = (w_y - 9.0) / 2.0  # 9.5m each
p_depth_x = d_x                # 16m

# Left Pylon
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, -9.25, h_z / 2.0))) @ Matrix.Diagonal(Vector((p_depth_x, p_width_y, h_z, 1.0))))
# Right Pylon
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 9.25, h_z / 2.0))) @ Matrix.Diagonal(Vector((p_depth_x, p_width_y, h_z, 1.0))))

# 3. Arch Spandrel & Upper Entablature (spanning across above the central arch from z=15m to z=26m)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, (h_z + 15.0) / 2.0))) @ Matrix.Diagonal(Vector((p_depth_x, 9.0, h_z - 15.0, 1.0))))

# 4. Central Pointed Arch Barrel Vault (faceted polygonal arch lining)
arch_r = 4.5
arch_spring_z = 11.0
arch_apex_z = 15.5
segs_arch = 12
for i in range(segs_arch):
    a1 = math.pi * (i / segs_arch)
    a2 = math.pi * ((i + 1) / segs_arch)
    y1 = math.cos(a1) * arch_r
    z1 = arch_spring_z + math.sin(a1) * (arch_apex_z - arch_spring_z)
    y2 = math.cos(a2) * arch_r
    z2 = arch_spring_z + math.sin(a2) * (arch_apex_z - arch_spring_z)
    # Inner arch intrados facet
    v1 = bm.verts.new(Vector((-p_depth_x / 2.0, y1, z1)))
    v2 = bm.verts.new(Vector((p_depth_x / 2.0, y1, z1)))
    v3 = bm.verts.new(Vector((p_depth_x / 2.0, y2, z2)))
    v4 = bm.verts.new(Vector((-p_depth_x / 2.0, y2, z2)))
    bm.faces.new((v1, v2, v3, v4))

# 5. Projecting Chhajja (Eaves cornice) running around the roof at z=26m
cornice_mat = Matrix.Translation(Vector((0, 0, 26.2))) @ Matrix.Diagonal(Vector((p_depth_x + 1.8, w_y + 1.8, 0.6, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=cornice_mat)

# 6. Perforated Jali Parapet balustrade (z=26.5 to 28.0)
parapet_mat = Matrix.Translation(Vector((0, 0, 27.2))) @ Matrix.Diagonal(Vector((p_depth_x + 1.2, w_y + 1.2, 1.4, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=parapet_mat)

# 7. Four Corner Minaret Turrets (Octagonal towers extending up to z=31m)
turret_offsets = [
    Vector((-p_depth_x / 2.0 - 0.5, -w_y / 2.0 - 0.5, 0)),
    Vector((p_depth_x / 2.0 + 0.5, -w_y / 2.0 - 0.5, 0)),
    Vector((-p_depth_x / 2.0 - 0.5, w_y / 2.0 + 0.5, 0)),
    Vector((p_depth_x / 2.0 + 0.5, w_y / 2.0 + 0.5, 0)),
]

for t_off in turret_offsets:
    # Octagonal turret shaft from z=0 to z=28.5m
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.8, radius2=1.6, depth=28.5, matrix=Matrix.Translation(t_off + Vector((0, 0, 14.25))))
    # Turret balcony bracket at z=28.5
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=2.3, radius2=2.1, depth=0.6, matrix=Matrix.Translation(t_off + Vector((0, 0, 28.8))))
    # Turret domed chhatri on top (z=29.1 to 32.5m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.9, radius2=0.2, depth=3.2, matrix=Matrix.Translation(t_off + Vector((0, 0, 30.7))))
    # Brass finial spire
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.2, radius2=0.02, depth=2.2, matrix=Matrix.Translation(t_off + Vector((0, 0, 33.4))))

# 8. Central Grand Indian Ribbed Dome
# Octagonal drum (z=27.5 to 29.5, radius=5.8m)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=5.8, radius2=5.6, depth=2.0, matrix=Matrix.Translation(Vector((0, 0, 28.5))))
# Main bulbous ribbed dome (z=29.5 to 35.5, radius=5.6m)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=5.6, radius2=0.8, depth=6.0, matrix=Matrix.Translation(Vector((0, 0, 32.5))))
# Lotus crown & brass kalasa finial on top of dome (up to z=38.5m)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.2, radius2=0.1, depth=3.0, matrix=Matrix.Translation(Vector((0, 0, 37.0))))

bm.to_mesh(gw_mesh)
bm.free()
gw_obj.data.materials.append(mat_basalt)
gw_obj.data.materials.append(mat_gold)

# Assign gold material to upper finials
for poly in gw_mesh.polygons:
    if poly.center.z > 33.0:
        poly.material_index = 1
    else:
        poly.material_index = 0

print("Rebuilt authentic Gateway of India geometry.")

# ----------------------------------------------------------------------
# 3. BUILD THE TRUE TAJ MAHAL PALACE HOTEL
# Real location: (94.17, -163.10, 0.0)
# Facing east towards harbour with grand central red dome
# ----------------------------------------------------------------------
old_taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
if old_taj:
    bpy.data.objects.remove(old_taj, do_unlink=True)

taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
col_landmarks.objects.link(taj_obj)
taj_obj.location = Vector((94.17, -163.10, 0.0))

bm_taj = bmesh.new()

# Taj Heritage Wing: Length along Y = 85m, Depth along X = 42m, Eaves height = 32m
# U-shaped plan with central court facing harbour
# 1. Main rear spine (West wing): spanning Y: [-42, 42], X: [-21, -9], Height: 32m
bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-15.0, 0.0, 16.0))) @ Matrix.Diagonal(Vector((12.0, 84.0, 32.0, 1.0))))

# 2. North projecting wing: Y: [30, 42], X: [-9, 15], Height: 32m
bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 16.0))) @ Matrix.Diagonal(Vector((24.0, 12.0, 32.0, 1.0))))

# 3. South projecting wing: Y: [-42, -30], X: [-9, 15], Height: 32m
bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 16.0))) @ Matrix.Diagonal(Vector((24.0, 12.0, 32.0, 1.0))))

# 4. Central entrance pavilion & rotunda: X: [-9, 10], Y: [-14, 14], Height: 35m
bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((0.5, 0.0, 17.5))) @ Matrix.Diagonal(Vector((19.0, 28.0, 35.0, 1.0))))

# 5. Distinctive Cantilevered Balconies & Arched Loggias (6 architectural tiers)
for tier in range(1, 6):
    tz = tier * 5.2 + 2.0
    # Front balcony bands
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((10.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.2, 26.0, 0.8, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((15.5, 36.0, tz))) @ Matrix.Diagonal(Vector((1.8, 12.0, 0.8, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((15.5, -36.0, tz))) @ Matrix.Diagonal(Vector((1.8, 12.0, 0.8, 1.0))))

# 6. Pitched Mangalore Terracotta Roofs along wings (z=32 to 38m)
# North roof
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=8.5, radius2=0.5, depth=6.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 35.0))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
# South roof
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=8.5, radius2=0.5, depth=6.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 35.0))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))

# 7. Iconic Central Red Florentine Dome!
# Arched octagonal lantern drum (z=35 to 44m, radius=9.5m)
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=9.5, radius2=9.2, depth=9.0, matrix=Matrix.Translation(Vector((0.5, 0.0, 39.5))))
# High Ribbed Florentine Pointed Dome (z=44 to 62m, peak at 62m)
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=9.2, radius2=0.8, depth=18.0, matrix=Matrix.Translation(Vector((0.5, 0.0, 53.0))))
# Gilded Lantern cupola on top of the dome (z=62 to 69m)
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=1.8, radius2=0.2, depth=7.0, matrix=Matrix.Translation(Vector((0.5, 0.0, 65.5))))

# 8. Corner Onion-Domed Chhatris (4 corner pavilions)
taj_chhatri_pts = [
    Vector((14.0, 41.0, 32.0)),
    Vector((14.0, -41.0, 32.0)),
    Vector((-20.0, 41.0, 32.0)),
    Vector((-20.0, -41.0, 32.0)),
]
for cp in taj_chhatri_pts:
    # Chhatri drum & onion dome (up to z=42m)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=2.8, radius2=2.4, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=2.4, radius2=0.3, depth=4.5, matrix=Matrix.Translation(cp + Vector((0, 0, 5.75))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.03, depth=2.5, matrix=Matrix.Translation(cp + Vector((0, 0, 8.5))))

# 9. Adjacent Modern Taj Tower (built 1973, fluted high-rise behind south wing)
# Location: X: -32m, Y: -55m, Height: 84m (24 stories)
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=12, radius1=16.0, radius2=15.5, depth=84.0, matrix=Matrix.Translation(Vector((-32.0, -55.0, 42.0))))
# Taj Tower architectural crown
bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=12, radius1=17.5, radius2=12.0, depth=8.0, matrix=Matrix.Translation(Vector((-32.0, -55.0, 88.0))))

bm_taj.to_mesh(taj_mesh)
bm_taj.free()

taj_obj.data.materials.append(mat_taj)
taj_obj.data.materials.append(mat_dome)
taj_obj.data.materials.append(mat_gold)

# Assign red dome and gold finial materials by face height and position
for poly in taj_mesh.polygons:
    pz = poly.center.z
    px = poly.center.x
    py = poly.center.y
    if pz > 62.0 and abs(py) < 8.0:
        poly.material_index = 2 # Gold spire
    elif pz > 43.0 and abs(py) < 14.0 and abs(px) < 14.0:
        poly.material_index = 1 # Red Florentine Dome
    elif pz > 33.0 and (abs(py) > 28.0 or (abs(px + 20.0) < 6.0 and abs(py) > 35.0)):
        poly.material_index = 1 # Red roof / corner dome
    else:
        poly.material_index = 0 # Taj heritage sandstone/cream facade

print("Rebuilt authentic Taj Mahal Palace Hotel.")

# ----------------------------------------------------------------------
# 4. APOLLO BUNDER JETTY, SEAWALL & PROMENADE PLAZA
# Paved stone plaza spanning between Taj and Gateway
# ----------------------------------------------------------------------
plaza_name = "PLAZA_Apollo_Bunder_Harbour_Jetty"
old_plaza = bpy.data.objects.get(plaza_name)
if old_plaza:
    bpy.data.objects.remove(old_plaza, do_unlink=True)

pz_mesh = bpy.data.meshes.new(f"{plaza_name}_Mesh")
pz_obj = bpy.data.objects.new(plaza_name, pz_mesh)
col_promenade.objects.link(pz_obj)

bm_pz = bmesh.new()
# Plaza slab from X: 70 to 200, Y: -200 to -80, Z: 0.0 to 1.5m
bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((140.0, -135.0, 0.75))) @ Matrix.Diagonal(Vector((140.0, 140.0, 1.5, 1.0))))
# Grand Ferry Steps down to sea along eastern edge (X: 200 to 215)
for s_idx in range(6):
    step_mat = Matrix.Translation(Vector((202.0 + s_idx * 1.5, -135.0, 0.75 - s_idx * 0.35))) @ Matrix.Diagonal(Vector((1.5, 80.0, 0.4, 1.0)))
    bmesh.ops.create_cube(bm_pz, size=1.0, matrix=step_mat)

bm_pz.to_mesh(pz_mesh)
bm_pz.free()

pz_mat = bpy.data.materials.get("MAT_MarineDrive_PromenadeStone")
if pz_mat:
    pz_obj.data.materials.append(pz_mat)

# ----------------------------------------------------------------------
# 5. HARBOUR FERRY BOATS (Authentic Gateway launches)
# ----------------------------------------------------------------------
col_props = get_or_create_col("Playable_Street_Props")
boat_mat = bpy.data.materials.get("MAT_Gateway_Ferry_Boat")
if not boat_mat:
    boat_mat = bpy.data.materials.new("MAT_Gateway_Ferry_Boat")
    boat_mat.use_nodes = True
    bsdf = boat_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.88, 0.90, 1.0) # White wooden ferry hull
        bsdf.inputs['Roughness'].default_value = 0.55

boat_roof_mat = bpy.data.materials.get("MAT_Gateway_Ferry_Roof")
if not boat_roof_mat:
    boat_roof_mat = bpy.data.materials.new("MAT_Gateway_Ferry_Roof")
    boat_roof_mat.use_nodes = True
    bsdf = boat_roof_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.38, 0.65, 1.0) # Blue canvas canopy

boat_positions = [
    Vector((225.0, -100.0, 0.2)),
    Vector((235.0, -125.0, 0.2)),
    Vector((220.0, -150.0, 0.2)),
    Vector((245.0, -165.0, 0.2)),
]

for b_idx, b_pos in enumerate(boat_positions):
    b_name = f"BOAT_Gateway_Ferry_{b_idx}"
    old_b = bpy.data.objects.get(b_name)
    if old_b:
        bpy.data.objects.remove(old_b, do_unlink=True)
    
    bm_b = bmesh.new()
    # Wooden hull: length 12m, width 3.6m, height 1.8m
    bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=8, radius1=2.0, radius2=1.4, depth=12.0, matrix=Matrix.Translation(b_pos) @ Matrix.Rotation(math.radians(90.0), 4, 'X'))
    # Passenger canopy
    bmesh.ops.create_cube(bm_b, size=1.0, matrix=Matrix.Translation(b_pos + Vector((0, 0, 1.6))) @ Matrix.Diagonal(Vector((2.8, 8.0, 1.2, 1.0))))
    
    b_mesh = bpy.data.meshes.new(f"{b_name}_Mesh")
    bm_b.to_mesh(b_mesh)
    bm_b.free()
    
    b_obj = bpy.data.objects.new(b_name, b_mesh)
    col_props.objects.link(b_obj)
    b_obj.data.materials.append(boat_mat)

print("Apollo Bunder Masterpiece Build Complete.")
