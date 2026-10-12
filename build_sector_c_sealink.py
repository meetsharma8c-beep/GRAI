"""
Build Sector C: Bandra-Worli Sea Link (Rajiv Gandhi Sea Link).
Constructs the iconic 8-lane cable-stayed bridge spanning Mahim Bay:
- 128m tall inverted-Y concrete pylons
- High-tensile stay cable harp fan systems
- Elevated 8-lane aerodynamic twin box-girder road deck
- Reinforced concrete marine piers and caisson foundations
- Worli and Bandra landfall approach viaducts
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

col_c = get_or_create_col('Sector_C_Bandra_WorliSeaLink')

# -------------------------------------------------------------
# Materials for Sea Link
# -------------------------------------------------------------
mat_pylon = get_or_create_mat("MAT_SeaLink_PylonConcrete", (0.88, 0.89, 0.91, 1.0), 0.05, 0.4)
mat_deck_concrete = get_or_create_mat("MAT_SeaLink_BoxGirder", (0.72, 0.74, 0.75, 1.0), 0.05, 0.6)
mat_sealink_asphalt = get_or_create_mat("MAT_SeaLink_HighwayAsphalt", (0.14, 0.14, 0.15, 1.0), 0.0, 0.8)
mat_stay_cables = get_or_create_mat("MAT_SeaLink_StayCables", (0.95, 0.95, 0.98, 1.0), 0.7, 0.25)
mat_pier = get_or_create_mat("MAT_SeaLink_SubstructurePier", (0.55, 0.58, 0.60, 1.0), 0.0, 0.8)

# -------------------------------------------------------------
# Sea Link Waypoints across Mahim Bay (Worli to Bandra)
# Total length approx 4.2 km in our georeferenced space
# -------------------------------------------------------------
sealink_spine = [
    Vector((-1790.0, 10500.0, 14.0)),  # Worli Landfall
    Vector((-1750.0, 10900.0, 18.0)),  # Worli Approach Viaduct
    Vector((-1630.0, 11400.0, 22.0)),  # Worli Cable Stay Span (Tower 1)
    Vector((-1480.0, 11800.0, 24.0)),  # Mid-Bay Viaduct
    Vector((-1316.0, 12250.0, 26.0)),  # Main Channel Cable Stay Span (Tower 2 - Main Pylon)
    Vector((-1160.0, 12700.0, 24.0)),  # Bandra Cable Stay Span
    Vector((-1020.0, 13150.0, 20.0)),  # Bandra Approach Curve
    Vector((-842.0, 13600.0, 14.0)),   # Bandra Toll Plaza Landfall
]

# Subdivide spine for smooth deck alignment
deck_pts = []
for i in range(len(sealink_spine) - 1):
    p0 = sealink_spine[i]
    p1 = sealink_spine[i + 1]
    for s in range(12):
        deck_pts.append(p0.lerp(p1, s / 12.0))
deck_pts.append(sealink_spine[-1])

# Build 8-lane Dual Box-Girder Road Deck Mesh
deck_mesh = bpy.data.meshes.new("SEALINK_RoadDeck_8Lanes")
deck_obj = bpy.data.objects.new("SEALINK_RoadDeck_8Lanes", deck_mesh)
bm_deck = bmesh.new()

road_width = 34.0  # 34m wide dual carriageway (4 lanes northbound + 4 lanes southbound)
girder_depth = 4.0

prev_v_left, prev_v_right = None, None
prev_v_b_left, prev_v_b_right = None, None

for i in range(len(deck_pts)):
    p = deck_pts[i]
    if i < len(deck_pts) - 1:
        tangent = (deck_pts[i + 1] - p).normalized()
    else:
        tangent = (p - deck_pts[i - 1]).normalized()
    normal = Vector((-tangent.y, tangent.x, 0.0)).normalized()

    # Top deck road surface
    v_tl = bm_deck.verts.new(p - normal * (road_width / 2.0))
    v_tr = bm_deck.verts.new(p + normal * (road_width / 2.0))
    # Bottom box-girder soffit
    v_bl = bm_deck.verts.new(p - normal * (road_width / 2.0 - 2.0) - Vector((0, 0, girder_depth)))
    v_br = bm_deck.verts.new(p + normal * (road_width / 2.0 - 2.0) - Vector((0, 0, girder_depth)))

    if prev_v_left:
        # Top deck face (roadway)
        bm_deck.faces.new([prev_v_left, prev_v_right, v_tr, v_tl])
        # Bottom soffit face
        bm_deck.faces.new([prev_v_b_left, v_bl, v_br, prev_v_b_right])
        # Left side web
        bm_deck.faces.new([prev_v_left, v_tl, v_bl, prev_v_b_left])
        # Right side web
        bm_deck.faces.new([prev_v_right, prev_v_b_right, v_br, v_tr])

    prev_v_left = v_tl
    prev_v_right = v_tr
    prev_v_b_left = v_bl
    prev_v_b_right = v_br

    # Marine Substructure Piers (spaced every 6 steps ~ 50 meters)
    if i % 6 == 0 and i > 2 and i < len(deck_pts) - 3:
        pier_loc = Vector((p.x, p.y, -2.0))
        pier_height = p.z + 1.0
        make_box(f"SEALINK_MarinePier_{i}", (6.0, 10.0, pier_height), pier_loc, mat_pier, col_c)
        # Underwater Caisson foundation
        make_cylinder(f"SEALINK_Caisson_{i}", 9.0, 6.0, 12, pier_loc - Vector((0,0,4)), mat_pier, col_c)

bm_deck.to_mesh(deck_mesh)
bm_deck.free()
deck_obj.data.materials.append(mat_sealink_asphalt)
col_c.objects.link(deck_obj)

# -------------------------------------------------------------
# ICONIC CABLE-STAYED TOWERS (PYLONS)
# 1. Main Channel Diamond Tower (Pylon 1 at ~12250m)
# 2. Worli Channel Inverted-Y Tower (Pylon 2 at ~11400m)
# -------------------------------------------------------------
tower_locations = [
    ("MainPylon_BandraChannel", Vector((-1316.0, 12250.0, 0.0)), 128.0),
    ("SecondaryPylon_WorliChannel", Vector((-1630.0, 11400.0, 0.0)), 96.0),
]

cable_mesh = bpy.data.meshes.new("SEALINK_StayCables_HarpSystem")
cable_obj = bpy.data.objects.new("SEALINK_StayCables_HarpSystem", cable_mesh)
bm_cables = bmesh.new()

for t_name, t_loc, t_height in tower_locations:
    # Massive Marine Caisson Base (Foundations resting in Arabian Sea)
    make_cylinder(f"SEALINK_Foundation_{t_name}", 18.0, 14.0, 24, t_loc - Vector((0, 0, 4)), mat_pylon, col_c)
    
    # Lower Flared Legs (below deck ~ Z=26m)
    make_box(f"SEALINK_LegLeft_Lower_{t_name}", (5.0, 7.0, 26.0), t_loc + Vector((-14.0, 0, 0)), mat_pylon, col_c)
    make_box(f"SEALINK_LegRight_Lower_{t_name}", (5.0, 7.0, 26.0), t_loc + Vector((14.0, 0, 0)), mat_pylon, col_c)
    
    # Lower Cross-Girder tie beam under the road deck
    make_box(f"SEALINK_CrossBeam_Lower_{t_name}", (34.0, 8.0, 4.0), t_loc + Vector((0, 0, 22.0)), mat_pylon, col_c)
    
    # Upper Inverted-Y Tower Legs converging to apex
    # Left Upper Arm
    leg_l = make_box(f"SEALINK_ArmLeft_{t_name}", (4.5, 6.0, t_height - 26.0), t_loc + Vector((-8.0, 0, 26.0)), mat_pylon, col_c)
    leg_l.rotation_euler = (0, 0.12, 0) # Inward lean
    # Right Upper Arm
    leg_r = make_box(f"SEALINK_ArmRight_{t_name}", (4.5, 6.0, t_height - 26.0), t_loc + Vector((8.0, 0, 26.0)), mat_pylon, col_c)
    leg_r.rotation_euler = (0, -0.12, 0) # Inward lean
    
    # Tower Apex Saddle Crown
    make_box(f"SEALINK_Apex_{t_name}", (10.0, 8.0, 16.0), t_loc + Vector((0, 0, t_height - 10.0)), mat_pylon, col_c)

    # Semi-Fan Stay Cables connecting tower saddle to deck spans
    apex_pt = t_loc + Vector((0, 0, t_height - 4.0))
    # Fan out along deck on both North and South sides
    for side in [-1, 1]:
        for c_idx in range(1, 14):
            # Deck anchor offset along spine (from 20m to 180m from pylon)
            dist = c_idx * 14.0 * side
            deck_anchor_l = t_loc + Vector((-12.0, dist, 26.0))
            deck_anchor_r = t_loc + Vector((12.0, dist, 26.0))
            
            # Saddle anchor along tower height (between Z=70m and Z=120m)
            saddle_z = t_height - 20.0 + (c_idx * 1.2)
            saddle_l = t_loc + Vector((-3.0, 0, saddle_z))
            saddle_r = t_loc + Vector((3.0, 0, saddle_z))
            
            # Create thin quad ribbon for each cable for clean rendering
            vl1 = bm_cables.verts.new(saddle_l)
            vl2 = bm_cables.verts.new(saddle_l + Vector((0.2, 0, 0)))
            vl3 = bm_cables.verts.new(deck_anchor_l + Vector((0.2, 0, 0)))
            vl4 = bm_cables.verts.new(deck_anchor_l)
            bm_cables.faces.new([vl1, vl2, vl3, vl4])

            vr1 = bm_cables.verts.new(saddle_r)
            vr2 = bm_cables.verts.new(saddle_r + Vector((0.2, 0, 0)))
            vr3 = bm_cables.verts.new(deck_anchor_r + Vector((0.2, 0, 0)))
            vr4 = bm_cables.verts.new(deck_anchor_r)
            bm_cables.faces.new([vr1, vr2, vr3, vr4])

bm_cables.to_mesh(cable_mesh)
bm_cables.free()
cable_obj.data.materials.append(mat_stay_cables)
col_c.objects.link(cable_obj)

# -------------------------------------------------------------
# Bandra Toll Plaza & Interchange (North Anchor)
# -------------------------------------------------------------
loc_toll = Vector((-842.0, 13600.0, 14.0))
make_box("SEALINK_Bandra_TollCanopy", (55.0, 16.0, 7.0), loc_toll, mat_pylon, col_c)
for b_idx in range(8):
    booth_loc = loc_toll + Vector((-24.0 + b_idx * 7.0, 0, 0))
    make_box(f"SEALINK_TollBooth_{b_idx}", (2.2, 3.5, 3.2), booth_loc, mat_deck_concrete, col_c)

result = "Sector C: Bandra-Worli Sea Link Construction Complete!"
print(result)
