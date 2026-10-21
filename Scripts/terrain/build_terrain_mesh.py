#!/usr/bin/env python3
"""
GRAI Terrain Elevation Pipeline
Generates physical 3D elevation terrain meshes from NASA/USGS SRTM 1-arc-second (30m) DEM data.
Losslessly projected to metric coordinates relative to the Unreal world origin.
"""

import os
import sys
import json
import gzip
import struct
import math
import pyproj
from typing import Dict, Any, List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_PATH = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")
SRTM_PATH = os.path.join(REPO_ROOT, "Data/raw/terrain/N18E072.hgt.gz")
OUTPUT_DIR = os.path.join(REPO_ROOT, "Data/processed/exported_terrain")

class SRTMProcessor:
    def __init__(self, srtm_gz_path: str):
        self.srtm_path = srtm_gz_path
        with gzip.open(self.srtm_path, 'rb') as f:
            self.raw_dem = f.read()

    def get_elevation_bilinear(self, lat: float, lon: float) -> float:
        if lat < 18.0 or lat > 19.0 or lon < 72.0 or lon > 73.0:
            return 0.0

        row_f = (19.0 - lat) * 3600.0
        col_f = (lon - 72.0) * 3600.0

        r0 = max(0, min(3600, int(math.floor(row_f))))
        r1 = min(3600, r0 + 1)
        c0 = max(0, min(3600, int(math.floor(col_f))))
        c1 = min(3600, c0 + 1)

        fr = row_f - r0
        fc = col_f - c0

        def sample(r, c):
            offset = (r * 3601 + c) * 2
            v = struct.unpack('>h', self.raw_dem[offset:offset+2])[0]
            return float(v) if v != -32768 else 0.0

        v00 = sample(r0, c0)
        v01 = sample(r0, c1)
        v10 = sample(r1, c0)
        v11 = sample(r1, c1)

        elev = (1.0 - fr) * ((1.0 - fc) * v00 + fc * v01) + fr * ((1.0 - fc) * v10 + fc * v11)
        if elev <= 0.0:
            return -0.25 # Sea level depression
        return round(elev, 2)

def build_terrain_grid(
    x_min: float = -5000.0,
    x_max: float = 5000.0,
    y_min: float = -3500.0,
    y_max: float = 16000.0,
    step: float = 50.0,
    output_filename: str = "mumbai_terrain_mesh.obj"
) -> str:
    print(f"[TerrainBuilder] Generating terrain grid ({x_min} to {x_max}m E, {y_min} to {y_max}m N, step={step}m)...")
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    unreal_origin = config.get("geospatial", {}).get("unreal_world_origin", {})
    origin_lat = unreal_origin.get("latitude", 18.923)
    origin_lon = unreal_origin.get("longitude", 72.833)

    # Inverse transformer (UTM 43N to WGS84 Lat/Lon)
    fwd_trans = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True)
    inv_trans = pyproj.Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True)
    x0, y0 = fwd_trans.transform(origin_lon, origin_lat)

    srtm = SRTMProcessor(SRTM_PATH)

    xs = [x_min + i * step for i in range(int((x_max - x_min) / step) + 1)]
    ys = [y_min + j * step for j in range(int((y_max - y_min) / step) + 1)]
    nx, ny = len(xs), len(ys)

    print(f"  Grid dimensions: {nx} x {ny} = {nx * ny} vertices ({nx-1}x{ny-1} quads)")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# GRAI Mumbai Digital Twin — SRTM 30M Terrain Mesh OBJ Export\n")
        f.write(f"# Grid Size: {nx} x {ny}\n")
        f.write(f"# Step: {step}m\n\n")
        f.write("o TERRAIN_SRTM_30M\n")
        f.write("usemtl MAT_Terrain_PBR\n")

        # Write vertices
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                # Back to UTM, then Lon/Lat
                utm_x = x + x0
                utm_y = y + y0
                lon, lat = inv_trans.transform(utm_x, utm_y)
                z = srtm.get_elevation_bilinear(lat, lon)
                f.write(f"v {x:.2f} {y:.2f} {z:.2f}\n")

        # Write quad faces
        for j in range(ny - 1):
            row_offset = j * nx
            next_row_offset = (j + 1) * nx
            for i in range(nx - 1):
                v0 = row_offset + i + 1
                v1 = row_offset + (i + 1) + 1
                v2 = next_row_offset + (i + 1) + 1
                v3 = next_row_offset + i + 1
                f.write(f"f {v0} {v1} {v2} {v3}\n")

    print(f"[TerrainBuilder] Successfully exported terrain mesh to {out_path} ({os.path.getsize(out_path)} bytes).")
    return out_path

if __name__ == "__main__":
    build_terrain_grid()
