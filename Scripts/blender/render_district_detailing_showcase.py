#!/usr/bin/env python3
"""
render_district_detailing_showcase.py
Renders 2 dedicated views verifying the district detailing:
1. Colaba Causeway Heritage Market Arcades (Striped shopfront canopies, wrought-iron balconies)
2. Lower Parel Historic Mill Chimneys & Soaring Megatowers
"""

import bpy
import mathutils
import math
import os

def main():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    renders_dir = "/Users/ms/Downloads/GRAI/renders/districts"
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

    # Camera 1: Colaba Causeway Market Arcade (Looking across street at market awnings)
    cam1 = get_or_create_cam(
        "Cam_District_Colaba_Market",
        loc=mathutils.Vector((52.0, -235.0, 11.2)),
        target=mathutils.Vector((66.5, -270.0, 11.0)),
        lens=28.0
    )

    # Camera 2: Lower Parel Historic Mill Chimney & Megatowers (Looking upward)
    cam2 = get_or_create_cam(
        "Cam_District_LowerParel_Mill",
        loc=mathutils.Vector((-420.0, 7000.0, 22.0)),
        target=mathutils.Vector((-520.0, 7150.0, 75.0)),
        lens=28.0
    )

    district_cameras = [
        ("district_1_colaba_causeway_market.png", cam1),
        ("district_2_lowerparel_chimneys_megatowers.png", cam2),
    ]

    for fname, cam in district_cameras:
        out_path = os.path.join(renders_dir, fname)
        brain_out_path = os.path.join(brain_renders_dir, fname)
        scene.camera = cam
        scene.render.filepath = out_path
        print(f"\n========================================================")
        print(f"RENDERING DISTRICT VIEW: {fname} using {cam.name}")
        print(f"========================================================")
        bpy.ops.render.render(write_still=True)
        print(f"Saved render to {out_path} ({os.path.getsize(out_path)} bytes)")
        
        # Mirror to brain directory
        with open(out_path, 'rb') as f_src, open(brain_out_path, 'wb') as f_dst:
            f_dst.write(f_src.read())
        print(f"Mirrored render to {brain_out_path}")

    scene.camera = cam1
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("District detailing render complete and blend saved.")

if __name__ == "__main__":
    main()
