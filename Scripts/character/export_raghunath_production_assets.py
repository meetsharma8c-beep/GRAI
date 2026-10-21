#!/usr/bin/env python3
"""
export_raghunath_production_assets.py
=====================================
Automated asset packager and UE5 FBX exporter for Raghunath Mattre.
Exports:
- Master Hero Skeletal Mesh: SKM_Raghunath_Mattre.fbx
- Modular Parts: SKM_Raghunath_Head.fbx, SKM_Raghunath_Body.fbx, SKM_Raghunath_Clothing.fbx
- Textures: authoritative face texture to Export/Textures/
- Material Documentation: Export/Materials/Materials_Summary.json
- Rig Documentation: Export/Rig/Rig_Hierarchy.json
"""

import bpy
import os
import json
import shutil

def export_assets():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    base_export_dir = "/Users/ms/Downloads/GRAI/GRAI/Characters/Raghunath/Export"
    mesh_export_dir = os.path.join(base_export_dir, "Meshes")
    texture_export_dir = os.path.join(base_export_dir, "Textures")
    material_export_dir = os.path.join(base_export_dir, "Materials")
    rig_export_dir = os.path.join(base_export_dir, "Rig")
    ue_content_dir = "/Users/ms/Downloads/GRAI/GRAI/Content/Characters/Raghunath"

    for d in [mesh_export_dir, texture_export_dir, material_export_dir, rig_export_dir, ue_content_dir]:
        os.makedirs(d, exist_ok=True)

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    if not col:
        print("ERROR: Character_Raghunath_Mattre collection not found.")
        return

    arm_obj = bpy.data.objects.get("Armature_Raghunath")
    if not arm_obj:
        print("ERROR: Armature_Raghunath not found.")
        return

    character_mesh_objs = [o for o in col.objects if o.type == 'MESH']
    print(f"Found {len(character_mesh_objs)} character meshes and armature {arm_obj.name}.")

    # 1. Export Master Hero Skeletal Mesh (All character meshes + Armature)
    print("\n--- Exporting Master Hero Skeletal Mesh ---")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    for o in character_mesh_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    master_fbx_path = os.path.join(mesh_export_dir, "SKM_Raghunath_Mattre.fbx")
    content_fbx_path = os.path.join(ue_content_dir, "SKM_Raghunath_Mattre.fbx")

    bpy.ops.export_scene.fbx(
        filepath=master_fbx_path,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        bake_anim=False
    )
    print(f"Master hero exported to {master_fbx_path} ({os.path.getsize(master_fbx_path) / (1024*1024):.2f} MB)")

    shutil.copy2(master_fbx_path, content_fbx_path)
    print(f"Synced master hero to UE Content directory: {content_fbx_path}")

    # 2. Export Modular Head
    print("\n--- Exporting Modular Head Mesh ---")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    head_parts = ["Raghunath_Head_Mesh", "Raghunath_Hair_Mesh", "Raghunath_Eye_L", "Raghunath_Eye_R", "Raghunath_Teeth_Mouth"]
    for name in head_parts:
        o = bpy.data.objects.get(name)
        if o: o.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    head_fbx_path = os.path.join(mesh_export_dir, "SKM_Raghunath_Head.fbx")
    bpy.ops.export_scene.fbx(
        filepath=head_fbx_path,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False
    )
    print(f"Modular Head exported to {head_fbx_path} ({os.path.getsize(head_fbx_path) / (1024*1024):.2f} MB)")

    # 3. Export Modular Body
    print("\n--- Exporting Modular Body Mesh ---")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    body_obj = bpy.data.objects.get("Raghunath_Body_Mesh")
    if body_obj: body_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    body_fbx_path = os.path.join(mesh_export_dir, "SKM_Raghunath_Body.fbx")
    bpy.ops.export_scene.fbx(
        filepath=body_fbx_path,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False
    )
    print(f"Modular Body exported to {body_fbx_path} ({os.path.getsize(body_fbx_path) / (1024*1024):.2f} MB)")

    # 4. Export Modular Clothing & Accessories
    print("\n--- Exporting Modular Clothing Mesh ---")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    clothing_parts = [
        "Raghunath_Shirt_Mesh", "Raghunath_Shirt_Pocket", "Raghunath_Jeans_Mesh",
        "Raghunath_Sandal_Sole_L", "Raghunath_Sandal_Strap_L", "Raghunath_Sandal_ToeRing_L",
        "Raghunath_Sandal_Sole_R", "Raghunath_Sandal_Strap_R", "Raghunath_Sandal_ToeRing_R",
        "Raghunath_Necklace_Cord", "Raghunath_Pendant"
    ]
    for name in clothing_parts:
        o = bpy.data.objects.get(name)
        if o: o.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    clothing_fbx_path = os.path.join(mesh_export_dir, "SKM_Raghunath_Clothing.fbx")
    bpy.ops.export_scene.fbx(
        filepath=clothing_fbx_path,
        use_selection=True,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False
    )
    print(f"Modular Clothing exported to {clothing_fbx_path} ({os.path.getsize(clothing_fbx_path) / (1024*1024):.2f} MB)")

    # 5. Copy Textures
    print("\n--- Copying Authoritative Textures ---")
    face_src = "/Users/ms/Downloads/GRAI/renders/raghunath_face_hires.jpg"
    face_dst = os.path.join(texture_export_dir, "T_Raghunath_Face_D.jpg")
    if os.path.exists(face_src):
        shutil.copy2(face_src, face_dst)
        print(f"Copied {face_src} -> {face_dst}")

    # 6. Material Documentation
    print("\n--- Documenting Materials ---")
    materials_info = {}
    for o in character_mesh_objs:
        for m in o.data.materials:
            if m and m.name not in materials_info:
                mat_data = {
                    "assigned_meshes": [obj.name for obj in character_mesh_objs if m.name in [mat.name for mat in obj.data.materials if mat]],
                    "blend_method": m.blend_method,
                    "use_backface_culling": m.use_backface_culling
                }
                materials_info[m.name] = mat_data
    
    mat_json_path = os.path.join(material_export_dir, "Materials_Summary.json")
    with open(mat_json_path, "w") as f:
        json.dump(materials_info, f, indent=2)
    print(f"Saved material manifest to {mat_json_path}")

    # 7. Rig Documentation
    print("\n--- Documenting Rig Hierarchy ---")
    rig_info = {
        "armature_name": arm_obj.name,
        "total_bones": len(arm_obj.data.bones),
        "root_bones": [b.name for b in arm_obj.data.bones if not b.parent],
        "bone_hierarchy": {}
    }
    for b in arm_obj.data.bones:
        rig_info["bone_hierarchy"][b.name] = {
            "parent": b.parent.name if b.parent else None,
            "children": [c.name for c in b.children],
            "head": [round(c, 4) for c in b.head_local],
            "tail": [round(c, 4) for c in b.tail_local],
            "length": round(b.length, 4)
        }
    rig_json_path = os.path.join(rig_export_dir, "Rig_Hierarchy.json")
    with open(rig_json_path, "w") as f:
        json.dump(rig_info, f, indent=2)
    print(f"Saved rig hierarchy documentation to {rig_json_path}")

    print("\n=== All Production Character Assets Successfully Packaged and Exported ===")

if __name__ == '__main__':
    export_assets()
