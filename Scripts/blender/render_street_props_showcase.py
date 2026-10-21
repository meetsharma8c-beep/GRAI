#!/usr/bin/env python3
"""
render_street_props_showcase.py
Renders 3 dedicated close-up views verifying the street-level urban furniture:
1. Marine Drive Queen's Necklace: Victorian 3-globe lampposts, highway median masts, BEST shelter, bilingual street sign
2. Fort / CSMT Victoria Terminus: Traffic signal cantilever, red Indian Post box, Victorian fire hydrant, pedestrian railings
3. Apollo Bunder Gateway Plaza: Basalt security bollards, street signs, heritage lanterns
"""

import bpy
import mathutils
import math
import os

def main():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    renders_dir = "/Users/ms/Downloads/GRAI/renders/props"
    brain_renders_dir = "/Users/ms/.gemini/antigravity-ide/brain/c8431605-a131-4036-979c-c27954fd5f10/renders"
    
    os.makedirs(renders_dir, exist_ok=True)
    os.makedirs(brain_renders_dir, exist_ok=True)

    print(f"Loading {blend_path}...")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    def look_at(cam_obj, target_pos):
        direction = target_pos - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()

    def get_or_create_cam(name, loc, target, lens=35.0):
        cam_obj = bpy.data.objects.get(name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(name=name)
            cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
            scene.collection.objects.link(cam_obj)
        else:
            cam_data = cam_obj.data
        cam_obj.location = loc
        cam_data.lens = lens
        cam_data.clip_start = 0.5
        cam_data.clip_end = 20000.0
        look_at(cam_obj, target)
        return cam_obj

    # Camera 1: Marine Drive Street Props (Near Veer Nariman Junction)
    # Looking north-west: Lampposts, BEST shelter at [-980, 980], street sign at [-982, 920], median masts
    cam1 = get_or_create_cam(
        "Cam_Prop_1_MarineDrive_Furniture",
        loc=mathutils.Vector((-995.0, 890.0, 9.5)),
        target=mathutils.Vector((-990.0, 1020.0, 8.5)),
        lens=32.0
    )

    # Camera 2: Fort / CSMT Urban Furniture
    # Standing on Dr. DN Road: Traffic signal at [240, 1750], post box at [248, 1690], hydrant at [238, 1675], shelter at [252, 1710]
    cam2 = get_or_create_cam(
        "Cam_Prop_2_Fort_CSMT_Furniture",
        loc=mathutils.Vector((260.0, 1665.0, 19.5)),
        target=mathutils.Vector((246.0, 1710.0, 14.8)),
        lens=32.0
    )

    # Camera 3: Gateway of India Plaza Basalt Bollards & Approach Signage
    # Looking towards Gateway arch: Bollards lining Y = -155, street sign at [165, -170], Taj Palace on left
    cam3 = get_or_create_cam(
        "Cam_Prop_3_Gateway_Basalt_Plaza",
        loc=mathutils.Vector((135.0, -185.0, 5.8)),
        target=mathutils.Vector((165.0, -140.0, 6.5)),
        lens=30.0
    )

    prop_cameras = [
        ("prop_1_marinedrive_street_furniture.png", cam1),
        ("prop_2_csmt_fort_street_furniture.png", cam2),
        ("prop_3_gateway_plaza_bollards.png", cam3)
    ]

    for fname, cam in prop_cameras:
        out_path = os.path.join(renders_dir, fname)
        brain_out_path = os.path.join(brain_renders_dir, fname)
        scene.camera = cam
        scene.render.filepath = out_path
        print(f"\n========================================================")
        print(f"RENDERING STREET PROP VIEW: {fname} using {cam.name}")
        print(f"========================================================")
        bpy.ops.render.render(write_still=True)
        print(f"Saved render to {out_path} ({os.path.getsize(out_path)} bytes)")
        
        # Mirror to brain directory
        with open(out_path, 'rb') as f_src, open(brain_out_path, 'wb') as f_dst:
            f_dst.write(f_src.read())
        print(f"Mirrored render to {brain_out_path}")

    # Set default camera
    scene.camera = cam1
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Props render showcase complete and blend file saved.")

if __name__ == "__main__":
    main()
