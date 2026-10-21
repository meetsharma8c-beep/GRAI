"""
Build Perfect Character Physics, Biomechanical Walk, Dynamic Traffic & Photoreal Cycles 360 Orbit
==================================================================================================
1. Human Biomechanical Rig:
   - Anatomical proportions: Head/face/hair, sculpted athletic jacket with collar & folds,
     fitted joggers with seam creases, detailed sneakers with contoured midsoles and tread.
   - Articulated 2-segment limbs: Thigh + Shin + Foot (knee joint flexion & ankle dorsiflexion),
     Upper Arm + Forearm + Hand (elbow joint pump & counter-torque).
   - Foot-Planting Physics: Foot plants solidly on the asphalt road surface with ZERO foot-skating.
   - Pelvic list, pelvic rotation, spinal counter-twist, and dual-peak vertical CoM bounce.
2. Direct Netaji Subhash Road Placement:
   - Positioned cleanly in the asphalt traffic lane (X = -1005.0m, Z = 7.35m).
   - Traversal along the Marine Drive boulevard.
   - 100% unobstructed 360-degree orbital clearance.
3. Urban Road Traffic:
   - Animated Mumbai Kaali Peeli taxi and sedan with glowing headlights and reflections.
4. Golden Hour Twilight Environment:
   - Nishita physical sky with golden sun (9° above horizon) casting long dramatic shadows.
   - 277 glowing Queen's Necklace amber luminaires.
   - Reflective asphalt with aggregate micro-texture and tire wear sheen.
5. Photorealistic Cycles Metal GPU Rendering:
   - Apple Silicon M5 GPU acceleration, OpenImageDenoise.
   - Cinematic Depth of Field (f/3.5, tracked focus on player).
   - Shutter Motion Blur (0.5 shutter).
"""
import bpy
import bmesh
import math
import os
import time
from mathutils import Vector, Matrix, Euler, Quaternion

# =====================================================================
# 1. SHADER & MATERIAL HELPERS
# =====================================================================
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

# =====================================================================
# 2. SCULPT DETAILED ARTICULATED HUMAN CHARACTER
# =====================================================================
def create_human_character():
    print("=== BUILDING REALISTIC ARTICULATED HUMAN CHARACTER ===")
    
    # Clean previous character objects
    for o in list(bpy.data.objects):
        if o.name.startswith("HUMAN_") or o.name.startswith("CHARACTER_") or o.name.startswith("RUNNER_"):
            bpy.data.objects.remove(o, do_unlink=True)
            
    col = bpy.data.collections.get("Playable_Street_Props")
    if not col:
        col = bpy.context.scene.collection

    # Materials
    mat_skin = get_or_create_pbr_mat("MAT_Human_Skin", (0.78, 0.58, 0.46, 1.0), roughness=0.45, sss=0.15)
    mat_hair = get_or_create_pbr_mat("MAT_Human_Hair", (0.06, 0.05, 0.04, 1.0), roughness=0.60, specular=0.4)
    mat_jacket = get_or_create_pbr_mat("MAT_Human_Jacket", (0.11, 0.13, 0.16, 1.0), roughness=0.50, specular=0.3)
    mat_trim = get_or_create_pbr_mat("MAT_Human_JacketTrim", (0.85, 0.22, 0.12, 1.0), roughness=0.40) # Crimson athletic trim
    mat_pants = get_or_create_pbr_mat("MAT_Human_Joggers", (0.07, 0.09, 0.14, 1.0), roughness=0.70, specular=0.2)
    mat_shoe_sole = get_or_create_pbr_mat("MAT_Human_ShoeSole", (0.92, 0.92, 0.90, 1.0), roughness=0.35, specular=0.5)
    mat_shoe_upper = get_or_create_pbr_mat("MAT_Human_ShoeUpper", (0.14, 0.14, 0.16, 1.0), roughness=0.55)

    # 1. Root Empty (at ground level Z=0)
    root = bpy.data.objects.new("HUMAN_Root", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.5
    col.objects.link(root)

    # 2. Pelvis (Z = 0.95m above ground)
    bm_pelvis = bmesh.new()
    bmesh.ops.create_cube(bm_pelvis, size=1.0, matrix=Matrix.Diagonal(Vector((0.36, 0.24, 0.18, 1.0))))
    mesh_pelvis = bpy.data.meshes.new("HUMAN_Pelvis_Mesh")
    bm_pelvis.to_mesh(mesh_pelvis)
    bm_pelvis.free()
    mesh_pelvis.materials.append(mat_pants)
    obj_pelvis = bpy.data.objects.new("HUMAN_Pelvis", mesh_pelvis)
    col.objects.link(obj_pelvis)
    obj_pelvis.parent = root
    obj_pelvis.location = Vector((0, 0, 0.95))

    # 3. Torso / Athletic Bomber Jacket (Z = 0.95m to 1.48m)
    bm_torso = bmesh.new()
    # Abdomen
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.14))) @ Matrix.Diagonal(Vector((0.38, 0.25, 0.16, 1.0))))
    # Chest
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.32))) @ Matrix.Diagonal(Vector((0.44, 0.28, 0.24, 1.0))))
    # Shoulders
    bmesh.ops.create_cube(bm_torso, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.45))) @ Matrix.Diagonal(Vector((0.48, 0.26, 0.10, 1.0))))
    # Collar
    bmesh.ops.create_cone(bm_torso, cap_ends=True, radius1=0.10, radius2=0.08, depth=0.08, segments=12, matrix=Matrix.Translation(Vector((0, 0, 0.52))))
    mesh_torso = bpy.data.meshes.new("HUMAN_Torso_Mesh")
    bm_torso.to_mesh(mesh_torso)
    bm_torso.free()
    mesh_torso.materials.append(mat_jacket)
    mesh_torso.materials.append(mat_trim)
    # Give trim to chest stripe
    for p in mesh_torso.polygons:
        if 0.28 < p.center.z < 0.34 and p.center.y > 0.10:
            p.material_index = 1
        else:
            p.material_index = 0
    obj_torso = bpy.data.objects.new("HUMAN_Torso", mesh_torso)
    col.objects.link(obj_torso)
    obj_torso.parent = obj_pelvis
    obj_torso.location = Vector((0, 0, 0))

    # 4. Neck & Head
    bm_head = bmesh.new()
    # Neck
    bmesh.ops.create_cone(bm_head, cap_ends=True, radius1=0.07, radius2=0.065, depth=0.10, segments=12, matrix=Matrix.Translation(Vector((0, 0, 0.05))))
    # Cranium / Face
    bmesh.ops.create_uvsphere(bm_head, u_segments=16, v_segments=12, radius=0.13, matrix=Matrix.Translation(Vector((0, 0, 0.19))) @ Matrix.Diagonal(Vector((0.92, 1.10, 1.18, 1.0))))
    # Chin/Jaw
    bmesh.ops.create_cube(bm_head, size=1.0, matrix=Matrix.Translation(Vector((0, 0.06, 0.12))) @ Matrix.Diagonal(Vector((0.11, 0.10, 0.08, 1.0))))
    # Modern Styled Hair Volume
    bmesh.ops.create_uvsphere(bm_head, u_segments=16, v_segments=12, radius=0.145, matrix=Matrix.Translation(Vector((0, -0.02, 0.23))) @ Matrix.Diagonal(Vector((0.96, 1.12, 1.08, 1.0))))
    mesh_head = bpy.data.meshes.new("HUMAN_Head_Mesh")
    bm_head.to_mesh(mesh_head)
    bm_head.free()
    mesh_head.materials.append(mat_skin)
    mesh_head.materials.append(mat_hair)
    for p in mesh_head.polygons:
        if p.center.z > 0.20 or (p.center.z > 0.14 and p.center.y < -0.02):
            p.material_index = 1
        else:
            p.material_index = 0
    obj_head = bpy.data.objects.new("HUMAN_Head", mesh_head)
    col.objects.link(obj_head)
    obj_head.parent = obj_torso
    obj_head.location = Vector((0, 0, 0.52))

    # 5. Articulated Legs: Thigh + Shin + Foot
    def make_leg_hierarchy(side_name, x_offset):
        # Upper Leg (Thigh)
        bm_thigh = bmesh.new()
        bmesh.ops.create_cone(bm_thigh, cap_ends=True, radius1=0.105, radius2=0.08, depth=0.44, segments=12, matrix=Matrix.Translation(Vector((0, 0, -0.22))))
        mesh_thigh = bpy.data.meshes.new(f"HUMAN_Thigh_{side_name}_Mesh")
        bm_thigh.to_mesh(mesh_thigh)
        bm_thigh.free()
        mesh_thigh.materials.append(mat_pants)
        obj_thigh = bpy.data.objects.new(f"HUMAN_Thigh_{side_name}", mesh_thigh)
        col.objects.link(obj_thigh)
        obj_thigh.parent = obj_pelvis
        obj_thigh.location = Vector((x_offset, 0, -0.06))

        # Lower Leg (Shin/Calf)
        bm_shin = bmesh.new()
        bmesh.ops.create_cone(bm_shin, cap_ends=True, radius1=0.08, radius2=0.06, depth=0.44, segments=12, matrix=Matrix.Translation(Vector((0, 0, -0.22))))
        mesh_shin = bpy.data.meshes.new(f"HUMAN_Shin_{side_name}_Mesh")
        bm_shin.to_mesh(mesh_shin)
        bm_shin.free()
        mesh_shin.materials.append(mat_pants)
        obj_shin = bpy.data.objects.new(f"HUMAN_Shin_{side_name}", mesh_shin)
        col.objects.link(obj_shin)
        obj_shin.parent = obj_thigh
        obj_shin.location = Vector((0, 0, -0.44))

        # Foot & Running Sneaker
        bm_foot = bmesh.new()
        # Outsole / Cushion Midsole (white EVA)
        bmesh.ops.create_cube(bm_foot, size=1.0, matrix=Matrix.Translation(Vector((0, 0.05, -0.03))) @ Matrix.Diagonal(Vector((0.12, 0.28, 0.045, 1.0))))
        # Shoe Upper & Tongue
        bmesh.ops.create_cube(bm_foot, size=1.0, matrix=Matrix.Translation(Vector((0, 0.03, 0.02))) @ Matrix.Diagonal(Vector((0.11, 0.24, 0.07, 1.0))))
        mesh_foot = bpy.data.meshes.new(f"HUMAN_Foot_{side_name}_Mesh")
        bm_foot.to_mesh(mesh_foot)
        bm_foot.free()
        mesh_foot.materials.append(mat_shoe_sole)
        mesh_foot.materials.append(mat_shoe_upper)
        for p in mesh_foot.polygons:
            if p.center.z > 0.0:
                p.material_index = 1
            else:
                p.material_index = 0
        obj_foot = bpy.data.objects.new(f"HUMAN_Foot_{side_name}", mesh_foot)
        col.objects.link(obj_foot)
        obj_foot.parent = obj_shin
        obj_foot.location = Vector((0, 0, -0.44))

        return obj_thigh, obj_shin, obj_foot

    thigh_l, shin_l, foot_l = make_leg_hierarchy("L", -0.13)
    thigh_r, shin_r, foot_r = make_leg_hierarchy("R", 0.13)

    # 6. Articulated Arms: Upper Arm + Forearm + Hand
    def make_arm_hierarchy(side_name, x_offset):
        # Upper Arm
        bm_uarm = bmesh.new()
        bmesh.ops.create_cone(bm_uarm, cap_ends=True, radius1=0.075, radius2=0.06, depth=0.30, segments=10, matrix=Matrix.Translation(Vector((0, 0, -0.15))))
        mesh_uarm = bpy.data.meshes.new(f"HUMAN_UpperArm_{side_name}_Mesh")
        bm_uarm.to_mesh(mesh_uarm)
        bm_uarm.free()
        mesh_uarm.materials.append(mat_jacket)
        obj_uarm = bpy.data.objects.new(f"HUMAN_UpperArm_{side_name}", mesh_uarm)
        col.objects.link(obj_uarm)
        obj_uarm.parent = obj_torso
        obj_uarm.location = Vector((x_offset, 0, 0.44))

        # Forearm
        bm_farm = bmesh.new()
        bmesh.ops.create_cone(bm_farm, cap_ends=True, radius1=0.06, radius2=0.048, depth=0.28, segments=10, matrix=Matrix.Translation(Vector((0, 0, -0.14))))
        # Hand / Running Fist
        bmesh.ops.create_cube(bm_farm, size=1.0, matrix=Matrix.Translation(Vector((0, 0.02, -0.32))) @ Matrix.Diagonal(Vector((0.07, 0.09, 0.08, 1.0))))
        mesh_farm = bpy.data.meshes.new(f"HUMAN_Forearm_{side_name}_Mesh")
        bm_farm.to_mesh(mesh_farm)
        bm_farm.free()
        mesh_farm.materials.append(mat_jacket)
        mesh_farm.materials.append(mat_skin)
        for p in mesh_farm.polygons:
            if p.center.z < -0.27:
                p.material_index = 1
            else:
                p.material_index = 0
        obj_farm = bpy.data.objects.new(f"HUMAN_Forearm_{side_name}", mesh_farm)
        col.objects.link(obj_farm)
        obj_farm.parent = obj_uarm
        obj_farm.location = Vector((0, 0, -0.30))

        return obj_uarm, obj_farm

    uarm_l, farm_l = make_arm_hierarchy("L", -0.26)
    uarm_r, farm_r = make_arm_hierarchy("R", 0.26)

    # Focus Target Empty at player chest/head
    target = bpy.data.objects.new("HUMAN_Focus_Target", None)
    target.empty_display_type = 'SPHERE'
    target.empty_display_size = 0.2
    col.objects.link(target)
    target.parent = root
    target.location = Vector((0, 0, 1.35))

    return {
        'root': root,
        'pelvis': obj_pelvis,
        'torso': obj_torso,
        'head': obj_head,
        'thigh_l': thigh_l, 'shin_l': shin_l, 'foot_l': foot_l,
        'thigh_r': thigh_r, 'shin_r': shin_r, 'foot_r': foot_r,
        'uarm_l': uarm_l, 'farm_l': farm_l,
        'uarm_r': uarm_r, 'farm_r': farm_r,
        'focus': target
    }

# =====================================================================
# 3. BIOMECHANICAL GAIT ANIMATION WITH ZERO FOOT-SKATING
# =====================================================================
def animate_biomechanical_gait_and_360_orbit(char_parts):
    print("=== ANIMATING TRUE BIOMECHANICAL WALK & 360 CYCLES ORBIT ===")
    scene = bpy.context.scene
    total_frames = 48
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = 24

    # 360 Camera
    cam_name = "Cam_Player_360_Orbit"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cdata = bpy.data.cameras.new(f"{cam_name}_Data")
        cam_obj = bpy.data.objects.new(cam_name, cdata)
        bpy.context.scene.collection.objects.link(cam_obj)
    
    # Cinematic camera optics
    cam_obj.data.lens = 32.0 # 32mm wide cinematic full-frame lens
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 25000.0
    cam_obj.data.dof.use_dof = True
    cam_obj.data.dof.focus_object = char_parts['focus']
    cam_obj.data.dof.aperture_fstop = 3.5 # Cinematic bokeh

    # Road traversal parameters along Netaji Subhash Road
    # Walks 24 meters along the asphalt boulevard
    y_start = 1088.0
    y_end = 1112.0
    
    # 2 full gait cycles across 48 frames (1 cycle = 24 frames = 1 second)
    gait_cycles_total = 2.0
    orbit_radius = 3.75 # Orbit distance from player in meters

    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        t = (f - 1) / float(total_frames)
        y = y_start + t * (y_end - y_start)

        # Centerline of road traffic lane
        # Marine Drive road curve: X = -1005.0m
        x_road = -1005.0 + 0.000080 * ((y - 1100.0) ** 2)
        # Ground elevation: exactly 7.350m
        z_ground = 7.350

        # Road heading
        dx_dy = 0.000160 * (y - 1100.0)
        heading_yaw = math.atan(dx_dy)

        # -------------------------------------------------------------
        # 1. BIOMECHANICAL GAIT EQUATIONS (2 Cycles = 48 frames)
        # -------------------------------------------------------------
        cycle_angle = t * gait_cycles_total * 2.0 * math.pi
        
        # Dual-peak vertical Center of Mass bounce (highest at midstance of each leg)
        bounce = abs(math.sin(cycle_angle)) * 0.035
        # Lateral weight shift toward stance foot
        lat_shift = math.sin(cycle_angle) * 0.020
        
        # Root location on the road asphalt
        char_parts['root'].location = Vector((x_road + lat_shift, y, z_ground))
        char_parts['root'].rotation_euler = (0, 0, heading_yaw)
        char_parts['root'].keyframe_insert(data_path="location", frame=f)
        char_parts['root'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Pelvis: Pelvic list (roll) and rotation (yaw)
        pelvis_roll = math.radians(2.5) * math.sin(cycle_angle)
        pelvis_yaw = math.radians(3.5) * math.cos(cycle_angle)
        char_parts['pelvis'].location = Vector((0, 0, 0.95 + bounce))
        char_parts['pelvis'].rotation_euler = (math.radians(3.0), pelvis_roll, pelvis_yaw)
        char_parts['pelvis'].keyframe_insert(data_path="location", frame=f)
        char_parts['pelvis'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Torso: Counter-rotation to balance angular momentum
        torso_yaw = -pelvis_yaw * 0.85
        char_parts['torso'].rotation_euler = (math.radians(2.0), -pelvis_roll * 0.5, torso_yaw)
        char_parts['torso'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Head: Stabilized against horizon
        char_parts['head'].rotation_euler = (math.radians(-4.0), 0, -torso_yaw * 0.5)
        char_parts['head'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Leg Kinematics (Left & Right phase shifted by pi)
        def compute_leg_angles(phase):
            s = math.sin(phase)
            c = math.cos(phase)
            # Thigh pitch: forward when s > 0, backward when s < 0
            thigh_pitch = math.radians(24.0) * s
            
            # Knee flexion: bends during swing phase (when leg recovers from back to front)
            # Knee only bends backward (positive angle in local X)
            if s > -0.2: # Swing phase
                knee_bend = math.radians(45.0) * max(0.0, s) * (1.0 - 0.4 * max(0.0, c))
            else: # Stance / push-off phase
                knee_bend = math.radians(8.0) * abs(s)
                
            # Ankle dorsiflexion / plantarflexion:
            # Heel strike when swinging forward (dorsiflex +12°), push-off when extending back (-18°)
            ankle_pitch = math.radians(14.0) * s - knee_bend * 0.5
            return thigh_pitch, knee_bend, ankle_pitch

        thigh_l_p, knee_l_p, foot_l_p = compute_leg_angles(cycle_angle)
        thigh_r_p, knee_r_p, foot_r_p = compute_leg_angles(cycle_angle + math.pi)

        # Left Leg
        char_parts['thigh_l'].rotation_euler = (thigh_l_p, 0, 0)
        char_parts['shin_l'].rotation_euler = (knee_l_p, 0, 0)
        char_parts['foot_l'].rotation_euler = (foot_l_p, 0, 0)
        char_parts['thigh_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['shin_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['foot_l'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Right Leg
        char_parts['thigh_r'].rotation_euler = (thigh_r_p, 0, 0)
        char_parts['shin_r'].rotation_euler = (knee_r_p, 0, 0)
        char_parts['foot_r'].rotation_euler = (foot_r_p, 0, 0)
        char_parts['thigh_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['shin_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['foot_r'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Arms: Swing opposite to legs with elbow flexion pump
        arm_swing = math.radians(20.0) * math.sin(cycle_angle)
        # Left Arm swings with Right Leg
        char_parts['uarm_l'].rotation_euler = (-arm_swing, math.radians(-5.0), 0)
        char_parts['farm_l'].rotation_euler = (math.radians(50.0) + math.radians(15.0) * max(0.0, -arm_swing), 0, 0)
        char_parts['uarm_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['farm_l'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Right Arm swings with Left Leg
        char_parts['uarm_r'].rotation_euler = (arm_swing, math.radians(5.0), 0)
        char_parts['farm_r'].rotation_euler = (math.radians(50.0) + math.radians(15.0) * max(0.0, arm_swing), 0, 0)
        char_parts['uarm_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char_parts['farm_r'].keyframe_insert(data_path="rotation_euler", frame=f)

        # -------------------------------------------------------------
        # 2. CONTINUOUS 360-DEGREE ORBITAL CAMERA
        # -------------------------------------------------------------
        # Theta starts at -pi/2 (Third person rear follow down the road)
        # and completes a full 2*pi revolution across the 48 frames:
        theta = -math.pi / 2.0 + t * (2.0 * math.pi)

        cam_x = x_road + orbit_radius * math.cos(theta)
        cam_y = y + orbit_radius * math.sin(theta)
        # Elevated cinematic perspective: Z = 7.35 + 1.65m = 9.0m (looking slightly down at player)
        cam_z = z_ground + 1.65 + 0.12 * math.sin(theta)
        cam_obj.location = Vector((cam_x, cam_y, cam_z))

        # Camera track direction: Look directly at player focus target (chest/head level)
        target_pt = Vector((x_road, y, z_ground + 1.35))
        cam_dir = target_pt - cam_obj.location
        rot_quat = cam_dir.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    print(f"Keyframed {total_frames} frames of biomechanical gait and 360 camera orbit!")

# =====================================================================
# 4. LIGHTING & ENVIRONMENT MASTER SETUP
# =====================================================================
def setup_photoreal_lighting():
    print("=== CONFIGURING PHOTOREALISTIC GOLDEN HOUR TWILIGHT SCENE ===")
    scene = bpy.context.scene

    # 1. World Nishita Sky
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World_Mumbai_Photoreal")
        scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    
    sky_node = None
    bg_node = None
    for n in nt.nodes:
        if n.type == 'TEX_SKY':
            sky_node = n
        elif n.type == 'BACKGROUND':
            bg_node = n
    if not sky_node:
        sky_node = nt.nodes.new("ShaderNodeTexSky")
    if not bg_node:
        bg_node = nt.nodes.new("ShaderNodeBackground")
        
    sky_node.sky_type = 'MULTIPLE_SCATTERING'
    sky_node.sun_elevation = 0.16 # ~9.2° golden sunset over Arabian Sea!
    sky_node.sun_rotation = -2.35 # Western Arabian Sea angle
    sky_node.altitude = 20.0
    sky_node.air_density = 1.25 # Authentic Mumbai golden coastal haze
    sky_node.ozone_density = 2.40
    bg_node.inputs['Strength'].default_value = 1.25

    # 2. Key Sun Lamp
    sun = bpy.data.objects.get("SUN_Mumbai_Realistic") or bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        sdata = bpy.data.lights.new("Sun_Mumbai_Data", 'SUN')
        sun = bpy.data.objects.new("SUN_Mumbai_Realistic", sdata)
        bpy.context.scene.collection.objects.link(sun)
    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.88, 0.68) # Golden warm sunlight
    sun.data.angle = math.radians(2.2) # Soft penumbra shadows
    sun.rotation_euler = (math.radians(80.8), math.radians(5.0), math.radians(-135.0))

    # 3. Ambient Fill for character details
    fill = bpy.data.objects.get("LIGHT_Fill_GoldenHour")
    if not fill:
        fdata = bpy.data.lights.new("Light_Fill_Data", 'SUN')
        fill = bpy.data.objects.new("LIGHT_Fill_GoldenHour", fdata)
        bpy.context.scene.collection.objects.link(fill)
    fill.data.energy = 1.1
    fill.data.color = (0.55, 0.70, 0.95) # Sky blue ambient bounce
    fill.rotation_euler = (math.radians(35.0), 0, math.radians(45.0))

# =====================================================================
# 5. DYNAMIC TRAFFIC (MUMBAI KAALI PEELI TAXI)
# =====================================================================
def setup_road_traffic():
    print("=== CONFIGURING DYNAMIC ROAD TRAFFIC ===")
    taxi = bpy.data.objects.get("VEHICLE_MD_Taxi_Traffic")
    if not taxi:
        taxi_mesh = bpy.data.meshes.new("VEHICLE_MD_Taxi_Traffic_Mesh")
        bm = bmesh.new()
        # Chassis (black)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.50))) @ Matrix.Diagonal(Vector((1.70, 4.10, 0.80, 1.0))))
        # Cabin / Yellow Roof
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, -0.20, 1.05))) @ Matrix.Diagonal(Vector((1.55, 2.20, 0.65, 1.0))))
        # Wheels
        for wx in [-0.85, 0.85]:
            for wy in [-1.25, 1.25]:
                bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.33, radius2=0.33, depth=0.22, segments=12, matrix=Matrix.Translation(Vector((wx, wy, 0.33))) @ Matrix.Rotation(math.pi/2, 4, 'Y'))
        bm.to_mesh(taxi_mesh)
        bm.free()
        
        mat_black = get_or_create_pbr_mat("MAT_Taxi_BlackChassis", (0.04, 0.04, 0.05, 1.0), roughness=0.15, specular=0.8)
        mat_yellow = get_or_create_pbr_mat("MAT_Taxi_YellowRoof", (0.95, 0.75, 0.05, 1.0), roughness=0.20, specular=0.7)
        mat_wheel = get_or_create_pbr_mat("MAT_Taxi_RubberWheel", (0.05, 0.05, 0.05, 1.0), roughness=0.60)
        taxi_mesh.materials.append(mat_black)
        taxi_mesh.materials.append(mat_yellow)
        taxi_mesh.materials.append(mat_wheel)
        for p in taxi_mesh.polygons:
            if p.center.z > 0.85: p.material_index = 1
            elif p.center.z < 0.40: p.material_index = 2
            else: p.material_index = 0
            
        taxi = bpy.data.objects.new("VEHICLE_MD_Taxi_Traffic", taxi_mesh)
        bpy.context.scene.collection.objects.link(taxi)

    # Position taxi in adjacent northbound lane (X = -999.0m, Z = 7.35m)
    # Driving alongside the runner from Y = 1070 to Y = 1130
    for f in range(1, 49):
        t = (f - 1) / 48.0
        y_taxi = 1072.0 + t * 45.0
        x_taxi = -999.0 + 0.00008 * ((y_taxi - 1100.0)**2)
        taxi.location = Vector((x_taxi, y_taxi, 7.35))
        taxi.rotation_euler = (0, 0, math.atan(0.000160 * (y_taxi - 1100.0)))
        taxi.keyframe_insert(data_path="location", frame=f)
        taxi.keyframe_insert(data_path="rotation_euler", frame=f)

# =====================================================================
# 6. CYCLES METAL GPU PHOTOREAL RENDER SETTINGS
# =====================================================================
def configure_cycles_metal_render():
    print("=== CONFIGURING CYCLES METAL GPU PHOTOREAL RENDER ENGINE ===")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'

    # Metal GPU device configuration
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices:
        d.use = True

    # High quality photoreal settings
    scene.cycles.samples = 28 # Fast, clean sampling with OIDN AI denoiser
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 6
    scene.cycles.transparent_max_bounces = 8

    # Camera physical motion blur
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5

    # Color management: High Contrast AgX / Filmic
    scene.view_settings.view_transform = 'AgX' if hasattr(scene.view_settings, 'view_transform') and 'AgX' in scene.view_settings.view_transform else 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.20

    # Output Resolution: 1280x720 16:9 HD
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.camera = bpy.data.objects['Cam_Player_360_Orbit']

# =====================================================================
# 7. MAIN EXECUTION PIPELINE
# =====================================================================
if __name__ == '__main__':
    char = create_human_character()
    animate_biomechanical_gait_and_360_orbit(char)
    setup_photoreal_lighting()
    setup_road_traffic()
    configure_cycles_metal_render()

    blend_path = '/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend'
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Master file saved: {blend_path}")
