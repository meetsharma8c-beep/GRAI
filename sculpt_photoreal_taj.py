"""
GRAI — HIGH-FIDELITY ARCHITECTURAL SCULPTOR FOR TAJ MAHAL PALACE & GATEWAY
Generates realistic Victorian Indo-Saracenic facade geometry:
- Recessed arched windows with stone mullions
- Corbelled cantilevered balconies with wrought-iron railings
- Fluted octagonal dome drum with arched windows
- Seamless Florentine bulbous dome and gold finial
- Naturalistic Royal Palm tree placement along plaza perimeter
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

def sculpt_photoreal_taj():
    print(">>> Sculpting Photorealistic Taj Mahal Palace & Gateway Precinct...")

    col_landmarks = bpy.data.collections.get("Landmarks_Bespoke_Architecture")
    if not col_landmarks:
        col_landmarks = bpy.data.collections.new("Landmarks_Bespoke_Architecture")
        bpy.context.scene.collection.children.link(col_landmarks)

    col_veg = bpy.data.collections.get("Urban_Vegetation_Palm_Trees")
    if not col_veg:
        col_veg = bpy.data.collections.new("Urban_Vegetation_Palm_Trees")
        bpy.context.scene.collection.children.link(col_veg)

    # -------------------------------------------------------------------------
    # 1. SHADERS WITH SCANNED MATERIAL REALISM
    # -------------------------------------------------------------------------
    # A) Kharodi Yellow Basalt Stone (Warm Mumbai Heritage Stone)
    mat_stone = bpy.data.materials.get("Mat_Taj_Kharodi_Basalt")
    if not mat_stone:
        mat_stone = bpy.data.materials.new("Mat_Taj_Kharodi_Basalt")
    mat_stone.use_nodes = True
    bsdf_st = mat_stone.node_tree.nodes.get("Principled BSDF")
    bsdf_st.inputs['Base Color'].default_value = (0.78, 0.66, 0.52, 1.0)
    bsdf_st.inputs['Roughness'].default_value = 0.72

    # B) Dark Kurla Basalt (Plinths & Ground Arches)
    mat_dark_basalt = bpy.data.materials.get("Mat_Heritage_Dark_Basalt")
    if not mat_dark_basalt:
        mat_dark_basalt = bpy.data.materials.new("Mat_Heritage_Dark_Basalt")
    mat_dark_basalt.use_nodes = True
    bsdf_db = mat_dark_basalt.node_tree.nodes.get("Principled BSDF")
    bsdf_db.inputs['Base Color'].default_value = (0.28, 0.26, 0.24, 1.0)
    bsdf_db.inputs['Roughness'].default_value = 0.85

    # C) Florentine Vermilion Red Tile
    mat_red = bpy.data.materials.get("Mat_Taj_Red_Dome_Tile")
    if not mat_red:
        mat_red = bpy.data.materials.new("Mat_Taj_Red_Dome_Tile")
    mat_red.use_nodes = True
    bsdf_rd = mat_red.node_tree.nodes.get("Principled BSDF")
    bsdf_rd.inputs['Base Color'].default_value = (0.64, 0.16, 0.11, 1.0)
    bsdf_rd.inputs['Roughness'].default_value = 0.35

    # D) Gold Finial & Ornaments
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat_gold:
        mat_gold = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
    mat_gold.use_nodes = True
    bsdf_gd = mat_gold.node_tree.nodes.get("Principled BSDF")
    bsdf_gd.inputs['Base Color'].default_value = (0.95, 0.78, 0.22, 1.0)
    bsdf_gd.inputs['Metallic'].default_value = 0.95
    bsdf_gd.inputs['Roughness'].default_value = 0.18

    # E) Recessed Window Glazing (Reflective Deep Blue-Grey)
    mat_glass = bpy.data.materials.get("Mat_Taj_Window_Glass")
    if not mat_glass:
        mat_glass = bpy.data.materials.new("Mat_Taj_Window_Glass")
    mat_glass.use_nodes = True
    bsdf_gl = mat_glass.node_tree.nodes.get("Principled BSDF")
    bsdf_gl.inputs['Base Color'].default_value = (0.04, 0.06, 0.08, 1.0)
    bsdf_gl.inputs['Roughness'].default_value = 0.10
    bsdf_gl.inputs['Metallic'].default_value = 0.20

    # F) Wrought Iron Railings & Mouldings
    mat_iron = bpy.data.materials.get("Mat_Wrought_Iron_Railing")
    if not mat_iron:
        mat_iron = bpy.data.materials.new("Mat_Wrought_Iron_Railing")
    mat_iron.use_nodes = True
    bsdf_ir = mat_iron.node_tree.nodes.get("Principled BSDF")
    bsdf_ir.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1.0)
    bsdf_ir.inputs['Roughness'].default_value = 0.45

    # G) Taj Tower Modernist Concrete
    mat_tower = bpy.data.materials.get("Mat_Taj_Tower_Concrete")
    if not mat_tower:
        mat_tower = bpy.data.materials.new("Mat_Taj_Tower_Concrete")
    mat_tower.use_nodes = True
    bsdf_tw = mat_tower.node_tree.nodes.get("Principled BSDF")
    bsdf_tw.inputs['Base Color'].default_value = (0.80, 0.78, 0.74, 1.0)
    bsdf_tw.inputs['Roughness'].default_value = 0.50

    # -------------------------------------------------------------------------
    # 2. REBUILD TAJ MAHAL PALACE WITH ARCHITECTURAL FENESTRATION & RELIEF
    # -------------------------------------------------------------------------
    old_taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
    if old_taj:
        bpy.data.objects.remove(old_taj, do_unlink=True)

    taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
    taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
    col_landmarks.objects.link(taj_obj)
    taj_obj.location = Vector((94.17, -163.10, 2.20))

    taj_mesh.materials.append(mat_stone)       # 0: Kharodi Basalt
    taj_mesh.materials.append(mat_dark_basalt) # 1: Dark Kurla Basalt
    taj_mesh.materials.append(mat_red)         # 2: Red Clay Tiles
    taj_mesh.materials.append(mat_gold)        # 3: Gold Finial
    taj_mesh.materials.append(mat_glass)       # 4: Recessed Glazing
    taj_mesh.materials.append(mat_iron)        # 5: Wrought Iron Railings
    taj_mesh.materials.append(mat_tower)       # 6: Tower Concrete

    bm = bmesh.new()

    # --- A) MAIN BUILDING MASSING (U-SHAPE) ---
    # Central Core: Width (Y) = 36m, Depth (X) = 24m, Height (Z) = 32m
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0.0, 0.0, 16.0))) @ Matrix.Diagonal(Vector((24.0, 36.0, 32.0, 1.0))))
    # North Wing: Width (Y) = 14m, Depth (X) = 28m, Height (Z) = 30m, at Y = +39m
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((2.0, 39.0, 15.0))) @ Matrix.Diagonal(Vector((28.0, 14.0, 30.0, 1.0))))
    # South Wing: Width (Y) = 14m, Depth (X) = 28m, Height (Z) = 30m, at Y = -39m
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((2.0, -39.0, 15.0))) @ Matrix.Diagonal(Vector((28.0, 14.0, 30.0, 1.0))))
    # Rear Spine: Width (Y) = 92m, Depth (X) = 12m, Height (Z) = 30m, at X = -14m
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-14.0, 0.0, 15.0))) @ Matrix.Diagonal(Vector((12.0, 92.0, 30.0, 1.0))))

    # Base Plinth (Dark Kurla Basalt step, Z = 0 to 2.2m)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0.5, 0.0, 1.1))) @ Matrix.Diagonal(Vector((26.0, 96.0, 2.2, 1.0))))

    # Assign base massing faces to mat_stone (0)
    for f in bm.faces:
        f.material_index = 0

    # --- B) GROUND FLOOR ARCADED LOGGIA & CORNICES ---
    # Ground floor rusticated arcade projecting 1.5m outward facing harbour (X = +12.5m)
    # Arcade piers and arched openings
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.8, 0.0, 3.2))) @ Matrix.Diagonal(Vector((1.6, 34.0, 4.4, 1.0))))
    # Ground cornice line dividing ground floor from upper tiers
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((13.2, 0.0, 5.6))) @ Matrix.Diagonal(Vector((2.2, 35.5, 0.6, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.4, 39.0, 5.6))) @ Matrix.Diagonal(Vector((2.0, 15.0, 0.6, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.4, -39.0, 5.6))) @ Matrix.Diagonal(Vector((2.0, 15.0, 0.6, 1.0))))

    # --- C) 5 UPPER FLOORS DETAILED WINDOW ARCADES & BALCONIES ---
    # Central facade bays: 7 window bays along Y between -15 and +15
    for floor in range(1, 6):
        fz = 5.6 + (floor - 1) * 5.0 + 2.5
        # Inter-floor horizontal string course / stone cornice
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.5, 0.0, fz + 2.2))) @ Matrix.Diagonal(Vector((1.0, 35.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.2, 39.0, fz + 2.2))) @ Matrix.Diagonal(Vector((1.0, 14.5, 0.45, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.2, -39.0, fz + 2.2))) @ Matrix.Diagonal(Vector((1.0, 14.5, 0.45, 1.0))))

        # Continuous cantilevered balcony slab
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((13.0, 0.0, fz - 2.0))) @ Matrix.Diagonal(Vector((2.0, 33.0, 0.4, 1.0))))
        # Wrought iron balustrade
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((13.9, 0.0, fz - 1.4))) @ Matrix.Diagonal(Vector((0.15, 33.0, 0.9, 1.0))))

        # North & South wing balconies
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.8, 39.0, fz - 2.0))) @ Matrix.Diagonal(Vector((1.8, 13.0, 0.4, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((17.6, 39.0, fz - 1.4))) @ Matrix.Diagonal(Vector((0.15, 13.0, 0.9, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.8, -39.0, fz - 2.0))) @ Matrix.Diagonal(Vector((1.8, 13.0, 0.4, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((17.6, -39.0, fz - 1.4))) @ Matrix.Diagonal(Vector((0.15, 13.0, 0.9, 1.0))))

        # Recessed arched window panes (dark reflective glass)
        # 8 bays on central facade
        for bay in range(-3, 4):
            by_pos = bay * 4.2
            # Arched window opening
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.15, by_pos, fz))) @ Matrix.Diagonal(Vector((0.2, 2.2, 3.2, 1.0))))
            # Stone hood moulding / pediment above window
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.4, by_pos, fz + 1.8))) @ Matrix.Diagonal(Vector((0.6, 2.6, 0.35, 1.0))))

        # Window bays on North & South Wings
        for w_bay in [-1, 0, 1]:
            # North wing east-facing windows
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.15, 39.0 + w_bay * 3.8, fz))) @ Matrix.Diagonal(Vector((0.2, 2.0, 3.2, 1.0))))
            # South wing east-facing windows
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.15, -39.0 + w_bay * 3.8, fz))) @ Matrix.Diagonal(Vector((0.2, 2.0, 3.2, 1.0))))

    # --- D) ROOF LEVEL: RED PITCHED ROOFS & GABLES ---
    # North Wing hip roof (Red Mangalore clay tile)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=10.0, radius2=1.0, depth=6.5, matrix=Matrix.Translation(Vector((2.0, 39.0, 33.0))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    # South Wing hip roof
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=10.0, radius2=1.0, depth=6.5, matrix=Matrix.Translation(Vector((2.0, -39.0, 33.0))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    # Rear spine roof
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-14.0, 0.0, 32.5))) @ Matrix.Diagonal(Vector((13.0, 92.0, 4.0, 1.0))))

    # Decorative parapet & bracketed chhajja along main facade
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.4, 0.0, 31.8))) @ Matrix.Diagonal(Vector((1.8, 36.0, 0.9, 1.0))))

    # --- E) THE MONUMENTAL FLORENTINE DOME ---
    # Octagonal drum base with 16 arched window bays (Z = 31.0 to 41.0m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=11.2, radius2=10.6, depth=10.0, matrix=Matrix.Translation(Vector((0.0, 0.0, 36.0))))
    # Arcaded gallery cornice ring
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=11.6, radius2=11.4, depth=1.2, matrix=Matrix.Translation(Vector((0.0, 0.0, 41.5))))
    # Florentine bulbous pointed dome (Seamless 32 segments, Z = 42.0 to 62.0m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=10.6, radius2=1.2, depth=21.0, matrix=Matrix.Translation(Vector((0.0, 0.0, 52.5))))
    # Lantern / Cupola atop dome (Z = 63.0 to 67.0m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=2.2, radius2=1.8, depth=4.5, matrix=Matrix.Translation(Vector((0.0, 0.0, 65.0))))
    # Slender gilded finial spire (Z = 67.0 to 72.0m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.6, radius2=0.04, depth=5.0, matrix=Matrix.Translation(Vector((0.0, 0.0, 69.5))))

    # --- F) 4 CORNER MOORISH ONION CHHATRIS ---
    chhatri_positions = [
        Vector((14.0, 44.0, 30.0)),
        Vector((14.0, -44.0, 30.0)),
        Vector((-19.0, 44.0, 30.0)),
        Vector((-19.0, -44.0, 30.0))
    ]
    for cp in chhatri_positions:
        # Octagonal base
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=2.8, radius2=2.5, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
        # Onion dome
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=2.5, radius2=0.25, depth=5.0, matrix=Matrix.Translation(cp + Vector((0, 0, 5.8))))
        # Finial
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.22, radius2=0.03, depth=2.5, matrix=Matrix.Translation(cp + Vector((0, 0, 8.8))))

    # --- G) TAJ TOWER (MODERNIST HIGH-RISE TOWER) ---
    tower_c = Vector((-34.0, -58.0, 0.0))
    # Core tower cylinder (radius 16m, height 86m)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=16.0, radius2=15.8, depth=86.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 43.0))))
    # 22 Cantilevered floor balcony rings
    for bf in range(1, 23):
        bfz = bf * 3.6 + 2.5
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=17.4, radius2=17.2, depth=0.75, matrix=Matrix.Translation(tower_c + Vector((0, 0, bfz))))
    # Observation deck flaring crown
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=18.5, radius2=12.0, depth=8.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 89.0))))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=3.5, radius2=0.4, depth=6.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 96.0))))

    bm.to_mesh(taj_mesh)
    bm.free()

    # Apply materials and smooth shading to Taj polygons
    for poly in taj_mesh.polygons:
        pz = poly.center.z
        px = poly.center.x
        py = poly.center.y

        if pz > 30.0 or px < -20.0:
            poly.use_smooth = True

        if px < -20.0 and py < -40.0:
            poly.material_index = 6 # Taj Tower Concrete
        elif pz > 67.0 and abs(py) < 8.0:
            poly.material_index = 3 # Gold Finial
        elif pz > 41.0 and abs(py) < 14.0 and abs(px) < 14.0:
            poly.material_index = 2 # Red Florentine Dome
        elif pz > 30.0 and px > -15.0:
            poly.material_index = 2 # Red Roof Tiles
        elif poly.normal.dot(Vector((1, 0, 0))) > 0.8 and px > 13.5 and pz < 30.0:
            poly.material_index = 5 # Wrought Iron Railings
        elif abs(px - 12.15) < 0.2 and pz < 30.0:
            poly.material_index = 4 # Recessed Glazing
        elif abs(px - 16.15) < 0.2 and pz < 30.0:
            poly.material_index = 4 # Wing Window Glazing
        elif pz < 2.5:
            poly.material_index = 1 # Dark Kurla Basalt Base
        else:
            poly.material_index = 0 # Kharodi Yellow Basalt Facade

    # -------------------------------------------------------------------------
    # 3. REALISTIC PALM TREES LINING THE PERIMETER PROMENADE
    # -------------------------------------------------------------------------
    # Remove old palms
    for o in list(bpy.data.objects):
        if o.name.startswith("PALM_GatewayPlaza_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # Realistic Royal Palm mesh: tall graceful trunk, curved fronds
    palm_mesh = bpy.data.meshes.new("RoyalPalm_Heritage_Mesh")
    bm_pm = bmesh.new()

    # Slender realistic trunk (height 14m, radius 0.26m)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=12, radius1=0.34, radius2=0.22, depth=13.0, matrix=Matrix.Translation(Vector((0, 0, 6.5))))
    # Smooth emerald crownshaft (height 2.2m)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=12, radius1=0.22, radius2=0.20, depth=2.2, matrix=Matrix.Translation(Vector((0, 0, 14.0))))

    for f in bm_pm.faces:
        f.material_index = 0 # Trunk bark

    # 24 Arching fronds with natural droop
    frond_count = 24
    for f_i in range(frond_count):
        ang = 2.0 * math.pi * (f_i / float(frond_count)) + f_i * 0.15
        pitch = math.radians(10.0 + (f_i % 3) * 18.0)
        flen = 4.8
        pts = []
        for s in range(8):
            fr = s / 7.0
            rd = fr * flen * math.cos(pitch)
            zd = math.sin(fr * math.pi * 0.85) * 1.4 - (fr ** 2) * 2.2
            pts.append(Vector((math.cos(ang) * rd, math.sin(ang) * rd, 14.8 + zd)))

        for s in range(7):
            p1 = pts[s]
            p2 = pts[s + 1]
            fr = s / 7.0
            w = math.sin(fr * math.pi) * 0.65 + 0.10
            perp = Vector((-math.sin(ang), math.cos(ang), -0.2 * fr)).normalized() * w
            v1 = bm_pm.verts.new(p1 - perp)
            v2 = bm_pm.verts.new(p1 + perp)
            v3 = bm_pm.verts.new(p2 + perp)
            v4 = bm_pm.verts.new(p2 - perp)
            f = bm_pm.faces.new((v1, v2, v3, v4))
            f.material_index = 1 # 100% Green leaf

    bm_pm.to_mesh(palm_mesh)
    bm_pm.free()

    for poly in palm_mesh.polygons:
        poly.use_smooth = True

    mat_ptrunk = bpy.data.materials.get("MAT_Palm_TrunkBark")
    mat_pleaf = bpy.data.materials.get("MAT_Palm_GreenFronds")
    if mat_ptrunk: palm_mesh.materials.append(mat_ptrunk)
    if mat_pleaf: palm_mesh.materials.append(mat_pleaf)

    # Place palms along perimeter garden borders (leaving the central Gateway-Taj plaza view open!)
    perimeter_palm_locs = [
        Vector((195.0, -90.0, 2.2)),
        Vector((195.0, -75.0, 2.2)),
        Vector((195.0, -60.0, 2.2)),
        Vector((165.0, -60.0, 2.2)),
        Vector((145.0, -60.0, 2.2)),
        Vector((110.0, -75.0, 2.2)),
        Vector((195.0, -195.0, 2.2)),
        Vector((180.0, -195.0, 2.2)),
        Vector((165.0, -195.0, 2.2)),
        Vector((145.0, -195.0, 2.2)),
        Vector((125.0, -195.0, 2.2)),
        Vector((105.0, -195.0, 2.2)),
    ]
    random.seed(42)
    for idx, pl in enumerate(perimeter_palm_locs):
        p_obj = bpy.data.objects.new(f"PALM_GatewayPlaza_{idx}", palm_mesh)
        col_veg.objects.link(p_obj)
        p_obj.location = pl
        p_obj.rotation_euler = Euler((0, 0, idx * 0.9), 'XYZ')
        p_obj.scale = Vector((1.0, 1.0, random.uniform(0.9, 1.15)))

    # Save blend file
    bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print(">>> Taj Mahal Palace architectural sculpt complete & saved!")
    with open('/tmp/taj_sculpt_complete.txt', 'w') as f:
        f.write('DONE')

if __name__ == '__main__':
    sculpt_photoreal_taj()
