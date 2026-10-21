#!/usr/bin/env python3
"""
GRAI Tile Grid Generator
Creates a deterministic geographic tile grid across the Mumbai world extent,
defining tile boundaries, unique spatial IDs, and initial provenance trackers.
"""

import os
import sys
import json
import math
import pyproj
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
OUTPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/tile_grid.json")

def create_tile_grid(
    x_min: float = -5000.0,
    x_max: float = 5000.0,
    y_min: float = -3500.0,
    y_max: float = 16000.0
) -> str:
    print(f"[TileGridGenerator] Generating tile grid ({x_min} to {x_max}m E, {y_min} to {y_max}m N)...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    tiling_cfg = config.get("tiling", {})
    tile_size = tiling_cfg.get("tile_size_meters", 500.0)
    overlap = tiling_cfg.get("tile_overlap_meters", 10.0)

    unreal_origin = config.get("geospatial", {}).get("unreal_world_origin", {})
    origin_lat = unreal_origin.get("latitude", 18.923)
    origin_lon = unreal_origin.get("longitude", 72.833)

    fwd_trans = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
    inv_trans = pyproj.Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)
    x0, y0 = fwd_trans.transform(origin_lon, origin_lat)

    cols = range(int(math.floor(x_min / tile_size)), int(math.ceil(x_max / tile_size)))
    rows = range(int(math.floor(y_min / tile_size)), int(math.ceil(y_max / tile_size)))

    tiles: Dict[str, Dict[str, Any]] = {}

    for c in cols:
        for r in rows:
            tile_id = f"TILE_E{c:+04d}_N{r:+04d}"
            local_min_x = c * tile_size
            local_max_x = (c + 1) * tile_size
            local_min_y = r * tile_size
            local_max_y = (r + 1) * tile_size

            # Geographic bounds
            min_lon, min_lat = inv_trans.transform(local_min_x + x0, local_min_y + y0)
            max_lon, max_lat = inv_trans.transform(local_max_x + x0, local_max_y + y0)

            tiles[tile_id] = {
                "tile_id": tile_id,
                "grid_col": c,
                "grid_row": r,
                "tile_size_m": tile_size,
                "overlap_m": overlap,
                "local_bounds": {
                    "min_x": local_min_x,
                    "max_x": local_max_x,
                    "min_y": local_min_y,
                    "max_y": local_max_y
                },
                "geographic_bounds": {
                    "min_lat": round(min_lat, 6),
                    "max_lat": round(max_lat, 6),
                    "min_lon": round(min_lon, 6),
                    "max_lon": round(max_lon, 6)
                },
                "neighbors": {
                    "north": f"TILE_E{c:+04d}_N{r+1:+04d}",
                    "south": f"TILE_E{c:+04d}_N{r-1:+04d}",
                    "east": f"TILE_E{c+1:+04d}_N{r:+04d}",
                    "west": f"TILE_E{c-1:+04d}_N{r:+04d}"
                },
                "status": "UNPROCESSED",
                "validation_status": "PENDING"
            }

    grid_data = {
        "metadata": {
            "total_tiles": len(tiles),
            "tile_size_meters": tile_size,
            "span_x_meters": x_max - x_min,
            "span_y_meters": y_max - y_min
        },
        "tiles": tiles
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(grid_data, f, indent=2)

    print(f"[TileGridGenerator] Created {len(tiles)} grid tiles in {OUTPUT_FILE}")
    return OUTPUT_FILE

if __name__ == "__main__":
    create_tile_grid()
