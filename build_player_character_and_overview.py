"""
Build 3D Player Character Model & Full Mumbai Overview Suite
=============================================================
1. Creates an authentic 3D open-world protagonist character model
   (CHARACTER_Player_Protagonist) standing on the Marine Drive promenade.
   - Head, stylized hair, jacket, denim jeans, boots, and posture.
   - PBR clothing materials with physically based shaders.
2. Calibrates an over-the-shoulder third-person player game camera
   (Cam_Player_ThirdPerson_Follow) directly framing the player character.
3. Configures and renders:
   - The Third-Person Player View (showing the player standing on Marine Drive).
   - The Whole Mumbai Master Overview (high-altitude peninsula vista).
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def get_or_create_mat(name, color, roughness=0.5, metallic=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return m

def build_player_character():
    print("=== BUILDING 3D PLAYER CHARACTER PROTAGONIST ===")

    # Clean up old character if any
    old = bpy.data.objects.get("CHARACTER_Player_Protagonist")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    col = bpy.data.collections.get("Playable_Street_Props")
    if not col:
        col = bpy.context.scene.collection

    # Materials for Player Character
    mat_skin = get_or_create_mat("MAT_Player_Skin", (0.80, 0.62, 0.50, 1.0), roughness=0.55)
    mat_hair = get_or_create_mat("MAT_Player_Hair", (0.05, 0.04, 0.04, 1.0), roughness=0.65)
    mat_jacket = get_or_create_mat("MAT_Player_Jacket", (0.12, 0.13, 0.15, 1.0), roughness=0.45) # Dark streetwear bomber
    mat_jeans = get_or_create_mat("MAT_Player_Jeans", (0.10, 0.18, 0.32, 1.0), roughness=0.75) # Dark indigo denim
    mat_boots = get_or_create_mat("MAT_Player_Boots", (0.06, 0.06, 0.07, 1.0), roughness=0.35) # Black leather boots

    bm = bmesh.new()

    # Base ground location on Marine Drive Promenade
    # X = -1026.8, Y = 1105.0, Z = 7.35m
    p_x = -1026.8
    p_y = 1105.0
    p_z = 7.35

    # 1. Boots (Left & Right) - Height: 0.0 to 0.22m
    mat_b_l = Matrix.Translation(Vector((p_x - 0.16, p_y + 0.04, p_z + 0.11)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_b_l @ Matrix.Diagonal(Vector((0.15, 0.32, 0.22, 1.0))))
    mat_b_r = Matrix.Translation(Vector((p_x + 0.16, p_y + 0.04, p_z + 0.11)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_b_r @ Matrix.Diagonal(Vector((0.15, 0.32, 0.22, 1.0))))

    # 2. Jeans / Legs - Height: 0.22 to 0.95m
    mat_l_l = Matrix.Translation(Vector((p_x - 0.16, p_y, p_z + 0.58)))
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.12, radius2=0.09, depth=0.74, segments=10, matrix=mat_l_l)
    mat_l_r = Matrix.Translation(Vector((p_x + 0.16, p_y, p_z + 0.58)))
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.12, radius2=0.09, depth=0.74, segments=10, matrix=mat_l_r)

    # 3. Torso / Pelvis & Jacket - Height: 0.95 to 1.55m
    # Pelvis
    mat_pelvis = Matrix.Translation(Vector((p_x, p_y, p_z + 0.98)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_pelvis @ Matrix.Diagonal(Vector((0.44, 0.26, 0.16, 1.0))))

    # Upper Torso / Bomber Jacket
    mat_torso = Matrix.Translation(Vector((p_x, p_y, p_z + 1.28)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_torso @ Matrix.Diagonal(Vector((0.52, 0.28, 0.48, 1.0))))

    # 4. Arms (Left & Right)
    mat_a_l = Matrix.Translation(Vector((p_x - 0.34, p_y, p_z + 1.20)))
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.09, radius2=0.07, depth=0.55, segments=8, matrix=mat_a_l)
    mat_a_r = Matrix.Translation(Vector((p_x + 0.34, p_y, p_z + 1.20)))
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.09, radius2=0.07, depth=0.55, segments=8, matrix=mat_a_r)

    # Hands
    mat_h_l = Matrix.Translation(Vector((p_x - 0.34, p_y, p_z + 0.88)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.07, matrix=mat_h_l)
    mat_h_r = Matrix.Translation(Vector((p_x + 0.34, p_y, p_z + 0.88)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.07, matrix=mat_h_r)

    # 5. Neck & Head - Height: 1.55 to 1.82m
    # Neck
    mat_neck = Matrix.Translation(Vector((p_x, p_y, p_z + 1.56)))
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.07, radius2=0.07, depth=0.12, segments=8, matrix=mat_neck)

    # Head
    mat_head = Matrix.Translation(Vector((p_x, p_y, p_z + 1.70)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=0.14, matrix=mat_head)

    # Hair Style
    mat_hair_m = Matrix.Translation(Vector((p_x, p_y - 0.02, p_z + 1.76)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.15, matrix=mat_hair_m)

    # Convert to mesh
    mesh_player = bpy.data.meshes.new("CHARACTER_Player_Protagonist_Mesh")
    bm.to_mesh(mesh_player)
    bm.free()

    # Assign materials
    mesh_player.materials.append(mat_jacket) # 0: Default
    mesh_player.materials.append(mat_jeans)  # 1: Jeans
    mesh_player.materials.append(mat_boots)  # 2: Boots
    mesh_player.materials.append(mat_skin)   # 3: Skin
    mesh_player.materials.append(mat_hair)   # 4: Hair

    # Assign polygon material slots based on Z height
    for p in mesh_player.polygons:
        z_c = p.center.z - p_z
        if z_c < 0.22:
            p.material_index = 2 # Boots
        elif z_c < 0.96:
            p.material_index = 1 # Jeans
        elif z_c > 1.74:
            p.material_index = 4 # Hair
        elif z_c > 1.52:
            p.material_index = 3 # Skin (Head & Neck)
        elif (p.center.x - p_x < -0.28 or p.center.x - p_x > 0.28) and z_c < 0.95:
            p.material_index = 3 # Hands
        else:
            p.material_index = 0 # Jacket

    obj_player = bpy.data.objects.new("CHARACTER_Player_Protagonist", mesh_player)
    col.objects.link(obj_player)
    print("Created 3D open-world player protagonist character model on Marine Drive!")

    # =========================================================================
    # 2. OVER-THE-SHOULDER THIRD-PERSON GAME CAMERA
    # =========================================================================
    cam_tp = bpy.data.objects.get("Cam_Player_ThirdPerson_Follow")
    if not cam_tp:
        cdata = bpy.data.cameras.new("Cam_Player_ThirdPerson_Follow_Data")
        cam_tp = bpy.data.objects.new("Cam_Player_ThirdPerson_Follow", cdata)
        bpy.context.scene.collection.objects.link(cam_tp)

    # Position 2.8m behind player, slightly over right shoulder (GTA / AAA style)
    cam_tp.location = Vector((p_x + 0.45, p_y - 2.8, p_z + 1.85))
    # Look past the player's head down the curved promenade toward the ocean and buildings
    target = Vector((p_x - 0.2, p_y + 18.0, p_z + 2.0))
    direction = target - cam_tp.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_tp.rotation_euler = rot_quat.to_euler()
    cam_tp.data.lens = 28.0 # Cinematic third-person focal length

    return obj_player

def calibrate_mumbai_whole_map_camera():
    # Whole Mumbai Master Overview Camera
    cam_whole = bpy.data.objects.get("Cam_Mumbai_Playable_Map_Master")
    if not cam_whole:
        cdata = bpy.data.cameras.new("Cam_Mumbai_Playable_Map_Master_Data")
        cam_whole = bpy.data.objects.new("Cam_Mumbai_Playable_Map_Master", cdata)
        bpy.context.scene.collection.objects.link(cam_whole)

    # Position high in the south-west over the Arabian Sea looking north-east
    cam_whole.location = Vector((-3400.0, -900.0, 2400.0))
    target = Vector((-700.0, 2800.0, 35.0)) # Center of peninsula
    direction = target - cam_whole.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_whole.rotation_euler = rot_quat.to_euler()
    cam_whole.data.lens = 24.0 # Wide angle landscape overview
    cam_whole.data.clip_end = 80000.0
    print("Calibrated whole Mumbai map overview camera.")

if __name__ == '__main__':
    build_player_character()
    calibrate_mumbai_whole_map_camera()
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Done!")
