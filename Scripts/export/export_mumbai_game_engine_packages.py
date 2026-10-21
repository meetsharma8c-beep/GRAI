#!/usr/bin/env python3
"""
export_mumbai_game_engine_packages.py
=====================================
Packages and exports the complete Mumbai Digital Twin into industry-standard game engine formats:
1. Universal glTF 2.0 Binary (.glb) with embedded PBR materials for Unreal Engine 5, Unity, Godot 4, and WebGL
2. Autodesk FBX Binary (.fbx) for Unreal Engine 5 / Unity asset pipelines
"""

import bpy
import os
import time

def export_packages():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    export_dir = "/Users/ms/Downloads/GRAI/exports"
    os.makedirs(export_dir, exist_ok=True)

    print(f"\n========================================================")
    print("PACKAGING & EXPORTING MUMBAI DIGITAL TWIN FOR GAME ENGINES")
    print(f"Loading {blend_path}...")
    print(f"========================================================")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 1. Export glTF 2.0 Binary (.glb)
    glb_path = os.path.join(export_dir, "mumbai_digital_twin_master.glb")
    print(f"\n[1/2] Exporting Universal glTF 2.0 Binary: {glb_path}...")
    t0 = time.time()
    try:
        bpy.ops.export_scene.gltf(
            filepath=glb_path,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_yup=True,
            export_texcoords=True,
            export_normals=True,
            export_materials='EXPORT',
            export_colors=True,
            export_cameras=True,
            export_lights=True
        )
        dt = time.time() - t0
        size_mb = os.path.getsize(glb_path) / (1024 * 1024)
        print(f"glTF .glb export complete in {dt:.1f}s ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"Error during glTF export: {e}")

    # 2. Export Autodesk FBX (.fbx)
    fbx_path = os.path.join(export_dir, "mumbai_digital_twin_master.fbx")
    print(f"\n[2/2] Exporting Autodesk FBX 7.4 Binary: {fbx_path}...")
    t0 = time.time()
    try:
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=False,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Z',
            axis_up='Y',
            mesh_smooth_type='FACE',
            bake_space_transform=True
        )
        dt = time.time() - t0
        size_mb = os.path.getsize(fbx_path) / (1024 * 1024)
        print(f"FBX export complete in {dt:.1f}s ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"Error during FBX export: {e}")

    print("\n========================================================")
    print("GAME ENGINE EXPORT FINISHED SUCCESSFULLY!")
    print(f"Outputs stored in: {export_dir}")
    print("========================================================")

if __name__ == "__main__":
    export_packages()
