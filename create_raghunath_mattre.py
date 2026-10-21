"""
GRAI — RAGHUNATH MATTRE: COMPLETE HIGH-FIDELITY CHARACTER
=========================================================
Authoritative Character Creation Script for Blender 5.2 & Unreal Engine 5
"""
import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Matrix, Euler, Quaternion

def build_raghunath_mattre():
    print("=== STARTING CREATION OF RAGHUNATH MATTRE ===")
    scene = bpy.context.scene

    # 1. CLEANUP OLD PLACEHOLDERS
    for o in list(bpy.data.objects):
        if o.name.startswith("HUMAN_") or o.name.startswith("RUNNER_") or o.name.startswith("CHARACTER_") or o.name.startswith("RAGHUNATH_"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_name = "Character_Raghunath_Mattre"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

    # 2. PBR MATERIALS
    def get_or_create_mat(name, base_color, roughness=0.5, metallic=0.0, sss_weight=0.0, specular=0.5):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        tree = m.node_tree
        bsdf = tree.nodes.get("Principled BSDF")
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
        m.diffuse_color = (base_color[0], base_color[1], base_color[2], 1.0)
        m.roughness = roughness
        return m

    # Materials
    mat_skin = get_or_create_mat("M_Raghunath_Skin", (0.58, 0.38, 0.28, 1.0), roughness=0.42, sss_weight=0.30)
    mat_hair = get_or_create_mat("M_Raghunath_Hair", (0.035, 0.03, 0.03, 1.0), roughness=0.55, specular=0.65)
    mat_beard = get_or_create_mat("M_Raghunath_Beard", (0.04, 0.035, 0.035, 1.0), roughness=0.65, specular=0.40)
    mat_shirt = get_or_create_mat("M_Raghunath_Shirt_Crimson", (0.32, 0.05, 0.08, 1.0), roughness=0.75, specular=0.25)
    mat_jeans = get_or_create_mat("M_Raghunath_Jeans_Charcoal", (0.08, 0.085, 0.10, 1.0), roughness=0.82, specular=0.20)
    mat_leather = get_or_create_mat("M_Raghunath_Sandals_Leather", (0.07, 0.05, 0.04, 1.0), roughness=0.50, specular=0.35)
    mat_sole = get_or_create_mat("M_Raghunath_Sandals_Sole", (0.02, 0.02, 0.02, 1.0), roughness=0.85, specular=0.15)
    mat_eyes = get_or_create_mat("M_Raghunath_Eyes", (0.10, 0.06, 0.04, 1.0), roughness=0.08, specular=0.95)
    mat_necklace = get_or_create_mat("M_Raghunath_Necklace", (0.02, 0.02, 0.02, 1.0), roughness=0.50, specular=0.30)

    # 3. ROOT & LOCATION
    # We place Raghunath on Marine Drive asphalt: X = -1007.0, Y = 1100.0, Z = 7.350m
    world_origin = Vector((-1007.0, 1100.0, 7.350))

    # 4. BUILD DETAILED HIGH-FIDELITY CHARACTER MESH
    bm = bmesh.new()

    # Helper: add cylinder/capsule limb
    def add_limb_section(bm, pt1, pt2, r1, r2, segs=12, mat_idx=0, vgroup_name=""):
        v_axis = pt2 - pt1
        length = v_axis.length
        if length < 0.001: return []
        mid = (pt1 + pt2) * 0.5
        rot = v_axis.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        trans = Matrix.Translation(mid)
        mat = trans @ rot
        verts = []
        for ring in range(segs):
            angle = (2.0 * math.pi * ring) / segs
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            # bottom ring
            p_bot = mat @ Vector((cos_a * r1, sin_a * r1, -length * 0.5))
            # top ring
            p_top = mat @ Vector((cos_a * r2, sin_a * r2, length * 0.5))
            v1 = bm.verts.new(p_bot)
            v2 = bm.verts.new(p_top)
            verts.extend([v1, v2])
        bm.verts.ensure_lookup_table()
        # faces
        for ring in range(segs):
            next_ring = (ring + 1) % segs
            v_bot_curr = verts[ring * 2]
            v_top_curr = verts[ring * 2 + 1]
            v_bot_next = verts[next_ring * 2]
            v_top_next = verts[next_ring * 2 + 1]
            f = bm.faces.new([v_bot_curr, v_bot_next, v_top_next, v_top_curr])
            f.material_index = mat_idx
            f.smooth = True
        return verts

    # Helper: add anatomical head mesh
    def build_anatomical_head(bm, center, scale=(0.11, 0.13, 0.15)):
        # Sculpted oval craniofacial form
        u_segs, v_segs = 20, 16
        head_verts = []
        for i in range(v_segs + 1):
            theta = (math.pi * i) / v_segs # 0 to pi
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            for j in range(u_segs):
                phi = (2.0 * math.pi * j) / u_segs # 0 to 2pi
                cos_p = math.cos(phi)
                sin_p = math.sin(phi)
                
                # Cranium & jaw shaping
                # Front is +Y, Back is -Y, Up is +Z, Sides are +/- X
                dx = cos_p * sin_t * scale[0]
                dy = sin_p * sin_t * scale[1]
                dz = cos_t * scale[2]
                
                # Jawline & chin definition (lower half)
                if cos_t < -0.2:
                    # Chin extends slightly forward at bottom
                    if sin_p > 0: # front
                        dy += 0.025 * ((-cos_t) - 0.2)
                        dx *= 0.85 # narrower jaw
                # Forehead flattening
                if cos_t > 0.3 and sin_p > 0:
                    dy *= 0.95
                
                pos = center + Vector((dx, dy, dz))
                v = bm.verts.new(pos)
                head_verts.append(v)
                
        bm.verts.ensure_lookup_table()
        for i in range(v_segs):
            for j in range(u_segs):
                j_next = (j + 1) % u_segs
                v1 = head_verts[i * u_segs + j]
                v2 = head_verts[i * u_segs + j_next]
                v3 = head_verts[(i + 1) * u_segs + j_next]
                v4 = head_verts[(i + 1) * u_segs + j]
                f = bm.faces.new([v1, v2, v3, v4])
                f.material_index = 0 # Skin
                f.smooth = True
        return head_verts

    # Helper: add hair volume (matching messy swept-back hair from reference)
    def build_hair_mesh(bm, head_center):
        # Layer of textured hair strands over top and sides
        u_segs, v_segs = 18, 12
        hair_verts = []
        for i in range(v_segs + 1):
            theta = (0.65 * math.pi * i) / v_segs # top and mid head
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            for j in range(u_segs):
                phi = (2.0 * math.pi * j) / u_segs
                cos_p = math.cos(phi)
                sin_p = math.sin(phi)
                
                # Hair radius is larger than cranium (adds volume)
                r_x = 0.125
                r_y = 0.145
                r_z = 0.170
                # Front quiff / swept back volume
                if cos_t > 0.4 and sin_p > 0.2:
                    r_z += 0.035 # high front volume
                    r_y += 0.025 # swept front
                # Messy locks variation
                wave = 0.012 * math.sin(phi * 4.0) * math.cos(theta * 3.0)
                
                dx = cos_p * sin_t * (r_x + wave)
                dy = sin_p * sin_t * (r_y + wave)
                dz = cos_t * (r_z + wave)
                
                pos = head_center + Vector((dx, dy, dz))
                v = bm.verts.new(pos)
                hair_verts.append(v)
                
        bm.verts.ensure_lookup_table()
        for i in range(v_segs):
            for j in range(u_segs):
                j_next = (j + 1) % u_segs
                v1 = hair_verts[i * u_segs + j]
                v2 = hair_verts[i * u_segs + j_next]
                v3 = hair_verts[(i + 1) * u_segs + j_next]
                v4 = hair_verts[(i + 1) * u_segs + j]
                f = bm.faces.new([v1, v2, v3, v4])
                f.material_index = 1 # Hair
                f.smooth = True
        return hair_verts

    # Helper: add beard & mustache geometry
    def build_beard_mesh(bm, head_center):
        # Contoured stubble layer around lower jaw, chin and upper lip
        u_segs, v_segs = 14, 6
        beard_verts = []
        for i in range(v_segs + 1):
            # Focus on lower face (theta from 0.65 pi to 0.95 pi)
            t_frac = i / v_segs
            theta = (0.68 + 0.27 * t_frac) * math.pi
            sin_t = math.sin(theta)
            cos_t = math.cos(theta)
            for j in range(u_segs):
                # Only front and jawline (phi from -0.3 pi to 0.3 pi)
                p_frac = (j / (u_segs - 1)) - 0.5 # -0.5 to 0.5
                phi = p_frac * 0.75 * math.pi
                cos_p = math.cos(phi)
                sin_p = math.sin(phi)
                
                dx = sin_p * sin_t * 0.105
                dy = cos_p * sin_t * 0.128 + 0.005 # slightly outside skin
                dz = cos_t * 0.152
                
                pos = head_center + Vector((dx, dy, dz))
                v = bm.verts.new(pos)
                beard_verts.append(v)
                
        bm.verts.ensure_lookup_table()
        for i in range(v_segs):
            for j in range(u_segs - 1):
                v1 = beard_verts[i * u_segs + j]
                v2 = beard_verts[i * u_segs + (j + 1)]
                v3 = beard_verts[(i + 1) * u_segs + (j + 1)]
                v4 = beard_verts[(i + 1) * u_segs + j]
                f = bm.faces.new([v1, v2, v3, v4])
                f.material_index = 2 # Beard
                f.smooth = True

    # Helper: add eyes
    def build_eyes(bm, head_center):
        for side in [-1, 1]:
            eye_pos = head_center + Vector((side * 0.038, 0.098, 0.025))
            bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.015, matrix=Matrix.Translation(eye_pos))
            # Set eye material
            for f in bm.faces[-16:]:
                f.material_index = 7 # Eyes
                f.smooth = True

    # Helper: add black cord necklace
    def build_necklace(bm, neck_center):
        # Ring around neck with slight downward dip in front
        segs = 16
        r_neck = 0.082
        for i in range(segs):
            angle = (2.0 * math.pi * i) / segs
            next_angle = (2.0 * math.pi * (i + 1)) / segs
            # Dip in front (+Y)
            dip = 0.035 * max(0.0, math.sin(angle))
            dip_next = 0.035 * max(0.0, math.sin(next_angle))
            p1 = neck_center + Vector((math.cos(angle) * r_neck, math.sin(angle) * r_neck, -dip))
            p2 = neck_center + Vector((math.cos(next_angle) * r_neck, math.sin(next_angle) * r_neck, -dip_next))
            add_limb_section(bm, p1, p2, 0.004, 0.004, segs=4, mat_idx=8)

    # ---------------------------------------------------------------------
    # BUILD ANATOMICAL BODY PARTS
    # ---------------------------------------------------------------------
    # Head & Neck
    head_center = Vector((0, 0, 1.70))
    neck_base = Vector((0, 0, 1.48))
    neck_top = Vector((0, 0, 1.62))
    
    # Neck (Skin)
    add_limb_section(bm, neck_base, neck_top, 0.075, 0.068, segs=14, mat_idx=0)
    # Head (Skin)
    build_anatomical_head(bm, head_center)
    # Hair
    build_hair_mesh(bm, head_center)
    # Beard
    build_beard_mesh(bm, head_center)
    # Eyes
    build_eyes(bm, head_center)
    # Necklace
    build_necklace(bm, neck_top - Vector((0, 0, 0.04)))

    # Crimson Casual Shirt (Torso + Rolled Sleeves)
    # Torso: Chest to waist, open V-neck
    chest_pos = Vector((0, 0, 1.42))
    waist_pos = Vector((0, 0, 1.15))
    hips_pos = Vector((0, 0, 0.98))
    # Upper chest / shoulders
    add_limb_section(bm, waist_pos, chest_pos, 0.175, 0.220, segs=16, mat_idx=3)
    # Lower torso / waist drape
    add_limb_section(bm, hips_pos, waist_pos, 0.185, 0.175, segs=16, mat_idx=3)

    # Shirt Collar: Open lapels
    for side in [-1, 1]:
        c1 = chest_pos + Vector((side * 0.05, 0.14, 0.05))
        c2 = chest_pos + Vector((side * 0.11, 0.08, -0.06))
        add_limb_section(bm, c1, c2, 0.025, 0.015, segs=6, mat_idx=3)
    # Left Chest Pocket
    pocket_pos = chest_pos + Vector((-0.08, 0.185, -0.04))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(pocket_pos) @ Matrix.Scale(0.06, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.005, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.07, 4, Vector((0, 0, 1))))
    for f in bm.faces[-6:]:
        f.material_index = 3

    # Arms (Crimson Shirt upper sleeves + Bare Forearms + Hands)
    for side, sign in [('L', -1), ('R', 1)]:
        shldr = chest_pos + Vector((sign * 0.23, 0.0, 0.02))
        elbow = shldr + Vector((sign * 0.07, 0.02, -0.32))
        mid_forearm = elbow + Vector((sign * 0.03, 0.04, -0.16)) # rolled cuff location
        wrist = mid_forearm + Vector((sign * 0.03, 0.05, -0.18))
        hand = wrist + Vector((sign * 0.02, 0.03, -0.10))

        # Upper Arm (Crimson Shirt Fabric)
        add_limb_section(bm, shldr, elbow, 0.085, 0.075, segs=12, mat_idx=3)
        # Rolled Sleeve Cuff (Crimson Shirt rolled cuff bunched at mid-forearm)
        add_limb_section(bm, elbow, mid_forearm, 0.082, 0.078, segs=12, mat_idx=3)
        # Cuff ring bulge
        bmesh.ops.create_cone(bm, cap_ends=False, radius1=0.085, radius2=0.085, depth=0.04, segments=12, matrix=Matrix.Translation(mid_forearm))
        for f in bm.faces[-12:]: f.material_index = 3

        # Bare Forearm (Skin: Melanin South Asian skin with muscle contour)
        add_limb_section(bm, mid_forearm, wrist, 0.062, 0.048, segs=12, mat_idx=0)

        # Hand & Fingers (Skin)
        # Palm
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(hand) @ Matrix.Scale(0.038, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.065, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.085, 4, Vector((0, 0, 1))))
        for f in bm.faces[-6:]: f.material_index = 0
        # 5 Fingers
        for f_idx, f_offset in enumerate([-0.025, -0.010, 0.005, 0.020]):
            f_base = hand + Vector((sign * f_offset, 0.02, -0.04))
            f_tip = f_base + Vector((0, 0.01, -0.065))
            add_limb_section(bm, f_base, f_tip, 0.010, 0.008, segs=6, mat_idx=0)
        # Thumb
        thumb_base = hand + Vector((sign * 0.030, 0.04, 0.01))
        thumb_tip = thumb_base + Vector((sign * 0.025, 0.03, -0.035))
        add_limb_section(bm, thumb_base, thumb_tip, 0.012, 0.009, segs=6, mat_idx=0)

    # Charcoal Black Denim Jeans (Hips, Thighs, Calves, Ankle folds)
    for side, sign in [('L', -1), ('R', 1)]:
        hip = hips_pos + Vector((sign * 0.11, 0.0, 0.0))
        knee = hip + Vector((0.0, 0.02, -0.46))
        ankle = knee + Vector((0.0, -0.02, -0.42))
        
        # Thigh (Jeans)
        add_limb_section(bm, hip, knee, 0.125, 0.095, segs=14, mat_idx=4)
        # Calf (Jeans)
        add_limb_section(bm, knee, ankle, 0.092, 0.082, segs=14, mat_idx=4)
        # Ankle bunching fold ring
        bmesh.ops.create_cone(bm, cap_ends=False, radius1=0.088, radius2=0.084, depth=0.05, segments=12, matrix=Matrix.Translation(ankle + Vector((0, 0, 0.02))))
        for f in bm.faces[-12:]: f.material_index = 4

    # Feet & Traditional Indian Leather Toe-Post Sandals (Chappals)
    for side, sign in [('L', -1), ('R', 1)]:
        ankle = hips_pos + Vector((sign * 0.11, 0.0, -0.88))
        foot_center = ankle + Vector((0.0, 0.07, -0.05))
        sole_z = 0.015

        # Bare Foot (Skin)
        # Heel to ball
        heel = Vector((sign * 0.11, -0.02, sole_z + 0.035))
        ball = Vector((sign * 0.11, 0.14, sole_z + 0.025))
        add_limb_section(bm, heel, ball, 0.048, 0.055, segs=10, mat_idx=0)
        # 5 Individual Sculpted Toes
        for t_idx, t_x in enumerate([-0.025, -0.012, 0.001, 0.014, 0.026]):
            t_base = ball + Vector((t_x, 0.04, 0.0))
            t_tip = t_base + Vector((0.0, 0.035, -0.005))
            r = 0.011 if t_idx == 0 else 0.008 # Big toe thicker
            add_limb_section(bm, t_base, t_tip, r, r * 0.85, segs=6, mat_idx=0)

        # Chappal Sole (Rubber outsole + Leather footbed)
        sole_mat = Matrix.Translation(Vector((sign * 0.11, 0.07, sole_z))) @ Matrix.Scale(0.062, 4, Vector((1, 0, 0))) @ Matrix.Scale(0.140, 4, Vector((0, 1, 0))) @ Matrix.Scale(0.014, 4, Vector((0, 0, 1)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=sole_mat)
        for f in bm.faces[-6:]: f.material_index = 6 # Sole

        # Chappal Leather Straps
        # Instep Bridge Strap (Dark Leather)
        strap1 = Vector((sign * 0.11 - 0.055, 0.05, sole_z + 0.01))
        strap_top = Vector((sign * 0.11, 0.06, sole_z + 0.055))
        strap2 = Vector((sign * 0.11 + 0.055, 0.05, sole_z + 0.01))
        add_limb_section(bm, strap1, strap_top, 0.014, 0.014, segs=6, mat_idx=5)
        add_limb_section(bm, strap_top, strap2, 0.014, 0.014, segs=6, mat_idx=5)

        # Toe-Post (between big toe and 2nd toe)
        post_bot = Vector((sign * 0.11 - 0.006, 0.155, sole_z + 0.01))
        post_top = strap_top
        add_limb_section(bm, post_bot, post_top, 0.008, 0.010, segs=6, mat_idx=5)

    # ---------------------------------------------------------------------
    # CONVERT BMESH TO MESH OBJECT
    # ---------------------------------------------------------------------
    mesh_raghunath = bpy.data.meshes.new("SKM_Raghunath_Mattre_Mesh")
    bm.to_mesh(mesh_raghunath)
    bm.free()

    # Assign all 9 Materials in order
    materials_list = [mat_skin, mat_hair, mat_beard, mat_shirt, mat_jeans, mat_leather, mat_sole, mat_eyes, mat_necklace]
    for m in materials_list:
        mesh_raghunath.materials.append(m)

    for p in mesh_raghunath.polygons:
        p.use_smooth = True

    obj_raghunath = bpy.data.objects.new("SKM_Raghunath_Mattre", mesh_raghunath)
    col.objects.link(obj_raghunath)
    obj_raghunath.location = world_origin

    # ---------------------------------------------------------------------
    # 5. UE5 HUMANOID SKELETON (SK_Mannequin Hierarchy)
    # ---------------------------------------------------------------------
    arm_data = bpy.data.armatures.new("Armature_Raghunath_Data")
    arm_obj = bpy.data.objects.new("Armature_Raghunath", arm_data)
    col.objects.link(arm_obj)
    arm_obj.location = world_origin

    # Switch to edit mode to create bones
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    # UE5 Bone Definitions: (name, parent, head_rel, tail_rel)
    bone_defs = [
        ("root", None, Vector((0, 0, 0)), Vector((0, 0, 0.1))),
        ("pelvis", "root", Vector((0, 0, 0.94)), Vector((0, 0, 1.04))),
        ("spine_01", "pelvis", Vector((0, 0, 1.04)), Vector((0, 0, 1.14))),
        ("spine_02", "spine_01", Vector((0, 0, 1.14)), Vector((0, 0, 1.25))),
        ("spine_03", "spine_02", Vector((0, 0, 1.25)), Vector((0, 0, 1.36))),
        ("spine_04", "spine_03", Vector((0, 0, 1.36)), Vector((0, 0, 1.45))),
        ("spine_05", "spine_04", Vector((0, 0, 1.45)), Vector((0, 0, 1.54))),
        ("neck_01", "spine_05", Vector((0, 0, 1.54)), Vector((0, 0, 1.62))),
        ("head", "neck_01", Vector((0, 0, 1.62)), Vector((0, 0, 1.84))),
        
        # Left Arm
        ("clavicle_l", "spine_05", Vector((0, 0, 1.46)), Vector((-0.18, 0, 1.46))),
        ("upperarm_l", "clavicle_l", Vector((-0.23, 0, 1.44)), Vector((-0.30, 0.02, 1.12))),
        ("lowerarm_l", "upperarm_l", Vector((-0.30, 0.02, 1.12)), Vector((-0.33, 0.07, 0.82))),
        ("hand_l", "lowerarm_l", Vector((-0.33, 0.07, 0.82)), Vector((-0.35, 0.10, 0.72))),
        
        # Right Arm
        ("clavicle_r", "spine_05", Vector((0, 0, 1.46)), Vector((0.18, 0, 1.46))),
        ("upperarm_r", "clavicle_r", Vector((0.23, 0, 1.44)), Vector((0.30, 0.02, 1.12))),
        ("lowerarm_r", "upperarm_r", Vector((0.30, 0.02, 1.12)), Vector((0.33, 0.07, 0.82))),
        ("hand_r", "lowerarm_r", Vector((0.33, 0.07, 0.82)), Vector((0.35, 0.10, 0.72))),
        
        # Left Leg
        ("thigh_l", "pelvis", Vector((-0.11, 0, 0.94)), Vector((-0.11, 0.02, 0.50))),
        ("calf_l", "thigh_l", Vector((-0.11, 0.02, 0.50)), Vector((-0.11, -0.02, 0.08))),
        ("foot_l", "calf_l", Vector((-0.11, -0.02, 0.08)), Vector((-0.11, 0.14, 0.02))),
        ("ball_l", "foot_l", Vector((-0.11, 0.14, 0.02)), Vector((-0.11, 0.20, 0.01))),
        
        # Right Leg
        ("thigh_r", "pelvis", Vector((0.11, 0, 0.94)), Vector((0.11, 0.02, 0.50))),
        ("calf_r", "thigh_r", Vector((0.11, 0.02, 0.50)), Vector((0.11, -0.02, 0.08))),
        ("foot_r", "calf_r", Vector((0.11, -0.02, 0.08)), Vector((0.11, 0.14, 0.02))),
        ("ball_r", "foot_r", Vector((0.11, 0.14, 0.02)), Vector((0.11, 0.20, 0.01))),
        
        # IK Bones (UE5 Standard)
        ("ik_foot_root", "root", Vector((0, 0, 0)), Vector((0, 0.1, 0))),
        ("ik_foot_l", "ik_foot_root", Vector((-0.11, 0.02, 0.02)), Vector((-0.11, 0.12, 0.02))),
        ("ik_foot_r", "ik_foot_root", Vector((0.11, 0.02, 0.02)), Vector((0.11, 0.12, 0.02))),
        ("ik_hand_root", "root", Vector((0, 0, 1.4)), Vector((0, 0.1, 1.4))),
        ("ik_hand_l", "ik_hand_root", Vector((-0.35, 0.10, 0.72)), Vector((-0.35, 0.15, 0.72))),
        ("ik_hand_r", "ik_hand_root", Vector((0.35, 0.10, 0.72)), Vector((0.35, 0.15, 0.72)))
    ]

    for bname, p_name, head, tail in bone_defs:
        b = eb.new(bname)
        b.head = head
        b.tail = tail
        if p_name and p_name in eb:
            b.parent = eb[p_name]

    bpy.ops.object.mode_set(mode='OBJECT')

    # 6. SKINNING & VERTEX GROUPS
    for bname, _, _, _ in bone_defs:
        obj_raghunath.vertex_groups.new(name=bname)

    # Armature modifier
    mod = obj_raghunath.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    mod.use_vertex_groups = True

    # Vertex weights assignment based on Z and proximity
    vg_map = {vg.name: vg for vg in obj_raghunath.vertex_groups}
    for v in mesh_raghunath.vertices:
        co = v.co # relative to object origin
        x, y, z = co.x, co.y, co.z
        
        # Head / Neck
        if z > 1.60:
            vg_map['head'].add([v.index], 1.0, 'REPLACE')
        elif z > 1.50:
            vg_map['neck_01'].add([v.index], 0.8, 'REPLACE')
            vg_map['head'].add([v.index], 0.2, 'ADD')
        # Arms
        elif abs(x) > 0.18 and z > 0.65:
            side = 'l' if x < 0 else 'r'
            if z > 1.25:
                vg_map[f'upperarm_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.90:
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
        elif z > 0.92:
            vg_map['pelvis'].add([v.index], 0.7, 'REPLACE')
            vg_map['spine_01'].add([v.index], 0.3, 'ADD')
        # Legs
        else:
            side = 'l' if x < 0 else 'r'
            if z > 0.50:
                vg_map[f'thigh_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.10:
                vg_map[f'calf_{side}'].add([v.index], 0.9, 'REPLACE')
            elif z > 0.04:
                vg_map[f'foot_{side}'].add([v.index], 0.9, 'REPLACE')
            else:
                vg_map[f'ball_{side}'].add([v.index], 1.0, 'REPLACE')

    # Parent mesh to armature
    obj_raghunath.parent = arm_obj

    # ---------------------------------------------------------------------
    # 7. ANIMATION: CANONICAL REFERENCE POSE (Frame 1) & NATURAL WALK (Frames 1-48)
    # ---------------------------------------------------------------------
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose = arm_obj.pose

    # Set interpolation to BEZIER
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    action = bpy.data.actions.new("A_Raghunath_Locomotion")
    arm_obj.animation_data.action = action

    # FRAME 1: Authoritative Stance matching Reference Photo:
    # Confident standing stance, right hand casual near pocket, intense gaze forward
    scene.frame_set(1)
    
    # Spine natural posture
    pose.bones['spine_02'].rotation_euler = Euler((0.02, 0, 0), 'XYZ')
    pose.bones['spine_04'].rotation_euler = Euler((0.03, 0, 0), 'XYZ')
    pose.bones['head'].rotation_euler = Euler((-0.03, 0, 0), 'XYZ')
    
    # Left Arm: Relaxed at side with natural slight bend
    pose.bones['upperarm_l'].rotation_euler = Euler((0.08, 0.05, 0.12), 'XYZ')
    pose.bones['lowerarm_l'].rotation_euler = Euler((0.18, 0, 0.08), 'XYZ')
    pose.bones['hand_l'].rotation_euler = Euler((0.05, 0, 0.05), 'XYZ')

    # Right Arm: Casual hand in pocket pose (forearm bent inward, hand resting at hip)
    pose.bones['upperarm_r'].rotation_euler = Euler((-0.18, -0.10, -0.22), 'XYZ')
    pose.bones['lowerarm_r'].rotation_euler = Euler((0.55, 0.20, -0.45), 'XYZ')
    pose.bones['hand_r'].rotation_euler = Euler((0.30, 0.10, -0.20), 'XYZ')

    # Legs: Weight slightly on left leg, right leg relaxed
    pose.bones['thigh_l'].rotation_euler = Euler((-0.03, 0, -0.02), 'XYZ')
    pose.bones['thigh_r'].rotation_euler = Euler((0.04, 0, 0.03), 'XYZ')
    
    for pb in pose.bones:
        pb.keyframe_insert(data_path="rotation_euler", frame=1)
        pb.keyframe_insert(data_path="location", frame=1)

    # 48-Frame Grounded Locomotion Walk Cycle
    for f in range(2, 49):
        t = ((f - 1) / 48.0) * 2.0 * math.pi
        scene.frame_set(f)
        
        # Hip sway & vertical bounce (two bounces per stride cycle)
        bounce = 0.025 * abs(math.sin(t))
        sway = 0.020 * math.sin(t)
        pose.bones['pelvis'].location = Vector((sway, 0, -bounce))
        pose.bones['pelvis'].rotation_euler = Euler((0, 0.03 * math.sin(t), 0.05 * math.sin(t)), 'XYZ')
        
        # Stride phase
        thigh_swing = 0.42 * math.sin(t)
        knee_flex = 0.50 * max(0.0, -math.sin(t)) # flex when leg swinging forward
        pose.bones['thigh_l'].rotation_euler = Euler((thigh_swing, 0, 0), 'XYZ')
        pose.bones['calf_l'].rotation_euler = Euler((knee_flex, 0, 0), 'XYZ')
        
        pose.bones['thigh_r'].rotation_euler = Euler((-thigh_swing, 0, 0), 'XYZ')
        pose.bones['calf_r'].rotation_euler = Euler((0.50 * max(0.0, math.sin(t)), 0, 0), 'XYZ')
        
        # Arm swing (opposite to leg swing)
        arm_swing = 0.35 * math.sin(t)
        pose.bones['upperarm_l'].rotation_euler = Euler((-arm_swing, 0, 0.10), 'XYZ')
        pose.bones['lowerarm_l'].rotation_euler = Euler((0.25 + 0.15 * max(0.0, -arm_swing), 0, 0), 'XYZ')
        
        # Right arm preserves casual style with dampened swing
        pose.bones['upperarm_r'].rotation_euler = Euler((arm_swing * 0.7 - 0.10, -0.05, -0.15), 'XYZ')
        pose.bones['lowerarm_r'].rotation_euler = Euler((0.35 + 0.15 * max(0.0, arm_swing), 0.10, -0.20), 'XYZ')
        
        # Spine counter-rotation & head stabilization
        pose.bones['spine_02'].rotation_euler = Euler((0.02, 0, -0.04 * math.sin(t)), 'XYZ')
        pose.bones['head'].rotation_euler = Euler((-0.02, 0, 0.02 * math.sin(t)), 'XYZ')
        
        for pb in pose.bones:
            pb.keyframe_insert(data_path="rotation_euler", frame=f)
            pb.keyframe_insert(data_path="location", frame=f)

    bpy.ops.object.mode_set(mode='OBJECT')
    print("Character modeled, rigged, and animated successfully!")

    # ---------------------------------------------------------------------
    # 8. CAMERAS & PHOTOREAL CYCLES METAL RENDERING
    # ---------------------------------------------------------------------
    scene.frame_set(1) # Authoritative reference pose

    # Hero Portrait Camera (Tack-sharp 50mm portrait lens framing face, beard, hair, open collar)
    cam_p_name = "Cam_Raghunath_Hero_Portrait"
    cam_p = bpy.data.objects.get(cam_p_name)
    if not cam_p:
        cdata = bpy.data.cameras.new(f"{cam_p_name}_Data")
        cam_p = bpy.data.objects.new(cam_p_name, cdata)
        col.objects.link(cam_p)
    cam_p.data.lens = 50.0
    cam_p.data.clip_start = 0.1
    cam_p.data.clip_end = 25000.0
    # Position: 2.2m in front, focused on eyes/face at Z ~ 8.95m
    cam_p.location = world_origin + Vector((0.08, 2.10, 1.68))
    target_face = world_origin + Vector((0, 0, 1.68))
    cam_p.rotation_euler = (target_face - cam_p.location).to_track_quat('-Z', 'Y').to_euler()

    # Hero Full-Body Camera (Framing Raghunath from head to toe-post sandals on Marine Drive road)
    cam_fb_name = "Cam_Raghunath_Full_Body"
    cam_fb = bpy.data.objects.get(cam_fb_name)
    if not cam_fb:
        cdata = bpy.data.cameras.new(f"{cam_fb_name}_Data")
        cam_fb = bpy.data.objects.new(cam_fb_name, cdata)
        col.objects.link(cam_fb)
    cam_fb.data.lens = 38.0
    cam_fb.data.clip_start = 0.1
    cam_fb.data.clip_end = 25000.0
    cam_fb.location = world_origin + Vector((0.35, 4.40, 1.05))
    target_body = world_origin + Vector((0, 0, 0.95))
    cam_fb.rotation_euler = (target_body - cam_fb.location).to_track_quat('-Z', 'Y').to_euler()

    # Configure Cycles Metal GPU
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True
    scene.cycles.samples = 36
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920 # Vertical format matching reference photo aspect
    scene.view_settings.exposure = -0.5
    scene.view_settings.look = 'High Contrast'

    os.makedirs("/Users/ms/Downloads/GRAI/renders", exist_ok=True)
    artifacts_dir = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012"

    # Render 1: Hero Portrait Close-Up
    scene.camera = cam_p
    out_portrait = "/Users/ms/Downloads/GRAI/renders/raghunath_mattre_hero_portrait.png"
    scene.render.filepath = out_portrait
    print("Rendering Raghunath Mattre Hero Portrait...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_portrait, os.path.join(artifacts_dir, "raghunath_mattre_hero_portrait.png"))

    # Render 2: Full-Body Authoritative Reference Shot
    scene.camera = cam_fb
    out_fullbody = "/Users/ms/Downloads/GRAI/renders/raghunath_mattre_full_body.png"
    scene.render.filepath = out_fullbody
    print("Rendering Raghunath Mattre Full Body...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_fullbody, os.path.join(artifacts_dir, "raghunath_mattre_full_body.png"))

    # ---------------------------------------------------------------------
    # 9. EXPORT FBX FOR UNREAL ENGINE 5
    # ---------------------------------------------------------------------
    ue_char_dir = "/Users/ms/Downloads/GRAI/GRAI/Content/Characters/Raghunath"
    os.makedirs(ue_char_dir, exist_ok=True)
    fbx_out = os.path.join(ue_char_dir, "SKM_Raghunath_Mattre.fbx")
    
    # Select only Raghunath mesh and armature for export
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    obj_raghunath.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    print(f"Exporting UE5 Skeletal Mesh to {fbx_out}...")
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
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

    # ---------------------------------------------------------------------
    # 10. SYNC ACTIVE BLENDER VIEWPORT
    # ---------------------------------------------------------------------
    scene.camera = cam_fb
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'MATERIAL'
                s.region_3d.view_perspective = 'CAMERA'
                s.region_3d.view_camera_zoom = 0.0
                a.tag_redraw()

    # Save Master Blend file
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Master Blend saved with Raghunath Mattre active!")

if __name__ == '__main__':
    build_raghunath_mattre()
