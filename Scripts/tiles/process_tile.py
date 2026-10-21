#!/usr/bin/env python3
"""
GRAI Tile Processor
Spatially indexes, partitions, and clips building footprints and roads into individual tiles,
producing self-contained, reproducible tile packages with full provenance.
"""

import os
import sys
import json
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
GRID_FILE = os.path.join(REPO_ROOT, "Data/processed/tile_grid.json")
BUILDINGS_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_attributed.json")
ROADS_FILE = os.path.join(REPO_ROOT, "Data/processed/road_graph.json")
TILES_DIR = os.path.join(REPO_ROOT, "Data/processed/tiles")

def point_in_bounds(x: float, y: float, bounds: Dict[str, float], buffer_m: float = 0.0) -> bool:
    return (bounds["min_x"] - buffer_m <= x <= bounds["max_x"] + buffer_m and
            bounds["min_y"] - buffer_m <= y <= bounds["max_y"] + buffer_m)

def process_single_tile(tile_id: str, grid_data: Dict[str, Any], buildings: List[Dict[str, Any]], roads: List[Dict[str, Any]]) -> Dict[str, Any]:
    tile_info = grid_data["tiles"][tile_id]
    bounds = tile_info["local_bounds"]
    overlap = tile_info.get("overlap_m", 10.0)

    # 1. Gather overlapping buildings
    tile_buildings = []
    level_a_cnt = 0
    level_b_cnt = 0
    level_c_cnt = 0

    for b in buildings:
        cx, cy = b["local_centroid"]
        if point_in_bounds(cx, cy, bounds, buffer_m=overlap):
            tile_buildings.append(b)
            tier = b.get("confidence_tier")
            if tier == "LEVEL_A_VERIFIED":
                level_a_cnt += 1
            elif tier == "LEVEL_B_INFERRED":
                level_b_cnt += 1
            else:
                level_c_cnt += 1

    # 2. Gather overlapping roads
    tile_roads = []
    road_length = 0.0
    for r in roads:
        coords = r["coordinates_3d"]
        if any(point_in_bounds(x, y, bounds, buffer_m=overlap) for x, y, z in coords):
            tile_roads.append(r)
            road_length += r.get("length_m", 0.0)

    # 3. Compute tile confidence
    total_bldgs = len(tile_buildings)
    if total_bldgs > 0:
        confidence = (level_a_cnt * 1.0 + level_b_cnt * 0.7 + level_c_cnt * 0.3) / total_bldgs
    else:
        confidence = 0.5 if len(tile_roads) > 0 else 0.0

    tile_package = {
        "tile_id": tile_id,
        "bounds": bounds,
        "geographic_bounds": tile_info["geographic_bounds"],
        "statistics": {
            "total_buildings": total_bldgs,
            "level_a_verified": level_a_cnt,
            "level_b_inferred": level_b_cnt,
            "level_c_unavailable": level_c_cnt,
            "total_roads": len(tile_roads),
            "road_length_m": round(road_length, 2),
            "confidence_score": round(confidence, 3)
        },
        "sources_used": ["srtm_n18e072", "osm_mumbai_official_colaba"],
        "status": "PROCESSED",
        "buildings": tile_buildings,
        "roads": tile_roads
    }

    os.makedirs(TILES_DIR, exist_ok=True)
    out_file = os.path.join(TILES_DIR, f"{tile_id}.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(tile_package, f, indent=2)

    return tile_package

def process_all_tiles():
    print("[TileProcessor] Spatially partitioning map data into discrete geographic tiles...")
    if not os.path.exists(GRID_FILE):
        from Scripts.tiles.create_tile_grid import create_tile_grid
        create_tile_grid()

    with open(GRID_FILE, 'r', encoding='utf-8') as f:
        grid_data = json.load(f)

    if not os.path.exists(BUILDINGS_FILE):
        from Scripts.buildings.assign_height import assign_building_heights
        assign_building_heights()

    with open(BUILDINGS_FILE, 'r', encoding='utf-8') as f:
        buildings = json.load(f)

    if not os.path.exists(ROADS_FILE):
        from Scripts.roads.build_road_graph import build_road_graph
        build_road_graph()

    with open(ROADS_FILE, 'r', encoding='utf-8') as f:
        roads_graph = json.load(f)
    roads = roads_graph.get("edges", [])

    processed_count = 0
    non_empty_count = 0

    for tile_id in grid_data["tiles"]:
        pkg = process_single_tile(tile_id, grid_data, buildings, roads)
        processed_count += 1
        stats = pkg["statistics"]
        if stats["total_buildings"] > 0 or stats["total_roads"] > 0:
            non_empty_count += 1
            print(f"  Tile {tile_id}: {stats['total_buildings']} buildings, {stats['total_roads']} roads (Conf: {stats['confidence_score']})")

    print(f"[TileProcessor] Partitioned {processed_count} tiles. {non_empty_count} active populated tiles saved to {TILES_DIR}")

if __name__ == "__main__":
    process_all_tiles()
