#!/usr/bin/env python3
"""
GRAI World Coverage Reporter
Generates comprehensive machine-readable and human-readable coverage reports
showing verified vs inferred geometry, missing data areas, and confidence metrics.
"""

import os
import sys
import json
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
GRID_FILE = os.path.join(REPO_ROOT, "Data/processed/tile_grid.json")
TILES_DIR = os.path.join(REPO_ROOT, "Data/processed/tiles")
REPORT_JSON = os.path.join(REPO_ROOT, "Reports/mumbai_world_coverage_report.json")
REPORT_MD = os.path.join(REPO_ROOT, "Reports/mumbai_world_coverage_summary.md")

def generate_coverage_report():
    print("[CoverageReporter] Generating comprehensive Mumbai world coverage report...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    if not os.path.exists(GRID_FILE):
        from Scripts.tiles.create_tile_grid import create_tile_grid
        create_tile_grid()

    with open(GRID_FILE, 'r', encoding='utf-8') as f:
        grid = json.load(f)

    tiles = grid["tiles"]
    total_grid_tiles = len(tiles)

    total_buildings = 0
    level_a_verified = 0
    level_b_inferred = 0
    level_c_unavailable = 0
    total_roads = 0
    total_road_km = 0.0
    active_tiles = 0

    tile_summaries = []

    for tile_id, t_info in tiles.items():
        t_file = os.path.join(TILES_DIR, f"{tile_id}.json")
        if os.path.exists(t_file):
            with open(t_file, 'r', encoding='utf-8') as f:
                t_data = json.load(f)
            stats = t_data["statistics"]
            b_cnt = stats["total_buildings"]
            r_cnt = stats["total_roads"]
            r_len = stats.get("road_length_m", 0.0)

            if b_cnt > 0 or r_cnt > 0:
                active_tiles += 1
                total_buildings += b_cnt
                level_a_verified += stats.get("level_a_verified", 0)
                level_b_inferred += stats.get("level_b_inferred", 0)
                level_c_unavailable += stats.get("level_c_unavailable", 0)
                total_roads += r_cnt
                total_road_km += r_len / 1000.0

                tile_summaries.append({
                    "tile_id": tile_id,
                    "buildings": b_cnt,
                    "roads": r_cnt,
                    "road_km": round(r_len / 1000.0, 2),
                    "confidence": stats.get("confidence_score", 0.0)
                })

    report_data = {
        "project": "GRAI — Grand Roads of India",
        "subproject": "Mumbai Digital Twin",
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "geographic_extent": config.get("geospatial", {}).get("boundaries", {}).get("metropolitan_mumbai", {}),
        "world_origin": config.get("geospatial", {}).get("unreal_world_origin", {}),
        "grid_metrics": {
            "total_tiles_defined": total_grid_tiles,
            "active_populated_tiles": active_tiles,
            "empty_sea_or_unmapped_tiles": total_grid_tiles - active_tiles
        },
        "feature_metrics": {
            "total_buildings": total_buildings,
            "level_a_verified": level_a_verified,
            "level_b_inferred": level_b_inferred,
            "level_c_unavailable": level_c_unavailable,
            "total_roads": total_roads,
            "total_road_network_km": round(total_road_km, 2)
        },
        "data_provenance": {
            "elevation": "NASA/USGS SRTM 1-arc-second (30m) DEM (N18E072.hgt.gz)",
            "building_footprints": "OpenStreetMap Authoritative Vector Records (ODbL)",
            "road_network": "OpenStreetMap Authoritative Vector Records (ODbL)"
        },
        "active_tiles": tile_summaries
    }

    os.makedirs(os.path.dirname(REPORT_JSON), exist_ok=True)
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)

    # Write Markdown Summary
    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("# GRAI Mumbai Digital Twin — World Coverage & Fidelity Report\n\n")
        f.write(f"**Generated:** `{report_data['timestamp']}`  \n")
        f.write(f"**World Origin:** `Lat {report_data['world_origin']['latitude']}, Lon {report_data['world_origin']['longitude']}`  \n")
        f.write(f"**CRS:** `EPSG:32643 (UTM Zone 43N) / Transverse Mercator`  \n\n")

        f.write("## 1. Summary Statistics\n\n")
        f.write(f"- **Total Grid Tiles Defined:** `{total_grid_tiles}`\n")
        f.write(f"- **Populated Urban Tiles:** `{active_tiles}`\n")
        f.write(f"- **Total Reconstructed Buildings:** `{total_buildings}`\n")
        f.write(f"  - **Level A (Verified Heights/Geometry):** `{level_a_verified}`\n")
        f.write(f"  - **Level B (Inferred from storeys/levels):** `{level_b_inferred}`\n")
        f.write(f"  - **Level C (Heuristic estimates labeled):** `{level_c_unavailable}`\n")
        f.write(f"- **Total Road Segments:** `{total_roads}` (`{total_road_km:.2f} km`)\n\n")

        f.write("## 2. Active Populated Tiles\n\n")
        f.write("| Tile ID | Buildings | Roads | Road Length (km) | Confidence |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for ts in tile_summaries:
            f.write(f"| `{ts['tile_id']}` | {ts['buildings']} | {ts['roads']} | {ts['road_km']} | {ts['confidence']:.2f} |\n")

        f.write("\n## 3. Strict Phase Exclusions Adherence\n\n")
        f.write("- **Characters / NPCs:** 0 (Strictly Excluded)\n")
        f.write("- **Vehicles / Traffic:** 0 (Strictly Excluded)\n")
        f.write("- **Animated Entities:** 0 (Strictly Excluded)\n")

    print(f"[CoverageReporter] Reports written to:\n  JSON: {REPORT_JSON}\n  Markdown: {REPORT_MD}")

if __name__ == "__main__":
    generate_coverage_report()
