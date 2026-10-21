#!/usr/bin/env python3
"""
GRAI Building Footprint Validator
Validates polygon topology with Shapely, repairs self-intersections, calculates areas,
and reprojects geographic coordinates to local metric space (EPSG:32643 UTM Zone 43N).
"""

import os
import sys
import json
from typing import Dict, Any, List
import pyproj
from shapely.geometry import Polygon
from shapely.validation import make_valid

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_raw.json")
OUTPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/buildings_validated.json")

def get_projection_transformer(config: Dict[str, Any]):
    unreal_origin = config.get("geospatial", {}).get("unreal_world_origin", {})
    origin_lat = unreal_origin.get("latitude", 18.923)
    origin_lon = unreal_origin.get("longitude", 72.833)

    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
    x0, y0 = transformer.transform(origin_lon, origin_lat)
    return transformer, x0, y0

def validate_and_project_buildings():
    print("[BuildingValidator] Validating and projecting building footprints...")
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    transformer, x0, y0 = get_projection_transformer(config)

    if not os.path.exists(INPUT_FILE):
        from Scripts.buildings.ingest_buildings import run_ingestion
        run_ingestion()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_buildings = json.load(f)

    validated_buildings = []
    invalid_count = 0
    degenerate_count = 0

    for b in raw_buildings:
        coords_geo = b["coordinates"] # list of (lat, lon)
        if len(coords_geo) < 3:
            degenerate_count += 1
            continue

        # Convert to local metric coordinates (x, y)
        local_coords = []
        for lat, lon in coords_geo:
            ux, uy = transformer.transform(lon, lat)
            local_coords.append((ux - x0, uy - y0))

        # Close polygon if not closed
        if local_coords[0] != local_coords[-1]:
            local_coords.append(local_coords[0])

        poly = Polygon(local_coords)
        if not poly.is_valid:
            poly = make_valid(poly)
            invalid_count += 1

        # Check if geometry is polygon or multipolygon
        if poly.geom_type == 'Polygon':
            polys = [poly]
        elif poly.geom_type == 'MultiPolygon':
            polys = list(poly.geoms)
        else:
            degenerate_count += 1
            continue

        for idx, sub_poly in enumerate(polys):
            area = sub_poly.area
            if area < 3.0: # Skip micro-slivers less than 3 sqm
                degenerate_count += 1
                continue

            exterior_coords = list(sub_poly.exterior.coords)
            centroid = (sub_poly.centroid.x, sub_poly.centroid.y)

            # Geographic centroid
            c_lat = sum(c[0] for c in coords_geo) / len(coords_geo)
            c_lon = sum(c[1] for c in coords_geo) / len(coords_geo)

            record = {
                "asset_id": f"BLDG_{b['osm_id']}_{idx}" if idx > 0 else f"BLDG_{b['osm_id']}",
                "source_id": b["source_id"],
                "osm_id": b["osm_id"],
                "sub_index": idx,
                "tags": b["tags"],
                "area_sqm": round(area, 2),
                "perimeter_m": round(sub_poly.length, 2),
                "local_centroid": [round(centroid[0], 2), round(centroid[1], 2)],
                "geo_centroid": [round(c_lat, 6), round(c_lon, 6)],
                "local_polygon_vertices": [[round(x, 2), round(y, 2)] for x, y in exterior_coords],
                "geo_coordinates": coords_geo
            }
            validated_buildings.append(record)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(validated_buildings, f, indent=2)

    print(f"[BuildingValidator] Validated {len(validated_buildings)} polygons.")
    print(f"  Fixed self-intersections: {invalid_count}")
    print(f"  Discarded degenerates (<3 sqm or non-polygons): {degenerate_count}")
    print(f"  Output saved to: {OUTPUT_FILE}")
    return OUTPUT_FILE

if __name__ == "__main__":
    validate_and_project_buildings()
