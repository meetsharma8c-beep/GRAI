#!/usr/bin/env python3
"""
Unit tests for GRAI Building, Road, Tile, and Source Validation pipelines.
"""

import os
import json
import unittest
from shapely.geometry import Polygon

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestPipelineValidation(unittest.TestCase):
    def test_source_manifest_exists_and_valid(self):
        manifest_path = os.path.join(REPO_ROOT, "Data/source_manifest.json")
        self.assertTrue(os.path.exists(manifest_path), "Data/source_manifest.json must exist")
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        self.assertIn("sources", manifest)
        self.assertGreaterEqual(len(manifest["sources"]), 3)

    def test_building_footprint_topology(self):
        validated_path = os.path.join(REPO_ROOT, "Data/processed/buildings_validated.json")
        self.assertTrue(os.path.exists(validated_path), "buildings_validated.json must exist")
        with open(validated_path, 'r', encoding='utf-8') as f:
            buildings = json.load(f)
        self.assertGreater(len(buildings), 0)

        for b in buildings[:30]:
            coords = b["local_polygon_vertices"]
            self.assertGreaterEqual(len(coords), 3)
            poly = Polygon(coords)
            self.assertTrue(poly.is_valid, f"Polygon for {b['asset_id']} must be valid")
            self.assertGreaterEqual(poly.area, 3.0, "Building area must be >= 3 sqm")

    def test_height_attribution_uncertainty(self):
        attributed_path = os.path.join(REPO_ROOT, "Data/processed/buildings_attributed.json")
        self.assertTrue(os.path.exists(attributed_path), "buildings_attributed.json must exist")
        with open(attributed_path, 'r', encoding='utf-8') as f:
            buildings = json.load(f)

        tiers_found = set()
        for b in buildings:
            tier = b.get("confidence_tier")
            self.assertIn(tier, ["LEVEL_A_VERIFIED", "LEVEL_B_INFERRED", "LEVEL_C_UNAVAILABLE"])
            tiers_found.add(tier)
            self.assertIn("height_source", b)
            self.assertGreater(b["height_m"], 0.0)

        self.assertIn("LEVEL_A_VERIFIED", tiers_found)
        self.assertIn("LEVEL_B_INFERRED", tiers_found)

    def test_road_network_connectivity(self):
        road_graph_path = os.path.join(REPO_ROOT, "Data/processed/road_graph.json")
        self.assertTrue(os.path.exists(road_graph_path), "road_graph.json must exist")
        with open(road_graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)

        self.assertIn("edges", graph)
        self.assertGreater(len(graph["edges"]), 100)
        self.assertGreater(len(graph["junction_node_ids"]), 10)

    def test_tile_grid_determinism(self):
        grid_path = os.path.join(REPO_ROOT, "Data/processed/tile_grid.json")
        self.assertTrue(os.path.exists(grid_path), "tile_grid.json must exist")
        with open(grid_path, 'r', encoding='utf-8') as f:
            grid = json.load(f)

        tiles = grid["tiles"]
        self.assertGreater(len(tiles), 50)
        self.assertIn("TILE_E+000_N+000", tiles, "Center origin tile must exist")

if __name__ == "__main__":
    unittest.main()
