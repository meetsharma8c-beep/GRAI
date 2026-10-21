"""
Build Definitive Continuous Queen's Necklace Lighting System
============================================================
Creates an authentic, continuous array of 68 Victorian 3-globe heritage lamp posts
along the entire 1,700m Marine Drive promenade seawall, plus dual-arm highway
median luminaires along Netaji Subhash Road.
All consolidated into two unified high-performance master meshes:
- LIGHTS_QueensNecklace_Promenade_Posts_Master (MAT_Heritage_Iron_LampPost)
- LIGHTS_QueensNecklace_Promenade_Globes_Master (MAT_StreetLight_WarmGlow)
"""
import bpy
import bmesh
from mathutils import Vector, Matrix

def build_queens_necklace_lights():
    print("=== BUILDING CONTINUOUS QUEEN'S NECKLACE LIGHTING ===")

    # 1. Clean up old sparse lamp objects
    old_lamps = [o for o in list(bpy.data.objects) if o.name.startswith(('LAMP_QueensNecklace_', 'LAMP_MarineDrive_')) or o.name.startswith('LIGHTS_QueensNecklace_')]
    for o in old_lamps:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"Removed {len(old_lamps)} old sparse lamp objects.")

    # 2. Get or create target collection
    col_lights = bpy.data.collections.get("Urban_Street_Lighting")
    if not col_lights:
        col_lights = bpy.data.collections.new("Urban_Street_Lighting")
        bpy.context.scene.collection.children.link(col_lights)

    # 3. Materials
    mat_iron = bpy.data.materials.get("MAT_Heritage_Iron_LampPost")
    if not mat_iron:
        mat_iron = bpy.data.materials.new("MAT_Heritage_Iron_LampPost")
        mat_iron.use_nodes = True
        bsdf = mat_iron.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.55
        bsdf.inputs['Metallic'].default_value = 0.85

    mat_glow = bpy.data.materials.get("MAT_StreetLight_WarmGlow")
    if not mat_glow:
        mat_glow = bpy.data.materials.new("MAT_StreetLight_WarmGlow")
        mat_glow.use_nodes = True
    bsdf_glow = mat_glow.node_tree.nodes.get("Principled BSDF")
    bsdf_glow.inputs['Base Color'].default_value = (1.0, 0.88, 0.65, 1.0)
    bsdf_glow.inputs['Emission Color'].default_value = (1.0, 0.82, 0.45, 1.0) # Rich amber sodium/LED glow
    bsdf_glow.inputs['Emission Strength'].default_value = 18.0

    # 4. Construct BMesh for Posts and Globes
    bm_posts = bmesh.new()
    bm_globes = bmesh.new()

    steps = 68 # Spaced every 25m along 1,700m curve
    y_start = 500.0
    y_end = 2200.0
    dy = (y_end - y_start) / float(steps)

    for i in range(steps + 1):
        y = y_start + i * dy
        # Parabolic arc of Marine Drive Back Bay
        x_c = -1016.0 + 0.000080 * ((y - 1100.0) ** 2)

        # -----------------------------------------------------------------
        # A. Victorian 3-Globe Heritage Promenade Lamp Post
        # Placed right on the seawall promenade (seaward edge of sidewalk)
        # -----------------------------------------------------------------
        x_prom = x_c - 11.5
        z_prom = 7.35

        # Base Plinth (height 0.8m)
        mat_trans = Matrix.Translation(Vector((x_prom, y, z_prom + 0.4)))
        bmesh.ops.create_cone(bm_posts, cap_ends=True, radius1=0.22, radius2=0.18, depth=0.8, segments=8, matrix=mat_trans)

        # Column Shaft (height 3.2m)
        mat_trans = Matrix.Translation(Vector((x_prom, y, z_prom + 2.4)))
        bmesh.ops.create_cone(bm_posts, cap_ends=True, radius1=0.10, radius2=0.07, depth=3.2, segments=8, matrix=mat_trans)

        # Horizontal Cross-Arm Bracket (width 1.2m)
        mat_rot = Matrix.Rotation(1.5708, 4, 'Y') # 90 deg rotation around Y -> spans across X
        mat_trans = Matrix.Translation(Vector((x_prom, y, z_prom + 4.05))) @ mat_rot
        bmesh.ops.create_cone(bm_posts, cap_ends=True, radius1=0.04, radius2=0.04, depth=1.2, segments=6, matrix=mat_trans)

        # 3 Glowing Frosted Globes
        # Center Globe
        mat_trans = Matrix.Translation(Vector((x_prom, y, z_prom + 4.45)))
        bmesh.ops.create_uvsphere(bm_globes, u_segments=10, v_segments=8, radius=0.22, matrix=mat_trans)

        # Left & Right Globes
        mat_trans = Matrix.Translation(Vector((x_prom - 0.55, y, z_prom + 4.15)))
        bmesh.ops.create_uvsphere(bm_globes, u_segments=8, v_segments=6, radius=0.18, matrix=mat_trans)

        mat_trans = Matrix.Translation(Vector((x_prom + 0.55, y, z_prom + 4.15)))
        bmesh.ops.create_uvsphere(bm_globes, u_segments=8, v_segments=6, radius=0.18, matrix=mat_trans)

        # -----------------------------------------------------------------
        # B. Highway Median High-Mast Luminaires (Every 50m - even indices)
        # -----------------------------------------------------------------
        if (i % 2) == 0:
            x_med = x_c
            z_med = 7.23

            # Tall highway mast (height 8.5m)
            mat_trans = Matrix.Translation(Vector((x_med, y, z_med + 4.25)))
            bmesh.ops.create_cone(bm_posts, cap_ends=True, radius1=0.16, radius2=0.09, depth=8.5, segments=8, matrix=mat_trans)

            # Dual mast cross-arm
            mat_rot = Matrix.Rotation(1.5708, 4, 'Y')
            mat_trans = Matrix.Translation(Vector((x_med, y, z_med + 8.5))) @ mat_rot
            bmesh.ops.create_cone(bm_posts, cap_ends=True, radius1=0.05, radius2=0.05, depth=3.6, segments=6, matrix=mat_trans)

            # Left & Right LED highway luminaires
            mat_trans = Matrix.Translation(Vector((x_med - 1.8, y, z_med + 8.45)))
            bmesh.ops.create_uvsphere(bm_globes, u_segments=8, v_segments=6, radius=0.25, matrix=mat_trans)

            mat_trans = Matrix.Translation(Vector((x_med + 1.8, y, z_med + 8.45)))
            bmesh.ops.create_uvsphere(bm_globes, u_segments=8, v_segments=6, radius=0.25, matrix=mat_trans)

    # 5. Build Final Objects
    mesh_posts = bpy.data.meshes.new("LIGHTS_QueensNecklace_Promenade_Posts_Mesh")
    bm_posts.to_mesh(mesh_posts)
    bm_posts.free()
    mesh_posts.materials.append(mat_iron)
    obj_posts = bpy.data.objects.new("LIGHTS_QueensNecklace_Promenade_Posts_Master", mesh_posts)
    col_lights.objects.link(obj_posts)

    mesh_globes = bpy.data.meshes.new("LIGHTS_QueensNecklace_Promenade_Globes_Mesh")
    bm_globes.to_mesh(mesh_globes)
    bm_globes.free()
    mesh_globes.materials.append(mat_glow)
    obj_globes = bpy.data.objects.new("LIGHTS_QueensNecklace_Promenade_Globes_Master", mesh_globes)
    col_lights.objects.link(obj_globes)

    total_posts = steps + 1
    total_globes = (steps + 1) * 3 + ((steps // 2) + 1) * 2
    print(f"Created {total_posts} Victorian Promenade Posts + Highway Masts with {total_globes} glowing globes.")

    return f"Queen's Necklace continuous lights built successfully ({total_posts} posts, {total_globes} glowing globes)!"

if __name__ == '__main__':
    msg = build_queens_necklace_lights()
    print(msg)
