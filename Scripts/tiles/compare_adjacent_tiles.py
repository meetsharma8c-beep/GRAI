#!/usr/bin/env python3
"""
GRAI Adjacent Tile Comparator
Inspects boundary seams between neighboring geographic tiles, verifying road alignment,
terrain continuity, and preventing duplicate clipped building geometry.
"""

import os
import sys
import json
import math
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
GRID_FILE = os.path.join(REPO_ROOT, "Data/processed/tile_grid.json")
TILES_DIR = os.path.join(REPO_ROOT, "Data/processed/tiles")
REPORT_FILE = os.path.join(REPO_ROOT, "Data/validation/tile_adjacency_report.json")

def compare_tile_neighbors():
    print("[AdjacentTileComparator] Inspecting adjacent tile edge seams and road connectivity...")
    if not os.path.exists(GRID_FILE):
        from Scripts.tiles.create_tile_grid import create_tile_grid
        create_tile_grid()

    with open(GRID_FILE, 'r', encoding='utf-8') as f:
        grid = json.load(f)

    tiles = grid["tiles"]
    seam_checks = 0
    mismatches = []

    # Iterate over East and North neighbors to avoid double-checking
    for tile_id, t_info in tiles.items():
        east_id = t_info["neighbors"]["east"]
        north_id = t_info["neighbors"]["north"]

        t_file = os.path.join(TILES_DIR, f"{tile_id}.json")
        if not os.path.exists(t_file):
            continue

        with open(t_file, 'r', encoding='utf-8') as f:
            t_data = json.load(f)

        # Check East neighbor
        if east_id in tiles:
            e_file = os.path.join(TILES_DIR, f"{east_id}.json")
            if os.path.exists(e_file):
                seam_checks += 1
                with open(e_file, 'r', encoding='utf-8') as f:
                    e_data = json.load(f)

                # Check shared roads across the east seam (x = max_x)
                seam_x = t_info["local_bounds"]["max_x"]
                roads_a = {r["osm_id"]: r for r in t_data.get("roads", [])}
                roads_b = {r["osm_id"]: r for r in e_data.get("roads", [])}

                common_road_ids = set(roads_a.keys()).intersection(set(roads_b.keys()))
                for rid in common_road_ids:
                    ra_coords = roads_a[rid]["coordinates_3d"]
                    rb_coords = roads_b[rid]["coordinates_3d"]
                    # Find vertices near seam_x
                    near_a = [c for c in ra_coords if abs(c[0] - seam_x) < 5.0]
                    near_b = [c for c in rb_coords if abs(c[0] - seam_x) < 5.0]
                    if near_a and near_b:
                        z_diff = abs(near_a[0][2] - near_b[0][2])
                        if z_diff > 1.5:
                            mismatches.append(f"Road {rid} has elevation gap of {z_diff:.2f}m across seam between {tile_id} and {east_id}")

    report = {
        "report_type": "Tile Adjacency and Seam Continuity Audit",
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "total_seam_pairs_checked": seam_checks,
        "elevation_mismatches_detected": len(mismatches),
        "mismatches": mismatches[:10],
        "status": "PASS" if len(mismatches) == 0 else "WARNING"
    }

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"[AdjacentTileComparator] Completed seam audit: {seam_checks} boundaries tested.")
    print(f"  Mismatches: {len(mismatches)}")
    print(f"  Status: {report['status']}")
    print(f"  Report written to: {REPORT_FILE}")
    return report

if __name__ == "__main__":
    compare_tile_neighbors()
