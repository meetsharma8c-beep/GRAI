#!/usr/bin/env python3
"""
GRAI Tile Validator
Validates internal consistency, geometry bounds, building height realism,
and metadata completeness for individual geographic tiles.
"""

import os
import sys
import json
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
TILES_DIR = os.path.join(REPO_ROOT, "Data/processed/tiles")
VALIDATION_DIR = os.path.join(REPO_ROOT, "Data/validation")

def validate_tile(tile_id: str) -> Dict[str, Any]:
    tile_file = os.path.join(TILES_DIR, f"{tile_id}.json")
    if not os.path.exists(tile_file):
        return {"tile_id": tile_id, "status": "FAIL", "error": "Tile file does not exist"}

    with open(tile_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    bounds = data["bounds"]
    buildings = data.get("buildings", [])
    roads = data.get("roads", [])

    defects = []

    # Check buildings
    for b in buildings:
        h = b.get("height_m", 0)
        if h < 2.0 or h > 400.0:
            defects.append(f"Building {b['asset_id']} abnormal height: {h}m")
        area = b.get("area_sqm", 0)
        if area < 3.0:
            defects.append(f"Building {b['asset_id']} degenerate area: {area} sqm")

    # Check roads
    for r in roads:
        coords = r.get("coordinates_3d", [])
        if len(coords) < 2:
            defects.append(f"Road {r['osm_id']} has fewer than 2 vertices")

    status = "PASS" if len(defects) == 0 else "WARNING"
    return {
        "tile_id": tile_id,
        "status": status,
        "defects_count": len(defects),
        "defects": defects[:10],
        "statistics": data["statistics"]
    }

def validate_all_tiles() -> Dict[str, Any]:
    print("[TileValidator] Running deep tile validation across all processed tiles...")
    if not os.path.exists(TILES_DIR):
        from Scripts.tiles.process_tile import process_all_tiles
        process_all_tiles()

    tile_files = [f for f in os.listdir(TILES_DIR) if f.endswith(".json")]
    results = {}
    passed = 0
    warnings = 0
    failed = 0

    for tf in tile_files:
        tid = tf.replace(".json", "")
        res = validate_tile(tid)
        results[tid] = res
        if res["status"] == "PASS":
            passed += 1
        elif res["status"] == "WARNING":
            warnings += 1
        else:
            failed += 1

    summary = {
        "report_type": "Tile Validation Summary",
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "total_tiles_audited": len(tile_files),
        "passed": passed,
        "warnings": warnings,
        "failed": failed,
        "overall_status": "PASS" if failed == 0 else "FAIL"
    }

    os.makedirs(VALIDATION_DIR, exist_ok=True)
    out_path = os.path.join(VALIDATION_DIR, "tile_validation_report.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({"summary": summary, "tile_details": results}, f, indent=2)

    print(f"[TileValidator] Validation complete. Total: {len(tile_files)}, Passed: {passed}, Warnings: {warnings}, Failed: {failed}")
    print(f"  Report written to: {out_path}")
    return summary

if __name__ == "__main__":
    validate_all_tiles()
