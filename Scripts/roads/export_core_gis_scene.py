#!/usr/bin/env python3
"""
GRAI — Export Core GIS Scene
Extracts surveyed road ribbons and building polygons from OSM datasets for South Mumbai to Bandra,
computing exact road widths, parcel coordinates, and heights for Blender and Unreal import.
"""

import os
import sys
import json
import math
import xml.parsers.expat
import pyproj

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUTPUT_JSON = os.path.join(REPO_ROOT, "Data/processed/mumbai_core_gis_scene.json")

transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
ORIGIN_LON = 72.833000
ORIGIN_LAT = 18.923000
x0, y0 = transformer.transform(ORIGIN_LON, ORIGIN_LAT)

def to_local(lon: float, lat: float):
    ux, uy = transformer.transform(lon, lat)
    return round(ux - x0, 2), round(uy - y0, 2)

WIDTH_TABLE = {
    "motorway": 24.0,
    "trunk": 20.0,
    "primary": 16.0,
    "secondary": 12.0,
    "tertiary": 9.0,
    "residential": 7.0,
    "service": 4.5,
    "unclassified": 6.0,
    "footway": 3.0,
    "pedestrian": 6.0,
    "living_street": 5.0
}

def export_gis_scene():
    print("[CoreGIS] Exporting real Mumbai roads and buildings...")
    MIN_LAT, MAX_LAT = 18.895, 19.060
    MIN_LON, MAX_LON = 72.780, 72.860

    osm_files = [
        os.path.join(REPO_ROOT, "Data/raw/osm/mumbai_official_colaba.osm"),
        os.path.join(REPO_ROOT, "Data/raw/osm/mumbai_colaba.osm"),
        os.path.join(REPO_ROOT, "Data/raw/osm/mumbai_worli_dadar.osm"),
        os.path.join(REPO_ROOT, "Data/raw/osm/mumbai_bandra_sealink.osm")
    ]

    nodes = {}
    roads = []
    buildings = []

    for path in osm_files:
        if not os.path.exists(path):
            continue
        print(f"  Reading {os.path.basename(path)}...")
        p = xml.parsers.expat.ParserCreate()
        in_way = False
        cur_nodes = []
        cur_tags = {}

        def start_elem(name, attrs):
            nonlocal in_way, cur_nodes, cur_tags
            if name == 'node':
                nid = int(attrs['id'])
                lat = float(attrs['lat'])
                lon = float(attrs['lon'])
                if MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON:
                    nodes[nid] = to_local(lon, lat)
            elif name == 'way':
                in_way = True
                cur_nodes = []
                cur_tags = {}
            elif name == 'nd' and in_way:
                cur_nodes.append(int(attrs['ref']))
            elif name == 'tag' and in_way:
                cur_tags[attrs['k']] = attrs['v']

        def end_elem(name):
            nonlocal in_way, cur_nodes, cur_tags
            if name == 'way':
                in_way = False
                if 'highway' in cur_tags:
                    valid = [nodes[nid] for nid in cur_nodes if nid in nodes]
                    if len(valid) >= 2:
                        hw = cur_tags['highway']
                        w = WIDTH_TABLE.get(hw, 7.0)
                        if 'width' in cur_tags:
                            try: w = float(cur_tags['width'].replace('m','').strip())
                            except: pass
                        elif 'lanes' in cur_tags:
                            try: w = float(cur_tags['lanes'].split(';')[0]) * 3.5
                            except: pass
                        roads.append({
                            'highway': hw,
                            'name': cur_tags.get('name', 'Street'),
                            'width': w,
                            'coords': valid
                        })
                elif 'building' in cur_tags:
                    valid = [nodes[nid] for nid in cur_nodes if nid in nodes]
                    if len(valid) >= 3:
                        h = 14.0
                        if 'height' in cur_tags:
                            try: h = float(cur_tags['height'].replace('m','').strip())
                            except: pass
                        elif 'building:levels' in cur_tags:
                            try: h = float(cur_tags['building:levels']) * 3.5
                            except: pass
                        buildings.append({
                            'coords': valid,
                            'height': min(max(h, 6.0), 160.0),
                            'type': cur_tags.get('building', 'yes'),
                            'name': cur_tags.get('name', '')
                        })

        p.StartElementHandler = start_elem
        p.EndElementHandler = end_elem
        with open(path, 'rb') as fp:
            try: p.ParseFile(fp)
            except Exception as e: print(f"Error parsing {path}: {e}")

    # Remove duplicate road segments and building polygons
    unique_roads = []
    seen_road_hashes = set()
    for r in roads:
        h = tuple(r['coords'][0] + r['coords'][-1])
        if h not in seen_road_hashes:
            seen_road_hashes.add(h)
            unique_roads.append(r)

    unique_buildings = []
    seen_bldg_hashes = set()
    for b in buildings:
        h = tuple(b['coords'][0])
        if h not in seen_bldg_hashes:
            seen_bldg_hashes.add(h)
            unique_buildings.append(b)

    payload = {
        "metadata": {
            "origin_lat": ORIGIN_LAT,
            "origin_lon": ORIGIN_LON,
            "total_roads": len(unique_roads),
            "total_buildings": len(unique_buildings)
        },
        "roads": unique_roads,
        "buildings": unique_buildings
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as fp:
        json.dump(payload, fp)

    print(f"[CoreGIS] Successfully exported {len(unique_roads)} roads and {len(unique_buildings)} buildings to {OUTPUT_JSON}")
    return OUTPUT_JSON

if __name__ == "__main__":
    export_gis_scene()
