#!/usr/bin/env python3
"""
GRAI Geospatial Source Registry
Tracks and catalogs all geospatial source datasets, licenses, CRS, spatial extents,
provenance, and redistribution permissions for the Mumbai Digital Twin.
"""

import os
import sys
import json
import hashlib
import time
from typing import Dict, Any, Optional

MANIFEST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Data/source_manifest.json"))

class SourceRegistry:
    def __init__(self, manifest_path: str = MANIFEST_PATH):
        self.manifest_path = manifest_path
        self.sources: Dict[str, Any] = {}
        self.load()

    def load(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                self.sources = json.load(f)
        else:
            self.sources = {
                "metadata": {
                    "project": "GRAI — Grand Roads of India",
                    "registry_version": "1.0.0",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "target": "Mumbai Digital Twin"
                },
                "sources": {}
            }

    def save(self):
        os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
        self.sources["metadata"]["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.sources, f, indent=2)
        print(f"[SourceRegistry] Saved manifest to {self.manifest_path} ({len(self.sources['sources'])} sources)")

    def calculate_sha256(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return "FILE_NOT_FOUND"
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def register_source(
        self,
        source_id: str,
        name: str,
        provider: str,
        endpoint_or_path: str,
        license_name: str,
        attribution: str,
        crs: str,
        coverage_bbox: Dict[str, float],
        dataset_date: str,
        resolution: Optional[str] = None,
        redistribution_permitted: bool = True,
        data_quality_limitations: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        sha256: Optional[str] = None
    ):
        file_path = os.path.abspath(endpoint_or_path) if os.path.exists(endpoint_or_path) else endpoint_or_path
        if os.path.exists(file_path):
            actual_size = os.path.getsize(file_path)
            actual_hash = self.calculate_sha256(file_path)
        else:
            actual_size = file_size_bytes or 0
            actual_hash = sha256 or "PENDING"

        record = {
            "source_id": source_id,
            "name": name,
            "provider": provider,
            "path_or_endpoint": file_path,
            "file_size_bytes": actual_size,
            "sha256": actual_hash,
            "acquisition_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "dataset_date": dataset_date,
            "coordinate_reference_system": crs,
            "spatial_resolution": resolution or "Varies",
            "geographic_coverage": coverage_bbox,
            "license": license_name,
            "attribution": attribution,
            "redistribution_permitted": redistribution_permitted,
            "data_quality_limitations": data_quality_limitations or "None documented",
            "processing_history": [
                {
                    "action": "registered",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            ]
        }
        self.sources["sources"][source_id] = record
        self.save()
        return record

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        return self.sources["sources"].get(source_id)

    def list_sources(self) -> Dict[str, Any]:
        return self.sources["sources"]

def register_default_sources():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    registry = SourceRegistry()

    # 1. SRTM Elevation Tile N18E072
    srtm_path = os.path.join(repo_root, "Data/raw/terrain/N18E072.hgt.gz")
    registry.register_source(
        source_id="srtm_n18e072",
        name="NASA/USGS SRTM 1-Arc-Second Global (N18E072)",
        provider="NASA JPL / USGS",
        endpoint_or_path=srtm_path,
        license_name="Public Domain (NASA Open Data Policy)",
        attribution="NASA SRTM mission courtesy USGS / JPL",
        crs="EPSG:4326 (WGS 84 Horizontal), EGM96 Geoid (Vertical MSL)",
        coverage_bbox={"min_lat": 18.0, "max_lat": 19.0, "min_lon": 72.0, "max_lon": 73.0},
        dataset_date="2000-02 (Reprocessed 2014)",
        resolution="1 arc-second (~30 meters)",
        redistribution_permitted=True,
        data_quality_limitations="Coarse 30m resolution; does not capture micro-topography, seawalls, or elevated bridges; upper latitude edge at 19.00."
    )

    # 2. OSM Colaba Official Extract
    osm_official = os.path.join(repo_root, "Data/raw/osm/mumbai_official_colaba.osm")
    registry.register_source(
        source_id="osm_mumbai_official_colaba",
        name="OpenStreetMap Apollo Bunder & Colaba Heritage Precinct",
        provider="OpenStreetMap Contributors",
        endpoint_or_path=osm_official,
        license_name="ODbL (Open Database License)",
        attribution="© OpenStreetMap contributors",
        crs="EPSG:4326 (WGS 84)",
        coverage_bbox={"min_lat": 18.918, "max_lat": 18.928, "min_lon": 72.828, "max_lon": 72.838},
        dataset_date="2026-07-08",
        resolution="Vector survey-level geometry",
        redistribution_permitted=True,
        data_quality_limitations="278 verified building footprints and 251 highway segments; building heights are largely missing and require explicit inference."
    )

    # 3. OSM Greater Mumbai Peninsula
    osm_peninsula = os.path.join(repo_root, "Data/raw/osm/mumbai_colaba.osm")
    registry.register_source(
        source_id="osm_mumbai_colaba_peninsula",
        name="OpenStreetMap Mumbai Peninsula Network",
        provider="OpenStreetMap Contributors",
        endpoint_or_path=osm_peninsula,
        license_name="ODbL (Open Database License)",
        attribution="© OpenStreetMap contributors",
        crs="EPSG:4326 (WGS 84)",
        coverage_bbox={"min_lat": 18.895, "max_lat": 19.055, "min_lon": 72.800, "max_lon": 72.875},
        dataset_date="2026-07-15",
        resolution="Vector geometry (1855 highways, 141 landmark buildings)",
        redistribution_permitted=True,
        data_quality_limitations="Extensive highway graph; selective building coverage; non-building areas require secondary datasets."
    )

    # 4. OSM Dharavi Informal Settlement Sector
    osm_dharavi = os.path.join(repo_root, "Data/raw/osm/mumbai_dharavi_sample.osm")
    if os.path.exists(osm_dharavi):
        registry.register_source(
            source_id="osm_mumbai_dharavi",
            name="OpenStreetMap Dharavi Mapped Settlement Structure",
            provider="OpenStreetMap Contributors",
            endpoint_or_path=osm_dharavi,
            license_name="ODbL (Open Database License)",
            attribution="© OpenStreetMap contributors",
            crs="EPSG:4326 (WGS 84)",
            coverage_bbox={"min_lat": 19.038, "max_lat": 19.048, "min_lon": 72.848, "max_lon": 72.858},
            dataset_date="2026-10-14",
            resolution="High-density vector footprints and alleyway network (1392 buildings, 3068 highways)",
            redistribution_permitted=True,
            data_quality_limitations="Dense mapped informal settlement fabric; ground verified footprints; narrow passageways."
        )

    # 5. OSM Worli & Dadar Arterial Sector
    osm_worli = os.path.join(repo_root, "Data/raw/osm/mumbai_worli_dadar.osm")
    if os.path.exists(osm_worli):
        registry.register_source(
            source_id="osm_mumbai_worli_dadar",
            name="OpenStreetMap Worli & Dadar Urban Sector",
            provider="OpenStreetMap Contributors",
            endpoint_or_path=osm_worli,
            license_name="ODbL (Open Database License)",
            attribution="© OpenStreetMap contributors",
            crs="EPSG:4326 (WGS 84)",
            coverage_bbox={"min_lat": 18.990, "max_lat": 19.025, "min_lon": 72.810, "max_lon": 72.840},
            dataset_date="2026-10-14",
            resolution="Vector geometry (5741 buildings, 8378 highways)",
            redistribution_permitted=True,
            data_quality_limitations="High density urban blocks, mill lands redevelopment, flyovers, and sea-facing high-rises."
        )

    # 6. OSM Bandra & Sea Link Coastal Sector
    osm_bandra = os.path.join(repo_root, "Data/raw/osm/mumbai_bandra_sealink.osm")
    if os.path.exists(osm_bandra):
        registry.register_source(
            source_id="osm_mumbai_bandra_sealink",
            name="OpenStreetMap Bandra & Bandra-Worli Sea Link Coastal Sector",
            provider="OpenStreetMap Contributors",
            endpoint_or_path=osm_bandra,
            license_name="ODbL (Open Database License)",
            attribution="© OpenStreetMap contributors",
            crs="EPSG:4326 (WGS 84)",
            coverage_bbox={"min_lat": 19.035, "max_lat": 19.065, "min_lon": 72.815, "max_lon": 72.840},
            dataset_date="2026-10-14",
            resolution="Vector geometry (2820 buildings, 6756 highways)",
            redistribution_permitted=True,
            data_quality_limitations="BWSL expressway geometry, toll plaza, Bandra West heritage villages and coastal promontory."
        )

    print("[SourceRegistry] All Mumbai metropolitan sources successfully registered.")

if __name__ == "__main__":
    register_default_sources()
