#!/usr/bin/env python3
"""
GRAI Building Ingestion Pipeline
Parses real OpenStreetMap XML data, extracts building footprints and all metadata tags,
preserving source IDs and spatial provenance.
"""

import os
import sys
import json
import xml.parsers.expat
from typing import Dict, Any, List, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUTPUT_DIR = os.path.join(REPO_ROOT, "Data/processed")

class BuildingIngestor:
    def __init__(self):
        self.nodes: Dict[int, tuple] = {}
        self.buildings: List[Dict[str, Any]] = []

    def parse_osm(self, osm_path: str) -> List[Dict[str, Any]]:
        print(f"[BuildingIngestor] Parsing building footprints from {osm_path}...")
        self.nodes.clear()
        self.buildings.clear()

        in_way = False
        in_relation = False
        current_way_id = None
        current_way_nodes = []
        current_tags = {}

        p = xml.parsers.expat.ParserCreate()

        def start_element(name, attrs):
            nonlocal in_way, in_relation, current_way_id, current_way_nodes, current_tags
            if name == 'node':
                nid = int(attrs['id'])
                lat = float(attrs['lat'])
                lon = float(attrs['lon'])
                self.nodes[nid] = (lat, lon)
            elif name == 'way':
                in_way = True
                current_way_id = int(attrs['id'])
                current_way_nodes = []
                current_tags = {}
            elif name == 'nd' and in_way:
                current_way_nodes.append(int(attrs['ref']))
            elif name == 'tag' and in_way:
                current_tags[attrs['k']] = attrs['v']

        def end_element(name):
            nonlocal in_way, in_relation, current_way_id, current_way_nodes, current_tags
            if name == 'way':
                in_way = False
                if 'building' in current_tags:
                    coords = []
                    for nid in current_way_nodes:
                        if nid in self.nodes:
                            coords.append(self.nodes[nid])

                    if len(coords) >= 3:
                        self.buildings.append({
                            "source_id": f"osm_way_{current_way_id}",
                            "osm_id": current_way_id,
                            "type": "way",
                            "tags": current_tags,
                            "coordinates": coords
                        })

        p.StartElementHandler = start_element
        p.EndElementHandler = end_element

        with open(osm_path, 'rb') as f:
            p.ParseFile(f)

        print(f"[BuildingIngestor] Extracted {len(self.buildings)} raw building footprints from {len(self.nodes)} nodes.")
        return self.buildings

def run_ingestion(source_files: Optional[List[str]] = None) -> str:
    if not source_files:
        osm_dir = os.path.join(REPO_ROOT, "Data/raw/osm")
        source_files = [os.path.join(osm_dir, f) for f in os.listdir(osm_dir) if f.endswith(".osm")]

    ingestor = BuildingIngestor()
    all_buildings = {}

    for path in source_files:
        if os.path.exists(path):
            bldgs = ingestor.parse_osm(path)
            for b in bldgs:
                sid = b["source_id"]
                if sid not in all_buildings:
                    all_buildings[sid] = b
                else:
                    all_buildings[sid]["tags"].update(b["tags"])

    buildings_list = list(all_buildings.values())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = os.path.join(OUTPUT_DIR, "buildings_raw.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(buildings_list, f, indent=2)

    print(f"[BuildingIngestor] Saved {len(buildings_list)} deduplicated building footprints to {out_file}")
    return out_file

if __name__ == "__main__":
    run_ingestion()
