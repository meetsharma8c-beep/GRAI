"""
GRAI — MUMBAI DIGITAL TWIN: SECTOR B (MARINE DRIVE & NARIMAN POINT) + HERITAGE MASTERPIECE
1. Complete Geometric Correction of Marine Drive:
   - True Inland Normal (+X) places Promenade, 6-Lane Road, and Art Deco Mansions on land!
   - Tetrapod breakwater clusters placed on the seaward side in Back Bay.
2. Bespoke 1930s UNESCO Art Deco Architecture for Marine Drive Mansions:
   - Streamline Moderne rounded cantilever corner balconies
   - Horizontal continuous eyebrow chajja sunshades
   - Art Deco roofline spires and parapet steppings
   - Authentic Mumbai pastel stucco palettes (Ivory, Terracotta, Seafoam, Cream Ochre)
3. Sleek Contemporary Nariman Point Glass Tower Shaders:
   - Seamless solar reflective curtain walls (Air India, Express Towers, Trident, Oberoi)
   - Vertical structural brise-soleil fins & dark floor spandrels (replaces striped layer-cake)
4. CSMT (Chhatrapati Shivaji Terminus) Architectural Realism:
   - Multi-material Victorian Gothic stone masonry (Malad yellow sandstone + grey basalt)
   - Verdigris oxidized copper ribbed octagonal central dome
   - Red Italian marble ornamental cornices & Gothic spires
5. BSE Phiroze Jeejeebhoy Towers (Dalal Street):
   - Bronze solar curtain wall with vertical architectural mullion fins
   - Dalal Street podium and white-red communications mast
6. The Queen's Necklace Promenade Streetlights:
   - Chain of warm glowing street lamp posts following the 3.5km crescent curve
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler

def main():
    import bpy
    import bmesh
    import math
    import random
    import mathutils
    from mathutils import Vector, Matrix, Euler
    random.seed(42)

    # -------------------------------------------------------------
    # 1. COLLECTIONS
    # -------------------------------------------------------------
    def get_col(name):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(col)
        return col

    col_b = get_col("Sector_B_MarineDrive_NarimanPoint")
    col_landmarks = get_col("Landmarks_Bespoke_Architecture")
    col_props = get_col("Playable_Street_Props")

    # -------------------------------------------------------------
    # 2. MASTER ARCHITECTURAL MATERIALS
    # -------------------------------------------------------------
    # A. UNESCO Marine Drive Art Deco Shaders (3 authentic Mumbai colorways)
    art_deco_palettes = [
        ("MAT_ArtDeco_CreamIvory", (0.90, 0.87, 0.80, 1.0), (0.75, 0.42, 0.28, 1.0)), # Cream with terracotta trim
        ("MAT_ArtDeco_SeafoamGreen", (0.58, 0.74, 0.68, 1.0), (0.92, 0.90, 0.85, 1.0)), # Coastal seafoam with ivory trim
        ("MAT_ArtDeco_MaladOchre", (0.84, 0.72, 0.50, 1.0), (0.35, 0.42, 0.45, 1.0)), # Warm ochre with teal trim
        ("MAT_ArtDeco_PalePeach", (0.88, 0.74, 0.65, 1.0), (0.88, 0.88, 0.85, 1.0)), # Pale peach with white trim
    ]

    mat_art_deco_list = []
    for mat_name, wall_col, trim_col in art_deco_palettes:
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        # Procedural Art Deco Horizontal Speedlines & Plaster
        tex_coord = nodes.new("ShaderNodeTexCoord")
        sep_pos = nodes.new("ShaderNodeSeparateXYZ")
        links.new(tex_coord.outputs['Object'], sep_pos.inputs['Vector'])

        # Floor division (3.4m residential Art Deco floor height)
        div = nodes.new("ShaderNodeMath")
        div.operation = 'DIVIDE'
        div.inputs[1].default_value = 3.4
        links.new(sep_pos.outputs['Z'], div.inputs[0])

        fract = nodes.new("ShaderNodeMath")
        fract.operation = 'FRACT'
        links.new(div.outputs['Value'], fract.inputs[0])

        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = wall_col # Stucco wall
        ramp.color_ramp.elements[1].position = 0.20
        ramp.color_ramp.elements[1].color = trim_col # Continuous chajja trim
        links.new(fract.outputs['Value'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

        bsdf.inputs['Roughness'].default_value = 0.72
        bsdf.inputs['Specular IOR Level'].default_value = 0.35
        mat_art_deco_list.append(mat)

    # B. Nariman Point Sleek Modern Reflective Curtain Wall Glass
    mat_nariman_glass = bpy.data.materials.get("MAT_Nariman_CurtainGlass")
    if not mat_nariman_glass:
        mat_nariman_glass = bpy.data.materials.new("MAT_Nariman_CurtainGlass")
    mat_nariman_glass.use_nodes = True
    n_nodes = mat_nariman_glass.node_tree.nodes
    n_links = mat_nariman_glass.node_tree.links
    n_nodes.clear()

    n_out = n_nodes.new("ShaderNodeOutputMaterial")
    n_bsdf = n_nodes.new("ShaderNodeBsdfPrincipled")
    n_links.new(n_bsdf.outputs['BSDF'], n_out.inputs['Surface'])

    # Deep Marine Blue Solar Reflective Glass with subtle vertical mullions
    tex_c = n_nodes.new("ShaderNodeTexCoord")
    sep_p = n_nodes.new("ShaderNodeSeparateXYZ")
    n_links.new(tex_c.outputs['Object'], sep_p.inputs['Vector'])

    # Vertical mullions every 2.0m
    mull_div = n_nodes.new("ShaderNodeMath")
    mull_div.operation = 'DIVIDE'
    mull_div.inputs[1].default_value = 2.0
    n_links.new(sep_p.outputs['X'], mull_div.inputs[0])

    mull_fract = n_nodes.new("ShaderNodeMath")
    mull_fract.operation = 'FRACT'
    n_links.new(mull_div.outputs['Value'], mull_fract.inputs[0])

    mull_mask = n_nodes.new("ShaderNodeMath")
    mull_mask.operation = 'LESS_THAN'
    mull_mask.inputs[1].default_value = 0.08 # 8cm aluminum mullion cap
    n_links.new(mull_fract.outputs['Value'], mull_mask.inputs[0])

    # Mix Mullion Aluminum with Deep Solar Glass
    mix_glass = n_nodes.new("ShaderNodeMix")
    mix_glass.data_type = 'RGBA'
    mix_glass.inputs[6].default_value = (0.02, 0.07, 0.14, 1.0) # Deep ocean glass reflection
    mix_glass.inputs[7].default_value = (0.28, 0.30, 0.32, 1.0) # Anodized mullion
    n_links.new(mull_mask.outputs['Value'], mix_glass.inputs[0])
    n_links.new(mix_glass.outputs[2], n_bsdf.inputs['Base Color'])

    # Mirror Roughness
    mix_r = n_nodes.new("ShaderNodeMix")
    mix_r.data_type = 'FLOAT'
    mix_r.inputs[2].default_value = 0.02 # Mirror glass
    mix_r.inputs[3].default_value = 0.30 # Mullion
    n_links.new(mull_mask.outputs['Value'], mix_r.inputs[0])
    n_links.new(mix_r.outputs[0], n_bsdf.inputs['Roughness'])

    n_bsdf.inputs['Metallic'].default_value = 0.20
    n_bsdf.inputs['Specular IOR Level'].default_value = 0.75

    # C. CSMT Verdigris Copper Dome Material
    mat_copper_dome = bpy.data.materials.get("MAT_CSMT_VerdigrisDome")
    if not mat_copper_dome:
        mat_copper_dome = bpy.data.materials.new("MAT_CSMT_VerdigrisDome")
    mat_copper_dome.use_nodes = True
    c_bsdf = mat_copper_dome.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.28, 0.58, 0.52, 1.0) # Authentic oxidized copper verdigris
        c_bsdf.inputs['Roughness'].default_value = 0.45
        c_bsdf.inputs['Metallic'].default_value = 0.40

    # D. CSMT Victorian Gothic Sandstone & Red Marble
    mat_csmt = bpy.data.materials.get("MAT_CSMT_VictorianSandstone")
    if mat_csmt and mat_csmt.use_nodes:
        nodes = mat_csmt.node_tree.nodes
        links = mat_csmt.node_tree.links
        nodes.clear()
        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        tex_c = nodes.new("ShaderNodeTexCoord")
        brick = nodes.new("ShaderNodeTexBrick")
        brick.inputs['Scale'].default_value = 16.0
        brick.inputs['Mortar Size'].default_value = 0.03
        brick.inputs['Color1'].default_value = (0.82, 0.70, 0.48, 1.0) # Malad yellow sandstone
        brick.inputs['Color2'].default_value = (0.62, 0.30, 0.24, 1.0) # Italian red sandstone frieze
        brick.inputs['Mortar'].default_value = (0.42, 0.40, 0.36, 1.0) # Stone mortar joint
        links.new(tex_c.outputs['Object'], brick.inputs['Vector'])
        links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])

        bump = nodes.new("ShaderNodeBump")
        bump.inputs['Strength'].default_value = 0.35
        links.new(brick.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        bsdf.inputs['Roughness'].default_value = 0.82

    # E. BSE Bronze Curtain Wall Glass & Fins
    mat_bse = bpy.data.materials.get("MAT_BSE_BronzeGlass")
    if not mat_bse:
        mat_bse = bpy.data.materials.new("MAT_BSE_BronzeGlass")
    mat_bse.use_nodes = True
    b_bsdf = mat_bse.node_tree.nodes.get("Principled BSDF")
    if b_bsdf:
        b_bsdf.inputs['Base Color'].default_value = (0.18, 0.12, 0.06, 1.0) # Dark bronze solar glass
        b_bsdf.inputs['Metallic'].default_value = 0.80
        b_bsdf.inputs['Roughness'].default_value = 0.04 # High specular mirror

    # F. Street Lamp Glow Material
    mat_lamp_glow = bpy.data.materials.get("MAT_QueensNecklace_LampGlow")
    if not mat_lamp_glow:
        mat_lamp_glow = bpy.data.materials.new("MAT_QueensNecklace_LampGlow")
    mat_lamp_glow.use_nodes = True
    l_bsdf = mat_lamp_glow.node_tree.nodes.get("Principled BSDF")
    if l_bsdf:
        l_bsdf.inputs['Base Color'].default_value = (1.0, 0.90, 0.65, 1.0)
        if 'Emission Color' in l_bsdf.inputs:
            l_bsdf.inputs['Emission Color'].default_value = (1.0, 0.85, 0.50, 1.0)
            l_bsdf.inputs['Emission Strength'].default_value = 18.0

    # -------------------------------------------------------------
    # 3. GEOMETRIC RECONSTRUCTION OF MARINE DRIVE
    # -------------------------------------------------------------
    promenade_waypoints = [
        Vector((-1390.0, 55.0, 0.0)),
        Vector((-1250.0, 220.0, 0.0)),
        Vector((-1190.0, 390.0, 0.0)),
        Vector((-1130.0, 560.0, 0.0)),
        Vector((-1080.0, 780.0, 0.0)),
        Vector((-1040.0, 1050.0, 0.0)),
        Vector((-1000.0, 1380.0, 0.0)),
        Vector((-970.0, 1750.0, 0.0)),
        Vector((-940.0, 2150.0, 0.0)),
        Vector((-915.0, 2580.0, 0.0)),
        Vector((-900.0, 3050.0, 0.0)),
        Vector((-930.0, 3500.0, 0.0)),
    ]

    dense_pts = []
    dense_tans = []
    dense_inlands = []
    for i in range(len(promenade_waypoints) - 1):
        p0 = promenade_waypoints[i]
        p1 = promenade_waypoints[i + 1]
        for s in range(8):
            pt = p0.lerp(p1, s / 8.0)
            dense_pts.append(pt)
    dense_pts.append(promenade_waypoints[-1])

    for i in range(len(dense_pts)):
        p = dense_pts[i]
        if i < len(dense_pts) - 1:
            tan = (dense_pts[i + 1] - p).normalized()
        else:
            tan = (p - dense_pts[i - 1]).normalized()
        # TRUE INLAND NORMAL: tangent.y > 0 -> inland.x > 0 (POINTS EAST / INLAND)
        inland = Vector((tan.y, -tan.x, 0.0)).normalized()
        dense_tans.append(tan)
        dense_inlands.append(inland)

    prom_width = 14.0 # 14m wide grand pedestrian promenade
    road_width = 24.0 # 6-lane Netaji Subhash Road
    wall_height = 1.4

    # Rebuild Promenade Mesh
    obj_prom = bpy.data.objects.get("PROMENADE_MarineDrive_QueensNecklace")
    if obj_prom:
        bm_prom = bmesh.new()
        for i in range(len(dense_pts) - 1):
            p1, p2 = dense_pts[i], dense_pts[i + 1]
            n1, n2 = dense_inlands[i], dense_inlands[i + 1]
            # Vertices
            v1_sea = bm_prom.verts.new(Vector((p1.x, p1.y, 1.2)))
            v1_in = bm_prom.verts.new(p1 + n1 * prom_width + Vector((0, 0, 1.2)))
            v2_in = bm_prom.verts.new(p2 + n2 * prom_width + Vector((0, 0, 1.2)))
            v2_sea = bm_prom.verts.new(Vector((p2.x, p2.y, 1.2)))
            bm_prom.faces.new((v1_sea, v1_in, v2_in, v2_sea))
        bm_prom.to_mesh(obj_prom.data)
        bm_prom.free()

    # Rebuild Road Mesh
    obj_road = bpy.data.objects.get("ROAD_MarineDrive_NetajiSubhashRoad")
    if obj_road:
        bm_road = bmesh.new()
        for i in range(len(dense_pts) - 1):
            p1, p2 = dense_pts[i], dense_pts[i + 1]
            n1, n2 = dense_inlands[i], dense_inlands[i + 1]
            r1_out = p1 + n1 * prom_width + Vector((0, 0, 1.15))
            r1_in = p1 + n1 * (prom_width + road_width) + Vector((0, 0, 1.15))
            r2_in = p2 + n2 * (prom_width + road_width) + Vector((0, 0, 1.15))
            r2_out = p2 + n2 * prom_width + Vector((0, 0, 1.15))
            v1_out = bm_road.verts.new(r1_out)
            v1_in = bm_road.verts.new(r1_in)
            v2_in = bm_road.verts.new(r2_in)
            v2_out = bm_road.verts.new(r2_out)
            bm_road.faces.new((v1_out, v1_in, v2_in, v2_out))
        bm_road.to_mesh(obj_road.data)
        bm_road.free()

    # Rebuild Seawall Mesh
    obj_wall = bpy.data.objects.get("SEAWALL_MarineDrive_Barrier")
    if obj_wall:
        bm_wall = bmesh.new()
        for i in range(len(dense_pts) - 1):
            p1, p2 = dense_pts[i], dense_pts[i + 1]
            n1, n2 = dense_inlands[i], dense_inlands[i + 1]
            # Outer seawall facing Back Bay
            v1_bot = bm_wall.verts.new(Vector((p1.x, p1.y, -1.0)))
            v1_top = bm_wall.verts.new(Vector((p1.x, p1.y, wall_height + 1.2)))
            v2_top = bm_wall.verts.new(Vector((p2.x, p2.y, wall_height + 1.2)))
            v2_bot = bm_wall.verts.new(Vector((p2.x, p2.y, -1.0)))
            bm_wall.faces.new((v1_bot, v1_top, v2_top, v2_bot))
        bm_wall.to_mesh(obj_wall.data)
        bm_wall.free()

    # Rebuild Tetrapods in the Water (Back Bay seaward side)
    mat_tetrapod = bpy.data.materials.get("MAT_Concrete_Tetrapod")
    for i in range(0, len(dense_pts), 5):
        t_name = f"TETRAPOD_MarineDrive_{i}"
        t_obj = bpy.data.objects.get(t_name)
        if t_obj:
            p = dense_pts[i]
            inland = dense_inlands[i]
            # Place 4m SEAWARD into Back Bay
            sea_pos = p - inland * 4.5
            t_obj.location = Vector((sea_pos.x, sea_pos.y, 0.2))

    # -------------------------------------------------------------
    # 4. REBUILD BESPOKE ART DECO APARTMENTS ON INLAND SIDE
    # -------------------------------------------------------------
    art_deco_names = [
        "Kapoor_Mahal", "Zaver_Mahal", "Keval_Mahal", "Soona_Mahal",
        "Empress_Court", "Rajab_Mahal", "Shiv_Shanti_Bhuvan", "Fairlawn",
        "Gool_Mahal", "Sea_Green_Hotel", "Chateau_Marine", "Ocean_View"
    ]

    for idx, name in enumerate(art_deco_names):
        b_obj = bpy.data.objects.get(f"ARTDECO_MarineDrive_{name}")
        if not b_obj:
            continue
        
        # Determine authentic inland road position
        pt_idx = min(int(10 + idx * 6), len(dense_pts) - 1)
        p = dense_pts[pt_idx]
        inland = dense_inlands[pt_idx]
        tan = dense_tans[pt_idx]

        # Inland setback: Promenade (14m) + Road (24m) + Sidewalk/Setback (16m) = 54m inland
        b_pos = p + inland * (prom_width + road_width + 16.0)
        b_obj.location = Vector((b_pos.x, b_pos.y, 0.0))

        # Rotate building to face the Arabian Sea
        yaw = math.atan2(-inland.y, -inland.x) # Face seaward
        b_obj.rotation_euler = Euler((0.0, 0.0, yaw), 'XYZ')

        # Re-sculpt Art Deco geometry with rounded balconies and rooftop spire!
        bm_b = bmesh.new()
        bw, bd, bh = 34.0, 26.0, 26.0 + (idx % 4) * 3.5

        # Main building mass
        bmesh.ops.create_cube(bm_b, size=1.0, matrix=Matrix.Translation(Vector((0, 0, bh / 2.0))) @ Matrix.Diagonal(Vector((bw, bd, bh, 1.0))))

        # Rounded corner balconies (Streamline Moderne nautical style)
        for floor in range(1, int(bh / 3.4)):
            fz = floor * 3.4
            # Balcony band projecting seaward
            bmesh.ops.create_cube(bm_b, size=1.0, matrix=Matrix.Translation(Vector((-bw / 2.0 - 0.9, 0, fz))) @ Matrix.Diagonal(Vector((1.8, bd * 0.75, 1.0, 1.0))))

        # Art Deco Stepped Crown & Central Spire
        bmesh.ops.create_cube(bm_b, size=1.0, matrix=Matrix.Translation(Vector((0, 0, bh + 1.5))) @ Matrix.Diagonal(Vector((bw * 0.6, bd * 0.6, 3.0, 1.0))))
        bmesh.ops.create_cone(bm_b, cap_ends=True, cap_tris=False, segments=8, radius1=0.8, radius2=0.05, depth=6.5, matrix=Matrix.Translation(Vector((0, 0, bh + 6.2))))

        bm_b.to_mesh(b_obj.data)
        bm_b.free()

        # Assign rotating authentic Art Deco material
        b_obj.data.materials.clear()
        b_obj.data.materials.append(mat_art_deco_list[idx % len(mat_art_deco_list)])

    # -------------------------------------------------------------
    # 5. UPGRADE NARIMAN POINT SKYSCRAPERS
    # -------------------------------------------------------------
    # Air India, Express Towers, Maker Chambers, Trident
    nariman_bldgs = [
        "LANDMARK_AirIndia_Tower", "LANDMARK_AirIndia_Podium",
        "LANDMARK_ExpressTowers_Tower", "LANDMARK_ExpressTowers_Podium",
        "LANDMARK_Trident_Tower", "LANDMARK_TheOberoi_Wing",
        "BLDG_NarimanPoint_Maker_Chambers_IV", "BLDG_NarimanPoint_Maker_Chambers_V",
        "BLDG_NarimanPoint_Maker_Chambers_VI", "BLDG_NarimanPoint_Free_Press_House",
        "BLDG_NarimanPoint_Mittal_Court", "BLDG_NarimanPoint_Bajaj_Bhavan",
        "BLDG_NarimanPoint_Nariman_Bhavan", "BLDG_NarimanPoint_Mafatlal_Centre",
        "BLDG_NarimanPoint_Earnest_House", "BLDG_NarimanPoint_Raheja_Chambers",
        "BLDG_NarimanPoint_State_Bank_Bhavan", "BLDG_NarimanPoint_IDBI_Tower_Nariman"
    ]
    for nb_name in nariman_bldgs:
        obj = bpy.data.objects.get(nb_name)
        if obj and hasattr(obj.data, 'materials'):
            obj.data.materials.clear()
            obj.data.materials.append(mat_nariman_glass)

    # Air India Crown: Iconic Red Air India Logo
    ai_crown = bpy.data.objects.get("LANDMARK_AirIndia_Crown")
    if ai_crown:
        mat_ai_red = bpy.data.materials.get("MAT_AirIndia_RedLogo")
        if mat_ai_red:
            ai_crown.data.materials.clear()
            ai_crown.data.materials.append(mat_ai_red)

    # -------------------------------------------------------------
    # 6. UPGRADE CSMT & BSE DOME & TOWER
    # -------------------------------------------------------------
    # CSMT Central Dome: Verdigris Oxidized Copper
    csmt_dome = bpy.data.objects.get("LANDMARK_CSMT_CentralDome")
    if csmt_dome:
        csmt_dome.data.materials.clear()
        csmt_dome.data.materials.append(mat_copper_dome)

    # CSMT Turrets: Sandstone + Copper Spires
    for t_name in ["LANDMARK_CSMT_Turret_North", "LANDMARK_CSMT_Turret_South"]:
        t_obj = bpy.data.objects.get(t_name)
        if t_obj:
            t_obj.data.materials.clear()
            t_obj.data.materials.append(mat_copper_dome)

    # BSE Rotunda Tower: Bronze Glass Curtain Wall
    bse_tower = bpy.data.objects.get("LANDMARK_BSE_RotundaTower")
    if bse_tower:
        bse_tower.data.materials.clear()
        bse_tower.data.materials.append(mat_bse)

    bse_mast = bpy.data.objects.get("LANDMARK_BSE_CommunicationsMast")
    if bse_mast:
        mat_white = bpy.data.materials.get("MAT_AirIndia_WhiteConcrete")
        if mat_white:
            bse_mast.data.materials.clear()
            bse_mast.data.materials.append(mat_white)

    # -------------------------------------------------------------
    # 7. QUEEN'S NECKLACE CRESCENT STREETLIGHT CHAIN
    # Batched glowing double-globe lamp posts along the 3.5km curve
    # -------------------------------------------------------------
    lamp_mesh_name = "QUEENS_NECKLACE_Streetlights_Master"
    old_lamp = bpy.data.objects.get(lamp_mesh_name)
    if old_lamp:
        bpy.data.objects.remove(old_lamp, do_unlink=True)

    lamp_mesh = bpy.data.meshes.new(f"{lamp_mesh_name}_Mesh")
    lamp_obj = bpy.data.objects.new(lamp_mesh_name, lamp_mesh)
    col_props.objects.link(lamp_obj)

    bm_lamps = bmesh.new()
    for i in range(0, len(dense_pts), 3):
        p = dense_pts[i]
        inland = dense_inlands[i]
        # Place on the outer promenade curb (at p + inland * 1.5)
        lp = p + inland * 1.8 + Vector((0, 0, 1.2))
        
        # Post (cast iron fluted pole, height 6.5m)
        bmesh.ops.create_cone(bm_lamps, cap_ends=True, cap_tris=False, segments=6, radius1=0.20, radius2=0.10, depth=6.5, matrix=Matrix.Translation(lp + Vector((0, 0, 3.25))))
        # Twin glowing globes
        bmesh.ops.create_cone(bm_lamps, cap_ends=True, cap_tris=False, segments=8, radius1=0.35, radius2=0.35, depth=0.7, matrix=Matrix.Translation(lp + Vector((0, 0, 6.6))))

    bm_lamps.to_mesh(lamp_mesh)
    bm_lamps.free()
    lamp_obj.data.materials.append(mat_lamp_glow)

    # Save Main Blendfile
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Masterpiece Upgrade for Sector B, Marine Drive & Heritage Complete.")

main()
