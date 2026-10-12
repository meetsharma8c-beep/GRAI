"""
GRAI — DEFINITIVE POLISH MASTER FOR APOLLO BUNDER (HERO PRECINCT)
"""

def main():
    import bpy
    import bmesh
    import math
    import random
    from mathutils import Vector, Matrix, Euler

    print("Executing Apollo Bunder Polish Master...")

    col_landmarks = bpy.data.collections.get("Landmarks_Bespoke_Architecture")
    col_veg = bpy.data.collections.get("Urban_Vegetation_Palm_Trees")

    # ==================================================================
    # 1. REBUILD ROYAL PALMS WITH 100% VIBRANT GREEN CANOPY
    # ==================================================================
    for o in list(bpy.data.objects):
        if o.name.startswith("PALM_GatewayPlaza_"):
            bpy.data.objects.remove(o, do_unlink=True)

    palm_mesh = bpy.data.meshes.new("RoyalPalm_Refined_Mesh")
    bm_pm = bmesh.new()

    # Trunk (height 11m)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.52, radius2=0.36, depth=11.0, matrix=Matrix.Translation(Vector((0, 0, 5.5))))
    # Crownshaft (height 2.2m)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.38, radius2=0.34, depth=2.2, matrix=Matrix.Translation(Vector((0, 0, 12.1))))

    # All cone faces so far get material_index = 0
    for f in bm_pm.faces:
        f.material_index = 0

    # 24 Arching fronds
    frond_count = 24
    for f_i in range(frond_count):
        f_ang = 2.0 * math.pi * (f_i / float(frond_count)) + (f_i * 0.12)
        f_elev = math.radians(20.0 + (f_i % 3) * 15.0)
        f_len = 5.8
        pts = []
        for step in range(8):
            frac = step / 7.0
            r_dist = frac * f_len * math.cos(f_elev)
            z_arch = math.sin(frac * math.pi) * 1.6 - frac * frac * 2.8
            fx = math.cos(f_ang) * r_dist
            fy = math.sin(f_ang) * r_dist
            fz = 13.0 + z_arch
            pts.append(Vector((fx, fy, fz)))
        for step in range(7):
            p1 = pts[step]
            p2 = pts[step + 1]
            side_w = math.sin((step / 7.0) * math.pi) * 0.75 + 0.15
            perp = Vector((-math.sin(f_ang), math.cos(f_ang), 0)) * side_w
            v1 = bm_pm.verts.new(p1 - perp)
            v2 = bm_pm.verts.new(p1 + perp)
            v3 = bm_pm.verts.new(p2 + perp)
            v4 = bm_pm.verts.new(p2 - perp)
            f = bm_pm.faces.new((v1, v2, v3, v4))
            f.material_index = 1 # 100% Green frond leaf!

    bm_pm.to_mesh(palm_mesh)
    bm_pm.free()

    for poly in palm_mesh.polygons:
        poly.use_smooth = True

    mat_palm_trunk = bpy.data.materials.get("MAT_Palm_TrunkBark")
    mat_palm_leaf = bpy.data.materials.get("MAT_Palm_GreenFronds")
    if mat_palm_trunk: palm_mesh.materials.append(mat_palm_trunk)
    if mat_palm_leaf: palm_mesh.materials.append(mat_palm_leaf)

    palm_locs = [
        Vector((150.0, -118.0, 2.2)),
        Vector((150.0, -135.0, 2.2)),
        Vector((150.0, -152.0, 2.2)),
        Vector((150.0, -170.0, 2.2)),
        Vector((185.0, -145.0, 2.2)),
        Vector((185.0, -165.0, 2.2)),
        Vector((185.0, -185.0, 2.2)),
        Vector((120.0, -125.0, 2.2)),
        Vector((120.0, -145.0, 2.2)),
        Vector((120.0, -165.0, 2.2)),
        Vector((195.0, -100.0, 2.2)),
        Vector((195.0, -85.0, 2.2))
    ]
    random.seed(42)
    for idx, pl in enumerate(palm_locs):
        p_obj = bpy.data.objects.new(f"PALM_GatewayPlaza_{idx}", palm_mesh)
        col_veg.objects.link(p_obj)
        p_obj.location = pl
        p_obj.rotation_euler = Euler((0, 0, idx * 0.8), 'XYZ')
        p_obj.scale = Vector((1.0, 1.0, random.uniform(0.9, 1.15)))

    # ==================================================================
    # 2. REBUILD TAJ MAHAL PALACE WITH SEAMLESS FLORENTINE DOME
    # ==================================================================
    old_taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
    if old_taj:
        bpy.data.objects.remove(old_taj, do_unlink=True)

    taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
    taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
    col_landmarks.objects.link(taj_obj)
    taj_obj.location = Vector((94.17, -163.10, 2.20))

    bm_taj = bmesh.new()

    # Ground Portico Arcade (Kurla Basalt arches)
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 2.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 3.0))) @ Matrix.Diagonal(Vector((24.0, 32.0, 6.0, 1.0))))

    # Main Wings (Z = 5.5 to 32.0m)
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 18.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 20.0))) @ Matrix.Diagonal(Vector((22.0, 30.0, 28.0, 1.0))))

    # 6 Architectural Tiers of Cantilevered Balconies
    for tier in range(1, 6):
        tz = tier * 5.2 + 2.5
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((12.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.4, 28.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((13.6, 0.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 28.0, 0.9, 1.0))))

        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, 36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((17.4, 36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 12.0, 0.9, 1.0))))

        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, -36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((17.4, -36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 12.0, 0.9, 1.0))))

    # Pitched Red Mangalore Tile Roofs
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 34.0))) @ Matrix.Diagonal(Vector((13.0, 84.0, 4.0, 1.0))))

    # Grand Florentine Pointed Red Dome (Seamless 32 segments, NO needle sticks!)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=10.5, radius2=10.0, depth=10.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 37.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=10.2, radius2=1.0, depth=21.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 52.5))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=2.2, radius2=1.9, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 65.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=12, radius1=0.6, radius2=0.04, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 70.0))))

    # 4 Corner Moorish Chhatris
    taj_chhatris = [
        Vector((15.0, 41.5, 32.0)),
        Vector((15.0, -41.5, 32.0)),
        Vector((-21.0, 41.5, 32.0)),
        Vector((-21.0, -41.5, 32.0))
    ]
    for cp in taj_chhatris:
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=3.0, radius2=2.6, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=24, radius1=2.6, radius2=0.3, depth=5.0, matrix=Matrix.Translation(cp + Vector((0, 0, 6.0))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=12, radius1=0.25, radius2=0.03, depth=2.8, matrix=Matrix.Translation(cp + Vector((0, 0, 9.0))))

    # Taj Tower
    tower_c = Vector((-34.0, -58.0, 0.0))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=16.0, radius2=15.8, depth=84.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 42.0))))
    for b_floor in range(1, 23):
        bf_z = b_floor * 3.6 + 2.0
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=17.4, radius2=17.2, depth=0.8, matrix=Matrix.Translation(tower_c + Vector((0, 0, bf_z))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=18.5, radius2=12.0, depth=8.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 88.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=3.5, radius2=0.4, depth=6.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 95.0))))

    bm_taj.to_mesh(taj_mesh)
    bm_taj.free()

    for poly in taj_mesh.polygons:
        if poly.center.z > 32.0 or poly.center.x < -20.0:
            poly.use_smooth = True

    mat_taj_facade = bpy.data.materials.get("Mat_Taj_Mahal_Facade_Detailed")
    mat_taj_red = bpy.data.materials.get("Mat_Taj_Red_Dome_Tile")
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    mat_tower = bpy.data.materials.get("Mat_Taj_Tower_Concrete")
    mat_iron = bpy.data.materials.get("Mat_Wrought_Iron_Railing")

    if mat_taj_facade: taj_obj.data.materials.append(mat_taj_facade)
    if mat_taj_red: taj_obj.data.materials.append(mat_taj_red)
    if mat_gold: taj_obj.data.materials.append(mat_gold)
    if mat_tower: taj_obj.data.materials.append(mat_tower)
    if mat_iron: taj_obj.data.materials.append(mat_iron)

    for poly in taj_mesh.polygons:
        pz = poly.center.z
        px = poly.center.x
        py = poly.center.y
        if px < -22.0 and py < -45.0:
            poly.material_index = 3 # Taj Tower
        elif pz > 67.0 and abs(py) < 8.0:
            poly.material_index = 2 # Gold finial
        elif pz > 41.0 and abs(py) < 14.0 and abs(px) < 14.0:
            poly.material_index = 1 # Red Florentine dome
        elif pz > 32.0 and px > -15.0:
            poly.material_index = 1 # Red pitched roofs
        elif poly.normal.dot(Vector((1, 0, 0))) > 0.8 and pz < 30.0 and px > 13.0:
            poly.material_index = 4 # Wrought iron railings
        else:
            poly.material_index = 0 # Facade

    bpy.context.view_layer.objects.active = taj_obj
    taj_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Save to master blend
    bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print("Apollo Bunder Polish complete and saved!")
    with open("/tmp/apollo_polish_done.txt", "w") as f:
        f.write("DONE")

main()
