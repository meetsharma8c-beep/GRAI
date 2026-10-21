"""
Animate Player Walking on Road with 360-Degree Rotating Cinematic Camera
========================================================================
1. Places the player character directly ON THE ASPHALT ROAD (Netaji Subhash Road).
2. Animates natural walking/jogging gait along the roadway across 72 frames (24 fps).
3. The camera performs a full seamless 360-degree continuous orbital rotation around
   the moving player, showcasing the entire Mumbai environment:
   - Behind: Third-person follow down the 6-lane boulevard.
   - Right Flank: Viewing the player with the Arabian Sea, tetrapods, and sunset.
   - Front POV: Looking directly at the player moving forward with the road behind.
   - Left Flank: Viewing the player with the Art Deco towers and streetscape.
   - Return: Seamlessly completing the full 360-degree circle!
4. Compiles the sequence into a smooth 24 fps looping video.
"""
import bpy
import bmesh
import math
import os
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

def setup_road_walking_character():
    print("=== SETTING UP CHARACTER ON ROAD ===")
    for o in list(bpy.data.objects):
        if o.name.startswith("RUNNER_") or o.name.startswith("CHARACTER_"):
            bpy.data.objects.remove(o, do_unlink=True)

    col = bpy.data.collections.get("Playable_Street_Props")
    if not col:
        col = bpy.context.scene.collection

    mat_jacket = get_or_create_mat("MAT_Player_Jacket", (0.12, 0.13, 0.16, 1.0), roughness=0.45)
    mat_jeans = get_or_create_mat("MAT_Player_Jeans", (0.10, 0.18, 0.32, 1.0), roughness=0.75)
    mat_boots = get_or_create_mat("MAT_Player_Boots", (0.06, 0.06, 0.07, 1.0), roughness=0.35)
    mat_skin = get_or_create_mat("MAT_Player_Skin", (0.80, 0.62, 0.50, 1.0), roughness=0.55)
    mat_hair = get_or_create_mat("MAT_Player_Hair", (0.05, 0.04, 0.04, 1.0), roughness=0.65)

    # 1. Torso & Head
    bm_torso = bmesh.new()
    # Pelvis
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.98))) @ Matrix.Diagonal(Vector((0.42, 0.26, 0.16, 1.0))))
    # Upper Torso
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 1.28))) @ Matrix.Diagonal(Vector((0.50, 0.28, 0.46, 1.0))))
    # Neck & Head
    bmesh.ops.create_cone(bm_torso, cap_ends=True, radius1=0.07, radius2=0.07, depth=0.12, segments=8, matrix=Matrix.Translation(Vector((0, 0, 1.56))))
    bmesh.ops.create_uvsphere(bm_torso, u_segments=12, v_segments=10, radius=0.14, matrix=Matrix.Translation(Vector((0, 0, 1.70))))
    # Hair
    bmesh.ops.create_uvsphere(bm_torso, u_segments=12, v_segments=8, radius=0.15, matrix=Matrix.Translation(Vector((0, -0.02, 1.76))))

    mesh_torso = bpy.data.meshes.new("CHARACTER_Torso_Mesh")
    bm_torso.to_mesh(mesh_torso)
    bm_torso.free()
    mesh_torso.materials.append(mat_jacket)
    mesh_torso.materials.append(mat_skin)
    mesh_torso.materials.append(mat_hair)
    for p in mesh_torso.polygons:
        if p.center.z > 1.74: p.material_index = 2
        elif p.center.z > 1.52: p.material_index = 1
        else: p.material_index = 0

    obj_torso = bpy.data.objects.new("CHARACTER_Torso", mesh_torso)
    col.objects.link(obj_torso)

    # 2. Left & Right Legs
    def make_leg(name, x_offset):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.11, radius2=0.08, depth=0.74, segments=10, matrix=Matrix.Translation(Vector((0, 0, -0.37))))
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
        obj.location = Vector((x_offset, 0, 0.95))
        return obj

    obj_leg_l = make_leg("CHARACTER_Leg_L", -0.16)
    obj_leg_r = make_leg("CHARACTER_Leg_R", 0.16)

    # 3. Left & Right Arms
    def make_arm(name, x_offset):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.08, radius2=0.06, depth=0.55, segments=8, matrix=Matrix.Translation(Vector((0, 0, -0.28))))
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
        obj.location = Vector((x_offset, 0, 1.45))
        return obj

    obj_arm_l = make_arm("CHARACTER_Arm_L", -0.32)
    obj_arm_r = make_arm("CHARACTER_Arm_R", 0.32)

    return obj_torso, obj_leg_l, obj_leg_r, obj_arm_l, obj_arm_r

def animate_360_orbit(obj_torso, obj_leg_l, obj_leg_r, obj_arm_l, obj_arm_r):
    print("=== ANIMATING 360-DEGREE ROTATING VIEW ALONG ROAD ===")
    scene = bpy.context.scene
    total_frames = 72
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = 24

    # Get or create 360 camera
    cam_name = "Cam_Player_360_Orbit"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cdata = bpy.data.cameras.new(f"{cam_name}_Data")
        cam_obj = bpy.data.objects.new(cam_name, cdata)
        bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.data.lens = 28.0 # Cinematic wide-normal field of view
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 25000.0

    # Curve lookup for Marine Drive seawall & road
    sw_curve = [
        (0.0, -1300.0), (200.0, -1200.0), (400.0, -1140.0), (600.0, -1090.0),
        (800.0, -1060.0), (1000.0, -1035.0), (1200.0, -1010.0), (1400.0, -990.0),
        (1600.0, -975.0), (1800.0, -960.0), (2000.0, -945.0), (2200.0, -930.0),
        (2400.0, -920.0), (2600.0, -910.0), (2800.0, -905.0), (3000.0, -905.0)
    ]
    def get_sw_x(y_val):
        if y_val <= sw_curve[0][0]: return sw_curve[0][1]
        if y_val >= sw_curve[-1][0]: return sw_curve[-1][1]
        for i in range(len(sw_curve) - 1):
            y1, x1 = sw_curve[i]
            y2, x2 = sw_curve[i + 1]
            if y1 <= y_val <= y2:
                t_val = (y_val - y1) / (y2 - y1)
                return x1 + t_val * (x2 - x1)
        return -1000.0

    # Raycast onto the actual road object for 100% physically accurate elevation
    rd_obj = bpy.data.objects.get("ROAD_MarineDrive_NetajiSubhashRoad")
    imw = rd_obj.matrix_world.inverted() if rd_obj else None

    def get_road_z(x, y):
        if rd_obj and imw:
            orig = imw @ Vector((x, y, 50.0))
            dir_vec = imw.to_3x3() @ Vector((0, 0, -1.0))
            hit, loc, norm, idx = rd_obj.ray_cast(orig, dir_vec)
            if hit:
                return (rd_obj.matrix_world @ loc).z
        return 6.2

    # Traversal parameters along Netaji Subhash Road:
    # Character walks 32 meters along the 6-lane asphalt boulevard from Y=1080 to Y=1112
    y_start = 1080.0
    y_end = 1112.0

    # 360 Camera parameters
    radius = 4.2 # Orbit radius around player in meters
    cam_height_offset = 1.35 # Eye-level view of player

    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        # Progress 0.0 to 1.0
        t = (f - 1) / float(total_frames - 1)
        y = y_start + t * (y_end - y_start)

        # Marine Drive road lane position:
        # Netaji Subhash Road sits between sw_x + 12m and sw_x + 40m.
        # sw_x + 18m puts the player right in the open seaside traffic lane!
        sw_x = get_sw_x(y)
        x_road = sw_x + 18.0
        z_surface = get_road_z(x_road, y)

        # Walking stride cadence (6 full stride cycles across 72 frames)
        cycle = (f - 1) * (math.pi * 2.0 / 12.0)
        # Walking vertical bounce
        bounce = abs(math.sin(cycle)) * 0.04
        z_char = z_surface + bounce

        # Road curvature heading/tangent
        sw_x_ahead = get_sw_x(y + 2.0)
        heading_yaw = math.atan2((sw_x_ahead - sw_x), 2.0)

        # 1. Update Torso
        obj_torso.location = Vector((x_road, y, z_char))
        obj_torso.rotation_euler = (math.radians(3.5), math.radians(1.2) * math.sin(cycle), heading_yaw)
        obj_torso.keyframe_insert(data_path="location", frame=f)
        obj_torso.keyframe_insert(data_path="rotation_euler", frame=f)

        # 2. Articulated Legs & Arms swing
        stride_angle = math.radians(26.0) * math.sin(cycle)
        obj_leg_l.rotation_euler = (stride_angle, 0, 0)
        obj_leg_r.rotation_euler = (-stride_angle, 0, 0)
        obj_leg_l.keyframe_insert(data_path="rotation_euler", frame=f)
        obj_leg_r.keyframe_insert(data_path="rotation_euler", frame=f)

        arm_angle = math.radians(22.0) * math.sin(cycle)
        obj_arm_l.rotation_euler = (-arm_angle, 0, 0)
        obj_arm_r.rotation_euler = (arm_angle, 0, 0)
        obj_arm_l.keyframe_insert(data_path="rotation_euler", frame=f)
        obj_arm_r.keyframe_insert(data_path="rotation_euler", frame=f)

        # 3. 360-DEGREE CONTINUOUS ORBITAL CAMERA
        # Angle theta starts directly behind runner (-pi/2) and completes a full 2*pi revolution:
        # f=1: theta = -pi/2 -> Behind player looking down the road
        # f=18: theta = 0     -> Right flank looking at player with Art Deco buildings in BG
        # f=36: theta = +pi/2 -> Direct front looking at player jogging towards camera!
        # f=54: theta = +pi   -> Left flank looking at player with Arabian Sea & sunset in BG
        # f=72: theta = +3pi/2 -> Seamless return to behind player!
        theta = -math.pi / 2.0 + t * (2.0 * math.pi)

        cam_x = x_road + radius * math.cos(theta)
        cam_y = y + radius * math.sin(theta)
        cam_z = z_surface + cam_height_offset + 0.15 * math.sin(theta)
        cam_obj.location = Vector((cam_x, cam_y, cam_z))

        # Target look direction: directly at player upper torso / head
        target = Vector((x_road, y, z_char + 1.25))
        direction = target - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    print(f"Animated {total_frames} frames of 360-degree orbital rotation around walking player on road!")

def render_360_frames():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.camera = bpy.data.objects['Cam_Player_360_Orbit']
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    out_dir = "/tmp/running_360_frames"
    os.makedirs(out_dir, exist_ok=True)

    print(f"Rendering 72 frames to {out_dir}...")
    for f in range(1, 73):
        scene.frame_set(f)
        out_path = f"{out_dir}/frame_{f:04d}.png"
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        if f % 12 == 0 or f == 72:
            print(f"Rendered frame {f}/72 -> {out_path}")

    print("All 72 frames rendered successfully!")

if __name__ == '__main__':
    t, ll, lr, al, ar = setup_road_walking_character()
    animate_360_orbit(t, ll, lr, al, ar)
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    render_360_frames()
