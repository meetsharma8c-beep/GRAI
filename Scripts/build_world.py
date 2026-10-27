#!/usr/bin/env python3
"""
GRAI — Grand Roads of India
Master World-Building Automation Pipeline
Orchestrates geospatial data validation, terrain modeling, building reconstruction,
road network generation, tile partitioning, Blender technical workflows, and Unreal Engine 5.8 assembly.
"""

import os
import sys
import json
import argparse
import subprocess
import time
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
DEFAULT_CONFIG = os.path.join(REPO_ROOT, "Config/grai_mumbai_world.json")

class WorldBuilderPipeline:
    def __init__(self, config_path: str = DEFAULT_CONFIG, dry_run: bool = False):
        self.config_path = config_path
        self.dry_run = dry_run
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def log_stage(self, stage_name: str, description: str):
        print("\n" + "=" * 75)
        print(f"STAGE: {stage_name.upper()} — {description}")
        print("=" * 75)

    def stage_inspect_project(self) -> bool:
        self.log_stage("inspect_project", "Inspecting Git, Unreal project, Blender, and environment")
        print(f"[inspect_project] Project Root: {REPO_ROOT}")
        print(f"[inspect_project] Config: {self.config_path}")
        u_proj = os.path.join(REPO_ROOT, self.config.get("unreal_engine", {}).get("project_file", "GRAI/GRAI.uproject"))
        print(f"[inspect_project] Unreal Project File: {u_proj} (Exists: {os.path.exists(u_proj)})")
        blender_bin = self.config.get("blender", {}).get("executable", "blender")
        print(f"[inspect_project] Blender Executable: {blender_bin} (Exists: {os.path.exists(blender_bin)})")

        raw_terrain = os.path.join(REPO_ROOT, "Data/raw/terrain/N18E072.hgt.gz")
        raw_osm = os.path.join(REPO_ROOT, "Data/raw/osm/mumbai_official_colaba.osm")
        print(f"[inspect_project] Raw SRTM DEM: {raw_terrain} (Exists: {os.path.exists(raw_terrain)})")
        print(f"[inspect_project] Raw OSM Vector: {raw_osm} (Exists: {os.path.exists(raw_osm)})")

        exclusions = self.config.get("project", {}).get("exclusions", [])
        print("[inspect_project] Active Strict Exclusions:")
        for exc in exclusions:
            print(f"  • {exc}")
        return True

    def stage_validate_sources(self) -> bool:
        self.log_stage("validate_sources", "Validating geospatial data sources and generating coverage report")
        if self.dry_run:
            print("[DRY RUN] Would execute Scripts/geospatial/validate_sources.py")
            return True
        from Scripts.geospatial.validate_sources import run_source_validation
        return run_source_validation()

    def stage_build_terrain(self) -> bool:
        self.log_stage("build_terrain", "Generating 3D physical elevation mesh from SRTM DEM")
        if self.dry_run:
            print("[DRY RUN] Would generate terrain mesh from SRTM")
            return True
        from Scripts.terrain.build_terrain_mesh import build_terrain_grid
        out_path = build_terrain_grid(step=50.0)
        return os.path.exists(out_path)

    def stage_build_buildings(self) -> bool:
        self.log_stage("build_buildings", "Ingesting footprints, validating geometry, assigning heights, and reconstructing 3D buildings")
        if self.dry_run:
            print("[DRY RUN] Would execute full buildings pipeline")
            return True
        from Scripts.buildings.ingest_buildings import run_ingestion
        from Scripts.buildings.validate_footprints import validate_and_project_buildings
        from Scripts.buildings.assign_height import assign_building_heights
        from Scripts.buildings.reconstruct_geometry import reconstruct_all_buildings
        from Scripts.buildings.export_buildings import export_buildings_to_obj

        run_ingestion()
        validate_and_project_buildings()
        assign_building_heights()
        reconstruct_all_buildings()
        out_obj = export_buildings_to_obj()
        return os.path.exists(out_obj)

    def stage_build_roads(self) -> bool:
        self.log_stage("build_roads", "Ingesting road linestrings, building graph, validating connectivity, and generating meshes")
        if self.dry_run:
            print("[DRY RUN] Would execute full roads pipeline")
            return True
        from Scripts.roads.ingest_roads import ingest_roads
        from Scripts.roads.build_road_graph import build_road_graph
        from Scripts.roads.validate_connectivity import validate_road_connectivity
        from Scripts.roads.generate_road_meshes import generate_all_road_meshes

        ingest_roads()
        build_road_graph()
        validate_road_connectivity()
        out_roads = generate_all_road_meshes()
        return os.path.exists(out_roads)

    def stage_process_textures(self) -> bool:
        self.log_stage("process_textures", "Cataloging textures, verifying power-of-two resolutions, and validating color spaces")
        if self.dry_run:
            print("[DRY RUN] Would validate texture library")
            return True
        from Scripts.textures.ingest_imagery import setup_default_texture_manifest
        from Scripts.textures.validate_textures import validate_texture_library

        setup_default_texture_manifest()
        rep = validate_texture_library()
        return rep["status"] == "PASS"

    def stage_build_tiles(self) -> bool:
        self.log_stage("build_tiles", "Creating tile grid, partitioning buildings and roads, and verifying adjacency seams")
        if self.dry_run:
            print("[DRY RUN] Would partition map into tiles and audit seams")
            return True
        from Scripts.tiles.create_tile_grid import create_tile_grid
        from Scripts.tiles.process_tile import process_all_tiles
        from Scripts.tiles.validate_tile import validate_all_tiles
        from Scripts.tiles.compare_adjacent_tiles import compare_tile_neighbors

        create_tile_grid()
        process_all_tiles()
        val = validate_all_tiles()
        adj = compare_tile_neighbors()
        return val["overall_status"] == "PASS" and adj["status"] in ["PASS", "WARNING"]

    def stage_export_blender_assets(self) -> bool:
        self.log_stage("export_blender_assets", "Running Blender background technical pipeline and mesh validation")
        blender_bin = self.config.get("blender", {}).get("executable", "/Users/ms/Desktop/Blender.app/Contents/MacOS/Blender")
        if not os.path.exists(blender_bin):
            print(f"[export_blender_assets] Warning: Blender executable not found at {blender_bin}. Skipping.")
            return False

        if self.dry_run:
            print(f"[DRY RUN] Would run {blender_bin} in background mode")
            return True

        cmd = [
            blender_bin,
            "-b",
            "--python-expr",
            (
                "import sys; sys.path.append('Scripts/blender'); "
                "import material_pipeline, building_pipeline, mesh_validation; "
                "material_pipeline.setup_material_library(); "
                "building_pipeline.import_buildings_to_blender('Data/processed/buildings_geometry.json', max_buildings=100); "
                "mesh_validation.validate_blender_scene_meshes();"
            )
        ]
        res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(res.stderr)
        return res.returncode == 0

    def stage_assemble_unreal(self) -> bool:
        self.log_stage("assemble_unreal", "Generating Unreal Engine 5.8 assembly script and verifying world partition layers")
        if self.dry_run:
            print("[DRY RUN] Would generate Unreal assembly script")
            return True
        from Scripts.unreal.assemble_unreal import generate_unreal_assembly_script
        out_script = generate_unreal_assembly_script()
        return os.path.exists(out_script)

    def stage_validate_world(self) -> bool:
        self.log_stage("validate_world", "Running comprehensive world-wide validation suite")
        if self.dry_run:
            print("[DRY RUN] Would run validation tests")
            return True
        res = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "Tests"], cwd=REPO_ROOT)
        return res.returncode == 0

    def stage_build_report(self) -> bool:
        self.log_stage("build_report", "Compiling final world fidelity, coverage reports, tile dashboard, and backlog")
        if self.dry_run:
            print("[DRY RUN] Would compile final reports")
            return True
        from Scripts.tiles.generate_coverage_report import generate_coverage_report
        from Scripts.validation.generate_phase_f_deliverables import generate_performance_and_coverage_audit
        generate_coverage_report()
        generate_performance_and_coverage_audit()
        return True

    def run_stage(self, stage_name: str) -> bool:
        stage_map = {
            "inspect_project": self.stage_inspect_project,
            "validate_sources": self.stage_validate_sources,
            "build_terrain": self.stage_build_terrain,
            "build_buildings": self.stage_build_buildings,
            "build_roads": self.stage_build_roads,
            "process_textures": self.stage_process_textures,
            "build_tiles": self.stage_build_tiles,
            "export_blender_assets": self.stage_export_blender_assets,
            "assemble_unreal": self.stage_assemble_unreal,
            "validate_world": self.stage_validate_world,
            "build_report": self.stage_build_report
        }

        if stage_name not in stage_map:
            raise ValueError(f"Unknown stage: '{stage_name}'. Supported stages: {list(stage_map.keys())}")

        start_time = time.time()
        success = stage_map[stage_name]()
        elapsed = time.time() - start_time

        if success:
            print(f"\n[SUCCESS] STAGE [{stage_name}] COMPLETED SUCCESSFULLY in {elapsed:.2f}s")
        else:
            print(f"\n[FAILED] STAGE [{stage_name}] FAILED in {elapsed:.2f}s")
        return success

    def run_all(self) -> bool:
        stages = [
            "inspect_project",
            "validate_sources",
            "build_terrain",
            "build_buildings",
            "build_roads",
            "process_textures",
            "build_tiles",
            "export_blender_assets",
            "assemble_unreal",
            "validate_world",
            "build_report"
        ]
        print("\n" + "=" * 75)
        print("STARTING FULL END-TO-END GRAI DIGITAL TWIN PIPELINE")
        print("=" * 75)
        overall_start = time.time()

        for s in stages:
            ok = self.run_stage(s)
            if not ok:
                print(f"\n[FAILED] PIPELINE HALTED AT STAGE: {s}")
                return False

        total_elapsed = time.time() - overall_start
        print("\n" + "=" * 75)
        print(f"[SUCCESS] ALL PIPELINE STAGES COMPLETED SUCCESSFULLY in {total_elapsed:.2f}s!")
        print("=" * 75)
        return True

def main():
    parser = argparse.ArgumentParser(description="Master orchestration pipeline for GRAI Mumbai Digital Twin.")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG, help="Path to grai_mumbai_world.json")
    parser.add_argument("--stage", type=str, choices=[
        "inspect_project", "validate_sources", "build_terrain", "build_buildings",
        "build_roads", "process_textures", "build_tiles", "export_blender_assets",
        "assemble_unreal", "validate_world", "build_report", "all"
    ], default="all", help="Pipeline stage to execute")
    parser.add_argument("--dry-run", action="store_true", help="Simulate stages without writing files")

    args = parser.parse_args()
    builder = WorldBuilderPipeline(config_path=args.config, dry_run=args.dry_run)

    if args.stage == "all":
        success = builder.run_all()
    else:
        success = builder.run_stage(args.stage)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
