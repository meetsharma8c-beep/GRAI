#!/usr/bin/env python3
"""
test_oriented_anatomy.py
========================
Tests the new oriented anatomical arm/sleeve geometry and balanced materials.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

def run():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    root_empty = bpy.data.objects.get("Character_Raghunath_Root")

    # Clean old body and clothing
    cleanup = ["Raghunath_Body_Mesh", "Raghunath_Shirt_Mesh", "Raghunath_Jeans_Mesh",
               "Raghunath_Shirt_Pocket", "Raghunath_Necklace_Cord", "Raghunath_Pendant"]
    for name in cleanup:
        o = bpy.data.objects.get(name)
        if o: bpy.data.objects.remove(o, do_unlink=True)

    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)

    mat_skin = bpy.data.materials.get("M_Raghunath_Skin_PBR")
    mat_shirt = bpy.data.materials.get("M_Raghunath_Shirt_Burgundy")
    mat_jeans = bpy.data.materials.get("M_Raghunath_Jeans_Charcoal")
    mat_leather = bpy.data.materials.get("M_Raghunath_Leather_Sandals")
    mat_sole = bpy.data.materials.get("M_Raghunath_Sandal_Sole")
    mat_neck = bpy.data.materials.get("M_Raghunath_Necklace")

    # 1. BODY MESH WITH ORIENTED ARMS
    bm_body = bmesh.new()
    N_t = 28

    # Torso
    torso_levels = [
        # (z, rx, ry, cx, cy)
        (1.578, 0.076, 0.070, 0.0,  0.012), # Neck top (welds to head base)
        (1.540, 0.082, 0.074, 0.0,  0.006), # Mid neck
        (1.500, 0.096, 0.082, 0.0, -0.004), # Base of neck / Jugular notch
        (1.460, 0.150, 0.108, 0.0, -0.008), # Clavicles & Trapezius
        (1.410, 0.192, 0.126, 0.0, -0.006), # Shoulder girdle
        (1.360, 0.208, 0.138, 0.0,  0.000), # Upper pectorals
        (1.300, 0.214, 0.144, 0.0,  0.006), # Mid pectorals
        (1.240, 0.205, 0.138, 0.0,  0.004), # Lower ribcage
        (1.180, 0.194, 0.128, 0.0,  0.000), # Epigastrium
        (1.120, 0.184, 0.122, 0.0, -0.004), # Upper waist
        (1.060, 0.175, 0.116, 0.0, -0.006), # Navel / Waist taper
        (1.000, 0.182, 0.120, 0.0, -0.006), # Iliac crest / Belt line
        (0.940, 0.192, 0.128, 0.0, -0.006), # Pelvis
        (0.880, 0.198, 0.136, 0.0, -0.005), # Gluteus
        (0.820, 0.196, 0.136, 0.0, -0.005), # Lower pelvis
        (0.780, 0.192, 0.132, 0.0, -0.005)  # Inseam crotch
    ]

    t_grid = []
    for z_lvl, rx, ry, cx, cy in torso_levels:
        row = []
        for i in range(N_t):
            th = 2.0 * math.pi * i / N_t
            px = cx + rx * math.cos(th)
            py = cy + ry * math.sin(th)
            row.append(bm_body.verts.new(Vector((px, py, z_lvl))))
        t_grid.append(row)

    for r in range(len(t_grid) - 1):
        r1, r2 = t_grid[r], t_grid[r + 1]
        for i in range(N_t):
            next_i = (i + 1) % N_t
            bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Oriented A-Pose Arms
    N_a = 16
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        # Define 3 key joint positions along arm
        p_shoulder = Vector((sign * 0.185, -0.006, 1.42))
        p_elbow    = Vector((sign * 0.255, -0.012, 1.16))
        p_wrist    = Vector((sign * 0.242, -0.008, 0.90))

        # Upper arm segments (oriented along shoulder->elbow)
        u_vec = (p_elbow - p_shoulder).normalized()
        n1 = Vector((0.0, 1.0, 0.0))
        n2 = u_vec.cross(n1).normalized()

        upper_arm_rings = []
        for s in [0.0, 0.25, 0.50, 0.75, 1.0]:
            center = p_shoulder + s * (p_elbow - p_shoulder)
            rx = 0.075 - 0.024 * s # tapers from 0.075 to 0.051
            ry = 0.075 - 0.024 * s
            ring = []
            for i in range(N_a):
                th = 2.0 * math.pi * i / N_a
                offset = (rx * math.cos(th)) * n2 + (ry * math.sin(th)) * n1
                ring.append(bm_body.verts.new(center + offset))
            upper_arm_rings.append(ring)

        for r in range(len(upper_arm_rings) - 1):
            r1, r2 = upper_arm_rings[r], upper_arm_rings[r + 1]
            for i in range(N_a):
                next_i = (i + 1) % N_a
                bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

        # Forearm segments (oriented along elbow->wrist)
        f_vec = (p_wrist - p_elbow).normalized()
        fn1 = Vector((0.0, 1.0, 0.0))
        fn2 = f_vec.cross(fn1).normalized()

        forearm_rings = [upper_arm_rings[-1]] # continuous from elbow ring
        for s in [0.33, 0.66, 1.0]:
            center = p_elbow + s * (p_wrist - p_elbow)
            rx = 0.050 - 0.016 * s
            ry = 0.048 - 0.016 * s
            ring = []
            for i in range(N_a):
                th = 2.0 * math.pi * i / N_a
                offset = (rx * math.cos(th)) * fn2 + (ry * math.sin(th)) * fn1
                ring.append(bm_body.verts.new(center + offset))
            forearm_rings.append(ring)

        for r in range(len(forearm_rings) - 1):
            r1, r2 = forearm_rings[r], forearm_rings[r + 1]
            for i in range(N_a):
                next_i = (i + 1) % N_a
                bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

        # Articulated 5-Finger Hands
        palm_center = p_wrist + Vector((0, 0, -0.065))
        for dx in [-0.024, -0.012, 0.0, 0.012, 0.024]:
            for dy in [-0.014, 0.014]:
                for dz in [0.030, -0.020]:
                    bm_body.verts.new(palm_center + Vector((sign * dx, dy, dz)))

        finger_defs = [
            ("thumb",  -0.016, -0.016, 0.045, 0.010),
            ("index",  -0.012,  0.000, 0.060, 0.0085),
            ("middle", -0.002,  0.000, 0.066, 0.0090),
            ("ring",    0.010,  0.000, 0.062, 0.0085),
            ("pinky",   0.020,  0.000, 0.050, 0.0075)
        ]
        for f_name, fx, fy, f_len, f_rad in finger_defs:
            f_base = palm_center + Vector((sign * fx, fy, -0.022))
            f_rings = []
            for ph in range(4):
                f_z = f_base.z - (f_len * ph / 3.0)
                f_y = f_base.y - (0.015 * (ph / 3.0)**2)
                rad = f_rad * (1.0 - 0.22 * (ph / 3.0))
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

    # Legs (Thighs, Knees, Calves, Ankles, 5-Toe Feet)
    N_l = 18
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_levels = [
            (0.780, 0.096, 0.096, sign * 0.100, -0.005),
            (0.710, 0.092, 0.092, sign * 0.102, -0.005),
            (0.640, 0.086, 0.086, sign * 0.105, -0.003),
            (0.570, 0.080, 0.080, sign * 0.106, -0.002),
            (0.510, 0.068, 0.072, sign * 0.105,  0.004),
            (0.470, 0.065, 0.068, sign * 0.105,  0.002),
            (0.400, 0.074, 0.076, sign * 0.105, -0.008),
            (0.330, 0.068, 0.070, sign * 0.105, -0.006),
            (0.260, 0.058, 0.058, sign * 0.104, -0.003),
            (0.180, 0.046, 0.046, sign * 0.102,  0.000),
            (0.120, 0.040, 0.040, sign * 0.100,  0.000),
            (0.085, 0.038, 0.042, sign * 0.100,  0.000)
        ]
        l_grid = []
        for z_lvl, rx, ry, cx, cy in leg_levels:
            row = []
            for i in range(N_l):
                th = 2.0 * math.pi * i / N_l
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                row.append(bm_body.verts.new(Vector((px, py, z_lvl))))
            l_grid.append(row)
        for r in range(len(l_grid) - 1):
            r1, r2 = l_grid[r], l_grid[r + 1]
            for i in range(N_l):
                next_i = (i + 1) % N_l
                bm_body.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

        # 5 Articulated Toes
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

        toe_defs = [
            ("big_toe",  0.018, 0.040, 0.011),
            ("toe_2",    0.006, 0.038, 0.009),
            ("toe_3",   -0.005, 0.035, 0.0085),
            ("toe_4",   -0.015, 0.031, 0.008),
            ("pinky_toe",-0.024, 0.026, 0.0075)
        ]
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

    # 2. CONFORMING SHIRT WITH ORIENTED 3/4 SLEEVES
    bm_s = bmesh.new()
    N_s = 28
    s_torso = [
        # (z, rx, ry, cx, cy)
        (1.575, 0.082, 0.076, 0.0,  0.010),
        (1.540, 0.092, 0.082, 0.0,  0.005),
        (1.500, 0.118, 0.098, 0.0, -0.005),
        (1.460, 0.170, 0.122, 0.0, -0.008),
        (1.410, 0.205, 0.136, 0.0, -0.005),
        (1.360, 0.220, 0.146, 0.0,  0.000),
        (1.300, 0.226, 0.152, 0.0,  0.006),
        (1.240, 0.218, 0.148, 0.0,  0.005),
        (1.180, 0.208, 0.140, 0.0,  0.000),
        (1.120, 0.198, 0.134, 0.0, -0.003),
        (1.060, 0.190, 0.128, 0.0, -0.005),
        (1.000, 0.196, 0.134, 0.0, -0.005),
        (0.950, 0.206, 0.144, 0.0, -0.005),
        (0.910, 0.214, 0.150, 0.0, -0.005)
    ]
    s_grid = []
    for z_lvl, rx, ry, cx, cy in s_torso:
        row = []
        for i in range(N_s):
            th = 2.0 * math.pi * i / N_s
            ripple = 0.004 * math.sin(6.0 * th)
            px = cx + (rx + ripple) * math.cos(th)
            py = cy + (ry + ripple) * math.sin(th)
            if z_lvl > 1.48 and py < -0.03:
                py += 0.024 * ((z_lvl - 1.48) / 0.095)
            row.append(bm_s.verts.new(Vector((px, py, z_lvl))))
        s_grid.append(row)

    for r in range(len(s_grid) - 1):
        r1, r2 = s_grid[r], s_grid[r + 1]
        for i in range(N_s):
            next_i = (i + 1) % N_s
            bm_s.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    # Oriented 3/4 Sleeves along arm direction!
    N_sl = 18
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        p_shoulder = Vector((sign * 0.185, -0.006, 1.42))
        p_elbow    = Vector((sign * 0.255, -0.012, 1.16))
        u_vec = (p_elbow - p_shoulder).normalized()
        n1 = Vector((0.0, 1.0, 0.0))
        n2 = u_vec.cross(n1).normalized()

        sl_rings = []
        # Upper sleeve to rolled cuff at mid-forearm (s from 0.0 to 1.1)
        for s in [0.0, 0.25, 0.50, 0.75, 1.0, 1.10]:
            center = p_shoulder + s * (p_elbow - p_shoulder)
            rx = 0.084 - 0.016 * s
            ry = 0.084 - 0.016 * s
            if s >= 1.0: # Folded cuff bunching
                rx += 0.006
                ry += 0.006
            ring = []
            for i in range(N_sl):
                th = 2.0 * math.pi * i / N_sl
                offset = (rx * math.cos(th)) * n2 + (ry * math.sin(th)) * n1
                ring.append(bm_s.verts.new(center + offset))
            sl_rings.append(ring)

        for r in range(len(sl_rings) - 1):
            r1, r2 = sl_rings[r], sl_rings[r + 1]
            for i in range(N_sl):
                next_i = (i + 1) % N_sl
                bm_s.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    shirt_data = bpy.data.meshes.new("Raghunath_Shirt_Mesh_Data")
    bm_s.to_mesh(shirt_data)
    bm_s.free()

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

    # 3. CONFORMING CHARCOAL JEANS
    bm_j = bmesh.new()
    N_j = 28
    jeans_torso = [
        (0.960, 0.200, 0.136, 0.0, -0.005),
        (0.910, 0.204, 0.140, 0.0, -0.005),
        (0.850, 0.206, 0.142, 0.0, -0.005),
        (0.790, 0.200, 0.138, 0.0, -0.005)
    ]
    j_grid = []
    for z_lvl, rx, ry, cx, cy in jeans_torso:
        row = []
        for i in range(N_j):
            th = 2.0 * math.pi * i / N_j
            px = cx + rx * math.cos(th)
            py = cy + ry * math.sin(th)
            row.append(bm_j.verts.new(Vector((px, py, z_lvl))))
        j_grid.append(row)

    for r in range(len(j_grid) - 1):
        r1, r2 = j_grid[r], j_grid[r + 1]
        for i in range(N_j):
            next_i = (i + 1) % N_j
            bm_j.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    N_jl = 18
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        j_legs = [
            (0.790, sign * 0.100, -0.005, 0.102, 0.102),
            (0.720, sign * 0.102, -0.005, 0.096, 0.096),
            (0.650, sign * 0.105, -0.003, 0.090, 0.091),
            (0.580, sign * 0.106, -0.002, 0.084, 0.085),
            (0.520, sign * 0.105, 0.005, 0.076, 0.078),
            (0.470, sign * 0.105, 0.002, 0.074, 0.076),
            (0.400, sign * 0.105, -0.006, 0.078, 0.080),
            (0.330, sign * 0.104, -0.004, 0.072, 0.074),
            (0.250, sign * 0.103, -0.002, 0.062, 0.062),
            (0.170, sign * 0.102, 0.000, 0.054, 0.054),
            (0.120, sign * 0.100, 0.000, 0.056, 0.056),
            (0.090, sign * 0.100, 0.000, 0.052, 0.054)
        ]
        jl_grid = []
        for z_lvl, cx, cy, rx, ry in j_legs:
            row = []
            for i in range(N_jl):
                th = 2.0 * math.pi * i / N_jl
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                row.append(bm_j.verts.new(Vector((px, py, z_lvl))))
            jl_grid.append(row)
        for r in range(len(jl_grid) - 1):
            r1, r2 = jl_grid[r], jl_grid[r + 1]
            for i in range(N_jl):
                next_i = (i + 1) % N_jl
                bm_j.faces.new([r1[i], r1[next_i], r2[next_i], r2[i]])

    jeans_data = bpy.data.meshes.new("Raghunath_Jeans_Mesh_Data")
    bm_j.to_mesh(jeans_data)
    bm_j.free()

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

    # 4. CORD NECKLACE & PENDANT
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

    # 5. SKINNING
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

    # 6. UV UNWRAP
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

    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Oriented anatomy test saved to master blend file.")

if __name__ == '__main__':
    run()
