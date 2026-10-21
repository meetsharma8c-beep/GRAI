#!/usr/bin/env python3
"""
inspect_raghunath_character.py
Technical inspection of Raghunath Mattre character in Blender scene.
"""
import bpy
import json
import os
from mathutils import Vector

def inspect_character():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    if bpy.data.filepath != blend_path and os.path.exists(blend_path):
        bpy.ops.wm.open_mainfile(filepath=blend_path)

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    char_objs = list(col.objects) if col else []

    report = {
        "collection_name": col.name if col else None,
        "total_objects": len(char_objs),
        "objects": [],
        "materials": [],
        "armatures": [],
        "overall_stats": {
            "total_vertices": 0,
            "total_polygons": 0,
            "min_coord": [float('inf')]*3,
            "max_coord": [float('-inf')]*3
        }
    }

    # Inspect objects
    for obj in sorted(char_objs, key=lambda x: x.name):
        obj_info = {
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "location": [round(c, 4) for c in obj.location],
            "world_matrix_translation": [round(c, 4) for c in obj.matrix_world.translation],
            "materials": [slot.material.name for slot in obj.material_slots if slot.material],
            "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers]
        }
        if obj.type == 'MESH':
            mesh = obj.data
            obj_info["vertices"] = len(mesh.vertices)
            obj_info["polygons"] = len(mesh.polygons)
            obj_info["uv_layers"] = [uv.name for uv in mesh.uv_layers]
            obj_info["vertex_groups"] = [vg.name for vg in obj.vertex_groups]
            
            report["overall_stats"]["total_vertices"] += len(mesh.vertices)
            report["overall_stats"]["total_polygons"] += len(mesh.polygons)
            
            # Bounding box in world coordinates
            bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            for pt in bbox:
                for i in range(3):
                    if pt[i] < report["overall_stats"]["min_coord"][i]:
                        report["overall_stats"]["min_coord"][i] = pt[i]
                    if pt[i] > report["overall_stats"]["max_coord"][i]:
                        report["overall_stats"]["max_coord"][i] = pt[i]
        
        report["objects"].append(obj_info)

    # Compute total dimensions
    min_c = report["overall_stats"]["min_coord"]
    max_c = report["overall_stats"]["max_coord"]
    if min_c[0] != float('inf'):
        report["overall_stats"]["dimensions"] = {
            "width_x_meters": round(max_c[0] - min_c[0], 4),
            "depth_y_meters": round(max_c[1] - min_c[1], 4),
            "height_z_meters": round(max_c[2] - min_c[2], 4),
            "world_bbox_min": [round(c, 4) for c in min_c],
            "world_bbox_max": [round(c, 4) for c in max_c]
        }

    # Inspect materials & textures
    mat_names = set()
    for o in char_objs:
        if o.type == 'MESH':
            for slot in o.material_slots:
                if slot.material:
                    mat_names.add(slot.material.name)
    
    for mname in sorted(mat_names):
        mat = bpy.data.materials.get(mname)
        mat_info = {
            "name": mname,
            "use_nodes": mat.use_nodes,
            "textures": []
        }
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    mat_info["textures"].append({
                        "node_name": node.name,
                        "image_name": node.image.name,
                        "image_filepath": node.image.filepath,
                        "image_size": list(node.image.size) if hasattr(node.image, 'size') else []
                    })
        report["materials"].append(mat_info)

    # Inspect armatures across scene
    for arm in bpy.data.armatures:
        report["armatures"].append({
            "name": arm.name,
            "bones_count": len(arm.bones),
            "bones": [b.name for b in arm.bones[:15]]
        })

    out_json = "/Users/ms/Downloads/GRAI/Reports/Raghunath_Scene_Inspection.json"
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Inspection written to {out_json}")
    return report

if __name__ == '__main__':
    inspect_character()
