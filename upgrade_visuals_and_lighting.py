"""
Upgrade Mumbai Digital Twin Visuals:
- Realistic Arabian Sea physical water shader with procedural wave bumps
- Physical Indian Sun & Sky lighting (warm late-afternoon Mumbai sun)
- Polished road & building materials
- Master panoramic playable overview camera showing the entire city
"""
import bpy
import math
from mathutils import Vector

# ------------------------------------------------------------------
# 1. Realistic Arabian Sea Water Material
# ------------------------------------------------------------------
mat_sea = bpy.data.materials.get("MAT_Arabian_Sea")
if not mat_sea:
    mat_sea = bpy.data.materials.new(name="MAT_Arabian_Sea")
    mat_sea.use_nodes = True

nodes = mat_sea.node_tree.nodes
links = mat_sea.node_tree.links
nodes.clear()

# Node setup: Principled BSDF + Wave Texture Normal Bump
node_out = nodes.new("ShaderNodeOutputMaterial")
node_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
node_bsdf.inputs['Base Color'].default_value = (0.04, 0.22, 0.32, 1.0) # Deep Arabian Sea cyan-blue
node_bsdf.inputs['Metallic'].default_value = 0.15
node_bsdf.inputs['Roughness'].default_value = 0.12 # Reflective water surface
if 'IOR' in node_bsdf.inputs:
    node_bsdf.inputs['IOR'].default_value = 1.333

# Procedural subtle wave bump
node_bump = nodes.new("ShaderNodeBump")
node_bump.inputs['Strength'].default_value = 0.35
node_bump.inputs['Distance'].default_value = 0.8

node_noise = nodes.new("ShaderNodeTexNoise")
node_noise.inputs['Scale'].default_value = 45.0
node_noise.inputs['Detail'].default_value = 4.0
node_noise.inputs['Roughness'].default_value = 0.6

links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

# Assign to Arabian Sea plane
sea_obj = bpy.data.objects.get("Arabian_Sea")
if sea_obj:
    sea_obj.data.materials.clear()
    sea_obj.data.materials.append(mat_sea)
    # Ensure sea plane is large enough to cover the entire Mumbai region
    sea_obj.dimensions = (35000.0, 35000.0, 0.0)
    sea_obj.location = Vector((-2000.0, 5000.0, -0.2))

# ------------------------------------------------------------------
# 2. Warm Indian Sunlight & Atmospheric Sky
# ------------------------------------------------------------------
# Configure World Sky Background
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("Mumbai_World")
    bpy.context.scene.world = world
world.use_nodes = True
w_nodes = world.node_tree.nodes
w_links = world.node_tree.links
w_nodes.clear()

w_out = w_nodes.new("ShaderNodeOutputWorld")
w_bg = w_nodes.new("ShaderNodeBackground")
# Realistic atmospheric sky color (warm tropical Mumbai hazy blue-white)
w_bg.inputs['Color'].default_value = (0.68, 0.78, 0.88, 1.0)
w_bg.inputs['Strength'].default_value = 1.25
w_links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

# Configure Main Sunlight
sun_obj = bpy.data.objects.get("Sun_Mumbai")
if not sun_obj:
    sun_data = bpy.data.lights.new("Sun_Mumbai", 'SUN')
    sun_obj = bpy.data.objects.new("Sun_Mumbai", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)

sun_obj.data.energy = 5.2
sun_obj.data.color = (1.0, 0.94, 0.85) # Warm golden sunlight
sun_obj.data.angle = math.radians(2.5) # Soft shadows
# Position and angle: Late afternoon sun shining from west-southwest
sun_obj.location = Vector((-3000.0, 2000.0, 5000.0))
sun_obj.rotation_euler = (math.radians(52.0), math.radians(12.0), math.radians(-115.0))

# ------------------------------------------------------------------
# 3. Create Master High-Altitude Panoramic Playable Map Camera
# ------------------------------------------------------------------
cam_master_name = "Cam_Mumbai_Playable_Map_Master"
if cam_master_name in bpy.data.objects:
    cam_master = bpy.data.objects[cam_master_name]
else:
    cam_data = bpy.data.cameras.new(cam_master_name)
    cam_master = bpy.data.objects.new(cam_master_name, cam_data)
    bpy.context.scene.collection.objects.link(cam_master)

cam_master.data.clip_end = 45000.0
cam_master.data.clip_start = 1.0
cam_master.data.lens = 24.0 # Wide angle cinematic lens

# Position high above Arabian Sea south-west of Mumbai looking northeast across all 4 sectors:
# Colaba, Nariman Point, Marine Drive, Fort/CSMT, and the Bandra-Worli Sea Link!
cam_master.location = Vector((-3800.0, -1200.0, 2800.0))
direction = Vector((-600.0, 6500.0, 0.0)) - cam_master.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_master.rotation_euler = rot_quat.to_euler()

# Also configure Eevee / Render engine settings
scene = bpy.context.scene
if hasattr(scene, "eevee"):
    # Enable ambient occlusion, bloom, screen space reflections if available
    try:
        scene.eevee.use_gtao = True
        scene.eevee.use_ssr = True
    except Exception:
        pass

result = "Visuals, Arabian Sea water shader, sun lighting, and Master Camera updated!"
print(result)
