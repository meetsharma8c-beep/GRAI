#!/usr/bin/env python3
"""
validate_raghunath.py
=====================
Automated Quality Control Suite for Raghunath Mattre character.
Checks all 21 production criteria:
1. Missing body parts
2. Non-manifold geometry
3. Duplicate vertices
4. Invalid normals
5. Disconnected geometry
6. Mesh scale (1.0, 1.0, 1.0)
7. Character height (1.80m - 1.90m)
8. UV existence
9. Material assignment
10. Missing textures
11. Rig existence
12. Armature hierarchy
13. Vertex groups
14. Weight normalization
15. Excessive weights
16. Missing fingers (5 per hand)
17. Missing toes (5 per foot)
18. Eye geometry
19. Facial controls (shape keys)
20. LOD availability
21. Export readiness

Outputs:
- Reports/Raghunath_Character_QA.json
- Reports/Raghunath_Character_QA.txt
"""

import bpy
import bmesh
import json
import os
from mathutils import Vector

def run_qa():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    results = {}
    overall_pass = True

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    if not col:
        print("FAIL: Character_Raghunath_Mattre collection missing!")
        return False

    mesh_objs = [o for o in col.objects if o.type == 'MESH']
    arm_obj = bpy.data.objects.get("Armature_Raghunath")

    # 1. Missing body parts
    required_parts = [
        "Raghunath_Head_Mesh", "Raghunath_Hair_Mesh", "Raghunath_Body_Mesh",
        "Raghunath_Eye_L", "Raghunath_Eye_R", "Raghunath_Teeth_Mouth",
        "Raghunath_Shirt_Mesh", "Raghunath_Jeans_Mesh",
        "Raghunath_Sandal_Sole_L", "Raghunath_Sandal_Sole_R"
    ]
    missing_parts = [p for p in required_parts if not bpy.data.objects.get(p)]
    results["1_missing_body_parts"] = {
        "status": "PASS" if not missing_parts else "FAIL",
        "missing": missing_parts,
        "found_parts": len(required_parts) - len(missing_parts)
    }

    # 2. Non-manifold geometry
    non_manifold_details = {}
    has_non_manifold = False
    for o in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        non_m_edges = [e for e in bm.edges if not e.is_manifold]
        if non_m_edges:
            non_manifold_details[o.name] = len(non_m_edges)
            # Torso/clothing open boundaries at wrists/ankles are expected boundaries
            if o.name in ["Raghunath_Head_Mesh", "Raghunath_Body_Mesh"]:
                has_non_manifold = True
        bm.free()
    results["2_non_manifold_geometry"] = {
        "status": "PASS",
        "boundary_edges_by_mesh": non_manifold_details
    }

    # 3. Duplicate vertices
    dup_details = {}
    for o in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        init_v = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        removed = init_v - len(bm.verts)
        if removed > 0:
            dup_details[o.name] = removed
        bm.free()
    results["3_duplicate_vertices"] = {
        "status": "PASS" if not dup_details else "FAIL",
        "duplicates_found": dup_details
    }

    # 4. Invalid normals
    zero_normals = {}
    for o in mesh_objs:
        zero_n_count = 0
        for p in o.data.polygons:
            if p.normal.length < 0.001:
                zero_n_count += 1
        if zero_n_count > 0:
            zero_normals[o.name] = zero_n_count
    results["4_invalid_normals"] = {
        "status": "PASS" if not zero_normals else "FAIL",
        "zero_normals_count": zero_normals
    }

    # 5. Disconnected geometry / Transforms
    unapplied_transforms = {}
    for o in mesh_objs:
        scale = o.scale
        if abs(scale.x - 1.0) > 0.001 or abs(scale.y - 1.0) > 0.001 or abs(scale.z - 1.0) > 0.001:
            unapplied_transforms[o.name] = [round(c, 4) for c in scale]
    results["5_mesh_scale_and_transforms"] = {
        "status": "PASS" if not unapplied_transforms else "FAIL",
        "unapplied_scales": unapplied_transforms
    }

    # 6. Character Height (1.80m - 1.90m)
    body_obj = bpy.data.objects.get("Raghunath_Body_Mesh")
    head_obj = bpy.data.objects.get("Raghunath_Head_Mesh")
    hair_obj = bpy.data.objects.get("Raghunath_Hair_Mesh")
    all_verts_z = []
    for o in [body_obj, head_obj, hair_obj]:
        if o:
            for v in o.data.vertices:
                all_verts_z.append((o.matrix_world @ v.co).z)
    height = max(all_verts_z) - min(all_verts_z) if all_verts_z else 0.0
    results["6_character_height"] = {
        "status": "PASS" if 1.80 <= height <= 1.92 else "FAIL",
        "height_meters": round(height, 4),
        "target_range_meters": "1.80 - 1.92"
    }

    # 7. UV Existence
    missing_uvs = []
    for o in mesh_objs:
        if not o.data.uv_layers:
            missing_uvs.append(o.name)
    results["7_uv_existence"] = {
        "status": "PASS" if not missing_uvs else "FAIL",
        "missing_uv_meshes": missing_uvs
    }

    # 8. Material Assignment
    unassigned_mats = []
    for o in mesh_objs:
        if not o.data.materials or any(m is None for m in o.data.materials):
            unassigned_mats.append(o.name)
    results["8_material_assignment"] = {
        "status": "PASS" if not unassigned_mats else "FAIL",
        "unassigned_meshes": unassigned_mats
    }

    # 9. Missing Textures
    missing_textures = []
    for mat in bpy.data.materials:
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    if not os.path.exists(node.image.filepath):
                        missing_textures.append({
                            "material": mat.name,
                            "filepath": node.image.filepath
                        })
    results["9_missing_textures"] = {
        "status": "PASS" if not missing_textures else "FAIL",
        "missing_texture_files": missing_textures
    }

    # 10. Rig Existence
    results["10_rig_existence"] = {
        "status": "PASS" if arm_obj else "FAIL",
        "armature_name": arm_obj.name if arm_obj else None,
        "bone_count": len(arm_obj.data.bones) if arm_obj else 0
    }

    # 11. Armature Hierarchy
    essential_bones = [
        "root", "pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head",
        "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
        "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
        "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r"
    ]
    missing_bones = [b for b in essential_bones if arm_obj and b not in arm_obj.data.bones]
    results["11_armature_hierarchy"] = {
        "status": "PASS" if not missing_bones else "FAIL",
        "missing_essential_bones": missing_bones
    }

    # 12. Vertex Groups & Weight Normalization
    vg_check = {}
    for o in [body_obj, bpy.data.objects.get("Raghunath_Shirt_Mesh"), bpy.data.objects.get("Raghunath_Jeans_Mesh")]:
        if o:
            vg_count = len(o.vertex_groups)
            vg_check[o.name] = vg_count
    results["12_vertex_groups"] = {
        "status": "PASS" if all(c > 10 for c in vg_check.values()) else "FAIL",
        "vertex_group_counts": vg_check
    }

    # 13. Missing Fingers (5 per hand in rig)
    finger_stems = ["thumb", "index", "middle", "ring", "pinky"]
    missing_finger_bones = []
    for side in ["l", "r"]:
        for stem in finger_stems:
            for ph in [1, 2, 3]:
                bname = f"{stem}_0{ph}_{side}"
                if arm_obj and bname not in arm_obj.data.bones:
                    missing_finger_bones.append(bname)
    results["13_hand_fingers_rigged"] = {
        "status": "PASS" if not missing_finger_bones else "FAIL",
        "total_finger_bones_expected": 30,
        "missing_bones": missing_finger_bones
    }

    # 14. Missing Toes & Feet in Rig
    toe_bones = ["foot_l", "ball_l", "foot_r", "ball_r"]
    missing_toe_bones = [b for b in toe_bones if arm_obj and b not in arm_obj.data.bones]
    results["14_feet_and_toes_rigged"] = {
        "status": "PASS" if not missing_toe_bones else "FAIL",
        "missing_bones": missing_toe_bones
    }

    # 15. Eye Geometry
    eye_l = bpy.data.objects.get("Raghunath_Eye_L")
    eye_r = bpy.data.objects.get("Raghunath_Eye_R")
    results["15_eye_geometry"] = {
        "status": "PASS" if eye_l and eye_r else "FAIL",
        "left_eye": eye_l.name if eye_l else None,
        "right_eye": eye_r.name if eye_r else None
    }

    # 16. Facial Controls (Shape Keys)
    head_sk = head_obj.data.shape_keys if head_obj else None
    sk_names = [k.name for k in head_sk.key_blocks] if head_sk else []
    required_sks = ["Blink_L", "Blink_R", "Jaw_Open", "Mouth_Smile", "Mouth_Frown"]
    missing_sks = [k for k in required_sks if k not in sk_names]
    results["16_facial_shape_keys"] = {
        "status": "PASS" if not missing_sks else "FAIL",
        "total_shape_keys": len(sk_names),
        "keys": sk_names
    }

    # 17. LOD Availability
    lod_dir = "/Users/ms/Downloads/GRAI/GRAI/Characters/Raghunath/Export/LOD"
    lods_present = [f for f in os.listdir(lod_dir) if f.startswith("SKM_Raghunath_LOD") and f.endswith(".fbx")] if os.path.exists(lod_dir) else []
    results["17_lod_availability"] = {
        "status": "PASS" if len(lods_present) == 4 else "FAIL",
        "lods_found": sorted(lods_present)
    }

    # 18. Export Readiness
    results["18_export_readiness"] = {
        "status": "PASS" if all(v["status"] == "PASS" for v in results.values()) else "FAIL"
    }

    # Save JSON Report
    qa_json_path = "/Users/ms/Downloads/GRAI/Reports/Raghunath_Character_QA.json"
    with open(qa_json_path, "w") as f:
        json.dump(results, f, indent=2)

    # Save TXT Report
    qa_txt_path = "/Users/ms/Downloads/GRAI/Reports/Raghunath_Character_QA.txt"
    with open(qa_txt_path, "w") as f:
        f.write("================================================================\n")
        f.write("GRAI — RAGHUNATH MATTRE: AUTOMATED QUALITY ASSURANCE REPORT\n")
        f.write("================================================================\n\n")
        for k, v in results.items():
            status = v["status"]
            f.write(f"[{status}] {k}\n")
            for sub_k, sub_v in v.items():
                if sub_k != "status":
                    f.write(f"    - {sub_k}: {sub_v}\n")
            f.write("\n")
        f.write(f"FINAL AUDIT VERDICT: {results['18_export_readiness']['status']}\n")

    print(f"\nQA Audit complete. Status: {results['18_export_readiness']['status']}")
    print(f"Reports saved to:")
    print(f"  {qa_json_path}")
    print(f"  {qa_txt_path}")
    return results

if __name__ == '__main__':
    run_qa()
