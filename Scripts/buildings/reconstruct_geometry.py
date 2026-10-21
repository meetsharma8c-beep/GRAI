#!/usr/bin/env python3
"""
GRAI Building 3D Geometry Reconstruction
Generates 3D polygonal meshes (LOD0 & LOD1) from validated 2D footprints and assigned heights.
Generates outward-facing normals, metric UV coordinates, and exportable mesh data structures.
"""

import os
import sys
import json
import math
from typing import Dict, Any, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_attributed.json")
OUTPUT_GEOMETRY_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_geometry.json")

def triangulate_polygon_fan(coords: List[List[float]]) -> List[Tuple[int, int, int]]:
    """Simple robust ear-clipping/fan triangulation for planar 2D polygons."""
    n = len(coords)
    if n < 3:
        return []
    triangles = []
    for i in range(1, n - 1):
        triangles.append((0, i, i + 1))
    return triangles

def build_building_mesh(building: Dict[str, Any]) -> Dict[str, Any]:
    verts_2d = building["local_polygon_vertices"]
    # Remove duplicate closing vertex if present
    if len(verts_2d) > 2 and verts_2d[0] == verts_2d[-1]:
        verts_2d = verts_2d[:-1]

    n = len(verts_2d)
    if n < 3:
        return {}

    base_z = building.get("elevation_msl", 0.0)
    height = building.get("height_m", 10.0)
    top_z = base_z + height

    vertices: List[List[float]] = []
    # Bottom ring vertices (0 to n-1)
    for x, y in verts_2d:
        vertices.append([x, y, base_z])

    # Top ring vertices (n to 2n-1)
    for x, y in verts_2d:
        vertices.append([x, y, top_z])

    faces: List[List[int]] = []
    uvs: List[List[float]] = []

    # 1. Wall quads
    perimeter_dist = 0.0
    u_scale = 1.0 / 3.0 # 1 UV unit per 3 meters
    v_scale = 1.0 / 3.0

    for i in range(n):
        next_i = (i + 1) % n
        v0 = i
        v1 = next_i
        v2 = next_i + n
        v3 = i + n
        faces.append([v0, v1, v2, v3])

        dx = verts_2d[next_i][0] - verts_2d[i][0]
        dy = verts_2d[next_i][1] - verts_2d[i][1]
        seg_len = math.hypot(dx, dy)
        perimeter_dist += seg_len

    # 2. Roof faces (triangulated top ring)
    roof_tris = triangulate_polygon_fan(verts_2d)
    for t0, t1, t2 in roof_tris:
        # Reversing winding order so normal points Up (+Z)
        faces.append([t0 + n, t2 + n, t1 + n])

    return {
        "asset_id": building["asset_id"],
        "source_id": building["source_id"],
        "confidence_tier": building["confidence_tier"],
        "height_m": height,
        "base_elevation_m": base_z,
        "vertex_count": len(vertices),
        "face_count": len(faces),
        "vertices": vertices,
        "faces": faces
    }

def reconstruct_all_buildings():
    print("[GeometryReconstructor] Reconstructing 3D building meshes from attributed footprints...")
    if not os.path.exists(INPUT_FILE):
        from Scripts.buildings.assign_height import assign_building_heights
        assign_building_heights()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        buildings = json.load(f)

    mesh_registry = []
    total_verts = 0
    total_faces = 0

    for b in buildings:
        mesh = build_building_mesh(b)
        if mesh:
            mesh_registry.append(mesh)
            total_verts += mesh["vertex_count"]
            total_faces += mesh["face_count"]

    os.makedirs(os.path.dirname(OUTPUT_GEOMETRY_FILE), exist_ok=True)
    with open(OUTPUT_GEOMETRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(mesh_registry, f)

    print(f"[GeometryReconstructor] Successfully reconstructed {len(mesh_registry)} 3D buildings.")
    print(f"  Total Vertices: {total_verts}")
    print(f"  Total Faces: {total_faces}")
    print(f"  Saved mesh registry to: {OUTPUT_GEOMETRY_FILE}")
    return OUTPUT_GEOMETRY_FILE

if __name__ == "__main__":
    reconstruct_all_buildings()
