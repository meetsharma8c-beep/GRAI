#!/usr/bin/env python3
"""
build_mumbai_street_props_master.py
===================================
Generates high-fidelity, authentic Mumbai street-level urban furniture and props:
1. Queen's Necklace Victorian 3-Globe Heritage Promenade Posts & Highway Masts (1,700m curve)
2. Fort & Colaba Classical Heritage Lampposts
3. BMC Bilingual Heritage Street Name Signboards (Marathi / English)
4. BEST Transit Passenger Bus Stop Shelters (Stainless steel, red bench, yellow route totem)
5. Traffic Signal Gantries & Cantilevers with 3-aspect LED signal heads
6. BMC Yellow & Black Tubular Steel Pedestrian Safety Guard Railings
7. Colonial Red Cast-Iron Fire Hydrants & Round Indian Post Pillar Boxes
8. BMC Segregated Public Litter Bins (Green / Blue dual receptacles)
9. Apollo Bunder Gateway Basalt Plaza Bollards

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

def build_street_props():
    print("\n========================================================")
    print("BUILDING AUTHENTIC MUMBAI STREET-LEVEL PROPS & INFRASTRUCTURE")
    print("========================================================")

    # 1. Clean up target collection and any old vehicle remnants
    target_col_name = "Urban_Street_Furniture_Props"
    col_props = get_or_create_col(target_col_name)

    # Purge old vehicles or obsolete props from scene
    old_to_purge = [o for o in list(bpy.data.objects) if any(kw in o.name for kw in [
        'VEHICLE_', 'Rick_Wheel', 'LIGHTS_QueensNecklace_', 'PROP_Chai_', 'LAMP_QueensNecklace_', 'PROP_MUMBAI_'
    ])]
    for o in old_to_purge:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"Purged {len(old_to_purge)} old prop/vehicle objects.")

    # 2. Material Palette Setup
    mat_castiron = get_or_create_mat("MAT_Prop_CastIron_Black", (0.05, 0.05, 0.06, 1.0), met=0.85, rough=0.45)
    mat_steelsilver = get_or_create_mat("MAT_Prop_GalvanizedSteel", (0.75, 0.77, 0.80, 1.0), met=0.90, rough=0.25)
    mat_lamp_glow = get_or_create_mat("MAT_Prop_Lamp_WarmGlow", (1.0, 0.90, 0.70, 1.0), met=0.0, rough=0.1, emit_col=(1.0, 0.84, 0.48, 1.0), emit_strength=18.0)
    mat_led_highway = get_or_create_mat("MAT_Prop_LED_HighwayGlow", (0.95, 0.98, 1.0, 1.0), met=0.0, rough=0.1, emit_col=(0.90, 0.95, 1.0, 1.0), emit_strength=24.0)
    
    mat_bmcyellow = get_or_create_mat("MAT_Prop_BMC_CanaryYellow", (0.92, 0.68, 0.04, 1.0), met=0.1, rough=0.35)
    mat_bmcblue = get_or_create_mat("MAT_Prop_BMC_CobaltBlue", (0.04, 0.18, 0.48, 1.0), met=0.2, rough=0.30)
    mat_bestred = get_or_create_mat("MAT_Prop_BEST_CrimsonRed", (0.82, 0.08, 0.06, 1.0), met=0.15, rough=0.35)
    mat_signalgreen = get_or_create_mat("MAT_Prop_Signal_Green", (0.02, 0.88, 0.22, 1.0), met=0.0, rough=0.1, emit_col=(0.02, 0.95, 0.25, 1.0), emit_strength=15.0)
    mat_signalred = get_or_create_mat("MAT_Prop_Signal_Red", (0.95, 0.04, 0.02, 1.0), met=0.0, rough=0.1, emit_col=(0.98, 0.05, 0.02, 1.0), emit_strength=15.0)
    mat_postred = get_or_create_mat("MAT_Prop_IndiaPost_Red", (0.78, 0.06, 0.04, 1.0), met=0.75, rough=0.35)
    mat_brass = get_or_create_mat("MAT_Prop_PolishedBrass", (0.85, 0.65, 0.18, 1.0), met=0.92, rough=0.20)
    mat_bin_green = get_or_create_mat("MAT_Prop_Dustbin_Green", (0.06, 0.46, 0.14, 1.0), met=0.2, rough=0.4)
    mat_bin_blue = get_or_create_mat("MAT_Prop_Dustbin_Blue", (0.08, 0.32, 0.72, 1.0), met=0.2, rough=0.4)
    mat_basalt_bollard = get_or_create_mat("MAT_Prop_KharodiBasalt", (0.32, 0.26, 0.20, 1.0), met=0.0, rough=0.85)

    # -----------------------------------------------------------------
    # A. Queen's Necklace Victorian 3-Globe Promenade Lamps & Masts
    # -----------------------------------------------------------------
    print("Building Marine Drive Queen's Necklace continuous lighting system...")
    bm_qn_posts = bmesh.new()
    bm_qn_globes = bmesh.new()
    steps_qn = 68
    y_start_qn, y_end_qn = 500.0, 2200.0
    dy_qn = (y_end_qn - y_start_qn) / float(steps_qn)

    for i in range(steps_qn + 1):
        y = y_start_qn + i * dy_qn
        x_c = -1016.0 + 0.000080 * ((y - 1100.0) ** 2)

        # Victorian 3-Globe Heritage Promenade Lamp Post
        x_prom = x_c - 11.5
        z_prom = 7.35

        # Base Plinth & Fluted Shaft (height 4.2m)
        mat_t1 = Matrix.Translation(Vector((x_prom, y, z_prom + 0.4)))
        bmesh.ops.create_cone(bm_qn_posts, cap_ends=True, radius1=0.24, radius2=0.18, depth=0.8, segments=8, matrix=mat_t1)
        mat_t2 = Matrix.Translation(Vector((x_prom, y, z_prom + 2.5)))
        bmesh.ops.create_cone(bm_qn_posts, cap_ends=True, radius1=0.11, radius2=0.07, depth=3.4, segments=8, matrix=mat_t2)

        # Arched Twin Cross-Arm (width 1.3m)
        mat_rot_x = Matrix.Rotation(1.5708, 4, 'Y')
        mat_t3 = Matrix.Translation(Vector((x_prom, y, z_prom + 4.15))) @ mat_rot_x
        bmesh.ops.create_cone(bm_qn_posts, cap_ends=True, radius1=0.045, radius2=0.045, depth=1.3, segments=6, matrix=mat_t3)

        # Center, Left, Right Frosted Globes
        bmesh.ops.create_uvsphere(bm_qn_globes, u_segments=10, v_segments=8, radius=0.24, matrix=Matrix.Translation(Vector((x_prom, y, z_prom + 4.55))))
        bmesh.ops.create_uvsphere(bm_qn_globes, u_segments=8, v_segments=6, radius=0.19, matrix=Matrix.Translation(Vector((x_prom - 0.60, y, z_prom + 4.22))))
        bmesh.ops.create_uvsphere(bm_qn_globes, u_segments=8, v_segments=6, radius=0.19, matrix=Matrix.Translation(Vector((x_prom + 0.60, y, z_prom + 4.22))))

        # Highway Median High-Mast Luminaires (every 50m)
        if (i % 2) == 0:
            x_med = x_c
            z_med = 7.23
            mat_tm1 = Matrix.Translation(Vector((x_med, y, z_med + 4.5)))
            bmesh.ops.create_cone(bm_qn_posts, cap_ends=True, radius1=0.18, radius2=0.10, depth=9.0, segments=8, matrix=mat_tm1)
            mat_tm2 = Matrix.Translation(Vector((x_med, y, z_med + 9.0))) @ mat_rot_x
            bmesh.ops.create_cone(bm_qn_posts, cap_ends=True, radius1=0.05, radius2=0.05, depth=3.8, segments=6, matrix=mat_tm2)
            bmesh.ops.create_uvsphere(bm_qn_globes, u_segments=8, v_segments=6, radius=0.26, matrix=Matrix.Translation(Vector((x_med - 1.9, y, z_med + 8.95))))
            bmesh.ops.create_uvsphere(bm_qn_globes, u_segments=8, v_segments=6, radius=0.26, matrix=Matrix.Translation(Vector((x_med + 1.9, y, z_med + 8.95))))

    # Consolidate Queen's Necklace meshes
    mesh_qn_posts = bpy.data.meshes.new("PROP_MUMBAI_QueensNecklace_Posts_Mesh")
    bm_qn_posts.to_mesh(mesh_qn_posts)
    bm_qn_posts.free()
    mesh_qn_posts.materials.append(mat_castiron)
    obj_qn_posts = bpy.data.objects.new("PROP_MUMBAI_QueensNecklace_Posts_Master", mesh_qn_posts)
    col_props.objects.link(obj_qn_posts)

    mesh_qn_globes = bpy.data.meshes.new("PROP_MUMBAI_QueensNecklace_Globes_Mesh")
    bm_qn_globes.to_mesh(mesh_qn_globes)
    bm_qn_globes.free()
    mesh_qn_globes.materials.append(mat_lamp_glow)
    obj_qn_globes = bpy.data.objects.new("PROP_MUMBAI_QueensNecklace_Globes_Master", mesh_qn_globes)
    col_props.objects.link(obj_qn_globes)

    # -----------------------------------------------------------------
    # B. BMC Heritage Bilingual Street Signboards
    # -----------------------------------------------------------------
    print("Building BMC Heritage bilingual street signboards...")
    sign_locations = [
        ("SIGN_MarineDrive_VeerNariman", Vector((-982.0, 920.0, 7.35)), 0.0),
        ("SIGN_CSMT_DNDadabhaiRoad", Vector((245.0, 1680.0, 13.5)), -0.25),
        ("SIGN_Churchgate_OvalMaidan", Vector((-850.0, 910.0, 7.4)), 0.0),
        ("SIGN_MadameCama_Mantralaya", Vector((-1050.0, 480.0, 7.25)), 0.15),
        ("SIGN_ApolloBunder_GatewayPlaza", Vector((165.0, -170.0, 4.2)), 0.5),
        ("SIGN_ColabaCauseway_RegalCircle", Vector((80.0, -210.0, 4.3)), 0.0),
        ("SIGN_WorliSeaFace_AcharyaAtre", Vector((-1040.0, 7150.0, 14.1)), 0.0),
    ]

    bm_signs = bmesh.new()
    for name, loc, rot_z in sign_locations:
        rot_mat = Matrix.Rotation(rot_z, 4, 'Z')
        # Cast iron signpost (height 3.2m, radius 0.06m)
        t_post = Matrix.Translation(loc + Vector((0, 0, 1.6))) @ rot_mat
        bmesh.ops.create_cone(bm_signs, cap_ends=True, radius1=0.07, radius2=0.05, depth=3.2, segments=8, matrix=t_post)
        # Decorative finial ball on top
        t_finial = Matrix.Translation(loc + Vector((0, 0, 3.25))) @ rot_mat
        bmesh.ops.create_uvsphere(bm_signs, u_segments=8, v_segments=6, radius=0.09, matrix=t_finial)
        # Sign plate (1.4m wide, 0.45m high, 0.04m thick)
        t_plate = Matrix.Translation(loc + Vector((0.7, 0, 2.75))) @ rot_mat
        bmesh.ops.create_cube(bm_signs, size=1.0, matrix=t_plate @ Matrix.Scale(1.4, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 0, 1))))

    mesh_signs = bpy.data.meshes.new("PROP_MUMBAI_StreetSigns_Mesh")
    bm_signs.to_mesh(mesh_signs)
    bm_signs.free()
    mesh_signs.materials.append(mat_bmcblue)
    obj_signs = bpy.data.objects.new("PROP_MUMBAI_StreetSigns_Master", mesh_signs)
    col_props.objects.link(obj_signs)

    # -----------------------------------------------------------------
    # C. BEST Bus Stop Passenger Shelters
    # -----------------------------------------------------------------
    print("Building authentic BEST transit shelters...")
    shelter_locations = [
        ("SHELTER_MarineDrive_ArtDeco", Vector((-980.0, 980.0, 7.35)), 0.0),
        ("SHELTER_CSMT_Forecourt", Vector((252.0, 1710.0, 13.5)), -0.2),
        ("SHELTER_Churchgate_East", Vector((-855.0, 890.0, 7.4)), 0.0),
        ("SHELTER_MadameCama_Oval", Vector((-1045.0, 520.0, 7.25)), 0.1),
        ("SHELTER_Gateway_Regal", Vector((155.0, -190.0, 4.2)), 0.4),
        ("SHELTER_WorliNaka_Central", Vector((-1035.0, 7220.0, 14.0)), 0.0),
    ]

    bm_shelters = bmesh.new()
    bm_shelter_benches = bmesh.new()
    bm_shelter_totems = bmesh.new()

    for name, loc, rot_z in shelter_locations:
        rot_mat = Matrix.Rotation(rot_z, 4, 'Z')
        # 4 Stainless steel corner columns (height 2.7m)
        col_offsets = [(-2.4, -0.9), (2.4, -0.9), (-2.4, 0.9), (2.4, 0.9)]
        for ox, oy in col_offsets:
            t_col = Matrix.Translation(loc + Vector((ox, oy, 1.35))) @ rot_mat
            bmesh.ops.create_cube(bm_shelters, size=1.0, matrix=t_col @ Matrix.Scale(0.10, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.10, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.7, 4, Vector((0, 0, 1))))

        # Cantilevered Curved Roof Canopy (5.2m wide, 2.2m deep, 0.12m thick)
        t_roof = Matrix.Translation(loc + Vector((0, 0, 2.75))) @ rot_mat
        bmesh.ops.create_cube(bm_shelters, size=1.0, matrix=t_roof @ Matrix.Scale(5.2, 4, Vector((1, 0, 0))) @ Matrix.Scale(2.2, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.12, 4, Vector((0, 0, 1))))

        # Rear Windscreen Panel (4.8m wide, 2.2m high)
        t_wind = Matrix.Translation(loc + Vector((0, 0.9, 1.4))) @ rot_mat
        bmesh.ops.create_cube(bm_shelters, size=1.0, matrix=t_wind @ Matrix.Scale(4.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.04, 4, Vector((0, 1, 0))) @ Matrix.Scale(2.2, 4, Vector((0, 0, 1))))

        # Red Passenger Seating Bench (3.8m wide, 0.5m deep, 0.45m high)
        t_bench = Matrix.Translation(loc + Vector((0, 0.6, 0.25))) @ rot_mat
        bmesh.ops.create_cube(bm_shelter_benches, size=1.0, matrix=t_bench @ Matrix.Scale(3.8, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.5, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.45, 4, Vector((0, 0, 1))))

        # BEST Circular Bus Stop Lollipop Totem Post (Yellow/Red)
        t_totem_pole = Matrix.Translation(loc + Vector((3.0, -0.8, 1.6))) @ rot_mat
        bmesh.ops.create_cone(bm_shelter_totems, cap_ends=True, radius1=0.06, radius2=0.06, depth=3.2, segments=8, matrix=t_totem_pole)
        t_totem_head = Matrix.Translation(loc + Vector((3.0, -0.8, 3.1))) @ rot_mat
        bmesh.ops.create_cone(bm_shelter_totems, cap_ends=True, radius1=0.35, radius2=0.35, depth=0.08, segments=12, matrix=t_totem_head @ Matrix.Rotation(1.5708, 4, 'X'))

    mesh_shelters = bpy.data.meshes.new("PROP_MUMBAI_BEST_Shelters_Mesh")
    bm_shelters.to_mesh(mesh_shelters)
    bm_shelters.free()
    mesh_shelters.materials.append(mat_steelsilver)
    obj_shelters = bpy.data.objects.new("PROP_MUMBAI_BEST_Shelters_Master", mesh_shelters)
    col_props.objects.link(obj_shelters)

    mesh_benches = bpy.data.meshes.new("PROP_MUMBAI_BEST_Benches_Mesh")
    bm_shelter_benches.to_mesh(mesh_benches)
    bm_shelter_benches.free()
    mesh_benches.materials.append(mat_bestred)
    obj_benches = bpy.data.objects.new("PROP_MUMBAI_BEST_Benches_Master", mesh_benches)
    col_props.objects.link(obj_benches)

    mesh_totems = bpy.data.meshes.new("PROP_MUMBAI_BEST_Totems_Mesh")
    bm_shelter_totems.to_mesh(mesh_totems)
    bm_shelter_totems.free()
    mesh_totems.materials.append(mat_bmcyellow)
    obj_totems = bpy.data.objects.new("PROP_MUMBAI_BEST_Totems_Master", mesh_totems)
    col_props.objects.link(obj_totems)

    # -----------------------------------------------------------------
    # D. Traffic Signal Gantries & Cantilevers
    # -----------------------------------------------------------------
    print("Building heavy traffic signal cantilevers...")
    traffic_signal_nodes = [
        ("SIG_MarineDrive_VeerNariman", Vector((-1005.0, 920.0, 7.2)), 0.0),
        ("SIG_MarineDrive_MadameCama", Vector((-1060.0, 480.0, 7.2)), 0.15),
        ("SIG_CSMT_DNDadabhaiJunction", Vector((240.0, 1750.0, 13.8)), -0.2),
        ("SIG_Worli_SeaFace_Junction", Vector((-1350.0, 8500.0, 15.0)), 0.0),
        ("SIG_ApolloBunder_Approach", Vector((175.0, -150.0, 4.2)), 0.4),
    ]

    bm_sig_poles = bmesh.new()
    bm_sig_heads = bmesh.new()
    bm_sig_red = bmesh.new()
    bm_sig_green = bmesh.new()

    for name, loc, rot_z in traffic_signal_nodes:
        rot_mat = Matrix.Rotation(rot_z, 4, 'Z')
        # Vertical mast pole (height 6.5m, radius 0.14m)
        t_mast = Matrix.Translation(loc + Vector((0, 0, 3.25))) @ rot_mat
        bmesh.ops.create_cone(bm_sig_poles, cap_ends=True, radius1=0.15, radius2=0.10, depth=6.5, segments=8, matrix=t_mast)

        # Cantilever outreach arm across lanes (length 7.0m, height 6.2m)
        t_arm = Matrix.Translation(loc + Vector((3.5, 0, 6.3))) @ rot_mat
        bmesh.ops.create_cone(bm_sig_poles, cap_ends=True, radius1=0.08, radius2=0.05, depth=7.0, segments=6, matrix=t_arm @ Matrix.Rotation(1.5708, 4, 'Y'))

        # Signal Head Box 1 (Overhead Lane Signal)
        t_box1 = Matrix.Translation(loc + Vector((5.5, 0, 5.8))) @ rot_mat
        bmesh.ops.create_cube(bm_sig_heads, size=1.0, matrix=t_box1 @ Matrix.Scale(0.35, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.40, 4, Vector((0, 1, 0))) @ Matrix.Scale(1.10, 4, Vector((0, 0, 1))))
        # Red & Green lenses
        bmesh.ops.create_uvsphere(bm_sig_red, u_segments=8, v_segments=6, radius=0.12, matrix=Matrix.Translation(loc + Vector((5.5, -0.22, 6.15))) @ rot_mat)
        bmesh.ops.create_uvsphere(bm_sig_green, u_segments=8, v_segments=6, radius=0.12, matrix=Matrix.Translation(loc + Vector((5.5, -0.22, 5.45))) @ rot_mat)

        # Signal Head Box 2 (Kerbside Pedestrian & Vehicle Signal at 2.8m height)
        t_box2 = Matrix.Translation(loc + Vector((0.35, 0, 2.8))) @ rot_mat
        bmesh.ops.create_cube(bm_sig_heads, size=1.0, matrix=t_box2 @ Matrix.Scale(0.32, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.35, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.95, 4, Vector((0, 0, 1))))
        bmesh.ops.create_uvsphere(bm_sig_red, u_segments=8, v_segments=6, radius=0.10, matrix=Matrix.Translation(loc + Vector((0.35, -0.20, 3.1))) @ rot_mat)
        bmesh.ops.create_uvsphere(bm_sig_green, u_segments=8, v_segments=6, radius=0.10, matrix=Matrix.Translation(loc + Vector((0.35, -0.20, 2.5))) @ rot_mat)

    mesh_sig_poles = bpy.data.meshes.new("PROP_MUMBAI_TrafficSignals_Poles_Mesh")
    bm_sig_poles.to_mesh(mesh_sig_poles)
    bm_sig_poles.free()
    mesh_sig_poles.materials.append(mat_steelsilver)
    obj_sig_poles = bpy.data.objects.new("PROP_MUMBAI_TrafficSignals_Poles_Master", mesh_sig_poles)
    col_props.objects.link(obj_sig_poles)

    mesh_sig_heads = bpy.data.meshes.new("PROP_MUMBAI_TrafficSignals_Heads_Mesh")
    bm_sig_heads.to_mesh(mesh_sig_heads)
    bm_sig_heads.free()
    mesh_sig_heads.materials.append(mat_castiron)
    obj_sig_heads = bpy.data.objects.new("PROP_MUMBAI_TrafficSignals_Heads_Master", mesh_sig_heads)
    col_props.objects.link(obj_sig_heads)

    mesh_sig_red = bpy.data.meshes.new("PROP_MUMBAI_TrafficSignals_Lenses_Red_Mesh")
    bm_sig_red.to_mesh(mesh_sig_red)
    bm_sig_red.free()
    mesh_sig_red.materials.append(mat_signalred)
    obj_sig_red = bpy.data.objects.new("PROP_MUMBAI_TrafficSignals_Lenses_Red_Master", mesh_sig_red)
    col_props.objects.link(obj_sig_red)

    mesh_sig_green = bpy.data.meshes.new("PROP_MUMBAI_TrafficSignals_Lenses_Green_Mesh")
    bm_sig_green.to_mesh(mesh_sig_green)
    bm_sig_green.free()
    mesh_sig_green.materials.append(mat_signalgreen)
    obj_sig_green = bpy.data.objects.new("PROP_MUMBAI_TrafficSignals_Lenses_Green_Master", mesh_sig_green)
    col_props.objects.link(obj_sig_green)

    # -----------------------------------------------------------------
    # E. BMC Yellow & Black Tubular Steel Pedestrian Guard Railings
    # -----------------------------------------------------------------
    print("Building BMC pedestrian safety guard railings...")
    railing_zones = [
        # Marine Drive crosswalk corner
        (Vector((-995.0, 910.0, 7.35)), 18.0, 0.0),
        # CSMT pedestrian perimeter
        (Vector((242.0, 1695.0, 13.5)), 24.0, -0.2),
        # Churchgate station exit
        (Vector((-860.0, 905.0, 7.4)), 16.0, 0.0),
        # Gateway approach curb
        (Vector((170.0, -160.0, 4.2)), 20.0, 0.45),
    ]

    bm_railings = bmesh.new()
    for base_loc, span_length, rot_z in railing_zones:
        rot_mat = Matrix.Rotation(rot_z, 4, 'Z')
        posts_count = int(span_length / 1.8) + 1
        for p_idx in range(posts_count):
            p_offset = Vector((p_idx * 1.8, 0, 0.5))
            t_post = Matrix.Translation(base_loc + rot_mat @ p_offset)
            bmesh.ops.create_cone(bm_railings, cap_ends=True, radius1=0.04, radius2=0.04, depth=1.0, segments=6, matrix=t_post)

        # Upper & Lower horizontal tubes (heights 0.9m and 0.45m)
        t_top_tube = Matrix.Translation(base_loc + rot_mat @ Vector((span_length / 2.0, 0, 0.95))) @ rot_mat @ Matrix.Rotation(1.5708, 4, 'Y')
        bmesh.ops.create_cone(bm_railings, cap_ends=True, radius1=0.035, radius2=0.035, depth=span_length, segments=6, matrix=t_top_tube)
        t_mid_tube = Matrix.Translation(base_loc + rot_mat @ Vector((span_length / 2.0, 0, 0.50))) @ rot_mat @ Matrix.Rotation(1.5708, 4, 'Y')
        bmesh.ops.create_cone(bm_railings, cap_ends=True, radius1=0.035, radius2=0.035, depth=span_length, segments=6, matrix=t_mid_tube)

    mesh_railings = bpy.data.meshes.new("PROP_MUMBAI_Pedestrian_Railings_Mesh")
    bm_railings.to_mesh(mesh_railings)
    bm_railings.free()
    mesh_railings.materials.append(mat_bmcyellow)
    obj_railings = bpy.data.objects.new("PROP_MUMBAI_Pedestrian_Railings_Master", mesh_railings)
    col_props.objects.link(obj_railings)

    # -----------------------------------------------------------------
    # F. Colonial Red Fire Hydrants & Round Indian Post Pillar Boxes
    # -----------------------------------------------------------------
    print("Building heritage fire hydrants and cylindrical post boxes...")
    hydrant_locations = [
        Vector((238.0, 1675.0, 13.5)), # Fort / CSMT
        Vector((210.0, 1550.0, 13.0)), # Ballard Estate
        Vector((160.0, -175.0, 4.2)),  # Apollo Bunder
        Vector((95.0, -220.0, 4.3)),   # Colaba
    ]
    bm_hydrants = bmesh.new()
    for h_loc in hydrant_locations:
        # Base fluted column
        t_base = Matrix.Translation(h_loc + Vector((0, 0, 0.4)))
        bmesh.ops.create_cone(bm_hydrants, cap_ends=True, radius1=0.18, radius2=0.14, depth=0.8, segments=8, matrix=t_base)
        # Domed top cap
        t_dome = Matrix.Translation(h_loc + Vector((0, 0, 0.85)))
        bmesh.ops.create_uvsphere(bm_hydrants, u_segments=8, v_segments=6, radius=0.14, matrix=t_dome)
        # Twin horizontal brass valve outlets
        t_valve = Matrix.Translation(h_loc + Vector((0, 0, 0.55))) @ Matrix.Rotation(1.5708, 4, 'X')
        bmesh.ops.create_cone(bm_hydrants, cap_ends=True, radius1=0.06, radius2=0.06, depth=0.45, segments=6, matrix=t_valve)

    mesh_hydrants = bpy.data.meshes.new("PROP_MUMBAI_FireHydrants_Mesh")
    bm_hydrants.to_mesh(mesh_hydrants)
    bm_hydrants.free()
    mesh_hydrants.materials.append(mat_postred)
    obj_hydrants = bpy.data.objects.new("PROP_MUMBAI_FireHydrants_Master", mesh_hydrants)
    col_props.objects.link(obj_hydrants)

    postbox_locations = [
        Vector((248.0, 1690.0, 13.5)), # Fort
        Vector((-978.0, 915.0, 7.35)), # Marine Drive / Veer Nariman
        Vector((170.0, -165.0, 4.2)),  # Gateway of India
        Vector((-845.0, 895.0, 7.4)),  # Churchgate
    ]
    bm_postboxes = bmesh.new()
    for p_loc in postbox_locations:
        # Circular cylinder body (height 1.35m, radius 0.28m)
        t_cyl = Matrix.Translation(p_loc + Vector((0, 0, 0.65)))
        bmesh.ops.create_cone(bm_postboxes, cap_ends=True, radius1=0.28, radius2=0.28, depth=1.3, segments=12, matrix=t_cyl)
        # Domed top with imperial crest crown
        t_p_dome = Matrix.Translation(p_loc + Vector((0, 0, 1.35)))
        bmesh.ops.create_uvsphere(bm_postboxes, u_segments=12, v_segments=8, radius=0.28, matrix=t_p_dome)

    mesh_postboxes = bpy.data.meshes.new("PROP_MUMBAI_IndiaPost_Boxes_Mesh")
    bm_postboxes.to_mesh(mesh_postboxes)
    bm_postboxes.free()
    mesh_postboxes.materials.append(mat_postred)
    obj_postboxes = bpy.data.objects.new("PROP_MUMBAI_IndiaPost_Boxes_Master", mesh_postboxes)
    col_props.objects.link(obj_postboxes)

    # -----------------------------------------------------------------
    # G. BMC Segregated Dustbins (Green / Blue Pairs)
    # -----------------------------------------------------------------
    print("Building BMC segregated municipal public litter bins...")
    bin_locations = [
        Vector((-1025.0, 850.0, 7.35)),  # Marine Drive promenade
        Vector((-1010.0, 1150.0, 7.35)), # Marine Drive promenade
        Vector((-990.0, 1450.0, 7.35)),  # Marine Drive promenade
        Vector((244.0, 1720.0, 13.5)),   # CSMT sidewalk
        Vector((180.0, -170.0, 4.2)),    # Gateway plaza edge
        Vector((-852.0, 930.0, 7.4)),    # Churchgate
    ]
    bm_bins_green = bmesh.new()
    bm_bins_blue = bmesh.new()
    bm_bin_frames = bmesh.new()

    for b_loc in bin_locations:
        # Central support post & cross frame
        t_frame = Matrix.Translation(b_loc + Vector((0, 0, 0.5)))
        bmesh.ops.create_cone(bm_bin_frames, cap_ends=True, radius1=0.035, radius2=0.035, depth=1.0, segments=6, matrix=t_frame)
        t_bar = Matrix.Translation(b_loc + Vector((0, 0, 0.75))) @ Matrix.Rotation(1.5708, 4, 'X')
        bmesh.ops.create_cone(bm_bin_frames, cap_ends=True, radius1=0.025, radius2=0.025, depth=0.8, segments=6, matrix=t_bar)

        # Green Can (Wet waste)
        t_green = Matrix.Translation(b_loc + Vector((0, -0.28, 0.7)))
        bmesh.ops.create_cone(bm_bins_green, cap_ends=True, radius1=0.18, radius2=0.16, depth=0.7, segments=10, matrix=t_green)

        # Blue Can (Dry waste)
        t_blue = Matrix.Translation(b_loc + Vector((0, 0.28, 0.7)))
        bmesh.ops.create_cone(bm_bins_blue, cap_ends=True, radius1=0.18, radius2=0.16, depth=0.7, segments=10, matrix=t_blue)

    mesh_bins_green = bpy.data.meshes.new("PROP_MUMBAI_Dustbins_Green_Mesh")
    bm_bins_green.to_mesh(mesh_bins_green)
    bm_bins_green.free()
    mesh_bins_green.materials.append(mat_bin_green)
    obj_bins_green = bpy.data.objects.new("PROP_MUMBAI_Dustbins_Green_Master", mesh_bins_green)
    col_props.objects.link(obj_bins_green)

    mesh_bins_blue = bpy.data.meshes.new("PROP_MUMBAI_Dustbins_Blue_Mesh")
    bm_bins_blue.to_mesh(mesh_bins_blue)
    bm_bins_blue.free()
    mesh_bins_blue.materials.append(mat_bin_blue)
    obj_bins_blue = bpy.data.objects.new("PROP_MUMBAI_Dustbins_Blue_Master", mesh_bins_blue)
    col_props.objects.link(obj_bins_blue)

    mesh_bin_frames = bpy.data.meshes.new("PROP_MUMBAI_Dustbins_Frames_Mesh")
    bm_bin_frames.to_mesh(mesh_bin_frames)
    bm_bin_frames.free()
    mesh_bin_frames.materials.append(mat_steelsilver)
    obj_bin_frames = bpy.data.objects.new("PROP_MUMBAI_Dustbins_Frames_Master", mesh_bin_frames)
    col_props.objects.link(obj_bin_frames)

    # -----------------------------------------------------------------
    # H. Apollo Bunder Gateway Basalt Plaza Bollards
    # -----------------------------------------------------------------
    print("Building Gateway of India ceremonial basalt bollards...")
    bm_bollards = bmesh.new()
    bollard_count = 28
    for b_i in range(bollard_count):
        bx = 60.0 + b_i * 6.0
        by = -155.0
        bz = 4.2
        t_boll = Matrix.Translation(Vector((bx, by, bz + 0.45)))
        bmesh.ops.create_cone(bm_bollards, cap_ends=True, radius1=0.22, radius2=0.19, depth=0.9, segments=8, matrix=t_boll)
        t_boll_cap = Matrix.Translation(Vector((bx, by, bz + 0.95)))
        bmesh.ops.create_uvsphere(bm_bollards, u_segments=8, v_segments=6, radius=0.19, matrix=t_boll_cap)

    mesh_bollards = bpy.data.meshes.new("PROP_MUMBAI_Basalt_Bollards_Mesh")
    bm_bollards.to_mesh(mesh_bollards)
    bm_bollards.free()
    mesh_bollards.materials.append(mat_basalt_bollard)
    obj_bollards = bpy.data.objects.new("PROP_MUMBAI_Basalt_Bollards_Master", mesh_bollards)
    col_props.objects.link(obj_bollards)

    total_props_objects = len(col_props.objects)
    print(f"\nSuccessfully generated {total_props_objects} unified street-level prop master objects in '{target_col_name}'!")
    return f"Street furniture & props completed successfully ({total_props_objects} master systems, 0 living entities)."

if __name__ == "__main__":
    msg = build_street_props()
    print(msg)
