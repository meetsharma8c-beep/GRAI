#!/usr/bin/env python3
"""
GRAI Blender Asset Exporter
Exports validated procedural geometry and landmarks from Blender into FBX / glTF formats
for Unreal Engine 5.8 ingestion, preserving transforms, Nanite readiness, and custom properties.
"""

import os
import sys

def export_collection_to_fbx(collection_name: str, output_filepath: str):
    import bpy

    print(f"[BlenderAssetExporter] Exporting collection '{collection_name}' to {output_filepath}...")
    if collection_name not in bpy.data.collections:
        print(f"  Warning: Collection '{collection_name}' not found. Skipping.")
        return False

    col = bpy.data.collections[collection_name]
    if not col.objects:
        print(f"  Warning: Collection '{collection_name}' contains no objects.")
        return False

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = col.objects[0]

    # Export FBX with Z-up, Y-forward
    bpy.ops.export_scene.fbx(
        filepath=output_filepath,
        use_selection=True,
        global_scale=1.0,
        axis_forward='Y',
        axis_up='Z',
        apply_unit_scale=True,
        bake_space_transform=True,
        object_types={'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE'
    )

    print(f"[BlenderAssetExporter] Successfully exported FBX to {output_filepath} ({os.path.getsize(output_filepath)} bytes).")
    return True

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    out_fbx = os.path.join(repo_root, "Data/processed/exported_fbx/mumbai_buildings_blender.fbx")
    export_collection_to_fbx("GRAI_BUILDINGS_AUTOMATED", out_fbx)
