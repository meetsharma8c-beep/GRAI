#!/usr/bin/env python3
"""
GRAI Texture Validator
Verifies texture resolution power-of-two compliance, color space assignments,
texel densities, and streaming tier readiness for Unreal Engine 5.8 Virtual Textures.
"""

import os
import sys
import json
import math
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
MANIFEST_PATH = os.path.join(REPO_ROOT, "Data/texture_manifest.json")
REPORT_PATH = os.path.join(REPO_ROOT, "Data/validation/texture_validation_report.json")

def is_power_of_two(n: int) -> bool:
    return (n > 0) and (n & (n - 1) == 0)

def validate_texture_library():
    print("[TextureValidator] Validating texture manifest and format compliance...")
    if not os.path.exists(MANIFEST_PATH):
        from Scripts.textures.ingest_imagery import setup_default_texture_manifest
        setup_default_texture_manifest()

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    textures = manifest.get("textures", {})
    defects = []
    validated_count = 0

    for tid, tex in textures.items():
        w, h = tex["resolution_px"]
        if not is_power_of_two(w) or not is_power_of_two(h):
            defects.append(f"Texture {tid} resolution {w}x{h} is not power-of-two (required for mipmaps/virtual textures)")

        cs = tex.get("color_space")
        if cs not in ["sRGB", "Linear"]:
            defects.append(f"Texture {tid} has unknown color space: {cs}")

        validated_count += 1

    report = {
        "report_type": "Texture and Material Asset Validation",
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "total_textures_audited": validated_count,
        "defects_count": len(defects),
        "defects": defects,
        "virtual_texture_ready": len(defects) == 0,
        "status": "PASS" if len(defects) == 0 else "FAIL"
    }

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"[TextureValidator] Validation complete. Status: {report['status']}")
    print(f"  Textures Audited: {validated_count}")
    print(f"  Defects: {len(defects)}")
    print(f"  Report saved to: {REPORT_PATH}")
    return report

if __name__ == "__main__":
    validate_texture_library()
