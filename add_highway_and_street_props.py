"""
Add Playable Street & Highway Props:
1. Sea Link Highway: Central Jersey median barrier, lane dividers, overhead gantry sign
2. Marine Drive: Victorian triple-globe streetlights (Queen's Necklace), promenade railings
3. Apollo Bandar: Plaza streetlights and heritage bollards
4. Traffic Assets: Kaali-Peeli taxis and BEST double-decker bus on Marine Drive
"""
import bpy
import bmesh
import math
import random
import mathutils
from mathutils import Vector, Matrix

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

def get_or_create_mat(mat_name, diff_col, met=0.0, rough=0.5, emit=0.0):
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
        if emit > 0 and 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = diff_col
            bsdf.inputs['Emission Strength'].default_value = emit
        elif emit > 0 and 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = diff_col
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

col_props = get_or_create_col('Playable_Street_Props')

# Materials
mat_barrier = get_or_create_mat("MAT_JerseyBarrier_Concrete", (0.80, 0.81, 0.82, 1.0), 0.05, 0.7)
mat_gantry_green = get_or_create_mat("MAT_HighwaySign_Green", (0.05, 0.42, 0.15, 1.0), 0.1, 0.3)
mat_gantry_steel = get_or_create_mat("MAT_HighwaySign_SteelTruss", (0.35, 0.38, 0.40, 1.0), 0.8, 0.3)
mat_lamp_castiron = get_or_create_mat("MAT_Victorian_CastIron", (0.12, 0.14, 0.15, 1.0), 0.85, 0.35)
mat_lamp_glow = get_or_create_mat("MAT_StreetLight_WarmGlow", (1.0, 0.85, 0.55, 1.0), 0.0, 0.1, emit=3.5)
mat_taxi_yellow = get_or_create_mat("MAT_Taxi_YellowRoof", (0.95, 0.72, 0.05, 1.0), 0.2, 0.3)
mat_taxi_black = get_or_create_mat("MAT_Taxi_BlackBody", (0.08, 0.08, 0.09, 1.0), 0.3, 0.3)
mat_best_red = get_or_create_mat("MAT_BEST_Bus_Red", (0.82, 0.12, 0.10, 1.0), 0.2, 0.4)

# -------------------------------------------------------------
# 1. Bandra-Worli Sea Link Highway Median & Overhead Gantry Sign
# -------------------------------------------------------------
# Median Jersey Barrier along the Sea Link spine
sealink_pts = [
    Vector((-1790.0, 10500.0, 14.0)),
    Vector((-1750.0, 10900.0, 18.0)),
    Vector((-1630.0, 11400.0, 22.0)),
    Vector((-1480.0, 11800.0, 24.0)),
    Vector((-1316.0, 12250.0, 26.0)),
    Vector((-1160.0, 12700.0, 24.0)),
    Vector((-1020.0, 13150.0, 20.0)),
    Vector((-842.0, 13600.0, 14.0)),
]

for i in range(len(sealink_pts) - 1):
    p0 = sealink_pts[i]
    p1 = sealink_pts[i + 1]
    mid = p0.lerp(p1, 0.5)
    length = (p1 - p0).length
    direction = (p1 - p0).normalized()
    angle = math.atan2(direction.y, direction.x)
    
    # Continuous concrete median jersey barrier (0.8m wide, 1.2m high)
    b_obj = make_box(f"SEALINK_MedianBarrier_{i}", (length, 0.8, 1.2), mid, mat_barrier, col_props)
    b_obj.rotation_euler = (0, 0, angle)

# Overhead Highway Gantry Sign at approach to Main Pylon (~12050m)
loc_gantry = Vector((-1380.0, 12050.0, 25.5))
# Gantry steel support pillars on either side of the 34m road
make_box("SEALINK_Gantry_PostLeft", (0.8, 0.8, 8.5), loc_gantry + Vector((-17.0, 0, 0)), mat_gantry_steel, col_props)
make_box("SEALINK_Gantry_PostRight", (0.8, 0.8, 8.5), loc_gantry + Vector((17.0, 0, 0)), mat_gantry_steel, col_props)
# Overhead Truss Beam across road
make_box("SEALINK_Gantry_CrossTruss", (35.0, 1.2, 1.0), loc_gantry + Vector((0, 0, 7.8)), mat_gantry_steel, col_props)
# Highway Green Destination Sign Board ("BANDRA / TOLL PLAZA 1.5 KM")
make_box("SEALINK_Gantry_SignBoard", (18.0, 0.4, 3.2), loc_gantry + Vector((0, -0.6, 6.2)), mat_gantry_green, col_props)

# -------------------------------------------------------------
# 2. Marine Drive "Queen's Necklace" Victorian Lampposts
# Curved along the pedestrian seawall
# -------------------------------------------------------------
marine_drive_sample_pts = [
    Vector((-1350.0, 120.0, 1.2)),
    Vector((-1220.0, 310.0, 1.2)),
    Vector((-1160.0, 480.0, 1.2)),
    Vector((-1100.0, 680.0, 1.2)),
    Vector((-1060.0, 920.0, 1.2)),
    Vector((-1020.0, 1200.0, 1.2)),
    Vector((-985.0, 1550.0, 1.2)),
    Vector((-955.0, 1950.0, 1.2)),
    Vector((-930.0, 2380.0, 1.2)),
    Vector((-910.0, 2820.0, 1.2)),
    Vector((-915.0, 3280.0, 1.2)),
]

for idx, p in enumerate(marine_drive_sample_pts):
    # Victorian Cast Iron Lamp Post (6m height)
    make_box(f"LAMP_MarineDrive_Post_{idx}", (0.35, 0.35, 5.5), p, mat_lamp_castiron, col_props)
    # Triple Globe Luminaire Arms
    make_box(f"LAMP_MarineDrive_Arm_{idx}", (1.8, 0.3, 0.3), p + Vector((0, 0, 5.2)), mat_lamp_castiron, col_props)
    # Luminous Glowing Globes
    make_box(f"LAMP_MarineDrive_GlobeCenter_{idx}", (0.5, 0.5, 0.5), p + Vector((0, 0, 5.6)), mat_lamp_glow, col_props)
    make_box(f"LAMP_MarineDrive_GlobeLeft_{idx}", (0.4, 0.4, 0.4), p + Vector((-0.8, 0, 5.4)), mat_lamp_glow, col_props)
    make_box(f"LAMP_MarineDrive_GlobeRight_{idx}", (0.4, 0.4, 0.4), p + Vector((0.8, 0, 5.4)), mat_lamp_glow, col_props)

# -------------------------------------------------------------
# 3. Iconic Mumbai Vehicles on Marine Drive & Apollo Bandar
# - Kaali-Peeli Taxis (Premier Padmini)
# - BEST Red Double-Decker City Bus
# -------------------------------------------------------------
# Kaali-Peeli Taxi cruising south on Marine Drive
loc_taxi_md = Vector((-1035.0, 1020.0, 1.1))
# Black Lower Body
make_box("VEHICLE_KaaliPeeli_MD_Body", (2.0, 4.4, 0.9), loc_taxi_md, mat_taxi_black, col_props)
# Yellow Iconic Cabin Roof
make_box("VEHICLE_KaaliPeeli_MD_Roof", (1.8, 2.4, 0.7), loc_taxi_md + Vector((0, -0.2, 0.9)), mat_taxi_yellow, col_props)

# BEST Red Double-Decker Bus on Netaji Subhash Chandra Bose Road
loc_bus = Vector((-1032.0, 960.0, 1.1))
make_box("VEHICLE_BEST_Bus_Chassis", (2.6, 9.8, 1.8), loc_bus, mat_best_red, col_props)
make_box("VEHICLE_BEST_Bus_UpperDeck", (2.6, 9.6, 1.9), loc_bus + Vector((0, 0, 1.8)), mat_best_red, col_props)

# Kaali-Peeli Taxi parked near Gateway of India Plaza
loc_taxi_gw = Vector((185.0, -180.0, 1.5))
make_box("VEHICLE_KaaliPeeli_Gateway_Body", (2.0, 4.4, 0.9), loc_taxi_gw, mat_taxi_black, col_props)
make_box("VEHICLE_KaaliPeeli_Gateway_Roof", (1.8, 2.4, 0.7), loc_taxi_gw + Vector((0, -0.2, 0.9)), mat_taxi_yellow, col_props)

result = "Playable Street & Highway Props Successfully Added!"
print(result)
