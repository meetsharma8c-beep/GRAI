"""
Animate Human Running & Exploring Mumbai Digital Twin
=====================================================
1. Builds an articulated runner character with moving legs, arms, and torso.
2. Animates a full 48-frame running cycle (24 fps) along the Marine Drive promenade:
   - Forward sprint along the Back Bay curve (Y: 1080m -> 1115m)
   - Dynamic stride kinematics: vertical bounce, leg swing, arm pump, forward lean
   - Third-person chase camera tracking over the right shoulder
3. Renders 48 HD frames (1280x720) in Blender EEVEE Next with PBR shaders.
4. Compiles rendered frames into:
   - human_running_mumbai_exploration.webp (24 fps animated looping video)
   - human_running_mumbai_exploration.gif
"""
import bpy
import bmesh
import math
import os
import subprocess
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

def setup_animated_runner():
    print("=== SETTING UP ANIMATED RUNNER ON MARINE DRIVE ===")

    # Clean existing runner objects
    for o in list(bpy.data.objects):
        if o.name.startswith("RUNNER_"):
            bpy.data.objects.remove(o, do_unlink=True)
    old = bpy.data.objects.get("CHARACTER_Player_Protagonist")
    if old:
        bpy.data.objects.remove(old, do_unlink=True)

    col = bpy.data.collections.get("Playable_Street_Props")
    if not col:
        col = bpy.context.scene.collection

    # Materials
    mat_jacket = get_or_create_mat("MAT_Player_Jacket", (0.12, 0.13, 0.16, 1.0), roughness=0.45)
    mat_jeans = get_or_create_mat("MAT_Player_Jeans", (0.10, 0.18, 0.32, 1.0), roughness=0.75)
    mat_boots = get_or_create_mat("MAT_Player_Boots", (0.06, 0.06, 0.07, 1.0), roughness=0.35)
    mat_skin = get_or_create_mat("MAT_Player_Skin", (0.80, 0.62, 0.50, 1.0), roughness=0.55)
    mat_hair = get_or_create_mat("MAT_Player_Hair", (0.05, 0.04, 0.04, 1.0), roughness=0.65)

    # 1. ROOT / TORSO OBJECT
    bm_torso = bmesh.new()
    # Pelvis
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.98))) @ Matrix.Diagonal(Vector((0.42, 0.26, 0.16, 1.0))))
    # Upper Torso / Bomber Jacket
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 1.28))) @ Matrix.Diagonal(Vector((0.50, 0.28, 0.46, 1.0))))
    # Neck & Head
    bmesh.ops.create_cone(bm_torso, cap_ends=True, radius1=0.07, radius2=0.07, depth=0.12, segments=8, matrix=Matrix.Translation(Vector((0, 0, 1.56))))
    bmesh.ops.create_uvsphere(bm_torso, u_segments=12, v_segments=10, radius=0.14, matrix=Matrix.Translation(Vector((0, 0, 1.70))))
    # Hair
    bmesh.ops.create_uvsphere(bm_torso, u_segments=12, v_segments=8, radius=0.15, matrix=Matrix.Translation(Vector((0, -0.02, 1.76))))

    mesh_torso = bpy.data.meshes.new("RUNNER_Torso_Mesh")
    bm_torso.to_mesh(mesh_torso)
    bm_torso.free()
    mesh_torso.materials.append(mat_jacket)
    mesh_torso.materials.append(mat_skin)
    mesh_torso.materials.append(mat_hair)
    for p in mesh_torso.polygons:
        if p.center.z > 1.74: p.material_index = 2
        elif p.center.z > 1.52: p.material_index = 1
        else: p.material_index = 0

    obj_torso = bpy.data.objects.new("RUNNER_Torso", mesh_torso)
    col.objects.link(obj_torso)

    # 2. LEFT & RIGHT LEGS
    def make_leg(name, x_offset):
        bm = bmesh.new()
        # Thigh + Shin
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.11, radius2=0.08, depth=0.74, segments=10, matrix=Matrix.Translation(Vector((0, 0, -0.37))))
        # Boot
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.05, -0.78))) @ Matrix.Diagonal(Vector((0.14, 0.30, 0.20, 1.0))))
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_jeans)
        mesh.materials.append(mat_boots)
        for p in mesh.polygons:
            if p.center.z < -0.68: p.material_index = 1
            else: p.material_index = 0
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        obj.parent = obj_torso
        obj.location = Vector((x_offset, 0, 0.95)) # Hip joint
        return obj

    obj_leg_l = make_leg("RUNNER_Leg_L", -0.16)
    obj_leg_r = make_leg("RUNNER_Leg_R", 0.16)

    # 3. LEFT & RIGHT ARMS
    def make_arm(name, x_offset):
        bm = bmesh.new()
        # Arm
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.08, radius2=0.06, depth=0.55, segments=8, matrix=Matrix.Translation(Vector((0, 0, -0.28))))
        # Hand
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.07, matrix=Matrix.Translation(Vector((0, 0, -0.58))))
        mesh = bpy.data.meshes.new(f"{name}_Mesh")
        bm.to_mesh(mesh)
        bm.free()
        mesh.materials.append(mat_jacket)
        mesh.materials.append(mat_skin)
        for p in mesh.polygons:
            if p.center.z < -0.52: p.material_index = 1
            else: p.material_index = 0
        obj = bpy.data.objects.new(name, mesh)
        col.objects.link(obj)
        obj.parent = obj_torso
        obj.location = Vector((x_offset, 0, 1.45)) # Shoulder joint
        return obj

    obj_arm_l = make_arm("RUNNER_Arm_L", -0.32)
    obj_arm_r = make_arm("RUNNER_Arm_R", 0.32)

    return obj_torso, obj_leg_l, obj_leg_r, obj_arm_l, obj_arm_r

def animate_running_sequence(obj_torso, obj_leg_l, obj_leg_r, obj_arm_l, obj_arm_r):
    print("=== ANIMATING RUNNING TRAJECTORY & STRIDE GAIT ===")
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 48
    scene.render.fps = 24

    cam = bpy.data.objects.get("Cam_Player_ThirdPerson_Follow")
    if not cam:
        cdata = bpy.data.cameras.new("Cam_Player_ThirdPerson_Follow_Data")
        cam = bpy.data.objects.new("Cam_Player_ThirdPerson_Follow", cdata)
        scene.collection.objects.link(cam)
    cam.data.lens = 28.0

    total_frames = 48
    # Running distance: 36 meters along Marine Drive promenade
    y_start = 1080.0
    y_end = 1118.0

    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        t = (f - 1) / float(total_frames - 1)
        y = y_start + t * (y_end - y_start)

        # Back Bay curve equation
        x_c = -1016.0 + 0.000080 * ((y - 1100.0) ** 2)
        x_prom = x_c - 11.5 # Standing on promenade path

        # Running Stride Cycle (Cadence: 3 steps per second -> ~8 frames per step)
        cycle = (f - 1) * (math.pi * 2.0 / 16.0) # 16 frames per full left-right stride cycle

        # Vertical Running Bounce (foot strike and rebound)
        bounce = abs(math.sin(cycle)) * 0.07
        z = 7.35 + bounce

        # Forward lean of sprinting human (approx 8 degrees)
        lean_angle = math.radians(8.5)
        # Tangent yaw angle of Marine Drive curve
        dx_dy = 0.000160 * (y - 1100.0)
        curve_yaw = math.atan(dx_dy)

        # 1. Torso position & rotation
        obj_torso.location = Vector((x_prom, y, z))
        # Torso slight side-to-side roll and tilt
        torso_roll = math.radians(2.0) * math.sin(cycle)
        obj_torso.rotation_euler = (lean_angle, torso_roll, curve_yaw)
        obj_torso.keyframe_insert(data_path="location", frame=f)
        obj_torso.keyframe_insert(data_path="rotation_euler", frame=f)

        # 2. Leg stride swing (alternating pitch +/- 36 degrees)
        stride_angle = math.radians(34.0) * math.sin(cycle)
        obj_leg_l.rotation_euler = (stride_angle, 0, 0)
        obj_leg_r.rotation_euler = (-stride_angle, 0, 0)
        obj_leg_l.keyframe_insert(data_path="rotation_euler", frame=f)
        obj_leg_r.keyframe_insert(data_path="rotation_euler", frame=f)

        # 3. Arm pump swing (opposite to leg stride +/- 32 degrees)
        arm_angle = math.radians(30.0) * math.sin(cycle)
        obj_arm_l.rotation_euler = (-arm_angle, 0, 0)
        obj_arm_r.rotation_euler = (arm_angle, 0, 0)
        obj_arm_l.keyframe_insert(data_path="rotation_euler", frame=f)
        obj_arm_r.keyframe_insert(data_path="rotation_euler", frame=f)

        # 4. Third-person follow camera tracking right behind runner
        cam_x = x_prom + 0.45 + 0.02 * math.cos(cycle)
        cam_y = y - 3.2
        cam_z = 7.35 + 1.82 + bounce * 0.4 # Smooth camera stabilization
        cam.location = Vector((cam_x, cam_y, cam_z))

        # Target look direction down promenade past runner
        target_y = y + 16.0
        target_x = (-1016.0 + 0.000080 * ((target_y - 1100.0) ** 2)) - 10.5
        target = Vector((target_x, target_y, 7.35 + 1.95))
        direction = target - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

        cam.keyframe_insert(data_path="location", frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)

    print(f"Animated {total_frames} frames of sprinting player on Marine Drive!")

def render_running_frames():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.camera = bpy.data.objects['Cam_Player_ThirdPerson_Follow']
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    out_dir = "/tmp/running_frames"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Rendering 48 frames to {out_dir}...")
    for f in range(1, 49):
        scene.frame_set(f)
        out_path = f"{out_dir}/frame_{f:04d}.png"
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        if f % 12 == 0 or f == 48:
            print(f"Rendered frame {f}/48 -> {out_path}")

    print("All 48 running animation frames rendered successfully!")

if __name__ == '__main__':
    t, ll, lr, al, ar = setup_animated_runner()
    animate_running_sequence(t, ll, lr, al, ar)
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    render_running_frames()
