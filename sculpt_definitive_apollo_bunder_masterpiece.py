"""
GRAI — DEFINITIVE SCANNED DETAILING MASTER FOR APOLLO BUNDER
"""

def main():
    import bpy
    import bmesh
    import math
    from mathutils import Vector, Matrix, Euler

    print("Executing Scanned Detailing Master for Apollo Bunder...")

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
    col_tetrapods = get_col("Coastline_Marine_Tetrapods")

    # ==================================================================
    # 1. REMOVE OLD OBJECTS TO REBUILD
    # ==================================================================
    for name in ["LANDMARK_Gateway_of_India", "LANDMARK_Taj_Mahal_Palace", "PLAZA_Apollo_Bunder_Harbour_Jetty"]:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    for o in list(bpy.data.objects):
        if (o.name.startswith("PALM_GatewayPlaza_") or 
            o.name.startswith("BOAT_Gateway_Ferry_") or
            o.name.startswith("TAXI_Apollo_") or
            o.name.startswith("TETRA_Apollo_")):
            bpy.data.objects.remove(o, do_unlink=True)

    # ==================================================================
    # 2. DEFINITIVE PBR MATERIALS
    # ==================================================================
    # A. Yellow Kharodi Basalt (Gateway of India)
    mat_basalt = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt")
    if not mat_basalt:
        mat_basalt = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt")
    mat_basalt.use_nodes = True
    nb = mat_basalt.node_tree.nodes
    lb = mat_basalt.node_tree.links
    nb.clear()
    out_b = nb.new("ShaderNodeOutputMaterial")
    bsdf_b = nb.new("ShaderNodeBsdfPrincipled")
    lb.new(bsdf_b.outputs['BSDF'], out_b.inputs['Surface'])

    tc_b = nb.new("ShaderNodeTexCoord")
    map_b = nb.new("ShaderNodeMapping")
    map_b.inputs['Scale'].default_value = (6.0, 6.0, 6.0)
    lb.new(tc_b.outputs['UV'], map_b.inputs['Vector'])

    brick_b = nb.new("ShaderNodeTexBrick")
    brick_b.inputs['Scale'].default_value = 1.0
    brick_b.inputs['Mortar Size'].default_value = 0.025
    brick_b.inputs['Mortar Smooth'].default_value = 0.05
    brick_b.inputs['Brick Width'].default_value = 0.65
    brick_b.inputs['Row Height'].default_value = 0.35
    brick_b.inputs['Color1'].default_value = (0.86, 0.73, 0.48, 1.0) # Golden Kharodi basalt
    brick_b.inputs['Color2'].default_value = (0.76, 0.62, 0.40, 1.0) # Weathered basalt
    brick_b.inputs['Mortar'].default_value = (0.38, 0.32, 0.24, 1.0) # Lime mortar joint
    lb.new(map_b.outputs['Vector'], brick_b.inputs['Vector'])

    noise_b = nb.new("ShaderNodeTexNoise")
    noise_b.inputs['Scale'].default_value = 30.0
    noise_b.inputs['Detail'].default_value = 4.0
    lb.new(map_b.outputs['Vector'], noise_b.inputs['Vector'])

    mix_b = nb.new("ShaderNodeMix")
    mix_b.data_type = 'RGBA'
    mix_b.inputs[0].default_value = 0.20
    lb.new(brick_b.outputs['Color'], mix_b.inputs[6])
    lb.new(noise_b.outputs['Color'], mix_b.inputs[7])
    lb.new(mix_b.outputs[2], bsdf_b.inputs['Base Color'])

    bump_b = nb.new("ShaderNodeBump")
    bump_b.inputs['Strength'].default_value = 0.40
    bump_b.inputs['Distance'].default_value = 0.02
    lb.new(brick_b.outputs['Fac'], bump_b.inputs['Height'])
    lb.new(bump_b.outputs['Normal'], bsdf_b.inputs['Normal'])
    bsdf_b.inputs['Roughness'].default_value = 0.80

    # B. Heritage Gold Finial
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat_gold:
        mat_gold = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
    mat_gold.use_nodes = True
    g_bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.95, 0.82, 0.25, 1.0)
        g_bsdf.inputs['Metallic'].default_value = 0.95
        g_bsdf.inputs['Roughness'].default_value = 0.18

    # C. Taj Mahal Palace Kurla Stone Facade (WARM BUFF STONE + WINDOW GRID)
    mat_taj_facade = bpy.data.materials.get("Mat_Taj_Mahal_Facade_Detailed")
    if not mat_taj_facade:
        mat_taj_facade = bpy.data.materials.new("Mat_Taj_Mahal_Facade_Detailed")
    mat_taj_facade.use_nodes = True
    nt = mat_taj_facade.node_tree.nodes
    lt = mat_taj_facade.node_tree.links
    nt.clear()
    out_t = nt.new("ShaderNodeOutputMaterial")
    bsdf_t = nt.new("ShaderNodeBsdfPrincipled")
    lt.new(bsdf_t.outputs['BSDF'], out_t.inputs['Surface'])

    tc_t = nt.new("ShaderNodeTexCoord")
    map_t = nt.new("ShaderNodeMapping")
    map_t.inputs['Scale'].default_value = (1.5, 1.5, 1.5)
    lt.new(tc_t.outputs['UV'], map_t.inputs['Vector'])

    brick_t = nt.new("ShaderNodeTexBrick")
    brick_t.inputs['Scale'].default_value = 1.0
    brick_t.inputs['Mortar Size'].default_value = 0.22 # WIDE WALL PIER BETWEEN WINDOWS
    brick_t.inputs['Mortar Smooth'].default_value = 0.04
    brick_t.inputs['Brick Width'].default_value = 0.45
    brick_t.inputs['Row Height'].default_value = 0.65
    brick_t.inputs['Color1'].default_value = (0.08, 0.12, 0.16, 1.0) # Dark reflective window glass
    brick_t.inputs['Color2'].default_value = (0.10, 0.14, 0.18, 1.0) # Glass reflection
    brick_t.inputs['Mortar'].default_value = (0.88, 0.82, 0.74, 1.0) # Warm buff Kurla sandstone wall
    lt.new(map_t.outputs['Vector'], brick_t.inputs['Vector'])
    lt.new(brick_t.outputs['Color'], bsdf_t.inputs['Base Color'])

    mix_r = nt.new("ShaderNodeMix")
    mix_r.data_type = 'FLOAT'
    mix_r.inputs[2].default_value = 0.12 # Glass roughness (shiny)
    mix_r.inputs[3].default_value = 0.78 # Stone roughness (matte)
    lt.new(brick_t.outputs['Fac'], mix_r.inputs[0])
    lt.new(mix_r.outputs[0], bsdf_t.inputs['Roughness'])

    # D. Taj Red Tile & Florentine Dome
    mat_taj_red = bpy.data.materials.get("Mat_Taj_Red_Dome_Tile")
    if not mat_taj_red:
        mat_taj_red = bpy.data.materials.new("Mat_Taj_Red_Dome_Tile")
    mat_taj_red.use_nodes = True
    nr = mat_taj_red.node_tree.nodes
    lr = mat_taj_red.node_tree.links
    nr.clear()
    out_r = nr.new("ShaderNodeOutputMaterial")
    bsdf_r = nr.new("ShaderNodeBsdfPrincipled")
    lr.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])
    bsdf_r.inputs['Base Color'].default_value = (0.68, 0.20, 0.14, 1.0) # Rich vermilion red tile
    bsdf_r.inputs['Roughness'].default_value = 0.40

    # E. Wrought Iron Balustrades / Railings (Jali)
    mat_iron = bpy.data.materials.get("Mat_Wrought_Iron_Railing")
    if not mat_iron:
        mat_iron = bpy.data.materials.new("Mat_Wrought_Iron_Railing")
    mat_iron.use_nodes = True
    i_bsdf = mat_iron.node_tree.nodes.get("Principled BSDF")
    if i_bsdf:
        i_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        i_bsdf.inputs['Metallic'].default_value = 0.90
        i_bsdf.inputs['Roughness'].default_value = 0.35

    # F. Taj Tower Fluted Cream Concrete
    mat_tower = bpy.data.materials.get("Mat_Taj_Tower_Concrete")
    if not mat_tower:
        mat_tower = bpy.data.materials.new("Mat_Taj_Tower_Concrete")
    mat_tower.use_nodes = True
    tw_bsdf = mat_tower.node_tree.nodes.get("Principled BSDF")
    if tw_bsdf:
        tw_bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 0.86, 1.0)
        tw_bsdf.inputs['Roughness'].default_value = 0.55

    # G. Marine Concrete Tetrapod with Wet Moss Staining
    mat_tetrapod = bpy.data.materials.get("MAT_Concrete_Tetrapod_Marine")
    if not mat_tetrapod:
        mat_tetrapod = bpy.data.materials.new("MAT_Concrete_Tetrapod_Marine")
    mat_tetrapod.use_nodes = True
    ntp = mat_tetrapod.node_tree.nodes
    ltp = mat_tetrapod.node_tree.links
    ntp.clear()
    out_tp = ntp.new("ShaderNodeOutputMaterial")
    bsdf_tp = ntp.new("ShaderNodeBsdfPrincipled")
    ltp.new(bsdf_tp.outputs['BSDF'], out_tp.inputs['Surface'])

    tc_tp = ntp.new("ShaderNodeTexCoord")
    noise_tp = ntp.new("ShaderNodeTexNoise")
    noise_tp.inputs['Scale'].default_value = 10.0
    noise_tp.inputs['Detail'].default_value = 4.0
    ltp.new(tc_tp.outputs['Object'], noise_tp.inputs['Vector'])

    ramp_tp = ntp.new("ShaderNodeValToRGB")
    ramp_tp.color_ramp.elements[0].position = 0.30
    ramp_tp.color_ramp.elements[0].color = (0.12, 0.18, 0.10, 1.0) # Dark green wet algae
    ramp_tp.color_ramp.elements[1].position = 0.65
    ramp_tp.color_ramp.elements[1].color = (0.48, 0.48, 0.46, 1.0) # Weathered marine concrete
    ltp.new(noise_tp.outputs['Fac'], ramp_tp.inputs['Fac'])
    ltp.new(ramp_tp.outputs['Color'], bsdf_tp.inputs['Base Color'])

    bump_tp = ntp.new("ShaderNodeBump")
    bump_tp.inputs['Strength'].default_value = 0.40
    bump_tp.inputs['Distance'].default_value = 0.04
    ltp.new(noise_tp.outputs['Fac'], bump_tp.inputs['Height'])
    ltp.new(bump_tp.outputs['Normal'], bsdf_tp.inputs['Normal'])
    bsdf_tp.inputs['Roughness'].default_value = 0.75

    # H. Paved Esplanade Plaza Flagstone Material
    mat_plaza = bpy.data.materials.get("MAT_Plaza_Basalt_Flagstone")
    if not mat_plaza:
        mat_plaza = bpy.data.materials.new("MAT_Plaza_Basalt_Flagstone")
    mat_plaza.use_nodes = True
    npz = mat_plaza.node_tree.nodes
    lpz = mat_plaza.node_tree.links
    npz.clear()
    out_pz = npz.new("ShaderNodeOutputMaterial")
    bsdf_pz = npz.new("ShaderNodeBsdfPrincipled")
    lpz.new(bsdf_pz.outputs['BSDF'], out_pz.inputs['Surface'])

    tc_pz = npz.new("ShaderNodeTexCoord")
    map_pz = npz.new("ShaderNodeMapping")
    map_pz.inputs['Scale'].default_value = (20.0, 20.0, 1.0)
    lpz.new(tc_pz.outputs['Object'], map_pz.inputs['Vector'])

    brick_pz = npz.new("ShaderNodeTexBrick")
    brick_pz.inputs['Scale'].default_value = 1.0
    brick_pz.inputs['Mortar Size'].default_value = 0.015
    brick_pz.inputs['Mortar Smooth'].default_value = 0.05
    brick_pz.inputs['Brick Width'].default_value = 0.50
    brick_pz.inputs['Row Height'].default_value = 0.50
    brick_pz.inputs['Color1'].default_value = (0.42, 0.40, 0.38, 1.0)
    brick_pz.inputs['Color2'].default_value = (0.48, 0.44, 0.40, 1.0)
    brick_pz.inputs['Mortar'].default_value = (0.22, 0.20, 0.18, 1.0)
    lpz.new(map_pz.outputs['Vector'], brick_pz.inputs['Vector'])

    noise_pz = npz.new("ShaderNodeTexNoise")
    noise_pz.inputs['Scale'].default_value = 40.0
    noise_pz.inputs['Detail'].default_value = 4.0
    lpz.new(map_pz.outputs['Vector'], noise_pz.inputs['Vector'])

    mix_pz = npz.new("ShaderNodeMix")
    mix_pz.data_type = 'RGBA'
    mix_pz.inputs[0].default_value = 0.15
    lpz.new(brick_pz.outputs['Color'], mix_pz.inputs[6])
    lpz.new(noise_pz.outputs['Color'], mix_pz.inputs[7])
    lpz.new(mix_pz.outputs[2], bsdf_pz.inputs['Base Color'])

    bump_pz = npz.new("ShaderNodeBump")
    bump_pz.inputs['Strength'].default_value = 0.35
    bump_pz.inputs['Distance'].default_value = 0.02
    lpz.new(brick_pz.outputs['Fac'], bump_pz.inputs['Height'])
    lpz.new(bump_pz.outputs['Normal'], bsdf_pz.inputs['Normal'])
    bsdf_pz.inputs['Roughness'].default_value = 0.65

    # ==================================================================
    # 3. SCULPT BESPOKE GATEWAY OF INDIA
    # ==================================================================
    gw_mesh = bpy.data.meshes.new("LANDMARK_Gateway_of_India_Mesh")
    gw_obj = bpy.data.objects.new("LANDMARK_Gateway_of_India", gw_mesh)
    col_landmarks.objects.link(gw_obj)
    gw_obj.location = Vector((174.17, -113.10, 2.20))

    bm_gw = bmesh.new()

    # 1. 3-Tier Stepped Basalt Plinth
    for tier in range(3):
        pz = tier * 0.45
        pw = 32.0 + (2 - tier) * 2.0
        pd = 20.0 + (2 - tier) * 2.0
        bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, pz + 0.225))) @ Matrix.Diagonal(Vector((pd, pw, 0.45, 1.0))))

    # 2. Main Flanking Pylons (Left & Right)
    p_height = 24.65
    p_cz = 1.35 + p_height / 2.0
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, -9.3, p_cz))) @ Matrix.Diagonal(Vector((15.0, 9.4, p_height, 1.0))))
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 9.3, p_cz))) @ Matrix.Diagonal(Vector((15.0, 9.4, p_height, 1.0))))

    # 3. Lateral Side Passageway Arches through Left & Right Pylons
    for py_c in [-9.3, 9.3]:
        side_r = 2.4
        side_segs = 16
        side_spring_z = 7.0
        side_apex_z = 10.5
        for s in range(side_segs):
            ang1 = math.pi * (s / side_segs)
            ang2 = math.pi * ((s + 1) / side_segs)
            y1 = py_c + math.cos(ang1) * side_r
            z1 = side_spring_z + math.sin(ang1) * (side_apex_z - side_spring_z)
            y2 = py_c + math.cos(ang2) * side_r
            z2 = side_spring_z + math.sin(ang2) * (side_apex_z - side_spring_z)
            v1 = bm_gw.verts.new(Vector((-7.51, y1, z1)))
            v2 = bm_gw.verts.new(Vector((7.51, y1, z1)))
            v3 = bm_gw.verts.new(Vector((7.51, y2, z2)))
            v4 = bm_gw.verts.new(Vector((-7.51, y2, z2)))
            bm_gw.faces.new((v1, v2, v3, v4))

    # 4. Upper Entablature & Spandrel (Z = 15.2 to 26.0m)
    span_h = 10.8
    span_cz = 15.2 + span_h / 2.0
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, span_cz))) @ Matrix.Diagonal(Vector((15.0, 9.2, span_h, 1.0))))

    # 5. Grand Central Cusped Pointed Horseshoe Barrel Vault
    arch_segs = 32
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
        v1 = bm_gw.verts.new(Vector((-7.5, y1, z1)))
        v2 = bm_gw.verts.new(Vector((7.5, y1, z1)))
        v3 = bm_gw.verts.new(Vector((7.5, y2, z2)))
        v4 = bm_gw.verts.new(Vector((-7.5, y2, z2)))
        bm_gw.faces.new((v1, v2, v3, v4))

    # 6. Front & Rear Cusped Arch Spandrel Facades
    for fx in [-7.52, 7.52]:
        for s in range(arch_segs):
            ang1 = math.pi * (s / arch_segs)
            ang2 = math.pi * ((s + 1) / arch_segs)
            y1 = math.cos(ang1) * arch_r
            z1 = arch_spring_z + math.sin(ang1) * (arch_apex_z - arch_spring_z)
            y2 = math.cos(ang2) * arch_r
            z2 = arch_spring_z + math.sin(ang2) * (arch_apex_z - arch_spring_z)

            v_bot1 = bm_gw.verts.new(Vector((fx, y1, z1)))
            v_bot2 = bm_gw.verts.new(Vector((fx, y2, z2)))
            v_top2 = bm_gw.verts.new(Vector((fx, y2, 15.2)))
            v_top1 = bm_gw.verts.new(Vector((fx, y1, 15.2)))
            bm_gw.faces.new((v_bot1, v_bot2, v_top2, v_top1))

    # 7. Carved Niches & String Course Moldings on Pylons
    for fx in [-7.55, 7.55]:
        for py_pos in [-9.3, 9.3]:
            bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((fx, py_pos, 8.5))) @ Matrix.Diagonal(Vector((0.4, 4.2, 8.2, 1.0))))
            bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((fx, py_pos, 9.5))) @ Matrix.Diagonal(Vector((0.6, 9.6, 0.45, 1.0))))
            bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=12, radius1=0.85, radius2=0.75, depth=0.25, 
                                 matrix=Matrix.Translation(Vector((fx, py_pos * 0.55, 13.5))) @ Matrix.Rotation(math.radians(90.0), 4, 'Y'))

    # 8. Projecting Bracketed Chhajja Eaves Cornice (Z = 26.2m, 1.5m overhang)
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 26.2))) @ Matrix.Diagonal(Vector((17.2, 30.2, 0.8, 1.0))))

    # 9. Carved Hindu-Style Stone Brackets (Corbels supporting chhajjas)
    for bx in [-7.8, 7.8]:
        for by in range(-13, 14, 3):
            bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((bx, float(by), 25.4))) @ Matrix.Diagonal(Vector((1.2, 0.5, 0.9, 1.0))))

    # 10. Perforated Jali Parapet Cresting (Z = 26.8 to 28.2m)
    bmesh.ops.create_cube(bm_gw, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 27.5))) @ Matrix.Diagonal(Vector((16.4, 29.4, 1.6, 1.0))))

    # 11. 4 Corner Octagonal Minarets (Rising to Z = 34.5m)
    turret_coords = [
        Vector((-7.8, -14.2, 0)),
        Vector((7.8, -14.2, 0)),
        Vector((-7.8, 14.2, 0)),
        Vector((7.8, 14.2, 0))
    ]
    for tc in turret_coords:
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.3, radius2=2.1, depth=24.85, matrix=Matrix.Translation(tc + Vector((0, 0, 13.775))))
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.8, radius2=2.6, depth=0.8, matrix=Matrix.Translation(tc + Vector((0, 0, 26.4))))
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=2.4, radius2=2.2, depth=3.7, matrix=Matrix.Translation(tc + Vector((0, 0, 28.65))))
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=16, radius1=2.3, radius2=0.3, depth=2.7, matrix=Matrix.Translation(tc + Vector((0, 0, 31.85))))
        bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=8, radius1=0.22, radius2=0.02, depth=2.3, matrix=Matrix.Translation(tc + Vector((0, 0, 34.35))))

    # 12. Grand Central Indian Ribbed Dome
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=16, radius1=6.8, radius2=6.6, depth=2.2, matrix=Matrix.Translation(Vector((0, 0, 28.9))))
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=32, radius1=6.6, radius2=0.9, depth=6.8, matrix=Matrix.Translation(Vector((0, 0, 33.4))))
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=16, radius1=1.8, radius2=0.8, depth=0.8, matrix=Matrix.Translation(Vector((0, 0, 37.2))))
    bmesh.ops.create_cone(bm_gw, cap_ends=True, cap_tris=False, segments=12, radius1=0.55, radius2=0.03, depth=3.2, matrix=Matrix.Translation(Vector((0, 0, 39.2))))

    bm_gw.to_mesh(gw_mesh)
    bm_gw.free()

    # Enable smooth shading on all curved surfaces of Gateway
    for poly in gw_mesh.polygons:
        poly.use_smooth = True

    gw_obj.data.materials.append(mat_basalt)
    gw_obj.data.materials.append(mat_gold)

    for poly in gw_mesh.polygons:
        if poly.center.z > 33.5:
            poly.material_index = 1
        else:
            poly.material_index = 0

    bpy.context.view_layer.objects.active = gw_obj
    gw_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')

    # ==================================================================
    # 4. SCULPT BESPOKE TAJ MAHAL PALACE & TOWER
    # ==================================================================
    taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
    taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
    col_landmarks.objects.link(taj_obj)
    taj_obj.location = Vector((94.17, -163.10, 2.20))

    bm_taj = bmesh.new()

    # 1. Ground Floor Rusticated Portico Arcade (Kurla Basalt arches)
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 2.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 2.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 5.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 3.0))) @ Matrix.Diagonal(Vector((24.0, 32.0, 6.0, 1.0))))

    # 2. Main Palace Wings (5 Hotel Guest Floors: Z = 5.5m to 32.0m)
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 18.75))) @ Matrix.Diagonal(Vector((12.0, 84.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 18.75))) @ Matrix.Diagonal(Vector((26.0, 12.0, 26.5, 1.0))))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 20.0))) @ Matrix.Diagonal(Vector((22.0, 30.0, 28.0, 1.0))))

    # 3. 6 Architectural Tiers of Cantilevered Balconies with Wrought-Iron Railings
    for tier in range(1, 6):
        tz = tier * 5.2 + 2.5
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((12.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.4, 28.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((13.6, 0.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 28.0, 0.9, 1.0))))

        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, 36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((17.4, 36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 12.0, 0.9, 1.0))))

        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((16.5, -36.0, tz))) @ Matrix.Diagonal(Vector((2.0, 12.0, 0.45, 1.0))))
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((17.4, -36.0, tz + 0.55))) @ Matrix.Diagonal(Vector((0.15, 12.0, 0.9, 1.0))))

    # 4. Pitched Mangalore Red Tile Roofs & Gables (Z = 32.0 to 38.5m)
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, 36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.8, depth=7.0, matrix=Matrix.Translation(Vector((3.0, -36.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
    bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((-16.0, 0.0, 34.0))) @ Matrix.Diagonal(Vector((13.0, 84.0, 4.0, 1.0))))

    # 5. Iconic Florentine Pointed Red Dome
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=24, radius1=10.5, radius2=10.0, depth=10.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 37.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=10.0, radius2=1.0, depth=20.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 52.0))))
    for rib_idx in range(16):
        rib_ang = 2.0 * math.pi * (rib_idx / 16.0)
        rib_x = 1.0 + math.cos(rib_ang) * 9.8
        rib_y = math.sin(rib_ang) * 9.8
        bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(Vector((rib_x, rib_y, 50.0))) @ Matrix.Diagonal(Vector((0.4, 0.4, 18.0, 1.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=2.2, radius2=1.9, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 64.5))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=12, radius1=0.6, radius2=0.04, depth=5.0, matrix=Matrix.Translation(Vector((1.0, 0.0, 69.5))))

    # 6. 4 Corner Moorish Chhatris on Heritage Wings
    taj_chhatris = [
        Vector((15.0, 41.5, 32.0)),
        Vector((15.0, -41.5, 32.0)),
        Vector((-21.0, 41.5, 32.0)),
        Vector((-21.0, -41.5, 32.0))
    ]
    for cp in taj_chhatris:
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=3.0, radius2=2.6, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=2.6, radius2=0.3, depth=5.0, matrix=Matrix.Translation(cp + Vector((0, 0, 6.0))))
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=8, radius1=0.25, radius2=0.03, depth=2.8, matrix=Matrix.Translation(cp + Vector((0, 0, 9.0))))

    # 7. The Adjacent 1973 Taj Tower
    tower_c = Vector((-34.0, -58.0, 0.0))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=16.0, radius2=15.8, depth=84.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 42.0))))
    for b_floor in range(1, 23):
        bf_z = b_floor * 3.6 + 2.0
        bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=17.4, radius2=17.2, depth=0.8, matrix=Matrix.Translation(tower_c + Vector((0, 0, bf_z))))
        for r_idx in range(12):
            r_ang = 2.0 * math.pi * (r_idx / 12.0)
            rx = math.cos(r_ang) * 17.3
            ry = math.sin(r_ang) * 17.3
            bmesh.ops.create_cube(bm_taj, size=1.0, matrix=Matrix.Translation(tower_c + Vector((rx, ry, bf_z))) @ Matrix.Diagonal(Vector((0.6, 0.6, 3.6, 1.0))))

    # Bronze Pagoda Crown Roof
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=32, radius1=18.5, radius2=12.0, depth=8.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 88.0))))
    bmesh.ops.create_cone(bm_taj, cap_ends=True, cap_tris=False, segments=16, radius1=3.5, radius2=0.4, depth=6.0, matrix=Matrix.Translation(tower_c + Vector((0, 0, 95.0))))

    bm_taj.to_mesh(taj_mesh)
    bm_taj.free()

    for poly in taj_mesh.polygons:
        if poly.center.z > 32.0 or poly.center.x < -20.0:
            poly.use_smooth = True

    taj_obj.data.materials.append(mat_taj_facade) # 0: Buff Kurla stone + window grid
    taj_obj.data.materials.append(mat_taj_red)    # 1: Vermilion red dome & roofs
    taj_obj.data.materials.append(mat_gold)       # 2: Gold finial spires
    taj_obj.data.materials.append(mat_tower)      # 3: White/cream tower concrete
    taj_obj.data.materials.append(mat_iron)       # 4: Wrought iron balustrades

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

    # ==================================================================
    # 5. ESPLANADE PLAZA, JETTY STEPS & SEAWALL
    # ==================================================================
    pz_name = "PLAZA_Apollo_Bunder_Harbour_Jetty"
    pz_mesh = bpy.data.meshes.new(f"{pz_name}_Mesh")
    pz_obj = bpy.data.objects.new(pz_name, pz_mesh)
    col_promenade.objects.link(pz_obj)
    pz_obj.location = Vector((0.0, 0.0, 0.0))

    bm_pz = bmesh.new()
    bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((140.0, -137.5, 1.1))) @ Matrix.Diagonal(Vector((140.0, 140.0, 2.2, 1.0))))
    bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((208.2, -137.5, 2.8))) @ Matrix.Diagonal(Vector((1.0, 140.0, 1.2, 1.0))))
    for s_idx in range(10):
        sx = 208.7 + s_idx * 1.3
        sz = 2.2 - (s_idx + 1) * 0.28
        bmesh.ops.create_cube(bm_pz, size=1.0, matrix=Matrix.Translation(Vector((sx, -137.5, sz / 2.0))) @ Matrix.Diagonal(Vector((1.3, 80.0, max(sz, 0.1), 1.0))))
    for by in range(-200, -70, 10):
        bmesh.ops.create_cone(bm_pz, cap_ends=True, cap_tris=False, segments=8, radius1=0.28, radius2=0.22, depth=0.8, matrix=Matrix.Translation(Vector((208.0, by, 3.8))))
        bmesh.ops.create_cone(bm_pz, cap_ends=True, cap_tris=False, segments=8, radius1=0.34, radius2=0.08, depth=0.3, matrix=Matrix.Translation(Vector((208.0, by, 4.25))))

    bm_pz.to_mesh(pz_mesh)
    bm_pz.free()
    pz_obj.data.materials.append(mat_plaza)

    bpy.context.view_layer.objects.active = pz_obj
    pz_obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')

    # ==================================================================
    # 6. AUTHENTIC 4-LEGGED CONCRETE TETRAPODS (BREAKWATER)
    # ==================================================================
    tetra_mesh = bpy.data.meshes.new("Tetrapod_Master_Core_Mesh")
    bm_tp = bmesh.new()
    bmesh.ops.create_icosphere(bm_tp, subdivisions=1, radius=0.9)
    tet_dirs = [
        Vector((0, 0, 1.0)),
        Vector((0.9428, 0, -0.3333)),
        Vector((-0.4714, 0.8165, -0.3333)),
        Vector((-0.4714, -0.8165, -0.3333))
    ]
    for t_dir in tet_dirs:
        rot = Vector((0, 0, 1)).rotation_difference(t_dir).to_matrix().to_4x4()
        bmesh.ops.create_cone(bm_tp, cap_ends=True, cap_tris=False, segments=12, radius1=0.9, radius2=0.6, depth=2.4, 
                             matrix=Matrix.Translation(t_dir * 1.2) @ rot)
    bm_tp.to_mesh(tetra_mesh)
    bm_tp.free()

    for poly in tetra_mesh.polygons:
        poly.use_smooth = True

    import random
    random.seed(42)
    for row in range(4):
        tx_base = 214.0 + row * 2.8
        for ty_base in range(-200, -70, 4):
            tx = tx_base + random.uniform(-0.6, 0.6)
            ty = ty_base + random.uniform(-0.8, 0.8)
            tz = 0.4 + row * 0.45 + random.uniform(-0.2, 0.3)
            
            t_obj = bpy.data.objects.new(f"TETRA_Apollo_{row}_{ty_base}", tetra_mesh)
            col_tetrapods.objects.link(t_obj)
            t_obj.location = Vector((tx, ty, tz))
            t_obj.rotation_euler = Euler((random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28)), 'XYZ')
            t_obj.scale = Vector((1.3, 1.3, 1.3))
            t_obj.data.materials.append(mat_tetrapod)

    # ==================================================================
    # 7. HIGH-FIDELITY ROYAL PALM TREES (Roystonea Regia)
    # ==================================================================
    palm_mesh = bpy.data.meshes.new("RoyalPalm_Master_Mesh")
    bm_pm = bmesh.new()
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.55, radius2=0.38, depth=11.0, matrix=Matrix.Translation(Vector((0, 0, 5.5))))
    bmesh.ops.create_cone(bm_pm, cap_ends=True, cap_tris=False, segments=16, radius1=0.40, radius2=0.36, depth=2.2, matrix=Matrix.Translation(Vector((0, 0, 12.1))))
    frond_count = 24
    for f_i in range(frond_count):
        f_ang = 2.0 * math.pi * (f_i / float(frond_count)) + (f_i * 0.15)
        f_elev = math.radians(15.0 + (f_i % 4) * 16.0)
        f_len = 6.2
        pts = []
        for step in range(8):
            frac = step / 7.0
            r_dist = frac * f_len * math.cos(f_elev)
            z_arch = math.sin(frac * math.pi) * 1.5 - frac * frac * 3.2
            fx = math.cos(f_ang) * r_dist
            fy = math.sin(f_ang) * r_dist
            fz = 13.0 + z_arch
            pts.append(Vector((fx, fy, fz)))
        for step in range(7):
            p1 = pts[step]
            p2 = pts[step + 1]
            side_w = math.sin((step / 7.0) * math.pi) * 0.85 + 0.15
            perp = Vector((-math.sin(f_ang), math.cos(f_ang), 0)) * side_w
            v1 = bm_pm.verts.new(p1 - perp)
            v2 = bm_pm.verts.new(p1 + perp)
            v3 = bm_pm.verts.new(p2 + perp)
            v4 = bm_pm.verts.new(p2 - perp)
            bm_pm.faces.new((v1, v2, v3, v4))

    bm_pm.to_mesh(palm_mesh)
    bm_pm.free()

    for poly in palm_mesh.polygons:
        poly.use_smooth = True

    mat_palm_trunk = bpy.data.materials.get("MAT_Palm_TrunkBark")
    if not mat_palm_trunk:
        mat_palm_trunk = bpy.data.materials.new("MAT_Palm_TrunkBark")
        mat_palm_trunk.use_nodes = True
        pt_bsdf = mat_palm_trunk.node_tree.nodes.get("Principled BSDF")
        if pt_bsdf:
            pt_bsdf.inputs['Base Color'].default_value = (0.52, 0.48, 0.44, 1.0)
            pt_bsdf.inputs['Roughness'].default_value = 0.85

    mat_palm_leaf = bpy.data.materials.get("MAT_Palm_GreenFronds")
    if not mat_palm_leaf:
        mat_palm_leaf = bpy.data.materials.new("MAT_Palm_GreenFronds")
        mat_palm_leaf.use_nodes = True
        pl_bsdf = mat_palm_leaf.node_tree.nodes.get("Principled BSDF")
        if pl_bsdf:
            pl_bsdf.inputs['Base Color'].default_value = (0.16, 0.42, 0.12, 1.0)
            pl_bsdf.inputs['Roughness'].default_value = 0.35

    palm_mesh.materials.append(mat_palm_trunk)
    palm_mesh.materials.append(mat_palm_leaf)
    for poly in palm_mesh.polygons:
        if poly.center.z > 12.0:
            poly.material_index = 1
        else:
            poly.material_index = 0

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
    for idx, pl in enumerate(palm_locs):
        p_obj = bpy.data.objects.new(f"PALM_GatewayPlaza_{idx}", palm_mesh)
        col_veg.objects.link(p_obj)
        p_obj.location = pl
        p_obj.rotation_euler = Euler((0, 0, idx * 0.8), 'XYZ')
        p_obj.scale = Vector((1.0, 1.0, random.uniform(0.9, 1.15)))

    # ==================================================================
    # 8. KAALI-PEELI TAXIS & HARBOUR FERRIES
    # ==================================================================
    taxi_mesh = bpy.data.meshes.get("KaaliPeeli_Taxi_Detailed_Mesh")
    if taxi_mesh:
        taxi_locs = [
            (Vector((142.0, -145.0, 2.2)), math.radians(20.0)),
            (Vector((147.0, -148.0, 2.2)), math.radians(20.0)),
            (Vector((135.0, -140.0, 2.2)), math.radians(110.0)),
            (Vector((115.0, -135.0, 2.2)), math.radians(-70.0))
        ]
        for idx, (t_pos, t_rot) in enumerate(taxi_locs):
            t_obj = bpy.data.objects.new(f"TAXI_Apollo_{idx}", taxi_mesh)
            col_props.objects.link(t_obj)
            t_obj.location = t_pos
            t_obj.rotation_euler = Euler((0, 0, t_rot), 'XYZ')

    boat_mesh = bpy.data.meshes.get("Harbour_Ferry_Master_Mesh")
    if boat_mesh:
        boat_locs = [
            (Vector((238.0, -190.0, 0.4)), math.radians(15.0)),
            (Vector((245.0, -210.0, 0.4)), math.radians(-25.0)),
            (Vector((230.0, -75.0, 0.4)), math.radians(35.0))
        ]
        for idx, (b_pos, b_rot) in enumerate(boat_locs):
            b_obj = bpy.data.objects.new(f"BOAT_Gateway_Ferry_{idx}", boat_mesh)
            col_promenade.objects.link(b_obj)
            b_obj.location = b_pos
            b_obj.rotation_euler = Euler((0, 0, b_rot), 'XYZ')

    # Save to master blend
    bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print("Apollo Bunder Scanned Detailing Master complete and saved!")

main()
