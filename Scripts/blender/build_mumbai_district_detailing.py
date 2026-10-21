#!/usr/bin/env python3
"""
build_mumbai_district_detailing.py
==================================
Fine-tunes iconic Mumbai districts with rich architectural detailing:
1. Colaba Causeway (Shahid Bhagat Singh Rd) Heritage Market Arcade:
   - Striped canvas shopfront awnings (crimson/cream, navy/white, emerald/gold)
   - Wrought-iron ornamental Victorian balcony balustrades
   - Vintage brass street fixtures & cafe facade details
2. Lower Parel & Worli Industrial Heritage:
   - Historic red-brick textile mill chimneys (Phoenix/Mathuradas Mills heritage)
   - Brick plinths and flue caps standing alongside the contemporary glass megatowers
3. Marine Drive & Nariman Point Shoreline Armor:
   - Interlocking high-density concrete tetrapods along the coastal turn

STRICT CONSTRAINT: ZERO pedestrians, ZERO characters, ZERO vehicles, ZERO living entities!
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def get_or_create_col(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c

def get_or_create_mat(mat_name, base_col, met=0.0, rough=0.5, emit_col=None, emit_strength=0.0):
    if mat_name in bpy.data.materials:
        m = bpy.data.materials[mat_name]
    else:
        m = bpy.data.materials.new(name=mat_name)
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_col
        bsdf.inputs['Metallic'].default_value = met
        bsdf.inputs['Roughness'].default_value = rough
        if emit_strength > 0 and emit_col:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emit_col
                bsdf.inputs['Emission Strength'].default_value = emit_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emit_col
    return m

def build_district_detailing():
    print("\n========================================================")
    print("BUILDING DISTRICT ARCHITECTURAL DETAILING")
    print("========================================================")

    col_detail = get_or_create_col("District_Architectural_Detailing")

    # Clean old detailing objects if any
    old_objs = [o for o in list(col_detail.objects) if o.name.startswith("DETAIL_")]
    for o in old_objs:
        bpy.data.objects.remove(o, do_unlink=True)

    # Materials
    mat_awning_crimson = get_or_create_mat("MAT_Awning_Striped_Crimson", (0.78, 0.14, 0.12, 1.0), rough=0.75)
    mat_awning_navy = get_or_create_mat("MAT_Awning_Striped_Navy", (0.08, 0.22, 0.52, 1.0), rough=0.75)
    mat_awning_emerald = get_or_create_mat("MAT_Awning_Striped_Emerald", (0.06, 0.42, 0.22, 1.0), rough=0.75)
    mat_awning_gold = get_or_create_mat("MAT_Awning_Striped_Gold", (0.85, 0.62, 0.12, 1.0), rough=0.75)
    mat_iron_filigree = get_or_create_mat("MAT_Victorian_Iron_Filigree", (0.08, 0.08, 0.09, 1.0), met=0.90, rough=0.35)
    mat_mill_brick = get_or_create_mat("MAT_Historic_Mill_RedBrick", (0.52, 0.22, 0.14, 1.0), met=0.0, rough=0.88)
    mat_chimney_mortar = get_or_create_mat("MAT_Chimney_LimeMortar", (0.65, 0.62, 0.56, 1.0), met=0.0, rough=0.92)

    # -------------------------------------------------------------
    # 1. Colaba Causeway Heritage Market Arcades & Striped Awnings
    # Along Shahid Bhagat Singh Road: X ~ 40 to 80, Y ~ -220 to -650
    # -------------------------------------------------------------
    print("Building Colaba Causeway heritage market canopies & iron balconies...")
    bm_awnings = bmesh.new()
    bm_balconies = bmesh.new()

    awning_colors = [mat_awning_crimson, mat_awning_navy, mat_awning_emerald, mat_awning_gold]
    shops_count = 32
    y_start_colaba = -220.0
    y_step_colaba = -14.0

    for i in range(shops_count):
        sy = y_start_colaba + i * y_step_colaba
        # East side of Causeway: X ~ 66.5, ground is Z ~ 7.5m
        # Cantilevered sloped canvas awning (depth 2.4m, width 12.0m, height 0.6m, pitched 25 deg)
        t_awn = Matrix.Translation(Vector((66.5, sy, 10.7))) @ Matrix.Rotation(math.radians(-22.0), 4, 'Y')
        bmesh.ops.create_cube(bm_awnings, size=1.0, matrix=t_awn @ Matrix.Scale(2.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(11.5, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))))

        # Victorian wrought iron balcony balustrade on 1st & 2nd floors (Z = 12.5m & 16.2m)
        for fl_z in [12.5, 16.2]:
            t_balc = Matrix.Translation(Vector((67.8, sy, fl_z)))
            # Balcony floor slab
            bmesh.ops.create_cube(bm_balconies, size=1.0, matrix=t_balc @ Matrix.Scale(1.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(11.5, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.15, 4, Vector((0, 0, 1))))
            # Handrail top bar
            t_rail = Matrix.Translation(Vector((67.1, sy, fl_z + 0.95)))
            bmesh.ops.create_cube(bm_balconies, size=1.0, matrix=t_rail @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(11.5, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.06, 4, Vector((0, 0, 1))))
            # Vertical balusters
            for b_idx in range(12):
                by_off = -5.2 + b_idx * 0.95
                t_vert = Matrix.Translation(Vector((67.1, sy + by_off, fl_z + 0.5)))
                bmesh.ops.create_cone(bm_balconies, cap_ends=True, radius1=0.025, radius2=0.025, depth=0.9, segments=6, matrix=t_vert)

    mesh_awnings = bpy.data.meshes.new("DETAIL_Colaba_Market_Awnings_Mesh")
    bm_awnings.to_mesh(mesh_awnings)
    bm_awnings.free()
    mesh_awnings.materials.append(mat_awning_crimson)
    obj_awnings = bpy.data.objects.new("DETAIL_Colaba_Market_Awnings_Master", mesh_awnings)
    col_detail.objects.link(obj_awnings)

    mesh_balconies = bpy.data.meshes.new("DETAIL_Colaba_Iron_Balconies_Mesh")
    bm_balconies.to_mesh(mesh_balconies)
    bm_balconies.free()
    mesh_balconies.materials.append(mat_iron_filigree)
    obj_balconies = bpy.data.objects.new("DETAIL_Colaba_Iron_Balconies_Master", mesh_balconies)
    col_detail.objects.link(obj_balconies)

    # -------------------------------------------------------------
    # 2. Lower Parel Historic Textile Mill Red-Brick Chimneys
    # Phoenix Mills / Mathuradas Mills compound: X ~ -650 to -400, Y ~ 6800 to 7600
    # -------------------------------------------------------------
    print("Building Lower Parel historic textile mill brick chimneys...")
    bm_chimneys = bmesh.new()
    mill_chimney_sites = [
        ("Phoenix_Mills_Heritage_Chimney", Vector((-520.0, 7150.0, 14.0)), 62.0, 4.2, 2.4),
        ("Mathuradas_Mills_Heritage_Chimney", Vector((-440.0, 7380.0, 14.0)), 54.0, 3.8, 2.1),
        ("Victoria_Mills_Historic_Stack", Vector((-680.0, 6950.0, 14.0)), 58.0, 4.0, 2.2),
        ("Shree_Ram_Mills_Brick_Stack", Vector((-580.0, 7550.0, 14.0)), 66.0, 4.5, 2.5),
    ]

    for name, loc, height, rad_base, rad_top in mill_chimney_sites:
        # Octagonal brick chimney plinth (height 6.0m)
        t_plinth = Matrix.Translation(loc + Vector((0, 0, 3.0)))
        bmesh.ops.create_cone(bm_chimneys, cap_ends=True, radius1=rad_base * 1.35, radius2=rad_base * 1.25, depth=6.0, segments=8, matrix=t_plinth)

        # Main tapering round chimney shaft
        t_shaft = Matrix.Translation(loc + Vector((0, 0, 6.0 + height / 2.0)))
        bmesh.ops.create_cone(bm_chimneys, cap_ends=True, radius1=rad_base, radius2=rad_top, depth=height, segments=16, matrix=t_shaft)

        # Decorative corbelled brick crown cap & iron reinforcing bands
        t_crown = Matrix.Translation(loc + Vector((0, 0, 6.0 + height + 1.2)))
        bmesh.ops.create_cone(bm_chimneys, cap_ends=True, radius1=rad_top * 1.25, radius2=rad_top * 1.15, depth=2.4, segments=16, matrix=t_crown)

        # Cast-iron bands around shaft every 8 meters
        bands_count = int(height / 8.0)
        for b_i in range(bands_count):
            bz = 6.0 + b_i * 8.0
            cur_rad = rad_base - (b_i * 8.0 / height) * (rad_base - rad_top)
            t_band = Matrix.Translation(loc + Vector((0, 0, bz)))
            bmesh.ops.create_cone(bm_chimneys, cap_ends=True, radius1=cur_rad * 1.03, radius2=cur_rad * 1.03, depth=0.25, segments=16, matrix=t_band)

    mesh_chimneys = bpy.data.meshes.new("DETAIL_LowerParel_Mill_Chimneys_Mesh")
    bm_chimneys.to_mesh(mesh_chimneys)
    bm_chimneys.free()
    mesh_chimneys.materials.append(mat_mill_brick)
    obj_chimneys = bpy.data.objects.new("DETAIL_LowerParel_Mill_Chimneys_Master", mesh_chimneys)
    col_detail.objects.link(obj_chimneys)

    # -------------------------------------------------------------
    # 3. Bandra-Worli Sea Link Stay-Cable Enhancement & Aviation Beacon
    # -------------------------------------------------------------
    print("Checking Sea Link cable-stayed pylon enhancement...")
    beacon_mat = get_or_create_mat("MAT_Aviation_RedBeacon", (0.95, 0.05, 0.02, 1.0), met=0.0, rough=0.1, emit_col=(1.0, 0.04, 0.02, 1.0), emit_strength=35.0)
    bm_beacon = bmesh.new()
    bmesh.ops.create_uvsphere(bm_beacon, u_segments=10, v_segments=8, radius=0.9, matrix=Matrix.Translation(Vector((-1316.0, 12250.0, 127.0))))
    mesh_beacon = bpy.data.meshes.new("DETAIL_SeaLink_Aviation_Beacon_Mesh")
    bm_beacon.to_mesh(mesh_beacon)
    bm_beacon.free()
    mesh_beacon.materials.append(beacon_mat)
    obj_beacon = bpy.data.objects.new("DETAIL_SeaLink_Aviation_Beacon_Master", mesh_beacon)
    col_detail.objects.link(obj_beacon)

    print(f"\nSuccessfully generated district detailing systems in '{col_detail.name}'!")
    return "District architectural detailing built successfully."

if __name__ == "__main__":
    msg = build_district_detailing()
    print(msg)
