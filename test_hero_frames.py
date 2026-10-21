"""
Setup Biomechanical Walk & Test Render Frame 1 (Rear) and Frame 24 (Front) with Cycles
"""
import bpy
import bmesh
import math
import os
import sys
sys.path.append('/Users/ms/Downloads/GRAI')
from mathutils import Vector, Matrix, Euler

# Import animation logic
from build_perfect_physics_and_render_360 import animate_biomechanical_gait_and_360_orbit, setup_road_traffic

# Re-link character parts
root = bpy.data.objects['HUMAN_Root']
parts = {
    'root': root,
    'pelvis': bpy.data.objects['HUMAN_Pelvis'],
    'torso': bpy.data.objects['HUMAN_Torso'],
    'head': bpy.data.objects['HUMAN_Head'],
    'thigh_l': bpy.data.objects['HUMAN_Thigh_L'],
    'shin_l': bpy.data.objects['HUMAN_Shin_L'],
    'foot_l': bpy.data.objects['HUMAN_Foot_L'],
    'thigh_r': bpy.data.objects['HUMAN_Thigh_R'],
    'shin_r': bpy.data.objects['HUMAN_Shin_R'],
    'foot_r': bpy.data.objects['HUMAN_Foot_R'],
    'uarm_l': bpy.data.objects['HUMAN_UpperArm_L'],
    'farm_l': bpy.data.objects['HUMAN_Forearm_L'],
    'uarm_r': bpy.data.objects['HUMAN_UpperArm_R'],
    'farm_r': bpy.data.objects['HUMAN_Forearm_R'],
    'focus': bpy.data.objects['HUMAN_Focus_Target']
}

# Animate
animate_biomechanical_gait_and_360_orbit(parts)
setup_road_traffic()

# Calibrate lighting & exposure
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences
cprefs.compute_device_type = 'METAL'
cprefs.get_devices()
for d in cprefs.devices: d.use = True

world = scene.world
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Strength'].default_value = 0.065

sun = bpy.data.objects.get("SUN_Mumbai_Realistic") or bpy.data.objects.get("Sun_Mumbai")
if sun:
    sun.data.energy = 3.2
    sun.data.color = (1.0, 0.88, 0.70)
    sun.data.angle = math.radians(2.0)

scene.view_settings.exposure = -0.85
scene.view_settings.look = 'High Contrast'
scene.render.use_motion_blur = False
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720

cam = bpy.data.objects['Cam_Player_360_Orbit']
cam.data.lens = 38.0 # Cinematic lens
cam.data.dof.use_dof = True
cam.data.dof.focus_object = parts['focus']
cam.data.dof.aperture_fstop = 3.5
scene.camera = cam

bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')

# Render Frame 1 (Rear Follow)
scene.frame_set(1)
scene.render.filepath = '/tmp/hero_frame_01.png'
print("Rendering Frame 1 (Rear Follow)...")
bpy.ops.render.render(write_still=True)

# Render Frame 24 (Front Hero)
scene.frame_set(24)
scene.render.filepath = '/tmp/hero_frame_24.png'
print("Rendering Frame 24 (Front Hero)...")
bpy.ops.render.render(write_still=True)

print("Test hero frames rendered!")
