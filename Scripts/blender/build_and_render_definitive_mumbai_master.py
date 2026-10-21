#!/usr/bin/env python3
"""
GRAI — Definitive Master Real-World Mumbai Digital Twin & Road Network Engine
=============================================================================
Deploys 100% geographically authentic surveyed Mumbai infrastructure:
1. Exact surveyed 1:1 scale road and path network from OSM/GIS (5,830 segments).
2. Deep PBR pitch-black asphalt (specular 0.06 to eliminate sky-glare bleach),
   thermoplastic white lane markings, yellow median, and fine aggregate bump.
3. Authentic BMC 3D kerbstones (alternating 0.60m Canary Yellow and Deep Black)
   and interlocking terracotta red/cement grey sidewalk paver blocks.
4. Dedicated pedestrian zones:
   - Marine Drive 12.0m seaside promenade with concrete seawall coping & tetrapods.
   - Apollo Bunder 65m x 45m hand-cut Kharodi basalt flagstone plaza.
5. Rich, saturated, authentic Mumbai architectural colors and PBR materials:
   - Gateway of India: Genuine golden-brown Kharodi basalt ashlar stone & gold finials.
   - Taj Mahal Palace: Buff Colaba sandstone, rich crimson Florentine dome, limestone tower.
   - CSMT Victoria Terminus: Golden Malad sandstone, marble arcades, verdigris copper dome.
   - Marine Drive Art Deco: UNESCO World Heritage turmeric, seafoam, terracotta & cream stuccos with bronze window casements.
   - Worli Megatowers: Deep marine navy solar-control double glazing & structural aluminum.
   - Nariman Point Waterfront: Modernist concrete brise-soleil & dark bronze ribbon glazing at +3.8m grade.
   - Girgaon Chawls: Aged lime-wash plaster, teakwood verandas, Mangalore roof tiles, Sintex water tanks.
6. Calibrated single tropical sun with Filmic Medium High Contrast (ZERO washed-out tones).
7. Strict constraint: NO characters, NO pedestrians, NO vehicles, NO traffic, NO living entities.
"""

import os
import sys
import json
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)
BLEND_PATH = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")

sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("=" * 80)
    print("GRAI — DEPLOYING DEFINITIVE MASTER REAL-WORLD MUMBAI DIGITAL TWIN")
    print("=" * 80)

    # 0. Rebuild surveyed roads with strict exclusion zones (no roads cutting across Gateway plaza)
    try:
        import build_mumbai_perfect_roads_and_paths
        build_mumbai_perfect_roads_and_paths.main()
    except Exception as e:
        print(f"[RoadRebuild] Warning running road generator: {e}")

    # 1. Purge unwanted entities, rogue lights, and stray markers
    cleanup_and_enforce_constraints()

    # 2. Setup single physical tropical sunlight & Filmic tone mapping
    setup_lighting_and_filmic()

    # 3. Build & apply deep PBR materials across all road and architectural networks
    materials = build_deep_authentic_pbr_materials()

    # 4. Refine bespoke architectural landmarks (Gateway, Taj, CSMT, Art Deco, Worli, Nariman, Girgaon)
    refine_architectural_landmarks(materials)

    # 5. Fix terrain, sea level, and plinth elevations (prevent submerged buildings)
    fix_terrain_and_plinths(materials)

    # 6. Configure 8 master cameras for iconic architectural & street perspectives
    cams = configure_masterpiece_cameras()

    # 7. Save updated digital twin blend
    print(f"[Save] Saving master blend to {BLEND_PATH}...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print("[Save] Successfully saved master Digital Twin!")

    # 8. Render all 8 perspectives in Cycles
    render_all_perspectives(cams)

# ---------------------------------------------------------------------------
# 1. Cleanup & Constraint Enforcement
# ---------------------------------------------------------------------------
def cleanup_and_enforce_constraints():
    print("[CleanUp] Purging duplicate objects, rogue lights, obstacles, and enforcing strict constraints...")
    
    # 0. Purge all duplicate objects ending in .001, .002, .003, .004
    dup_removed = 0
    for o in list(bpy.data.objects):
        if o.name.endswith(('.001', '.002', '.003', '.004')):
            bpy.data.objects.remove(o, do_unlink=True)
            dup_removed += 1
    if dup_removed > 0:
        print(f"  Purged {dup_removed} duplicate overlapping objects (.001/.002) to resolve z-fighting!")

    # Rogue daytime floodlights and duplicate suns
    rogue_lights = [
        "Light_Apollo_Harbour_Bounce", "LIGHT_Fill_GoldenHour",
        "LIGHT_Gateway_Flood_East", "LIGHT_Gateway_Flood_West",
        "LIGHT_Taj_Flood_Facade", "LIGHT_Taj_Dome_Glow",
        "Sun_Mumbai_Map", "LAMP_Mumbai_GoldenHour_Sun"
    ]
    for l_name in rogue_lights:
        l_obj = bpy.data.objects.get(l_name)
        if l_obj:
            bpy.data.objects.remove(l_obj, do_unlink=True)

    # Legacy barrier mesh and floating stray curbs
    for o in list(bpy.data.objects):
        if o.name == "SEAWALL_MarineDrive_Barrier" or o.name.startswith("BMC_Curb_MD_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # Purge stray faces of ARCH_MUMBAI_HeritageGothic in Apollo Bunder
    goth = bpy.data.objects.get("ARCH_MUMBAI_HeritageGothic")
    if goth and goth.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(goth.data)
        bm.faces.ensure_lookup_table()
        del_f = [f for f in bm.faces if 50.0 < f.calc_center_median().x < 250.0 and -250.0 < f.calc_center_median().y < -50.0]
        if del_f:
            bmesh.ops.delete(bm, geom=del_f, context='FACES_ONLY')
            bm.to_mesh(goth.data)
            print(f"  Purged {len(del_f)} stray gothic portal faces in Apollo Bunder plaza!")
        bm.free()

    # Strict constraint: NO characters, pedestrians, vehicles, traffic, living entities
    unwanted_kws = ["raghunath", "character", "pedestrian", "vehicle", "car", "traffic", "human", "avatar", "npc"]
    for o in list(bpy.data.objects):
        if any(kw in o.name.lower() for kw in unwanted_kws) and o.type != 'CAMERA':
            bpy.data.objects.remove(o, do_unlink=True)

    # Remove stray player spawn markers visible in renders
    for spawn_name in ["PLAYER_SPAWN_MarineDrive_Promenade", "PLAYER_SPAWN_Gateway_Esplanade"]:
        sp = bpy.data.objects.get(spawn_name)
        if sp:
            bpy.data.objects.remove(sp, do_unlink=True)

    # Hide duplicate/floating terrain polygons
    for t_name in ['Terrain', 'Terrain_envelope', 'TERRAIN_Mumbai_Peninsula_Landmass.001']:
        t_obj = bpy.data.objects.get(t_name)
        if t_obj:
            t_obj.hide_render = True
            t_obj.hide_viewport = True

# ---------------------------------------------------------------------------
# 2. Lighting & Filmic Color Management
# ---------------------------------------------------------------------------
def setup_lighting_and_filmic():
    print("[Lighting] Calibrating single physical tropical sun & Filmic tonemapping...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.preview_samples = 16
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.08

    # Filmic tonemapping with rich contrast
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -0.85
    scene.view_settings.gamma = 1.0

    # Calibrate World Nishita Sky
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
    sky.sun_elevation = math.radians(30.0)
    sky.sun_rotation = math.radians(72.0)
    sky.altitude = 5.0
    sky.air_density = 1.05
    sky.aerosol_density = 1.6 # Natural tropical Mumbai atmospheric haze
    sky.ozone_density = 3.5
    w_nt.links.new(sky.outputs['Color'], w_bg.inputs['Color'])
    # Moderate background strength to prevent washing out midtones & asphalt
    w_bg.inputs['Strength'].default_value = 0.32

    # Calibrated single Sun_Mumbai
    sun = bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        s_data = bpy.data.lights.new("Sun_Mumbai", type='SUN')
        sun = bpy.data.objects.new("Sun_Mumbai", s_data)
        bpy.context.scene.collection.objects.link(sun)
    sun.data.energy = 3.0
    sun.data.color = (1.0, 0.90, 0.76) # Warm tropical sunlight
    sun.data.angle = math.radians(1.2) # Soft realistic penumbra
    sun.rotation_euler = Euler((math.radians(40.0), math.radians(12.0), math.radians(68.0)), 'XYZ')

# ---------------------------------------------------------------------------
# 3. Deep Authentic PBR Shaders
# ---------------------------------------------------------------------------
def build_deep_authentic_pbr_materials():
    print("[Materials] Engineering rich, deep PBR materials with zero washed-out tones...")
    materials = {}

    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # -----------------------------------------------------------------------
    # A. Pitch-Black Bitumen Tropical Road Asphalt
    # -----------------------------------------------------------------------
    # Specular 0.06 is CRITICAL: eliminates diffuse sky-glare bleaching!
    mat_asphalt = get_or_create_mat("MAT_RealMumbai_Road_Asphalt_Master")
    nt = mat_asphalt.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    bsdf.inputs['Base Color'].default_value = (0.026, 0.026, 0.030, 1.0) # Deep charcoal pitch asphalt
    bsdf.inputs['Roughness'].default_value = 0.78
    bsdf.inputs['Metallic'].default_value = 0.0
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.06
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.06

    # Micro-aggregate stone chipping bump
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 140.0
    noise.inputs['Detail'].default_value = 10.0
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.005
    nt.links.new(noise.outputs['Factor'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    materials["Asphalt"] = mat_asphalt
    # Mirror to other asphalt materials
    for extra_name in ['MAT_MarineDrive_Asphalt_Master', 'MAT_RealRoad_Asphalt', 'MAT_SeaLink_HighwayAsphalt']:
        em = get_or_create_mat(extra_name)
        em.node_tree.nodes.clear()
        e_out = em.node_tree.nodes.new("ShaderNodeOutputMaterial")
        e_bsdf = em.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
        em.node_tree.links.new(e_bsdf.outputs['BSDF'], e_out.inputs['Surface'])
        e_bsdf.inputs['Base Color'].default_value = (0.026, 0.026, 0.030, 1.0)
        e_bsdf.inputs['Roughness'].default_value = 0.78
        if 'Specular IOR Level' in e_bsdf.inputs:
            e_bsdf.inputs['Specular IOR Level'].default_value = 0.06
        elif 'Specular' in e_bsdf.inputs:
            e_bsdf.inputs['Specular'].default_value = 0.06

    # -----------------------------------------------------------------------
    # B. Road Markings (Thermoplastic White & Median Yellow)
    # -----------------------------------------------------------------------
    mat_white = get_or_create_mat("MAT_Road_White_Markings")
    nt = mat_white.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.94, 0.94, 0.92, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.45
    materials["White"] = mat_white

    mat_yellow = get_or_create_mat("MAT_Road_Yellow_Median")
    nt = mat_yellow.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.92, 0.68, 0.04, 1.0) # Saturated Indian median yellow
    bsdf.inputs['Roughness'].default_value = 0.38
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.40
    materials["Yellow"] = mat_yellow

    # -----------------------------------------------------------------------
    # C. Iconic BMC Kerbstones (Alternating 0.60m Canary Yellow & Black)
    # -----------------------------------------------------------------------
    mat_curb = get_or_create_mat("MAT_RealMumbai_BMC_Curb_Stones")
    nt = mat_curb.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    c_coord = nt.nodes.new("ShaderNodeTexCoord")
    c_sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(c_coord.outputs['UV'], c_sep.inputs['Vector'])

    c_mod = nt.nodes.new("ShaderNodeMath")
    c_mod.operation = 'MODULO'
    c_mod.inputs[1].default_value = 1.20 # 0.60m Yellow + 0.60m Black
    nt.links.new(c_sep.outputs['Y'], c_mod.inputs[0])

    c_comp = nt.nodes.new("ShaderNodeMath")
    c_comp.operation = 'LESS_THAN'
    c_comp.inputs[1].default_value = 0.60
    nt.links.new(c_mod.outputs['Value'], c_comp.inputs[0])

    c_mix = nt.nodes.new("ShaderNodeMix")
    c_mix.data_type = 'RGBA'
    c_mix.inputs[6].default_value = (0.04, 0.04, 0.05, 1.0) # Deep Coal Black
    c_mix.inputs[7].default_value = (0.92, 0.68, 0.04, 1.0) # Canary Yellow
    nt.links.new(c_comp.outputs['Value'], c_mix.inputs[0])
    nt.links.new(c_mix.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.58
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.18
    materials["Curb"] = mat_curb

    # Dedicated black/yellow individual curb materials
    mat_cb = get_or_create_mat("MAT_BMC_Curb_Black")
    mat_cb.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    mat_cy = get_or_create_mat("MAT_BMC_Curb_Yellow")
    mat_cy.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value = (0.92, 0.68, 0.04, 1.0)

    # -----------------------------------------------------------------------
    # D. Pedestrian Sidewalk Uni-Pavers (BMC Terracotta Red & Cement Grey)
    # -----------------------------------------------------------------------
    mat_paver = get_or_create_mat("MAT_RealMumbai_Sidewalk_Pavers")
    nt = mat_paver.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    p_coord = nt.nodes.new("ShaderNodeTexCoord")
    p_brick = nt.nodes.new("ShaderNodeTexBrick")
    p_brick.inputs['Scale'].default_value = 4.5
    p_brick.inputs['Mortar Size'].default_value = 0.03
    p_brick.inputs['Color1'].default_value = (0.48, 0.18, 0.12, 1.0) # Rich BMC terracotta red
    p_brick.inputs['Color2'].default_value = (0.50, 0.48, 0.45, 1.0) # Cement grey
    p_brick.inputs['Mortar'].default_value = (0.16, 0.14, 0.12, 1.0)
    nt.links.new(p_coord.outputs['UV'], p_brick.inputs['Vector'])
    nt.links.new(p_brick.outputs['Color'], bsdf.inputs['Base Color'])

    p_bump = nt.nodes.new("ShaderNodeBump")
    p_bump.inputs['Strength'].default_value = 0.35
    p_bump.inputs['Distance'].default_value = 0.008
    nt.links.new(p_brick.outputs['Fac'], p_bump.inputs['Height'])
    nt.links.new(p_bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.78
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.12
    materials["Pavers"] = mat_paver

    # -----------------------------------------------------------------------
    # E. Hand-Cut Kharodi Basalt Flagstone Plaza (Apollo Bunder)
    # -----------------------------------------------------------------------
    mat_basalt = get_or_create_mat("MAT_RealMumbai_Heritage_Basalt_Flagstone")
    nt = mat_basalt.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    b_coord = nt.nodes.new("ShaderNodeTexCoord")
    b_vor = nt.nodes.new("ShaderNodeTexVoronoi")
    b_vor.feature = 'DISTANCE_TO_EDGE'
    b_vor.inputs['Scale'].default_value = 2.8
    nt.links.new(b_coord.outputs['UV'], b_vor.inputs['Vector'])

    b_ramp = nt.nodes.new("ShaderNodeValToRGB")
    b_ramp.color_ramp.elements[0].position = 0.05
    b_ramp.color_ramp.elements[0].color = (0.12, 0.10, 0.08, 1.0) # Deep dark stone joint
    b_ramp.color_ramp.elements[1].position = 0.22
    b_ramp.color_ramp.elements[1].color = (0.24, 0.21, 0.17, 1.0) # Weathered basalt flagstone
    nt.links.new(b_vor.outputs['Distance'], b_ramp.inputs['Fac'])
    nt.links.new(b_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    b_bump = nt.nodes.new("ShaderNodeBump")
    b_bump.inputs['Strength'].default_value = 0.42
    b_bump.inputs['Distance'].default_value = 0.012
    nt.links.new(b_vor.outputs['Distance'], b_bump.inputs['Height'])
    nt.links.new(b_bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.78
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.10
    materials["Basalt"] = mat_basalt

    # Also assign to MAT_Plaza_Basalt_Flagstone
    m_plz = get_or_create_mat("MAT_Plaza_Basalt_Flagstone")
    m_plz.node_tree.nodes.clear()
    m_out = m_plz.node_tree.nodes.new("ShaderNodeOutputMaterial")
    m_bsdf = m_plz.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    m_plz.node_tree.links.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])
    m_bsdf.inputs['Base Color'].default_value = (0.22, 0.19, 0.16, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.78
    if 'Specular IOR Level' in m_bsdf.inputs: m_bsdf.inputs['Specular IOR Level'].default_value = 0.10

    # -----------------------------------------------------------------------
    # F. Marine Seawall Concrete & Tetrapods
    # -----------------------------------------------------------------------
    mat_wall = get_or_create_mat("MAT_MarineDrive_SeawallConcrete")
    w_bsdf = mat_wall.node_tree.nodes.get("Principled BSDF")
    if w_bsdf:
        w_bsdf.inputs['Base Color'].default_value = (0.48, 0.46, 0.42, 1.0)
        w_bsdf.inputs['Roughness'].default_value = 0.82
        if 'Specular IOR Level' in w_bsdf.inputs: w_bsdf.inputs['Specular IOR Level'].default_value = 0.10

    mat_tetra = get_or_create_mat("MAT_Concrete_Tetrapod_Marine")
    t_bsdf = mat_tetra.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.32, 0.32, 0.33, 1.0)
        t_bsdf.inputs['Roughness'].default_value = 0.88
        if 'Specular IOR Level' in t_bsdf.inputs: t_bsdf.inputs['Specular IOR Level'].default_value = 0.08

    # -----------------------------------------------------------------------
    # G. Arabian Sea PBR Deep Navy Cyan
    # -----------------------------------------------------------------------
    mat_sea = get_or_create_mat("MAT_Arabian_Sea")
    nt = mat_sea.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = (0.012, 0.052, 0.12, 1.0) # Deep tropical ocean
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['IOR'].default_value = 1.333
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.75
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 18.0
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.04
    bump.inputs['Distance'].default_value = 0.12
    nt.links.new(noise.outputs['Factor'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # -----------------------------------------------------------------------
    # H. Urban Ground Plinth
    # -----------------------------------------------------------------------
    for g_name in ['MAT_Mumbai_Peninsula_SRTM_PBR', 'Mat_Mumbai_Real_Terrain', 'MAT_Mumbai_Peninsula_Ground']:
        mg = get_or_create_mat(g_name)
        g_bsdf = mg.node_tree.nodes.get("Principled BSDF")
        if g_bsdf:
            g_bsdf.inputs['Base Color'].default_value = (0.09, 0.09, 0.10, 1.0) # Dark neutral urban ground
            g_bsdf.inputs['Roughness'].default_value = 0.88
            if 'Specular IOR Level' in g_bsdf.inputs: g_bsdf.inputs['Specular IOR Level'].default_value = 0.06

    return materials

# ---------------------------------------------------------------------------
# 4. Refine Architectural Landmarks & Facades
# ---------------------------------------------------------------------------
def refine_architectural_landmarks(materials):
    print("[Landmarks] Applying authentic stone masonry, window glazing & saturated palettes...")

    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # -----------------------------------------------------------------------
    # 1. Gateway of India: Dedicated Golden Kharodi Basalt Ashlar Shader
    # -----------------------------------------------------------------------
    mat_gw = get_or_create_mat("Mat_Yellow_Kharodi_Basalt_Authentic")
    nt = mat_gw.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Use OBJECT coordinates so ashlar blocks map cleanly relative to Gateway geometry
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 0.35
    brick.inputs['Mortar Size'].default_value = 0.025
    brick.inputs['Brick Width'].default_value = 1.8
    brick.inputs['Row Height'].default_value = 0.8
    brick.inputs['Color1'].default_value = (0.48, 0.32, 0.14, 1.0) # Warm golden Kharodi basalt
    brick.inputs['Color2'].default_value = (0.34, 0.22, 0.10, 1.0) # Dark weathered volcanic basalt
    brick.inputs['Mortar'].default_value = (0.14, 0.11, 0.08, 1.0) # Historic lime mortar
    nt.links.new(tc.outputs['Object'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.012
    nt.links.new(brick.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.80
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.12

    # Golden Finial
    mat_gold = get_or_create_mat("Mat_Heritage_Gold_Finial_Authentic")
    g_bsdf = mat_gold.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.15, 1.0)
        g_bsdf.inputs['Metallic'].default_value = 0.85
        g_bsdf.inputs['Roughness'].default_value = 0.22

    gw_obj = bpy.data.objects.get("LANDMARK_Gateway_of_India")
    if gw_obj:
        gw_obj.data.materials.clear()
        gw_obj.data.materials.append(mat_gw)
        gw_obj.data.materials.append(mat_gold)
        for poly in gw_obj.data.polygons:
            poly.material_index = 1 if poly.center.z > 33.5 else 0

    # -----------------------------------------------------------------------
    # 2. Taj Mahal Palace Hotel
    # -----------------------------------------------------------------------
    # Heritage Wing Sandstone
    mat_taj_cream = get_or_create_mat("Mat_Taj_Mahal_Palace_Cream")
    t_bsdf = mat_taj_cream.node_tree.nodes.get("Principled BSDF")
    if t_bsdf:
        t_bsdf.inputs['Base Color'].default_value = (0.64, 0.52, 0.38, 1.0) # Warm Colaba buff sandstone
        t_bsdf.inputs['Roughness'].default_value = 0.68

    # Florentine Grand Crimson Red Dome
    mat_taj_dome = get_or_create_mat("Mat_Taj_Red_Dome_Authentic")
    d_bsdf = mat_taj_dome.node_tree.nodes.get("Principled BSDF")
    if d_bsdf:
        d_bsdf.inputs['Base Color'].default_value = (0.48, 0.05, 0.02, 1.0) # Saturated vermilion red
        d_bsdf.inputs['Roughness'].default_value = 0.28
        if 'Specular IOR Level' in d_bsdf.inputs: d_bsdf.inputs['Specular IOR Level'].default_value = 0.60

    # Taj Tower: Warm Architectural Limestone & Bronze Glazing
    mat_taj_tower = get_or_create_mat("Mat_Taj_Tower_White")
    tt_bsdf = mat_taj_tower.node_tree.nodes.get("Principled BSDF")
    if tt_bsdf:
        tt_bsdf.inputs['Base Color'].default_value = (0.60, 0.55, 0.48, 1.0) # Warm limestone buff (NOT pure white!)
        tt_bsdf.inputs['Roughness'].default_value = 0.62

    # -----------------------------------------------------------------------
    # 3. CSMT Victoria Terminus: Remove blank square box & detail facade
    # -----------------------------------------------------------------------
    csmt = bpy.data.objects.get("LANDMARK_CSMT_Masterpiece")
    if csmt and csmt.type == 'MESH':
        bm = bmesh.new()
        bm.from_mesh(csmt.data)
        bm.faces.ensure_lookup_table()
        # The projecting box was centered around (0, -6, 17.8) with depth 48 extending to Y = -30m
        # Let's remove faces that form that solid forward blocking box (Y < -18.5)
        del_faces = [f for f in bm.faces if f.calc_center_median().y < -19.0]
        if del_faces:
            print(f"  CSMT: Purged {len(del_faces)} blocking box faces in front of entrance!")
            bmesh.ops.delete(bm, geom=del_faces, context='FACES_ONLY')
            bm.to_mesh(csmt.data)
        bm.free()

    mat_csmt_stone = get_or_create_mat("MAT_RealMumbai_HeritageGothic_PBR")
    c_bsdf = mat_csmt_stone.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.56, 0.42, 0.24, 1.0) # Golden Malad sandstone
        c_bsdf.inputs['Roughness'].default_value = 0.75

    mat_csmt_tile = get_or_create_mat("MAT_RealMumbai_TerracottaTiles")
    ct_bsdf = mat_csmt_tile.node_tree.nodes.get("Principled BSDF")
    if ct_bsdf:
        ct_bsdf.inputs['Base Color'].default_value = (0.50, 0.16, 0.10, 1.0) # Red terracotta
        ct_bsdf.inputs['Roughness'].default_value = 0.60

    mat_csmt_dome = get_or_create_mat("MAT_CSMT_VerdigrisDome")
    cd_bsdf = mat_csmt_dome.node_tree.nodes.get("Principled BSDF")
    if cd_bsdf:
        cd_bsdf.inputs['Base Color'].default_value = (0.18, 0.46, 0.40, 1.0) # Verdigris copper patina
        cd_bsdf.inputs['Roughness'].default_value = 0.42

    # -----------------------------------------------------------------------
    # 4. Marine Drive Art Deco Mansions: Procedural Facades & Windows
    # -----------------------------------------------------------------------
    def build_artdeco_shader(name, wall_rgb):
        mat = get_or_create_mat(name)
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])

        # Vertical floor bands (3.2m per floor)
        mod_z = nt.nodes.new("ShaderNodeMath")
        mod_z.operation = 'MODULO'
        mod_z.inputs[1].default_value = 3.2
        nt.links.new(sep.outputs['Z'], mod_z.inputs[0])

        ramp_z = nt.nodes.new("ShaderNodeValToRGB")
        ramp_z.color_ramp.interpolation = 'CONSTANT'
        ramp_z.color_ramp.elements[0].position = 0.0
        ramp_z.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Wall spandrel
        e1 = ramp_z.color_ramp.elements.new(0.85 / 3.2)
        e1.color = (1.0, 1.0, 1.0, 1.0) # Window band
        e2 = ramp_z.color_ramp.elements.new(2.35 / 3.2)
        e2.color = (0.0, 0.0, 0.0, 1.0) # Lintel
        nt.links.new(mod_z.outputs['Value'], ramp_z.inputs['Factor'])

        # Horizontal window rhythm (brick pattern)
        brick = nt.nodes.new("ShaderNodeTexBrick")
        brick.inputs['Scale'].default_value = 0.42
        brick.inputs['Mortar Size'].default_value = 0.18
        brick.inputs['Brick Width'].default_value = 1.8
        brick.inputs['Row Height'].default_value = 1.0
        nt.links.new(tc.outputs['Object'], brick.inputs['Vector'])

        win_mask = nt.nodes.new("ShaderNodeMath")
        win_mask.operation = 'MULTIPLY'
        nt.links.new(ramp_z.outputs['Color'], win_mask.inputs[0])
        nt.links.new(brick.outputs['Color'], win_mask.inputs[1])

        mix_col = nt.nodes.new("ShaderNodeMix")
        mix_col.data_type = 'RGBA'
        mix_col.inputs[6].default_value = wall_rgb # Pastel stucco wall
        mix_col.inputs[7].default_value = (0.035, 0.065, 0.10, 1.0) # Deep reflective window glazing
        nt.links.new(win_mask.outputs['Value'], mix_col.inputs[0])
        nt.links.new(mix_col.outputs[2], bsdf.inputs['Base Color'])

        mix_rough = nt.nodes.new("ShaderNodeMix")
        mix_rough.data_type = 'FLOAT'
        mix_rough.inputs[2].default_value = 0.72 # Stucco roughness
        mix_rough.inputs[3].default_value = 0.10 # Glass roughness
        nt.links.new(win_mask.outputs['Value'], mix_rough.inputs[0])
        nt.links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

        if 'Specular IOR Level' in bsdf.inputs:
            bsdf.inputs['Specular IOR Level'].default_value = 0.65
        return mat

    m_cream = build_artdeco_shader("MAT_RealMumbai_ArtDeco_Cream", (0.82, 0.74, 0.58, 1.0))
    m_ochre = build_artdeco_shader("MAT_RealMumbai_ArtDeco_Ochre", (0.74, 0.44, 0.12, 1.0))
    m_seafoam = build_artdeco_shader("MAT_RealMumbai_ArtDeco_Seafoam", (0.18, 0.48, 0.38, 1.0))
    m_peach = build_artdeco_shader("MAT_RealMumbai_ArtDeco_Peach", (0.74, 0.34, 0.18, 1.0))

    mansion_palette = {
        "ARTDECO_MarineDrive_Kapoor_Mahal": m_cream,
        "ARTDECO_MarineDrive_Zaver_Mahal": m_seafoam,
        "ARTDECO_MarineDrive_Keval_Mahal": m_ochre,
        "ARTDECO_MarineDrive_Soona_Mahal": m_peach,
        "ARTDECO_MarineDrive_Empress_Court": m_cream,
        "ARTDECO_MarineDrive_Shiv_Shanti_Bhuvan": m_ochre,
        "ARTDECO_MarineDrive_Rajab_Mahal": m_peach,
        "ARTDECO_MarineDrive_Fairlawn": m_seafoam,
        "ARTDECO_MarineDrive_Gool_Mahal": m_cream,
        "ARTDECO_MarineDrive_Sea_Green_Hotel": m_ochre,
        "ARTDECO_MarineDrive_Chateau_Marine": m_seafoam,
        "ARTDECO_MarineDrive_Ocean_View": m_peach
    }
    for m_name, s_mat in mansion_palette.items():
        m_obj = bpy.data.objects.get(m_name)
        if m_obj:
            m_obj.data.materials.clear()
            m_obj.data.materials.append(s_mat)

    # -----------------------------------------------------------------------
    # 5. Worli Megatowers: Architectural Solar Curtain Wall Glazing
    # -----------------------------------------------------------------------
    mat_worli = get_or_create_mat("MAT_RealMumbai_Megatower_CurtainWall")
    nt = mat_worli.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Reflective architectural solar curtain glass: Metallic = 0.85, Roughness = 0.06, azure blue
    bsdf.inputs['Base Color'].default_value = (0.16, 0.32, 0.48, 1.0) # Gleaming marine navy solar glass
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['IOR'].default_value = 1.52
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.85

    # Structural mullions bump grid
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 0.40
    brick.inputs['Mortar Size'].default_value = 0.08
    brick.inputs['Brick Width'].default_value = 1.5
    brick.inputs['Row Height'].default_value = 3.6
    nt.links.new(tc.outputs['Object'], brick.inputs['Vector'])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.02
    nt.links.new(brick.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Apply to all Worli / Lower Parel megatower objects
    worli_kws = ['World_One', 'Palais_Royale', 'Imperial_Tower', 'World_Crest', 'One_Avighna', 'Indiabulls', 'Minerva', 'Lodha', 'Nathani', 'Omkar', 'Three_Sixty']
    for o in bpy.data.objects:
        if o.type == 'MESH' and 'Helipad' not in o.name:
            if any(kw in o.name for kw in worli_kws):
                o.data.materials.clear()
                o.data.materials.append(mat_worli)

    # -----------------------------------------------------------------------
    # 6. Nariman Point Financial CBD: Modernist Concrete & Dark Ribbon Glazing
    # -----------------------------------------------------------------------
    mat_nariman = get_or_create_mat("MAT_RealMumbai_Modernist_Concrete_PBR")
    nt = mat_nariman.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Concrete frame with dark bronze ribbon glazing
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])

    mod_z = nt.nodes.new("ShaderNodeMath")
    mod_z.operation = 'MODULO'
    mod_z.inputs[1].default_value = 3.6
    nt.links.new(sep.outputs['Z'], mod_z.inputs[0])

    ramp_z = nt.nodes.new("ShaderNodeValToRGB")
    ramp_z.color_ramp.interpolation = 'CONSTANT'
    ramp_z.color_ramp.elements[0].position = 0.0
    ramp_z.color_ramp.elements[0].color = (0.52, 0.50, 0.46, 1.0) # Concrete spandrel
    e1 = ramp_z.color_ramp.elements.new(0.90 / 3.6)
    e1.color = (0.06, 0.05, 0.04, 1.0) # Dark bronze ribbon window
    e2 = ramp_z.color_ramp.elements.new(2.40 / 3.6)
    e2.color = (0.52, 0.50, 0.46, 1.0) # Concrete beam
    nt.links.new(mod_z.outputs['Value'], ramp_z.inputs['Factor'])
    nt.links.new(ramp_z.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.65
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = 0.50

    # -----------------------------------------------------------------------
    # 7. Girgaon Chawls Vernacular Quarter
    # -----------------------------------------------------------------------
    mat_chawl = get_or_create_mat("MAT_RealMumbai_Chawl_Plaster_PBR")
    c_bsdf = mat_chawl.node_tree.nodes.get("Principled BSDF")
    if c_bsdf:
        c_bsdf.inputs['Base Color'].default_value = (0.58, 0.54, 0.44, 1.0) # Aged monsoon-weathered lime plaster
        c_bsdf.inputs['Roughness'].default_value = 0.85

    mat_teak = get_or_create_mat("MAT_Chawl_Teak_Timber")
    tk_bsdf = mat_teak.node_tree.nodes.get("Principled BSDF")
    if tk_bsdf:
        tk_bsdf.inputs['Base Color'].default_value = (0.18, 0.10, 0.05, 1.0) # Dark oiled teak timber
        tk_bsdf.inputs['Roughness'].default_value = 0.70

    mat_tank = get_or_create_mat("MAT_RealMumbai_WaterTank_PBR")
    tn_bsdf = mat_tank.node_tree.nodes.get("Principled BSDF")
    if tn_bsdf:
        tn_bsdf.inputs['Base Color'].default_value = (0.02, 0.22, 0.58, 1.0) # Iconic Sintex Polyethylene Blue
        tn_bsdf.inputs['Roughness'].default_value = 0.35

    mat_chhajja = get_or_create_mat("MAT_Chawl_Corrugated_Chhajja")
    ch_bsdf = mat_chhajja.node_tree.nodes.get("Principled BSDF")
    if ch_bsdf:
        ch_bsdf.inputs['Base Color'].default_value = (0.44, 0.42, 0.40, 1.0) # Galvanized corrugated tin
        ch_bsdf.inputs['Roughness'].default_value = 0.55
        ch_bsdf.inputs['Metallic'].default_value = 0.40

    # Road_MarineDrive_Unified: Fix material slots
    rd_uni = bpy.data.objects.get("ROAD_MarineDrive_Unified")
    if rd_uni and len(rd_uni.data.materials) >= 4:
        rd_uni.data.materials[0] = materials["Asphalt"]
        rd_uni.data.materials[1] = materials["White"]
        rd_uni.data.materials[2] = materials["Yellow"]
        rd_uni.data.materials[3] = materials["Pavers"]
        print("  ROAD_MarineDrive_Unified slots calibrated: [Asphalt, WhiteMarking, YellowMedian, Pavers]")

# ---------------------------------------------------------------------------
# 5. Fix Terrain, Sea Level & Plinths
# ---------------------------------------------------------------------------
def fix_terrain_and_plinths(materials):
    print("[Terrain] Calibrating Nariman Point plinth grade (+3.8m) and Apollo Bunder esplanade...")

    # A. Nariman Point Reclaimed Landmass Plinth Slab (+3.80m above sea level)
    np_name = "PLINTH_NarimanPoint_ReclaimedWaterfront"
    if np_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[np_name], do_unlink=True)
    if np_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[np_name])

    bm_np = bmesh.new()
    poly_xy = [
        (-1260.0, 320.0),
        (-1220.0, 750.0),
        (-1020.0, 850.0),
        (-880.0, 850.0),
        (-880.0, 280.0),
        (-1180.0, 280.0)
    ]
    v_bottom = [bm_np.verts.new((x, y, 0.0)) for x, y in poly_xy]
    v_top = [bm_np.verts.new((x, y, 3.80)) for x, y in poly_xy]
    bm_np.faces.new(reversed(v_top))
    bm_np.faces.new(v_bottom)
    n = len(poly_xy)
    for i in range(n):
        next_i = (i + 1) % n
        bm_np.faces.new([v_bottom[i], v_bottom[next_i], v_top[next_i], v_top[i]])
    mesh_np = bpy.data.meshes.new(np_name)
    bm_np.to_mesh(mesh_np)
    bm_np.free()
    obj_np = bpy.data.objects.new(np_name, mesh_np)
    bpy.context.scene.collection.objects.link(obj_np)
    mat_conc = bpy.data.materials.get("MAT_RealMumbai_Modernist_Concrete_PBR")
    if mat_conc:
        obj_np.data.materials.append(mat_conc)

    # Ensure all Nariman Point commercial towers have base at Z >= 3.80m (above sea level 1.2m!)
    nariman_bldgs = [
        "LANDMARK_AirIndia_Tower", "LANDMARK_AirIndia_Podium", "LANDMARK_AirIndia_Crown",
        "LANDMARK_ExpressTowers_Tower", "LANDMARK_ExpressTowers_Podium", "LANDMARK_ExpressTowers_Core",
        "LANDMARK_Trident_Tower", "LANDMARK_TheOberoi_Wing",
        "BLDG_NarimanPoint_Maker_Chambers_IV", "BLDG_NarimanPoint_Maker_Chambers_V",
        "BLDG_NarimanPoint_Maker_Chambers_VI", "BLDG_NarimanPoint_Free_Press_House",
        "BLDG_NarimanPoint_Mittal_Court", "BLDG_NarimanPoint_Bajaj_Bhavan",
        "BLDG_NarimanPoint_Nariman_Bhavan", "BLDG_NarimanPoint_Mafatlal_Centre"
    ]
    for b_name in nariman_bldgs:
        b_obj = bpy.data.objects.get(b_name)
        if b_obj:
            if b_obj.location.z < 3.80:
                b_obj.location.z = 3.80
            b_obj.data.materials.clear()
            b_obj.data.materials.append(bpy.data.materials.get("MAT_RealMumbai_Modernist_Concrete_PBR"))

    # B. Apollo Bunder Esplanade Mesh Check (keep at origin, vertices already have z=2.38m!)
    esp = bpy.data.objects.get("ESPLANADE_ApolloBunder_Gateway_HeritageBasalt")
    if esp:
        esp.data.materials.clear()
        esp.data.materials.append(materials["Basalt"])
        esp.location = Vector((0.0, 0.0, 0.0))

    # C. Ensure proper materials across all surveyed road objects
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and any(k in o.name for k in ['CURBS_MUMBAI', 'ROADS_MUMBAI', 'SIDEWALKS_MUMBAI']):
            if 'CURBS' in o.name:
                o.data.materials.clear()
                o.data.materials.append(materials["Curb"])
            elif 'SIDEWALKS' in o.name:
                o.data.materials.clear()
                o.data.materials.append(materials["Pavers"])
            elif 'ROADS' in o.name:
                o.data.materials.clear()
                o.data.materials.append(materials["Asphalt"])

    # D. Clamp raw SRTM radar spikes in coastal flat reclamation zones (Marine Drive / Nariman Point)
    srtm = bpy.data.objects.get("TERRAIN_SRTM_Mumbai_Peninsula_30M")
    if srtm and srtm.type == 'MESH':
        clamped = 0
        for v in srtm.data.vertices:
            if -1200 < v.co.x < -950 and 500 < v.co.y < 2300:
                if v.co.z > 6.8:
                    v.co.z = 6.8
                    clamped += 1
        srtm.data.update()
        if clamped > 0:
            print(f"  Clamped {clamped} coastal SRTM radar spikes to 6.8m under road corridors.")

# ---------------------------------------------------------------------------
# 6. Configure Masterpiece Cameras
# ---------------------------------------------------------------------------
def configure_masterpiece_cameras():
    print("[Cameras] Curating 8 dedicated architectural & road cameras...")

    cams = [
        # 1. Marine Drive Art Deco Heritage Row
        # Elevated promenade view looking North-East obliquely across the 6-lane road at Keval, Soona & Zaver Mahal facades
        {
            "id": "arch_1_marinedrive_artdeco.png",
            "name": "Cam_Arch_1_MarineDrive_ArtDeco",
            "eye": Vector((-1008.0, 915.0, 11.0)),
            "target": Vector((-960.0, 1040.0, 22.0)),
            "lens": 24.0,
            "title": "Marine Drive Art Deco Heritage Row (UNESCO World Heritage)"
        },
        # 2. CSMT Victoria Terminus & Fort Victorian Gothic
        # Frontal street-level view looking north up Dr DN Road toward grand pointed arch entrance & octagonal dome
        {
            "id": "arch_2_csmt_fort_gothic.png",
            "name": "Cam_Arch_2_Fort_VictorianHeritage",
            "eye": Vector((263.0, 1720.0, 16.5)),
            "target": Vector((263.0, 1860.0, 48.0)),
            "lens": 24.0,
            "title": "CSMT Victoria Terminus & Fort Victorian Gothic Precinct"
        },
        # 3. Worli & Lower Parel Contemporary Megatowers
        # Perspective looking North-East from Annie Besant Road showing gleaming azure glass towers
        {
            "id": "arch_3_worli_megatowers.png",
            "name": "Cam_Arch_3_Worli_MegatowerHighRise",
            "eye": Vector((-560.0, 7680.0, 42.0)),
            "target": Vector((-315.0, 7960.0, 195.0)),
            "lens": 22.0,
            "title": "Worli & Lower Parel Contemporary Megatower Skyline"
        },
        # 4. Nariman Point Waterfront Financial CBD
        # Marine elevation across Back Bay showing modernist concrete framing and dark ribbon glazing at +3.8m grade
        {
            "id": "arch_4_narimanpoint_waterfront.png",
            "name": "Cam_Arch_4_NarimanPoint_Waterfront",
            "eye": Vector((-1300.0, 280.0, 22.0)),
            "target": Vector((-1080.0, 560.0, 68.0)),
            "lens": 26.0,
            "title": "Nariman Point Modernist Commercial Waterfront Skyline"
        },
        # 5. Girgaon Traditional Chawl Quarter
        # Atmospheric street-level view looking down the traditional paved gully flanked by wooden verandas
        {
            "id": "arch_5_girgaon_chawls.png",
            "name": "Cam_Arch_5_Girgaon_ChawlVernacular",
            "eye": Vector((-360.0, 4775.0, 15.2)),
            "target": Vector((-360.0, 4845.0, 18.0)),
            "lens": 28.0,
            "title": "Girgaon High-Density Vernacular Chawl Quarter"
        },
        # 6. Apollo Bunder Gateway of India & Taj Mahal Palace
        # Postcard dual view showing golden Kharodi basalt Gateway arch (right) & red-domed Taj Palace (left) over basalt plaza
        {
            "id": "arch_6_apollobunder_gateway_taj.png",
            "name": "Cam_Arch_6_ApolloBunder_HeritagePlaza",
            "eye": Vector((220.0, -170.0, 10.0)),
            "target": Vector((140.0, -135.0, 25.0)),
            "lens": 24.0,
            "title": "Apollo Bunder Gateway of India & Taj Mahal Palace Precinct"
        },
        # 7. Marine Drive Street-Level Perspective (Road 1 Close-up)
        # Low street-level shot along Queen's Necklace showing pitch-black asphalt, BMC kerbstones, and promenade
        {
            "id": "road_1_marinedrive_streetview.png",
            "name": "Cam_Player_MarineDrive_Promenade",
            "eye": Vector((-1024.0, 1020.0, 8.8)),
            "target": Vector((-1012.0, 800.0, 10.5)),
            "lens": 28.0,
            "title": "Marine Drive Street-Level Road, BMC Curbs & 12M Promenade Close-Up"
        },
        # 8. Apollo Bunder Ceremonial Basalt Esplanade (Road 2 Close-up)
        # Ceremonial esplanade shot looking at the Gateway arch entrance across hand-cut basalt flagstones
        {
            "id": "road_2_gateway_plaza_close.png",
            "name": "Cam_Player_Gateway_Plaza",
            "eye": Vector((210.0, -113.0, 4.2)),
            "target": Vector((165.0, -113.0, 16.0)),
            "lens": 24.0,
            "title": "Apollo Bunder Ceremonial Basalt Esplanade & Gateway Arch Close-Up"
        }
    ]

    for c in cams:
        cam_obj = bpy.data.objects.get(c["name"])
        if not cam_obj:
            c_data = bpy.data.cameras.new(c["name"])
            cam_obj = bpy.data.objects.new(c["name"], c_data)
            bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = c["eye"]
        dir_v = (c["target"] - c["eye"]).normalized()
        cam_obj.rotation_euler = dir_v.to_track_quat('-Z', 'Y').to_euler()
        cam_obj.data.lens = c["lens"]
        cam_obj.data.clip_start = 0.5
        cam_obj.data.clip_end = 50000.0

    return cams

# ---------------------------------------------------------------------------
# 7. Render All Perspectives in Cycles
# ---------------------------------------------------------------------------
def render_all_perspectives(cams):
    print("[Render] Starting Cycles rendering of all 8 authentic Mumbai views at 1920x1080...")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.use_nodes = False

    for c in cams:
        cam_obj = bpy.data.objects.get(c["name"])
        if cam_obj:
            scene.camera = cam_obj
            out_p = os.path.join(OUTPUT_DIR, c["id"])
            scene.render.filepath = out_p
            print(f"  Rendering {c['title']}...")
            bpy.ops.render.render(write_still=True)
            print(f"    Saved: {out_p}")

if __name__ == "__main__":
    main()
