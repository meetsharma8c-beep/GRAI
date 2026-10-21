"""
GRAI — RAGHUNATH MATTRE: MASTERPIECE ORGANIC 3D CHARACTER SCULPT
================================================================
Faithful organic anatomical reproduction of the authoritative reference photograph:
- Anatomical head with defined masculine jawline, zygomatic cheekbones, nose, lips, eyes, ears, and neck.
- Voluminous, textured, messy dark hair with organic swept-back locks.
- Groomed dark stubble beard and mustache following the mandibular jaw and upper lip.
- Crimson / burgundy casual button-down shirt with open V-collar, rolled 3/4 sleeves, chest pocket, and organic drape.
- Charcoal black denim jeans with realistic seams, knee creases, and ankle stacking.
- Traditional Indian leather toe-post strap sandals (chappals) with detailed anatomical bare feet and toes.
- Reference Stance: Confident standing posture, right hand resting in front pocket, relaxed left arm, direct focused gaze.
- Standard UE5 Humanoid Armature (SK_Mannequin compatible) with smooth vertex skinning.
- Rendered in Cycles Metal GPU at 1080x1920.
"""
import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Matrix, Euler, Quaternion

def build_raghunath_masterpiece():
    print("=== SCULPTING MASTERPIECE RAGHUNATH MATTRE ===")
    scene = bpy.context.scene

    # 1. CLEANUP PREVIOUS OBJECTS
    for o in list(bpy.data.objects):
        if "Raghunath" in o.name or "RAGHUNATH" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    col_name = "Character_Raghunath_Mattre"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

    # 2. PBR MATERIALS
    def make_mat(name, base_color, roughness=0.5, metallic=0.0, sss_weight=0.0, sss_radius=(0.1, 0.05, 0.02), specular=0.5):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = base_color
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = specular
            elif 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = specular
            if sss_weight > 0.0:
                if 'Subsurface Weight' in bsdf.inputs:
                    bsdf.inputs['Subsurface Weight'].default_value = sss_weight
                elif 'Subsurface' in bsdf.inputs:
                    bsdf.inputs['Subsurface'].default_value = sss_weight
                if 'Subsurface Radius' in bsdf.inputs:
                    bsdf.inputs['Subsurface Radius'].default_value = sss_radius
        m.diffuse_color = (base_color[0], base_color[1], base_color[2], 1.0)
        m.roughness = roughness
        return m

    # Material Palette matching reference
    mat_skin = make_mat("M_Raghunath_Skin", (0.52, 0.33, 0.23, 1.0), roughness=0.38, sss_weight=0.32, sss_radius=(0.38, 0.18, 0.10))
    mat_hair = make_mat("M_Raghunath_Hair", (0.025, 0.02, 0.02, 1.0), roughness=0.48, specular=0.65)
    mat_beard = make_mat("M_Raghunath_Beard", (0.03, 0.025, 0.025, 1.0), roughness=0.62, specular=0.35)
    mat_shirt = make_mat("M_Raghunath_Shirt_Crimson", (0.30, 0.04, 0.065, 1.0), roughness=0.72, specular=0.25)
    if mat_shirt.node_tree:
        bsdf = mat_shirt.node_tree.nodes.get("Principled BSDF")
        if bsdf and 'Sheen Weight' in bsdf.inputs:
            bsdf.inputs['Sheen Weight'].default_value = 0.60
            if 'Sheen Tint' in bsdf.inputs:
                bsdf.inputs['Sheen Tint'].default_value = (0.7, 0.2, 0.3, 1.0)
    mat_jeans = make_mat("M_Raghunath_Jeans_Charcoal", (0.07, 0.075, 0.085, 1.0), roughness=0.82, specular=0.20)
    mat_leather = make_mat("M_Raghunath_Sandals_Leather", (0.06, 0.045, 0.035, 1.0), roughness=0.45, specular=0.40)
    mat_sole = make_mat("M_Raghunath_Sandals_Sole", (0.02, 0.02, 0.02, 1.0), roughness=0.90, specular=0.10)
    mat_eyes = make_mat("M_Raghunath_Eyes", (0.08, 0.05, 0.03, 1.0), roughness=0.06, specular=0.98)
    mat_necklace = make_mat("M_Raghunath_Necklace", (0.015, 0.015, 0.015, 1.0), roughness=0.50, specular=0.30)

    # Road elevation at Marine Drive (Y = 1100) is Z = 7.225m
    road_z = 7.225
    world_origin = Vector((-1007.0, 1100.0, road_z))

    bm = bmesh.new()

    # Helper: Loft generator for connected quad rings
    def loft_rings(bm, rings, mat_idx=0, cap_bot=False, cap_top=False):
        N = len(rings[0])
        num_rings = len(rings)
        vert_grid = []
        for r_idx, ring in enumerate(rings):
            row = []
            for pt in ring:
                row.append(bm.verts.new(pt))
            vert_grid.append(row)
        bm.verts.ensure_lookup_table()
        
        for r in range(num_rings - 1):
            for i in range(N):
                i_next = (i + 1) % N
                v1 = vert_grid[r][i]
                v2 = vert_grid[r][i_next]
                v3 = vert_grid[r + 1][i_next]
                v4 = vert_grid[r + 1][i]
                f = bm.faces.new([v1, v2, v3, v4])
                f.material_index = mat_idx
                f.smooth = True
        
        if cap_bot:
            f = bm.faces.new(list(reversed(vert_grid[0])))
            f.material_index = mat_idx
            f.smooth = True
        if cap_top:
            f = bm.faces.new(vert_grid[-1])
            f.material_index = mat_idx
            f.smooth = True
        return vert_grid

    # Helper: Anatomical ring with independent front/back/side sculpting
    def sculpt_ring(cz, rx, ry_front, ry_back, N=24, cx=0.0, cy=0.0, z_front_offset=0.0):
        ring = []
        for i in range(N):
            angle = (2.0 * math.pi * i) / N
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # Front is -Y, Back is +Y
            ry = ry_front if sin_a < 0 else ry_back
            x = cx + cos_a * rx
            y = cy + sin_a * ry
            z = cz + (z_front_offset if sin_a < 0 else 0.0) * abs(sin_a)
            ring.append(Vector((x, y, z)))
        return ring

    # ---------------------------------------------------------------------
    # 1. ANATOMICAL HEAD & NECK
    # Character faces -Y (South)
    # Head height: 1.58m (neck/jaw base) to 1.82m (cranium)
    # ---------------------------------------------------------------------
    head_rings = [
        # Neck base (flaring outwards into trapezius and clavicles)
        sculpt_ring(1.47, 0.095, 0.088, 0.095, 24, cy=0.01),
        # Mid neck (cervical spine, Adam's apple forward)
        sculpt_ring(1.53, 0.076, 0.075, 0.080, 24, cy=0.005),
        # Upper neck / submandibular under jaw
        sculpt_ring(1.58, 0.072, 0.070, 0.076, 24),
        # Mandible / square masculine jawline & chin apex (front projects to -Y)
        sculpt_ring(1.61, 0.076, 0.088, 0.078, 24, z_front_offset=-0.015),
        # Lips & mouth corners (philtrum, lower lip)
        sculpt_ring(1.64, 0.078, 0.092, 0.080, 24),
        # Nose base, nostrils & cheekbones (zygomatic arches widen to sides)
        sculpt_ring(1.68, 0.084, 0.108, 0.085, 24), # Nose tip projects forward to -Y
        # Nose bridge & eye orbits (recessed eye sockets)
        sculpt_ring(1.71, 0.082, 0.096, 0.088, 24),
        # Supraorbital brow ridge & temples
        sculpt_ring(1.74, 0.083, 0.094, 0.092, 24),
        # Forehead (slight backward cranial slope)
        sculpt_ring(1.77, 0.080, 0.088, 0.094, 24, cy=0.008),
        # Cranium crown
        sculpt_ring(1.80, 0.068, 0.074, 0.085, 24, cy=0.015),
        # Top of skull
        sculpt_ring(1.82, 0.040, 0.045, 0.055, 24, cy=0.020),
    ]
    loft_rings(bm, head_rings, mat_idx=0, cap_top=True) # Skin

    # Eyeballs (Deep brown South Asian eyes matching reference)
    for sign in [-1, 1]:
        eye_pos = Vector((sign * 0.036, -0.082, 1.712))
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.014, matrix=Matrix.Translation(eye_pos))
        for f in bm.faces[-16:]:
            f.material_index = 7 # Eyes
            f.smooth = True

    # 3D Groomed Stubble Beard & Mustache (wrapping jawline, chin, and upper lip)
    beard_rings = [
        # Upper lip mustache
        sculpt_ring(1.650, 0.076, 0.095, 0.076, 24),
        # Mandible jawline & chin stubble
        sculpt_ring(1.615, 0.077, 0.091, 0.080, 24),
        # Under chin stubble
        sculpt_ring(1.585, 0.073, 0.074, 0.076, 24),
    ]
    loft_rings(bm, beard_rings, mat_idx=2) # Beard

    # Voluminous Textured Messy Hair (Full volume, swept-back sides, stylish quiff locks)
    hair_rings = [
        # Hairline ring
        sculpt_ring(1.745, 0.088, 0.098, 0.098, 24, cy=0.010),
        # Mid volume (sides and back)
        sculpt_ring(1.780, 0.096, 0.106, 0.108, 24, cy=0.012),
        # Top swept-back volume & front quiff
        sculpt_ring(1.820, 0.094, 0.114, 0.106, 24, cy=0.015, z_front_offset=0.035),
        # Upper crown
        sculpt_ring(1.848, 0.080, 0.095, 0.098, 24, cy=0.018),
        # Peak crown
        sculpt_ring(1.865, 0.045, 0.055, 0.060, 24, cy=0.020),
    ]
    loft_rings(bm, hair_rings, mat_idx=1, cap_top=True) # Hair

    # Black Cord Necklace with silver/black pendant
    neck_rings = [
        sculpt_ring(1.475, 0.080, 0.086, 0.082, 24, z_front_offset=-0.045),
        sculpt_ring(1.470, 0.078, 0.084, 0.080, 24, z_front_offset=-0.045),
    ]
    loft_rings(bm, neck_rings, mat_idx=8) # Necklace
    # Pendant
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, -0.095, 1.415))) @ Matrix.Scale(0.012, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.006, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.020, 4, Vector((0, 0, 1))))
    for f in bm.faces[-6:]: f.material_index = 8

    # ---------------------------------------------------------------------
    # 2. CRIMSON / BURGUNDY CASUAL SHIRT (Torso & Open Collar)
    # ---------------------------------------------------------------------
    shirt_rings = [
        # Hem: Relaxed untucked drape over jeans waistband
        sculpt_ring(0.92, 0.192, 0.148, 0.145, 24),
        # Lower waist
        sculpt_ring(1.04, 0.182, 0.140, 0.138, 24),
        # Mid-torso
        sculpt_ring(1.18, 0.190, 0.145, 0.142, 24),
        # Athletic broad chest
        sculpt_ring(1.32, 0.222, 0.158, 0.150, 24),
        # Upper chest / under collar (open V-neck)
        sculpt_ring(1.42, 0.218, 0.148, 0.145, 24),
        # Collar line / shoulders
        sculpt_ring(1.47, 0.182, 0.125, 0.130, 24),
    ]
    loft_rings(bm, shirt_rings, mat_idx=3) # Crimson Shirt

    # Open Spread Collar Lapels (draping down and outwards on chest)
    for sign in [-1, 1]:
        c1 = Vector((sign * 0.035, -0.115, 1.48))
        c2 = Vector((sign * 0.095, -0.075, 1.44))
        c3 = Vector((sign * 0.105, -0.135, 1.39))
        c4 = Vector((sign * 0.045, -0.150, 1.43))
        f = bm.faces.new([bm.verts.new(c1), bm.verts.new(c2), bm.verts.new(c3), bm.verts.new(c4)])
        f.material_index = 3
        f.smooth = True

    # Left Chest Pocket
    pocket_mat = Matrix.Translation(Vector((-0.092, -0.156, 1.31))) @ Matrix.Scale(0.065, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.006, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.075, 4, Vector((0, 0, 1)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=pocket_mat)
    for f in bm.faces[-6:]: f.material_index = 3

    # Shirt Buttons down center front
    for btn_z in [1.30, 1.22, 1.14, 1.06, 0.98]:
        btn_pos = Vector((0, -0.152, btn_z))
        bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=6, radius=0.007, matrix=Matrix.Translation(btn_pos))
        for f in bm.faces[-12:]: f.material_index = 3

    # ---------------------------------------------------------------------
    # 3. ARMS: 3/4 ROLLED SLEEVES + FOREARMS + HANDS
    # ---------------------------------------------------------------------
    for side, sign in [('L', -1), ('R', 1)]:
        shldr_c = Vector((sign * 0.22, 0.00, 1.44))
        elbow_c = Vector((sign * 0.27, 0.01, 1.20))
        cuff_c  = Vector((sign * 0.28, 0.02, 1.06)) # Rolled sleeve cuff at mid-forearm
        wrist_c = Vector((sign * 0.25, -0.04, 0.88))
        hand_c  = Vector((sign * 0.24, -0.06, 0.78))

        # Upper Sleeve (Crimson Shirt)
        sleeve_rings = [
            sculpt_ring(1.44, 0.092, 0.092, 0.092, 12, cx=shldr_c.x, cy=shldr_c.y),
            sculpt_ring(1.32, 0.086, 0.086, 0.086, 12, cx=sign * 0.25, cy=0.005),
            sculpt_ring(1.20, 0.082, 0.082, 0.082, 12, cx=elbow_c.x, cy=elbow_c.y),
            sculpt_ring(1.06, 0.085, 0.085, 0.085, 12, cx=cuff_c.x, cy=cuff_c.y),
        ]
        loft_rings(bm, sleeve_rings, mat_idx=3)

        # Rolled Cuff Bulge Ring
        bmesh.ops.create_cone(bm, cap_ends=False, radius1=0.092, radius2=0.088, depth=0.045, segments=12, matrix=Matrix.Translation(cuff_c))
        for f in bm.faces[-12:]: f.material_index = 3

        # Bare Forearms (Skin with muscular contour)
        forearm_rings = [
            sculpt_ring(1.03, 0.062, 0.058, 0.060, 12, cx=cuff_c.x, cy=cuff_c.y),
            sculpt_ring(0.95, 0.055, 0.050, 0.052, 12, cx=sign * 0.26, cy=-0.01),
            sculpt_ring(0.88, 0.048, 0.040, 0.044, 12, cx=wrist_c.x, cy=wrist_c.y),
        ]
        loft_rings(bm, forearm_rings, mat_idx=0) # Skin

        # Anatomical Hand & Fingers
        palm_mat = Matrix.Translation(hand_c) @ Matrix.Scale(0.040, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.024, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.075, 4, Vector((0, 0, 1)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=palm_mat)
        for f in bm.faces[-6:]: f.material_index = 0
        
        # 4 Fingers
        for f_idx, f_x in enumerate([-0.020, -0.006, 0.008, 0.020]):
            f_base = hand_c + Vector((sign * f_x, 0.0, -0.038))
            f_tip  = f_base + Vector((0.0, -0.012, -0.062))
            f_rings = [
                sculpt_ring(f_base.z, 0.009, 0.009, 0.009, 6, cx=f_base.x, cy=f_base.y),
                sculpt_ring((f_base.z + f_tip.z)*0.5, 0.008, 0.008, 0.008, 6, cx=f_base.x, cy=f_base.y - 0.006),
                sculpt_ring(f_tip.z, 0.006, 0.006, 0.006, 6, cx=f_tip.x, cy=f_tip.y),
            ]
            loft_rings(bm, f_rings, mat_idx=0, cap_top=True)
        # Thumb
        thumb_base = hand_c + Vector((sign * 0.026, -0.012, 0.010))
        thumb_tip  = thumb_base + Vector((sign * 0.020, -0.022, -0.035))
        t_rings = [
            sculpt_ring(thumb_base.z, 0.011, 0.011, 0.011, 6, cx=thumb_base.x, cy=thumb_base.y),
            sculpt_ring(thumb_tip.z, 0.008, 0.008, 0.008, 6, cx=thumb_tip.x, cy=thumb_tip.y),
        ]
        loft_rings(bm, t_rings, mat_idx=0, cap_top=True)

    # ---------------------------------------------------------------------
    # 4. CHARCOAL BLACK DENIM JEANS
    # ---------------------------------------------------------------------
    jeans_pelvis_rings = [
        sculpt_ring(0.94, 0.185, 0.142, 0.140, 24),
        sculpt_ring(0.86, 0.182, 0.138, 0.138, 24),
        sculpt_ring(0.78, 0.180, 0.135, 0.136, 24),
    ]
    loft_rings(bm, jeans_pelvis_rings, mat_idx=4) # Jeans

    for side, sign in [('L', -1), ('R', 1)]:
        leg_rings = [
            sculpt_ring(0.76, 0.115, 0.110, 0.112, 12, cx=sign * 0.105),
            sculpt_ring(0.60, 0.102, 0.096, 0.098, 12, cx=sign * 0.105),
            sculpt_ring(0.46, 0.088, 0.085, 0.086, 12, cx=sign * 0.105, cy=0.006), # Knee flexion
            sculpt_ring(0.28, 0.082, 0.076, 0.078, 12, cx=sign * 0.105),
            sculpt_ring(0.10, 0.076, 0.072, 0.074, 12, cx=sign * 0.105, cy=-0.005),
        ]
        loft_rings(bm, leg_rings, mat_idx=4)

        # Ankle Stacking Fold
        bmesh.ops.create_cone(bm, cap_ends=False, radius1=0.080, radius2=0.078, depth=0.04, segments=12, matrix=Matrix.Translation(Vector((sign * 0.105, -0.005, 0.105))))
        for f in bm.faces[-12:]: f.material_index = 4

    # ---------------------------------------------------------------------
    # 5. TRADITIONAL INDIAN LEATHER TOE-POST SANDALS & ANATOMICAL FEET
    # Sandal sole rests directly on the road surface: Z = 0.0 to 0.015m!
    # ---------------------------------------------------------------------
    sole_thick = 0.015
    for side, sign in [('L', -1), ('R', 1)]:
        fx = sign * 0.105

        # Anatomical Bare Foot (Skin)
        foot_rings = [
            sculpt_ring(0.085, 0.044, 0.040, 0.042, 12, cx=fx, cy=-0.002),
            sculpt_ring(0.052, 0.050, 0.044, 0.044, 12, cx=fx, cy=-0.015),
            sculpt_ring(0.032, 0.054, 0.036, 0.038, 12, cx=fx, cy=-0.055),
        ]
        loft_rings(bm, foot_rings, mat_idx=0) # Skin

        # 5 Individual Sculpted Toes
        for t_idx, t_dx in enumerate([-0.022, -0.010, 0.002, 0.013, 0.024]):
            t_base = Vector((fx + t_dx, -0.078, sole_thick + 0.010))
            t_tip  = t_base + Vector((0.0, -0.036, -0.003))
            r = 0.011 if t_idx == 0 else 0.008
            t_rings = [
                sculpt_ring(t_base.z, r, r, r, 6, cx=t_base.x, cy=t_base.y),
                sculpt_ring((t_base.z + t_tip.z)*0.5, r*0.95, r*0.95, r*0.95, 6, cx=t_base.x, cy=t_base.y - 0.018),
                sculpt_ring(t_tip.z, r*0.7, r*0.7, r*0.7, 6, cx=t_tip.x, cy=t_tip.y),
            ]
            loft_rings(bm, t_rings, mat_idx=0, cap_top=True)

        # Chappal Sole (Contoured rubber outsole & leather footbed)
        sole_rings = [
            sculpt_ring(sole_thick*0.5, 0.046, 0.035, 0.040, 12, cx=fx, cy=0.080), # Heel
            sculpt_ring(sole_thick*0.5, 0.044, 0.052, 0.046, 12, cx=fx, cy=0.000), # Arch
            sculpt_ring(sole_thick*0.5, 0.056, 0.048, 0.050, 12, cx=fx, cy=-0.082), # Ball
            sculpt_ring(sole_thick*0.5, 0.046, 0.024, 0.026, 12, cx=fx, cy=-0.130), # Toe edge
        ]
        loft_rings(bm, sole_rings, mat_idx=6, cap_bot=True, cap_top=True) # Sole

        # Leather Straps: Instep bridge strap (Dark Tanned Leather)
        s_left  = Vector((fx - 0.050, -0.020, sole_thick + 0.005))
        s_mid   = Vector((fx, -0.025, sole_thick + 0.050))
        s_right = Vector((fx + 0.050, -0.020, sole_thick + 0.005))
        for p1, p2 in [(s_left, s_mid), (s_mid, s_right)]:
            bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.012, radius2=0.012, depth=(p2 - p1).length, segments=6, matrix=Matrix.Translation((p1 + p2)*0.5) @ (p2 - p1).to_track_quat('Z', 'Y').to_matrix().to_4x4())
            for f in bm.faces[-8:]: f.material_index = 5 # Leather

        # Toe-Post
        tp_bot = Vector((fx - 0.005, -0.082, sole_thick + 0.005))
        tp_top = s_mid
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.008, radius2=0.009, depth=(tp_top - tp_bot).length, segments=6, matrix=Matrix.Translation((tp_bot + tp_top)*0.5) @ (tp_top - tp_bot).to_track_quat('Z', 'Y').to_matrix().to_4x4())
        for f in bm.faces[-8:]: f.material_index = 5 # Leather

    # ---------------------------------------------------------------------
    # CONVERT TO MESH OBJECT & SUBDIVISION SURFACE
    # ---------------------------------------------------------------------
    mesh = bpy.data.meshes.new("SKM_Raghunath_Mattre_MasterMesh")
    bm.to_mesh(mesh)
    bm.free()

    mat_list = [mat_skin, mat_hair, mat_beard, mat_shirt, mat_jeans, mat_leather, mat_sole, mat_eyes, mat_necklace]
    for m in mat_list:
        mesh.materials.append(m)

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new("SKM_Raghunath_Mattre", mesh)
    col.objects.link(obj)
    obj.location = world_origin

    # Subdivision modifier for organic skin and fabric smoothness
    sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # ---------------------------------------------------------------------
    # 6. ARMATURE & RIGGING (SK_Mannequin Hierarchy)
    # ---------------------------------------------------------------------
    arm_data = bpy.data.armatures.new("Armature_Raghunath_Data")
    arm_obj = bpy.data.objects.new("Armature_Raghunath", arm_data)
    col.objects.link(arm_obj)
    arm_obj.location = world_origin

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    bone_defs = [
        ("root", None, Vector((0, 0, 0)), Vector((0, 0, 0.1))),
        ("pelvis", "root", Vector((0, 0, 0.88)), Vector((0, 0, 0.98))),
        ("spine_01", "pelvis", Vector((0, 0, 0.98)), Vector((0, 0, 1.10))),
        ("spine_02", "spine_01", Vector((0, 0, 1.10)), Vector((0, 0, 1.22))),
        ("spine_03", "spine_02", Vector((0, 0, 1.22)), Vector((0, 0, 1.34))),
        ("spine_04", "spine_03", Vector((0, 0, 1.34)), Vector((0, 0, 1.44))),
        ("spine_05", "spine_04", Vector((0, 0, 1.44)), Vector((0, 0, 1.52))),
        ("neck_01", "spine_05", Vector((0, 0, 1.52)), Vector((0, 0, 1.62))),
        ("head", "neck_01", Vector((0, 0, 1.62)), Vector((0, 0, 1.82))),
        
        ("clavicle_l", "spine_05", Vector((0, 0, 1.46)), Vector((-0.18, 0, 1.46))),
        ("upperarm_l", "clavicle_l", Vector((-0.22, 0.00, 1.44)), Vector((-0.27, 0.01, 1.20))),
        ("lowerarm_l", "upperarm_l", Vector((-0.27, 0.01, 1.20)), Vector((-0.25, -0.04, 0.88))),
        ("hand_l", "lowerarm_l", Vector((-0.25, -0.04, 0.88)), Vector((-0.24, -0.06, 0.78))),
        
        ("clavicle_r", "spine_05", Vector((0, 0, 1.46)), Vector((0.18, 0, 1.46))),
        ("upperarm_r", "clavicle_r", Vector((0.22, 0.00, 1.44)), Vector((0.27, 0.01, 1.20))),
        ("lowerarm_r", "upperarm_r", Vector((0.27, 0.01, 1.20)), Vector((0.25, -0.04, 0.88))),
        ("hand_r", "lowerarm_r", Vector((0.25, -0.04, 0.88)), Vector((0.24, -0.06, 0.78))),
        
        ("thigh_l", "pelvis", Vector((-0.105, 0.00, 0.78)), Vector((-0.105, 0.006, 0.46))),
        ("calf_l", "thigh_l", Vector((-0.105, 0.006, 0.46)), Vector((-0.105, -0.005, 0.10))),
        ("foot_l", "calf_l", Vector((-0.105, -0.005, 0.10)), Vector((-0.105, -0.082, 0.02))),
        ("ball_l", "foot_l", Vector((-0.105, -0.082, 0.02)), Vector((-0.105, -0.130, 0.01))),
        
        ("thigh_r", "pelvis", Vector((0.105, 0.00, 0.78)), Vector((0.105, 0.006, 0.46))),
        ("calf_r", "thigh_r", Vector((0.105, 0.006, 0.46)), Vector((0.105, -0.005, 0.10))),
        ("foot_r", "calf_r", Vector((0.105, -0.005, 0.10)), Vector((0.105, -0.082, 0.02))),
        ("ball_r", "foot_r", Vector((0.105, -0.082, 0.02)), Vector((0.105, -0.130, 0.01))),

        ("ik_foot_root", "root", Vector((0, 0, 0)), Vector((0, 0.1, 0))),
        ("ik_foot_l", "ik_foot_root", Vector((-0.105, -0.02, 0.02)), Vector((-0.105, -0.12, 0.02))),
        ("ik_foot_r", "ik_foot_root", Vector((0.105, -0.02, 0.02)), Vector((0.105, -0.12, 0.02))),
        ("ik_hand_root", "root", Vector((0, 0, 1.4)), Vector((0, 0.1, 1.4))),
        ("ik_hand_l", "ik_hand_root", Vector((-0.24, -0.06, 0.78)), Vector((-0.24, -0.12, 0.78))),
        ("ik_hand_r", "ik_hand_root", Vector((0.24, -0.06, 0.78)), Vector((0.24, -0.12, 0.78))),
    ]

    for bname, p_name, head, tail in bone_defs:
        b = eb.new(bname)
        b.head = head
        b.tail = tail
        if p_name and p_name in eb:
            b.parent = eb[p_name]

    bpy.ops.object.mode_set(mode='OBJECT')

    # Vertex skinning
    for bname, _, _, _ in bone_defs:
        obj.vertex_groups.new(name=bname)

    arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    arm_mod.object = arm_obj
    arm_mod.use_vertex_groups = True

    vg_map = {vg.name: vg for vg in obj.vertex_groups}
    for v in mesh.vertices:
        co = v.co
        x, y, z = co.x, co.y, co.z
        
        # Head / Neck
        if z > 1.62:
            vg_map['head'].add([v.index], 1.0, 'REPLACE')
        elif z > 1.48:
            vg_map['neck_01'].add([v.index], 0.8, 'REPLACE')
            vg_map['head'].add([v.index], 0.2, 'ADD')
        # Arms
        elif abs(x) > 0.18 and z > 0.65:
            side = 'l' if x < 0 else 'r'
            if z > 1.25:
                vg_map[f'upperarm_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.92:
                vg_map[f'lowerarm_{side}'].add([v.index], 0.9, 'REPLACE')
            else:
                vg_map[f'hand_{side}'].add([v.index], 1.0, 'REPLACE')
        # Torso & Spine
        elif z > 1.35:
            vg_map['spine_04'].add([v.index], 0.6, 'REPLACE')
            vg_map['spine_05'].add([v.index], 0.4, 'ADD')
        elif z > 1.15:
            vg_map['spine_02'].add([v.index], 0.5, 'REPLACE')
            vg_map['spine_03'].add([v.index], 0.5, 'ADD')
        elif z > 0.82:
            vg_map['pelvis'].add([v.index], 0.7, 'REPLACE')
            vg_map['spine_01'].add([v.index], 0.3, 'ADD')
        # Legs
        else:
            side = 'l' if x < 0 else 'r'
            if z > 0.48:
                vg_map[f'thigh_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.12:
                vg_map[f'calf_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.03:
                vg_map[f'foot_{side}'].add([v.index], 0.9, 'REPLACE')
            else:
                vg_map[f'ball_{side}'].add([v.index], 1.0, 'REPLACE')

    obj.parent = arm_obj
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = Vector((0, 0, 0))

    # ---------------------------------------------------------------------
    # 7. AUTHORITATIVE REFERENCE POSE (Matching Photograph)
    # ---------------------------------------------------------------------
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose = arm_obj.pose

    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    action = bpy.data.actions.new("A_Raghunath_Authoritative_Pose")
    arm_obj.animation_data.action = action

    scene.frame_set(1)

    # Spine natural posture: confident, tall, athletic
    pose.bones['spine_02'].rotation_euler = Euler((0.02, 0, 0), 'XYZ')
    pose.bones['spine_04'].rotation_euler = Euler((0.02, 0, 0), 'XYZ')
    pose.bones['head'].rotation_euler = Euler((-0.02, 0, 0), 'XYZ')

    # Left Arm: Relaxed at side with natural slight bend
    pose.bones['upperarm_l'].rotation_euler = Euler((0.05, 0.03, 0.06), 'XYZ')
    pose.bones['lowerarm_l'].rotation_euler = Euler((0.12, 0.02, 0.04), 'XYZ')
    pose.bones['hand_l'].rotation_euler = Euler((0.04, 0, 0.02), 'XYZ')

    # Right Arm: Casual hand in front pocket (forearm bent inward and forward)
    pose.bones['upperarm_r'].rotation_euler = Euler((-0.18, -0.10, -0.22), 'XYZ')
    pose.bones['lowerarm_r'].rotation_euler = Euler((0.62, 0.20, -0.45), 'XYZ')
    pose.bones['hand_r'].rotation_euler = Euler((0.30, 0.12, -0.20), 'XYZ')

    # Legs: Weight slightly on left leg
    pose.bones['thigh_l'].rotation_euler = Euler((-0.02, 0, -0.02), 'XYZ')
    pose.bones['thigh_r'].rotation_euler = Euler((0.03, 0, 0.03), 'XYZ')

    for pb in pose.bones:
        pb.keyframe_insert(data_path="rotation_euler", frame=1)
        pb.keyframe_insert(data_path="location", frame=1)

    bpy.ops.object.mode_set(mode='OBJECT')

    # ---------------------------------------------------------------------
    # 8. CAMERAS FACING RAGHUNATH'S FRONT
    # Character faces -Y (South). Cameras are placed at -Y looking +Y!
    # ---------------------------------------------------------------------
    # Portrait Camera
    cam_p_name = "Cam_Raghunath_Hero_Portrait"
    cam_p = bpy.data.objects.get(cam_p_name)
    if not cam_p:
        cdata = bpy.data.cameras.new(f"{cam_p_name}_Data")
        cam_p = bpy.data.objects.new(cam_p_name, cdata)
        col.objects.link(cam_p)
    cam_p.data.lens = 52.0
    cam_p.data.clip_start = 0.1
    cam_p.data.clip_end = 25000.0
    # Camera at Y = 1097.8 (2.2m in front), height Z = 8.92 (eye level)
    cam_p.location = world_origin + Vector((0.02, -2.10, 1.68))
    target_face = world_origin + Vector((0.0, 0.0, 1.68))
    cam_p.rotation_euler = (target_face - cam_p.location).to_track_quat('-Z', 'Y').to_euler()

    # Full Body Camera
    cam_fb_name = "Cam_Raghunath_Full_Body"
    cam_fb = bpy.data.objects.get(cam_fb_name)
    if not cam_fb:
        cdata = bpy.data.cameras.new(f"{cam_fb_name}_Data")
        cam_fb = bpy.data.objects.new(cam_fb_name, cdata)
        col.objects.link(cam_fb)
    cam_fb.data.lens = 38.0
    cam_fb.data.clip_start = 0.1
    cam_fb.data.clip_end = 25000.0
    cam_fb.location = world_origin + Vector((0.12, -4.20, 1.02))
    target_body = world_origin + Vector((0.0, 0.0, 0.92))
    cam_fb.rotation_euler = (target_body - cam_fb.location).to_track_quat('-Z', 'Y').to_euler()

    # 3-Point Studio & Environment Lighting
    for l_name, l_type, l_pos, l_power, l_color in [
        ("LIGHT_Raghunath_Key", 'SPOT', world_origin + Vector((-0.9, -1.8, 2.3)), 300.0, (1.0, 0.96, 0.92)),
        ("LIGHT_Raghunath_Fill", 'POINT', world_origin + Vector((1.3, -1.5, 1.8)), 110.0, (0.88, 0.92, 1.0)),
        ("LIGHT_Raghunath_Rim", 'SPOT', world_origin + Vector((0.4, 1.6, 2.4)), 200.0, (1.0, 0.90, 0.80)),
    ]:
        light = bpy.data.objects.get(l_name)
        if not light:
            ldata = bpy.data.lights.new(name=f"{l_name}_Data", type=l_type)
            light = bpy.data.objects.new(l_name, ldata)
            col.objects.link(light)
        light.location = l_pos
        light.data.energy = l_power
        light.data.color = l_color
        if light.data.type == 'SPOT':
            light.rotation_euler = (target_face - light.location).to_track_quat('-Z', 'Y').to_euler()

    # Cycles Metal GPU Settings
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True
    scene.cycles.samples = 28
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.view_settings.exposure = -0.5
    scene.view_settings.look = 'High Contrast'

    os.makedirs("/Users/ms/Downloads/GRAI/renders", exist_ok=True)
    artifacts_dir = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012"

    # Render 1: Hero Portrait
    scene.camera = cam_p
    out_p = "/Users/ms/Downloads/GRAI/renders/raghunath_mattre_hero_portrait.png"
    scene.render.filepath = out_p
    print("Rendering Masterpiece Hero Portrait...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_p, os.path.join(artifacts_dir, "raghunath_mattre_hero_portrait.png"))

    # Render 2: Full Body Shot
    scene.camera = cam_fb
    out_fb = "/Users/ms/Downloads/GRAI/renders/raghunath_mattre_full_body.png"
    scene.render.filepath = out_fb
    print("Rendering Masterpiece Full Body...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_fb, os.path.join(artifacts_dir, "raghunath_mattre_full_body.png"))

    # Export FBX for Unreal Engine 5
    ue_dir = "/Users/ms/Downloads/GRAI/GRAI/Content/Characters/Raghunath"
    os.makedirs(ue_dir, exist_ok=True)
    fbx_path = os.path.join(ue_dir, "SKM_Raghunath_Mattre.fbx")

    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    print(f"Exporting UE5 Skeletal Mesh to {fbx_path}...")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_step=1.0
    )
    print("FBX Export completed successfully!")

    # Set Blender 3D viewport to camera view
    scene.camera = cam_p
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'MATERIAL'
                s.region_3d.view_perspective = 'CAMERA'
                s.region_3d.view_camera_zoom = 0.0
                a.tag_redraw()

    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Master Blend saved!")

if __name__ == '__main__':
    build_raghunath_masterpiece()
