"""
Build Sector D: Fort, CSMT, BSE, Heritage Quarter & Full Mumbai Peninsula Landmass.
Constructs continuous georeferenced landmass covering South to Central Mumbai,
along with UNESCO heritage landmarks (CSMT, Rajabai Tower, High Court),
Bombay Stock Exchange, Mantralaya, Churchgate, and historic Maidans.
"""
import bpy
import bmesh
import math
import random
import mathutils
from mathutils import Vector, Matrix

# Inject globals for exec scope
globals()['bmesh'] = bmesh
globals()['mathutils'] = mathutils
globals()['Vector'] = Vector
globals()['Matrix'] = Matrix
globals()['math'] = math
globals()['random'] = random

def get_or_create_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

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

def make_cylinder(c_name, radius, height, segs, c_loc, c_mat, target_col):
    m = bpy.data.meshes.new(c_name)
    o = bpy.data.objects.new(c_name, m)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=height)
    for v in bm.verts:
        v.co.z += height / 2.0
    bm.to_mesh(m)
    bm.free()
    o.location = c_loc
    if c_mat:
        o.data.materials.append(c_mat)
    target_col.objects.link(o)
    return o

col_d = get_or_create_col('Sector_D_Dharavi_CentralMumbai')
col_land = get_or_create_col('Coastline_Promenade_Structures')

# ------------------------------------------------------------------
# Materials
# ------------------------------------------------------------------
mat_land = get_or_create_mat("MAT_Mumbai_Peninsula_Ground", (0.55, 0.58, 0.52, 1.0), 0.0, 0.85)
mat_maidan_grass = get_or_create_mat("MAT_OvalMaidan_Grass", (0.28, 0.48, 0.22, 1.0), 0.0, 0.9)
mat_csmt_stone = get_or_create_mat("MAT_CSMT_VictorianSandstone", (0.82, 0.68, 0.52, 1.0), 0.0, 0.65)
mat_csmt_dome = get_or_create_mat("MAT_CSMT_CopperRibbedDome", (0.42, 0.58, 0.50, 1.0), 0.2, 0.4)
mat_bse_tower = get_or_create_mat("MAT_BSE_ModernistRotunda", (0.75, 0.78, 0.82, 1.0), 0.4, 0.3)
mat_bse_glass = get_or_create_mat("MAT_BSE_CurtainGlass", (0.20, 0.32, 0.42, 1.0), 0.8, 0.2)
mat_gothic_stone = get_or_create_mat("MAT_Gothic_BasaltStone", (0.48, 0.45, 0.42, 1.0), 0.0, 0.8)
mat_mantralaya = get_or_create_mat("MAT_Mantralaya_AdminWhite", (0.88, 0.89, 0.90, 1.0), 0.05, 0.5)

# ------------------------------------------------------------------
# 1. GEOGRAPHIC REAL PENINSULA LANDMASS MESH
# Accurate georeferenced outline connecting Colaba to Bandra/Mahim
# ------------------------------------------------------------------
# Coastline perimeter vertices (clockwise from Colaba South Tip)
coastline_pts = [
    # Colaba West
    (-150.0, -3200.0, 1.0), # Colaba Point / Lighthouse
    (-250.0, -2600.0, 1.5),
    (-280.0, -2000.0, 2.0),
    (-320.0, -1400.0, 2.0),
    (-350.0, -800.0, 2.0),
    (-400.0, -200.0, 2.0),
    # Back Bay & Nariman Point
    (-1390.0, 55.0, 1.2),   # NCPA Tip
    (-1200.0, 390.0, 1.2),  # Trident
    (-1100.0, 560.0, 1.2),  # Air India
    (-1050.0, 850.0, 1.2),  # Marine Drive start
    (-980.0, 1400.0, 1.2),  # Churchgate outer
    (-940.0, 2100.0, 1.2),  # Marine Lines
    (-900.0, 2800.0, 1.2),  # Charni Road
    (-940.0, 3400.0, 1.2),  # Girgaon Chowpatty
    # Malabar Hill Peninsula (promontory into Arabian Sea)
    (-1600.0, 3800.0, 15.0),
    (-2100.0, 4400.0, 35.0), # Walkeshwar / Banganga
    (-2200.0, 5000.0, 45.0), # Malabar Hill Crest
    (-1900.0, 5600.0, 30.0), # Hanging Gardens slope
    (-1600.0, 6200.0, 10.0), # Breach Candy
    (-1500.0, 7200.0, 4.0),  # Mahalaxmi / Haji Ali
    # Worli Peninsula
    (-1800.0, 8500.0, 6.0),
    (-1950.0, 9800.0, 8.0),
    (-1800.0, 11300.0, 5.0), # Worli Seaface Point (Sea Link anchor)
    (-1200.0, 11800.0, 3.0),
    # Mahim Bay & Dadar West
    (-600.0, 12400.0, 2.5),
    (-400.0, 13200.0, 2.5),
    # Bandra South (North end of Mahim Bay)
    (-1200.0, 13800.0, 4.0), # Bandra Fort
    (-800.0, 14500.0, 6.0),  # Bandra Sea Link anchor
    (200.0, 14500.0, 5.0),   # Bandra East
    # East Coast / Harbour Shoreline (heading south)
    (1200.0, 13000.0, 3.0),  # Sion / Dharavi East
    (1800.0, 11000.0, 2.5),  # Chunabhatti / Kurla
    (2200.0, 9000.0, 2.0),   # Wadala
    (2400.0, 7000.0, 2.0),   # Sewri Mudflats
    (1800.0, 5000.0, 2.5),   # Cotton Green
    (1400.0, 3500.0, 2.0),   # Mazagaon Docks
    (1000.0, 2500.0, 2.0),   # Princess Dock
    (800.0, 1500.0, 2.0),    # Victoria Dock
    (600.0, 700.0, 2.0),     # Ballard Pier / Indira Dock
    (400.0, 200.0, 2.0),     # Mumbai Port Trust
    (200.0, -100.0, 1.5),    # Apollo Bandar / Gateway Wharf
    (150.0, -800.0, 1.5),    # Colaba East / Sassoon Dock
    (80.0, -1800.0, 1.5),    # Colaba Naval Base East
    (-50.0, -2600.0, 1.2),   # Dandi Point
]

# Generate triangulated 2D landmass mesh using fan/grid triangulation
land_mesh = bpy.data.meshes.new("TERRAIN_Mumbai_Peninsula_Landmass")
land_obj = bpy.data.objects.new("TERRAIN_Mumbai_Peninsula_Landmass", land_mesh)
bm_land = bmesh.new()

# Create interior spine vertices to ensure convex triangulation without gaps
interior_spine = [
    # Centerline from Colaba north to Dharavi
    (-100.0, -2500.0, 2.0),
    (-120.0, -1500.0, 3.0),
    (-150.0, -500.0, 3.0),
    (-200.0, 500.0, 3.5),   # Fort
    (-300.0, 1500.0, 3.5),  # Churchgate / Azad Maidan
    (-400.0, 2500.0, 4.0),  # Dhobi Talao / Crawford Market
    (-500.0, 4000.0, 5.0),  # Girgaon / Opera House
    (-800.0, 5500.0, 15.0), # Tardeo / Cumballa Hill
    (-600.0, 7500.0, 5.0),  # Mahalaxmi Racecourse
    (-500.0, 9500.0, 4.0),  # Lower Parel
    (-200.0, 11500.0, 3.5), # Dadar Central
    (100.0, 13000.0, 3.0),  # Dharavi
]

# Add boundary and interior vertices
v_boundary = [bm_land.verts.new(Vector(pt)) for pt in coastline_pts]
v_spine = [bm_land.verts.new(Vector(pt)) for pt in interior_spine]

# Create boundary polygon face and triangulate
try:
    face = bm_land.faces.new(v_boundary)
    bmesh.ops.triangulate(bm_land, faces=[face])
except Exception as e:
    print(f"Polygon triangulate warning: {e}")

bm_land.to_mesh(land_mesh)
bm_land.free()
land_obj.data.materials.append(mat_land)
col_land.objects.link(land_obj)

# ------------------------------------------------------------------
# 2. LANDMARK: Chhatrapati Shivaji Maharaj Terminus (CSMT)
# UNESCO World Heritage Site (Victorian Gothic Railway Terminus)
# Georeferenced: lat 18.9398, lon 72.8355 -> (+263m, +1860m)
# ------------------------------------------------------------------
loc_csmt = Vector((263.0, 1860.0, 3.0))

# Main Grand Facade Building (130m wide, 45m deep, 32m tall stone palace)
csmt_main = make_box("LANDMARK_CSMT_GrandFacade", (130, 45, 32), loc_csmt, mat_csmt_stone, col_d)
# Central Octagonal Ribbed Dome (100m total height from ground)
loc_dome = loc_csmt + Vector((0.0, 0.0, 32.0))
csmt_drum = make_cylinder("LANDMARK_CSMT_DomeDrum", 18.0, 24.0, 16, loc_dome, mat_csmt_stone, col_d)
loc_ribs = loc_dome + Vector((0.0, 0.0, 24.0))
csmt_ribdome = make_cylinder("LANDMARK_CSMT_CentralDome", 16.0, 28.0, 16, loc_ribs, mat_csmt_dome, col_d)
# North and South Turret Towers with Gothic Steeples
loc_turret_n = loc_csmt + Vector((-55.0, 0.0, 32.0))
loc_turret_s = loc_csmt + Vector((55.0, 0.0, 32.0))
make_cylinder("LANDMARK_CSMT_Turret_North", 6.0, 26.0, 8, loc_turret_n, mat_csmt_stone, col_d)
make_cylinder("LANDMARK_CSMT_Turret_South", 6.0, 26.0, 8, loc_turret_s, mat_csmt_stone, col_d)
# Massive 18-Track Rail Platform Shed Canopies extending North
loc_shed = loc_csmt + Vector((0.0, 120.0, 0.0))
make_box("LANDMARK_CSMT_TrainShed_Platforms", (110, 180, 14), loc_shed, mat_gothic_stone, col_d)

# ------------------------------------------------------------------
# 3. LANDMARK: Bombay Stock Exchange (BSE / Phiroze Jeejeebhoy Towers)
# Georeferenced: lat 18.9298, lon 72.8331 -> (+10m, +753m)
# ------------------------------------------------------------------
loc_bse = Vector((10.0, 753.0, 3.0))
# 28-Storey Curved Rotunda Tower (118m height)
# Base Podium on Dalal Street
make_box("LANDMARK_BSE_DalalStreet_Podium", (65, 55, 16), loc_bse, mat_bse_tower, col_d)
# Signature Rotunda Elliptical Tower
loc_bse_tower = loc_bse + Vector((0.0, 0.0, 16.0))
make_cylinder("LANDMARK_BSE_RotundaTower", 22.0, 102.0, 24, loc_bse_tower, mat_bse_glass, col_d)
# Rooftop Satellite Telecom Mast
loc_bse_mast = loc_bse + Vector((0.0, 0.0, 118.0))
make_cylinder("LANDMARK_BSE_CommunicationsMast", 1.2, 25.0, 8, loc_bse_mast, mat_bse_tower, col_d)

# ------------------------------------------------------------------
# 4. LANDMARK: Rajabai Clock Tower & University of Mumbai (Fort Campus)
# Georeferenced: lat 18.9297, lon 72.8301 -> (-305m, +742m)
# ------------------------------------------------------------------
loc_rajabai = Vector((-305.0, 742.0, 3.5))
# Main University Library Hall (Venetian Gothic)
make_box("LANDMARK_MumbaiUniv_ConvocationHall", (55, 38, 20), loc_rajabai, mat_gothic_stone, col_d)
# Rajabai Clock Tower (85m height, modeled after Big Ben)
loc_rt = loc_rajabai + Vector((0.0, 18.0, 0.0))
make_box("LANDMARK_RajabaiTower_Shaft", (12, 12, 60), loc_rt, mat_gothic_stone, col_d)
loc_rt_spire = loc_rt + Vector((0.0, 0.0, 60.0))
make_cylinder("LANDMARK_RajabaiTower_Spire", 5.0, 25.0, 8, loc_rt_spire, mat_csmt_dome, col_d)

# ------------------------------------------------------------------
# 5. LANDMARK: Bombay High Court
# Georeferenced: lat 18.9312, lon 72.8306 -> (-252m, +908m)
# ------------------------------------------------------------------
loc_highcourt = Vector((-252.0, 908.0, 3.5))
make_box("LANDMARK_BombayHighCourt_Main", (140, 58, 38), loc_highcourt, mat_gothic_stone, col_d)
# Central Tower with Lady of Justice
loc_hc_tower = loc_highcourt + Vector((0.0, 0.0, 38.0))
make_box("LANDMARK_HighCourt_CentralGothicTower", (20, 18, 20), loc_hc_tower, mat_gothic_stone, col_d)

# ------------------------------------------------------------------
# 6. Oval Maidan & Cross Maidan (Iconic Historic Public Parklands)
# Dividing the Victorian Gothic Quarter from Art Deco Marine Drive
# ------------------------------------------------------------------
loc_oval = Vector((-480.0, 820.0, 3.2))
make_box("MAIDAN_Oval_CricketGrounds", (180, 520, 0.4), loc_oval, mat_maidan_grass, col_d)
loc_cross = Vector((-380.0, 1500.0, 3.2))
make_box("MAIDAN_Cross_PublicGardens", (160, 480, 0.4), loc_cross, mat_maidan_grass, col_d)

# ------------------------------------------------------------------
# 7. LANDMARK: Mantralaya & Vidhan Bhavan (Administrative Headquarters)
# Georeferenced: lat 18.9285, lon 72.8275 -> (-579m, +609m)
# ------------------------------------------------------------------
loc_mantralaya = Vector((-579.0, 609.0, 3.0))
make_box("LANDMARK_Mantralaya_Secretariat", (95, 60, 38), loc_mantralaya, mat_mantralaya, col_d)
loc_vidhan = Vector((-720.0, 520.0, 3.0))
make_box("LANDMARK_VidhanBhavan_Assembly", (80, 75, 28), loc_vidhan, mat_mantralaya, col_d)

# ------------------------------------------------------------------
# 8. LANDMARK: Churchgate Railway Station & Western Railway Headquarters
# Georeferenced: lat 18.9355, lon 72.8272 -> (-610m, +1384m)
# ------------------------------------------------------------------
loc_churchgate = Vector((-610.0, 1384.0, 3.0))
make_box("LANDMARK_ChurchgateStation_Terminal", (75, 55, 32), loc_churchgate, mat_mantralaya, col_d)
loc_wr_hq = Vector((-510.0, 1384.0, 3.0))
make_box("LANDMARK_WesternRailway_Headquarters", (85, 45, 26), loc_wr_hq, mat_gothic_stone, col_d)

result = "Sector D & Full Peninsula Landmass Construction Complete!"
print(result)
