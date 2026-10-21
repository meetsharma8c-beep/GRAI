#!/usr/bin/env python3
"""
GRAI Geospatial Source Downloader
Fetches authoritative geospatial data (OSM Overpass API, SRTM tiles, Open Data)
with caching, rate limiting, and integrity verification.
"""

import os
import sys
import time
import requests
from typing import Dict, Any, Optional

try:
    from source_registry import SourceRegistry
except ImportError:
    from Scripts.geospatial.source_registry import SourceRegistry

OVERPASS_SERVERS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

def fetch_osm_bbox(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    output_path: str,
    timeout: int = 120,
    force_download: bool = False
) -> bool:
    """
    Downloads OSM vector data for a bounding box using Overpass QL.
    Never re-downloads if file already exists with size > 1000 bytes unless forced.
    """
    if os.path.exists(output_path) and not force_download:
        size = os.path.getsize(output_path)
        if size > 1000:
            print(f"[Downloader] Cached file exists at {output_path} ({size} bytes). Skipping download.")
            return True

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    query = f"""
    [out:xml][timeout:{timeout}];
    (
      node({min_lat},{min_lon},{max_lat},{max_lon});
      way({min_lat},{min_lon},{max_lat},{max_lon});
      relation({min_lat},{min_lon},{max_lat},{max_lon});
    );
    (._;>;);
    out meta;
    """

    print(f"[Downloader] Querying Overpass API for bbox ({min_lat}, {min_lon}, {max_lat}, {max_lon})...")
    for endpoint in OVERPASS_SERVERS:
        try:
            resp = requests.post(
                endpoint,
                data={'data': query},
                headers={'User-Agent': 'GRAI-Mumbai-Digital-Twin/1.0 (Lead Geospatial Automation)'},
                timeout=timeout
            )
            if resp.status_code == 200 and b'<osm' in resp.content[:200]:
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                print(f"[Downloader] Successfully downloaded {len(resp.content)} bytes from {endpoint} to {output_path}")
                return True
            else:
                print(f"[Downloader] Server {endpoint} returned status {resp.status_code} or non-OSM content.")
        except Exception as e:
            print(f"[Downloader] Error connecting to {endpoint}: {e}")
            time.sleep(2)

    print("[Downloader] Failed to fetch data from all Overpass servers.")
    return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download geospatial sources for GRAI Mumbai Twin.")
    parser.add_argument("--bbox", nargs=4, type=float, metavar=("MIN_LAT", "MIN_LON", "MAX_LAT", "MAX_LON"),
                        help="Bounding box coordinates to download")
    parser.add_argument("--out", type=str, required=True, help="Output OSM file path")
    parser.add_argument("--force", action="store_true", help="Force re-download even if cached")
    args = parser.parse_args()

    if args.bbox:
        min_lat, min_lon, max_lat, max_lon = args.bbox
        fetch_osm_bbox(min_lat, min_lon, max_lat, max_lon, args.out, force_download=args.force)
