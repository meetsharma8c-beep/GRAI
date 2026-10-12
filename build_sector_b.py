import bpy
import bmesh
import math
import random
import mathutils
from mathutils import Vector, Matrix

# Inject into exec globals so functions can access them
globals()['bmesh'] = bmesh
globals()['mathutils'] = mathutils
globals()['Vector'] = Vector
globals()['Matrix'] = Matrix
globals()['math'] = math
globals()['random'] = random

# Ensure collection exists
if 'Sector_B_MarineDrive_NarimanPoint' in bpy.data.collections:
    col_b = bpy.data.collections['Sector_B_MarineDrive_NarimanPoint']
else:
    col_b = bpy.data.collections.new('Sector_B_MarineDrive_NarimanPoint')
    bpy.context.scene.collection.children.link(col_b)

def get_or_create_mat(mat_name, diff_col, met=0.0, rough=0.5):
    if mat_name in bpy.data.materials:
        m = bpy.data.materials[mat_name]
    else:
        m = bpy.data.materials.new(name=mat_name)
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = diff_col
        bsdf.inputs['Metallic'].default_value = met
        bsdf.inputs['Roughness'].default_value = rough
    return m

def make_box(b_name, b_size, b_loc, b_mat, target_col):
    m = bpy.data.meshes.new(b_name)
    o = bpy.data.objects.new(b_name, m)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= b_size[0]
        v.co.y *= b_size[1]
        v.co.z *= b_size[2]
        v.co.z += b_size[2] / 2.0
    bm.to_mesh(m)
    bm.free()
    o.location = b_loc
    if b_mat:
        o.data.materials.append(b_mat)
    target_col.objects.link(o)
    return o

# -------------------------------------------------------------
# Materials for Sector B
# -------------------------------------------------------------
mat_air_india = get_or_create_mat("MAT_AirIndia_WhiteConcrete", (0.92, 0.93, 0.95, 1.0), 0.1, 0.35)
mat_air_india_red = get_or_create_mat("MAT_AirIndia_RedLogo", (0.85, 0.08, 0.08, 1.0), 0.2, 0.3)
mat_express = get_or_create_mat("MAT_ExpressTowers_Concrete", (0.65, 0.64, 0.62, 1.0), 0.0, 0.7)
mat_trident = get_or_create_mat("MAT_Trident_SandstoneGlass", (0.78, 0.72, 0.65, 1.0), 0.3, 0.3)
mat_ncpa = get_or_create_mat("MAT_NCPA_Granite", (0.55, 0.53, 0.50, 1.0), 0.0, 0.8)
mat_commercial_glass = get_or_create_mat("MAT_Nariman_CurtainGlass", (0.20, 0.35, 0.45, 1.0), 0.8, 0.15)
mat_art_deco = get_or_create_mat("MAT_MarineDrive_ArtDeco", (0.88, 0.82, 0.72, 1.0), 0.0, 0.6)
mat_promenade = get_or_create_mat("MAT_MarineDrive_PromenadeStone", (0.60, 0.60, 0.58, 1.0), 0.0, 0.7)
mat_asphalt = get_or_create_mat("MAT_Road_Asphalt_Indian", (0.15, 0.15, 0.16, 1.0), 0.0, 0.8)
mat_seawall = get_or_create_mat("MAT_MarineDrive_SeawallConcrete", (0.45, 0.47, 0.48, 1.0), 0.0, 0.85)

count = 0

# 1. Air India Building (Nariman Point)
loc_ai = Vector((-1105.7, 531.3, 0.0))
make_box("LANDMARK_AirIndia_Podium", (60, 55, 12), loc_ai, mat_air_india, col_b)
make_box("LANDMARK_AirIndia_Tower", (42, 38, 92), loc_ai + Vector((0, 0, 12)), mat_air_india, col_b)
make_box("LANDMARK_AirIndia_Crown", (20, 15, 6), loc_ai + Vector((0, 0, 104)), mat_air_india_red, col_b)
count += 3

# 2. Express Towers
loc_et = Vector((-1074.1, 642.0, 0.0))
make_box("LANDMARK_ExpressTowers_Podium", (55, 50, 10), loc_et, mat_express, col_b)
make_box("LANDMARK_ExpressTowers_Tower", (38, 38, 108), loc_et + Vector((0, 0, 10)), mat_express, col_b)
make_box("LANDMARK_ExpressTowers_Core", (18, 18, 8), loc_et + Vector((0, 0, 118)), mat_commercial_glass, col_b)
count += 3

# 3. The Trident & The Oberoi
loc_trident = Vector((-1179.4, 387.4, 0.0))
make_box("LANDMARK_Trident_Tower", (48, 34, 125), loc_trident, mat_trident, col_b)
make_box("LANDMARK_TheOberoi_Wing", (55, 50, 60), loc_trident + Vector((35, -45, 0)), mat_trident, col_b)
count += 2

# 4. NCPA
loc_ncpa = Vector((-1390.0, 55.3, 0.0))
make_box("LANDMARK_NCPA_TataTheatre", (70, 65, 24), loc_ncpa, mat_ncpa, col_b)
make_box("LANDMARK_NCPA_Complex", (50, 45, 18), loc_ncpa + Vector((40, 50, 0)), mat_ncpa, col_b)
count += 2

# 5. Nariman Point Skyline Blocks
skyline_defs = [
    ("Maker_Chambers_IV", (-1140, 480, 0), (45, 40, 95)),
    ("Maker_Chambers_V", (-1120, 420, 0), (42, 38, 90)),
    ("Maker_Chambers_VI", (-1080, 460, 0), (44, 40, 85)),
    ("Free_Press_House", (-1040, 540, 0), (40, 36, 100)),
    ("Mittal_Court", (-1010, 600, 0), (50, 42, 80)),
    ("Bajaj_Bhavan", (-1090, 580, 0), (45, 38, 88)),
    ("Nariman_Bhavan", (-1050, 660, 0), (42, 40, 92)),
    ("Mafatlal_Centre", (-1110, 650, 0), (38, 38, 84)),
    ("Earnest_House", (-1060, 720, 0), (40, 35, 78)),
    ("Raheja_Chambers", (-1020, 780, 0), (44, 40, 82)),
    ("State_Bank_Bhavan", (-1180, 520, 0), (52, 45, 105)),
    ("IDBI_Tower_Nariman", (-1150, 580, 0), (46, 40, 98)),
]
for b_name, b_loc, b_size in skyline_defs:
    make_box(f"BLDG_NarimanPoint_{b_name}", b_size, Vector(b_loc), mat_commercial_glass, col_b)
    count += 1

# 6. Sweeping Marine Drive "Queen's Necklace" Promenade & Roadway
promenade_waypoints = [
    Vector((-1390.0, 55.0, 0.0)),
    Vector((-1250.0, 220.0, 0.0)),
    Vector((-1190.0, 390.0, 0.0)),
    Vector((-1130.0, 560.0, 0.0)),
    Vector((-1080.0, 780.0, 0.0)),
    Vector((-1040.0, 1050.0, 0.0)),
    Vector((-1000.0, 1380.0, 0.0)),
    Vector((-970.0, 1750.0, 0.0)),
    Vector((-940.0, 2150.0, 0.0)),
    Vector((-915.0, 2580.0, 0.0)),
    Vector((-900.0, 3050.0, 0.0)),
    Vector((-930.0, 3500.0, 0.0)),
]

dense_pts = []
for i in range(len(promenade_waypoints) - 1):
    p0 = promenade_waypoints[i]
    p1 = promenade_waypoints[i + 1]
    for s in range(8):
        dense_pts.append(p0.lerp(p1, s / 8.0))
dense_pts.append(promenade_waypoints[-1])

prom_width = 14.0
road_width = 24.0
wall_height = 2.4

# Promenade
mesh_prom = bpy.data.meshes.new("PROMENADE_MarineDrive_QueensNecklace")
obj_prom = bpy.data.objects.new("PROMENADE_MarineDrive_QueensNecklace", mesh_prom)
bm_prom = bmesh.new()

# Road
mesh_road = bpy.data.meshes.new("ROAD_MarineDrive_NetajiSubhashRoad")
obj_road = bpy.data.objects.new("ROAD_MarineDrive_NetajiSubhashRoad", mesh_road)
bm_road = bmesh.new()

# Seawall
mesh_wall = bpy.data.meshes.new("SEAWALL_MarineDrive_Barrier")
obj_wall = bpy.data.objects.new("SEAWALL_MarineDrive_Barrier", mesh_wall)
bm_wall = bmesh.new()

prev_p_sea, prev_p_inland = None, None
prev_r_outer, prev_r_inner = None, None
prev_wall = None

for i in range(len(dense_pts)):
    p = dense_pts[i]
    if i < len(dense_pts) - 1:
        tangent = (dense_pts[i + 1] - p).normalized()
    else:
        tangent = (p - dense_pts[i - 1]).normalized()
    normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()

    sea_edge = p
    prom_edge = p + normal * prom_width
    road_edge = p + normal * (prom_width + road_width)

    # Promenade
    vp_sea = bm_prom.verts.new(Vector((sea_edge.x, sea_edge.y, 1.2)))
    vp_in = bm_prom.verts.new(Vector((prom_edge.x, prom_edge.y, 1.2)))
    if prev_p_sea:
        bm_prom.faces.new([prev_p_sea, prev_p_inland, vp_in, vp_sea])
    prev_p_sea = vp_sea
    prev_p_inland = vp_in

    # Road
    vr_out = bm_road.verts.new(Vector((prom_edge.x, prom_edge.y, 1.1)))
    vr_in = bm_road.verts.new(Vector((road_edge.x, road_edge.y, 1.1)))
    if prev_r_outer:
        bm_road.faces.new([prev_r_outer, prev_r_inner, vr_in, vr_out])
    prev_r_outer = vr_out
    prev_r_inner = vr_in

    # Seawall
    vw_bs = bm_wall.verts.new(Vector((sea_edge.x, sea_edge.y, -1.0)))
    vw_ts = bm_wall.verts.new(Vector((sea_edge.x, sea_edge.y, wall_height)))
    vw_tp = bm_wall.verts.new(Vector((sea_edge.x + normal.x * 0.8, sea_edge.y + normal.y * 0.8, wall_height)))
    vw_bp = bm_wall.verts.new(Vector((sea_edge.x + normal.x * 0.8, sea_edge.y + normal.y * 0.8, 1.2)))
    if prev_wall:
        pw_bs, pw_ts, pw_tp, pw_bp = prev_wall
        bm_wall.faces.new([pw_bs, pw_ts, vw_ts, vw_bs])
        bm_wall.faces.new([pw_ts, pw_tp, vw_tp, vw_ts])
        bm_wall.faces.new([pw_tp, pw_bp, vw_bp, vw_tp])
    prev_wall = (vw_bs, vw_ts, vw_tp, vw_bp)

bm_prom.to_mesh(mesh_prom)
bm_prom.free()
obj_prom.data.materials.append(mat_promenade)
col_b.objects.link(obj_prom)

bm_road.to_mesh(mesh_road)
bm_road.free()
obj_road.data.materials.append(mat_asphalt)
col_b.objects.link(obj_road)

bm_wall.to_mesh(mesh_wall)
bm_wall.free()
obj_wall.data.materials.append(mat_seawall)
col_b.objects.link(obj_wall)
count += 3

# 7. Art Deco Buildings along Marine Drive
art_deco_names = [
    "Kapoor_Mahal", "Zaver_Mahal", "Keval_Mahal", "Soona_Mahal",
    "Empress_Court", "Rajab_Mahal", "Shiv_Shanti_Bhuvan", "Fairlawn",
    "Gool_Mahal", "Sea_Green_Hotel", "Chateau_Marine", "Ocean_View"
]
for idx, name in enumerate(art_deco_names):
    pt_idx = min(int(12 + idx * 6), len(dense_pts) - 1)
    p = dense_pts[pt_idx]
    if pt_idx < len(dense_pts) - 1:
        tangent = (dense_pts[pt_idx + 1] - p).normalized()
    else:
        tangent = (p - dense_pts[pt_idx - 1]).normalized()
    normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()
    b_loc = p + normal * (prom_width + road_width + 25.0)
    b_height = 24.0 + (idx % 3) * 4.0
    make_box(f"ARTDECO_MarineDrive_{name}", (35, 28, b_height), Vector((b_loc.x, b_loc.y, 0.0)), mat_art_deco, col_b)
    count += 1

# 8. Tetrapods Breakwaters
mat_tetrapod = get_or_create_mat("MAT_Concrete_Tetrapod", (0.50, 0.52, 0.53, 1.0), 0.0, 0.9)
for i in range(0, len(dense_pts), 5):
    p = dense_pts[i]
    if i < len(dense_pts) - 1:
        tangent = (dense_pts[i + 1] - p).normalized()
    else:
        tangent = (p - dense_pts[i - 1]).normalized()
    normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()
    t_loc = p - normal * 3.5
    t_obj = make_box(f"TETRAPOD_MarineDrive_{i}", (3.0, 3.0, 2.5), Vector((t_loc.x, t_loc.y, 0.0)), mat_tetrapod, col_b)
    t_obj.rotation_euler = (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), random.uniform(0, 3.14))
    count += 1

result = f"Sector B constructed successfully! Added {count} objects."
print(result)
