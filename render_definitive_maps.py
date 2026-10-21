"""
Render Master Photorealistic Full Mumbai Map in Blender Cycles
==============================================================
1. Expands Arabian Sea to 100km x 100km at Z=1.8m to submerge SRTM bathymetry,
   eliminating all rectangular borders and revealing the organic Mumbai peninsula.
2. Rich deep sapphire coastal ocean PBR shader (non-transparent, glossy Fresnel).
3. Rich monsoon parkland green and coastal sand PBR shaders for terrain.
4. Afternoon sun angle (45 degrees) with physical Nishita sky for vibrant illumination.
5. Renders:
   - definitive_full_rendered_mumbai_map.png (High-altitude 3D aerial view)
   - definitive_topdown_rendered_map.png (Top-down satellite map)
"""
import bpy
import math
from mathutils import Vector, Euler
import os, shutil

def setup_and_render_full_map():
    print("=== CONFIGURING MASTER FULL MUMBAI MAP REALISM ===")
    scene = bpy.context.scene

    # 1. Calibrate Arabian Sea
    sea = bpy.data.objects.get("Arabian_Sea")
    if sea:
        sea.location = Vector((-1000.0, 6000.0, 1.8)) # Centered on peninsula at Z=1.8m
        sea.scale = Vector((50000.0, 50000.0, 1.0)) # 100km x 100km expanse
        sea.dimensions = Vector((100000.0, 100000.0, 0.0))

    sea_mat = bpy.data.materials.get("MAT_Arabian_Sea")
    if sea_mat and sea_mat.use_nodes:
        bsdf = None
        for n in sea_mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
        if bsdf:
            # Deep rich coastal Arabian Sea blue
            bsdf.inputs['Base Color'].default_value = (0.015, 0.09, 0.22, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.07
            bsdf.inputs['Metallic'].default_value = 0.0
            if 'Transmission Weight' in bsdf.inputs:
                bsdf.inputs['Transmission Weight'].default_value = 0.0
            elif 'Transmission' in bsdf.inputs:
                bsdf.inputs['Transmission'].default_value = 0.0
            bsdf.inputs['IOR'].default_value = 1.333
        sea_mat.diffuse_color = (0.015, 0.09, 0.22, 1.0)

    # 2. Calibrate SRTM Terrain PBR Shader
    srtm_mat = bpy.data.materials.get("MAT_Mumbai_Peninsula_SRTM_PBR")
    if srtm_mat and srtm_mat.use_nodes:
        cr = srtm_mat.node_tree.nodes.get("Color Ramp")
        if cr:
            # Beach / coastal ground to lush monsoon greenery
            cr.color_ramp.elements[0].position = 0.15
            cr.color_ramp.elements[0].color = (0.62, 0.54, 0.40, 1.0) # Coastal sand / ground
            cr.color_ramp.elements[1].position = 0.60
            cr.color_ramp.elements[1].color = (0.16, 0.40, 0.16, 1.0) # Monsoon green canopy

        cr2 = srtm_mat.node_tree.nodes.get("Color Ramp.001")
        if cr2:
            cr2.color_ramp.elements[0].position = 0.10
            cr2.color_ramp.elements[0].color = (0.24, 0.26, 0.28, 1.0) # Paved / urban ground
            cr2.color_ramp.elements[1].position = 0.75
            cr2.color_ramp.elements[1].color = (0.18, 0.38, 0.18, 1.0) # Parkland vegetation

        srtm_mat.diffuse_color = (0.22, 0.38, 0.20, 1.0)

    # 3. Calibrate Ground & Terrain Landmass
    ground_mat = bpy.data.materials.get("MAT_Mumbai_Peninsula_Ground")
    if ground_mat and ground_mat.use_nodes:
        bsdf = None
        for n in ground_mat.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                bsdf = n
                break
        if bsdf and not bsdf.inputs['Base Color'].is_linked:
            bsdf.inputs['Base Color'].default_value = (0.20, 0.38, 0.18, 1.0)
        ground_mat.diffuse_color = (0.20, 0.38, 0.18, 1.0)

    # 4. Sun & Sky Lighting (High afternoon sun for vibrant illumination)
    sun = bpy.data.objects.get("Sun_Mumbai")
    if sun:
        sun.data.energy = 4.2
        sun.rotation_euler = Euler((math.radians(45.0), math.radians(15.0), math.radians(-45.0)), 'XYZ')

    # 5. Cycles Metal GPU Configuration
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices:
        d.use = True

    scene.cycles.samples = 36
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = -0.60

    # 6. Render View 1: 3D High-Altitude Aerial Full Map Vista
    cam_ov = bpy.data.objects.get("Cam_Mumbai_Overview")
    if cam_ov:
        # Move back and up to frame the whole peninsula from south to north with Back Bay in foreground
        cam_ov.location = Vector((-3200.0, 1200.0, 2600.0))
        target = Vector((-700.0, 6200.0, 20.0))
        cam_ov.rotation_euler = (target - cam_ov.location).to_track_quat('-Z', 'Y').to_euler()
        cam_ov.data.lens = 20.0 # Ultra-wide cinematic aerial
        cam_ov.data.clip_start = 10.0
        cam_ov.data.clip_end = 120000.0

        scene.camera = cam_ov
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        out1 = "/Users/ms/Downloads/GRAI/renders/definitive_full_rendered_mumbai_map.png"
        art1 = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/definitive_full_rendered_mumbai_map.png"
        scene.render.filepath = out1
        print("Rendering 3D High-Altitude Aerial Full Map in Cycles Metal...")
        bpy.ops.render.render(write_still=True)
        if os.path.exists(out1):
            shutil.copy2(out1, art1)
            print(f"Saved {out1}")

    # 7. Render View 2: Top-Down Satellite Full Map
    cam_top = bpy.data.objects.get("Cam_Mumbai_Full_Map_TopDown")
    if cam_top:
        cam_top.location = Vector((-960.0, 6300.0, 14000.0))
        cam_top.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
        cam_top.data.lens = 22.0
        cam_top.data.clip_start = 10.0
        cam_top.data.clip_end = 120000.0

        scene.camera = cam_top
        scene.render.resolution_x = 1440
        scene.render.resolution_y = 2560
        out2 = "/Users/ms/Downloads/GRAI/renders/definitive_topdown_rendered_map.png"
        art2 = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/definitive_topdown_rendered_map.png"
        scene.render.filepath = out2
        print("Rendering Top-Down Satellite Full Map in Cycles Metal...")
        bpy.ops.render.render(write_still=True)
        if os.path.exists(out2):
            shutil.copy2(out2, art2)
            print(f"Saved {out2}")

    # 8. Save main blend file
    bpy.ops.wm.save_as_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print("=== SAVED BLEND FILE & COMPLETED RENDERS ===")

if __name__ == '__main__':
    setup_and_render_full_map()
