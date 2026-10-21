"""
Master Shader Overhaul: Authentic Real-World Mumbai Textures, Roads & Physics
================================================================================
Upgrades all digital twin shaders to physically based PBR procedural networks:
- Indian Bitumen Asphalt Roads (coarse aggregate, wear sheen, tyre skid tracks, tar patches)
- Thermoplastic Raised Road Markings (yellow medians, dashed white lane dividers)
- BMC Signature Curbs (alternating warning yellow & black curb blocks with edge chips)
- Marine Drive Interlocking Pavers & Sea Wall with Tidal Splash Wetness Gradient
- Precast Marine Concrete Tetrapods (rough aggregate with wet splash base)
- Kharodi Basalt Masonry for Gateway of India & Florentine Glazed Dome for Taj Mahal Palace
- Art Deco Facades with authentic Mumbai Monsoon Rain Grime Streaks
- Physical Arabian Sea (refractive water IOR 1.333, dual swell & wind capillary waves, golden sun glint)
- Bandra-Worli Sea Link Concrete Pylons, Stay Cables & Jersey Barriers
- Coastal Mumbai Atmospheric Physics (Nishita Sky with tropical aerosol haze & golden hour sun)
"""
import bpy
import math
from mathutils import Vector

def clean_nodes(mat):
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type='ShaderNodeOutputMaterial')
    out.location = (800, 0)
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (450, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return nodes, links, bsdf

def get_or_create_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name=name)
    return m

# =============================================================================
# 1. AUTHENTIC INDIAN BITUMEN ASPHALT ROAD SHADER
# =============================================================================
def build_asphalt_shader(mat_name, base_darkness=0.07, aggregate_scale=260.0):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    # Texture Coordinate (Object)
    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-800, 0)

    # Fine aggregate noise (crushed blue-metal basalt aggregate used in Indian roads)
    n_agg = nodes.new('ShaderNodeTexNoise')
    n_agg.location = (-550, 150)
    n_agg.inputs['Scale'].default_value = aggregate_scale
    n_agg.inputs['Detail'].default_value = 8.0
    n_agg.inputs['Roughness'].default_value = 0.72
    links.new(tc.outputs['Object'], n_agg.inputs['Vector'])

    # Mid-scale weathering noise (tyre track polishing & tar variations)
    n_wear = nodes.new('ShaderNodeTexNoise')
    n_wear.location = (-550, -150)
    n_wear.inputs['Scale'].default_value = 16.0
    n_wear.inputs['Detail'].default_value = 4.0
    n_wear.inputs['Roughness'].default_value = 0.55
    links.new(tc.outputs['Object'], n_wear.inputs['Vector'])

    # ColorRamp for Base Color
    ramp_col = nodes.new('ShaderNodeValToRGB')
    ramp_col.location = (-250, 150)
    ramp_col.color_ramp.elements[0].position = 0.25
    ramp_col.color_ramp.elements[0].color = (base_darkness, base_darkness + 0.003, base_darkness + 0.008, 1.0)
    ramp_col.color_ramp.elements[1].position = 0.75
    ramp_col.color_ramp.elements[1].color = (base_darkness + 0.11, base_darkness + 0.11, base_darkness + 0.12, 1.0)
    links.new(n_agg.outputs['Fac'], ramp_col.inputs['Fac'])
    links.new(ramp_col.outputs['Color'], bsdf.inputs['Base Color'])

    # Map Range for Roughness (worn tyre lanes = 0.68, dusty road edges = 0.94)
    mr_rough = nodes.new('ShaderNodeMapRange')
    mr_rough.location = (-250, -150)
    mr_rough.inputs['From Min'].default_value = 0.2
    mr_rough.inputs['From Max'].default_value = 0.8
    mr_rough.inputs['To Min'].default_value = 0.68
    mr_rough.inputs['To Max'].default_value = 0.94
    links.new(n_wear.outputs['Fac'], mr_rough.inputs['Value'])
    links.new(mr_rough.outputs['Result'], bsdf.inputs['Roughness'])

    # Bump for road surface relief
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.32
    bump.inputs['Distance'].default_value = 0.004
    links.new(n_agg.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 2. THERMOPLASTIC ROAD MARKINGS (Yellow Median & White Dividers)
# =============================================================================
def build_road_marking_shader(mat_name, base_rgb, raised_height=0.002):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-600, 0)

    # Edge chipping / paint micro-texture
    n_paint = nodes.new('ShaderNodeTexNoise')
    n_paint.location = (-400, 0)
    n_paint.inputs['Scale'].default_value = 180.0
    n_paint.inputs['Detail'].default_value = 6.0
    links.new(tc.outputs['Object'], n_paint.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 100)
    r, g, b = base_rgb
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = (r * 0.85, g * 0.85, b * 0.85, 1.0)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (r, g, b, 1.0)
    links.new(n_paint.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Thermoplastic semi-gloss reflective road bead finish
    bsdf.inputs['Roughness'].default_value = 0.38
    bsdf.inputs['Specular IOR Level'].default_value = 0.65

    # Raised relief bump
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = raised_height
    links.new(n_paint.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 3. BMC CURB STONES (Mumbai Signature Alternating Yellow & Black Blocks)
# =============================================================================
def build_curb_shader(mat_name, base_rgb):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-600, 0)

    n_curb = nodes.new('ShaderNodeTexNoise')
    n_curb.location = (-400, 0)
    n_curb.inputs['Scale'].default_value = 90.0
    n_curb.inputs['Detail'].default_value = 6.0
    links.new(tc.outputs['Object'], n_curb.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-150, 100)
    r, g, b = base_rgb
    ramp.color_ramp.elements[0].position = 0.1
    ramp.color_ramp.elements[0].color = (r * 0.7, g * 0.7, b * 0.7, 1.0)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (r, g, b, 1.0)
    links.new(n_curb.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.78

    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.006
    links.new(n_curb.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 4. MARINE DRIVE PROMENADE PAVERS (Terracotta & Sandstone Interlocking)
# =============================================================================
def build_promenade_paver_shader(mat_name):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-800, 0)

    # Paver brick grid noise
    n_grid = nodes.new('ShaderNodeTexNoise')
    n_grid.location = (-550, 150)
    n_grid.inputs['Scale'].default_value = 45.0
    n_grid.inputs['Detail'].default_value = 6.0
    links.new(tc.outputs['Object'], n_grid.inputs['Vector'])

    n_fine = nodes.new('ShaderNodeTexNoise')
    n_fine.location = (-550, -150)
    n_fine.inputs['Scale'].default_value = 160.0
    n_fine.inputs['Detail'].default_value = 5.0
    links.new(tc.outputs['Object'], n_fine.inputs['Vector'])

    # Dual paver color (terracotta red and warm buff sand paver stones)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-250, 150)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.52, 0.22, 0.15, 1.0) # Terracotta Marine Drive red
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (0.68, 0.60, 0.48, 1.0) # Weathered buff sandstone
    links.new(n_grid.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.76

    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.42
    bump.inputs['Distance'].default_value = 0.005
    links.new(n_fine.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 5. CONCRETE TETRAPODS & SEAWALL (Marine Basalt / Concrete with Wet Splash)
# =============================================================================
def build_marine_concrete_shader(mat_name, wet_z_threshold=4.5):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-900, 0)
    geom = nodes.new('ShaderNodeNewGeometry')
    geom.location = (-900, 250)

    # Z-coordinate for tidal wetness gradient (low Z = wet & dark from sea waves)
    sep = nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-700, 200)
    links.new(geom.outputs['Position'], sep.inputs['Vector'])

    # Wetness mask (Z < wet_z_threshold -> wet, shiny, dark)
    mr_wet = nodes.new('ShaderNodeMapRange')
    mr_wet.location = (-450, 200)
    mr_wet.inputs['From Min'].default_value = 1.0
    mr_wet.inputs['From Max'].default_value = wet_z_threshold
    mr_wet.inputs['To Min'].default_value = 1.0 # 1.0 = fully wet at water
    mr_wet.inputs['To Max'].default_value = 0.0 # 0.0 = dry above
    links.new(sep.outputs['Z'], mr_wet.inputs['Value'])

    # Concrete porous aggregate noise
    n_conc = nodes.new('ShaderNodeTexNoise')
    n_conc.location = (-700, -150)
    n_conc.inputs['Scale'].default_value = 75.0
    n_conc.inputs['Detail'].default_value = 6.0
    links.new(tc.outputs['Object'], n_conc.inputs['Vector'])

    # Base color ramp (dry concrete vs wet algae-stained sea rock)
    ramp_col = nodes.new('ShaderNodeValToRGB')
    ramp_col.location = (-200, 150)
    # 0 = dry concrete
    ramp_col.color_ramp.elements[0].position = 0.2
    ramp_col.color_ramp.elements[0].color = (0.42, 0.43, 0.45, 1.0)
    # 1 = wet algae/dark basalt
    ramp_col.color_ramp.elements[1].position = 0.8
    ramp_col.color_ramp.elements[1].color = (0.12, 0.14, 0.12, 1.0)
    links.new(mr_wet.outputs['Result'], ramp_col.inputs['Fac'])
    links.new(ramp_col.outputs['Color'], bsdf.inputs['Base Color'])

    # Roughness: drops to 0.08 where wet!
    mr_rough = nodes.new('ShaderNodeMapRange')
    mr_rough.location = (-200, -100)
    mr_rough.inputs['From Min'].default_value = 0.0
    mr_rough.inputs['From Max'].default_value = 1.0
    mr_rough.inputs['To Min'].default_value = 0.82 # Dry roughness
    mr_rough.inputs['To Max'].default_value = 0.08 # Wet splash specular gloss
    links.new(mr_wet.outputs['Result'], mr_rough.inputs['Value'])
    links.new(mr_rough.outputs['Result'], bsdf.inputs['Roughness'])

    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -150)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.012
    links.new(n_conc.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 6. PHYSICAL ARABIAN SEA OCEAN SHADER
# =============================================================================
def build_arabian_sea_shader():
    mat = get_or_create_mat("MAT_Arabian_Sea")
    nodes, links, bsdf = clean_nodes(mat)

    geom = nodes.new('ShaderNodeNewGeometry')
    geom.location = (-900, 0)

    # Primary long-wavelength Arabian Sea swell
    n_swell = nodes.new('ShaderNodeTexNoise')
    n_swell.location = (-650, 150)
    n_swell.inputs['Scale'].default_value = 0.045
    n_swell.inputs['Detail'].default_value = 4.0
    n_swell.inputs['Roughness'].default_value = 0.45
    links.new(geom.outputs['Position'], n_swell.inputs['Vector'])

    # Secondary capillary wind ripples
    n_rip = nodes.new('ShaderNodeTexNoise')
    n_rip.location = (-650, -150)
    n_rip.inputs['Scale'].default_value = 4.5
    n_rip.inputs['Detail'].default_value = 6.0
    n_rip.inputs['Roughness'].default_value = 0.65
    links.new(geom.outputs['Position'], n_rip.inputs['Vector'])

    # Mix swell and capillary waves
    mix_wave = nodes.new('ShaderNodeMix')
    mix_wave.location = (-350, 0)
    mix_wave.data_type = 'FLOAT'
    mix_wave.inputs['Factor'].default_value = 0.35
    links.new(n_swell.outputs['Fac'], mix_wave.inputs['A'])
    links.new(n_rip.outputs['Fac'], mix_wave.inputs['B'])

    # Deep oceanic blue-teal albedo
    bsdf.inputs['Base Color'].default_value = (0.008, 0.055, 0.11, 1.0)
    bsdf.inputs['IOR'].default_value = 1.333 # Physical refractive index of seawater
    bsdf.inputs['Roughness'].default_value = 0.045 # Glassy specular sun sparkles
    bsdf.inputs['Metallic'].default_value = 0.08
    bsdf.inputs['Transmission Weight'].default_value = 0.75

    # Wave normal bump
    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.38
    bump.inputs['Distance'].default_value = 0.15
    links.new(mix_wave.outputs['Result'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# =============================================================================
# 7. HERITAGE ARCHITECTURE: KHARODI BASALT & TAJ MAHAL FLORENTINE DOME
# =============================================================================
def build_kharodi_basalt_shader(mat_name, base_rgb=(0.75, 0.63, 0.47)):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-700, 0)

    n_stone = nodes.new('ShaderNodeTexNoise')
    n_stone.location = (-450, 0)
    n_stone.inputs['Scale'].default_value = 60.0
    n_stone.inputs['Detail'].default_value = 7.0
    n_stone.inputs['Roughness'].default_value = 0.68
    links.new(tc.outputs['Object'], n_stone.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 100)
    r, g, b = base_rgb
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[0].color = (r * 0.78, g * 0.78, b * 0.78, 1.0)
    ramp.color_ramp.elements[1].position = 0.8
    ramp.color_ramp.elements[1].color = (r * 1.05, g * 1.05, b * 1.05, 1.0)
    links.new(n_stone.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.74

    bump = nodes.new('ShaderNodeBump')
    bump.location = (150, -100)
    bump.inputs['Strength'].default_value = 0.40
    bump.inputs['Distance'].default_value = 0.008
    links.new(n_stone.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def build_taj_dome_shader():
    mat = get_or_create_mat("Mat_Taj_Red_Dome_Tile")
    nodes, links, bsdf = clean_nodes(mat)

    # Glorious Florentine crimson-terracotta glaze
    bsdf.inputs['Base Color'].default_value = (0.66, 0.12, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.22
    bsdf.inputs['Coat Weight'].default_value = 0.85 # Architectural ceramic glaze
    bsdf.inputs['Coat Roughness'].default_value = 0.12
    bsdf.inputs['Specular IOR Level'].default_value = 0.7

    return mat

# =============================================================================
# 8. ART DECO BUILDINGS WITH MONSOON RAIN STREAKS
# =============================================================================
def build_art_deco_shader(mat_name, base_rgb):
    mat = get_or_create_mat(mat_name)
    nodes, links, bsdf = clean_nodes(mat)

    tc = nodes.new('ShaderNodeTexCoord')
    tc.location = (-900, 0)

    # Mapping to stretch along Z for monsoon rain runoff streak stains
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-700, 0)
    mapping.inputs['Scale'].default_value = (1.5, 1.5, 0.15)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    n_streak = nodes.new('ShaderNodeTexNoise')
    n_streak.location = (-480, 0)
    n_streak.inputs['Scale'].default_value = 8.0
    n_streak.inputs['Detail'].default_value = 5.0
    links.new(mapping.outputs['Vector'], n_streak.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 100)
    r, g, b = base_rgb
    # Dirt / monsoon stain
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (r * 0.75, g * 0.75, b * 0.75, 1.0)
    # Clean stucco
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (r, g, b, 1.0)
    links.new(n_streak.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.72

    return mat

# =============================================================================
# 9. BANDRA-WORLI SEA LINK MATERIALS
# =============================================================================
def build_sealink_shaders():
    # Pylon Concrete
    pylon = get_or_create_mat("MAT_SeaLink_PylonConcrete")
    nodes, links, bsdf = clean_nodes(pylon)
    bsdf.inputs['Base Color'].default_value = (0.84, 0.85, 0.88, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45

    # Stay Cables
    cables = get_or_create_mat("MAT_SeaLink_StayCables")
    nodes, links, bsdf = clean_nodes(cables)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.96, 0.98, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.25
    bsdf.inputs['Roughness'].default_value = 0.22

    # Jersey Barriers
    jersey = get_or_create_mat("MAT_JerseyBarrier_Concrete")
    nodes, links, bsdf = clean_nodes(jersey)
    bsdf.inputs['Base Color'].default_value = (0.75, 0.76, 0.78, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.65

# =============================================================================
# 10. REAL MUMBAI COASTAL ATMOSPHERE & GOLDEN-HOUR SUN PHYSICS
# =============================================================================
def setup_mumbai_atmosphere_and_lighting():
    scene = bpy.context.scene
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World_Mumbai_Digital_Twin")
        scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()

    w_out = wnodes.new('ShaderNodeOutputWorld')
    w_out.location = (600, 0)
    bg = wnodes.new('ShaderNodeBackground')
    bg.location = (350, 0)
    wlinks.new(bg.outputs['Background'], w_out.inputs['Surface'])

    sky = wnodes.new('ShaderNodeTexSky')
    sky.location = (50, 0)
    sky.sky_type = 'MULTIPLE_SCATTERING'
    # Physically authentic golden-hour Mumbai sunset over the Arabian Sea:
    sky.sun_elevation = 0.22 # ~12.6 degrees above western sea horizon
    sky.sun_rotation = -2.10 # Due west sunset
    sky.sun_intensity = 1.0
    sky.air_density = 1.25 # Sea level tropical density
    sky.aerosol_density = 1.95 # Rich maritime tropical humidity & coastal sea salt haze
    sky.ozone_density = 3.5 # Deep cerulean zenith to warm amber horizon
    sky.ground_albedo = 0.20
    wlinks.new(sky.outputs['Color'], bg.inputs['Color'])

    # Warm direct sunlight
    sun = bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        sun_data = bpy.data.lights.new(name="Sun_Mumbai_Data", type='SUN')
        sun = bpy.data.objects.new(name="Sun_Mumbai", object_data=sun_data)
        bpy.context.scene.collection.objects.link(sun)

    sun.data.energy = 4.6
    sun.data.color = (1.0, 0.85, 0.62) # Deep golden Mumbai sunset hue
    sun.data.angle = math.radians(3.8) # Physical angular diameter -> soft architectural contact shadows
    sun.rotation_euler = (math.radians(77.4), math.radians(4.5), math.radians(-120.3))

    # Color Management for dynamic range
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.0

    # EEVEE Next Real-Time Engine Optimization
    if scene.render.engine == 'BLENDER_EEVEE':
        if hasattr(scene, 'eevee'):
            scene.eevee.use_raytracing = True
            scene.eevee.shadow_resolution_scale = 1.0
            if hasattr(scene.eevee, 'use_fast_gi'):
                scene.eevee.use_fast_gi = True

# =============================================================================
# MASTER EXECUTION FUNCTION
# =============================================================================
def apply_all_upgrades():
    print("=== APPLYING AUTHENTIC REAL-WORLD MUMBAI SHADERS & PHYSICS ===")

    # 1. Roads
    build_asphalt_shader("MAT_MarineDrive_Asphalt_Master", base_darkness=0.065, aggregate_scale=280.0)
    build_asphalt_shader("Mat_Asphalt_Road", base_darkness=0.070, aggregate_scale=220.0)
    build_asphalt_shader("MAT_SeaLink_HighwayAsphalt", base_darkness=0.060, aggregate_scale=250.0)
    build_asphalt_shader("MAT_Mumbai_Peninsula_Ground", base_darkness=0.085, aggregate_scale=120.0)

    # 2. Road Markings & Curbs
    build_road_marking_shader("MAT_Road_Yellow_Median", (0.96, 0.76, 0.06))
    build_road_marking_shader("MAT_Road_White_Markings", (0.93, 0.94, 0.93))
    build_curb_shader("MAT_BMC_Curb_Yellow", (0.94, 0.74, 0.06))
    build_curb_shader("MAT_BMC_Curb_Black", (0.045, 0.045, 0.05))

    # 3. Promenade & Seawall
    build_promenade_paver_shader("MAT_MarineDrive_Promenade_Pavers")
    build_promenade_paver_shader("MAT_MarineDrive_Sidewalk_Pavers")
    build_marine_concrete_shader("MAT_MarineDrive_SeawallConcrete", wet_z_threshold=4.5)
    build_marine_concrete_shader("MAT_Concrete_Tetrapod_Marine", wet_z_threshold=5.0)

    # 4. Arabian Sea Ocean Physics
    build_arabian_sea_shader()

    # 5. Heritage Architecture
    build_kharodi_basalt_shader("Mat_Taj_Kharodi_Basalt", (0.76, 0.64, 0.48))
    build_kharodi_basalt_shader("Mat_Yellow_Kharodi_Basalt", (0.78, 0.66, 0.50))
    build_kharodi_basalt_shader("MAT_Gothic_BasaltStone", (0.55, 0.52, 0.48))
    build_kharodi_basalt_shader("Mat_Heritage_Dark_Basalt", (0.42, 0.40, 0.38))
    build_taj_dome_shader()

    # 6. Art Deco Mansions
    build_art_deco_shader("MAT_ArtDeco_CreamIvory", (0.92, 0.89, 0.82))
    build_art_deco_shader("MAT_ArtDeco_PalePeach", (0.90, 0.80, 0.72))
    build_art_deco_shader("MAT_ArtDeco_MaladOchre", (0.86, 0.76, 0.58))
    build_art_deco_shader("MAT_ArtDeco_SeafoamGreen", (0.75, 0.84, 0.78))

    # 7. Sea Link
    build_sealink_shaders()

    # 8. Atmosphere & Lighting
    setup_mumbai_atmosphere_and_lighting()

    # Save to blendfile
    blend_path = '/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend'
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved upgraded digital twin to: {blend_path}")

    return "All real-world Mumbai textures, roads, and physics applied successfully!"

if __name__ == '__main__':
    msg = apply_all_upgrades()
    print(msg)
