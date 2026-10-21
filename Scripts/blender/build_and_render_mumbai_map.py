#!/usr/bin/env python3
"""
build_and_render_mumbai_map.py
Creates dedicated aerial/orthographic map cameras, purges extreme unprojected objects,
configures the 3D viewport for GUI inspection, and renders 4 comprehensive map views.
"""

import bpy
import mathutils
import math
import os
import sys

def main():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    renders_dir = "/Users/ms/Downloads/GRAI/renders/maps"
    brain_renders_dir = "/Users/ms/.gemini/antigravity-ide/brain/c8431605-a131-4036-979c-c27954fd5f10/renders"
    
    os.makedirs(renders_dir, exist_ok=True)
    os.makedirs(brain_renders_dir, exist_ok=True)

    print(f"Loading {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 1. Purge extreme unprojected objects (> 50,000m away)
    purged_count = 0
    to_delete = []
    for o in bpy.data.objects:
        if abs(o.matrix_world.translation.x) > 50000 or abs(o.matrix_world.translation.y) > 50000:
            to_delete.append(o)
    
    for o in to_delete:
        print(f"Purging extreme coordinate object: {o.name} at {o.matrix_world.translation}")
        bpy.data.objects.remove(o, do_unlink=True)
        purged_count += 1
    print(f"Purged {purged_count} extreme objects.")

    # 2. Setup Sun & World Lighting for aerial map clarity
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Mumbai_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.75, 0.85, 0.98, 1.0)
        bg_node.inputs["Strength"].default_value = 1.3

    sun_light = bpy.data.objects.get("SUN_Global_Atmosphere")
    if not sun_light:
        light_data = bpy.data.lights.new(name="SUN_Global_Atmosphere", type='SUN')
        sun_light = bpy.data.objects.new(name="SUN_Global_Atmosphere", object_data=light_data)
        bpy.context.scene.collection.objects.link(sun_light)
    sun_light.data.energy = 5.0
    sun_light.data.angle = math.radians(2.0)
    sun_light.rotation_euler = (math.radians(52.0), math.radians(18.0), math.radians(-38.0))

    # Helper function to create or update camera
    def setup_camera(name, location, rotation_euler, cam_type='PERSP', ortho_scale=20000.0, clip_end=150000.0, lens=35.0):
        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name=name)
            cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        else:
            cam_data = cam_obj.data
        
        cam_obj.location = location
        cam_obj.rotation_euler = rotation_euler
        cam_data.type = cam_type
        if cam_type == 'ORTHO':
            cam_data.ortho_scale = ortho_scale
        else:
            cam_data.lens = lens
        cam_data.clip_start = 1.0
        cam_data.clip_end = clip_end
        return cam_obj

    # Helper function to point camera at target
    def look_at(cam_obj, target_pos):
        loc = cam_obj.location
        direction = target_pos - loc
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

    # Camera 1: Cartographic Orthographic Top-Down Map of entire Mumbai Peninsula
    # Center X ~ -570, Center Y ~ 6200
    cam1 = setup_camera(
        "Cam_Map_1_Full_Peninsula_Orthographic",
        location=mathutils.Vector((-570.0, 6200.0, 30000.0)),
        rotation_euler=(0.0, 0.0, 0.0),
        cam_type='ORTHO',
        ortho_scale=22000.0
    )

    # Camera 2: Iconic 3D Isometric Bird's-Eye Perspective looking North over the entire peninsula
    cam2 = setup_camera(
        "Cam_Map_2_Peninsula_Birdseye_Isometric",
        location=mathutils.Vector((-1200.0, -6800.0, 7500.0)),
        rotation_euler=(0.0, 0.0, 0.0),
        cam_type='PERSP',
        lens=28.0
    )
    look_at(cam2, mathutils.Vector((-600.0, 6500.0, 100.0)))

    # Camera 3: South Mumbai Urban Road Grid (Colaba, Marine Drive, Nariman Pt, Fort, CSMT)
    cam3 = setup_camera(
        "Cam_Map_3_South_Mumbai_Road_Grid",
        location=mathutils.Vector((-600.0, -3200.0, 3800.0)),
        rotation_euler=(0.0, 0.0, 0.0),
        cam_type='PERSP',
        lens=32.0
    )
    look_at(cam3, mathutils.Vector((-600.0, 1200.0, 30.0)))

    # Camera 4: Worli Skyline & Bandra-Worli Sea Link Coastal Corridor
    cam4 = setup_camera(
        "Cam_Map_4_Worli_SeaLink_Aerial",
        location=mathutils.Vector((-4500.0, 6500.0, 3500.0)),
        rotation_euler=(0.0, 0.0, 0.0),
        cam_type='PERSP',
        lens=35.0
    )
    look_at(cam4, mathutils.Vector((-1200.0, 9500.0, 80.0)))

    # 3. Configure Render Settings (Cycles, GPU / Apple Silicon Metal, 48 samples + denoise)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    # Ensure preferences use Metal if available
    try:
        cprefs = bpy.context.preferences.addons['cycles'].preferences
        cprefs.compute_device_type = 'METAL'
        for d in cprefs.devices:
            d.use = True
    except Exception as e:
        print(f"Note on Metal preferences: {e}")

    # Set active camera to Cam_Map_2 for viewport default
    scene.camera = cam2

    # Map renders list
    map_cameras = [
        ("map_1_mumbai_peninsula_orthographic.png", cam1),
        ("map_2_mumbai_peninsula_birdseye_isometric.png", cam2),
        ("map_3_south_mumbai_road_grid.png", cam3),
        ("map_4_worli_sealink_aerial.png", cam4)
    ]

    for fname, cam in map_cameras:
        out_path = os.path.join(renders_dir, fname)
        brain_out_path = os.path.join(brain_renders_dir, fname)
        scene.camera = cam
        scene.render.filepath = out_path
        print(f"\n========================================================")
        print(f"RENDERING MAP VIEW: {fname} using {cam.name}")
        print(f"========================================================")
        bpy.ops.render.render(write_still=True)
        print(f"Saved render to {out_path} ({os.path.getsize(out_path)} bytes)")
        
        # Copy to brain artifact directory
        with open(out_path, 'rb') as f_src, open(brain_out_path, 'wb') as f_dst:
            f_dst.write(f_src.read())
        print(f"Mirrored render to {brain_out_path}")

    # Reset camera to iconic bird's-eye map view for when user opens file
    scene.camera = cam2

    # Save the cleaned and updated blend file
    print(f"\nSaving updated master blend file: {blend_path}")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Blend file saved successfully.")

if __name__ == "__main__":
    main()
