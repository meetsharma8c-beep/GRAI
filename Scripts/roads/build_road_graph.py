#!/usr/bin/env python3
"""
GRAI Road Graph Builder
Constructs a topologically connected graph of the Mumbai road network,
computing segment widths, elevations, junctions, and bridge grade-separations.
"""

import os
import sys
import json
import math
from typing import Dict, Any, List
from collections import defaultdict

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/roads_raw.json")
OUTPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/road_graph.json")
SRTM_PATH = os.path.join(REPO_ROOT, "Data/raw/terrain/N18E072.hgt.gz")

try:
    from Scripts.buildings.assign_height import TerrainSampler
except ImportError:
    sys.path.append(os.path.join(REPO_ROOT, "Scripts/buildings"))
    from assign_height import TerrainSampler

def build_road_graph():
    print("[RoadGraphBuilder] Building topological road graph...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    width_table = config.get("road_rules", {}).get("widths_by_highway_type", {})
    terrain = TerrainSampler(SRTM_PATH)

    if not os.path.exists(INPUT_FILE):
        from Scripts.roads.ingest_roads import ingest_roads
        ingest_roads()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        roads = json.load(f)

    node_connectivity = defaultdict(list)
    graph_edges = []
    junctions = set()

    # Pass 1: Map node connectivity to find intersections
    for r in roads:
        nids = r["node_ids"]
        for nid in nids:
            node_connectivity[nid].append(r["osm_id"])

    for nid, ways in node_connectivity.items():
        if len(ways) > 1:
            junctions.add(nid)

    # Pass 2: Build enriched edges
    for r in roads:
        tags = r.get("tags", {})
        h_type = r.get("highway", "residential")
        local_coords = r["local_coordinates"]
        geo_coords = r["geo_coordinates"]

        # 1. Determine Width
        width_m = None
        width_source = "estimated"
        if "width" in tags:
            try:
                width_m = float(tags["width"].replace("m", "").strip())
                width_source = "osm_explicit_width"
            except ValueError:
                pass

        if width_m is None and "lanes" in tags:
            try:
                lanes = float(tags["lanes"].split(";")[0])
                width_m = round(lanes * 3.5, 2)
                width_source = f"osm_lanes_inferred:{tags['lanes']}"
            except ValueError:
                pass

        if width_m is None:
            width_m = width_table.get(h_type, 6.5)
            width_source = f"default_highway_type:{h_type}"

        # 2. Bridge & Grade Separation
        is_bridge = tags.get("bridge") in ["yes", "viaduct"]
        is_tunnel = tags.get("tunnel") in ["yes", "culvert"]
        layer = int(tags.get("layer", "0"))

        elev_offset = 0.0
        if is_bridge or layer > 0:
            elev_offset = 5.5 * max(1, layer)
        elif is_tunnel or layer < 0:
            elev_offset = -4.0 * max(1, abs(layer))

        # 3. Compute 3D Coordinates with Terrain Elevation
        coords_3d = []
        total_length = 0.0
        for i, (lx, ly) in enumerate(local_coords):
            lat, lon = geo_coords[i]
            base_z = terrain.sample_elevation(lat, lon)
            final_z = round(base_z + elev_offset + 0.05, 2) # +5cm above terrain
            coords_3d.append([lx, ly, final_z])

            if i > 0:
                prev_x, prev_y = local_coords[i - 1]
                total_length += math.hypot(lx - prev_x, ly - prev_y)

        edge_record = {
            "source_id": r["source_id"],
            "osm_id": r["osm_id"],
            "name": r["name"],
            "highway": h_type,
            "width_m": width_m,
            "width_source": width_source,
            "length_m": round(total_length, 2),
            "is_bridge": is_bridge,
            "is_tunnel": is_tunnel,
            "layer": layer,
            "node_ids": r["node_ids"],
            "coordinates_3d": coords_3d,
            "has_junction": any(nid in junctions for nid in r["node_ids"])
        }
        graph_edges.append(edge_record)

    graph_data = {
        "metadata": {
            "total_edges": len(graph_edges),
            "total_nodes": len(node_connectivity),
            "total_junctions": len(junctions),
            "total_road_network_km": round(sum(e["length_m"] for e in graph_edges) / 1000.0, 2)
        },
        "junction_node_ids": list(junctions),
        "edges": graph_edges
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, indent=2)

    print(f"[RoadGraphBuilder] Road graph built successfully:")
    print(f"  Total Edges: {len(graph_edges)}")
    print(f"  Total Junctions: {len(junctions)}")
    print(f"  Network Length: {graph_data['metadata']['total_road_network_km']} km")
    print(f"  Saved to: {OUTPUT_FILE}")
    return OUTPUT_FILE

if __name__ == "__main__":
    build_road_graph()
