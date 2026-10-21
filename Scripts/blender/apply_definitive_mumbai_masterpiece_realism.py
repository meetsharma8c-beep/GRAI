#!/usr/bin/env python3
"""
GRAI — Definitive Master Mumbai Realism & Surveyed Road Network
==============================================================
Fully integrates:
1. Exact surveyed 1:1 scale Mumbai roads, paths, BMC curbs, and promenades.
2. Pitch-black asphalt with low specular (no white sky-glare wash).
3. Rich, saturated, authentic Mumbai architectural colors and procedural window glazing:
   - Art Deco (turmeric ochre, seafoam mint, terracotta peach, ivory cream with bronze window casements)
   - Gateway of India (warm golden Kharodi basalt with ashlar stone courses, NO office windows)
   - Taj Mahal Palace (Colaba sandstone cream, Florentine vermilion dome, ivory tower)
   - CSMT Victoria Terminus (Malad sandstone, pointed arch arcades, 100m dome, verdigris spires)
   - Worli Megatowers (deep marine navy reflective double-glazed curtain walls)
   - Nariman Point CBD (architectural concrete framing & dark bronze ribbon glazing)
   - Girgaon Chawls (aged plaster, teak timber verandas, red Mangalore roof tiles, Sintex tanks)
4. Calibrated single tropical sun with Filmic Medium High Contrast (ZERO washed-out tones).
5. Strict constraint: NO characters, NO pedestrians, NO vehicles, NO traffic, NO living entities.
"""

import os
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_definitive_masterpiece():
    print("=" * 75)
    print("GRAI — DEPLOYING DEFINITIVE REAL MUMBAI ROAD & ARCHITECTURAL REALISM")
    print("=" * 75)

    # 1. Clean scene & enforce strict constraints
    purge_unwanted_and_rogue_lights()

    # 2. Lighting & Color Management
    setup_single_sun_and_filmic()

    # 3. Fix Road Materials (Pitch-Black Asphalt & Bold Markings)
    fix_all_road_materials_and_slots()

    # 4. Build Procedural Architectural Shaders with Real Windows
    shaders = build_rich_architectural_shaders()

    # 5. Apply Shaders to Iconic Precincts
    apply_shaders_to_precincts(shaders)

    # 6. Save Updated Master Blend
    blend_path = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Save] Upgraded Digital Twin saved to {blend_path}")

    # 7. Render All Master Architectural & Street Perspectives
    render_all_views()

# ---------------------------------------------------------------------------
# 1. Purge unwanted & rogue lights
# ---------------------------------------------------------------------------
def purge_unwanted_and_rogue_lights():
    print("[CleanUp] Purging rogue lights and enforcing entity constraints...")
    rogue_lights = [
        "Light_Apollo_Harbour_Bounce", "LIGHT_Fill_GoldenHour",
        "LIGHT_Gateway_Flood_East", "LIGHT_Gateway_Flood_West",
        "LIGHT_Taj_Flood_Facade", "LIGHT_Taj_Dome_Glow"
    ]
    for l_name in rogue_lights:
        l_obj = bpy.data.objects.get(l_name)
        if l_obj:
            bpy.data.objects.remove(l_obj, do_unlink=True)

    unwanted_kws = ["raghunath", "character", "pedestrian", "vehicle", "car", "traffic", "human", "avatar", "npc"]
    for o in list(bpy.data.objects):
        if any(kw in o.name.lower() for kw in unwanted_kws) and o.type != 'CAMERA':
            bpy.data.objects.remove(o, do_unlink=True)

    # Hide duplicate/floating terrain polygons
    for t_name in ['Terrain', 'Terrain_envelope', 'TERRAIN_Mumbai_Peninsula_Landmass.001']:
        t_obj = bpy.data.objects.get(t_name)
        if t_obj:
            t_obj.hide_render = True
            t_obj.hide_viewport = True

# ---------------------------------------------------------------------------
# 2. Single Tropical Sunlight & Filmic Medium High Contrast
# ---------------------------------------------------------------------------
def setup_single_sun_and_filmic():
    print("[Lighting] Calibrating single physical tropical sunlight & Filmic contrast...")
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -1.25
    scene.view_settings.gamma = 1.0

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
    sky.sun_elevation = math.radians(26.0)
    sky.sun_rotation = math.radians(78.0)
    sky.altitude = 10.0
    sky.air_density = 1.02
    sky.ozone_density = 3.2
    w_nt.links.new(sky.outputs['Color'], w_bg.inputs['Color'])
    w_bg.inputs['Strength'].default_value = 0.45

    for s_old in ['Sun_Mumbai_Map', 'LAMP_Mumbai_GoldenHour_Sun']:
        so = bpy.data.objects.get(s_old)
        if so: bpy.data.objects.remove(so, do_unlink=True)

    sun = bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        s_data = bpy.data.lights.new("Sun_Mumbai", type='SUN')
        sun = bpy.data.objects.new("Sun_Mumbai", s_data)
        bpy.context.scene.collection.objects.link(sun)
    sun.data.energy = 3.6
    sun.data.color = (1.0, 0.90, 0.78)
    sun.data.angle = math.radians(0.8)
    sun.rotation_euler = Euler((math.radians(46.0), math.radians(14.0), math.radians(65.0)), 'XYZ')

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.preview_samples = 16
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.08

# ---------------------------------------------------------------------------
# 3. Road Materials & Slots Fix
# ---------------------------------------------------------------------------
def fix_all_road_materials_and_slots():
    print("[RoadMaterials] Engineering pitch-black asphalt, BMC curbs & fixing slots...")

    def create_pbr_mat(name, base_rgb, rough=0.75, spec=0.10, metal=0.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        bsdf.inputs['Base Color'].default_value = base_rgb
        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
        if 'Specular IOR Level' in bsdf.inputs:
            bsdf.inputs['Specular IOR Level'].default_value = spec
        elif 'Specular' in bsdf.inputs:
            bsdf.inputs['Specular'].default_value = spec
        return mat

    # Deep pitch-black tropical asphalt (low specular prevents sky reflection glare)
    asphalt_rgb = (0.038, 0.038, 0.042, 1.0)
    mat_asphalt = create_pbr_mat('MAT_MarineDrive_Asphalt_Master', asphalt_rgb, rough=0.78, spec=0.08)
    create_pbr_mat('MAT_RealRoad_Asphalt', asphalt_rgb, rough=0.78, spec=0.08)
    create_pbr_mat('MAT_RealMumbai_Road_Asphalt_Master', asphalt_rgb, rough=0.78, spec=0.08)
    create_pbr_mat('MAT_SeaLink_HighwayAsphalt', (0.045, 0.045, 0.050, 1.0), rough=0.72, spec=0.10)

    # Crisp Markings
    create_pbr_mat('MAT_Road_White_Markings', (0.95, 0.95, 0.92, 1.0), rough=0.35, spec=0.45)
    create_pbr_mat('MAT_Road_Yellow_Median', (0.94, 0.72, 0.06, 1.0), rough=0.40, spec=0.35)

    # BMC Curbs
    create_pbr_mat('MAT_BMC_Curb_Black', (0.05, 0.05, 0.06, 1.0), rough=0.70, spec=0.10)
    create_pbr_mat('MAT_BMC_Curb_Yellow', (0.94, 0.72, 0.06, 1.0), rough=0.55, spec=0.25)
    create_pbr_mat('MAT_RealMumbai_BMC_Curb_Stones', (0.94, 0.72, 0.06, 1.0), rough=0.60, spec=0.20)

    # Sidewalks & Promenades
    paver_rgb = (0.52, 0.22, 0.16, 1.0)
    create_pbr_mat('MAT_MarineDrive_Sidewalk_Pavers', paver_rgb, rough=0.82, spec=0.15)
    create_pbr_mat('MAT_RealMumbai_Sidewalk_Pavers', paver_rgb, rough=0.82, spec=0.15)
    create_pbr_mat('MAT_RealMumbai_Promenade_Seawall', (0.58, 0.56, 0.52, 1.0), rough=0.85, spec=0.15)
    create_pbr_mat('MAT_MarineDrive_SeawallConcrete', (0.58, 0.56, 0.52, 1.0), rough=0.85, spec=0.15)
    create_pbr_mat('MAT_Concrete_Tetrapod_Marine', (0.34, 0.34, 0.35, 1.0), rough=0.88, spec=0.10)

    # Apollo Bunder Heritage Basalt Flagstone Plaza
    basalt_rgb = (0.34, 0.30, 0.24, 1.0)
    create_pbr_mat('MAT_RealMumbai_Heritage_Basalt_Flagstone', basalt_rgb, rough=0.78, spec=0.12)
    create_pbr_mat('MAT_Plaza_Basalt_Flagstone', basalt_rgb, rough=0.78, spec=0.12)

    # Urban Ground Plinth
    create_pbr_mat('MAT_Mumbai_Peninsula_SRTM_PBR', (0.10, 0.10, 0.11, 1.0), rough=0.88, spec=0.08)
    create_pbr_mat('Mat_Mumbai_Real_Terrain', (0.10, 0.10, 0.11, 1.0), rough=0.88, spec=0.08)

    # Arabian Sea
    create_pbr_mat('MAT_Arabian_Sea', (0.010, 0.048, 0.12, 1.0), rough=0.06, spec=0.85)

    # Fix ROAD_MarineDrive_Unified slot assignment!
    rd_uni = bpy.data.objects.get("ROAD_MarineDrive_Unified")
    if rd_uni:
        # Slot 0: Asphalt, Slot 1: Asphalt (was mistakenly White Markings!), Slot 2: Yellow, Slot 3: Pavers
        rd_uni.data.materials[1] = mat_asphalt
        print("  Fixed ROAD_MarineDrive_Unified: Slot 1 reset to Asphalt!")

# ---------------------------------------------------------------------------
# 4. Rich Architectural Procedural Shaders
# ---------------------------------------------------------------------------
def build_rich_architectural_shaders():
    print("[Shaders] Building procedural architectural facades with genuine window glazing...")
    shaders = {}

    def make_facade_shader(name, wall_rgb, window_rgb, floor_h=3.2, roughness=0.68, metal=0.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        geom = nodes.new("ShaderNodeNewGeometry")
        sep = nodes.new("ShaderNodeSeparateXYZ")
        links.new(geom.outputs['Position'], sep.inputs['Vector'])

        # Vertical floor repetition
        mod_z = nodes.new("ShaderNodeMath")
        mod_z.operation = 'MODULO'
        mod_z.inputs[1].default_value = floor_h
        links.new(sep.outputs['Z'], mod_z.inputs[0])

        map_z = nodes.new("ShaderNodeMapRange")
        map_z.inputs['From Min'].default_value = 0.0
        map_z.inputs['From Max'].default_value = floor_h
        map_z.inputs['To Min'].default_value = 0.0
        map_z.inputs['To Max'].default_value = 1.0
        links.new(mod_z.outputs['Value'], map_z.inputs['Value'])

        # Window band height: from 0.85m to 2.30m of each floor
        ramp_z = nodes.new("ShaderNodeValToRGB")
        ramp_z.color_ramp.interpolation = 'CONSTANT'
        ramp_z.color_ramp.elements[0].position = 0.0
        ramp_z.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
        e1 = ramp_z.color_ramp.elements.new(0.85 / floor_h)
        e1.color = (1.0, 1.0, 1.0, 1.0)
        e2 = ramp_z.color_ramp.elements.new(2.30 / floor_h)
        e2.color = (0.0, 0.0, 0.0, 1.0)
        links.new(map_z.outputs['Result'], ramp_z.inputs['Factor'])

        # Horizontal window spacing
        brick = nodes.new("ShaderNodeTexBrick")
        brick.inputs['Scale'].default_value = 0.45
        brick.inputs['Mortar Size'].default_value = 0.18
        brick.inputs['Brick Width'].default_value = 1.6
        brick.inputs['Row Height'].default_value = 1.0
        links.new(geom.outputs['Position'], brick.inputs['Vector'])

        math_mult = nodes.new("ShaderNodeMath")
        math_mult.operation = 'MULTIPLY'
        links.new(ramp_z.outputs['Color'], math_mult.inputs[0])
        links.new(brick.outputs['Color'], math_mult.inputs[1])

        mix_col = nodes.new("ShaderNodeMix")
        mix_col.data_type = 'RGBA'
        mix_col.inputs[6].default_value = wall_rgb
        mix_col.inputs[7].default_value = window_rgb
        links.new(math_mult.outputs['Value'], mix_col.inputs[0])
        links.new(mix_col.outputs[2], bsdf.inputs['Base Color'])

        mix_rough = nodes.new("ShaderNodeMix")
        mix_rough.data_type = 'FLOAT'
        mix_rough.inputs[2].default_value = roughness
        mix_rough.inputs[3].default_value = 0.12 # reflective glass
        links.new(math_mult.outputs['Value'], mix_rough.inputs[0])
        links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

        bsdf.inputs['Metallic'].default_value = metal
        if 'Specular IOR Level' in bsdf.inputs:
            bsdf.inputs['Specular IOR Level'].default_value = 0.65
        elif 'Specular' in bsdf.inputs:
            bsdf.inputs['Specular'].default_value = 0.65

        # Micro-noise stucco bump
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs['Scale'].default_value = 35.0
        links.new(geom.outputs['Position'], noise.inputs['Vector'])

        bump = nodes.new("ShaderNodeBump")
        bump.inputs['Strength'].default_value = 0.20
        bump.inputs['Distance'].default_value = 0.005
        links.new(noise.outputs['Factor'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        shaders[name] = mat
        return mat

    # Art Deco Pastels with Dark Bronze Window Casements
    bronze_window = (0.10, 0.09, 0.08, 1.0)
    make_facade_shader("MAT_RealMumbai_ArtDeco_Cream", (0.84, 0.76, 0.60, 1.0), bronze_window, floor_h=3.2)
    make_facade_shader("MAT_RealMumbai_ArtDeco_Ochre", (0.76, 0.46, 0.14, 1.0), bronze_window, floor_h=3.2)
    make_facade_shader("MAT_RealMumbai_ArtDeco_Seafoam", (0.20, 0.52, 0.42, 1.0), bronze_window, floor_h=3.2)
    make_facade_shader("MAT_RealMumbai_ArtDeco_Peach", (0.76, 0.36, 0.20, 1.0), bronze_window, floor_h=3.2)

    # Worli Megatower Deep Marine Navy Curtain Wall
    make_facade_shader("MAT_RealMumbai_Megatower_CurtainWall", (0.16, 0.22, 0.28, 1.0), (0.015, 0.065, 0.15, 1.0), floor_h=3.8, roughness=0.08, metal=0.40)
    make_facade_shader("MAT_RealMumbai_HighRise_CurtainWall_PBR", (0.18, 0.22, 0.26, 1.0), (0.02, 0.08, 0.16, 1.0), floor_h=3.6, roughness=0.10, metal=0.35)

    # Nariman Point Architectural Concrete & Dark Bronze Ribbon Glazing
    make_facade_shader("MAT_RealMumbai_Modernist_Concrete_PBR", (0.62, 0.60, 0.56, 1.0), (0.08, 0.07, 0.06, 1.0), floor_h=3.5, roughness=0.75)

    # Girgaon Chawl Vernacular (Lime Plaster, Timber, Tin & Terracotta)
    make_facade_shader("MAT_RealMumbai_Chawl_Plaster_PBR", (0.68, 0.64, 0.54, 1.0), (0.14, 0.10, 0.07, 1.0), floor_h=2.9, roughness=0.85)

    return shaders

# ---------------------------------------------------------------------------
# 5. Apply Shaders to Iconic Precincts
# ---------------------------------------------------------------------------
def apply_shaders_to_precincts(shaders):
    print("[Landmarks] Detailing Gateway of India, Taj Mahal Palace & CSMT...")

    # A. Gateway of India: Dedicated Solid Golden Kharodi Basalt Ashlar Courses (NO Windows!)
    mat_gw = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt_Authentic")
    if not mat_gw:
        mat_gw = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt_Authentic")
    mat_gw.use_nodes = True
    nt = mat_gw.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    geom = nt.nodes.new("ShaderNodeNewGeometry")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 0.60
    brick.inputs['Mortar Size'].default_value = 0.035
    brick.inputs['Color1'].default_value = (0.58, 0.42, 0.20, 1.0) # Deep golden Kharodi basalt
    brick.inputs['Color2'].default_value = (0.46, 0.32, 0.16, 1.0) # Dark volcanic basalt
    brick.inputs['Mortar'].default_value = (0.22, 0.18, 0.14, 1.0) # Heritage lime mortar
    nt.links.new(geom.outputs['Position'], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.012
    nt.links.new(brick.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.82

    gw_obj = bpy.data.objects.get("LANDMARK_Gateway_of_India")
    if gw_obj:
        gw_obj.data.materials.clear()
        gw_obj.data.materials.append(mat_gw)

    # B. Taj Mahal Palace
    mat_taj_wall = bpy.data.materials.get("Mat_Taj_Mahal_Palace_Cream")
    if mat_taj_wall:
        bsdf_t = mat_taj_wall.node_tree.nodes.get("Principled BSDF")
        if bsdf_t: bsdf_t.inputs['Base Color'].default_value = (0.76, 0.68, 0.54, 1.0)

    mat_taj_dome = bpy.data.materials.get("Mat_Taj_Red_Dome_Authentic")
    if mat_taj_dome:
        bsdf_d = mat_taj_dome.node_tree.nodes.get("Principled BSDF")
        if bsdf_d: bsdf_d.inputs['Base Color'].default_value = (0.52, 0.06, 0.04, 1.0)

    # C. CSMT Victoria Terminus: Golden Malad Sandstone
    mat_csmt = bpy.data.materials.get("MAT_CSMT_VictorianSandstone")
    if mat_csmt:
        bsdf_c = mat_csmt.node_tree.nodes.get("Principled BSDF")
        if bsdf_c: bsdf_c.inputs['Base Color'].default_value = (0.66, 0.52, 0.32, 1.0)

    # D. Marine Drive Art Deco Mansions: Distribute authentic pastels
    mansion_palette = {
        "ARTDECO_MarineDrive_Kapoor_Mahal": shaders['MAT_RealMumbai_ArtDeco_Cream'],
        "ARTDECO_MarineDrive_Zaver_Mahal": shaders['MAT_RealMumbai_ArtDeco_Seafoam'],
        "ARTDECO_MarineDrive_Keval_Mahal": shaders['MAT_RealMumbai_ArtDeco_Ochre'],
        "ARTDECO_MarineDrive_Soona_Mahal": shaders['MAT_RealMumbai_ArtDeco_Peach'],
        "ARTDECO_MarineDrive_Empress_Court": shaders['MAT_RealMumbai_ArtDeco_Cream'],
        "ARTDECO_MarineDrive_Shiv_Shanti_Bhuvan": shaders['MAT_RealMumbai_ArtDeco_Ochre'],
        "ARTDECO_MarineDrive_Rajab_Mahal": shaders['MAT_RealMumbai_ArtDeco_Peach'],
        "ARTDECO_MarineDrive_Fairlawn": shaders['MAT_RealMumbai_ArtDeco_Seafoam'],
        "ARTDECO_MarineDrive_Sea_Green_Hotel": shaders['MAT_RealMumbai_ArtDeco_Ochre'],
        "ARTDECO_MarineDrive_Gool_Mahal": shaders['MAT_RealMumbai_ArtDeco_Cream'],
        "ARTDECO_MarineDrive_Chateau_Marine": shaders['MAT_RealMumbai_ArtDeco_Seafoam'],
        "ARTDECO_MarineDrive_Ocean_View": shaders['MAT_RealMumbai_ArtDeco_Peach']
    }
    for m_name, s_mat in mansion_palette.items():
        m_obj = bpy.data.objects.get(m_name)
        if m_obj:
            m_obj.data.materials.clear()
            m_obj.data.materials.append(s_mat)

# ---------------------------------------------------------------------------
# 6. Render All Master Perspectives in Cycles
# ---------------------------------------------------------------------------
def render_all_views():
    print("[Render] Starting Cycles rendering of all authentic Mumbai views at 1920x1080...")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.use_nodes = False

    cams = [
        ("arch_1_marinedrive_artdeco.png", "Cam_Arch_1_MarineDrive_ArtDeco", "Marine Drive Art Deco Heritage Row & 6-Lane Coastal Boulevard"),
        ("arch_2_csmt_fort_gothic.png", "Cam_Arch_2_Fort_VictorianHeritage", "CSMT Victoria Terminus & Dr Dadabhai Naoroji Arterial Road"),
        ("arch_3_worli_megatowers.png", "Cam_Arch_3_Worli_MegatowerHighRise", "Worli Megatower Corridor & Annie Besant Road Network"),
        ("arch_4_narimanpoint_waterfront.png", "Cam_Arch_4_NarimanPoint_Waterfront", "Nariman Point Commercial Waterfront & Madame Cama Road"),
        ("arch_5_girgaon_chawls.png", "Cam_Arch_5_Girgaon_ChawlVernacular", "Girgaon Vernacular Chawl Quarter & Traditional Paved Gully"),
        ("arch_6_apollobunder_gateway_taj.png", "Cam_Arch_6_ApolloBunder_HeritagePlaza", "Apollo Bunder Gateway of India & Taj Mahal Palace Basalt Esplanade"),
        ("road_1_marinedrive_streetview.png", "Cam_Player_MarineDrive_Promenade", "Marine Drive Street-Level Road, BMC Curbs & 12M Promenade Close-Up"),
        ("road_2_gateway_plaza_close.png", "Cam_Player_Gateway_Plaza", "Apollo Bunder Ceremonial Basalt Esplanade & Gateway Arch Close-Up")
    ]

    for fname, cname, title in cams:
        cam = bpy.data.objects.get(cname)
        if cam:
            scene.camera = cam
            out_p = os.path.join(OUTPUT_DIR, fname)
            scene.render.filepath = out_p
            print(f"  Rendering {title}...")
            bpy.ops.render.render(write_still=True)
            print(f"    Saved: {out_p}")

if __name__ == "__main__":
    build_definitive_masterpiece()
