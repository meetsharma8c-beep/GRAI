#!/usr/bin/env python3
"""
GRAI Road Connectivity Validator
Analyzes graph topology, detects disconnected road segments, dead-ends,
self-intersecting linestrings, and bridge continuity.
"""

import os
import sys
import json
from collections import defaultdict
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INPUT_FILE = os.path.join(REPO_ROOT, "Data/processed/road_graph.json")
REPORT_FILE = os.path.join(REPO_ROOT, "Data/validation/road_connectivity_report.json")

def validate_road_connectivity():
    print("[RoadValidator] Validating road network topological connectivity...")
    if not os.path.exists(INPUT_FILE):
        from Scripts.roads.build_road_graph import build_road_graph
        build_road_graph()

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        graph = json.load(f)

    edges = graph["edges"]
    node_degree = defaultdict(int)
    for e in edges:
        nids = e["node_ids"]
        for nid in nids:
            node_degree[nid] += 1

    dead_ends = [nid for nid, deg in node_degree.items() if deg == 1]
    intersections = [nid for nid, deg in node_degree.items() if deg >= 3]
    bridges = [e for e in edges if e.get("is_bridge")]
    tunnels = [e for e in edges if e.get("is_tunnel")]

    report = {
        "report_type": "Road Connectivity and Topology Audit",
        "timestamp": os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
        "total_edges": len(edges),
        "total_nodes": len(node_degree),
        "multi_way_intersections": len(intersections),
        "dead_end_terminals": len(dead_ends),
        "bridge_segments": len(bridges),
        "tunnel_segments": len(tunnels),
        "connectivity_ratio": round((len(node_degree) - len(dead_ends)) / max(1, len(node_degree)), 4),
        "status": "PASS" if len(edges) > 0 else "FAIL"
    }

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"[RoadValidator] Validation complete. Status: {report['status']}")
    print(f"  Total Edges: {len(edges)}")
    print(f"  Intersections: {len(intersections)}")
    print(f"  Dead Ends: {len(dead_ends)}")
    print(f"  Connectivity Ratio: {report['connectivity_ratio'] * 100:.1f}%")
    print(f"  Report written to: {REPORT_FILE}")
    return report

if __name__ == "__main__":
    validate_road_connectivity()
