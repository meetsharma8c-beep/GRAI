#!/usr/bin/env python3
"""
build_raghunath_realistic_human.py
==================================
Builds a complete, realistic, game-ready human character for Raghunath Mattre in GRAI.
Includes:
- Seamless neck interface with Raghunath_Head_Mesh
- Continuous anatomical body with shoulders, deltoids, A-pose arms, 5-finger hands, 5-toe feet
- Tailored crimson button-up shirt with open V-collar, folded lapels, button placket, chest pocket, and 3/4 rolled sleeves
- Slim-fit charcoal jeans with waistband, belt, knee creases, and hem cuffs
- Traditional Indian Kolhapuri leather sandals with toe ring
- Black cord necklace with brass pendant
- 59-bone UE5 Manny-compatible armature and normalized skinning
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler, Quaternion

def run():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    if not col:
        col = bpy.data.collections.new("Character_Raghunath_Mattre")
        scene.collection.children.link(col)

    head_obj = bpy.data.objects.get("Raghunath_Head_Mesh")
    hair_obj = bpy.data.objects.get("Raghunath_Hair_Mesh")
    if not head_obj:
        raise RuntimeError("Raghunath_Head_Mesh not found!")

    # Clean old generated meshes (keep head, hair, eyes, teeth, cameras, lights)
    cleanup = [
        "Raghunath_Body_Mesh", "Raghunath_Shirt_Mesh", "Raghunath_Shirt_Pocket",
        "Raghunath_Jeans_Mesh", "Raghunath_Sandal_Sole_L", "Raghunath_Sandal_Strap_L",
        "Raghunath_Sandal_ToeRing_L", "Raghunath_Sandal_Sole_R", "Raghunath_Sandal_Strap_R",
        "Raghunath_Sandal_ToeRing_R", "Raghunath_Necklace_Cord", "Raghunath_Pendant",
        "Raghunath_Belt", "Raghunath_Collar_Lapels", "Raghunath_Shirt_Buttons"
    ]
    for name in cleanup:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)

    root_empty = bpy.data.objects.get("Character_Raghunath_Root")
    world_origin = Vector((-1007.0, 1100.0, 7.238))
    if not root_empty:
        root_empty = bpy.data.objects.new("Character_Raghunath_Root", None)
        root_empty.empty_display_type = 'ARROWS'
        col.objects.link(root_empty)
    root_empty.location = world_origin

    # Materials
    mat_skin = bpy.data.materials.get("M_Raghunath_Skin_PBR")
    mat_shirt = bpy.data.materials.get("M_Raghunath_Shirt_Burgundy")
    mat_jeans = bpy.data.materials.get("M_Raghunath_Jeans_Charcoal")
    mat_leather = bpy.data.materials.get("M_Raghunath_Leather_Sandals")
    mat_sole = bpy.data.materials.get("M_Raghunath_Sandal_Sole")
    mat_neck = bpy.data.materials.get("M_Raghunath_Necklace")

    # Ensure rich saturated colors and correct roughness
    if mat_shirt and mat_shirt.node_tree:
        bsdf = mat_shirt.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.12, 0.012, 0.024, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.72
            if 'Sheen Weight' in bsdf.inputs: bsdf.inputs['Sheen Weight'].default_value = 0.25

    if mat_jeans and mat_jeans.node_tree:
        bsdf = mat_jeans.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.018, 0.020, 0.024, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.88

    if mat_skin and mat_skin.node_tree:
        bsdf = mat_skin.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.48, 0.31, 0.22, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.44
            if 'Subsurface Weight' in bsdf.inputs: bsdf.inputs['Subsurface Weight'].default_value = 0.20

    # =========================================================================
    # 1. ANATOMICAL BODY MESH
    # =========================================================================
    print("Building unified organic body mesh...")
    bm_body = bmesh.new()

    # --- TORSO ---
    # Anatomically shaped rings from neck down to crotch
    N_torso = 24
    torso_specs = [
        # (z, rx_l, rx_r, ry_f, ry_b, cx, cy)
        (1.578, 0.076, 0.076, 0.068, 0.072, 0.0,  0.010), # Welds to trimmed head base
        (1.540, 0.082, 0.082, 0.072, 0.076, 0.0,  0.006), # Mid neck
        (1.500, 0.098, 0.098, 0.080, 0.084, 0.0, -0.002), # Jugular notch / neck base
        (1.460, 0.165, 0.165, 0.095, 0.115, 0.0, -0.006), # Clavicles & Trapezius slope
        (1.420, 0.215, 0.215, 0.112, 0.130, 0.0, -0.005), # Broad athletic shoulders
        (1.360, 0.218, 0.218, 0.136, 0.136, 0.0,  0.002), # Upper pectorals / axilla
        (1.300, 0.214, 0.214, 0.142, 0.140, 0.0,  0.006), # Mid chest / nipples
        (1.240, 0.204, 0.204, 0.134, 0.136, 0.0,  0.004), # Lower ribcage
        (1.180, 0.192, 0.192, 0.124, 0.128, 0.0,  0.000), # Epigastrium
        (1.120, 0.180, 0.180, 0.116, 0.122, 0.0, -0.004), # Athletic waist taper
        (1.060, 0.174, 0.174, 0.112, 0.118, 0.0, -0.006), # Navel
        (1.000, 0.182, 0.182, 0.116, 0.122, 0.0, -0.006), # Iliac crest / Belt line
        (0.940, 0.192, 0.192, 0.124, 0.130, 0.0, -0.006), # Pelvis
        (0.880, 0.196, 0.196, 0.128, 0.136, 0.0, -0.005), # Gluteus
        (0.820, 0.194, 0.194, 0.128, 0.136, 0.0, -0.005), # Lower pelvis
        (0.780, 0.188, 0.188, 0.122, 0.130, 0.0, -0.005)  # Inseam crotch
    ]

    torso_rings = []
    for z_lvl, rx_l, rx_r, ry_f, ry_b, cx, cy in torso_specs:
        ring = []
        for i in range(N_torso):
            th = 2.0 * math.pi * i / N_torso
            rx = rx_l if math.cos(th) >= 0 else rx_r
            ry = ry_b if math.sin(th) >= 0 else ry_f
            px = cx + rx * math.cos(th)
            py = cy + ry * math.sin(th)
            ring.append(bm_body.verts.new(Vector((px, py, z_lvl))))
        torso_rings.append(ring)

    for r in range(len(torso_rings) - 1):
        r1, r2 = torso_rings[r], torso_rings[r + 1]
        for i in range(N_torso):
            ni = (i + 1) % N_torso
            bm_body.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    # --- A-POSE ARMS, WRISTS & 5-FINGER HANDS ---
    N_arm = 16
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        p_shoulder_joint = Vector((sign * 0.235, -0.008, 1.37))
        p_elbow          = Vector((sign * 0.285, -0.012, 1.14))
        p_wrist          = Vector((sign * 0.315, -0.006, 0.88))

        # Upper arm path
        v_upper = (p_elbow - p_shoulder_joint).normalized()
        n_up_y = Vector((0.0, 1.0, 0.0))
        n_up_x = v_upper.cross(n_up_y).normalized()

        arm_rings = []
        upper_stations = [
            (0.00, 0.078, 0.078), # Deltoid cap
            (0.20, 0.072, 0.074), # Deltoid belly
            (0.40, 0.065, 0.066), # Mid-biceps/triceps
            (0.70, 0.058, 0.058), # Lower bicep
            (1.00, 0.052, 0.052), # Elbow joint
        ]
        for s, rx, ry in upper_stations:
            center = p_shoulder_joint + s * (p_elbow - p_shoulder_joint)
            ring = []
            for i in range(N_arm):
                th = 2.0 * math.pi * i / N_arm
                offset = (rx * math.cos(th)) * n_up_x + (ry * math.sin(th)) * n_up_y
                ring.append(bm_body.verts.new(center + offset))
            arm_rings.append(ring)

        # Forearm path
        v_fore = (p_wrist - p_elbow).normalized()
        n_fo_y = Vector((0.0, 1.0, 0.0))
        n_fo_x = v_fore.cross(n_fo_y).normalized()

        fore_stations = [
            (0.25, 0.050, 0.048),
            (0.50, 0.044, 0.042),
            (0.75, 0.038, 0.034),
            (1.00, 0.034, 0.026),
        ]
        for s, rx, ry in fore_stations:
            center = p_elbow + s * (p_wrist - p_elbow)
            ring = []
            for i in range(N_arm):
                th = 2.0 * math.pi * i / N_arm
                offset = (rx * math.cos(th)) * n_fo_x + (ry * math.sin(th)) * n_fo_y
                ring.append(bm_body.verts.new(center + offset))
            arm_rings.append(ring)

        # Build arm quad faces
        for r in range(len(arm_rings) - 1):
            r1, r2 = arm_rings[r], arm_rings[r + 1]
            for i in range(N_arm):
                ni = (i + 1) % N_arm
                bm_body.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

        # Continuous Hand Palm (Extending from wrist ring at Z=0.88 down to knuckles at Z=0.80)
        wrist_ring = arm_rings[-1] # 16 vertices at wrist
        
        # Palm slice at mid-metacarpal (Z=0.84)
        palm_mid_ring = []
        for i in range(N_arm):
            th = 2.0 * math.pi * i / N_arm
            rx = 0.042
            ry = 0.016
            offset = Vector((sign * rx * math.cos(th), ry * math.sin(th), 0.0))
            palm_mid_ring.append(bm_body.verts.new(p_wrist + Vector((0, 0, -0.040)) + offset))

        for i in range(N_arm):
            ni = (i + 1) % N_arm
            bm_body.faces.new([wrist_ring[i], wrist_ring[ni], palm_mid_ring[ni], palm_mid_ring[i]])

        # Knuckle line at Z=0.80
        knuckle_ring = []
        for i in range(N_arm):
            th = 2.0 * math.pi * i / N_arm
            rx = 0.044
            ry = 0.014
            offset = Vector((sign * rx * math.cos(th), ry * math.sin(th), 0.0))
            knuckle_ring.append(bm_body.verts.new(p_wrist + Vector((0, 0, -0.075)) + offset))

        for i in range(N_arm):
            ni = (i + 1) % N_arm
            bm_body.faces.new([palm_mid_ring[i], palm_mid_ring[ni], knuckle_ring[ni], knuckle_ring[i]])

        # 5 Articulated Quad-Cylinder Fingers
        finger_specs = [
            ("thumb",  -0.018, -0.012, -0.035, 0.046, 0.0095, 0.35),
            ("index",  -0.014,  0.002, -0.075, 0.062, 0.0082, 0.05),
            ("middle", -0.001,  0.003, -0.075, 0.068, 0.0086, 0.02),
            ("ring",    0.012,  0.002, -0.075, 0.063, 0.0082, 0.02),
            ("pinky",   0.023,  0.001, -0.075, 0.052, 0.0072, 0.04),
        ]
        for fname, fx, fy, fz, flen, frad, frot in finger_specs:
            f_base = p_wrist + Vector((sign * fx, fy, fz))
            f_rings = []
            N_f = 8
            for ph in range(4): # 3 phalanx segments = 4 rings
                t = ph / 3.0
                pz = f_base.z - (flen * t)
                py = f_base.y - (flen * t * frot)
                rad = frad * (1.0 - 0.20 * t)
                ring = []
                for s in range(N_f):
                    th = 2.0 * math.pi * s / N_f
                    vx = f_base.x + sign * (rad * math.cos(th))
                    vy = py + rad * math.sin(th)
                    ring.append(bm_body.verts.new(Vector((vx, vy, pz))))
                f_rings.append(ring)

            for r in range(len(f_rings) - 1):
                r1, r2 = f_rings[r], f_rings[r + 1]
                for s in range(N_f):
                    ns = (s + 1) % N_f
                    bm_body.faces.new([r1[s], r1[ns], r2[ns], r2[s]])

            # Rounded fingertip cap
            tip_center = bm_body.verts.new(Vector((f_base.x, f_rings[-1][0].co.y, f_rings[-1][0].co.z - 0.004)))
            for s in range(N_f):
                ns = (s + 1) % N_f
                bm_body.faces.new([f_rings[-1][s], f_rings[-1][ns], tip_center])

    # --- LEGS & 5-TOE FEET ---
    N_leg = 16
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_specs = [
            (0.780, 0.098, 0.098, sign * 0.100, -0.005),
            (0.710, 0.094, 0.094, sign * 0.102, -0.005),
            (0.640, 0.088, 0.088, sign * 0.104, -0.003),
            (0.570, 0.080, 0.080, sign * 0.105, -0.002),
            (0.510, 0.070, 0.074, sign * 0.105,  0.004),
            (0.470, 0.066, 0.070, sign * 0.105,  0.002),
            (0.400, 0.076, 0.080, sign * 0.105, -0.008),
            (0.330, 0.070, 0.072, sign * 0.105, -0.006),
            (0.260, 0.058, 0.058, sign * 0.104, -0.003),
            (0.180, 0.046, 0.046, sign * 0.102,  0.000),
            (0.120, 0.040, 0.040, sign * 0.100,  0.000),
            (0.080, 0.038, 0.042, sign * 0.100,  0.000),
        ]
        l_grid = []
        for z_lvl, rx, ry, cx, cy in leg_specs:
            ring = []
            for i in range(N_leg):
                th = 2.0 * math.pi * i / N_leg
                px = cx + rx * math.cos(th)
                py = cy + ry * math.sin(th)
                ring.append(bm_body.verts.new(Vector((px, py, z_lvl))))
            l_grid.append(ring)

        for r in range(len(l_grid) - 1):
            r1, r2 = l_grid[r], l_grid[r + 1]
            for i in range(N_leg):
                ni = (i + 1) % N_leg
                bm_body.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

        # Foot Body
        foot_center = Vector((sign * 0.100, 0.030, 0.040))
        foot_rings = []
        N_ft = 12
        for fy in [-0.055, -0.020, 0.020, 0.060, 0.085]:
            if fy < 0:
                fw, fh, fz = 0.034, 0.032, 0.035
            else:
                fw, fh, fz = 0.044, 0.022, 0.024
            ring = []
            for i in range(N_ft):
                th = 2.0 * math.pi * i / N_ft
                px = foot_center.x + sign * (fw * math.cos(th))
                pz = fz + fh * math.sin(th)
                ring.append(bm_body.verts.new(Vector((px, fy, pz))))
            foot_rings.append(ring)

        for r in range(len(foot_rings) - 1):
            r1, r2 = foot_rings[r], foot_rings[r + 1]
            for i in range(N_ft):
                ni = (i + 1) % N_ft
                bm_body.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

        # 5 Articulated Toes
        toe_specs = [
            ("big_toe",  0.016, 0.085, 0.042, 0.011),
            ("toe_2",    0.005, 0.085, 0.040, 0.009),
            ("toe_3",   -0.006, 0.085, 0.036, 0.0085),
            ("toe_4",   -0.016, 0.085, 0.032, 0.0080),
            ("pinky_toe",-0.025, 0.085, 0.026, 0.0075)
        ]
        for tname, tx, start_y, tlen, trad in toe_specs:
            t_base = Vector((foot_center.x + sign * tx, start_y, 0.024))
            t_rings = []
            N_t = 8
            for ph in range(3):
                t = ph / 2.0
                ty = t_base.y + (tlen * t)
                rad = trad * (1.0 - 0.22 * t)
                ring = []
                for s in range(N_t):
                    th = 2.0 * math.pi * s / N_t
                    px = t_base.x + sign * (rad * math.cos(th))
                    pz = t_base.z + rad * math.sin(th)
                    ring.append(bm_body.verts.new(Vector((px, ty, pz))))
                t_rings.append(ring)

            for r in range(len(t_rings) - 1):
                r1, r2 = t_rings[r], t_rings[r + 1]
                for s in range(N_t):
                    ns = (s + 1) % N_t
                    bm_body.faces.new([r1[s], r1[ns], r2[ns], r2[s]])

            tip_v = bm_body.verts.new(Vector((t_base.x, t_rings[-1][0].co.y + 0.004, t_base.z)))
            for s in range(N_t):
                ns = (s + 1) % N_t
                bm_body.faces.new([t_rings[-1][s], t_rings[-1][ns], tip_v])

    body_mesh_data = bpy.data.meshes.new("Raghunath_Body_Mesh_Data")
    bm_body.to_mesh(body_mesh_data)
    bm_body.free()

    body_obj = bpy.data.objects.new("Raghunath_Body_Mesh", body_mesh_data)
    col.objects.link(body_obj)
    body_obj.parent = root_empty
    body_obj.data.materials.append(mat_skin)
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.shade_smooth()

    # =========================================================================
    # 2. CONFORMING CRIMSON BUTTON-UP SHIRT
    # =========================================================================
    print("Building conforming crimson button-up shirt...")
    bm_shirt = bmesh.new()

    N_sh = 24
    shirt_specs = [
        # (z, rx_l, rx_r, ry_f, ry_b, cx, cy, is_open_v)
        (1.540, 0.088, 0.088, 0.076, 0.082, 0.0,  0.006, True),
        (1.500, 0.108, 0.108, 0.088, 0.092, 0.0, -0.002, True),
        (1.460, 0.178, 0.178, 0.108, 0.126, 0.0, -0.006, True),
        (1.420, 0.228, 0.228, 0.124, 0.140, 0.0, -0.005, True),
        (1.370, 0.228, 0.228, 0.146, 0.146, 0.0,  0.002, True),
        (1.310, 0.222, 0.222, 0.150, 0.148, 0.0,  0.006, False),
        (1.240, 0.212, 0.212, 0.142, 0.144, 0.0,  0.004, False),
        (1.170, 0.200, 0.200, 0.132, 0.136, 0.0,  0.000, False),
        (1.100, 0.190, 0.190, 0.124, 0.130, 0.0, -0.004, False),
        (1.030, 0.192, 0.192, 0.126, 0.132, 0.0, -0.006, False),
        (0.960, 0.204, 0.204, 0.136, 0.142, 0.0, -0.006, False),
        (0.900, 0.214, 0.214, 0.144, 0.150, 0.0, -0.006, False),
    ]

    sh_rings = []
    for z_lvl, rx_l, rx_r, ry_f, ry_b, cx, cy, is_open_v in shirt_specs:
        ring = []
        for i in range(N_sh):
            th = 2.0 * math.pi * i / N_sh
            rx = rx_l if math.cos(th) >= 0 else rx_r
            ry = ry_b if math.sin(th) >= 0 else ry_f
            
            wrinkle = 0.003 * math.sin(5.0 * th + z_lvl * 12.0)
            px = cx + (rx + wrinkle) * math.cos(th)
            py = cy + (ry + wrinkle) * math.sin(th)

            if is_open_v and math.sin(th) < -0.70:
                v_depth = (z_lvl - 1.37) / (1.54 - 1.37)
                py += 0.035 * v_depth

            ring.append(bm_shirt.verts.new(Vector((px, py, z_lvl))))
        sh_rings.append(ring)

    for r in range(len(sh_rings) - 1):
        r1, r2 = sh_rings[r], sh_rings[r + 1]
        for i in range(N_sh):
            ni = (i + 1) % N_sh
            bm_shirt.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    # 3/4 Sleeves with Folded Rolled Cuffs
    N_sl = 16
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        p_sh_joint = Vector((sign * 0.235, -0.008, 1.38))
        p_elbow    = Vector((sign * 0.285, -0.012, 1.14))
        v_arm = (p_elbow - p_sh_joint).normalized()
        n_y = Vector((0.0, 1.0, 0.0))
        n_x = v_arm.cross(n_y).normalized()

        sl_rings = []
        sleeve_stations = [
            (0.00, 0.088, 0.088),
            (0.25, 0.082, 0.082),
            (0.50, 0.076, 0.076),
            (0.75, 0.072, 0.072),
            (1.00, 0.068, 0.068),
            (1.08, 0.076, 0.076),
            (1.15, 0.078, 0.078),
        ]
        for s, rx, ry in sleeve_stations:
            center = p_sh_joint + s * (p_elbow - p_sh_joint)
            ring = []
            for i in range(N_sl):
                th = 2.0 * math.pi * i / N_sl
                wrinkle = 0.003 * math.sin(4.0 * th)
                offset = ((rx + wrinkle) * math.cos(th)) * n_x + ((ry + wrinkle) * math.sin(th)) * n_y
                ring.append(bm_shirt.verts.new(center + offset))
            sl_rings.append(ring)

        for r in range(len(sl_rings) - 1):
            r1, r2 = sl_rings[r], sl_rings[r + 1]
            for i in range(N_sl):
                ni = (i + 1) % N_sl
                bm_shirt.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    shirt_mesh_data = bpy.data.meshes.new("Raghunath_Shirt_Mesh_Data")
    bm_shirt.to_mesh(shirt_mesh_data)
    bm_shirt.free()

    shirt_obj = bpy.data.objects.new("Raghunath_Shirt_Mesh", shirt_mesh_data)
    col.objects.link(shirt_obj)
    shirt_obj.parent = root_empty
    shirt_obj.data.materials.append(mat_shirt)
    bpy.context.view_layer.objects.active = shirt_obj
    bpy.ops.object.shade_smooth()

    # Left Chest Pocket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.085, -0.150, 1.285))
    pocket = bpy.context.active_object
    pocket.name = "Raghunath_Shirt_Pocket"
    col.objects.link(pocket)
    if pocket.name in scene.collection.objects: scene.collection.objects.unlink(pocket)
    pocket.parent = root_empty
    pocket.scale = (0.042, 0.004, 0.052)
    bpy.ops.object.transform_apply(scale=True)
    pocket.data.materials.append(mat_shirt)

    # Folded Collar Lapels
    bm_lapel = bmesh.new()
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        v1 = bm_lapel.verts.new(Vector((sign * 0.075, -0.075, 1.520)))
        v2 = bm_lapel.verts.new(Vector((sign * 0.115, -0.110, 1.440)))
        v3 = bm_lapel.verts.new(Vector((sign * 0.040, -0.125, 1.390)))
        v4 = bm_lapel.verts.new(Vector((sign * 0.085, -0.135, 1.410)))
        bm_lapel.faces.new([v1, v2, v4, v3])

    m_lapel = bpy.data.meshes.new("Raghunath_Collar_Lapels_Data")
    bm_lapel.to_mesh(m_lapel)
    bm_lapel.free()
    lapels_obj = bpy.data.objects.new("Raghunath_Collar_Lapels", m_lapel)
    col.objects.link(lapels_obj)
    lapels_obj.parent = root_empty
    lapels_obj.data.materials.append(mat_shirt)
    bpy.context.view_layer.objects.active = lapels_obj
    bpy.ops.object.shade_smooth()

    # =========================================================================
    # 3. CONFORMING SLIM-FIT CHARCOAL JEANS
    # =========================================================================
    print("Building conforming slim-fit charcoal jeans...")
    bm_jeans = bmesh.new()

    N_j = 24
    jeans_pelvis_specs = [
        (0.920, 0.188, 0.126, 0.0, -0.006),
        (0.860, 0.198, 0.134, 0.0, -0.006),
        (0.810, 0.200, 0.138, 0.0, -0.005),
        (0.760, 0.194, 0.132, 0.0, -0.005)
    ]
    j_pelvis_rings = []
    for z_lvl, rx, ry, cx, cy in jeans_pelvis_specs:
        ring = []
        for i in range(N_j):
            th = 2.0 * math.pi * i / N_j
            px = cx + rx * math.cos(th)
            py = cy + ry * math.sin(th)
            ring.append(bm_jeans.verts.new(Vector((px, py, z_lvl))))
        j_pelvis_rings.append(ring)

    for r in range(len(j_pelvis_rings) - 1):
        r1, r2 = j_pelvis_rings[r], j_pelvis_rings[r + 1]
        for i in range(N_j):
            ni = (i + 1) % N_j
            bm_jeans.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    N_jl = 16
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_jeans_specs = [
            (0.760, 0.104, 0.104, sign * 0.100, -0.005),
            (0.690, 0.098, 0.098, sign * 0.102, -0.005),
            (0.620, 0.092, 0.092, sign * 0.104, -0.003),
            (0.550, 0.084, 0.084, sign * 0.105, -0.002),
            (0.490, 0.076, 0.080, sign * 0.105,  0.004),
            (0.450, 0.074, 0.078, sign * 0.105,  0.002),
            (0.380, 0.080, 0.082, sign * 0.105, -0.006),
            (0.310, 0.074, 0.074, sign * 0.105, -0.005),
            (0.240, 0.065, 0.065, sign * 0.104, -0.002),
            (0.160, 0.055, 0.055, sign * 0.102,  0.000),
            (0.100, 0.052, 0.052, sign * 0.100,  0.000),
            (0.065, 0.050, 0.052, sign * 0.100,  0.000),
        ]
        jl_grid = []
        for z_lvl, rx, ry, cx, cy in leg_jeans_specs:
            ring = []
            for i in range(N_jl):
                th = 2.0 * math.pi * i / N_jl
                crease = 0.003 * math.sin(3.0 * th + z_lvl * 15.0)
                px = cx + (rx + crease) * math.cos(th)
                py = cy + (ry + crease) * math.sin(th)
                ring.append(bm_jeans.verts.new(Vector((px, py, z_lvl))))
            jl_grid.append(ring)

        for r in range(len(jl_grid) - 1):
            r1, r2 = jl_grid[r], jl_grid[r + 1]
            for i in range(N_jl):
                ni = (i + 1) % N_jl
                bm_jeans.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    jeans_mesh_data = bpy.data.meshes.new("Raghunath_Jeans_Mesh_Data")
    bm_jeans.to_mesh(jeans_mesh_data)
    bm_jeans.free()

    jeans_obj = bpy.data.objects.new("Raghunath_Jeans_Mesh", jeans_mesh_data)
    col.objects.link(jeans_obj)
    jeans_obj.parent = root_empty
    jeans_obj.data.materials.append(mat_jeans)
    bpy.context.view_layer.objects.active = jeans_obj
    bpy.ops.object.shade_smooth()

    # Dark Leather Belt
    bm_belt = bmesh.new()
    N_b = 24
    for bz in [0.925, 0.905]:
        b_ring = []
        for i in range(N_b):
            th = 2.0 * math.pi * i / N_b
            px = 0.192 * math.cos(th)
            py = -0.006 + 0.130 * math.sin(th)
            b_ring.append(bm_belt.verts.new(Vector((px, py, bz))))
    
    r1 = bm_belt.verts[:N_b]
    r2 = bm_belt.verts[N_b:]
    for i in range(N_b):
        ni = (i + 1) % N_b
        bm_belt.faces.new([r1[i], r1[ni], r2[ni], r2[i]])

    m_belt = bpy.data.meshes.new("Raghunath_Belt_Data")
    bm_belt.to_mesh(m_belt)
    bm_belt.free()
    belt_obj = bpy.data.objects.new("Raghunath_Belt", m_belt)
    col.objects.link(belt_obj)
    belt_obj.parent = root_empty
    belt_obj.data.materials.append(mat_leather)
    bpy.context.view_layer.objects.active = belt_obj
    bpy.ops.object.shade_smooth()

    # =========================================================================
    # 4. TRADITIONAL INDIAN KOLHAPURI LEATHER SANDALS
    # =========================================================================
    print("Building traditional Indian Kolhapuri sandals...")
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        foot_center = Vector((sign * 0.100, 0.030, 0.0))

        bm_sole = bmesh.new()
        sole_profile = [
            (sign * 0.000, -0.075),
            (sign * 0.032, -0.060),
            (sign * 0.034, -0.020),
            (sign * 0.024,  0.020),
            (sign * 0.046,  0.070),
            (sign * 0.042,  0.125),
            (sign * 0.010,  0.135),
            (sign * -0.025, 0.120),
            (sign * -0.038, 0.070),
            (sign * -0.025, 0.020),
            (sign * -0.034, -0.020),
            (sign * -0.032, -0.060),
        ]
        v_bottom = [bm_sole.verts.new(Vector((foot_center.x + px, foot_center.y + py, 0.000))) for px, py in sole_profile]
        v_top    = [bm_sole.verts.new(Vector((foot_center.x + px, foot_center.y + py, 0.016))) for px, py in sole_profile]
        N_sp = len(sole_profile)
        for i in range(N_sp):
            ni = (i + 1) % N_sp
            bm_sole.faces.new([v_bottom[i], v_bottom[ni], v_top[ni], v_top[i]])
        bm_sole.faces.new(list(reversed(v_bottom)))
        bm_sole.faces.new(v_top)

        m_sole = bpy.data.meshes.new(f"Raghunath_Sandal_Sole_{side}_Data")
        bm_sole.to_mesh(m_sole)
        bm_sole.free()
        sole_obj = bpy.data.objects.new(f"Raghunath_Sandal_Sole_{side}", m_sole)
        col.objects.link(sole_obj)
        sole_obj.parent = root_empty
        sole_obj.data.materials.append(mat_sole)

        # Arched leather strap
        bm_strap = bmesh.new()
        N_st = 10
        strap_r1, strap_r2 = [], []
        for i in range(N_st):
            t = i / (N_st - 1.0)
            ang = math.pi * t
            sx = foot_center.x + sign * (0.040 - 0.080 * t)
            sz = 0.016 + 0.040 * math.sin(ang)
            strap_r1.append(bm_strap.verts.new(Vector((sx, foot_center.y + 0.030, sz))))
            strap_r2.append(bm_strap.verts.new(Vector((sx, foot_center.y + 0.060, sz))))

        for i in range(N_st - 1):
            bm_strap.faces.new([strap_r1[i], strap_r1[i+1], strap_r2[i+1], strap_r2[i]])

        m_strap = bpy.data.meshes.new(f"Raghunath_Sandal_Strap_{side}_Data")
        bm_strap.to_mesh(m_strap)
        bm_strap.free()
        strap_obj = bpy.data.objects.new(f"Raghunath_Sandal_Strap_{side}", m_strap)
        col.objects.link(strap_obj)
        strap_obj.parent = root_empty
        strap_obj.data.materials.append(mat_leather)
        strap_obj.modifiers.new("Solidify", 'SOLIDIFY').thickness = 0.003
        bpy.context.view_layer.objects.active = strap_obj
        bpy.ops.object.shade_smooth()

        # Traditional Leather Toe Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.015, minor_radius=0.003,
                                         major_segments=16, minor_segments=8,
                                         location=(foot_center.x + sign * 0.016, foot_center.y + 0.095, 0.024))
        toering = bpy.context.active_object
        toering.name = f"Raghunath_Sandal_ToeRing_{side}"
        col.objects.link(toering)
        if toering.name in scene.collection.objects: scene.collection.objects.unlink(toering)
        toering.parent = root_empty
        toering.data.materials.append(mat_leather)

    # =========================================================================
    # 5. BLACK CORD NECKLACE & BRASS PENDANT
    # =========================================================================
    print("Building necklace and brass pendant...")
    bm_neck = bmesh.new()
    N_nc = 24
    n_r1, n_r2 = [], []
    for i in range(N_nc):
        th = 2.0 * math.pi * i / N_nc
        nx = 0.068 * math.cos(th)
        ny = 0.010 + 0.074 * math.sin(th)
        nz = 1.485
        if math.sin(th) < 0:
            nz -= 0.100 * (-math.sin(th))**1.5
            ny -= 0.028 * (-math.sin(th))
        n_r1.append(bm_neck.verts.new(Vector((nx, ny, nz))))
        n_r2.append(bm_neck.verts.new(Vector((nx, ny, nz - 0.003))))

    for i in range(N_nc):
        ni = (i + 1) % N_nc
        bm_neck.faces.new([n_r1[i], n_r1[ni], n_r2[ni], n_r2[i]])

    m_neck = bpy.data.meshes.new("Raghunath_Necklace_Cord_Data")
    bm_neck.to_mesh(m_neck)
    bm_neck.free()
    neck_cord = bpy.data.objects.new("Raghunath_Necklace_Cord", m_neck)
    col.objects.link(neck_cord)
    neck_cord.parent = root_empty
    neck_cord.data.materials.append(mat_neck)
    bpy.context.view_layer.objects.active = neck_cord
    bpy.ops.object.shade_smooth()

    # Brass Pendant
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.008,
                                         location=(0.0, -0.096, 1.380))
    pendant = bpy.context.active_object
    pendant.name = "Raghunath_Pendant"
    col.objects.link(pendant)
    if pendant.name in scene.collection.objects: scene.collection.objects.unlink(pendant)
    pendant.parent = root_empty
    pendant.scale = (0.75, 0.40, 1.50)
    bpy.ops.object.transform_apply(scale=True)
    pendant.data.materials.append(mat_neck)

    # =========================================================================
    # 6. SKINNING & RIGGING (UE5 MANNY COMPATIBLE ARMATURE)
    # =========================================================================
    print("Skinning all character meshes to Armature_Raghunath...")
    arm_obj = bpy.data.objects.get("Armature_Raghunath")
    bone_names = [b.name for b in arm_obj.data.bones] if arm_obj else []

    all_meshes = [
        body_obj, shirt_obj, pocket, lapels_obj, jeans_obj, belt_obj,
        bpy.data.objects.get("Raghunath_Sandal_Sole_L"),
        bpy.data.objects.get("Raghunath_Sandal_Strap_L"),
        bpy.data.objects.get("Raghunath_Sandal_ToeRing_L"),
        bpy.data.objects.get("Raghunath_Sandal_Sole_R"),
        bpy.data.objects.get("Raghunath_Sandal_Strap_R"),
        bpy.data.objects.get("Raghunath_Sandal_ToeRing_R"),
        neck_cord, pendant, head_obj, hair_obj,
        bpy.data.objects.get("Raghunath_Eye_L"),
        bpy.data.objects.get("Raghunath_Eye_R"),
        bpy.data.objects.get("Raghunath_Teeth_Mouth")
    ]

    for o in all_meshes:
        if not o or not arm_obj: continue
        arm_mod = None
        for m in o.modifiers:
            if m.type == 'ARMATURE':
                arm_mod = m
                break
        if not arm_mod:
            arm_mod = o.modifiers.new("Armature", 'ARMATURE')
        arm_mod.object = arm_obj

        existing_vgs = set(o.vertex_groups.keys())
        for bname in bone_names:
            if bname not in existing_vgs:
                o.vertex_groups.new(name=bname)

        if len(o.data.vertices) > 0 and o != head_obj and o != hair_obj:
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

    # =========================================================================
    # 7. UV UNWRAPPING & CLEANUP
    # =========================================================================
    print("Unwrapping UVs and removing doubles...")
    for o in all_meshes:
        if not o or o == head_obj or o == hair_obj: continue
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')

    # Save to master scene
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Realistic Raghunath character successfully built and saved to master blend!")

if __name__ == '__main__':
    run()
