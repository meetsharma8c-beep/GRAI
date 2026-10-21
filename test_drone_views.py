"""
Test Two Epic Drone Views of the Whole Mumbai Digital Twin:
1. Cam_Drone_QueensNecklace_Panorama (Back Bay aerial sweep over Marine Drive curve)
2. Cam_Drone_Peninsula_Spine_Vista (South-to-North whole peninsula aerial)
"""
import bpy
import math
from mathutils import Vector

scene = bpy.context.scene

# 1. Hide untextured proxy objects like Terrain_envelope
env = bpy.data.objects.get("Terrain_envelope")
if env:
    env.hide_render = True

# 2. Upgrade Terrain Shader to have realistic urban asphalt, parkland greens, and coastal tones
terrain_mat = bpy.data.materials.get("MAT_Mumbai_Peninsula_SRTM_PBR")
if terrain_mat and terrain_mat.node_tree:
    nt = terrain_mat.node_tree
    # Adjust noise texture scale for macro landscape variation
    noise = nt.nodes.get("Noise Texture")
    if noise:
        noise.inputs['Scale'].default_value = 0.003 # 300m macro landscape variations
        noise.inputs['Detail'].default_value = 6.0
        noise.inputs['Roughness'].default_value = 0.55
    cr = nt.nodes.get("Color Ramp")
    if cr:
        # Realistic urban coastal palette:
        # 0.0: Dark weathered coastal asphalt
        # 0.25: Urban concrete / built fabric
        # 0.60: Oval Maidan / Malabar Hill monsoon green parkland
        # 1.0: Malabar Hill ridge foliage
        cr.color_ramp.elements[0].color = (0.10, 0.11, 0.13, 1.0)
        cr.color_ramp.elements[1].color = (0.22, 0.23, 0.25, 1.0)
        cr.color_ramp.elements[2].color = (0.12, 0.24, 0.10, 1.0)
        cr.color_ramp.elements[3].color = (0.16, 0.28, 0.12, 1.0)

# 3. Create Drone View 1: Back Bay Marine Drive Crescent Panorama
cam1_name = "Cam_Drone_QueensNecklace_Panorama"
cam1 = bpy.data.objects.get(cam1_name)
if not cam1:
    cdata = bpy.data.cameras.new(f"{cam1_name}_Data")
    cam1 = bpy.data.objects.new(cam1_name, cdata)
    bpy.context.scene.collection.objects.link(cam1)

cam1.data.lens = 22.0 # Ultra-wide cinematic aerial drone lens
cam1.data.clip_start = 1.0
cam1.data.clip_end = 45000.0
cam1.location = Vector((-1750.0, 500.0, 340.0))
target1 = Vector((-900.0, 1350.0, 30.0))
cam1.rotation_euler = (target1 - cam1.location).to_track_quat('-Z', 'Y').to_euler()

# 4. Create Drone View 2: High-Altitude Peninsula Spine Vista
cam2_name = "Cam_Drone_Peninsula_Spine_Vista"
cam2 = bpy.data.objects.get(cam2_name)
if not cam2:
    cdata = bpy.data.cameras.new(f"{cam2_name}_Data")
    cam2 = bpy.data.objects.new(cam2_name, cdata)
    bpy.context.scene.collection.objects.link(cam2)

cam2.data.lens = 26.0
cam2.data.clip_start = 1.0
cam2.data.clip_end = 45000.0
cam2.location = Vector((-1300.0, -350.0, 680.0))
target2 = Vector((-950.0, 1400.0, 50.0))
cam2.rotation_euler = (target2 - cam2.location).to_track_quat('-Z', 'Y').to_euler()

# Render settings
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences
cprefs.compute_device_type = 'METAL'
cprefs.get_devices()
for d in cprefs.devices: d.use = True

scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.exposure = -0.75
scene.view_settings.look = 'High Contrast'

bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')

# Test Render View 1
scene.camera = cam1
scene.render.filepath = '/tmp/drone_view_1_crescent.png'
print("Rendering Drone View 1 (Queen's Necklace Crescent)...")
bpy.ops.render.render(write_still=True)

# Test Render View 2
scene.camera = cam2
scene.render.filepath = '/tmp/drone_view_2_peninsula.png'
print("Rendering Drone View 2 (Peninsula Spine)...")
bpy.ops.render.render(write_still=True)

print("Both test drone views rendered successfully!")
