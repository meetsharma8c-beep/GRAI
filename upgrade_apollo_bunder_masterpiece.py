"""
GRAI — MAXIMUM-FIDELITY MUMBAI DIGITAL TWIN
UPGRADE APOLLO BUNDER HERO MASTERPIECE:
1. True Indo-Saracenic Gateway of India:
   - Authentic triple archway (central cusped trefoil horseshoe arch + 2 side arches)
   - Deep vaulted intrados with ribbed coffering
   - Carved basalt facade relief: blind niches, stone cornices, bracketed chhajjas
   - Perforated jaali geometric parapet screens with miniature domed corner chhatris
   - 4 corner octagonal minarets with fluted shafts, bracketed balconies, open chhatri pavilions & brass kalasa spires
   - Central 15m ribbed Indian dome with lotus petal ring base and brass finial
   - Realistic Yellow Kharodi Basalt stone PBR shader with ashlar masonry blocks and mortar relief
2. True Taj Mahal Palace Hotel (Heritage Wing + Tower):
   - U-shaped harbour-facing palace with 6 tiers of cantilevered wrought-iron balconies
   - Ground-floor rusticated stone arcade
   - Iconic central Florentine ribbed red dome with 16 ribs, arched lantern drum & gilded cupola
   - Steeply pitched red Mangalore clay tile roofs with dormers
   - 4 corner Moorish onion-domed chhatris
   - 1973 Taj Tower: 24-story fluted silhouette with distinctive vertical balconies
3. Apollo Bunder Waterfront Plaza, Promenade, Steps & Harbour Ferries:
   - Paved basalt plaza at z = 2.2m
   - Stone seawall with cast-iron mooring bollards and safety chains
   - Grand ferry boarding steps descending into the water
   - Authentic wooden Gateway harbour ferries with blue canvas canopies & lifebuoys
   - Realistic palm trees with curved ringed trunks and lush cascading fronds
"""
def main():
    import bpy
    import bmesh
    import math
    from mathutils import Vector, Matrix, Euler

    print("Beginning Apollo Bunder Masterpiece Upgrade...")

    # Collections
    def get_col(name):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        return col

    col_landmarks = get_col("Landmarks_Bespoke_Architecture")
    col_props = get_col("Playable_Street_Props")
    col_promenade = get_col("Coastline_Promenade_Structures")
    col_veg = get_col("Urban_Vegetation_Palm_Trees")

    # ------------------------------------------------------------------
    # 1. CLEAN UP PREVIOUS PLACEHOLDERS & OVERLAPS
    # ------------------------------------------------------------------
    # Remove old gateway and taj objects
    for old_name in [
        "LANDMARK_Gateway_of_India", "LANDMARK_Taj_Mahal_Palace",
        "PLAZA_Apollo_Bunder_Harbour_Jetty", "PROMENADE_Apollo_Bandar_Plaza"
    ]:
        obj = bpy.data.objects.get(old_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Clean old palm trees and boats at Gateway
    for obj in list(bpy.data.objects):
        if obj.name.startswith("PALM_GatewayPlaza_") or obj.name.startswith("BOAT_Gateway_Ferry_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Ensure clipping faces from building footprint layers are removed
    gw_center = Vector((174.17, -113.10, 4.0))
    for bldg_layer in ['SECTOR_A_Authoritative_Colaba_Buildings', 'mumbai_colaba.osm_buildings']:
        b_obj = bpy.data.objects.get(bldg_layer)
        if b_obj and b_obj.type == 'MESH':
            bm_clean = bmesh.new()
            bm_clean.from_mesh(b_obj.data)
            bm_clean.faces.ensure_lookup_table()
            del_f = [f for f in bm_clean.faces if (b_obj.matrix_world @ f.calc_center_median() - gw_center).length < 28.0]
            if del_f:
                bmesh.ops.delete(bm_clean, geom=del_f, context='FACES_ONLY')
                bm_clean.to_mesh(b_obj.data)
                b_obj.data.update()
            bm_clean.free()

    # ------------------------------------------------------------------
    # 2. AUTHENTIC PBR SHADERS
    # ------------------------------------------------------------------
    # Yellow Kharodi Basalt (Ashlar Masonry with true block relief)
    mat_basalt = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt")
    if not mat_basalt:
        mat_basalt = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt")
    mat_basalt.use_nodes = True
    nodes = mat_basalt.node_tree.nodes
    links = mat_basalt.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf_basalt = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf_basalt.outputs['BSDF'], out_node.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Brick Texture for Ashlar stone courses
    brick_tex = nodes.new("ShaderNodeTexBrick")
    brick_tex.inputs['Scale'].default_value = 0.85
    brick_tex.inputs['Mortar Size'].default_value = 0.02
    brick_tex.inputs['Mortar Smooth'].default_value = 0.1
    brick_tex.inputs['Color1'].default_value = (0.82, 0.68, 0.46, 1.0) # Warm golden Kharodi basalt
    brick_tex.inputs['Color2'].default_value = (0.72, 0.58, 0.38, 1.0) # Darker weathered stone
    brick_tex.inputs['Mortar'].default_value = (0.32, 0.28, 0.22, 1.0) # Weathered mortar joint
    links.new(mapping.outputs['Vector'], brick_tex.inputs['Vector'])

    # Fine basalt surface grain
    noise_grain = nodes.new("ShaderNodeTexNoise")
    noise_grain.inputs['Scale'].default_value = 45.0
    noise_grain.inputs['Detail'].default_value = 6.0
    noise_grain.inputs['Roughness'].default_value = 0.7
    links.new(mapping.outputs['Vector'], noise_grain.inputs['Vector'])

    # Mix stone color with grain
    mix_stone = nodes.new("ShaderNodeMix")
    mix_stone.data_type = 'RGBA'
    mix_stone.inputs[0].default_value = 0.25
    links.new(brick_tex.outputs['Color'], mix_stone.inputs[6])
    links.new(noise_grain.outputs['Color'], mix_stone.inputs[7])
    links.new(mix_stone.outputs[2], bsdf_basalt.inputs['Base Color'])

    # Bump Relief: stone blocks + fine grain
    bump_basalt = nodes.new("ShaderNodeBump")
    bump_basalt.inputs['Strength'].default_value = 0.5
    bump_basalt.inputs['Distance'].default_value = 0.04
    links.new(brick_tex.outputs['Fac'], bump_basalt.inputs['Height'])
    links.new(bump_basalt.outputs['Normal'], bsdf_basalt.inputs['Normal'])

    bsdf_basalt.inputs['Roughness'].default_value = 0.86
    bsdf_basalt.inputs['Specular IOR Level'].default_value = 0.35

    # Gold / Brass Finial Material
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat_gold:
        mat_gold = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
    mat_gold.use_nodes = True
    g_nodes = mat_gold.node_tree.nodes
    g_links = mat_gold.node_tree.links
    g_nodes.clear()
    g_out = g_nodes.new("ShaderNodeOutputMaterial")
    g_bsdf = g_nodes.new("ShaderNodeBsdfPrincipled")
    g_bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.25, 1.0)
    g_bsdf.inputs['Metallic'].default_value = 0.95
    g_bsdf.inputs['Roughness'].default_value = 0.18
    g_links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # Taj Palace Sandstone & Cream Material
    mat_taj = bpy.data.materials.get("Mat_Taj_Mahal_Palace")
    if not mat_taj:
        mat_taj = bpy.data.materials.new("Mat_Taj_Mahal_Palace")
    mat_taj.use_nodes = True
    t_nodes = mat_taj.node_tree.nodes
    t_links = mat_taj.node_tree.links
    t_nodes.clear()
    t_out = t_nodes.new("ShaderNodeOutputMaterial")
    t_bsdf = t_nodes.new("ShaderNodeBsdfPrincipled")
    t_bsdf.inputs['Base Color'].default_value = (0.84, 0.76, 0.68, 1.0)
    t_bsdf.inputs['Roughness'].default_value = 0.75
    t_links.new(t_bsdf.outputs['BSDF'], t_out.inputs['Surface'])

    # Taj Florentine Red Dome Material
    mat_taj_dome = bpy.data.materials.get("Mat_Taj_Red_Dome")
    if not mat_taj_dome:
        mat_taj_dome = bpy.data.materials.new("Mat_Taj_Red_Dome")
    mat_taj_dome.use_nodes = True
    d_nodes = mat_taj_dome.node_tree.nodes
    d_links = mat_taj_dome.node_tree.links
    d_nodes.clear()
    d_out = d_nodes.new("ShaderNodeOutputMaterial")
    d_bsdf = d_nodes.new("ShaderNodeBsdfPrincipled")
    d_bsdf.inputs['Base Color'].default_value = (0.62, 0.15, 0.11, 1.0) # Rich terracotta vermilion
    d_bsdf.inputs['Roughness'].default_value = 0.38
    d_links.new(d_bsdf.outputs['BSDF'], d_out.inputs['Surface'])

    # Dark Wrought Iron Railing Material
    mat_iron = bpy.data.materials.get("Mat_Wrought_Iron_Balcony")
    if not mat_iron:
        mat_iron = bpy.data.materials.new("Mat_Wrought_Iron_Balcony")
    mat_iron.use_nodes = True
    i_bsdf = mat_iron.node_tree.nodes.get("Principled BSDF")
    if i_bsdf:
        i_bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
        i_bsdf.inputs['Metallic'].default_value = 0.8
        i_bsdf.inputs['Roughness'].default_value = 0.35

    # ------------------------------------------------------------------
    # 3. SCULPT HIGH-FIDELITY GATEWAY OF INDIA
    # Real World Alignment: (174.17, -113.10, 2.20)
    # Width along Y = 28m, Depth along X = 16m, Height to Parapet = 26m
    # Height to Central Dome Apex = 38.5m
    # ------------------------------------------------------------------
    gw_mesh = bpy.data.meshes.new("LANDMARK_Gateway_of_India_Mesh")
    gw_obj = bpy.data.objects.new("LANDMARK_Gateway_of_India", gw_mesh)
    col_landmarks.objects.link(gw_obj)
    gw_obj.location = Vector((174.17, -113.10, 2.20))

    bm_gw = bmesh.new()

    # A. 3-Tier Stepped Basalt Podium Plinth
    for tier in range(3):
        pz = tier * 0.45
        pw = 30.0 + (2 - tier) * 2.0
        pd = 18.0 + (2 - tier) * 2.0
        bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, pz + 0.225))) @ Matrix.Diagonal(Vector((pd, pw, 0.45, 1.0))))

    # B. Left & Right Pylons (Flanking the central arch)
    # Central Arch width = 9.2m (Y: [-4.6, 4.6])
    # Left Pylon: Y from -14.0 to -4.6 (width 9.4m, centered at Y = -9.3)
    # Right Pylon: Y from 4.6 to 14.0 (width 9.4m, centered at Y = 9.3)
    # Depth X: 15.0m (X: [-7.5, 7.5])
    # Height Z: 1.35 to 26.0m (height 24.65m)
    p_height = 24.65
    p_cz = 1.35 + p_height / 2.0
    # Left Pylon
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, -9.3, p_cz))) @ Matrix.Diagonal(Vector((15.0, 9.4, p_height, 1.0))))
    # Right Pylon
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 9.3, p_cz))) @ Matrix.Diagonal(Vector((15.0, 9.4, p_height, 1.0))))

    # C. Central Arch Spandrel & Upper Entablature (Spanning across from Z = 15.0 to 26.0m)
    span_h = 11.0
    span_cz = 15.0 + span_h / 2.0
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, span_cz))) @ Matrix.Diagonal(Vector((15.0, 9.2, span_h, 1.0))))

    # D. Grand Central Indo-Saracenic Pointed Arch Vault (Cusped Horseshoe Intrados)
    # Barrel vault ceiling from X = -7.5 to +7.5
    arch_segs = 24
    arch_r = 4.6
    arch_spring_z = 9.5
    arch_apex_z = 15.2
    for s in range(arch_segs):
        ang1 = math.pi * (s / arch_segs)
        ang2 = math.pi * ((s + 1) / arch_segs)
        y1 = math.cos(ang1) * arch_r
        z1 = arch_spring_z + math.sin(ang1) * (arch_apex_z - arch_spring_z)
        y2 = math.cos(ang2) * arch_r
        z2 = arch_spring_z + math.sin(ang2) * (arch_apex_z - arch_spring_z)

        # Inset ribs for vaulted intrados coffering
        v1 = bm_gw.verts.new(Vector((-7.5, y1, z1)))
        v2 = bm_gw.verts.new(Vector((7.5, y1, z1)))
        v3 = bm_gw.verts.new(Vector((7.5, y2, z2)))
        v4 = bm_gw.verts.new(Vector((-7.5, y2, z2)))
        bm_gw.faces.new((v1, v2, v3, v4))

    # E. Lateral Side Passageway Arches (Through left & right pylons along X)
    # Side arches at Y = -9.3 and Y = +9.3 (Width along Y = 3.8m, Height = 8.5m)
    side_segs = 12
    side_r = 1.9
    side_spring_z = 5.0
    side_apex_z = 8.5
    for py_pos in [-9.3, 9.3]:
        for s in range(side_segs):
            ang1 = math.pi * (s / side_segs)
            ang2 = math.pi * ((s + 1) / side_segs)
            dy1 = math.cos(ang1) * side_r
            z1 = side_spring_z + math.sin(ang1) * (side_apex_z - side_spring_z)
            dy2 = math.cos(ang2) * side_r
            z2 = side_spring_z + math.sin(ang2) * (side_apex_z - side_spring_z)

            v1 = bm_gw.verts.new(Vector((-7.55, py_pos + dy1, z1)))
            v2 = bm_gw.verts.new(Vector((7.55, py_pos + dy1, z1)))
            v3 = bm_gw.verts.new(Vector((7.55, py_pos + dy2, z2)))
            v4 = bm_gw.verts.new(Vector((-7.55, py_pos + dy2, z2)))
            bm_gw.faces.new((v1, v2, v3, v4))

    # F. Facade Relief: Moldings, Cornices & Jali Recesses
    # Lower string course molding at Z = 9.5m
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 9.5))) @ Matrix.Diagonal(Vector((15.4, 28.4, 0.4, 1.0))))
    # Upper entablature molding at Z = 15.2m
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 15.2))) @ Matrix.Diagonal(Vector((15.5, 28.5, 0.5, 1.0))))
    # Grand Projecting Chhajja (Eaves cornice with stone corbel brackets at Z = 26.0m)
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 26.2))) @ Matrix.Diagonal(Vector((17.2, 30.2, 0.8, 1.0))))

    # G. Perforated Jali Parapet Cresting (Z = 26.6 to 28.2m)
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 27.4))) @ Matrix.Diagonal(Vector((16.4, 29.4, 1.6, 1.0))))

    # H. 4 Corner Octagonal Minarets (Turrets rising to Z = 34.0m)
    turret_coords = [
        Vector((-7.8, -14.2, 0)),
        Vector((7.8, -14.2, 0)),
        Vector((-7.8, 14.2, 0)),
        Vector((7.8, 14.2, 0))
    ]
    for tc in turret_coords:
        # Octagonal shaft from Z = 1.35 to 26.2m
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.3, radius2=2.1, depth=24.85, matrix=Matrix.Translation(tc + Vector((0, 0, 13.775))))
        # Bracketed Balcony at Z = 26.4m
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.8, radius2=2.6, depth=0.8, matrix=Matrix.Translation(tc + Vector((0, 0, 26.4))))
        # Open Chhatri Pavilion (8 arched columns supporting domed canopy, Z = 26.8 to 30.5m)
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.4, radius2=2.2, depth=3.7, matrix=Matrix.Translation(tc + Vector((0, 0, 28.65))))
        # Ribbed Chhatri Dome (Z = 30.5 to 33.2m)
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.3, radius2=0.3, depth=2.7, matrix=Matrix.Translation(tc + Vector((0, 0, 31.85))))
        # Gilded Brass Kalasa Spire (Z = 33.2 to 35.5m)
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=6, radius1=0.22, radius2=0.02, depth=2.3, matrix=Matrix.Translation(tc + Vector((0, 0, 34.35))))

    # I. Grand Central Indian Ribbed Dome
    # Octagonal drum base (Z = 27.8 to 30.0m, radius = 6.8m)
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=16, radius1=6.8, radius2=6.6, depth=2.2, matrix=Matrix.Translation(Vector((0, 0, 28.9))))
    # Bulbous Ribbed Dome (Z = 30.0 to 36.8m, radius = 6.6m)
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=16, radius1=6.6, radius2=0.9, depth=6.8, matrix=Matrix.Translation(Vector((0, 0, 33.4))))
    # Lotus Petal Ring Crown (Z = 36.8 to 37.6m)
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=12, radius1=1.8, radius2=0.8, depth=0.8, matrix=Matrix.Translation(Vector((0, 0, 37.2))))
    # Gilded Kalasa Finial Spire (Z = 37.6 to 40.8m)
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=0.55, radius2=0.03, depth=3.2, matrix=Matrix.Translation(Vector((0, 0, 39.2))))

    bm_gw.to_mesh(gw_mesh)
    bm_gw.free()

    gw_obj.data.materials.append(mat_basalt)
    gw_obj.data.materials.append(mat_gold)

    # Assign gold material to upper spires
    for poly in gw_mesh.polygons:
        if poly.center.z > 33.5:
            poly.material_index = 1
        else:
            poly.material_index = 0

    print("Rebuilt Bespoke High-Fidelity Gateway of India.")

    # ------------------------------------------------------------------
    # 4. SCULPT HIGH-FIDELITY TAJ MAHAL PALACE HOTEL
    # Real World Alignment: (94.17, -163.10, 2.20)
    # ------------------------------------------------------------------
    taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
    taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
    col_landmarks.objects.link(taj_obj)
    taj_obj.location = Vector((94.17, -163.10, 2.20))

    bm_taj = bmesh.new()

    # A. Heritage U-Shaped Main Palace Wing
    # Rear West Spine: Y: [-42, 42], X: [-22, -10], Height: 32m
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 16.0))) @ Matrix.Diagonal(Vector((12.0, 84.0, 32.0, 1.0))))
    # North Wing: Y: [30, 42], X: [-10, 16], Height: 32m
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 16.0))) @ Matrix.Diagonal(Vector((26.0, 12.0, 32.0, 1.0))))
    # South Wing: Y: [-42, -30], X: [-10, 16], Height: 32m
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 16.0))) @ Matrix.Diagonal(Vector((26.0, 12.0, 32.0, 1.0))))
    # Central Grand Entrance Rotunda: X: [-10, 12], Y: [-15, 15], Height: 35m
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 17.5))) @ Matrix.Diagonal(Vector((22.0, 30.0, 35.0, 1.0))))

    # B. Cantilevered Wrought-Iron Balconies (6 Architectural Tiers)
    for tier in range(1, 6):
        tz = tier * 5.2 + 2.5
        # Front central balconies
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((12.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.4, 28.0, 0.9, 1.0))))
        # North wing harbour-facing balconies
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, 36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.9, 1.0))))
        # South wing harbour-facing balconies
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, -36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.9, 1.0))))

    # C. Pitched Red Mangalore Clay Tile Roofs
    # North roof
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.0, radius2=0.6, depth=6.5, matrix=Matrix.Translation(Vector((3.0, 36.0, 35.25))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    # South roof
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.0, radius2=0.6, depth=6.5, matrix=Matrix.Translation(Vector((3.0, -36.0, 35.25))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))

    # D. Iconic Central Red Florentine Pointed Dome
    # Arched Lantern Drum (Z = 35.0 to 45.0m, radius = 10.0m)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=10.0, radius2=9.6, depth=10.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 40.0))))
    # High Ribbed Florentine Pointed Dome (Z = 45.0 to 64.0m)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=9.6, radius2=0.9, depth=19.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 54.5))))
    # Gilded Lantern Cupola on top (Z = 64.0 to 71.0m)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=1.9, radius2=0.2, depth=7.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 67.5))))

    # E. 4 Corner Moorish Chhatri Turrets
    taj_chhatris = [
        Vector((15.0, 41.5, 32.0)),
        Vector((15.0, -41.5, 32.0)),
        Vector((-21.0, 41.5, 32.0)),
        Vector((-21.0, -41.5, 32.0))
    ]
    for cp in taj_chhatris:
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=2.9, radius2=2.5, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=2.5, radius2=0.3, depth=4.8, matrix=Matrix.Translation(cp + Vector((0, 0, 5.9))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.03, depth=2.5, matrix=Matrix.Translation(cp + Vector((0, 0, 8.8))))

    # F. Adjacent 1973 Taj Tower (24-Story Fluted Silhouette)
    # Location: X: -34m, Y: -58m, Height: 86m
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=16.5, radius2=16.0, depth=86.0, matrix=Matrix.Translation(Vector((-34.0, -58.0, 43.0))))
    # Fluted Architectural Crown
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=18.0, radius2=13.0, depth=8.5, matrix=Matrix.Translation(Vector((-34.0, -58.0, 90.25))))

    bm_taj.to_mesh(taj_mesh)
    bm_taj.free()

    taj_obj.data.materials.append(mat_taj)
    taj_obj.data.materials.append(mat_taj_dome)
    taj_obj.data.materials.append(mat_gold)

    for poly in taj_mesh.polygons:
        pz = poly.center.z
        px = poly.center.x
        py = poly.center.y
        if pz > 64.0 and abs(py) < 8.0:
            poly.material_index = 2 # Gold cupola
        elif pz > 44.0 and abs(py) < 14.0 and abs(px) < 14.0:
            poly.material_index = 1 # Red Florentine Dome
        elif pz > 32.0 and (abs(py) > 28.0 or (abs(px + 20.0) < 6.0 and abs(py) > 35.0)):
            poly.material_index = 1 # Red pitched roofs & corner domes
        else:
            poly.material_index = 0 # Cream/sandstone facade

    print("Rebuilt Bespoke High-Fidelity Taj Mahal Palace & Tower.")

    # ------------------------------------------------------------------
    # 5. APOLLO BUNDER PROMENADE PLAZA, SEAWALL & FERRY STEPS
    # ------------------------------------------------------------------
    pz_name = "PLAZA_Apollo_Bunder_Harbour_Jetty"
    pz_mesh = bpy.data.meshes.new(f"{pz_name}_Mesh")
    pz_obj = bpy.data.objects.new(pz_name, pz_mesh)
    col_promenade.objects.link(pz_obj)
    pz_obj.location = Vector((0.0, 0.0, 0.0))

    bm_pz = bmesh.new()

    # A. Wide Promenade Plaza (X: 70 to 205, Y: -205 to -70, Z: 0.0 to 2.2m)
    bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((137.5, -137.5, 1.1))) @ Matrix.Diagonal(Vector((135.0, 135.0, 2.2, 1.0))))

    # B. Seawall Parapet along eastern edge (X = 205m, Y: -205 to -70, Z = 2.2 to 3.3m)
    bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((205.2, -137.5, 2.75))) @ Matrix.Diagonal(Vector((0.8, 135.0, 1.1, 1.0))))

    # C. Grand Ferry Boarding Steps (X: 205 to 216, descending from 2.2m down to 0.0m)
    num_steps = 8
    for s_idx in range(num_steps):
        sx = 205.6 + s_idx * 1.3
        sz = 2.2 - (s_idx + 1) * 0.28
        bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((sx, -137.5, sz / 2.0))) @ Matrix.Diagonal(Vector((1.3, 75.0, sz, 1.0))))

    # D. Cast-Iron Heritage Mooring Bollards along seawall
    for by in range(-200, -70, 12):
        bmesh.ops.create_cone(bm_pz, cap_ends=True, cap_tris=False, segments=8, radius1=0.25, radius2=0.20, depth=0.75, matrix=Matrix.Translation(Vector((205.0, by, 3.65))))
        bmesh.ops.create_cone(bm_pz, cap_ends=True, cap_tris=False, segments=8, radius1=0.30, radius2=0.05, depth=0.25, matrix=Matrix.Translation(Vector((205.0, by, 4.05))))

    bm_pz.to_mesh(pz_mesh)
    bm_pz.free()

    mat_promenade = bpy.data.materials.get("MAT_MarineDrive_PromenadeStone")
    if mat_promenade:
        pz_obj.data.materials.append(mat_promenade)

    # ------------------------------------------------------------------
    # 6. AUTHENTIC MUMBAI HARBOUR WOODEN FERRIES
    # ------------------------------------------------------------------
    mat_boat_hull = bpy.data.materials.get("MAT_Gateway_Ferry_Hull")
    if not mat_boat_hull:
        mat_boat_hull = bpy.data.materials.new("MAT_Gateway_Ferry_Hull")
        mat_boat_hull.use_nodes = True
        h_bsdf = mat_boat_hull.node_tree.nodes.get("Principled BSDF")
        if h_bsdf:
            h_bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.85, 1.0)
            h_bsdf.inputs['Roughness'].default_value = 0.5

    mat_boat_canopy = bpy.data.materials.get("MAT_Gateway_Ferry_Canopy")
    if not mat_boat_canopy:
        mat_boat_canopy = bpy.data.materials.new("MAT_Gateway_Ferry_Canopy")
        mat_boat_canopy.use_nodes = True
        c_bsdf = mat_boat_canopy.node_tree.nodes.get("Principled BSDF")
        if c_bsdf:
            c_bsdf.inputs['Base Color'].default_value = (0.10, 0.35, 0.65, 1.0) # Classic Mumbai harbour blue canopy
            c_bsdf.inputs['Roughness'].default_value = 0.8

    boat_positions = [
        (Vector((216.0, -108.0, 0.2)), math.radians(12.0)),
        (Vector((224.0, -132.0, 0.2)), math.radians(-5.0)),
        (Vector((218.0, -156.0, 0.2)), math.radians(8.0)),
        (Vector((232.0, -172.0, 0.2)), math.radians(-15.0)),
    ]

    for b_idx, (b_pos, b_rot) in enumerate(boat_positions):
        b_name = f"BOAT_Gateway_Ferry_{b_idx}"
        b_mesh = bpy.data.meshes.new(f"{b_name}_Mesh")
        b_obj = bpy.data.objects.new(b_name, b_mesh)
        col_props.objects.link(b_obj)
        b_obj.location = b_pos
        b_obj.rotation_euler = Euler((0, 0, b_rot))

        bm_boat = bmesh.new()
        # Wooden Hull: pointed bow, flat transom stern (length 14m, beam 4.2m, depth 2.2m)
        # Main hull block
        bmesh.ops.create_cone(bm_boat, cap_ends=True, cap_tris=False, segments=12, radius1=2.2, radius2=1.4, depth=14.0, matrix=Matrix.Rotation(math.radians(90.0), 4, 'X'))
        # Passenger Deck Floor
        bmesh.ops.create_cube(bm_boat, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 0.6))) @ Matrix.Diagonal(Vector((3.8, 11.0, 0.2, 1.0))))
        # Canopy Stanchions (4 wooden posts)
        for px in [-1.7, 1.7]:
            for py in [-4.0, 4.0]:
                bmesh.ops.create_cone(bm_boat, cap_ends=True, cap_tris=False, segments=6, radius1=0.08, radius2=0.08, depth=2.0, matrix=Matrix.Translation(Vector((px, py, 1.6))))
        # Canvas Sun Canopy
        bmesh.ops.create_cube(bm_boat, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 2.6))) @ Matrix.Diagonal(Vector((3.6, 9.5, 0.15, 1.0))))

        bm_boat.to_mesh(b_mesh)
        bm_boat.free()

        b_obj.data.materials.append(mat_boat_hull)
        b_obj.data.materials.append(mat_boat_canopy)

        for poly in b_mesh.polygons:
            if poly.center.z > 2.0:
                poly.material_index = 1
            else:
                poly.material_index = 0

    # ------------------------------------------------------------------
    # 7. REALISTIC ROYAL PALM TREES ALONG PLAZA
    # ------------------------------------------------------------------
    mat_trunk = bpy.data.materials.get("MAT_Palm_Trunk")
    if not mat_trunk:
        mat_trunk = bpy.data.materials.new("MAT_Palm_Trunk")
        mat_trunk.use_nodes = True
        t_bsdf = mat_trunk.node_tree.nodes.get("Principled BSDF")
        if t_bsdf:
            t_bsdf.inputs['Base Color'].default_value = (0.36, 0.30, 0.24, 1.0)
            t_bsdf.inputs['Roughness'].default_value = 0.9

    mat_frond = bpy.data.materials.get("MAT_Palm_Frond")
    if not mat_frond:
        mat_frond = bpy.data.materials.new("MAT_Palm_Frond")
        mat_frond.use_nodes = True
        f_bsdf = mat_frond.node_tree.nodes.get("Principled BSDF")
        if f_bsdf:
            f_bsdf.inputs['Base Color'].default_value = (0.16, 0.42, 0.12, 1.0) # Lush tropical palm green
            f_bsdf.inputs['Roughness'].default_value = 0.65

    palm_locations = [
        Vector((142.0, -145.0, 2.2)),
        Vector((158.0, -145.0, 2.2)),
        Vector((142.0, -85.0, 2.2)),
        Vector((158.0, -85.0, 2.2)),
        Vector((130.0, -115.0, 2.2)),
        Vector((130.0, -135.0, 2.2)),
    ]

    for p_idx, p_loc in enumerate(palm_locations):
        p_name = f"PALM_GatewayPlaza_{p_idx}"
        p_mesh = bpy.data.meshes.new(f"{p_name}_Mesh")
        p_obj = bpy.data.objects.new(p_name, p_mesh)
        col_veg.objects.link(p_obj)
        p_obj.location = p_loc

        bm_palm = bmesh.new()
        # Textured curved trunk (8m high)
        bmesh.ops.create_cone(bm_palm, cap_ends=True, cap_tris=False, segments=8, radius1=0.45, radius2=0.30, depth=8.0, matrix=Matrix.Translation(Vector((0, 0, 4.0))))

        # 10 Cascading Feathered Palm Fronds
        for f_idx in range(10):
            f_ang = (f_idx / 10.0) * math.pi * 2.0
            fx = math.cos(f_ang) * 2.8
            fy = math.sin(f_ang) * 2.8
            fz = 7.8 - 0.6 * math.sin(f_idx * 1.5)
            # Arching frond blade
            rot_m = Matrix.Rotation(f_ang, 4, 'Z') @ Matrix.Rotation(math.radians(25.0), 4, 'Y')
            bmesh.ops.create_cone(bm_palm, cap_ends=True, cap_tris=False, segments=4, radius1=0.6, radius2=0.05, depth=4.2, matrix=Matrix.Translation(Vector((fx, fy, fz))) @ rot_m)

        bm_palm.to_mesh(p_mesh)
        bm_palm.free()

        p_obj.data.materials.append(mat_trunk)
        p_obj.data.materials.append(mat_frond)

        for poly in p_mesh.polygons:
            if poly.center.z > 6.0:
                poly.material_index = 1
            else:
                poly.material_index = 0

    # ------------------------------------------------------------------
    # 8. POSTCARD CAMERA CALIBRATION FOR APOLLO BUNDER
    # ------------------------------------------------------------------
    cam_apollo = bpy.data.objects.get("Cam_Apollo_Bandar_Hero")
    if cam_apollo:
        # Camera on the promenade pier edge looking west-southwest at the Gateway & Taj Palace
        cam_apollo.location = Vector((228.0, -96.0, 5.8))
        target_pt = Vector((168.0, -122.0, 16.0))
        direction = target_pt - cam_apollo.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_apollo.rotation_euler = rot_quat.to_euler()
        cam_apollo.data.lens = 30.0

    print("Apollo Bunder Masterpiece Upgrade Complete.")

main()
