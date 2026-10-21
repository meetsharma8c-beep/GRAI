#!/usr/bin/env python3
"""
GRAI Building Asset Exporter
Exports validated 3D building meshes to Wavefront OBJ / FBX format with embedded provenance metadata,
ready for Unreal Engine 5.8 Nanite static mesh ingestion and Blender technical workflows.
"""

import os
import sys
import json
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_geometry.json")
OUTPUT_DIR = os.path.join(REPO_ROOT, "Data/processed/exported_buildings")

def export_buildings_to_obj(output_filename: str = "mumbai_buildings_batch.obj") -> str:
    print(f"[BuildingExporter] Exporting buildings to OBJ format in {OUTPUT_DIR}...")
    if not os.path.exists(INPUT_FILE):
        from Scripts.buildings.reconstruct_geometry import reconstruct_all_buildings
        reconstruct_all_buildings()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        meshes = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, output_filename)

    vertex_offset = 1
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# GRAI Mumbai Digital Twin — Procedural Buildings OBJ Export\n")
        f.write(f"# Total Buildings: {len(meshes)}\n")
        f.write("# Units: Metric Meters (Z-up)\n\n")

        for mesh in meshes:
            asset_id = mesh["asset_id"]
            tier = mesh.get("confidence_tier", "LEVEL_C_UNAVAILABLE")
            f.write(f"o {asset_id}\n")
            f.write(f"# meta:confidence_tier={tier}\n")
            f.write(f"# meta:source_id={mesh.get('source_id')}\n")
            f.write(f"# meta:height_m={mesh.get('height_m')}\n")
            f.write(f"usemtl MAT_Building_{tier}\n")

            verts = mesh["vertices"]
            for x, y, z in verts:
                f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")

            faces = mesh["faces"]
            for face in faces:
                # 1-indexed for OBJ
                face_indices = [str(idx + vertex_offset) for idx in face]
                f.write(f"f {' '.join(face_indices)}\n")

            vertex_offset += len(verts)

    print(f"[BuildingExporter] Successfully exported {len(meshes)} buildings to {out_path} ({os.path.getsize(out_path)} bytes).")
    return out_path

if __name__ == "__main__":
    export_buildings_to_obj()
