#!/usr/bin/env python3
"""
GRAI — Authentic Mumbai Color & Lighting Master Calibration
============================================================
Upgrades all procedural PBR shaders and scene lighting to authentic,
rich, vibrant, high-contrast Mumbai tones:
- Replaces washed-out pale tones with deep, saturated local architectural colors:
  * Malad yellow-gold sandstone & Kurla dark volcanic basalt (CSMT, Gateway, Fort)
  * Rich Bombay Art Deco tropical heritage pastels (turmeric ochre, seafoam, terracotta peach, warm ivory)
  * Deep marine cyan-navy curtain wall glass & structural aluminum (Worli megatowers)
  * Exposed architectural concrete & dark bronze ribbon glazing (Nariman Point CBD)
  * Aged lime plaster, teak timber verandas & Mangalore red tiles (Girgaon chawls)
  * Florentine vermilion red dome & Colaba sandstone (Taj Mahal Palace)
  * Deep marine Arabian Sea water & dark asphalt with crisp yellow/black BMC curbs
- Calibrates Nishita tropical golden-hour sky and direct sunlight with rich shadow depth.
- Sets Filmic Medium High Contrast color management to eliminate washed-out/pale appearance.
- Renders all 6 architectural master views at 1920x1080 Full HD.
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def calibrate_mumbai_lighting_and_atmosphere():
    print("[Lighting] Calibrating vibrant tropical Mumbai golden sunlight and sky...")
    scene = bpy.context.scene

    # 1. Color Management: Filmic with Medium High Contrast
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -1.15
    scene.view_settings.gamma = 1.0

    # 2. Nishita Tropical Atmosphere
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    w_nt = world.node_tree
    w_nt.nodes.clear()

    w_out = w_nt.nodes.new("ShaderNodeOutputWorld")
    w_bg = w_nt.nodes.new("ShaderNodeBackground")
    w_nt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

    sky = w_nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_elevation = math.radians(26.0) # Warm tropical afternoon sun
    sky.sun_rotation = math.radians(78.0)  # Direct illumination on East/South faces
    sky.altitude = 10.0
    sky.air_density = 1.02
    sky.ozone_density = 3.2
    w_nt.links.new(sky.outputs['Color'], w_bg.inputs['Color'])
    w_bg.inputs['Strength'].default_value = 0.55 # Stop washing out shadows!

    # 3. Direct Tropical Sunlight
    for s_old_name in ['Sun_Mumbai_Map', 'LAMP_Mumbai_GoldenHour_Sun']:
        s_old = bpy.data.objects.get(s_old_name)
        if s_old:
            bpy.data.objects.remove(s_old, do_unlink=True)

    sun = bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        s_data = bpy.data.lights.new("Sun_Mumbai", type='SUN')
        sun = bpy.data.objects.new("Sun_Mumbai", s_data)
        bpy.context.scene.collection.objects.link(sun)

    sun.data.energy = 4.2
    sun.data.color = (1.0, 0.90, 0.76) # Warm golden sunlight
    sun.data.angle = math.radians(0.8) # Crisp architectural shadows
    sun.rotation_euler = Euler((math.radians(46.0), math.radians(14.0), math.radians(65.0)), 'XYZ')

def build_rich_pbr_shader(name, wall_rgb, window_rgb, floor_height=3.2, roughness=0.75, metal=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1100, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (800, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-1400, 0)

    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-1150, 200)
    links.new(geom.outputs['Position'], sep.inputs['Vector'])

    mod_z = nodes.new("ShaderNodeMath")
    mod_z.location = (-950, 200)
    mod_z.operation = 'MODULO'
    mod_z.inputs[1].default_value = floor_height
    links.new(sep.outputs['Z'], mod_z.inputs[0])

    map_norm = nodes.new("ShaderNodeMapRange")
    map_norm.location = (-750, 200)
    map_norm.inputs['From Min'].default_value = 0.0
    map_norm.inputs['From Max'].default_value = floor_height
    map_norm.inputs['To Min'].default_value = 0.0
    map_norm.inputs['To Max'].default_value = 1.0
    links.new(mod_z.outputs['Value'], map_norm.inputs['Value'])

    ramp_band = nodes.new("ShaderNodeValToRGB")
    ramp_band.location = (-500, 200)
    ramp_band.color_ramp.interpolation = 'CONSTANT'
    ramp_band.color_ramp.elements[0].position = 0.0
    ramp_band.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    e1 = ramp_band.color_ramp.elements.new(0.85 / floor_height)
    e1.color = (1.0, 1.0, 1.0, 1.0)
    e2 = ramp_band.color_ramp.elements.new(2.30 / floor_height)
    e2.color = (0.0, 0.0, 0.0, 1.0)
    links.new(map_norm.outputs['Result'], ramp_band.inputs['Factor'])

    brick = nodes.new("ShaderNodeTexBrick")
    brick.location = (-500, -150)
    brick.inputs['Scale'].default_value = 0.40
    brick.inputs['Mortar Size'].default_value = 0.16
    brick.inputs['Brick Width'].default_value = 1.8
    brick.inputs['Row Height'].default_value = 1.0
    links.new(geom.outputs['Position'], brick.inputs['Vector'])

    math_mult = nodes.new("ShaderNodeMath")
    math_mult.location = (-250, 50)
    math_mult.operation = 'MULTIPLY'
    links.new(ramp_band.outputs['Color'], math_mult.inputs[0])
    links.new(brick.outputs['Color'], math_mult.inputs[1])

    mix_col = nodes.new("ShaderNodeMix")
    mix_col.location = (50, 150)
    mix_col.data_type = 'RGBA'
    mix_col.inputs[6].default_value = wall_rgb
    mix_col.inputs[7].default_value = window_rgb
    links.new(math_mult.outputs['Value'], mix_col.inputs[0])
    links.new(mix_col.outputs[2], bsdf.inputs['Base Color'])

    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (50, -100)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = roughness
    mix_rough.inputs[3].default_value = 0.08
    links.new(math_mult.outputs['Value'], mix_rough.inputs[0])
    links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

    bsdf.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.65
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.65
    bsdf.inputs['IOR'].default_value = 1.52

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (150, -350)
    noise.inputs['Scale'].default_value = 25.0
    links.new(geom.outputs['Position'], noise.inputs['Vector'])

    bump = nodes.new("ShaderNodeBump")
    bump.location = (450, -300)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.05
    links.new(noise.outputs['Factor'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def apply_rich_mumbai_colors():
    print("[Colors] Applying rich, saturated, authentic Mumbai colors across all architectural shaders...")

    # 1. Marine Drive Art Deco Tropical Palette (Deep, warm, saturated heritage pastels)
    mat_deco_ochre = build_rich_pbr_shader(
        "MAT_RealMumbai_ArtDeco_Ochre",
        wall_rgb=(0.76, 0.46, 0.16, 1.0), # Rich turmeric mustard ochre
        window_rgb=(0.04, 0.05, 0.07, 1.0),
        floor_height=3.2,
        roughness=0.70
    )
    mat_deco_seafoam = build_rich_pbr_shader(
        "MAT_RealMumbai_ArtDeco_Seafoam",
        wall_rgb=(0.22, 0.52, 0.42, 1.0), # Deep marine seafoam mint
        window_rgb=(0.04, 0.05, 0.07, 1.0),
        floor_height=3.2,
        roughness=0.70
    )
    mat_deco_peach = build_rich_pbr_shader(
        "MAT_RealMumbai_ArtDeco_Peach",
        wall_rgb=(0.74, 0.36, 0.22, 1.0), # Rich terracotta coral peach
        window_rgb=(0.04, 0.05, 0.07, 1.0),
        floor_height=3.2,
        roughness=0.70
    )
    mat_deco_cream = build_rich_pbr_shader(
        "MAT_RealMumbai_ArtDeco_Cream",
        wall_rgb=(0.82, 0.74, 0.58, 1.0), # Warm antique ivory cream
        window_rgb=(0.04, 0.05, 0.07, 1.0),
        floor_height=3.2,
        roughness=0.70
    )

    deco_map = {
        "ARTDECO_MarineDrive_Kapoor_Mahal": mat_deco_cream,
        "ARTDECO_MarineDrive_Zaver_Mahal": mat_deco_seafoam,
        "ARTDECO_MarineDrive_Keval_Mahal": mat_deco_ochre,
        "ARTDECO_MarineDrive_Soona_Mahal": mat_deco_peach,
        "ARTDECO_MarineDrive_Empress_Court": mat_deco_cream,
        "ARTDECO_MarineDrive_Shiv_Shanti_Bhuvan": mat_deco_ochre,
        "ARTDECO_MarineDrive_Rajab_Mahal": mat_deco_peach,
        "ARTDECO_MarineDrive_Fairlawn": mat_deco_seafoam,
        "ARTDECO_MarineDrive_Gool_Mahal": mat_deco_cream,
        "ARTDECO_MarineDrive_Sea_Green_Hotel": mat_deco_ochre,
        "ARTDECO_MarineDrive_Chateau_Marine": mat_deco_seafoam,
        "ARTDECO_MarineDrive_Ocean_View": mat_deco_cream
    }
    for b_name, mat in deco_map.items():
        o = bpy.data.objects.get(b_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat)
            o.hide_render = False

    # 2. Arabian Sea: Deep Marine Ocean Blue
    mat_sea = bpy.data.materials.get("MAT_Arabian_Sea")
    if not mat_sea:
        mat_sea = bpy.data.materials.new("MAT_Arabian_Sea")
    mat_sea.use_nodes = True
    s_bsdf = mat_sea.node_tree.nodes.get("Principled BSDF")
    if s_bsdf:
        s_bsdf.inputs['Base Color'].default_value = (0.012, 0.055, 0.14, 1.0) # Deep marine ocean blue
        s_bsdf.inputs['Roughness'].default_value = 0.06
        s_bsdf.inputs['IOR'].default_value = 1.333
        if 'Specular IOR Level' in s_bsdf.inputs:
            s_bsdf.inputs['Specular IOR Level'].default_value = 0.70

    # 3. Roads: Deep Charcoal Pitch Black Asphalt & Bright BMC Curbs
    mat_asphalt = bpy.data.materials.get("MAT_RealRoad_Asphalt")
    if not mat_asphalt:
        mat_asphalt = bpy.data.materials.new("MAT_RealRoad_Asphalt")
    mat_asphalt.use_nodes = True
    a_bsdf = mat_asphalt.node_tree.nodes.get("Principled BSDF")
    if a_bsdf:
        a_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0) # Deep dark pitch asphalt
        a_bsdf.inputs['Roughness'].default_value = 0.65

    for rd_name in ["ROAD_MarineDrive_NetajiSubhashRoad", "ROAD_Girgaon_Chawl_Gully"]:
        rd = bpy.data.objects.get(rd_name)
        if rd:
            rd.data.materials.clear()
            rd.data.materials.append(mat_asphalt)

    # Promenade Seawall
    sw_md = bpy.data.objects.get("SEAWALL_MarineDrive_Barrier")
    if sw_md:
        mat_conc = bpy.data.materials.get("MAT_Promenade_Concrete")
        if not mat_conc:
            mat_conc = bpy.data.materials.new("MAT_Promenade_Concrete")
        mat_conc.use_nodes = True
        c_bsdf = mat_conc.node_tree.nodes.get("Principled BSDF")
        if c_bsdf:
            c_bsdf.inputs['Base Color'].default_value = (0.42, 0.41, 0.39, 1.0) # Weathered marine granite
            c_bsdf.inputs['Roughness'].default_value = 0.85
        sw_md.data.materials.clear()
        sw_md.data.materials.append(mat_conc)

    # 4. CSMT Victoria Terminus: Rich Yellow Malad Sandstone & Kurla Basalt
    mat_csmt_sandstone = build_rich_pbr_shader(
        "MAT_RealMumbai_HeritageGothic_PBR",
        wall_rgb=(0.65, 0.46, 0.22, 1.0), # Rich golden-ochre Malad sandstone
        window_rgb=(0.04, 0.05, 0.07, 1.0),
        floor_height=4.2,
        roughness=0.86
    )

    mat_tile = bpy.data.materials.get("MAT_RealMumbai_TerracottaTiles")
    if not mat_tile:
        mat_tile = bpy.data.materials.new("MAT_RealMumbai_TerracottaTiles")
    mat_tile.use_nodes = True
    tl_bsdf = mat_tile.node_tree.nodes.get("Principled BSDF")
    if tl_bsdf:
        tl_bsdf.inputs['Base Color'].default_value = (0.58, 0.16, 0.10, 1.0) # Rich terracotta red clay
        tl_bsdf.inputs['Roughness'].default_value = 0.60

    mat_copper = bpy.data.materials.get("MAT_CSMT_VerdigrisDome")
    if not mat_copper:
        mat_copper = bpy.data.materials.new("MAT_CSMT_VerdigrisDome")
    mat_copper.use_nodes = True
    cp_bsdf = mat_copper.node_tree.nodes.get("Principled BSDF")
    if cp_bsdf:
        cp_bsdf.inputs['Base Color'].default_value = (0.18, 0.50, 0.40, 1.0) # Rich oxidized verdigris patina
        cp_bsdf.inputs['Metallic'].default_value = 0.40
        cp_bsdf.inputs['Roughness'].default_value = 0.45

    csmt = bpy.data.objects.get("LANDMARK_CSMT_Masterpiece")
    if csmt:
        csmt.data.materials.clear()
        csmt.data.materials.append(mat_csmt_sandstone)
        csmt.data.materials.append(mat_tile)
        csmt.data.materials.append(mat_copper)
        for poly in csmt.data.polygons:
            cz = poly.center.z
            cx = abs(poly.center.x)
            if cz > 49.0 and cx > 45.0:
                poly.material_index = 2 # Verdigris spires
            elif cz > 56.0 and cz < 83.0 and cx < 25.0:
                poly.material_index = 1 # Terracotta dome
            else:
                poly.material_index = 0 # Malad sandstone

    # 5. Worli & Lower Parel Megatowers: Deep Reflective Marine Cyan-Navy Glass
    mat_glass = build_rich_pbr_shader(
        "MAT_RealMumbai_Megatower_CurtainWall",
        wall_rgb=(0.04, 0.14, 0.26, 1.0), # Deep marine navy
        window_rgb=(0.14, 0.36, 0.54, 1.0), # High-specular cyan reflection
        floor_height=3.6,
        roughness=0.06,
        metal=0.82
    )
    for c_name in ["Skyscrapers_Megatower_Corridor"]:
        c = bpy.data.collections.get(c_name)
        if c:
            for o in c.objects:
                if o.type == 'MESH':
                    o.data.materials.clear()
                    o.data.materials.append(mat_glass)
                    o.hide_render = False

    # 6. Nariman Point CBD: Weathered Architectural Concrete & Dark Ribbon Windows
    mat_nariman = build_rich_pbr_shader(
        "MAT_RealMumbai_Modernist_Concrete_PBR",
        wall_rgb=(0.48, 0.47, 0.45, 1.0), # Weathered architectural formwork concrete
        window_rgb=(0.05, 0.08, 0.12, 1.0), # Deep tinted bronze ribbon glass
        floor_height=3.6,
        roughness=0.78
    )
    nariman_bldgs = [
        "LANDMARK_AirIndia_Tower", "LANDMARK_AirIndia_Podium", "LANDMARK_AirIndia_Crown",
        "LANDMARK_ExpressTowers_Tower", "LANDMARK_ExpressTowers_Podium", "LANDMARK_ExpressTowers_Core",
        "LANDMARK_Trident_Tower", "LANDMARK_TheOberoi_Wing",
        "BLDG_NarimanPoint_Maker_Chambers_IV", "BLDG_NarimanPoint_Maker_Chambers_V",
        "BLDG_NarimanPoint_Maker_Chambers_VI", "BLDG_NarimanPoint_Free_Press_House",
        "BLDG_NarimanPoint_Mittal_Court", "BLDG_NarimanPoint_Bajaj_Bhavan",
        "BLDG_NarimanPoint_Nariman_Bhavan", "BLDG_NarimanPoint_Mafatlal_Centre",
        "BLDG_NarimanPoint_Earnest_House", "BLDG_NarimanPoint_Raheja_Chambers",
        "BLDG_NarimanPoint_State_Bank_Bhavan", "BLDG_NarimanPoint_IDBI_Tower_Nariman"
    ]
    for b_name in nariman_bldgs:
        o = bpy.data.objects.get(b_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(mat_nariman)
            o.hide_render = False

    # 7. Girgaon Traditional Chawl Quarter: Weathered Turmeric Lime Plaster, Teak Wood & Mangalore Red Tiles
    mat_chawl_ochre = build_rich_pbr_shader(
        "MAT_RealMumbai_Chawl_Plaster_PBR",
        wall_rgb=(0.68, 0.48, 0.24, 1.0), # Weathered turmeric lime plaster
        window_rgb=(0.14, 0.09, 0.05, 1.0),
        floor_height=2.9,
        roughness=0.88
    )
    mat_wood = bpy.data.materials.get("MAT_Chawl_Teak_Timber")
    if not mat_wood:
        mat_wood = bpy.data.materials.new("MAT_Chawl_Teak_Timber")
    mat_wood.use_nodes = True
    w_bsdf = mat_wood.node_tree.nodes.get("Principled BSDF")
    if w_bsdf:
        w_bsdf.inputs['Base Color'].default_value = (0.16, 0.09, 0.04, 1.0) # Deep dark Indian teak wood
        w_bsdf.inputs['Roughness'].default_value = 0.72

    mat_tin = bpy.data.materials.get("MAT_Chawl_Corrugated_Chhajja")
    if not mat_tin:
        mat_tin = bpy.data.materials.new("MAT_Chawl_Corrugated_Chhajja")
    mat_tin.use_nodes = True
    tn_bsdf = mat_tin.node_tree.nodes.get("Principled BSDF")
    if tn_bsdf:
        tn_bsdf.inputs['Base Color'].default_value = (0.35, 0.38, 0.40, 1.0) # Weathered zinc metal
        tn_bsdf.inputs['Metallic'].default_value = 0.85
        tn_bsdf.inputs['Roughness'].default_value = 0.45

    mat_sintex = bpy.data.materials.get("MAT_RealMumbai_WaterTank_PBR")
    if not mat_sintex:
        mat_sintex = bpy.data.materials.new("MAT_RealMumbai_WaterTank_PBR")
    mat_sintex.use_nodes = True
    sx_bsdf = mat_sintex.node_tree.nodes.get("Principled BSDF")
    if sx_bsdf:
        sx_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0) # Pitch black Sintex plastic
        sx_bsdf.inputs['Roughness'].default_value = 0.30

    chawl_mats = [mat_chawl_ochre, mat_deco_seafoam, mat_deco_peach, mat_deco_cream, mat_chawl_ochre, mat_deco_ochre]
    chawl_names = [
        "CHAWL_Girgaon_Lokmanya_1", "CHAWL_Girgaon_Ganesh_2", "CHAWL_Girgaon_Shree_3",
        "CHAWL_Girgaon_Shivaji_4", "CHAWL_Girgaon_Tilak_5", "CHAWL_Girgaon_Sardar_6"
    ]
    for idx, c_name in enumerate(chawl_names):
        o = bpy.data.objects.get(c_name)
        if o:
            o.data.materials.clear()
            o.data.materials.append(chawl_mats[idx % len(chawl_mats)])
            o.data.materials.append(mat_tile)
            o.data.materials.append(mat_wood)
            o.data.materials.append(mat_tin)
            o.data.materials.append(mat_sintex)
            o.hide_render = False

    # 8. Apollo Bunder: Gateway of India & Taj Mahal Palace
    # Purge any remaining clipping proxy faces from ARCH_MUMBAI_HeritageGothic
    gw_center = Vector((174.17, -113.10, 4.0))
    taj_center = Vector((94.17, -163.10, 4.0))
    for obj_name in ["ARCH_MUMBAI_HeritageGothic", "ARCH_MUMBAI_Rooftop_Tar", "ARCH_MUMBAI_Rooftop_WaterTanks", "ROOFTOP_Fixtures_Citywide_Master"]:
        p_obj = bpy.data.objects.get(obj_name)
        if p_obj and p_obj.type == 'MESH':
            bm = bmesh.new()
            bm.from_mesh(p_obj.data)
            bm.faces.ensure_lookup_table()
            del_f = [f for f in bm.faces if (p_obj.matrix_world @ f.calc_center_median() - gw_center).length < 32.0 or (p_obj.matrix_world @ f.calc_center_median() - taj_center).length < 45.0]
            if del_f:
                bmesh.ops.delete(bm, geom=del_f, context='FACES_ONLY')
                bm.to_mesh(p_obj.data)
            bm.free()

    # Authentic Yellow Kharodi Basalt stone (Rich golden-brown ashlar masonry)
    mat_basalt = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt_Authentic")
    if not mat_basalt:
        mat_basalt = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt_Authentic")
    mat_basalt.use_nodes = True
    b_nodes = mat_basalt.node_tree.nodes
    b_links = mat_basalt.node_tree.links
    b_nodes.clear()
    out_b = b_nodes.new("ShaderNodeOutputMaterial")
    bsdf_b = b_nodes.new("ShaderNodeBsdfPrincipled")
    b_links.new(bsdf_b.outputs['BSDF'], out_b.inputs['Surface'])

    tc_b = b_nodes.new("ShaderNodeTexCoord")
    brick_b = b_nodes.new("ShaderNodeTexBrick")
    brick_b.inputs['Scale'].default_value = 0.8
    brick_b.inputs['Mortar Size'].default_value = 0.015
    brick_b.inputs['Brick Width'].default_value = 2.6
    brick_b.inputs['Row Height'].default_value = 0.75
    brick_b.inputs['Color1'].default_value = (0.58, 0.42, 0.22, 1.0) # Deep golden Kharodi basalt
    brick_b.inputs['Color2'].default_value = (0.48, 0.34, 0.18, 1.0) # Weathered stone
    brick_b.inputs['Mortar'].default_value = (0.24, 0.20, 0.15, 1.0) # Lime mortar
    b_links.new(tc_b.outputs['Object'], brick_b.inputs['Vector'])
    b_links.new(brick_b.outputs['Color'], bsdf_b.inputs['Base Color'])

    bump_b = b_nodes.new("ShaderNodeBump")
    bump_b.inputs['Strength'].default_value = 0.35
    bump_b.inputs['Distance'].default_value = 0.04
    b_links.new(brick_b.outputs['Fac'], bump_b.inputs['Height'])
    b_links.new(bump_b.outputs['Normal'], bsdf_b.inputs['Normal'])
    bsdf_b.inputs['Roughness'].default_value = 0.86

    # Gold Spire
    mat_gold = bpy.data.materials.get("Mat_Heritage_Gold_Finial_Authentic")
    if not mat_gold:
        mat_gold = bpy.data.materials.new("Mat_Heritage_Gold_Finial_Authentic")
    mat_gold.use_nodes = True
    g_bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.95, 0.78, 0.20, 1.0)
        g_bsdf.inputs['Metallic'].default_value = 0.95
        g_bsdf.inputs['Roughness'].default_value = 0.18

    gw = bpy.data.objects.get("LANDMARK_Gateway_of_India")
    if gw:
        gw.data.materials.clear()
        gw.data.materials.append(mat_basalt)
        gw.data.materials.append(mat_gold)
        for poly in gw.data.polygons:
            poly.material_index = 1 if poly.center.z > 33.5 else 0
        gw.hide_render = False

    # Taj Mahal Palace: Rich Vermilion Florentine Dome & Warm Colaba Sandstone
    mat_taj_cream = bpy.data.materials.get("Mat_Taj_Mahal_Palace_Cream")
    if not mat_taj_cream:
        mat_taj_cream = bpy.data.materials.new("Mat_Taj_Mahal_Palace_Cream")
    mat_taj_cream.use_nodes = True
    tc_bsdf = mat_taj_cream.node_tree.nodes.get("Principled BSDF")
    if tc_bsdf:
        tc_bsdf.inputs['Base Color'].default_value = (0.76, 0.68, 0.56, 1.0) # Warm Colaba sandstone
        tc_bsdf.inputs['Roughness'].default_value = 0.72

    mat_taj_red = bpy.data.materials.get("Mat_Taj_Red_Dome_Authentic")
    if not mat_taj_red:
        mat_taj_red = bpy.data.materials.new("Mat_Taj_Red_Dome_Authentic")
    mat_taj_red.use_nodes = True
    tr_bsdf = mat_taj_red.node_tree.nodes.get("Principled BSDF")
    if tr_bsdf:
        tr_bsdf.inputs['Base Color'].default_value = (0.50, 0.06, 0.04, 1.0) # Deep Florentine vermilion red
        tr_bsdf.inputs['Roughness'].default_value = 0.32

    mat_taj_tower = bpy.data.materials.get("Mat_Taj_Tower_White")
    if not mat_taj_tower:
        mat_taj_tower = bpy.data.materials.new("Mat_Taj_Tower_White")
    mat_taj_tower.use_nodes = True
    tt_bsdf = mat_taj_tower.node_tree.nodes.get("Principled BSDF")
    if tt_bsdf:
        tt_bsdf.inputs['Base Color'].default_value = (0.84, 0.82, 0.78, 1.0) # Architectural concrete
        tt_bsdf.inputs['Roughness'].default_value = 0.60

    taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
    if taj:
        taj.data.materials.clear()
        taj.data.materials.append(mat_taj_cream)
        taj.data.materials.append(mat_taj_red)
        taj.data.materials.append(mat_taj_tower)
        for poly in taj.data.polygons:
            cz = poly.center.z
            cx = poly.center.x
            cy = poly.center.y
            if cz > 45.0 and (cx**2 + cy**2)**0.5 < 20.0:
                poly.material_index = 1
            elif cz > 35.0:
                poly.material_index = 2
            else:
                poly.material_index = 0
        taj.hide_render = False

    # Plaza Flagstones
    mat_plaza = bpy.data.materials.get("MAT_Plaza_Basalt_Flagstone")
    if not mat_plaza:
        mat_plaza = bpy.data.materials.new("MAT_Plaza_Basalt_Flagstone")
    mat_plaza.use_nodes = True
    p_bsdf = mat_plaza.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs['Base Color'].default_value = (0.18, 0.17, 0.16, 1.0) # Dark basalt flagstones
        p_bsdf.inputs['Roughness'].default_value = 0.82

    plz = bpy.data.objects.get("PLAZA_Apollo_Bunder_Harbour_Jetty")
    if plz:
        plz.data.materials.clear()
        plz.data.materials.append(mat_plaza)

    # Palm Trees
    mat_frond = bpy.data.materials.get("MAT_Palm_GreenFronds")
    if mat_frond and mat_frond.node_tree:
        bsdf = mat_frond.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.05, 0.18, 0.04, 1.0) # Rich tropical green
            bsdf.inputs['Roughness'].default_value = 0.45

    mat_trunk = bpy.data.materials.get("MAT_Palm_TrunkBark")
    if mat_trunk and mat_trunk.node_tree:
        bsdf = mat_trunk.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.14, 0.09, 0.05, 1.0) # Dark ringed coconut bark

def render_all_rich_views():
    cams = [
        {"id": "arch_1_marinedrive_artdeco", "name": "Cam_Arch_1_MarineDrive_ArtDeco", "title": "Marine Drive Art Deco Heritage Row"},
        {"id": "arch_2_csmt_fort_gothic", "name": "Cam_Arch_2_Fort_VictorianHeritage", "title": "CSMT Victoria Terminus & Fort Gothic"},
        {"id": "arch_3_worli_megatowers", "name": "Cam_Arch_3_Worli_MegatowerHighRise", "title": "Worli & Lower Parel Megatowers"},
        {"id": "arch_4_narimanpoint_waterfront", "name": "Cam_Arch_4_NarimanPoint_Waterfront", "title": "Nariman Point Commercial CBD"},
        {"id": "arch_5_girgaon_chawls", "name": "Cam_Arch_5_Girgaon_ChawlVernacular", "title": "Girgaon Traditional Chawl Quarter"},
        {"id": "arch_6_apollobunder_gateway_taj", "name": "Cam_Arch_6_ApolloBunder_HeritagePlaza", "title": "Apollo Bunder Gateway & Taj Mahal Palace"}
    ]

    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'

    scene.use_nodes = False
    if hasattr(scene.render, "use_compositing"):
        scene.render.use_compositing = False

    rendered = []
    for idx, c in enumerate(cams, 1):
        cam_obj = bpy.data.objects.get(c["name"])
        if not cam_obj:
            continue
        scene.camera = cam_obj
        fname = f"{c['id']}.png"
        fpath = os.path.join(OUTPUT_DIR, fname)
        scene.render.filepath = fpath

        print(f"  Rendering [{idx}/{len(cams)}] {c['title']} at 1080p...")
        bpy.ops.render.render(write_still=True)
        sz = os.path.getsize(fpath)
        print(f"    Saved: {fpath} ({sz / 1024:.1f} KB)")
        rendered.append((c["title"], fpath, sz))

    return rendered

def main():
    print("========================================================================")
    print("GRAI — MUMBAI DIGITAL TWIN: AUTHENTIC RICH COLOR RE-CALIBRATION PIPELINE")
    print("========================================================================")
    calibrate_mumbai_lighting_and_atmosphere()
    apply_rich_mumbai_colors()
    rendered = render_all_rich_views()

    # Save upgraded .blend
    blend_path = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Save] Upgraded Digital Twin saved to {blend_path}")

    print("========================================================================")
    print("Re-render Summary (Vibrant Mumbai Colors):")
    for title, path, sz in rendered:
        print(f"  * {title}: {path} ({sz / 1024:.1f} KB)")
    print("========================================================================")

if __name__ == "__main__":
    main()
