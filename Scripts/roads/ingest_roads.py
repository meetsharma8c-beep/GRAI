#!/usr/bin/env python3
"""
GRAI Road Ingestion Pipeline
Extracts topologically valid road geometry and attributes from OpenStreetMap datasets,
preserving curvature, road classifications, lanes, bridge/tunnel markers, and provenance.
"""

import os
import sys
import json
import xml.parsers.expat
from typing import Dict, Any, List, Optional
import pyproj

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
OUTPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/roads_raw.json")

def get_projection_transformer(config: Dict[str, Any]):
    unreal_origin = config.get("geospatial", {}).get("unreal_world_origin", {})
    origin_lat = unreal_origin.get("latitude", 18.923)
    origin_lon = unreal_origin.get("longitude", 72.833)
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
    x0, y0 = transformer.transform(origin_lon, origin_lat)
    return transformer, x0, y0

def ingest_roads(source_files: Optional[List[str]] = None) -> str:
    print("[RoadIngestor] Ingesting road networks from OSM datasets...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    transformer, x0, y0 = get_projection_transformer(config)

    if not source_files:
        osm_dir = os.path.join(REPO_ROOT, "Data/raw/osm")
        source_files = [os.path.join(osm_dir, f) for f in os.listdir(osm_dir) if f.endswith(".osm")]

    nodes: Dict[int, tuple] = {}
    roads: Dict[int, Dict[str, Any]] = {}

    for path in source_files:
        if not os.path.exists(path):
            continue
        print(f"  Parsing roads from {path}...")
        p = xml.parsers.expat.ParserCreate()
        in_way = False
        current_way_id = None
        current_way_nodes = []
        current_tags = {}

        def start_elem(name, attrs):
            nonlocal in_way, current_way_id, current_way_nodes, current_tags
            if name == 'node':
                nid = int(attrs['id'])
                lat = float(attrs['lat'])
                lon = float(attrs['lon'])
                nodes[nid] = (lat, lon)
            elif name == 'way':
                in_way = True
                current_way_id = int(attrs['id'])
                current_way_nodes = []
                current_tags = {}
            elif name == 'nd' and in_way:
                current_way_nodes.append(int(attrs['ref']))
            elif name == 'tag' and in_way:
                current_tags[attrs['k']] = attrs['v']

        def end_elem(name):
            nonlocal in_way, current_way_id, current_way_nodes, current_tags
            if name == 'way':
                in_way = False
                if 'highway' in current_tags:
                    geo_coords = []
                    local_coords = []
                    valid_node_ids = []
                    for nid in current_way_nodes:
                        if nid in nodes:
                            lat, lon = nodes[nid]
                            geo_coords.append((lat, lon))
                            ux, uy = transformer.transform(lon, lat)
                            local_coords.append([round(ux - x0, 2), round(uy - y0, 2)])
                            valid_node_ids.append(nid)

                    if len(local_coords) >= 2:
                        roads[current_way_id] = {
                            "source_id": f"osm_road_{current_way_id}",
                            "osm_id": current_way_id,
                            "highway": current_tags["highway"],
                            "name": current_tags.get("name", "Unnamed Road"),
                            "tags": current_tags,
                            "node_ids": valid_node_ids,
                            "geo_coordinates": geo_coords,
                            "local_coordinates": local_coords
                        }

        p.StartElementHandler = start_elem
        p.EndElementHandler = end_elem

        with open(path, 'rb') as f:
            p.ParseFile(f)

    road_list = list(roads.values())
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(road_list, f, indent=2)

    print(f"[RoadIngestor] Ingested {len(road_list)} deduplicated road segments into {OUTPUT_FILE}")
    return OUTPUT_FILE

if __name__ == "__main__":
    ingest_roads()
