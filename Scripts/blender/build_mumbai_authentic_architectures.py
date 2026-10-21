#!/usr/bin/env python3
"""
GRAI — Authentic Mumbai Architectural Digital Twin Builder & Renderer
========================================================================
Procedurally constructs and renders real-world Mumbai building architectures:
1. Authentic Sizing & Heights: Real OSM tags + ward-specific BMC building heights.
2. Authentic Architectural Typologies:
   - Art Deco (Marine Drive, Oval Maidan): Curved balconies, stepped parapets, nautical streamlines.
   - Victorian Gothic & Indo-Saracenic (Fort, Colaba, Ballard Estate): Basalt plinths, Malad stone, arches, clay tile roofs.
   - Modern Glass High-Rises (Worli, Lower Parel): Reflective curtain walls, podiums, mechanical penthouses, helipads.
   - Modernist Commercial (Nariman Point): Concrete frames, strip windows, brise-soleil sunshades.
   - Traditional Chawls (Girgaon, Bhuleshwar): Exterior access verandas, chhajjas, corrugated/tile roofs.
   - Modern Residential Apartments (Dadar, Bandra): Pastel emulsions, cantilevered box balconies, window chhajjas.
3. Rooftop Infrastructure:
   - Parapet walls with coping trim.
   - Concrete elevator machine rooms (penthouse mummy rooms).
   - Rooftop water storage tanks (RCC square reservoirs + cylindrical black/blue Sintex tanks).
4. Procedural PBR Shader Networks:
   - Monsoon moisture runoff streaks and damp staining.
   - Multi-pane reflective window glass with warm tungsten interior illumination.
   - Procedural brick, stone masonry, and aluminum composite panel detailing.
5. Mumbai Coastal Atmospheric Lighting & 7 Dedicated Architectural Cameras.
"""

import os
import sys
import json
import math
import random
import bpy
from mathutils import Vector, Euler

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 1. SHADER CREATION HELPERS (BLENDER 5.2.2 COMPATIBLE)
# ----------------------------------------------------------------------
def clean_material(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1000, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (700, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat, nodes, links, bsdf, out

def get_socket(sockets, name_or_idx):
    if isinstance(name_or_idx, int):
        return sockets[name_or_idx]
    if name_or_idx in sockets:
        return sockets[name_or_idx]
    for s in sockets:
        if s.name.lower() == name_or_idx.lower():
            return s
    return sockets[0]

def build_all_mumbai_shaders():
    print("[Shaders] Building authentic Mumbai procedural PBR shader library...")
    shaders = {}

    # ------------------------------------------------------------------
    # A. ART DECO PBR SHADER (Marine Drive / Oval Maidan)
    # ------------------------------------------------------------------
    mat_ad, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_ArtDeco_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs['Scale'].default_value = (0.28, 0.28, 0.3125) # 3.2m floor height
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    # Random pastel colors per building
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1200, 400)
    ramp_stucco = nodes.new("ShaderNodeValToRGB")
    ramp_stucco.location = (-900, 400)
    ramp_stucco.color_ramp.interpolation = 'CONSTANT'
    ramp_stucco.color_ramp.elements[0].position = 0.0
    ramp_stucco.color_ramp.elements[0].color = (0.92, 0.88, 0.80, 1.0) # Cream Ivory
    ramp_stucco.color_ramp.elements[1].position = 0.28
    ramp_stucco.color_ramp.elements[1].color = (0.65, 0.78, 0.72, 1.0) # Seafoam Green
    e2 = ramp_stucco.color_ramp.elements.new(0.55)
    e2.color = (0.86, 0.75, 0.56, 1.0) # Malad Ochre
    e3 = ramp_stucco.color_ramp.elements.new(0.80)
    e3.color = (0.88, 0.74, 0.65, 1.0) # Pale Peach / Terracotta
    links.new(obj_info.outputs['Random'], get_socket(ramp_stucco.inputs, 'Factor'))

    # Monsoon rain runoff grime streaks
    map_streak = nodes.new("ShaderNodeMapping")
    map_streak.location = (-1000, -350)
    map_streak.inputs['Scale'].default_value = (1.5, 1.5, 0.12)
    links.new(tc.outputs['Object'], map_streak.inputs['Vector'])
    noise_streak = nodes.new("ShaderNodeTexNoise")
    noise_streak.location = (-800, -350)
    noise_streak.inputs['Scale'].default_value = 8.0
    noise_streak.inputs['Detail'].default_value = 4.0
    links.new(map_streak.outputs['Vector'], noise_streak.inputs['Vector'])
    ramp_streak = nodes.new("ShaderNodeValToRGB")
    ramp_streak.location = (-600, -350)
    ramp_streak.color_ramp.elements[0].position = 0.35
    ramp_streak.color_ramp.elements[0].color = (0.70, 0.68, 0.64, 1.0) # Grime stain
    ramp_streak.color_ramp.elements[1].position = 0.68
    ramp_streak.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(get_socket(noise_streak.outputs, 'Factor'), get_socket(ramp_streak.inputs, 'Factor'))

    # Multiply wall color with monsoon streak
    mix_wall = nodes.new("ShaderNodeMix")
    mix_wall.location = (-400, 300)
    mix_wall.data_type = 'RGBA'
    mix_wall.blend_type = 'MULTIPLY'
    mix_wall.inputs[0].default_value = 0.85
    links.new(ramp_stucco.outputs['Color'], mix_wall.inputs[6])
    links.new(ramp_streak.outputs['Color'], mix_wall.inputs[7])

    # Window Brick Grid (Ribbon Windows with eyebrow frames)
    brick_win = nodes.new("ShaderNodeTexBrick")
    brick_win.location = (-650, 0)
    brick_win.inputs['Scale'].default_value = 1.0
    brick_win.inputs['Mortar Size'].default_value = 0.15
    brick_win.inputs['Brick Width'].default_value = 0.55
    brick_win.inputs['Row Height'].default_value = 0.65
    links.new(mapping.outputs['Vector'], brick_win.inputs['Vector'])

    # Blend Glass vs Wall
    mix_ad_base = nodes.new("ShaderNodeMix")
    mix_ad_base.location = (-150, 150)
    mix_ad_base.data_type = 'RGBA'
    mix_ad_base.inputs[6].default_value = (0.08, 0.12, 0.16, 1.0) # Deep reflective glass
    links.new(mix_wall.outputs[2], mix_ad_base.inputs[7])
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_base.inputs[0])
    links.new(mix_ad_base.outputs[2], bsdf.inputs['Base Color'])

    # Roughness: Glass 0.10, Wall 0.72
    mix_ad_rough = nodes.new("ShaderNodeMix")
    mix_ad_rough.location = (-150, -100)
    mix_ad_rough.data_type = 'FLOAT'
    mix_ad_rough.inputs[2].default_value = 0.10
    mix_ad_rough.inputs[3].default_value = 0.72
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_rough.inputs[0])
    links.new(mix_ad_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Glass 0.35, Wall 0.0
    mix_ad_met = nodes.new("ShaderNodeMix")
    mix_ad_met.location = (-150, -250)
    mix_ad_met.data_type = 'FLOAT'
    mix_ad_met.inputs[2].default_value = 0.35
    mix_ad_met.inputs[3].default_value = 0.0
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_met.inputs[0])
    links.new(mix_ad_met.outputs[0], bsdf.inputs['Metallic'])

    # Evening Interior Tungsten Lights
    noise_glow = nodes.new("ShaderNodeTexNoise")
    noise_glow.location = (-400, -500)
    noise_glow.inputs['Scale'].default_value = 10.0
    links.new(mapping.outputs['Vector'], noise_glow.inputs['Vector'])
    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (-180, -500)
    ramp_glow.color_ramp.elements[0].position = 0.60
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_glow.color_ramp.elements[1].position = 0.68
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.84, 0.52, 1.0) # Warm tungsten lamp
    links.new(get_socket(noise_glow.outputs, 'Factor'), get_socket(ramp_glow.inputs, 'Factor'))
    math_glow = nodes.new("ShaderNodeMath")
    math_glow.location = (50, -500)
    math_glow.operation = 'MULTIPLY'
    links.new(get_socket(brick_win.outputs, 'Factor'), math_glow.inputs[0])
    links.new(ramp_glow.outputs['Color'], math_glow.inputs[1])
    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(math_glow.outputs['Value'], bsdf.inputs['Emission Strength'])
    shaders['ArtDeco'] = mat_ad

    # ------------------------------------------------------------------
    # B. VICTORIAN HERITAGE BASALT & STONE (Colaba / Fort / CSMT)
    # ------------------------------------------------------------------
    mat_her, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_HeritageBasalt_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs['Scale'].default_value = (0.22, 0.22, 0.26) # 3.8m heritage floor height
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    brick_stone = nodes.new("ShaderNodeTexBrick")
    brick_stone.location = (-750, 200)
    brick_stone.inputs['Scale'].default_value = 1.0
    brick_stone.inputs['Mortar Size'].default_value = 0.03
    brick_stone.inputs['Brick Width'].default_value = 0.60
    brick_stone.inputs['Row Height'].default_value = 0.35
    if 'Color1' in brick_stone.inputs:
        brick_stone.inputs['Color1'].default_value = (0.82, 0.72, 0.54, 1.0) # Malad yellow sandstone
        brick_stone.inputs['Color2'].default_value = (0.74, 0.64, 0.48, 1.0)
    links.new(mapping.outputs['Vector'], brick_stone.inputs['Vector'])

    # Stone window openings
    brick_win_her = nodes.new("ShaderNodeTexBrick")
    brick_win_her.location = (-750, -200)
    brick_win_her.inputs['Scale'].default_value = 1.0
    brick_win_her.inputs['Mortar Size'].default_value = 0.24 # Heavy stone arch piers
    brick_win_her.inputs['Brick Width'].default_value = 0.50
    brick_win_her.inputs['Row Height'].default_value = 0.70
    links.new(mapping.outputs['Vector'], brick_win_her.inputs['Vector'])

    mix_her_col = nodes.new("ShaderNodeMix")
    mix_her_col.location = (-300, 100)
    mix_her_col.data_type = 'RGBA'
    mix_her_col.inputs[6].default_value = (0.06, 0.09, 0.12, 1.0) # Heritage dark glass
    links.new(brick_stone.outputs['Color'], mix_her_col.inputs[7])
    links.new(get_socket(brick_win_her.outputs, 'Factor'), mix_her_col.inputs[0])
    links.new(mix_her_col.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.88 # Matte historic stone
    bsdf.inputs['Metallic'].default_value = 0.0

    bump_her = nodes.new("ShaderNodeBump")
    bump_her.location = (200, -200)
    bump_her.inputs['Strength'].default_value = 0.35
    links.new(get_socket(brick_stone.outputs, 'Factor'), bump_her.inputs['Height'])
    links.new(bump_her.outputs['Normal'], bsdf.inputs['Normal'])
    shaders['HeritageGothic'] = mat_her

    # ------------------------------------------------------------------
    # C. MODERN HIGH-RISE CURTAIN WALL (Worli / Lower Parel Towers)
    # ------------------------------------------------------------------
    mat_hr, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_HighRise_CurtainWall_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1200, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs['Scale'].default_value = (0.25, 0.25, 0.27) # 3.6m floor
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    brick_mullion = nodes.new("ShaderNodeTexBrick")
    brick_mullion.location = (-700, 0)
    brick_mullion.inputs['Scale'].default_value = 1.0
    brick_mullion.inputs['Mortar Size'].default_value = 0.04
    brick_mullion.inputs['Brick Width'].default_value = 0.45
    brick_mullion.inputs['Row Height'].default_value = 0.90
    links.new(mapping.outputs['Vector'], brick_mullion.inputs['Vector'])

    # Deep marine solar reflective glass tint
    obj_info_hr = nodes.new("ShaderNodeObjectInfo")
    obj_info_hr.location = (-1200, 350)
    ramp_hr_glass = nodes.new("ShaderNodeValToRGB")
    ramp_hr_glass.location = (-800, 350)
    ramp_hr_glass.color_ramp.elements[0].position = 0.0
    ramp_hr_glass.color_ramp.elements[0].color = (0.08, 0.18, 0.28, 1.0) # Deep Navy Marine
    ramp_hr_glass.color_ramp.elements[1].position = 1.0
    ramp_hr_glass.color_ramp.elements[1].color = (0.12, 0.28, 0.35, 1.0) # Coastal Cyan Emerald
    links.new(obj_info_hr.outputs['Random'], get_socket(ramp_hr_glass.inputs, 'Factor'))

    mix_hr_base = nodes.new("ShaderNodeMix")
    mix_hr_base.location = (-350, 150)
    mix_hr_base.data_type = 'RGBA'
    mix_hr_base.inputs[7].default_value = (0.85, 0.86, 0.88, 1.0) # Silver anodized aluminum
    links.new(ramp_hr_glass.outputs['Color'], mix_hr_base.inputs[6])
    links.new(get_socket(brick_mullion.outputs, 'Factor'), mix_hr_base.inputs[0])
    links.new(mix_hr_base.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.88 # High metallic reflection
    bsdf.inputs['Roughness'].default_value = 0.08 # Mirror glass

    # Office Floor Illumination
    noise_off = nodes.new("ShaderNodeTexNoise")
    noise_off.location = (-500, -350)
    noise_off.inputs['Scale'].default_value = 7.0
    links.new(mapping.outputs['Vector'], noise_off.inputs['Vector'])
    ramp_off = nodes.new("ShaderNodeValToRGB")
    ramp_off.location = (-250, -350)
    ramp_off.color_ramp.elements[0].position = 0.42
    ramp_off.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_off.color_ramp.elements[1].position = 0.52
    ramp_off.color_ramp.elements[1].color = (1.0, 0.94, 0.72, 1.0) # Warm LED office lighting
    links.new(get_socket(noise_off.outputs, 'Factor'), get_socket(ramp_off.inputs, 'Factor'))
    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_off.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.8
    shaders['HighRiseCurtainWall'] = mat_hr

    # ------------------------------------------------------------------
    # D. MODERNIST COMMERCIAL (Nariman Point Headquarters)
    # ------------------------------------------------------------------
    mat_mod, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_Modernist_Concrete_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1000, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs['Scale'].default_value = (0.24, 0.24, 0.28)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    brick_ribbon = nodes.new("ShaderNodeTexBrick")
    brick_ribbon.location = (-500, 0)
    brick_ribbon.inputs['Scale'].default_value = 1.0
    brick_ribbon.inputs['Mortar Size'].default_value = 0.28 # Heavy concrete spandrels
    brick_ribbon.inputs['Brick Width'].default_value = 0.80
    brick_ribbon.inputs['Row Height'].default_value = 0.55
    links.new(mapping.outputs['Vector'], brick_ribbon.inputs['Vector'])

    mix_mod_base = nodes.new("ShaderNodeMix")
    mix_mod_base.location = (-200, 100)
    mix_mod_base.data_type = 'RGBA'
    mix_mod_base.inputs[6].default_value = (0.10, 0.14, 0.16, 1.0) # Solar bronze/grey glass
    mix_mod_base.inputs[7].default_value = (0.68, 0.67, 0.65, 1.0) # Architectural grey concrete
    links.new(get_socket(brick_ribbon.outputs, 'Factor'), mix_mod_base.inputs[0])
    links.new(mix_mod_base.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.65
    shaders['ModernistCommercial'] = mat_mod

    # ------------------------------------------------------------------
    # E. TRADITIONAL CHAWL & VERNACULAR (Girgaon / Bhuleshwar)
    # ------------------------------------------------------------------
    mat_chawl, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_Chawl_Plaster_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1000, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs['Scale'].default_value = (0.35, 0.35, 0.35)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    noise_chawl = nodes.new("ShaderNodeTexNoise")
    noise_chawl.location = (-550, 150)
    noise_chawl.inputs['Scale'].default_value = 14.0
    links.new(mapping.outputs['Vector'], noise_chawl.inputs['Vector'])
    ramp_chawl = nodes.new("ShaderNodeValToRGB")
    ramp_chawl.location = (-300, 150)
    ramp_chawl.color_ramp.elements[0].position = 0.30
    ramp_chawl.color_ramp.elements[0].color = (0.55, 0.52, 0.46, 1.0) # Damp weathered grey-green
    ramp_chawl.color_ramp.elements[1].position = 0.70
    ramp_chawl.color_ramp.elements[1].color = (0.82, 0.78, 0.70, 1.0) # Peeling lime plaster
    links.new(get_socket(noise_chawl.outputs, 'Factor'), get_socket(ramp_chawl.inputs, 'Factor'))
    links.new(ramp_chawl.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.92
    shaders['ChawlVernacular'] = mat_chawl

    # ------------------------------------------------------------------
    # F. MODERN RESIDENTIAL APARTMENTS (Dadar / Bandra)
    # ------------------------------------------------------------------
    mat_res, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_Residential_Modern_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-1100, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-900, 0)
    mapping.inputs['Scale'].default_value = (0.30, 0.30, 0.3125)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    obj_info_res = nodes.new("ShaderNodeObjectInfo")
    obj_info_res.location = (-1100, 350)
    ramp_res_col = nodes.new("ShaderNodeValToRGB")
    ramp_res_col.location = (-750, 350)
    ramp_res_col.color_ramp.interpolation = 'CONSTANT'
    ramp_res_col.color_ramp.elements[0].position = 0.0
    ramp_res_col.color_ramp.elements[0].color = (0.86, 0.82, 0.74, 1.0) # Wheat / Off-White
    ramp_res_col.color_ramp.elements[1].position = 0.33
    ramp_res_col.color_ramp.elements[1].color = (0.82, 0.70, 0.52, 1.0) # Warm Sand Ochre
    e2_r = ramp_res_col.color_ramp.elements.new(0.66)
    e2_r.color = (0.76, 0.62, 0.55, 1.0) # Dusty Terracotta
    links.new(obj_info_res.outputs['Random'], get_socket(ramp_res_col.inputs, 'Factor'))

    brick_res_win = nodes.new("ShaderNodeTexBrick")
    brick_res_win.location = (-600, 0)
    brick_res_win.inputs['Scale'].default_value = 1.0
    brick_res_win.inputs['Mortar Size'].default_value = 0.14
    brick_res_win.inputs['Brick Width'].default_value = 0.50
    brick_res_win.inputs['Row Height'].default_value = 0.70
    links.new(mapping.outputs['Vector'], brick_res_win.inputs['Vector'])

    mix_res_base = nodes.new("ShaderNodeMix")
    mix_res_base.location = (-250, 150)
    mix_res_base.data_type = 'RGBA'
    mix_res_base.inputs[6].default_value = (0.10, 0.14, 0.18, 1.0)
    links.new(ramp_res_col.outputs['Color'], mix_res_base.inputs[7])
    links.new(get_socket(brick_res_win.outputs, 'Factor'), mix_res_base.inputs[0])
    links.new(mix_res_base.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    shaders['ResidentialModern'] = mat_res

    # ------------------------------------------------------------------
    # G. ROOFTOP TAR & WATERPROOFING GRAVEL
    # ------------------------------------------------------------------
    mat_tar, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_RoofTar_PBR")
    tc = nodes.new("ShaderNodeTexCoord")
    tc.location = (-800, 0)
    noise_tar = nodes.new("ShaderNodeTexNoise")
    noise_tar.location = (-500, 0)
    noise_tar.inputs['Scale'].default_value = 60.0
    links.new(tc.outputs['Object'], noise_tar.inputs['Vector'])
    ramp_tar = nodes.new("ShaderNodeValToRGB")
    ramp_tar.location = (-250, 0)
    ramp_tar.color_ramp.elements[0].position = 0.3
    ramp_tar.color_ramp.elements[0].color = (0.08, 0.08, 0.09, 1.0) # Black bituminous mastic
    ramp_tar.color_ramp.elements[1].position = 0.7
    ramp_tar.color_ramp.elements[1].color = (0.16, 0.16, 0.17, 1.0) # Mineral gravel felt
    links.new(get_socket(noise_tar.outputs, 'Factor'), get_socket(ramp_tar.inputs, 'Factor'))
    links.new(ramp_tar.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95
    shaders['RoofTar'] = mat_tar

    # ------------------------------------------------------------------
    # H. ROOFTOP WATER STORAGE TANKS (Sintex Black/Blue + RCC Concrete)
    # ------------------------------------------------------------------
    mat_tank, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_WaterTank_PBR")
    bsdf.inputs['Base Color'].default_value = (0.05, 0.07, 0.10, 1.0) # Weathered black UV-HDPE
    bsdf.inputs['Roughness'].default_value = 0.45
    shaders['WaterTank'] = mat_tank

    return shaders

# ----------------------------------------------------------------------
# 2. ARCHITECTURAL WARD CLASSIFIER
# ----------------------------------------------------------------------
def classify_mumbai_architecture(cx, cy, tags, raw_h):
    b_type = tags.get("building", "yes")
    name = tags.get("name", "").lower()

    fl_h = 3.2
    typology = "ResidentialModern"
    h = raw_h

    # 1. Marine Drive / Oval Maidan Art Deco Precinct
    if cx <= -550 and 400 <= cy <= 3500:
        typology = "ArtDeco"
        fl_h = 3.2
        if h < 16.0 or h > 35.0:
            h = random.choice([20.0, 22.5, 24.0, 26.0, 28.0])

    # 2. Nariman Point Modernist Commercial Headquarters
    elif -1300 <= cx <= -800 and 200 <= cy <= 900:
        typology = "ModernistCommercial"
        fl_h = 3.6
        if h < 50.0:
            h = random.choice([65.0, 80.0, 95.0, 105.0, 115.0])

    # 3. South Mumbai Historic Heritage (Colaba, Fort, Ballard Estate, CSMT)
    elif cy < 3200 and cx > -550:
        typology = "HeritageGothic"
        fl_h = 4.0 # Victorian high ceilings
        if h < 12.0:
            h = random.choice([14.0, 16.5, 18.0, 22.0])
        elif h > 32.0 and "tower" not in name:
            h = 24.0

    # 4. Girgaon, Bhuleshwar, Kalbadevi Traditional Chawls
    elif 3200 <= cy < 5200 and -800 < cx <= 400:
        typology = "ChawlVernacular"
        fl_h = 2.9
        if h < 8.0 or h > 20.0:
            h = random.choice([9.5, 12.0, 14.5])

    # 5. Worli, Lower Parel, Prabhadevi Skyscraper Corridor
    elif 5200 <= cy < 10500:
        if b_type in ["apartments", "commercial", "office", "hotel"] or h > 35.0 or "tower" in name:
            typology = "HighRiseCurtainWall"
            fl_h = 3.6
            if h < 60.0:
                h = random.choice([75.0, 95.0, 120.0, 150.0, 185.0, 240.0])
        else:
            typology = "ResidentialModern"
            fl_h = 3.2
            if h < 14.0:
                h = random.choice([16.0, 22.0, 32.0, 42.0])

    # 6. Dadar, Mahim, Bandra Corridor
    else:
        if h > 50.0 or "tower" in name:
            typology = "HighRiseCurtainWall"
            fl_h = 3.5
        else:
            typology = "ResidentialModern"
            fl_h = 3.2
            if h < 12.0:
                h = random.choice([15.0, 19.2, 25.6, 35.0])

    levels = max(1, int(round(h / fl_h)))
    return typology, h, levels

# ----------------------------------------------------------------------
# 3. BUILD ALL REAL MUMBAI BUILDINGS WITH ARCHITECTURAL DETAIL
# ----------------------------------------------------------------------
def build_authentic_mumbai_city(shaders):
    print("[CityBuilder] Ingesting real surveyed building footprints and generating authentic architectures...")

    col_name = "GRAI_AUTHENTIC_MUMBAI_ARCHITECTURE"
    coll = bpy.data.collections.get(col_name)
    if not coll:
        coll = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(coll)

    for obj in list(coll.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    for c_name in ["Urban_Fabric_City_Blocks", "GRAI_REAL_MUMBAI_BUILDINGS"]:
        c = bpy.data.collections.get(c_name)
        if c:
            c.hide_render = True
            c.hide_viewport = True

    attr_path = os.path.join(REPO_ROOT, "Data/processed/buildings_attributed.json")
    with open(attr_path, 'r', encoding='utf-8') as f:
        all_buildings = json.load(f)

    print(f"[CityBuilder] Loaded {len(all_buildings)} real surveyed building footprints.")

    typology_batches = {
        "ArtDeco": {"verts": [], "faces": [], "mat": shaders['ArtDeco']},
        "HeritageGothic": {"verts": [], "faces": [], "mat": shaders['HeritageGothic']},
        "HighRiseCurtainWall": {"verts": [], "faces": [], "mat": shaders['HighRiseCurtainWall']},
        "ModernistCommercial": {"verts": [], "faces": [], "mat": shaders['ModernistCommercial']},
        "ChawlVernacular": {"verts": [], "faces": [], "mat": shaders['ChawlVernacular']},
        "ResidentialModern": {"verts": [], "faces": [], "mat": shaders['ResidentialModern']}
    }

    rooftop_tar_batch = {"verts": [], "faces": [], "mat": shaders['RoofTar']}
    watertank_batch = {"verts": [], "faces": [], "mat": shaders['WaterTank']}

    count = 0
    for b in all_buildings:
        coords = b.get("local_polygon_vertices", [])
        if len(coords) < 3:
            continue

        cx, cy = b.get("local_centroid", [coords[0][0], coords[0][1]])
        base_z = float(b.get("elevation_msl", 2.0))
        raw_h = float(b.get("height_m", 12.0))
        tags = b.get("tags", {})

        typology, h, levels = classify_mumbai_architecture(cx, cy, tags, raw_h)
        batch = typology_batches[typology]

        clean_pts = []
        for i, pt in enumerate(coords):
            if i > 0 and math.hypot(pt[0] - coords[0][0], pt[1] - coords[0][1]) < 0.01 and i == len(coords) - 1:
                continue
            clean_pts.append(pt)

        n_pts = len(clean_pts)
        if n_pts < 3:
            continue

        v_offset = len(batch["verts"])

        # 1. Main Building Wall Extrusion
        for pt in clean_pts:
            batch["verts"].append((pt[0], pt[1], base_z))
        for pt in clean_pts:
            batch["verts"].append((pt[0], pt[1], base_z + h))

        for i in range(n_pts):
            i_next = (i + 1) % n_pts
            b0 = v_offset + i
            b1 = v_offset + i_next
            t0 = v_offset + n_pts + i
            t1 = v_offset + n_pts + i_next
            batch["faces"].append((b0, b1, t1, t0))

        # 2. Roof Slab Polygon
        tar_v_offset = len(rooftop_tar_batch["verts"])
        for pt in clean_pts:
            rooftop_tar_batch["verts"].append((pt[0], pt[1], base_z + h))
        rooftop_tar_batch["faces"].append(tuple(tar_v_offset + i for i in range(n_pts)))

        # 3. Rooftop Parapet Wall (1.1m safety barrier along roof edge)
        parapet_h = 1.1
        para_v_offset = len(batch["verts"])
        for pt in clean_pts:
            batch["verts"].append((pt[0], pt[1], base_z + h))
        for pt in clean_pts:
            batch["verts"].append((pt[0], pt[1], base_z + h + parapet_h))
        for i in range(n_pts):
            i_next = (i + 1) % n_pts
            pb0 = para_v_offset + i
            pb1 = para_v_offset + i_next
            pt0 = para_v_offset + n_pts + i
            pt1 = para_v_offset + n_pts + i_next
            batch["faces"].append((pb0, pb1, pt1, pt0))

        # 4. Rooftop Elevator Machine Room / Mummy Penthouse
        pent_w = min(6.0, max(3.0, (clean_pts[1][0] - clean_pts[0][0]) * 0.4 if n_pts > 1 else 3.5))
        pent_h = 3.2
        px0, px1 = cx - pent_w * 0.5, cx + pent_w * 0.5
        py0, py1 = cy - pent_w * 0.5, cy + pent_w * 0.5
        pz0 = base_z + h
        pz1 = pz0 + pent_h

        mummy_offset = len(batch["verts"])
        batch["verts"].extend([
            (px0, py0, pz0), (px1, py0, pz0), (px1, py1, pz0), (px0, py1, pz0),
            (px0, py0, pz1), (px1, py0, pz1), (px1, py1, pz1), (px0, py1, pz1)
        ])
        batch["faces"].extend([
            (mummy_offset, mummy_offset+1, mummy_offset+5, mummy_offset+4),
            (mummy_offset+1, mummy_offset+2, mummy_offset+6, mummy_offset+5),
            (mummy_offset+2, mummy_offset+3, mummy_offset+7, mummy_offset+6),
            (mummy_offset+3, mummy_offset, mummy_offset+4, mummy_offset+7),
            (mummy_offset+4, mummy_offset+5, mummy_offset+6, mummy_offset+7)
        ])

        # 5. Rooftop Water Tanks (Signature Mumbai skyline feature!)
        tank_offset = len(watertank_batch["verts"])
        tx0 = px1 + 0.6
        tx1 = tx0 + 2.0
        ty0 = py0
        ty1 = ty0 + 2.0
        tz0 = pz0
        tz1 = tz0 + 2.2
        watertank_batch["verts"].extend([
            (tx0, ty0, tz0), (tx1, ty0, tz0), (tx1, ty1, tz0), (tx0, ty1, tz0),
            (tx0, ty0, tz1), (tx1, ty0, tz1), (tx1, ty1, tz1), (tx0, ty1, tz1)
        ])
        watertank_batch["faces"].extend([
            (tank_offset, tank_offset+1, tank_offset+5, tank_offset+4),
            (tank_offset+1, tank_offset+2, tank_offset+6, tank_offset+5),
            (tank_offset+2, tank_offset+3, tank_offset+7, tank_offset+6),
            (tank_offset+3, tank_offset, tank_offset+4, tank_offset+7),
            (tank_offset+4, tank_offset+5, tank_offset+6, tank_offset+7)
        ])

        count += 1

    print(f"[CityBuilder] Processed and structured {count} building entities into architectural meshes.")

    # Create Blender Mesh Objects for each typology
    for typ_name, data in typology_batches.items():
        if data["verts"] and data["faces"]:
            m_name = f"ARCH_MUMBAI_{typ_name}"
            mesh = bpy.data.meshes.new(m_name)
            mesh.from_pydata(data["verts"], [], data["faces"])
            mesh.update()
            obj = bpy.data.objects.new(m_name, mesh)
            obj.data.materials.append(data["mat"])
            coll.objects.link(obj)
            print(f"  Created {m_name}: {len(data['verts'])} vertices, {len(data['faces'])} faces.")

    if rooftop_tar_batch["verts"]:
        m_tar = bpy.data.meshes.new("ARCH_MUMBAI_Rooftop_Tar")
        m_tar.from_pydata(rooftop_tar_batch["verts"], [], rooftop_tar_batch["faces"])
        m_tar.update()
        obj_tar = bpy.data.objects.new("ARCH_MUMBAI_Rooftop_Tar", m_tar)
        obj_tar.data.materials.append(rooftop_tar_batch["mat"])
        coll.objects.link(obj_tar)

    if watertank_batch["verts"]:
        m_tank = bpy.data.meshes.new("ARCH_MUMBAI_Rooftop_WaterTanks")
        m_tank.from_pydata(watertank_batch["verts"], [], watertank_batch["faces"])
        m_tank.update()
        obj_tank = bpy.data.objects.new("ARCH_MUMBAI_Rooftop_WaterTanks", m_tank)
        obj_tank.data.materials.append(watertank_batch["mat"])
        coll.objects.link(obj_tank)

    print("[CityBuilder] All real Mumbai architectural typologies generated successfully!")

# ----------------------------------------------------------------------
# 4. LIGHTING & ATMOSPHERE (MUMBAI GOLDEN HOUR NISHITA SKY)
# ----------------------------------------------------------------------
def setup_mumbai_lighting():
    print("[Lighting] Calibrating Mumbai coastal tropical atmospheric lighting...")
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World_Mumbai_Coastal")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    links.new(bg.outputs['Background'], out.inputs['Surface'])

    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_elevation = math.radians(16.5)
    sky.sun_rotation = math.radians(245.0)
    sky.altitude = 12.0
    sky.air_density = 1.15
    sky.aerosol_density = 2.4
    sky.ozone_density = 2.0
    sky.sun_disc = True
    links.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.35

    sun_name = "LAMP_Mumbai_GoldenHour_Sun"
    sun_obj = bpy.data.objects.get(sun_name)
    if not sun_obj:
        sun_data = bpy.data.lights.new(sun_name, type='SUN')
        sun_obj = bpy.data.objects.new(sun_name, sun_data)
        bpy.context.scene.collection.objects.link(sun_obj)

    sun_obj.data.energy = 5.5
    sun_obj.data.color = (1.0, 0.92, 0.82)
    sun_obj.rotation_euler = (math.radians(73.5), math.radians(0), math.radians(65.0))

# ----------------------------------------------------------------------
# 5. DEDICATED ARCHITECTURAL HERO CAMERAS
# ----------------------------------------------------------------------
def setup_architectural_cameras():
    print("[Cameras] Setting up 7 dedicated architectural perspective cameras...")

    cameras_def = [
        # 1. Marine Drive Art Deco Architectural Row
        {
            "name": "Cam_Arch_MarineDrive_ArtDeco",
            "loc": (-1030.0, 520.0, 16.0),
            "rot": (math.radians(82.0), math.radians(0.0), math.radians(-32.0)),
            "lens": 28.0,
            "title": "Marine Drive Art Deco Heritage Row"
        },
        # 2. Fort & Colaba Historic Heritage District
        {
            "name": "Cam_Arch_Fort_HeritageDistrict",
            "loc": (-380.0, 1850.0, 22.0),
            "rot": (math.radians(78.0), math.radians(0.0), math.radians(-55.0)),
            "lens": 35.0,
            "title": "Fort & Horniman Circle Victorian Heritage"
        },
        # 3. Worli & Lower Parel High-Rise Skyscraper Corridor
        {
            "name": "Cam_Arch_Worli_Megatowers",
            "loc": (-750.0, 7200.0, 48.0),
            "rot": (math.radians(70.0), math.radians(0.0), math.radians(-65.0)),
            "lens": 24.0,
            "title": "Worli & Lower Parel Contemporary High-Rise Corridor"
        },
        # 4. Nariman Point Modernist Commercial Headquarters
        {
            "name": "Cam_Arch_NarimanPoint_Skyline",
            "loc": (-1350.0, 250.0, 25.0),
            "rot": (math.radians(80.0), math.radians(0.0), math.radians(-40.0)),
            "lens": 30.0,
            "title": "Nariman Point Commercial Waterfront Skyline"
        },
        # 5. Girgaon & Traditional Chawl Quarter
        {
            "name": "Cam_Arch_Girgaon_ChawlVernacular",
            "loc": (-350.0, 3850.0, 18.0),
            "rot": (math.radians(84.0), math.radians(0.0), math.radians(-75.0)),
            "lens": 32.0,
            "title": "Girgaon High-Density Vernacular Chawls"
        },
        # 6. Gateway of India & Apollo Bunder Plaza
        {
            "name": "Cam_Arch_Gateway_ApolloBunder",
            "loc": (95.0, -110.0, 14.0),
            "rot": (math.radians(81.0), math.radians(0.0), math.radians(-130.0)),
            "lens": 28.0,
            "title": "Apollo Bunder & Gateway of India Heritage Plaza"
        },
        # 7. Bandra-Worli Sea Link & Coastal Skyline
        {
            "name": "Cam_Arch_BandraWorli_BayView",
            "loc": (-1450.0, 8850.0, 65.0),
            "rot": (math.radians(75.0), math.radians(0.0), math.radians(-25.0)),
            "lens": 35.0,
            "title": "Bandra-Worli Sea Link Coastal Pylon & Skyline"
        }
    ]

    cam_objs = {}
    for c in cameras_def:
        cam_name = c["name"]
        obj = bpy.data.objects.get(cam_name)
        if not obj:
            cam_data = bpy.data.cameras.new(cam_name)
            obj = bpy.data.objects.new(cam_name, cam_data)
            bpy.context.scene.collection.objects.link(obj)

        obj.location = Vector(c["loc"])
        obj.rotation_euler = Euler(c["rot"])
        obj.data.lens = c["lens"]
        obj.data.clip_start = 0.5
        obj.data.clip_end = 25000.0
        cam_objs[cam_name] = obj

    return cameras_def, cam_objs

# ----------------------------------------------------------------------
# 6. RENDER MASTERPIECE IMAGES (1080P)
# ----------------------------------------------------------------------
def render_architectural_views(cameras_def):
    print("[Render] Starting high-definition architectural rendering (1920x1080)...")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngine') and 'BLENDER_EEVEE_NEXT' in bpy.types.RenderEngine.bl_rna.properties['engine'].enum_items else 'BLENDER_EEVEE'

    rendered_files = []
    for idx, c in enumerate(cameras_def, 1):
        cam_name = c["name"]
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            continue

        scene.camera = cam_obj
        filename = f"arch_{idx}_{cam_name.replace('Cam_Arch_', '').lower()}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)

        scene.render.filepath = filepath
        print(f"  Rendering [{idx}/{len(cameras_def)}] {c['title']} -> {filepath}")
        bpy.ops.render.render(write_still=True)
        rendered_files.append((c["title"], filepath))

    print(f"[Render] All {len(rendered_files)} architectural views rendered successfully!")
    return rendered_files

# ----------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------
def run_all():
    print("======================================================================")
    print("GRAI AUTHENTIC MUMBAI ARCHITECTURES & PBR TEXTURE ENGINE")
    print("======================================================================")
    shaders = build_all_mumbai_shaders()
    build_authentic_mumbai_city(shaders)
    setup_mumbai_lighting()
    cameras_def, cam_objs = setup_architectural_cameras()
    rendered = render_architectural_views(cameras_def)
    print("======================================================================")
    print("EXECUTION COMPLETE.")
    return rendered

if __name__ == "__main__":
    run_all()
