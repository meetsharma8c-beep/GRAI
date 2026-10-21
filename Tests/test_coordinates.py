#!/usr/bin/env python3
"""
Unit tests for GRAI Geospatial Coordinate Reference Systems and Projections.
"""

import unittest
import pyproj
import math

class TestGeospatialCoordinates(unittest.TestCase):
    def setUp(self):
        self.origin_lat = 18.923
        self.origin_lon = 72.833
        self.fwd = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
        self.inv = pyproj.Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)
        self.x0, self.y0 = self.fwd.transform(self.origin_lon, self.origin_lat)

    def test_origin_maps_to_zero(self):
        ux, uy = self.fwd.transform(self.origin_lon, self.origin_lat)
        local_x = ux - self.x0
        local_y = uy - self.y0
        self.assertAlmostEqual(local_x, 0.0, places=3)
        self.assertAlmostEqual(local_y, 0.0, places=3)

    def test_inverse_projection_lossless(self):
        lon_back, lat_back = self.inv.transform(self.x0, self.y0)
        self.assertAlmostEqual(lon_back, self.origin_lon, places=6)
        self.assertAlmostEqual(lat_back, self.origin_lat, places=6)

    def test_known_landmarks_offsets(self):
        # Gateway of India (18.921984, 72.834654)
        gw_lat, gw_lon = 18.921984, 72.834654
        gw_x, gw_y = self.fwd.transform(gw_lon, gw_lat)
        local_gw_x = gw_x - self.x0
        local_gw_y = gw_y - self.y0

        # Gateway is east (~174m) and south (~-113m) of origin
        self.assertGreater(local_gw_x, 150.0)
        self.assertLess(local_gw_x, 200.0)
        self.assertLess(local_gw_y, -90.0)
        self.assertGreater(local_gw_y, -140.0)

    def test_unreal_scale_multiplier(self):
        scale_mult = 100.0 # 100cm per meter
        test_distance_m = 15.5
        unreal_units = test_distance_m * scale_mult
        self.assertEqual(unreal_units, 1550.0)

if __name__ == "__main__":
    unittest.main()
