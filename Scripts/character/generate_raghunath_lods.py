#!/usr/bin/env python3
"""
generate_raghunath_lods.py
Generates Game-Ready Level-of-Detail (LOD0 through LOD3) models for Raghunath Mattre.
Exports modular LOD FBX assets to GRAI/Characters/Raghunath/Export/LOD/
"""
import bpy
import os
import json

def generate_lods():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    lod_dir = "/Users/ms/Downloads/GRAI/GRAI/Characters/Raghunath/Export/LOD"
    os.makedirs(lod_dir, exist_ok=True)

    lod_configs = [
        ("LOD0", 1.00), # Full quality (Hero / Cinematic)
        ("LOD1", 0.65), # Close Gameplay (65% poly count)
        ("LOD2", 0.35), # Medium Distance (35% poly count)
        ("LOD3", 0.15)  # Far Distance / Crowds (15% poly count)
    ]

    lod_report = []

    for lod_name, ratio in lod_configs:
        print(f"\n--- Generating {lod_name} (ratio: {ratio:.2f}) ---")
        bpy.ops.wm.open_mainfile(filepath=blend_path)
        col = bpy.data.collections.get("Character_Raghunath_Mattre")
        arm_obj = bpy.data.objects.get("Armature_Raghunath")
        mesh_objects = [o for o in col.objects if o.type == 'MESH']

        total_verts = 0
        total_tris = 0

        # Apply decimation if ratio < 1.0
        for obj in mesh_objects:
            if ratio < 1.0:
                # If mesh has shape keys, clear them on distant LODs to allow decimation
                if obj.data.shape_keys:
                    obj.shape_key_clear()
                mod_dec = obj.modifiers.new(f"Decimate_{lod_name}", 'DECIMATE')
                mod_dec.ratio = ratio
                bpy.context.view_layer.objects.active = obj
                try:
                    bpy.ops.object.modifier_apply(modifier=mod_dec.name)
                except Exception as e:
                    print(f"Note applying decimate on {obj.name}: {e}")

            total_verts += len(obj.data.vertices)
            total_tris += len(obj.data.polygons)

        fbx_name = f"SKM_Raghunath_{lod_name}.fbx"
        fbx_path = os.path.join(lod_dir, fbx_name)

        # Select all character meshes and armature
        bpy.ops.object.select_all(action='DESELECT')
        if arm_obj:
            arm_obj.select_set(True)
        for obj in mesh_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj if arm_obj else mesh_objects[0]

        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            axis_forward='-Y',
            axis_up='Z',
            object_types={'ARMATURE', 'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='FACE',
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            armature_nodetype='NULL',
            bake_anim=False
        )

        size_kb = os.path.getsize(fbx_path) / 1024
        print(f"Exported {lod_name}: {total_verts} verts, {total_tris} polys ({size_kb:.1f} KB)")
        lod_report.append({
            "lod": lod_name,
            "decimation_ratio": ratio,
            "vertices": total_verts,
            "polygons": total_tris,
            "file_size_kb": round(size_kb, 1),
            "export_path": fbx_path
        })

    report_path = "/Users/ms/Downloads/GRAI/Reports/Raghunath_LOD_Report.json"
    with open(report_path, "w") as f:
        json.dump(lod_report, f, indent=2)

    print(f"\nLOD generation complete. Report saved to {report_path}")

if __name__ == '__main__':
    generate_lods()
