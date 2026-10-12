"""
Test fixing the World Background Shader and test rendering in Cycles vs EEVEE Next
"""
import bpy
import math

# 1. Fix World Node Tree: Sky Texture -> Background Node -> World Output
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World_Mumbai_Atmosphere")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

out = nodes.new("ShaderNodeOutputWorld")
out.location = (600, 0)

bg = nodes.new("ShaderNodeBackground")
bg.location = (300, 0)
bg.inputs['Strength'].default_value = 1.0

sky = nodes.new("ShaderNodeTexSky")
sky.location = (0, 0)
sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_elevation = math.radians(8.5) # ~8.5 degrees above horizon (Golden Sunset)
sky.sun_rotation = math.radians(245.0) # West-southwest over Arabian Sea
sky.sun_intensity = 1.0
sky.air_density = 1.2
sky.aerosol_density = 1.6 # Realistic coastal Mumbai maritime haze
sky.ground_albedo = 0.25

links.new(sky.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], out.inputs['Surface'])

# 2. Configure Sun Light matching the sky sun position
sun = bpy.data.objects.get("Sun_Mumbai")
if not sun:
    sun_data = bpy.data.lights.new(name="Sun_Mumbai", type='SUN')
    sun = bpy.data.objects.new("Sun_Mumbai", sun_data)
    bpy.context.scene.collection.objects.link(sun)

sun.data.energy = 3.5
sun.data.color = (1.0, 0.82, 0.62) # Warm golden hour sunlight
sun.data.angle = math.radians(3.5) # Soft architectural shadows
# Align rotation with sun_elevation (8.5 deg) and sun_rotation (245 deg)
sun.rotation_euler = (math.radians(81.5), math.radians(3.0), math.radians(-115.0))

# 3. Color Management: Filmic or AgX with Medium High Contrast
scene = bpy.context.scene
scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.0

# 4. Render test frame
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
cam = bpy.data.objects.get("Cam_Fort_Heritage_District")
if cam:
    scene.camera = cam
    scene.render.filepath = "/tmp/test_sky_fix_eevee.png"
    bpy.ops.render.render(write_still=True)

print("Sky fix and EEVEE test complete.")
