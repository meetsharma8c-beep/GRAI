#!/usr/bin/env python3
"""
test_anatomical_sculpt.py
=========================
Generates organic anatomical geometry with muscle flow and realistic clothing,
and renders a test view to verify the visual transformation.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

def run_test():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    root_empty = bpy.data.objects.get("Character_Raghunath_Root")

    # Clean previous body and clothing
    cleanup = ["Raghunath_Body_Mesh", "Raghunath_Shirt_Mesh", "Raghunath_Jeans_Mesh",
               "Raghunath_Shirt_Pocket", "Raghunath_Necklace_Cord", "Raghunath_Pendant"]
    for name in cleanup:
        o = bpy.data.objects.get(name)
        if o: bpy.data.objects.remove(o, do_unlink=True)

    # Clean orphan meshes
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)

    # 1. MATERIALS WITH RICH SATURATED PALETTE
    mat_skin = bpy.data.materials.get("M_Raghunath_Skin_PBR")
    if mat_skin and mat_skin.node_tree:
        bsdf = mat_skin.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.45, 0.28, 0.20, 1.0) # Deep warm South Asian melanin
            bsdf.inputs['Roughness'].default_value = 0.44

    mat_shirt = bpy.data.materials.get("M_Raghunath_Shirt_Burgundy")
    if mat_shirt and mat_shirt.node_tree:
        bsdf = mat_shirt.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            # Rich deep crimson/burgundy (NOT pink!)
            bsdf.inputs['Base Color'].default_value = (0.12, 0.010, 0.022, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.82

    mat_jeans = bpy.data.materials.get("M_Raghunath_Jeans_Charcoal")
    if mat_jeans and mat_jeans.node_tree:
        bsdf = mat_jeans.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.016, 0.017, 0.020, 1.0) # Charcoal black
            bsdf.inputs['Roughness'].default_value = 0.88

    mat_neck = bpy.data.materials.get("M_Raghunath_Necklace")

    # 2. ANATOMICAL BODY MESH WITH MUSCLE HARMONICS
    bm_body = bmesh.new()
    N = 32 # 32 points per ring for smooth organic curvature

    # Torso levels: (z, rx, ry, cx, cy, pect_fac, lat_fac)
    torso_levels = [
        (1.578, 0.076, 0.070, 0.0,  0.012, 0.00, 0.00), # Neck top (seamless with head)
        (1.540, 0.082, 0.074, 0.0,  0.006, 0.00, 0.00), # Mid neck
        (1.500, 0.096, 0.082, 0.0, -0.004, 0.01, 0.01), # Base of neck
        (1.460, 0.150, 0.108, 0.0, -0.008, 0.02, 0.02), # Clavicles & Trapezius
        (1.410, 0.192, 0.126, 0.0, -0.006, 0.03, 0.03), # Shoulder girdle
        (1.360, 0.208, 0.138, 0.0,  0.000, 0.04, 0.03), # Upper chest / Deltoid
        (1.300, 0.214, 0.144, 0.0,  0.006, 0.04, 0.02), # Mid chest / Pectorals
        (1.240, 0.205, 0.138, 0.0,  0.004, 0.02, 0.02), # Lower chest
        (1.180, 0.194, 0.128, 0.0,  0.000, 0.01, 0.01), # Ribcage
        (1.120, 0.184, 0.122, 0.0, -0.004, 0.00, 0.00), # Upper abdomen
        (1.060, 0.175, 0.116, 0.0, -0.006, 0.00, 0.00), # Waist taper
        (1.000, 0.182, 0.120, 0.0, -0.006, 0.00, 0.00), # Iliac crest
        (0.940, 0.192, 0.128, 0.0, -0.006, 0.00, 0.01), # Pelvis
        (0.880, 0.198, 0.136, 0.0, -0.005, 0.00, 0.02), # Gluteus
        (0.820, 0.196, 0.136, 0.0, -0.005, 0.00, 0.02), # Lower pelvis
        (0.780, 0.192, 0.132, 0.0, -0.005, 0.00, 0.01)  # Crotch bifurcation
    ]

    t_rings = []
    for z_lvl, rx, ry, cx, cy, p_fac, l_fac in torso_levels:
        ring = []
        for i in range(N):
            th = 2.0 * math.pi * i / N
            # Anatomical shape modulation
            # Pectoral bulge on front (th ~ -pi/2 in our coord sys: y < 0 is front)
            # latissimus on sides/back
            sin_th = math.sin(th)
            cos_th = math.cos(th)
            
            # Pectoral projection at front (sin_th < 0)
            d_p = -p_fac * (sin_th**2) if sin_th < 0 else 0.0
            # Gluteus/lat at back (sin_th > 0)
            d_l = l_fac * (sin_th**2) if sin_th > 0 else 0.0
            
            px = cx + (rx) * cos_th
            py = cy + (ry + d_p + d_l) * sin_th
            ring.append(bm_body.verts.new(Vector((px, py, z_lvl))))
        t_rings.append(ring)

    for r in range(len(t_rings) - 1):
        r1, r2 = t_rings[r], t_rings[r + 1]
        for i in range(N):
            next_i = (i + 1) % N
            bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Legs (Thighs, Knees, Calves, Ankles)
    N_l = 20
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_levels = [
            (0.780, 0.096, 0.096, sign * 0.100, -0.005),
            (0.710, 0.092, 0.092, sign * 0.102, -0.005),
            (0.640, 0.086, 0.086, sign * 0.105, -0.003),
            (0.570, 0.080, 0.080, sign * 0.106, -0.002),
            # Knee
            (0.510, 0.068, 0.072, sign * 0.105,  0.005),
            (0.470, 0.065, 0.068, sign * 0.105,  0.002),
            # Calf
            (0.400, 0.074, 0.076, sign * 0.105, -0.008),
            (0.330, 0.068, 0.070, sign * 0.105, -0.006),
            (0.260, 0.058, 0.058, sign * 0.104, -0.003),
            # Lower shin
            (0.180, 0.046, 0.046, sign * 0.102,  0.000),
            (0.120, 0.040, 0.040, sign * 0.100,  0.000),
            # Ankle
            (0.085, 0.038, 0.042, sign * 0.100,  0.000)
        ]
        l_rings = []
        for z_lvl, rx, ry, cx, cy in leg_levels:
            ring = []
            for i in range(N_l):
                th = 2.0 * math.pi * i / N_l
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                ring.append(bm_body.verts.new(Vector((px, py, z_lvl))))
            l_rings.append(ring)
        for r in range(len(l_rings) - 1):
            r1, r2 = l_rings[r], l_rings[r + 1]
            for i in range(N_l):
                next_i = (i + 1) % N_l
                bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Arms with Deltoid shoulder curve, A-pose angle, and natural taper
    N_a = 20
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        arm_levels = [
            # Shoulder transition
            (1.400, sign * 0.185, -0.005, 0.076, 0.076),
            (1.350, sign * 0.215, -0.005, 0.070, 0.070),
            (1.290, sign * 0.235, -0.008, 0.064, 0.064),
            (1.220, sign * 0.246, -0.010, 0.058, 0.058),
            # Elbow
            (1.160, sign * 0.252, -0.012, 0.052, 0.052),
            (1.100, sign * 0.254, -0.012, 0.050, 0.050),
            # Forearm
            (1.040, sign * 0.252, -0.010, 0.050, 0.048),
            (0.970, sign * 0.248, -0.008, 0.044, 0.042),
            # Wrist
            (0.910, sign * 0.242, -0.005, 0.038, 0.034),
            (0.860, sign * 0.236, -0.005, 0.034, 0.030)
        ]
        a_rings = []
        for z_lvl, cx, cy, rx, ry in arm_levels:
            ring = []
            for i in range(N_a):
                th = 2.0 * math.pi * i / N_a
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                ring.append(bm_body.verts.new(Vector((px, py, z_lvl))))
            a_rings.append(ring)
        for r in range(len(a_rings) - 1):
            r1, r2 = a_rings[r], a_rings[r + 1]
            for i in range(N_a):
                next_i = (i + 1) % N_a
                bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Hands (5 articulated fingers)
    finger_defs = [
        ("thumb",  -0.018, -0.018, 0.045, 0.0105),
        ("index",  -0.014,  0.000, 0.062, 0.0090),
        ("middle", -0.002,  0.000, 0.068, 0.0095),
        ("ring",    0.010,  0.000, 0.064, 0.0090),
        ("pinky",   0.021,  0.000, 0.052, 0.0080)
    ]
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        palm_center = Vector((sign * 0.236, -0.005, 0.825))
        p_verts = []
        for dx in [-0.028, -0.014, 0.0, 0.014, 0.028]:
            for dy in [-0.016, 0.016]:
                for dz in [0.035, -0.025]:
                    p_verts.append(bm_body.verts.new(palm_center + Vector((sign * dx, dy, dz))))

        for f_name, fx, fy, f_len, f_rad in finger_defs:
            f_base = palm_center + Vector((sign * fx, fy, -0.025))
            f_rings = []
            ph_count = 3
            for ph in range(ph_count + 1):
                f_z = f_base.z - (f_len * ph / ph_count)
                f_y = f_base.y - (0.015 * (ph / ph_count)**2)
                rad = f_rad * (1.0 - 0.22 * (ph / ph_count))
                ring = []
                for s in range(8):
                    th = 2.0 * math.pi * s / 8.0
                    px = f_base.x + sign * (rad * math.cos(th))
                    py = f_y + rad * math.sin(th)
                    ring.append(bm_body.verts.new(Vector((px, py, f_z))))
                f_rings.append(ring)
            for r in range(len(f_rings) - 1):
                r1, r2 = f_rings[r], f_rings[r + 1]
                for s in range(8):
                    next_s = (s + 1) % 8
                    bm_body.faces.new([r1[s], r1[next_s], r2[next_s], r2[s]])

    # Feet (5 articulated toes)
    toe_defs = [
        ("big_toe",  0.018, 0.040, 0.011),
        ("toe_2",    0.006, 0.038, 0.009),
        ("toe_3",   -0.005, 0.035, 0.0085),
        ("toe_4",   -0.015, 0.031, 0.008),
        ("pinky_toe",-0.024, 0.026, 0.0075)
    ]
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        foot_center = Vector((sign * 0.100, 0.030, 0.045))
        ft_rings = []
        for y_sec, r_wd, r_ht, z_sec in [
            (-0.080, 0.034, 0.038, 0.045),
            (-0.030, 0.032, 0.032, 0.042),
            ( 0.020, 0.042, 0.028, 0.038),
            ( 0.070, 0.046, 0.022, 0.032)
        ]:
            ring = []
            for s in range(12):
                th = 2.0 * math.pi * s / 12.0
                px = foot_center.x + sign * (r_wd * math.cos(th))
                pz = z_sec + r_ht * math.sin(th)
                ring.append(bm_body.verts.new(Vector((px, foot_center.y + y_sec, pz))))
            ft_rings.append(ring)
        for r in range(len(ft_rings) - 1):
            r1, r2 = ft_rings[r], ft_rings[r + 1]
            for s in range(12):
                next_s = (s + 1) % 12
                bm_body.faces.new([r1[s], r1[next_s], r2[next_s], r2[s]])

        for t_name, tx, t_len, t_rad in toe_defs:
            t_base = Vector((foot_center.x + sign * tx, foot_center.y + 0.070, 0.032))
            t_rings = []
            for seg in [0.0, 0.5, 1.0]:
                ty = t_base.y + (t_len * seg)
                rad = t_rad * (1.0 - 0.20 * seg)
                ring = []
                for s in range(8):
                    th = 2.0 * math.pi * s / 8.0
                    px = t_base.x + sign * (rad * math.cos(th))
                    pz = t_base.z + (rad * math.sin(th))
                    ring.append(bm_body.verts.new(Vector((px, ty, pz))))
                t_rings.append(ring)
            for r in range(len(t_rings) - 1):
                r1, r2 = t_rings[r], t_rings[r + 1]
                for s in range(8):
                    next_s = (s + 1) % 8
                    bm_body.faces.new([r1[s], r1[next_s], r2[next_s], r2[s]])

    body_mesh_data = bpy.data.meshes.new("Raghunath_Body_Mesh_Data")
    bm_body.to_mesh(body_mesh_data)
    bm_body.free()

    body_obj = bpy.data.objects.new("Raghunath_Body_Mesh", body_mesh_data)
    col.objects.link(body_obj)
    body_obj.parent = root_empty
    body_obj.data.materials.append(mat_skin)
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.shade_smooth()
    mod_sub_b = body_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub_b.levels = 1

    # 3. REALISTIC CONFORMING SHIRT (Realistic Shoulder Slope, Continuous Sleeves, Drape)
    bm_shirt = bmesh.new()
    N_s = 32

    # Torso shirt levels
    shirt_levels = [
        # (z, rx, ry, cx, cy)
        (1.575, 0.082, 0.076, 0.0,  0.010), # Collar stand meeting neck
        (1.540, 0.092, 0.082, 0.0,  0.005), # Collar mid
        (1.500, 0.118, 0.098, 0.0, -0.005), # Collar base & neck notch
        (1.460, 0.170, 0.122, 0.0, -0.008), # Shoulder slope
        (1.410, 0.208, 0.138, 0.0, -0.005), # Shoulder yoke
        (1.360, 0.224, 0.148, 0.0,  0.000), # Upper chest
        (1.300, 0.228, 0.154, 0.0,  0.006), # Pectorals / Chest
        (1.240, 0.220, 0.150, 0.0,  0.005), # Mid chest
        (1.180, 0.210, 0.142, 0.0,  0.000), # Ribcage
        (1.120, 0.200, 0.136, 0.0, -0.003), # Upper waist
        (1.060, 0.192, 0.130, 0.0, -0.005), # Waist taper
        (1.000, 0.198, 0.136, 0.0, -0.005), # Lower waist
        (0.950, 0.208, 0.145, 0.0, -0.005), # Hem flare
        (0.910, 0.216, 0.152, 0.0, -0.005)  # Bottom hem line
    ]

    s_rings = []
    for z_lvl, rx, ry, cx, cy in shirt_levels:
        ring = []
        for i in range(N_s):
            th = 2.0 * math.pi * i / N_s
            ripple = 0.004 * math.sin(6.0 * th)
            px = cx + (rx + ripple) * math.cos(th)
            py = cy + (ry + ripple) * math.sin(th)
            # Open V-neck in front (y < -0.03, z > 1.48)
            if z_lvl > 1.48 and py < -0.03:
                py += 0.024 * ((z_lvl - 1.48) / 0.095)
            ring.append(bm_shirt.verts.new(Vector((px, py, z_lvl))))
        s_rings.append(ring)

    for r in range(len(s_rings) - 1):
        r1, r2 = s_rings[r], s_rings[r + 1]
        for i in range(N_s):
            next_i = (i + 1) % N_s
            bm_shirt.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # 3/4 Sleeves with folded cuffs
    N_sl = 20
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        sleeve_levels = [
            (1.410, sign * 0.195, -0.005, 0.084, 0.084),
            (1.350, sign * 0.225, -0.005, 0.078, 0.078),
            (1.290, sign * 0.245, -0.008, 0.072, 0.072),
            (1.220, sign * 0.255, -0.010, 0.068, 0.068),
            (1.170, sign * 0.260, -0.012, 0.065, 0.065),
            # Folded cuff rim
            (1.140, sign * 0.262, -0.012, 0.070, 0.070),
            (1.130, sign * 0.262, -0.012, 0.066, 0.066)
        ]
        sl_rings = []
        for z_lvl, cx, cy, rx, ry in sleeve_levels:
            ring = []
            for i in range(N_sl):
                th = 2.0 * math.pi * i / N_sl
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                ring.append(bm_shirt.verts.new(Vector((px, py, z_lvl))))
            sl_rings.append(ring)
        for r in range(len(sl_rings) - 1):
            r1, r2 = sl_rings[r], sl_rings[r + 1]
            for i in range(N_sl):
                next_i = (i + 1) % N_sl
                bm_shirt.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    shirt_data = bpy.data.meshes.new("Raghunath_Shirt_Mesh_Data")
    bm_shirt.to_mesh(shirt_data)
    bm_shirt.free()

    shirt_obj = bpy.data.objects.new("Raghunath_Shirt_Mesh", shirt_data)
    col.objects.link(shirt_obj)
    shirt_obj.parent = root_empty
    shirt_obj.data.materials.append(mat_shirt)
    bpy.context.view_layer.objects.active = shirt_obj
    bpy.ops.object.shade_smooth()
    mod_solid = shirt_obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod_solid.thickness = 0.003
    mod_sub_s = shirt_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub_s.levels = 1

    # Left chest pocket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.085, -0.155, 1.300))
    pocket = bpy.context.active_object
    pocket.name = "Raghunath_Shirt_Pocket"
    col.objects.link(pocket)
    if pocket.name in scene.collection.objects: scene.collection.objects.unlink(pocket)
    pocket.parent = root_empty
    pocket.scale = (0.045, 0.005, 0.055)
    bpy.ops.object.transform_apply(scale=True)
    pocket.data.materials.append(mat_shirt)

    # 4. CONFORMING SLIM-FIT CHARCOAL DENIM JEANS
    bm_jeans = bmesh.new()
    N_j = 32
    jeans_torso_levels = [
        (0.960, 0.200, 0.136, 0.0, -0.005), # Waistband sitting under shirt
        (0.910, 0.204, 0.140, 0.0, -0.005), # Hips
        (0.850, 0.206, 0.142, 0.0, -0.005), # Gluteal line
        (0.790, 0.200, 0.138, 0.0, -0.005)  # Inseam crotch level
    ]
    j_rings = []
    for z_lvl, rx, ry, cx, cy in jeans_torso_levels:
        ring = []
        for i in range(N_j):
            th = 2.0 * math.pi * i / N_j
            px = cx + rx * math.cos(th)
            py = cy + ry * math.sin(th)
            ring.append(bm_jeans.verts.new(Vector((px, py, z_lvl))))
        j_rings.append(ring)

    for r in range(len(j_rings) - 1):
        r1, r2 = j_rings[r], j_rings[r + 1]
        for i in range(N_j):
            next_i = (i + 1) % N_j
            bm_jeans.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Jeans legs with knee crease ripples and ankle cuff stack
    N_jl = 20
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        j_leg_levels = [
            (0.790, sign * 0.100, -0.005, 0.102, 0.102),
            (0.720, sign * 0.102, -0.005, 0.096, 0.096),
            (0.650, sign * 0.105, -0.003, 0.090, 0.091),
            (0.580, sign * 0.106, -0.002, 0.084, 0.085),
            # Knee folds
            (0.520, sign * 0.105, 0.005, 0.076, 0.078),
            (0.470, sign * 0.105, 0.002, 0.074, 0.076),
            # Calves
            (0.400, sign * 0.105, -0.006, 0.078, 0.080),
            (0.330, sign * 0.104, -0.004, 0.072, 0.074),
            (0.250, sign * 0.103, -0.002, 0.062, 0.062),
            # Ankle cuff stack
            (0.170, sign * 0.102, 0.000, 0.054, 0.054),
            (0.120, sign * 0.100, 0.000, 0.056, 0.056),
            (0.090, sign * 0.100, 0.000, 0.052, 0.054)
        ]
        jl_rings = []
        for z_lvl, cx, cy, rx, ry in j_leg_levels:
            ring = []
            for i in range(N_jl):
                th = 2.0 * math.pi * i / N_jl
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                ring.append(bm_jeans.verts.new(Vector((px, py, z_lvl))))
            jl_rings.append(ring)
        for r in range(len(jl_rings) - 1):
            r1, r2 = jl_rings[r], jl_rings[r + 1]
            for i in range(N_jl):
                next_i = (i + 1) % N_jl
                bm_jeans.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    jeans_data = bpy.data.meshes.new("Raghunath_Jeans_Mesh_Data")
    bm_jeans.to_mesh(jeans_data)
    bm_jeans.free()

    jeans_obj = bpy.data.objects.new("Raghunath_Jeans_Mesh", jeans_data)
    col.objects.link(jeans_obj)
    jeans_obj.parent = root_empty
    jeans_obj.data.materials.append(mat_jeans)
    bpy.context.view_layer.objects.active = jeans_obj
    bpy.ops.object.shade_smooth()
    mod_solid_j = jeans_obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod_solid_j.thickness = 0.003
    mod_sub_j = jeans_obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub_j.levels = 1

    # 5. CORD NECKLACE & BRASS PENDANT
    bpy.ops.mesh.primitive_torus_add(major_radius=0.088, minor_radius=0.0035,
                                     major_segments=36, minor_segments=8,
                                     location=(0.0, -0.015, 1.490))
    neck_cord = bpy.context.active_object
    neck_cord.name = "Raghunath_Necklace_Cord"
    col.objects.link(neck_cord)
    if neck_cord.name in scene.collection.objects: scene.collection.objects.unlink(neck_cord)
    neck_cord.parent = root_empty
    neck_cord.rotation_euler = Euler((math.radians(20.0), 0.0, 0.0), 'XYZ')
    bpy.ops.object.transform_apply(rotation=True)
    neck_cord.data.materials.append(mat_neck)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.009,
                                         location=(0.0, -0.100, 1.440))
    pendant = bpy.context.active_object
    pendant.name = "Raghunath_Pendant"
    col.objects.link(pendant)
    if pendant.name in scene.collection.objects: scene.collection.objects.unlink(pendant)
    pendant.parent = root_empty
    pendant.scale = (0.75, 0.40, 1.40)
    bpy.ops.object.transform_apply(scale=True)
    pendant.data.materials.append(mat_neck)

    # 6. SKINNING
    arm_obj = bpy.data.objects.get("Armature_Raghunath")
    bone_names = [b.name for b in arm_obj.data.bones] if arm_obj else []

    for o in [body_obj, shirt_obj, pocket, jeans_obj, neck_cord, pendant]:
        if not o or not arm_obj: continue
        arm_mod = o.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = arm_obj
        for bname in bone_names:
            o.vertex_groups.new(name=bname)
        for v in o.data.vertices:
            v_co = v.co
            weights = {}
            for b in arm_obj.data.bones:
                mid = (b.head_local + b.tail_local) * 0.5
                dist = (v_co - mid).length
                w = 1.0 / max(dist**2, 0.001)
                weights[b.name] = w
            sorted_weights = sorted(weights.items(), key=lambda item: item[1], reverse=True)[:4]
            tot_w = sum(w for _, w in sorted_weights)
            for bname, w in sorted_weights:
                norm_w = w / tot_w
                if norm_w > 0.01:
                    o.vertex_groups[bname].add([v.index], norm_w, 'REPLACE')

    # UV unwrap
    for o in [body_obj, shirt_obj, pocket, jeans_obj, neck_cord, pendant]:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        if not o.data.uv_layers: o.data.uv_layers.new(name="UVMap")
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')

    # Save
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Test build complete, blend file saved.")

if __name__ == '__main__':
    run_test()
