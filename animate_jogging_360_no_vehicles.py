"""
Jogging Character on Netaji Subhash Road with Slow 360-Degree Camera Orbit (No Vehicles)
========================================================================================
1. Complete removal of all vehicle objects on Marine Drive.
2. Slower, majestic 360-degree continuous camera orbit: 96 frames (4.0 seconds at 24 fps).
3. Realistic jogging biomechanics:
   - Dynamic forward lean (7.5°).
   - Higher knee lift (64° flexion during recovery swing).
   - Tight athletic runner's arm carriage (75° elbow flexion with dynamic counter-pumping).
   - Dynamic vertical spring bounce (Z_bounce = 0.055m).
   - Full ankle heel-strike to toe-off spring propulsion.
4. Cycles Metal GPU path-traced photorealism with optical DOF.
"""
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix, Euler

sys.path.append('/Users/ms/Downloads/GRAI')
from sculpt_hero_human import build_hero_photoreal_human

def clean_all_vehicles():
    print("=== REMOVING ALL VEHICLES FROM SCENE ===")
    removed = 0
    for o in list(bpy.data.objects):
        name_upper = o.name.upper()
        if any(k in name_upper for k in ['VEHICLE', 'TAXI', 'CAR', 'CAB', 'BUS', 'RICKSHAW']):
            if 'SEALINK' not in name_upper: # Keep sea link cables
                bpy.data.objects.remove(o, do_unlink=True)
                removed += 1
    print(f"Removed {removed} vehicle objects. Netaji Subhash Road is completely open and clear!")

def setup_jogging_animation():
    clean_all_vehicles()
    
    print("=== SCULPTING HERO JOGGER CHARACTER ===")
    char = build_hero_photoreal_human()

    # Hide any stray rooftop fixtures if present
    rf = bpy.data.objects.get("ROOFTOP_Fixtures_Citywide_Master")
    if rf:
        rf.hide_render = True

    print("=== ANIMATING 96-FRAME JOGGING GAIT & SLOW 360 ORBIT ===")
    scene = bpy.context.scene
    total_frames = 96 # Slower 4.0 second loop at 24 fps
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = 24

    # Traversal parameters: 24 meters along Netaji Subhash Road
    y_start = 1088.0
    y_end = 1112.0
    orbit_radius = 3.40 # Cinematic camera distance
    gait_cycles = 6.0   # 6 full cycles (16 frames per cycle = 150 steps/min athletic jog cadence)

    # Camera
    cam_name = "Cam_Player_360_Orbit"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cdata = bpy.data.cameras.new(f"{cam_name}_Data")
        cam_obj = bpy.data.objects.new(cam_name, cdata)
        bpy.context.scene.collection.objects.link(cam_obj)
    
    cam_obj.data.lens = 36.0 # Cinematic focal length
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 25000.0
    cam_obj.data.dof.use_dof = True
    cam_obj.data.dof.focus_object = char['focus']
    cam_obj.data.dof.aperture_fstop = 3.6
    scene.camera = cam_obj

    for f in range(1, total_frames + 1):
        scene.frame_set(f)
        t = (f - 1) / float(total_frames)
        y = y_start + t * (y_end - y_start)

        # Marine Drive asphalt carriageway centerline (X = -1007.0m)
        x_road = -1007.0 + 0.000080 * ((y - 1100.0) ** 2)
        z_ground = 7.350

        # Heading along curved road
        dx_dy = 0.000160 * (y - 1100.0)
        heading_yaw = math.atan(dx_dy)

        # Jogging cycle phase (exact loop closure: 6 full cycles across 96 frames)
        cycle_angle = t * gait_cycles * 2.0 * math.pi

        # Jogging vertical spring bounce (double peak per stride cycle)
        bounce = abs(math.sin(cycle_angle)) * 0.055
        lat_shift = math.sin(cycle_angle) * 0.022

        # 1. Update Root (Running on asphalt road)
        char['root'].location = Vector((x_road + lat_shift, y, z_ground))
        char['root'].rotation_euler = (0, 0, heading_yaw)
        char['root'].keyframe_insert(data_path="location", frame=f)
        char['root'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 2. Pelvis: Jogger forward pitch + list + yaw
        pelvis_pitch = math.radians(6.5) # Active forward lean into run
        pelvis_roll = math.radians(2.8) * math.sin(cycle_angle)
        pelvis_yaw = math.radians(4.2) * math.cos(cycle_angle)
        char['pelvis'].location = Vector((0, 0, 0.95 + bounce))
        char['pelvis'].rotation_euler = (pelvis_pitch, pelvis_roll, pelvis_yaw)
        char['pelvis'].keyframe_insert(data_path="location", frame=f)
        char['pelvis'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 3. Torso: Athletic forward lean + counter-yaw balance
        torso_yaw = -pelvis_yaw * 0.85
        char['torso'].rotation_euler = (math.radians(2.0), -pelvis_roll * 0.5, torso_yaw)
        char['torso'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 4. Head: Stabilized against horizon looking forward down the road
        char['head'].rotation_euler = (math.radians(-7.0), 0, -torso_yaw * 0.4)
        char['head'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 5. Articulated Jogging Legs (Higher knee lift, dynamic heel-toe propulsion)
        def compute_jog_leg(phase):
            s = math.sin(phase)
            c = math.cos(phase)
            if s > 0: # Swing phase forward
                thigh = math.radians(32.0) * s
                # High athletic knee fold
                knee = math.radians(64.0) * s * (1.0 - 0.30 * max(0.0, c))
                # Foot dorsiflexion
                ankle = math.radians(16.0) * s - knee * 0.35
            else: # Stance & push-off phase backward
                thigh = math.radians(25.0) * s
                # Impact compliance bend
                knee = math.radians(14.0) * abs(s)
                # Strong toe push-off
                ankle = math.radians(24.0) * s
            return thigh, knee, ankle

        tl_p, kl_p, fl_p = compute_jog_leg(cycle_angle)
        tr_p, kr_p, fr_p = compute_jog_leg(cycle_angle + math.pi)

        char['thigh_l'].rotation_euler = (tl_p, 0, 0)
        char['shin_l'].rotation_euler = (kl_p, 0, 0)
        char['foot_l'].rotation_euler = (fl_p, 0, 0)
        char['thigh_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['shin_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['foot_l'].keyframe_insert(data_path="rotation_euler", frame=f)

        char['thigh_r'].rotation_euler = (tr_p, 0, 0)
        char['shin_r'].rotation_euler = (kr_p, 0, 0)
        char['foot_r'].rotation_euler = (fr_p, 0, 0)
        char['thigh_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['shin_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['foot_r'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 6. Jogging Arms (Tight carriage, flexed elbows, vigorous counter-pump)
        arm_s = math.radians(26.0) * math.sin(cycle_angle)
        # Left Arm (pumps opposite to left leg)
        char['uarm_l'].rotation_euler = (-arm_s, math.radians(-5.0), 0)
        char['farm_l'].rotation_euler = (math.radians(72.0) + math.radians(16.0) * max(0.0, -arm_s), 0, 0)
        char['uarm_l'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['farm_l'].keyframe_insert(data_path="rotation_euler", frame=f)

        # Right Arm (pumps opposite to right leg)
        char['uarm_r'].rotation_euler = (arm_s, math.radians(5.0), 0)
        char['farm_r'].rotation_euler = (math.radians(72.0) + math.radians(16.0) * max(0.0, arm_s), 0, 0)
        char['uarm_r'].keyframe_insert(data_path="rotation_euler", frame=f)
        char['farm_r'].keyframe_insert(data_path="rotation_euler", frame=f)

        # 7. SLOWER CONTINUOUS 360-DEGREE CAMERA ORBIT (96 Frames = 4.0 Seconds)
        # Slower, smoother, majestic rotation around the jogging player!
        theta = -math.pi / 2.0 + t * (2.0 * math.pi)

        cam_x = x_road + orbit_radius * math.cos(theta)
        cam_y = y + orbit_radius * math.sin(theta)
        cam_z = z_ground + 1.45 + 0.10 * math.sin(theta)
        cam_obj.location = Vector((cam_x, cam_y, cam_z))

        # Look target at player chest
        target_pt = Vector((x_road, y, z_ground + 1.28))
        cam_dir = target_pt - cam_obj.location
        rot_quat = cam_dir.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    print("Configured 96 frames of jogging gait and slow 360-degree camera orbit!")

    # Configure Cycles Render Settings
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True

    scene.cycles.samples = 14 # Optimized for speed and pristine AI denoising
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.use_motion_blur = False
    scene.view_settings.exposure = -0.85
    scene.view_settings.look = 'High Contrast'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    blend_file = '/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend'
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"Master file saved: {blend_file}")

if __name__ == '__main__':
    setup_jogging_animation()
