#!/usr/bin/env python3
"""
GRAI Blender Building Pipeline
Automates building mesh creation, custom provenance property attachment,
and material assignment in Blender's Python runtime.
"""

import os
import sys
import json

def import_buildings_to_blender(geometry_json_path: str, max_buildings: int = 500):
    import bpy

    print(f"[BlenderBuildingPipeline] Importing building meshes from {geometry_json_path}...")
    if not os.path.exists(geometry_json_path):
        raise FileNotFoundError(f"Geometry file not found: {geometry_json_path}")

    with open(geometry_json_path, 'r', encoding='utf-8') as f:
        meshes_data = json.load(f)

    # Collection setup
    col_name = "GRAI_BUILDINGS_AUTOMATED"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # Ensure materials exist
    import material_pipeline
    material_pipeline.setup_material_library()

    count = 0
    for data in meshes_data[:max_buildings]:
        asset_id = data["asset_id"]

        # Clean old object if exists
        if asset_id in bpy.data.objects:
            old_obj = bpy.data.objects[asset_id]
            bpy.data.objects.remove(old_obj, do_unlink=True)
        if asset_id in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[asset_id])

        mesh = bpy.data.meshes.new(asset_id)
        mesh.from_pydata(data["vertices"], [], data["faces"])
        mesh.update()

        obj = bpy.data.objects.new(asset_id, mesh)
        col.objects.link(obj)

        # Attach custom properties
        obj["source_id"] = data.get("source_id", "")
        obj["confidence_tier"] = data.get("confidence_tier", "LEVEL_C_UNAVAILABLE")
        obj["height_m"] = data.get("height_m", 0.0)
        obj["base_elevation_m"] = data.get("base_elevation_m", 0.0)

        # Assign material
        mat_name = f"MAT_Building_{obj['confidence_tier']}"
        if mat_name in bpy.data.materials:
            obj.data.materials.append(bpy.data.materials[mat_name])

        count += 1

    print(f"[BlenderBuildingPipeline] Successfully imported {count} buildings into collection '{col_name}'.")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    geom_path = os.path.join(repo_root, "Data/processed/buildings_geometry.json")
    sys.path.append(os.path.dirname(__file__))
    import_buildings_to_blender(geom_path)
