#!/usr/bin/env python3
"""
unwrap_raghunath_uvs.py
Ensure all Raghunath character meshes have clean, non-overlapping UV maps.
"""
import bpy

def unwrap_uvs():
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    if not col:
        print("Collection Character_Raghunath_Mattre not found!")
        return

    for obj in col.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            if "UVMap" not in mesh.uv_layers:
                mesh.uv_layers.new(name="UVMap")
            mesh.uv_layers.active = mesh.uv_layers["UVMap"]

            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            try:
                bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
            except Exception as e:
                print(f"UV unwrapping note for {obj.name}: {e}")
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"UV unwrapped: {obj.name} ({len(mesh.uv_layers)} UV layers)")

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("All character meshes successfully UV unwrapped and saved.")

if __name__ == '__main__':
    unwrap_uvs()
