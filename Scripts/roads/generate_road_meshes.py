#!/usr/bin/env python3
"""
GRAI Road Mesh Generator
Generates continuous 3D polygonal ribbon meshes from validated road graph linestrings,
applying road width offsets, collision boundaries, and standard OBJ export.
"""

import os
import sys
import json
import math
from typing import Dict, Any, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/road_graph.json")
OUTPUT_DIR = os.path.join(REPO_ROOT, "Data/processed/exported_roads")

def generate_road_ribbon(coords_3d: List[List[float]], width: float) -> Tuple[List[List[float]], List[List[int]]]:
    n = len(coords_3d)
    if n < 2:
        return [], []

    half_w = max(1.0, width / 2.0)
    left_verts = []
    right_verts = []

    for i in range(n):
        cx, cy, cz = coords_3d[i]
        # Tangent vector
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
        if mag < 1e-4:
            nx, ny = 0.0, 1.0
        else:
            # Perpendicular normal (-dy, dx)
            nx = -dy / mag
            ny = dx / mag

        left_verts.append([round(cx + nx * half_w, 3), round(cy + ny * half_w, 3), round(cz, 3)])
        right_verts.append([round(cx - nx * half_w, 3), round(cy - ny * half_w, 3), round(cz, 3)])

    vertices = left_verts + right_verts
    faces = []

    for i in range(n - 1):
        # Left side: i, i+1; Right side: i+n, (i+1)+n
        v_l0 = i
        v_l1 = i + 1
        v_r1 = (i + 1) + n
        v_r0 = i + n
        faces.append([v_l0, v_l1, v_r1, v_r0])

    return vertices, faces

def generate_all_road_meshes(output_filename: str = "mumbai_roads_batch.obj") -> str:
    print("[RoadMeshGenerator] Generating 3D road ribbon meshes...")
    if not os.path.exists(INPUT_FILE):
        from Scripts.roads.build_road_graph import build_road_graph
        build_road_graph()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        graph = json.load(f)

    edges = graph["edges"]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, output_filename)

    vertex_offset = 1
    total_quads = 0

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# GRAI Mumbai Digital Twin — Road Mesh Network OBJ Export\n")
        f.write(f"# Total Road Segments: {len(edges)}\n")
        f.write("# Units: Metric Meters (Z-up)\n\n")

        for e in edges:
            osm_id = e["osm_id"]
            h_type = e["highway"]
            width = e["width_m"]
            coords = e["coordinates_3d"]

            verts, faces = generate_road_ribbon(coords, width)
            if not verts or not faces:
                continue

            f.write(f"o ROAD_{osm_id}\n")
            f.write(f"# meta:highway={h_type}\n")
            f.write(f"# meta:width_m={width}\n")
            f.write(f"usemtl MAT_Road_{h_type}\n")

            for x, y, z in verts:
                f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")

            for face in faces:
                idx_str = [str(idx + vertex_offset) for idx in face]
                f.write(f"f {' '.join(idx_str)}\n")

            vertex_offset += len(verts)
            total_quads += len(faces)

    print(f"[RoadMeshGenerator] Successfully exported {len(edges)} road segments to {out_path}.")
    print(f"  Total Road Quads: {total_quads}")
    print(f"  File size: {os.path.getsize(out_path)} bytes")
    return out_path

if __name__ == "__main__":
    generate_all_road_meshes()
