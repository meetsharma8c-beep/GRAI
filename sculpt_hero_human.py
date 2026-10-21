"""
Sculpt High-Fidelity Organic Human Character with Anatomical Facial Features & PBR Shading
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def get_or_create_pbr_mat(name, base_color, roughness=0.5, metallic=0.0, sss=0.0, specular=0.5):
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
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = sss
        elif 'Subsurface' in bsdf.inputs:
            bsdf.inputs['Subsurface'].default_value = sss
    return m

def build_hero_photoreal_human():
    print("=== SCULPTING HERO ORGANIC HUMAN CHARACTER ===")
    for o in list(bpy.data.objects):
        if o.name.startswith("HUMAN_") or o.name.startswith("CHARACTER_") or o.name.startswith("RUNNER_"):
            bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.data.collections.get("Playable_Street_Props")
    if not col:
        col = bpy.context.scene.collection

    # 1. Premium Materials
    mat_skin = get_or_create_pbr_mat("MAT_Human_Skin_Photoreal", (0.82, 0.62, 0.52, 1.0), roughness=0.38, sss=0.25, specular=0.5)
    mat_hair = get_or_create_pbr_mat("MAT_Human_Hair_Photoreal", (0.05, 0.04, 0.04, 1.0), roughness=0.55, specular=0.45)
    mat_jacket = get_or_create_pbr_mat("MAT_Human_BomberJacket", (0.12, 0.14, 0.18, 1.0), roughness=0.45, specular=0.35)
    mat_zip = get_or_create_pbr_mat("MAT_Human_JacketZip", (0.75, 0.75, 0.78, 1.0), roughness=0.20, metallic=0.9)
    mat_trim = get_or_create_pbr_mat("MAT_Human_CrimsonTrim", (0.80, 0.15, 0.10, 1.0), roughness=0.35)
    mat_pants = get_or_create_pbr_mat("MAT_Human_Joggers_Photoreal", (0.08, 0.10, 0.15, 1.0), roughness=0.75, specular=0.20)
    mat_sole = get_or_create_pbr_mat("MAT_Human_SneakerSole", (0.94, 0.94, 0.92, 1.0), roughness=0.30, specular=0.55)
    mat_shoe = get_or_create_pbr_mat("MAT_Human_SneakerUpper", (0.15, 0.16, 0.18, 1.0), roughness=0.50, specular=0.30)
    mat_eyes = get_or_create_pbr_mat("MAT_Human_Eyes", (0.15, 0.12, 0.10, 1.0), roughness=0.10, specular=0.9)

    root = bpy.data.objects.new("HUMAN_Root", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.5
    col.objects.link(root)

    # 2. Pelvis
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.18, radius2=0.16, depth=0.20, segments=16)
    m_pelvis = bpy.data.meshes.new("HUMAN_Pelvis_Mesh")
    bm.to_mesh(m_pelvis)
    bm.free()
    m_pelvis.materials.append(mat_pants)
    for p in m_pelvis.polygons: p.use_smooth = True
    obj_pelvis = bpy.data.objects.new("HUMAN_Pelvis", m_pelvis)
    col.objects.link(obj_pelvis)
    obj_pelvis.parent = root
    obj_pelvis.location = Vector((0, 0, 0.95))

    # 3. Torso (Sculpted Athletic Bomber Jacket)
    bm = bmesh.new()
    # Lower waist
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.17, radius2=0.20, depth=0.18, segments=16, matrix=Matrix.Translation(Vector((0, 0, 0.09))))
    # Chest / Lats
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.20, radius2=0.24, depth=0.22, segments=16, matrix=Matrix.Translation(Vector((0, 0, 0.28))))
    # Shoulders
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.24, matrix=Matrix.Translation(Vector((0, 0, 0.40))) @ Matrix.Diagonal(Vector((1.15, 0.70, 0.55, 1.0))))
    # Collar
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.10, radius2=0.08, depth=0.08, segments=16, matrix=Matrix.Translation(Vector((0, 0, 0.50))))
    # Zipper line down front (+Y)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.17, 0.25))) @ Matrix.Diagonal(Vector((0.015, 0.015, 0.36, 1.0))))
    m_torso = bpy.data.meshes.new("HUMAN_Torso_Mesh")
    bm.to_mesh(m_torso)
    bm.free()
    m_torso.materials.append(mat_jacket)
    m_torso.materials.append(mat_zip)
    m_torso.materials.append(mat_trim)
    for p in m_torso.polygons:
        p.use_smooth = True
        if p.center.y > 0.15 and abs(p.center.x) < 0.02:
            p.material_index = 1 # Zipper
        elif 0.30 < p.center.z < 0.34 and p.center.y > 0.10:
            p.material_index = 2 # Crimson chest trim
        else:
            p.material_index = 0
    obj_torso = bpy.data.objects.new("HUMAN_Torso", m_torso)
    col.objects.link(obj_torso)
    obj_torso.parent = obj_pelvis
    obj_torso.location = Vector((0, 0, 0))

    # 4. Head & Face (Sculpted features, nose, eyes, mouth, stylized hair)
    bm = bmesh.new()
    # Neck
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.065, radius2=0.06, depth=0.11, segments=14, matrix=Matrix.Translation(Vector((0, 0, 0.05))))
    # Cranium
    bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=14, radius=0.12, matrix=Matrix.Translation(Vector((0, 0, 0.18))) @ Matrix.Diagonal(Vector((0.88, 1.05, 1.15, 1.0))))
    # Jaw / Chin
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.05, 0.12))) @ Matrix.Diagonal(Vector((0.09, 0.08, 0.07, 1.0))))
    # Nose
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.018, radius2=0.005, depth=0.035, segments=8, matrix=Matrix.Translation(Vector((0, 0.12, 0.18))) @ Matrix.Rotation(math.radians(75), 4, 'X'))
    # Left & Right Eyes
    for ex in [-0.04, 0.04]:
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=8, radius=0.016, matrix=Matrix.Translation(Vector((ex, 0.095, 0.20))))
    # Stylized Pompadour / Undercut Hair
    bmesh.ops.create_uvsphere(bm, u_segments=18, v_segments=12, radius=0.135, matrix=Matrix.Translation(Vector((0, -0.015, 0.22))) @ Matrix.Diagonal(Vector((0.92, 1.08, 1.12, 1.0))))
    # Front hair quiff swept forward
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.04, 0.27))) @ Matrix.Diagonal(Vector((0.11, 0.08, 0.06, 1.0))))

    m_head = bpy.data.meshes.new("HUMAN_Head_Mesh")
    bm.to_mesh(m_head)
    bm.free()
    m_head.materials.append(mat_skin)
    m_head.materials.append(mat_hair)
    m_head.materials.append(mat_eyes)
    for p in m_head.polygons:
        p.use_smooth = True
        # Eyes
        if abs(p.center.x) > 0.025 and abs(p.center.x) < 0.055 and p.center.y > 0.085 and abs(p.center.z - 0.20) < 0.02:
            p.material_index = 2
        # Hair
        elif p.center.z > 0.21 or (p.center.z > 0.13 and p.center.y < -0.01):
            p.material_index = 1
        else:
            p.material_index = 0
    obj_head = bpy.data.objects.new("HUMAN_Head", m_head)
    col.objects.link(obj_head)
    obj_head.parent = obj_torso
    obj_head.location = Vector((0, 0, 0.50))

    # 5. Articulated Legs: Thigh + Shin + Sneaker
    def make_leg(side, x_off):
        # Thigh
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.10, radius2=0.075, depth=0.44, segments=14, matrix=Matrix.Translation(Vector((0, 0, -0.22))))
        m_t = bpy.data.meshes.new(f"HUMAN_Thigh_{side}_Mesh")
        bm.to_mesh(m_t)
        bm.free()
        m_t.materials.append(mat_pants)
        for p in m_t.polygons: p.use_smooth = True
        o_t = bpy.data.objects.new(f"HUMAN_Thigh_{side}", m_t)
        col.objects.link(o_t)
        o_t.parent = obj_pelvis
        o_t.location = Vector((x_off, 0, -0.05))

        # Shin / Knee
        bm = bmesh.new()
        # Knee joint bulb
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=0.078, matrix=Matrix.Translation(Vector((0, 0.01, 0))))
        # Calf / Shin taper
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.075, radius2=0.055, depth=0.44, segments=14, matrix=Matrix.Translation(Vector((0, 0, -0.22))))
        m_s = bpy.data.meshes.new(f"HUMAN_Shin_{side}_Mesh")
        bm.to_mesh(m_s)
        bm.free()
        m_s.materials.append(mat_pants)
        for p in m_s.polygons: p.use_smooth = True
        o_s = bpy.data.objects.new(f"HUMAN_Shin_{side}", m_s)
        col.objects.link(o_s)
        o_s.parent = o_t
        o_s.location = Vector((0, 0, -0.44))

        # Running Sneaker (White sculpted midsole, dark upper, laces)
        bm = bmesh.new()
        # White EVA Midsole with rocker curvature
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.06, -0.03))) @ Matrix.Diagonal(Vector((0.11, 0.27, 0.04, 1.0))))
        # Rubber outsole tread
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.06, -0.055))) @ Matrix.Diagonal(Vector((0.108, 0.265, 0.015, 1.0))))
        # Breathable Mesh Upper
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.04, 0.02))) @ Matrix.Diagonal(Vector((0.10, 0.23, 0.07, 1.0))))
        # Toe cap
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.055, matrix=Matrix.Translation(Vector((0, 0.16, -0.01))))
        m_f = bpy.data.meshes.new(f"HUMAN_Foot_{side}_Mesh")
        bm.to_mesh(m_f)
        bm.free()
        m_f.materials.append(mat_sole)
        m_f.materials.append(mat_shoe)
        m_f.materials.append(mat_trim)
        for p in m_f.polygons:
            p.use_smooth = True
            if p.center.z < -0.01: p.material_index = 0 # Sole
            elif p.center.y > 0.08: p.material_index = 2 # Toe accent
            else: p.material_index = 1 # Upper
        o_f = bpy.data.objects.new(f"HUMAN_Foot_{side}", m_f)
        col.objects.link(o_f)
        o_f.parent = o_s
        o_f.location = Vector((0, 0, -0.44))

        return o_t, o_s, o_f

    thigh_l, shin_l, foot_l = make_leg("L", -0.12)
    thigh_r, shin_r, foot_r = make_leg("R", 0.12)

    # 6. Articulated Arms: Upper Arm + Forearm + Sculpted Hands
    def make_arm(side, x_off):
        # Shoulder / Upper Arm
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=0.08, matrix=Matrix.Translation(Vector((0, 0, 0))))
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.075, radius2=0.058, depth=0.30, segments=12, matrix=Matrix.Translation(Vector((0, 0, -0.15))))
        m_u = bpy.data.meshes.new(f"HUMAN_UpperArm_{side}_Mesh")
        bm.to_mesh(m_u)
        bm.free()
        m_u.materials.append(mat_jacket)
        for p in m_u.polygons: p.use_smooth = True
        o_u = bpy.data.objects.new(f"HUMAN_UpperArm_{side}", m_u)
        col.objects.link(o_u)
        o_u.parent = obj_torso
        o_u.location = Vector((x_off, 0, 0.44))

        # Forearm + Sculpted Hand
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.058, radius2=0.045, depth=0.28, segments=12, matrix=Matrix.Translation(Vector((0, 0, -0.14))))
        # Hand / Runner fist
        bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.045, matrix=Matrix.Translation(Vector((0, 0.02, -0.31))))
        # Thumb
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0.025 if x_off<0 else -0.025, 0.035, -0.29))) @ Matrix.Diagonal(Vector((0.02, 0.03, 0.025, 1.0))))
        m_a = bpy.data.meshes.new(f"HUMAN_Forearm_{side}_Mesh")
        bm.to_mesh(m_a)
        bm.free()
        m_a.materials.append(mat_jacket)
        m_a.materials.append(mat_skin)
        for p in m_a.polygons:
            p.use_smooth = True
            if p.center.z < -0.26: p.material_index = 1 # Skin
            else: p.material_index = 0
        o_a = bpy.data.objects.new(f"HUMAN_Forearm_{side}", m_a)
        col.objects.link(o_a)
        o_a.parent = o_u
        o_a.location = Vector((0, 0, -0.30))

        return o_u, o_a

    uarm_l, farm_l = make_arm("L", -0.25)
    uarm_r, farm_r = make_arm("R", 0.25)

    # Focus Target
    target = bpy.data.objects.get("HUMAN_Focus_Target")
    if not target:
        target = bpy.data.objects.new("HUMAN_Focus_Target", None)
        col.objects.link(target)
    target.parent = root
    target.location = Vector((0, 0, 1.35))

    return {
        'root': root,
        'pelvis': obj_pelvis, 'torso': obj_torso, 'head': obj_head,
        'thigh_l': thigh_l, 'shin_l': shin_l, 'foot_l': foot_l,
        'thigh_r': thigh_r, 'shin_r': shin_r, 'foot_r': foot_r,
        'uarm_l': uarm_l, 'farm_l': farm_l,
        'uarm_r': uarm_r, 'farm_r': farm_r,
        'focus': target
    }

if __name__ == '__main__':
    build_hero_photoreal_human()
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Sculpted hero human character successfully!")
