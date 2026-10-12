"""
GRAI — SCULPT SCANNED APOLLO BUNDER MASTERPIECE
Photorealistic, scanned-fidelity detailing for Gateway of India,
Taj Mahal Palace & Tower, Royal Palms, and Heritage Forecourt.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

def build_scanned_apollo():
    print(">>> Sculpting Scanned Apollo Bunder Masterpiece...")

    col_landmarks = bpy.data.collections.get("Landmarks_Bespoke_Architecture")
    if not col_landmarks:
        col_landmarks = bpy.data.collections.new("Landmarks_Bespoke_Architecture")
        bpy.context.scene.collection.children.link(col_landmarks)

    col_veg = bpy.data.collections.get("Urban_Vegetation_Palm_Trees")
    if not col_veg:
        col_veg = bpy.data.collections.new("Urban_Vegetation_Palm_Trees")
        bpy.context.scene.collection.children.link(col_veg)

    # -------------------------------------------------------------
    # 1. MATERIALS DEFINITION (REALISTIC PHYSICAL SHADERS)
    # -------------------------------------------------------------
    # A) Warm Mumbai Kharodi Basalt for Taj Facade
    mat_taj_stone = bpy.data.materials.get("Mat_Taj_Kharodi_Basalt")
    if not mat_taj_stone:
        mat_taj_stone = bpy.data.materials.new("Mat_Taj_Kharodi_Basalt")
        mat_taj_stone.use_nodes = True
        nodes = mat_taj_stone.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.76, 0.64, 0.52, 1.0) # Warm golden buff basalt
        bsdf.inputs['Roughness'].default_value = 0.68

    # B) Florentine Red Ceramic Dome & Mangalore Roof Tiles
    mat_taj_red = bpy.data.materials.get("Mat_Taj_Red_Dome_Tile")
    if not mat_taj_red:
        mat_taj_red = bpy.data.materials.new("Mat_Taj_Red_Dome_Tile")
        mat_taj_red.use_nodes = True
        bsdf = mat_taj_red.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.65, 0.18, 0.12, 1.0) # Deep terracotta vermilion
        bsdf.inputs['Roughness'].default_value = 0.38

    # C) Heritage Gold Finial
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat_gold:
        mat_gold = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
        mat_gold.use_nodes = True
        bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.25, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.20

    # D) Wrought Iron Railings & Dark Basalt Trims
    mat_iron = bpy.data.materials.get("Mat_Wrought_Iron_Railing")
    if not mat_iron:
        mat_iron = bpy.data.materials.new("Mat_Wrought_Iron_Railing")
        mat_iron.use_nodes = True
        bsdf = mat_iron.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.50

    # E) Taj Tower Modernist Concrete & Bronze Tinted Glass
    mat_tower = bpy.data.materials.get("Mat_Taj_Tower_Concrete")
    if not mat_tower:
        mat_tower = bpy.data.materials.new("Mat_Taj_Tower_Concrete")
        mat_tower.use_nodes = True
        bsdf = mat_tower.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.82, 0.80, 0.76, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.45

    # F) Royal Palm Smooth Trunk Bark
    mat_palm_trunk = bpy.data.materials.get("MAT_Palm_TrunkBark")
    if not mat_palm_trunk:
        mat_palm_trunk = bpy.data.materials.new("MAT_Palm_TrunkBark")
        mat_palm_trunk.use_nodes = True
    bsdf_tr = mat_palm_trunk.node_tree.nodes.get("Principled BSDF")
    bsdf_tr.inputs['Base Color'].default_value = (0.58, 0.55, 0.50, 1.0) # Smooth concrete-grey royal palm bark
    bsdf_tr.inputs['Roughness'].default_value = 0.80

    # G) Royal Palm Lush Green Fronds
    mat_palm_leaf = bpy.data.materials.get("MAT_Palm_GreenFronds")
    if not mat_palm_leaf:
        mat_palm_leaf = bpy.data.materials.new("MAT_Palm_GreenFronds")
        mat_palm_leaf.use_nodes = True
    bsdf_lf = mat_palm_leaf.node_tree.nodes.get("Principled BSDF")
    bsdf_lf.inputs['Base Color'].default_value = (0.12, 0.45, 0.08, 1.0) # Vibrant lush tropical emerald green
    bsdf_lf.inputs['Roughness'].default_value = 0.35

    # -------------------------------------------------------------
    # 2. REBUILD HIGH-FIDELITY ROYAL PALMS
    # -------------------------------------------------------------
    # Clean previous palms in Apollo Bunder
    for o in list(bpy.data.objects):
        if o.name.startswith("PALM_GatewayPlaza_"):
            bpy.data.objects.remove(o, do_unlink=True)

    palm_mesh = bpy.data.meshes.new("RoyalPalm_Scanned_Mesh")
    bm_pm = bmesh.new()

    # Slender realistic trunk (height 12m, base r=0.38, slight swell at 3m r=0.45, top r=0.28)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.38, radius2=0.44, depth=3.5, matrix=Matrix.Translation(Vector((0, 0, 1.75))))
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.44, radius2=0.28, depth=8.5, matrix=Matrix.Translation(Vector((0, 0, 7.75))))
    # Smooth green crownshaft (height 2.0m, r=0.28 to 0.25)
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.28, radius2=0.25, depth=2.0, matrix=Matrix.Translation(Vector((0, 0, 13.0))))

    # All trunk faces -> material_index = 0
    for f in bm_pm.faces:
        f.material_index = 0

    # 28 Arching pinnate fronds with realistic curvature and wide leaflets
    frond_count = 28
    for f_i in range(frond_count):
        f_ang = 2.0 * math.pi * (f_i / float(frond_count)) + (f_i * 0.11)
        f_elev = math.radians(12.0 + (f_i % 4) * 14.0)
        f_len = 5.6
        pts = []
        for step in range(9):
            frac = step / 8.0
            r_dist = frac * f_len * math.cos(f_elev)
            # Natural parabolic arch + drooping tip
            z_arch = math.sin(frac * math.pi * 0.9) * 1.8 - (frac ** 2.2) * 2.8
            fx = math.cos(f_ang) * r_dist
            fy = math.sin(f_ang) * r_dist
            fz = 13.8 + z_arch
            pts.append(Vector((fx, fy, fz)))

        # Create wide cascading leaflet ribbons along each frond
        for step in range(8):
            p1 = pts[step]
            p2 = pts[step + 1]
            frac = step / 8.0
            # Leaflet width profile (widest in middle, tapering at tip)
            w = math.sin(frac * math.pi) * 0.95 + 0.15
            perp = Vector((-math.sin(f_ang), math.cos(f_ang), 0)).normalized() * w

            # Droop angle for leaflets
            v1 = bm_pm.verts.new(p1 - perp + Vector((0, 0, -0.1 * frac)))
            v2 = bm_pm.verts.new(p1 + perp + Vector((0, 0, -0.1 * frac)))
            v3 = bm_pm.verts.new(p2 + perp + Vector((0, 0, -0.15 * frac)))
            v4 = bm_pm.verts.new(p2 - perp + Vector((0, 0, -0.15 * frac)))
            f = bm_pm.faces.new((v1, v2, v3, v4))
            f.material_index = 1 # 100% Green leaf!

    bm_pm.to_mesh(palm_mesh)
    bm_pm.free()

    for poly in palm_mesh.polygons:
        poly.use_smooth = True

    palm_mesh.materials.append(mat_palm_trunk)
    palm_mesh.materials.append(mat_palm_leaf)

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
        p_obj.rotation_euler = Euler((0, 0, idx * 0.7 + 0.3), 'XYZ')
        p_obj.scale = Vector((1.0, 1.0, random.uniform(0.95, 1.12)))

    # -------------------------------------------------------------
    # 3. REBUILD TAJ MAHAL PALACE WITH ARCHITECTURAL DETAIL
    # -------------------------------------------------------------
    old_taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
    if old_taj:
        bpy.data.objects.remove(old_taj, do_unlink=True)

    taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
    taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
    col_landmarks.objects.link(taj_obj)
    taj_obj.location = Vector((94.17, -163.10, 2.20))

    bm = bmesh.new()

    # Materials setup on mesh
    taj_mesh.materials.append(mat_taj_stone) # 0: Kharodi Basalt
    taj_mesh.materials.append(mat_taj_red)   # 1: Red Dome/Roof Tile
    taj_mesh.materials.append(mat_gold)      # 2: Gold Finial
    taj_mesh.materials.append(mat_tower)     # 3: Tower Concrete
    taj_mesh.materials.append(mat_iron)      # 4: Wrought Iron / Dark Stone

    # BASE & PLINTH
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 2.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 3.0))) @ Matrix.Diagonal(Vector((24.0, 32.0, 6.0, 1.0))))

    # UPPER WINGS (Z = 5.5 to 32.0m)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 18.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 20.0))) @ Matrix.Diagonal(Vector((22.0, 30.0, 28.0, 1.0))))

    # 6 ARCHITECTURAL TIERS OF BALCONIES & FENESTRATION BANDS
    for tier in range(1, 6):
        tz = tier * 5.2 + 2.5
        # Cantilevered stone balcony slab
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.2, 28.0, 0.45, 1.0))))
        # Wrought iron filigree balustrade
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((13.5, 0.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 28.0, 0.9, 1.0))))

        # North Wing balconies
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.2, 36.0, tz))) @ Matrix.Diagonal(Vector((1.8, 11.5, 0.45, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((17.0, 36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 11.5, 0.9, 1.0))))

        # South Wing balconies
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.2, -36.0, tz))) @ Matrix.Diagonal(Vector((1.8, 11.5, 0.45, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((17.0, -36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 11.5, 0.9, 1.0))))

        # Arched window mouldings (horizontal stone cornices)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((12.1, 0.0, tz + 4.2))) @ Matrix.Diagonal(Vector((0.6, 28.5, 0.35, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.0, 36.0, tz + 4.2))) @ Matrix.Diagonal(Vector((0.6, 12.0, 0.35, 1.0))))
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((16.0, -36.0, tz + 4.2))) @ Matrix.Diagonal(Vector((0.6, 12.0, 0.35, 1.0))))

    # PITCHED RED MANGALORE CLAY TILE ROOFS
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 34.0))) @ Matrix.Diagonal(Vector((13.0, 84.0, 4.0, 1.0))))

    # GRAND FLORENTINE POINTED BULBOUS DOME (32 Smooth Segments, Authentic Profile)
    # Drum with arched openings
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=10.5, radius2=10.0, depth=10.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 37.0))))
    # Main bulbous pointed dome
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=10.2, radius2=1.0, depth=21.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 52.5))))
    # Cupola / Lantern atop dome
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=2.2, radius2=1.9, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 65.0))))
    # Slender gilded needle finial
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.6, radius2=0.04, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 70.0))))

    # 4 CORNER MOORISH ONION CHHATRIS
    taj_chhatris = [
        Vector((15.0, 41.5, 32.0)),
        Vector((15.0, -41.5, 32.0)),
        Vector((-21.0, 41.5, 32.0)),
        Vector((-21.0, -41.5, 32.0))
    ]
    for cp in taj_chhatris:
        # Octagonal pavilion base
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=3.0, radius2=2.6, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
        # Pointed onion dome
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24, radius1=2.6, radius2=0.3, depth=5.0, matrix=Matrix.Translation(cp + Vector((0, 0, 6.0))))
        # Brass spire
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=0.25, radius2=0.03, depth=2.8, matrix=Matrix.Translation(cp + Vector((0, 0, 9.0))))

    # TAJ TOWER (1973 Modernist Masterpiece)
    tower_c = Vector((-34.0, -58.0, 0.0))
    # Fluted cylindrical core
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=16.0, radius2=15.8, depth=84.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 42.0))))
    # 22 Tiers of cantilevered circular balconies
    for b_floor in range(1, 23):
        bf_z = b_floor * 3.6 + 2.0
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=17.4, radius2=17.2, depth=0.8, matrix=Matrix.Translation(tower_c + Vector((0, 0, bf_z))))
    # Crown flaring observation deck & roof mechanical plant
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32, radius1=18.5, radius2=12.0, depth=8.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 88.0))))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=3.5, radius2=0.4, depth=6.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 95.0))))

    bm.to_mesh(taj_mesh)
    bm.free()

    # Smooth shading & material assignments
    for poly in taj_mesh.polygons:
        pz = poly.center.z
        px = poly.center.x
        py = poly.center.y
        if pz > 32.0 or px < -20.0:
            poly.use_smooth = True

        if px < -22.0 and py < -45.0:
            poly.material_index = 3 # Taj Tower Concrete
        elif pz > 67.0 and abs(py) < 8.0:
            poly.material_index = 2 # Gold Finial
        elif pz > 41.0 and abs(py) < 14.0 and abs(px) < 14.0:
            poly.material_index = 1 # Red Florentine Dome
        elif pz > 32.0 and px > -15.0:
            poly.material_index = 1 # Red Pitched Roofs
        elif poly.normal.dot(Vector((1, 0, 0))) > 0.8 and pz < 30.0 and px > 13.0:
            poly.material_index = 4 # Wrought Iron Railings
        else:
            poly.material_index = 0 # Kharodi Basalt Facade

    # -------------------------------------------------------------
    # 4. AUTHENTIC MUMBAI KAALI-PEELI TAXIS & BEST BUSES IN PLAZA
    # -------------------------------------------------------------
    # Create Taxi Model (Premier Padmini)
    mat_taxi_black = bpy.data.materials.get("MAT_Taxi_GlossBlack")
    if not mat_taxi_black:
        mat_taxi_black = bpy.data.materials.new("MAT_Taxi_GlossBlack")
        mat_taxi_black.use_nodes = True
        bsdf = mat_taxi_black.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.20

    mat_taxi_yellow = bpy.data.materials.get("MAT_Taxi_CanaryYellow")
    if not mat_taxi_yellow:
        mat_taxi_yellow = bpy.data.materials.new("MAT_Taxi_CanaryYellow")
        mat_taxi_yellow.use_nodes = True
        bsdf = mat_taxi_yellow.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs['Base Color'].default_value = (0.95, 0.75, 0.05, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.25

    taxi_mesh = bpy.data.meshes.new("Taxi_KaaliPeeli_Mesh")
    bm_tx = bmesh.new()
    # Lower Body (Black)
    bmesh.ops.create_cube(bm_tx, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.55))) @ Matrix.Diagonal(Vector((3.8, 1.55, 0.65, 1.0))))
    for f in bm_tx.faces:
        f.material_index = 0
    # Cabin & Roof (Canary Yellow)
    bmesh.ops.create_cube(bm_tx, size=1.0, matrix=Matrix.Translation(Vector((-0.2, 0, 1.10))) @ Matrix.Diagonal(Vector((2.1, 1.45, 0.55, 1.0))))
    # Taxi Meter Light on Roof
    bmesh.ops.create_cube(bm_tx, size=1.0, matrix=Matrix.Translation(Vector((-0.2, 0, 1.45))) @ Matrix.Diagonal(Vector((0.45, 0.25, 0.15, 1.0))))
    for f in bm_tx.faces:
        if f.material_index != 0:
            f.material_index = 1
    bm_tx.to_mesh(taxi_mesh)
    bm_tx.free()
    taxi_mesh.materials.append(mat_taxi_black)
    taxi_mesh.materials.append(mat_taxi_yellow)

    # Clean old taxis
    for o in list(bpy.data.objects):
        if o.name.startswith("TAXI_Apollo_"):
            bpy.data.objects.remove(o, do_unlink=True)

    col_props = bpy.data.collections.get("Playable_Street_Props")
    if not col_props:
        col_props = bpy.data.collections.new("Playable_Street_Props")
        bpy.context.scene.collection.children.link(col_props)

    taxi_locs = [
        (Vector((142.0, -145.0, 2.2)), 1.57),
        (Vector((148.0, -145.0, 2.2)), 1.57),
        (Vector((155.0, -145.0, 2.2)), 1.62),
        (Vector((130.0, -165.0, 2.2)), 0.0),
        (Vector((138.0, -165.0, 2.2)), 0.05),
    ]
    for i, (tl, rot_z) in enumerate(taxi_locs):
        tx_obj = bpy.data.objects.new(f"TAXI_Apollo_{i}", taxi_mesh)
        col_props.objects.link(tx_obj)
        tx_obj.location = tl
        tx_obj.rotation_euler = Euler((0, 0, rot_z), 'XYZ')

    # Save to blend
    bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print(">>> Scanned Apollo Bunder Masterpiece successfully built and saved!")
    with open('/tmp/apollo_sculpt_ok.txt', 'w') as f:
        f.write('DONE')

if __name__ == '__main__':
    build_scanned_apollo()
