#!/usr/bin/env python3
"""
GRAI Blender Road Pipeline
Automates 3D road ribbon mesh construction, material assignment,
and custom property attachment in Blender's Python runtime.
"""

import os
import sys
import json
import math

def import_roads_to_blender(road_graph_path: str, max_roads: int = 500):
    import bpy

    print(f"[BlenderRoadPipeline] Importing road meshes from {road_graph_path}...")
    if not os.path.exists(road_graph_path):
        raise FileNotFoundError(f"Road graph file not found: {road_graph_path}")

    with open(road_graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)

    edges = graph.get("edges", [])

    # Collection setup
    col_name = "GRAI_ROADS_AUTOMATED"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    import material_pipeline
    material_pipeline.setup_material_library()

    count = 0
    for edge in edges[:max_roads]:
        osm_id = edge["osm_id"]
        coords_3d = edge["coordinates_3d"]
        width = edge["width_m"]
        h_type = edge["highway"]

        if len(coords_3d) < 2:
            continue

        half_w = max(1.0, width / 2.0)
        left_verts = []
        right_verts = []
        n = len(coords_3d)

        for i in range(n):
            cx, cy, cz = coords_3d[i]
            if i == 0:
                dx = coords_3d[1][0] - cx
                dy = coords_3d[1][1] - cy
            elif i == n - 1:
                dx = cx - coords_3d[n - 2][0]
                dy = cy - coords_3d[n - 2][1]
            else:
                dx = coords_3d[i + 1][0] - coords_3d[i - 1][0]
                dy = coords_3d[i + 1][1] - coords_3d[i - 1][1]

            mag = math.hypot(dx, dy)
            nx = -dy / mag if mag > 1e-4 else 0.0
            ny = dx / mag if mag > 1e-4 else 1.0

            left_verts.append((cx + nx * half_w, cy + ny * half_w, cz))
            right_verts.append((cx - nx * half_w, cy - ny * half_w, cz))

        vertices = left_verts + right_verts
        faces = []
        for i in range(n - 1):
            faces.append((i, i + 1, (i + 1) + n, i + n))

        obj_name = f"ROAD_{osm_id}"
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
        if obj_name in bpy.data.meshes:
            bpy.data.meshes.remove(bpy.data.meshes[obj_name])

        mesh = bpy.data.meshes.new(obj_name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        obj = bpy.data.objects.new(obj_name, mesh)
        col.objects.link(obj)

        obj["source_id"] = edge.get("source_id", "")
        obj["highway"] = h_type
        obj["width_m"] = width
        obj["length_m"] = edge.get("length_m", 0.0)

        # Assign material
        mat_name = f"MAT_Road_{h_type.capitalize()}"
        if mat_name not in bpy.data.materials:
            mat_name = "MAT_Road_Asphalt"
        if mat_name in bpy.data.materials:
            obj.data.materials.append(bpy.data.materials[mat_name])

        count += 1

    print(f"[BlenderRoadPipeline] Successfully imported {count} road segments into collection '{col_name}'.")

if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    road_path = os.path.join(repo_root, "Data/processed/road_graph.json")
    sys.path.append(os.path.dirname(__file__))
    import_roads_to_blender(road_path)
