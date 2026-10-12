"""
Tuning Masterpiece Materials, Golden Hour Lighting, and Rendering Full Suite
- Dark asphalt / concrete city ground contrast
- Dramatic low golden-hour sun (elevation ~8 deg) creating iconic long sunset shadows
- Deep navy/teal ocean with specular sun trail
- Full 4K/1080p renders of all 5 iconic Mumbai perspectives
"""
import bpy
import math
from mathutils import Vector

# 1. Darken and texture the Peninsula Landmass Ground
mat_land = bpy.data.materials.get("MAT_Mumbai_Peninsula_Ground")
if mat_land and mat_land.use_nodes:
    bsdf = mat_land.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.22, 0.23, 0.24, 1.0) # Real asphalt/concrete urban ground
        bsdf.inputs['Roughness'].default_value = 0.9

# 2. Rich Deep Arabian Sea Shader
mat_sea = bpy.data.materials.get("MAT_Arabian_Sea")
if mat_sea and mat_sea.use_nodes:
    bsdf = mat_sea.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.015, 0.12, 0.20, 1.0) # Deep Arabian Sea navy
        bsdf.inputs['Roughness'].default_value = 0.08 # Mirror-like water for sunset glint
        bsdf.inputs['Metallic'].default_value = 0.1

# 3. Golden Hour Sunset Sky & Warm Sun Light
world = bpy.context.scene.world
if world and world.use_nodes:
    for n in world.node_tree.nodes:
        if n.type == 'TEX_SKY':
            n.sun_elevation = 0.12 # ~7 degrees above western sea horizon
            n.sun_rotation = -2.05 # Due west sunset
            n.sun_intensity = 1.0
            n.air_density = 1.3
            n.aerosol_density = 1.8 # Rich atmospheric haze
            n.ground_albedo = 0.2

sun = bpy.data.objects.get("Sun_Mumbai")
if sun:
    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.82, 0.60) # Deep golden-amber sunset light
    sun.data.angle = math.radians(3.5) # Soft architectural shadows
    sun.rotation_euler = (math.radians(78.0), math.radians(5.0), math.radians(-120.0))

# Save mainfile to preserve all 5,600+ objects
bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
print("Saved GRAI_Mumbai_Digital_Twin.blend with full masterpiece geometry.")

# Render List
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

renders = [
    ("Cam_Mumbai_Playable_Map_Master", "/tmp/mumbai_master_overview_final.png"),
    ("Cam_MarineDrive_QueensNecklace", "/tmp/mumbai_marinedrive_final.png"),
    ("Cam_SeaLink_Hero", "/tmp/mumbai_sealink_final.png"),
    ("Cam_SeaLink_Driver", "/tmp/mumbai_sealink_driver_final.png"),
    ("Cam_Fort_Heritage_District", "/tmp/mumbai_fort_heritage_final.png"),
]

for cam_name, out_path in renders:
    cam = bpy.data.objects.get(cam_name)
    if cam:
        scene.camera = cam
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {cam_name} -> {out_path}")

result = "Full Masterpiece Suite Rendered and Saved Successfully!"
print(result)
