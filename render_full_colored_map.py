"""
Render Full-Colored Top-Down Map and Aerial Peninsula Vista of Mumbai in Blender Cycles
========================================================================================
1. Cam_Mumbai_Full_Map_TopDown:
   - High-altitude satellite top-down view framing the entire 17.4 km Mumbai peninsula in full color.
   - 1440x2560 vertical resolution to fit the North-South geography of Mumbai.
2. Cam_Mumbai_Overview:
   - 1920x1080 3D colored aerial overview capturing the full urban peninsula and coastal waters.
"""
import bpy
import math
from mathutils import Vector, Euler
import os, shutil

def render_full_colored_maps():
    print("=== CONFIGURING FULL COLORED MAP RENDERS ===")
    scene = bpy.context.scene

    # 1. Top-Down Satellite Camera (Cam_Mumbai_Full_Map_TopDown)
    cam_top_name = "Cam_Mumbai_Full_Map_TopDown"
    cam_top = bpy.data.objects.get(cam_top_name)
    if not cam_top:
        cdata = bpy.data.cameras.new(f"{cam_top_name}_Data")
        cam_top = bpy.data.objects.new(cam_top_name, cdata)
        scene.collection.objects.link(cam_top)

    # Frame the 17.4 km peninsula: Center X=-960m, Center Y=6300m
    cam_top.location = Vector((-960.0, 6300.0, 16500.0))
    cam_top.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
    cam_top.data.lens = 28.0
    cam_top.data.clip_start = 10.0
    cam_top.data.clip_end = 60000.0

    # 2. 3D Overview Camera (Cam_Mumbai_Overview)
    cam_ov_name = "Cam_Mumbai_Overview"
    cam_ov = bpy.data.objects.get(cam_ov_name)
    if cam_ov:
        cam_ov.data.clip_end = 60000.0

    # Ensure Cycles Metal GPU settings
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices:
        d.use = True

    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = -0.65

    # Render View 1: Top-Down Colored Satellite Map (Portrait 1440x2560 to match Mumbai's vertical geography)
    scene.camera = cam_top
    scene.render.resolution_x = 1440
    scene.render.resolution_y = 2560
    scene.render.resolution_percentage = 100

    out_top = "/Users/ms/Downloads/GRAI/renders/mumbai_full_colored_satellite_map.png"
    art_top = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/mumbai_full_colored_satellite_map.png"
    scene.render.filepath = out_top

    print("Rendering Full Colored Top-Down Satellite Map...")
    bpy.ops.render.render(write_still=True)
    if os.path.exists(out_top):
        shutil.copy2(out_top, art_top)
        print(f"Saved and copied {out_top}")

    # Render View 2: High-Altitude 3D Colored Overview (1920x1080 Landscape)
    if cam_ov:
        scene.camera = cam_ov
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        out_ov = "/Users/ms/Downloads/GRAI/renders/mumbai_full_colored_peninsula_aerial.png"
        art_ov = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/mumbai_full_colored_peninsula_aerial.png"
        scene.render.filepath = out_ov
        print("Rendering High-Altitude 3D Colored Peninsula Overview...")
        bpy.ops.render.render(write_still=True)
        if os.path.exists(out_ov):
            shutil.copy2(out_ov, art_ov)
            print(f"Saved and copied {out_ov}")

    # Also make a square 2048x2048 version of the full map
    scene.camera = cam_top
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 2048
    cam_top.location = Vector((-960.0, 6300.0, 18500.0))
    out_sq = "/Users/ms/Downloads/GRAI/renders/mumbai_full_colored_map_square.png"
    art_sq = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/mumbai_full_colored_map_square.png"
    scene.render.filepath = out_sq
    print("Rendering Square 2048x2048 Full Colored Map...")
    bpy.ops.render.render(write_still=True)
    if os.path.exists(out_sq):
        shutil.copy2(out_sq, art_sq)
        print(f"Saved and copied {out_sq}")

    # Save blend file
    bpy.ops.wm.save_as_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print("=== ALL FULL COLORED MAP RENDERS COMPLETED ===")

if __name__ == '__main__':
    render_full_colored_maps()
