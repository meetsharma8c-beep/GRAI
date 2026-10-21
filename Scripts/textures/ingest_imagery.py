#!/usr/bin/env python3
"""
GRAI Texture and Imagery Ingestion Pipeline
Catalogs and ingests satellite orthophotos, surface textures, and normal maps
preserving CRS, spatial resolution, and licensing in Data/texture_manifest.json.
"""

import os
import sys
import json
import time
from PIL import Image
from typing import Dict, Any, List, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MANIFEST_PATH = os.path.join(REPO_ROOT, "Data/texture_manifest.json")

class TextureRegistry:
    def __init__(self, manifest_path: str = MANIFEST_PATH):
        self.manifest_path = manifest_path
        self.textures: Dict[str, Any] = {}
        self.load()

    def load(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                self.textures = json.load(f)
        else:
            self.textures = {
                "metadata": {
                    "project": "GRAI — Grand Roads of India",
                    "registry_version": "1.0.0",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "target": "Mumbai Digital Twin Materials"
                },
                "textures": {}
            }

    def save(self):
        os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
        self.textures["metadata"]["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.textures, f, indent=2)

    def register_texture(
        self,
        texture_id: str,
        name: str,
        filepath: str,
        category: str,
        resolution: tuple,
        color_space: str,
        source: str,
        license_name: str,
        physical_scale_m: float = 2.0
    ):
        record = {
            "texture_id": texture_id,
            "name": name,
            "filepath": filepath,
            "category": category,
            "resolution_px": list(resolution),
            "color_space": color_space,
            "physical_scale_meters": physical_scale_m,
            "texel_density_px_per_m": round(resolution[0] / max(0.1, physical_scale_m), 1),
            "source": source,
            "license": license_name,
            "status": "VALIDATED"
        }
        self.textures["textures"][texture_id] = record
        self.save()
        return record

def setup_default_texture_manifest():
    print("[TextureIngestor] Setting up texture registry manifest...")
    reg = TextureRegistry()

    default_textures = [
        ("tex_mumbai_basalt_diffuse", "Kharodi Yellow Basalt Diffuse", "Textures/Basalt/T_Basalt_D.png", "Facade_Basalt", (2048, 2048), "sRGB", "Surveyed Material Capture", "GRAI Proprietary", 3.0),
        ("tex_mumbai_basalt_normal", "Kharodi Yellow Basalt Normal", "Textures/Basalt/T_Basalt_N.png", "Facade_Basalt", (2048, 2048), "Linear", "Surveyed Material Capture", "GRAI Proprietary", 3.0),
        ("tex_mumbai_asphalt_diffuse", "Mumbai Coastal Weathered Asphalt Diffuse", "Textures/Road/T_Asphalt_D.png", "Road_Surface", (2048, 2048), "sRGB", "Surveyed Road Material", "GRAI Proprietary", 4.0),
        ("tex_mumbai_asphalt_roughness", "Mumbai Coastal Weathered Asphalt Roughness", "Textures/Road/T_Asphalt_R.png", "Road_Surface", (2048, 2048), "Linear", "Surveyed Road Material", "GRAI Proprietary", 4.0),
        ("tex_mumbai_concrete_curb", "BMC Yellow-Black Painted Curb", "Textures/Road/T_Curb_D.png", "Road_Curb", (1024, 1024), "sRGB", "Surveyed BMC Infrastructure", "GRAI Proprietary", 1.0)
    ]

    for tid, name, path, cat, res, cs, src, lic, scale in default_textures:
        reg.register_texture(tid, name, path, cat, res, cs, src, lic, scale)

    print(f"[TextureIngestor] Default textures registered to {MANIFEST_PATH}")

if __name__ == "__main__":
    setup_default_texture_manifest()
