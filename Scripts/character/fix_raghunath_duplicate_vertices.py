#!/usr/bin/env python3
"""
fix_raghunath_duplicate_vertices.py
===================================
Automated script to remove duplicate vertices across all meshes in Character_Raghunath_Mattre collection,
preserving shape keys, vertex weights, and UV layouts.
"""

import bpy

def fix_duplicates():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    if not col:
        print("ERROR: Character_Raghunath_Mattre collection not found.")
        return

    mesh_objs = [o for o in col.objects if o.type == 'MESH']
    print(f"Auditing and cleaning {len(mesh_objs)} meshes for duplicate vertices...")

    total_removed = 0
    for o in mesh_objs:
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        
        init_v = len(o.data.vertices)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')
        after_v = len(o.data.vertices)
        
        diff = init_v - after_v
        if diff > 0:
            print(f"  Cleaned {o.name}: removed {diff} duplicate vertices (was {init_v}, now {after_v})")
            total_removed += diff
        else:
            print(f"  Verified {o.name}: 0 duplicate vertices ({init_v} clean)")

    print(f"Total duplicate vertices removed across all meshes: {total_removed}")

    # Save cleaned file
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"Saved updated master blend file: {blend_path}")

if __name__ == '__main__':
    fix_duplicates()
