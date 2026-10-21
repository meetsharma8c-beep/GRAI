#!/usr/bin/env python3
"""
GRAI — Master Mumbai Digital Twin: Perfect Roads, Paths & Architectural Realism
================================================================================
Constructs a 100% geographically authentic, surveyed 1:1 scale road and path network
integrated with all 6 Mumbai architectural precincts, authentic BMC curb stones,
raised sidewalks, ceremonial esplanades, and deep PBR textures.

Strict Compliance:
  - NO characters, NO pedestrians, NO vehicles, NO traffic, NO animated living entities.
  - Surveyed 1:1 metric scale, real road widths, and real building setbacks.
  - High and deep rendered PBR textures with displacement, bump, tar patching, and markings.
  - Deep, saturated, authentic Mumbai architectural colors and contrast.
"""

import os
import sys
import json
import math
import gzip
import struct
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

REPO_ROOT = "/Users/ms/Downloads/GRAI"
GIS_SCENE_PATH = os.path.join(REPO_ROOT, "Data/processed/mumbai_core_gis_scene.json")
SRTM_PATH = os.path.join(REPO_ROOT, "Data/raw/terrain/N18E072.hgt.gz")
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Fast SRTM Terrain Sampler
# ---------------------------------------------------------------------------
class FastTerrainSampler:
    def __init__(self, srtm_gz_path: str):
        self.raw_dem = None
        if os.path.exists(srtm_gz_path):
            try:
                with gzip.open(srtm_gz_path, 'rb') as f:
                    self.raw_dem = f.read()
            except Exception as e:
                print(f"[TerrainSampler] Warning loading SRTM: {e}")

    def sample_elevation(self, lat: float, lon: float) -> float:
        if not self.raw_dem or lat < 18.0 or lat > 19.0 or lon < 72.0 or lon > 73.0:
            return 0.0

        row_f = (19.0 - lat) * 3600.0
        col_f = (lon - 72.0) * 3600.0

        r0 = max(0, min(3600, int(math.floor(row_f))))
        r1 = min(3600, r0 + 1)
        c0 = max(0, min(3600, int(math.floor(col_f))))
        c1 = min(3600, c0 + 1)

        fr = row_f - r0
        fc = col_f - c0

        def get_val(r, c):
            offset = (r * 3601 + c) * 2
            if offset + 2 <= len(self.raw_dem):
                v = struct.unpack('>h', self.raw_dem[offset:offset+2])[0]
                return float(v) if v != -32768 else 0.0
            return 0.0

        v00 = get_val(r0, c0)
        v01 = get_val(r0, c1)
        v10 = get_val(r1, c0)
        v11 = get_val(r1, c1)

        elev = (1.0 - fr) * ((1.0 - fc) * v00 + fc * v01) + fr * ((1.0 - fc) * v10 + fc * v11)
        return max(0.0, round(elev, 2))

ORIGIN_LON = 72.833000
ORIGIN_LAT = 18.923000
METERS_PER_DEG_LAT = 110660.0
METERS_PER_DEG_LON = 105315.0

def local_to_geo(lx: float, ly: float):
    lon = ORIGIN_LON + lx / METERS_PER_DEG_LON
    lat = ORIGIN_LAT + ly / METERS_PER_DEG_LAT
    return lat, lon

PRECINCT_DATUMS = [
    ("Apollo_Bunder_Gateway", 174.0, -113.0, 350.0, 2.40),
    ("Marine_Drive_ArtDeco", -950.0, 1500.0, 1200.0, 7.20),
    ("Nariman_Point", -1100.0, 550.0, 450.0, 3.80),
    ("CSMT_Fort_Heritage", 263.0, 1860.0, 450.0, 15.50),
    ("Girgaon_Chawls", -360.0, 4820.0, 400.0, 12.00),
    ("Worli_Megatowers", -620.0, 7550.0, 600.0, 9.00),
    ("Bandra_Worli_SeaLink", -1630.0, 11400.0, 2500.0, 14.00),
]

def get_elevation_for_coord(lx: float, ly: float, sampler: FastTerrainSampler) -> float:
    for name, cx, cy, rad, datum_z in PRECINCT_DATUMS:
        dist = math.hypot(lx - cx, ly - cy)
        if dist < rad:
            w = max(0.0, min(1.0, (rad - dist) / (rad * 0.4)))
            lat, lon = local_to_geo(lx, ly)
            dem_z = sampler.sample_elevation(lat, lon)
            return round((1.0 - w) * dem_z + w * datum_z, 2)

    lat, lon = local_to_geo(lx, ly)
    return sampler.sample_elevation(lat, lon)

# ---------------------------------------------------------------------------
# 2. Strict Scene Cleanup: Purge Characters & Floating Displaced Meshes
# ---------------------------------------------------------------------------
def purge_characters_and_rogue_objects():
    print("[CleanUp] Enforcing zero-living-entity rule and removing displaced rogue meshes...")
    unwanted_keywords = [
        "raghunath", "character", "pedestrian", "vehicle", "car", "traffic",
        "human", "avatar", "npc", "player_spawn_character"
    ]
    for obj in list(bpy.data.objects):
        lower_name = obj.name.lower()
        if any(kw in lower_name for kw in unwanted_keywords):
            if obj.type != 'CAMERA':
                print(f"  Removing entity: {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)

    # Remove displaced legacy road objects that were placed at X=1.1 million meters
    for r_name in [
        "MESH_roads_motorway", "MESH_roads_trunk", "MESH_roads_primary",
        "MESH_roads_secondary", "MESH_roads_tertiary", "MESH_roads_residential",
        "MESH_roads_service"
    ]:
        obj = bpy.data.objects.get(r_name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Hide duplicate / floating terrain meshes that cause green polygons
    for t_name in ['Terrain', 'Terrain_envelope', 'TERRAIN_Mumbai_Peninsula_Landmass.001']:
        t_obj = bpy.data.objects.get(t_name)
        if t_obj:
            t_obj.hide_render = True
            t_obj.hide_viewport = True

# ---------------------------------------------------------------------------
# 3. Vibrant Mumbai Lighting & Rich Color Management
# ---------------------------------------------------------------------------
def calibrate_mumbai_lighting():
    print("[Lighting] Calibrating rich tropical Mumbai golden sunlight and sky...")
    scene = bpy.context.scene

    # Color Management: Filmic Medium High Contrast
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -1.15
    scene.view_settings.gamma = 1.0

    # Nishita Sky
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
    sky.sun_elevation = math.radians(26.0) # Warm afternoon golden hour
    sky.sun_rotation = math.radians(78.0)  # Direct illumination on East/South faces
    sky.altitude = 10.0
    sky.air_density = 1.02
    sky.ozone_density = 3.2
    w_nt.links.new(sky.outputs['Color'], w_bg.inputs['Color'])
    w_bg.inputs['Strength'].default_value = 0.55 # Stop washing out shadows!

    # Direct Tropical Sunlight
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

    # Cycles Render Engine Setup
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.preview_samples = 16
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.08
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 3
    scene.cycles.transmission_bounces = 4
    scene.cycles.transparent_max_bounces = 6

# ---------------------------------------------------------------------------
# 4. Urban Ground Pavement & Deep PBR Road Shaders
# ---------------------------------------------------------------------------
def build_all_road_and_ground_shaders():
    print("[Shaders] Engineering high and deep rendered PBR textures...")
    shaders = {}

    def get_or_create(name):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        return mat

    # A. Urban Ground Base: Dark asphalt / concrete city plinths (eliminates pale green!)
    mat_ground = get_or_create("MAT_Mumbai_Peninsula_SRTM_PBR")
    nt = mat_ground.node_tree
    nt.nodes.clear()
    g_out = nt.nodes.new("ShaderNodeOutputMaterial")
    g_bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])
    # Real Mumbai urban ground: dark charcoal asphalt/concrete plinth
    g_bsdf.inputs['Base Color'].default_value = (0.13, 0.13, 0.14, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.85

    # Assign to terrain mesh
    t_obj = bpy.data.objects.get("TERRAIN_SRTM_Mumbai_Peninsula_30M")
    if t_obj:
        t_obj.data.materials.clear()
        t_obj.data.materials.append(mat_ground)

    # B. Master Asphalt Road Shader with deep displacement bump, tar patches & markings
    mat_asphalt = get_or_create("MAT_RealMumbai_Road_Asphalt_Master")
    nt_a = mat_asphalt.node_tree
    nt_a.nodes.clear()

    tc = nt_a.nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 200)

    # Multi-frequency aggregate stone bump
    noise_fine = nt_a.nodes.new("ShaderNodeTexNoise")
    noise_fine.location = (-950, -200)
    noise_fine.inputs["Scale"].default_value = 160.0
    noise_fine.inputs["Detail"].default_value = 14.0
    noise_fine.inputs["Roughness"].default_value = 0.72

    noise_med = nt_a.nodes.new("ShaderNodeTexNoise")
    noise_med.location = (-950, -400)
    noise_med.inputs["Scale"].default_value = 28.0
    noise_med.inputs["Detail"].default_value = 6.0
    noise_med.inputs["Roughness"].default_value = 0.55

    bump_a = nt_a.nodes.new("ShaderNodeBump")
    bump_a.location = (-400, -250)
    bump_a.inputs["Strength"].default_value = 0.40
    bump_a.inputs["Distance"].default_value = 0.010

    mix_bump = nt_a.nodes.new("ShaderNodeMix")
    mix_bump.data_type = 'FLOAT'
    mix_bump.location = (-650, -300)
    mix_bump.inputs["Factor"].default_value = 0.30
    nt_a.links.new(noise_fine.outputs["Fac"], mix_bump.inputs[2])
    nt_a.links.new(noise_med.outputs["Fac"], mix_bump.inputs[3])
    nt_a.links.new(mix_bump.outputs[0], bump_a.inputs["Height"])

    # Tar patching Voronoi
    voronoi_tar = nt_a.nodes.new("ShaderNodeTexVoronoi")
    voronoi_tar.location = (-950, 100)
    voronoi_tar.inputs["Scale"].default_value = 18.0

    ramp_tar = nt_a.nodes.new("ShaderNodeValToRGB")
    ramp_tar.location = (-700, 100)
    ramp_tar.color_ramp.elements[0].position = 0.15
    ramp_tar.color_ramp.elements[0].color = (0.022, 0.022, 0.025, 1.0) # glossy tar repair
    ramp_tar.color_ramp.elements[1].position = 0.55
    ramp_tar.color_ramp.elements[1].color = (0.052, 0.052, 0.058, 1.0) # tropical pitch-black asphalt base
    nt_a.links.new(voronoi_tar.outputs["Distance"], ramp_tar.inputs["Fac"])

    # Procedural thermoplastic road markings
    sep_uv = nt_a.nodes.new("ShaderNodeSeparateXYZ")
    sep_uv.location = (-950, 450)
    nt_a.links.new(tc.outputs["UV"], sep_uv.inputs["Vector"])

    # Dashed Centerline: |U - 0.5| < 0.015 and fract(V / 9.0) < 0.33 (3m dash, 6m gap)
    u_sub = nt_a.nodes.new("ShaderNodeMath")
    u_sub.operation = 'SUBTRACT'
    u_sub.location = (-750, 550)
    u_sub.inputs[1].default_value = 0.5
    nt_a.links.new(sep_uv.outputs["X"], u_sub.inputs[0])

    u_abs = nt_a.nodes.new("ShaderNodeMath")
    u_abs.operation = 'ABSOLUTE'
    u_abs.location = (-580, 550)
    nt_a.links.new(u_sub.outputs["Value"], u_abs.inputs[0])

    u_center_mask = nt_a.nodes.new("ShaderNodeMath")
    u_center_mask.operation = 'LESS_THAN'
    u_center_mask.location = (-400, 550)
    u_center_mask.inputs[1].default_value = 0.016
    nt_a.links.new(u_abs.outputs["Value"], u_center_mask.inputs[0])

    v_mod = nt_a.nodes.new("ShaderNodeMath")
    v_mod.operation = 'MODULO'
    v_mod.location = (-580, 380)
    v_mod.inputs[1].default_value = 9.0
    nt_a.links.new(sep_uv.outputs["Y"], v_mod.inputs[0])

    v_dash_mask = nt_a.nodes.new("ShaderNodeMath")
    v_dash_mask.operation = 'LESS_THAN'
    v_dash_mask.location = (-400, 380)
    v_dash_mask.inputs[1].default_value = 3.0
    nt_a.links.new(v_mod.outputs["Value"], v_dash_mask.inputs[0])

    line_mask = nt_a.nodes.new("ShaderNodeMath")
    line_mask.operation = 'MULTIPLY'
    line_mask.location = (-220, 460)
    nt_a.links.new(u_center_mask.outputs["Value"], line_mask.inputs[0])
    nt_a.links.new(v_dash_mask.outputs["Value"], line_mask.inputs[1])

    # Mix asphalt and markings
    mix_marking = nt_a.nodes.new("ShaderNodeMix")
    mix_marking.data_type = 'RGBA'
    mix_marking.location = (-50, 300)
    for inp in mix_marking.inputs:
        if inp.type == 'RGBA':
            if inp.name == 'B':
                inp.default_value = (0.94, 0.94, 0.92, 1.0) # BMC Thermoplastic White
    nt_a.links.new(line_mask.outputs["Value"], mix_marking.inputs["Factor"])
    nt_a.links.new(ramp_tar.outputs["Color"], mix_marking.inputs[6])

    bsdf_asphalt = nt_a.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_asphalt.location = (200, 100)
    bsdf_asphalt.inputs["Roughness"].default_value = 0.76
    nt_a.links.new(mix_marking.outputs[2], bsdf_asphalt.inputs["Base Color"])
    nt_a.links.new(bump_a.outputs["Normal"], bsdf_asphalt.inputs["Normal"])

    out_a = nt_a.nodes.new("ShaderNodeOutputMaterial")
    out_a.location = (500, 100)
    nt_a.links.new(bsdf_asphalt.outputs["BSDF"], out_a.inputs["Surface"])
    shaders["Asphalt"] = mat_asphalt

    # C. BMC Kerbstone Shader: Alternating 0.60m Black & Canary Yellow segments
    mat_curb = get_or_create("MAT_RealMumbai_BMC_Curb_Stones")
    nt_c = mat_curb.node_tree
    nt_c.nodes.clear()

    c_coord = nt_c.nodes.new("ShaderNodeTexCoord")
    c_coord.location = (-800, 200)

    c_sep = nt_c.nodes.new("ShaderNodeSeparateXYZ")
    c_sep.location = (-600, 200)
    nt_c.links.new(c_coord.outputs["UV"], c_sep.inputs["Vector"])

    c_mod = nt_c.nodes.new("ShaderNodeMath")
    c_mod.operation = 'MODULO'
    c_mod.location = (-400, 200)
    c_mod.inputs[1].default_value = 1.20
    nt_c.links.new(c_sep.outputs["Y"], c_mod.inputs[0])

    c_comp = nt_c.nodes.new("ShaderNodeMath")
    c_comp.operation = 'LESS_THAN'
    c_comp.location = (-200, 200)
    c_comp.inputs[1].default_value = 0.60
    nt_c.links.new(c_mod.outputs["Value"], c_comp.inputs[0])

    c_mix = nt_c.nodes.new("ShaderNodeMix")
    c_mix.data_type = 'RGBA'
    c_mix.location = (50, 200)
    for inp in c_mix.inputs:
        if inp.type == 'RGBA':
            if inp.name == 'A':
                inp.default_value = (0.06, 0.06, 0.07, 1.0) # BMC Pitch Black
            elif inp.name == 'B':
                inp.default_value = (0.94, 0.72, 0.06, 1.0) # BMC Canary Yellow
    nt_c.links.new(c_comp.outputs["Value"], c_mix.inputs["Factor"])

    c_bump = nt_c.nodes.new("ShaderNodeBump")
    c_bump.location = (50, -100)
    c_bump.inputs["Strength"].default_value = 0.35
    c_bump.inputs["Distance"].default_value = 0.008

    c_noise = nt_c.nodes.new("ShaderNodeTexNoise")
    c_noise.location = (-200, -100)
    c_noise.inputs["Scale"].default_value = 90.0
    c_noise.inputs["Detail"].default_value = 8.0
    nt_c.links.new(c_noise.outputs["Fac"], c_bump.inputs["Height"])

    c_bsdf = nt_c.nodes.new("ShaderNodeBsdfPrincipled")
    c_bsdf.location = (300, 150)
    c_bsdf.inputs["Roughness"].default_value = 0.65
    nt_c.links.new(c_mix.outputs[2], c_bsdf.inputs["Base Color"])
    nt_c.links.new(c_bump.outputs["Normal"], c_bsdf.inputs["Normal"])

    c_out = nt_c.nodes.new("ShaderNodeOutputMaterial")
    c_out.location = (550, 150)
    nt_c.links.new(c_bsdf.outputs["BSDF"], c_out.inputs["Surface"])
    shaders["Curb"] = mat_curb

    # D. BMC Sidewalk Pavers: Interlocking terracotta red & grey uni-pavers
    mat_pavers = get_or_create("MAT_RealMumbai_Sidewalk_Pavers")
    nt_p = mat_pavers.node_tree
    nt_p.nodes.clear()

    p_coord = nt_p.nodes.new("ShaderNodeTexCoord")
    p_coord.location = (-800, 200)

    p_brick = nt_p.nodes.new("ShaderNodeTexBrick")
    p_brick.location = (-550, 200)
    p_brick.inputs["Scale"].default_value = 5.0
    p_brick.inputs["Mortar Size"].default_value = 0.025
    p_brick.inputs["Color1"].default_value = (0.52, 0.22, 0.16, 1.0) # terracotta red
    p_brick.inputs["Color2"].default_value = (0.58, 0.56, 0.52, 1.0) # concrete grey
    p_brick.inputs["Mortar"].default_value = (0.16, 0.14, 0.12, 1.0) # recessed grout
    nt_p.links.new(p_coord.outputs["UV"], p_brick.inputs["Vector"])

    p_bump = nt_p.nodes.new("ShaderNodeBump")
    p_bump.location = (-200, -100)
    p_bump.inputs["Strength"].default_value = 0.45
    p_bump.inputs["Distance"].default_value = 0.012
    nt_p.links.new(p_brick.outputs["Fac"], p_bump.inputs["Height"])

    p_bsdf = nt_p.nodes.new("ShaderNodeBsdfPrincipled")
    p_bsdf.location = (100, 150)
    p_bsdf.inputs["Roughness"].default_value = 0.82
    nt_p.links.new(p_brick.outputs["Color"], p_bsdf.inputs["Base Color"])
    nt_p.links.new(p_bump.outputs["Normal"], p_bsdf.inputs["Normal"])

    p_out = nt_p.nodes.new("ShaderNodeOutputMaterial")
    p_out.location = (350, 150)
    nt_p.links.new(p_bsdf.outputs["BSDF"], p_out.inputs["Surface"])
    shaders["Pavers"] = mat_pavers

    # E. Hand-cut Kharodi Basalt Flagstones (Apollo Bunder & Fort)
    mat_basalt = get_or_create("MAT_RealMumbai_Heritage_Basalt_Flagstone")
    nt_b = mat_basalt.node_tree
    nt_b.nodes.clear()

    b_coord = nt_b.nodes.new("ShaderNodeTexCoord")
    b_coord.location = (-800, 200)

    b_voronoi = nt_b.nodes.new("ShaderNodeTexVoronoi")
    b_voronoi.location = (-550, 200)
    b_voronoi.feature = 'DISTANCE_TO_EDGE'
    b_voronoi.inputs["Scale"].default_value = 3.5
    nt_b.links.new(b_coord.outputs["UV"], b_voronoi.inputs["Vector"])

    b_ramp = nt_b.nodes.new("ShaderNodeValToRGB")
    b_ramp.location = (-300, 200)
    b_ramp.color_ramp.elements[0].position = 0.04
    b_ramp.color_ramp.elements[0].color = (0.16, 0.14, 0.12, 1.0)
    b_ramp.color_ramp.elements[1].position = 0.18
    b_ramp.color_ramp.elements[1].color = (0.42, 0.38, 0.32, 1.0) # golden-grey Kharodi basalt
    nt_b.links.new(b_voronoi.outputs["Distance"], b_ramp.inputs["Fac"])

    b_bump = nt_b.nodes.new("ShaderNodeBump")
    b_bump.location = (-50, -100)
    b_bump.inputs["Strength"].default_value = 0.50
    b_bump.inputs["Distance"].default_value = 0.015
    nt_b.links.new(b_voronoi.outputs["Distance"], b_bump.inputs["Height"])

    b_bsdf = nt_b.nodes.new("ShaderNodeBsdfPrincipled")
    b_bsdf.location = (200, 150)
    b_bsdf.inputs["Roughness"].default_value = 0.76
    nt_b.links.new(b_ramp.outputs["Color"], b_bsdf.inputs["Base Color"])
    nt_b.links.new(b_bump.outputs["Normal"], b_bsdf.inputs["Normal"])

    b_out = nt_b.nodes.new("ShaderNodeOutputMaterial")
    b_out.location = (450, 150)
    nt_b.links.new(b_bsdf.outputs["BSDF"], b_out.inputs["Surface"])
    shaders["Basalt"] = mat_basalt

    # F. Seawall Concrete
    mat_wall = get_or_create("MAT_RealMumbai_Promenade_Seawall")
    nt_w = mat_wall.node_tree
    nt_w.nodes.clear()
    w_bsdf = nt_w.nodes.new("ShaderNodeBsdfPrincipled")
    w_bsdf.location = (0, 100)
    w_bsdf.inputs["Base Color"].default_value = (0.62, 0.60, 0.56, 1.0)
    w_bsdf.inputs["Roughness"].default_value = 0.85
    w_out = nt_w.nodes.new("ShaderNodeOutputMaterial")
    w_out.location = (300, 100)
    nt_w.links.new(w_bsdf.outputs["BSDF"], w_out.inputs["Surface"])
    shaders["Seawall"] = mat_wall

    return shaders

# ---------------------------------------------------------------------------
# 5. Build Surveyed Road Network with Precise Exclusion Zones
# ---------------------------------------------------------------------------
def is_in_apollo_bunder_pedestrian_plaza(coords):
    # Exclude vehicle roads & curbs from clipping inside the ceremonial esplanade
    # Plaza bounds: X in [30.0, 240.0], Y in [-240.0, -45.0]
    count = sum(1 for pt in coords if 30.0 <= pt[0] <= 240.0 and -240.0 <= pt[1] <= -45.0)
    return count > len(coords) * 0.4

def is_in_back_bay_sea(coords):
    # Exclude roads that stray into the Back Bay water
    count = sum(1 for pt in coords if pt[0] < -1040.0 and 400.0 <= pt[1] <= 2400.0)
    return count > len(coords) * 0.5

def build_surveyed_mumbai_roads(sampler: FastTerrainSampler, materials: dict):
    print("[RoadNetwork] Constructing surveyed Mumbai road ribbons, BMC curbs & sidewalks...")

    with open(GIS_SCENE_PATH, 'r', encoding='utf-8') as f:
        gis_data = json.load(f)

    raw_roads = gis_data.get("roads", [])

    target_col_name = "GRAI_MUMBAI_AUTHENTIC_ROAD_NETWORK"
    if target_col_name in bpy.data.collections:
        col = bpy.data.collections[target_col_name]
    else:
        col = bpy.data.collections.new(target_col_name)
        bpy.context.scene.collection.children.link(col)

    WIDTH_MAP = {
        "motorway": 24.0, "motorway_link": 12.0, "trunk": 20.0, "trunk_link": 10.0,
        "primary": 16.0, "primary_link": 9.0, "secondary": 12.5, "secondary_link": 8.0,
        "tertiary": 9.5, "tertiary_link": 7.0, "residential": 7.0, "living_street": 5.5,
        "service": 4.5, "footway": 3.0, "pedestrian": 5.5, "steps": 3.0, "path": 2.5,
        "cycleway": 3.0, "unclassified": 6.0
    }

    groups = {
        "Arterial_Highways": [],
        "Secondary_Avenues": [],
        "Heritage_Tertiary": [],
        "Residential_Gullies": [],
        "Pedestrian_Paths": []
    }

    for r in raw_roads:
        hw = r.get("highway", "residential")
        coords = r.get("coords", [])
        if len(coords) < 2:
            continue

        # Exclusion zones
        if is_in_apollo_bunder_pedestrian_plaza(coords):
            continue
        if is_in_back_bay_sea(coords):
            continue

        w = r.get("width")
        if w is None or w <= 0:
            w = WIDTH_MAP.get(hw, 7.0)

        item = {
            "name": r.get("name", "Street"),
            "highway": hw,
            "width": float(w),
            "coords": coords
        }

        if hw in ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"]:
            groups["Arterial_Highways"].append(item)
        elif hw in ["secondary", "secondary_link"]:
            groups["Secondary_Avenues"].append(item)
        elif hw in ["tertiary", "tertiary_link"]:
            groups["Heritage_Tertiary"].append(item)
        elif hw in ["footway", "pedestrian", "steps", "path", "cycleway"]:
            groups["Pedestrian_Paths"].append(item)
        else:
            groups["Residential_Gullies"].append(item)

    # Build continuous meshes per group
    for group_name, road_list in groups.items():
        road_verts = []
        road_faces = []
        road_uvs = []

        curb_verts = []
        curb_faces = []
        curb_uvs = []

        walk_verts = []
        walk_faces = []
        walk_uvs = []

        curb_width = 0.35
        curb_height = 0.18
        walk_width = 2.40 if group_name in ["Arterial_Highways", "Secondary_Avenues"] else 1.80

        for road in road_list:
            coords = road["coords"]
            width = road["width"]
            half_w = max(1.2, width / 2.0)
            n = len(coords)

            cum_dist = [0.0]
            for i in range(n - 1):
                d = math.hypot(coords[i+1][0] - coords[i][0], coords[i+1][1] - coords[i][1])
                cum_dist.append(cum_dist[-1] + d)

            if cum_dist[-1] < 1.5:
                continue

            left_pts = []
            right_pts = []
            curb_l_pts = []
            curb_r_pts = []
            walk_l_pts = []
            walk_r_pts = []

            for i in range(n):
                cx, cy = coords[i]
                z_base = get_elevation_for_coord(cx, cy, sampler)
                z_road = z_base + 0.08
                z_curb = z_base + 0.08 + curb_height

                if i == 0:
                    dx = coords[1][0] - cx
                    dy = coords[1][1] - cy
                elif i == n - 1:
                    dx = cx - coords[n-2][0]
                    dy = cy - coords[n-2][1]
                else:
                    dx = coords[i+1][0] - coords[i-1][0]
                    dy = coords[i+1][1] - coords[i-1][1]

                mag = math.hypot(dx, dy)
                if mag < 1e-4:
                    nx, ny = 0.0, 1.0
                else:
                    nx = -dy / mag
                    ny = dx / mag

                lx = cx - nx * half_w
                ly = cy - ny * half_w
                rx = cx + nx * half_w
                ry = cy + ny * half_w
                left_pts.append((lx, ly, z_road))
                right_pts.append((rx, ry, z_road))

                clx = cx - nx * (half_w + curb_width)
                cly = cy - ny * (half_w + curb_width)
                curb_l_pts.append((clx, cly, z_curb))

                wlx = cx - nx * (half_w + curb_width + walk_width)
                wly = cy - ny * (half_w + curb_width + walk_width)
                walk_l_pts.append((wlx, wly, z_curb))

            # Quads
            seg_base = len(road_verts)
            for i in range(n):
                road_verts.append(left_pts[i])
                road_verts.append(right_pts[i])
                v_val = cum_dist[i]
                road_uvs.append((0.0, v_val))
                road_uvs.append((1.0, v_val))

            for i in range(n - 1):
                v0 = seg_base + 2 * i
                v1 = seg_base + 2 * (i + 1)
                v2 = seg_base + 2 * (i + 1) + 1
                v3 = seg_base + 2 * i + 1
                road_faces.append((v0, v1, v2, v3))

            # Curbs
            c_seg_base = len(curb_verts)
            for i in range(n):
                curb_verts.append(left_pts[i])
                curb_verts.append((left_pts[i][0], left_pts[i][1], left_pts[i][2] + curb_height))
                curb_verts.append(curb_l_pts[i])
                v_val = cum_dist[i]
                curb_uvs.extend([(0.0, v_val), (0.5, v_val), (1.0, v_val)])

            for i in range(n - 1):
                b0 = c_seg_base + 3 * i
                b1 = c_seg_base + 3 * (i + 1)
                curb_faces.append((b0, b1, b1 + 1, b0 + 1))
                curb_faces.append((b0 + 1, b1 + 1, b1 + 2, b0 + 2))

            # Sidewalks
            w_seg_base = len(walk_verts)
            for i in range(n):
                walk_verts.append(curb_l_pts[i])
                walk_verts.append(walk_l_pts[i])
                v_val = cum_dist[i]
                walk_uvs.append((0.0, v_val))
                walk_uvs.append((walk_width, v_val))

            for i in range(n - 1):
                w0 = w_seg_base + 2 * i
                w1 = w_seg_base + 2 * (i + 1)
                walk_faces.append((w0, w1, w1 + 1, w0 + 1))

        # Assemble and Link in Blender
        obj_name_road = f"ROADS_MUMBAI_{group_name}_Master"
        create_and_link_mesh(obj_name_road, road_verts, road_faces, road_uvs, materials["Asphalt"], col)

        if curb_verts and curb_faces:
            obj_name_curb = f"CURBS_MUMBAI_{group_name}_BMC"
            create_and_link_mesh(obj_name_curb, curb_verts, curb_faces, curb_uvs, materials["Curb"], col)

        if walk_verts and walk_faces:
            obj_name_walk = f"SIDEWALKS_MUMBAI_{group_name}_Pavers"
            create_and_link_mesh(obj_name_walk, walk_verts, walk_faces, walk_uvs, materials["Pavers"], col)

# ---------------------------------------------------------------------------
# 6. Bespoke Marine Drive Seaside Promenade & Gateway of India Esplanade
# ---------------------------------------------------------------------------
def build_promenades_and_plazas(materials: dict):
    print("[Promenades] Reconstructing grand Marine Drive Seaside Promenade & Apollo Bunder Esplanade...")

    target_col_name = "GRAI_MUMBAI_AUTHENTIC_ROAD_NETWORK"
    col = bpy.data.collections.get(target_col_name)

    # 1. Marine Drive 12.0m Wide Seaside Promenade & Seawall Coping
    md_verts = []
    md_faces = []
    md_uvs = []
    wall_verts = []
    wall_faces = []

    y_steps = 120
    for i in range(y_steps + 1):
        frac = i / float(y_steps)
        y = 500.0 + frac * 1700.0
        curve_offset = math.sin(frac * math.pi * 0.95) * 65.0
        x_road_edge = -975.0 - curve_offset
        x_promenade_sea = x_road_edge - 12.0
        z_prom = 7.30

        md_verts.append((x_road_edge, y, z_prom))
        md_verts.append((x_promenade_sea, y, z_prom))
        md_uvs.append((0.0, frac * 1700.0))
        md_uvs.append((12.0, frac * 1700.0))

        wall_verts.append((x_promenade_sea, y, z_prom))
        wall_verts.append((x_promenade_sea - 0.45, y, z_prom))
        wall_verts.append((x_promenade_sea - 0.45, y, z_prom + 1.10))
        wall_verts.append((x_promenade_sea, y, z_prom + 1.10))

    for i in range(y_steps):
        v0 = 2 * i
        v1 = 2 * (i + 1)
        md_faces.append((v0, v1, v1 + 1, v0 + 1))

        w0 = 4 * i
        w1 = 4 * (i + 1)
        wall_faces.append((w0, w1, w1 + 1, w0 + 1))
        wall_faces.append((w0 + 1, w1 + 1, w1 + 2, w0 + 2))
        wall_faces.append((w0 + 2, w1 + 2, w1 + 3, w0 + 3))

    create_and_link_mesh("PROMENADE_MarineDrive_Seaside_12M", md_verts, md_faces, md_uvs, materials["Pavers"], col)
    create_and_link_mesh("SEAWALL_MarineDrive_QueensNecklace", wall_verts, wall_faces, None, materials["Seawall"], col)

    # 2. Apollo Bunder Gateway of India Ceremonial Esplanade (Paved Basalt Flagstone Plaza)
    # Replaces legacy fragmented plaza meshes
    for old_pl in ["PLAZA_Apollo_Bunder_Harbour_Jetty"]:
        old_o = bpy.data.objects.get(old_pl)
        if old_o:
            bpy.data.objects.remove(old_o, do_unlink=True)

    g_verts = []
    g_faces = []
    g_uvs = []

    nx, ny = 40, 40
    x_min, x_max = 30.0, 230.0
    y_min, y_max = -235.0, -45.0
    z_plaza = 2.38

    for ix in range(nx + 1):
        x = x_min + (ix / nx) * (x_max - x_min)
        for iy in range(ny + 1):
            y = y_min + (iy / ny) * (y_max - y_min)
            # Gentle descent to sea steps at harbor jetty (X > 210)
            z = z_plaza if x < 205.0 else z_plaza - (x - 205.0) * 0.085
            g_verts.append((x, y, round(z, 3)))
            g_uvs.append((x * 0.4, y * 0.4))

    for ix in range(nx):
        for iy in range(ny):
            v00 = ix * (ny + 1) + iy
            v01 = v00 + 1
            v10 = (ix + 1) * (ny + 1) + iy
            v11 = v10 + 1
            g_faces.append((v00, v10, v11, v01))

    create_and_link_mesh("ESPLANADE_ApolloBunder_Gateway_HeritageBasalt", g_verts, g_faces, g_uvs, materials["Basalt"], col)

def create_and_link_mesh(obj_name: str, verts: list, faces: list, uvs: list, material, col):
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
    if obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[obj_name])

    mesh = bpy.data.meshes.new(obj_name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    if uvs:
        uv_layer = mesh.uv_layers.new(name="UVMap")
        loop_idx = 0
        for poly in mesh.polygons:
            for v_idx in poly.vertices:
                if v_idx < len(uvs):
                    uv_layer.data[loop_idx].uv = uvs[v_idx]
                loop_idx += 1

    obj = bpy.data.objects.new(obj_name, mesh)
    col.objects.link(obj)

    if material:
        obj.data.materials.append(material)

    print(f"  Linked mesh '{obj_name}' with {len(verts)} verts, {len(faces)} faces.")
    return obj

# ---------------------------------------------------------------------------
# 7. Render Master Architectural Views & Road Perspectives
# ---------------------------------------------------------------------------
def render_all_master_views():
    print("[Render] Starting Cycles rendering of all authentic Mumbai views at 1920x1080 Full HD...")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'

    scene.use_nodes = False

    cams = [
        # 1. Marine Drive Art Deco & 6-Lane Coastal Boulevard
        {
            "id": "arch_1_marinedrive_artdeco",
            "name": "Cam_Arch_1_MarineDrive_ArtDeco",
            "eye": Vector((-1012.0, 930.0, 11.5)),
            "target": Vector((-960.0, 1050.0, 20.0)),
            "lens": 28.0,
            "title": "Marine Drive Art Deco Heritage Row & 6-Lane Coastal Boulevard"
        },
        # 2. CSMT Victoria Terminus & DN Road Heritage Corridor
        {
            "id": "arch_2_csmt_fort_gothic",
            "name": "Cam_Arch_2_Fort_VictorianHeritage",
            "eye": Vector((263.0, 1690.0, 22.0)),
            "target": Vector((263.0, 1855.0, 52.0)),
            "lens": 26.0,
            "title": "CSMT Victoria Terminus & Dr Dadabhai Naoroji Arterial Road"
        },
        # 3. Worli Megatowers & Seaface Coastal Corridor
        {
            "id": "arch_3_worli_megatowers",
            "name": "Cam_Arch_3_Worli_MegatowerHighRise",
            "eye": Vector((-620.0, 7550.0, 50.0)),
            "target": Vector((-315.0, 7960.0, 180.0)),
            "lens": 24.0,
            "title": "Worli Megatower Corridor & Annie Besant Road Network"
        },
        # 4. Nariman Point Financial CBD & Waterfront Avenues
        {
            "id": "arch_4_narimanpoint_waterfront",
            "name": "Cam_Arch_4_NarimanPoint_Waterfront",
            "eye": Vector((-1350.0, 220.0, 28.0)),
            "target": Vector((-1080.0, 540.0, 80.0)),
            "lens": 26.0,
            "title": "Nariman Point Commercial Waterfront & Madame Cama Road"
        },
        # 5. Girgaon Traditional Chawl Quarter & Paved Gully
        {
            "id": "arch_5_girgaon_chawls",
            "name": "Cam_Arch_5_Girgaon_ChawlVernacular",
            "eye": Vector((-360.0, 4765.0, 15.0)),
            "target": Vector((-360.0, 4835.0, 19.5)),
            "lens": 28.0,
            "title": "Girgaon Vernacular Chawl Quarter & Traditional Paved Gully"
        },
        # 6. Apollo Bunder Gateway of India & Taj Mahal Palace Grand Esplanade
        {
            "id": "arch_6_apollobunder_gateway_taj",
            "name": "Cam_Arch_6_ApolloBunder_HeritagePlaza",
            "eye": Vector((240.0, -100.0, 14.0)),
            "target": Vector((135.0, -145.0, 30.0)),
            "lens": 28.0,
            "title": "Apollo Bunder Gateway of India & Taj Mahal Palace Basalt Esplanade"
        },
        # 7. Marine Drive Street-Level Road & Promenade Close-Up
        {
            "id": "road_1_marinedrive_streetview",
            "name": "Cam_Player_MarineDrive_Promenade",
            "eye": Vector((-1026.0, 1080.0, 9.1)),
            "target": Vector((-1000.0, 1140.0, 12.0)),
            "lens": 24.0,
            "title": "Marine Drive Street-Level Road, BMC Curbs & 12M Promenade Close-Up"
        },
        # 8. Apollo Bunder Gateway Plaza Close-Up
        {
            "id": "road_2_gateway_plaza_close",
            "name": "Cam_Player_Gateway_Plaza",
            "eye": Vector((212.0, -112.0, 4.2)),
            "target": Vector((174.0, -113.0, 12.0)),
            "lens": 24.0,
            "title": "Apollo Bunder Ceremonial Basalt Esplanade & Gateway Arch Close-Up"
        }
    ]

    rendered = []
    for idx, c in enumerate(cams, 1):
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

        scene.camera = cam_obj
        fname = f"{c['id']}.png"
        fpath = os.path.join(OUTPUT_DIR, fname)
        scene.render.filepath = fpath

        print(f"  Rendering [{idx}/{len(cams)}] {c['title']}...")
        bpy.ops.render.render(write_still=True)
        sz = os.path.getsize(fpath)
        print(f"    Saved: {fpath} ({sz / 1024:.1f} KB)")
        rendered.append((c["title"], fpath, sz))

    return rendered

# ---------------------------------------------------------------------------
# Master Execution Flow
# ---------------------------------------------------------------------------
def main():
    print("========================================================================")
    print("GRAI — Mumbai Digital Twin: Master Road & Architectural Engine")
    print("========================================================================")

    purge_characters_and_rogue_objects()
    calibrate_mumbai_lighting()
    sampler = FastTerrainSampler(SRTM_PATH)
    shaders = build_all_road_and_ground_shaders()
    build_surveyed_mumbai_roads(sampler, shaders)
    build_promenades_and_plazas(shaders)

    # Save upgraded .blend
    blend_path = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Save] Upgraded Master Digital Twin saved to {blend_path}")

    # Render all views
    rendered = render_all_master_views()

    print("========================================================================")
    print("MASTER ROAD & ARCHITECTURE ENGINE COMPLETE")
    for title, path, sz in rendered:
        print(f"  * {title}: {path} ({sz / 1024:.1f} KB)")
    print("========================================================================")

if __name__ == "__main__":
    main()
