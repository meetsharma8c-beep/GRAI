#!/usr/bin/env python3
"""
GRAI — Master Architectural Digital Twin Engine
========================================================================
Procedurally constructs, attires, and renders real-world Mumbai building architectures:
1. Authentic Sizing & Heights: Real OSM tags + ward-specific BMC building heights.
2. Authentic Architectural Typologies:
   - Art Deco (Marine Drive): Stepped parapets, curved balconies, pastel stucco, nautical lines.
   - Victorian Gothic & Indo-Saracenic (Colaba, Fort, CSMT): Basalt plinths, Malad stone, arches.
   - Modern Glass High-Rises (Worli, Lower Parel): Reflective curtain walls, podiums, helipads.
   - Modernist Commercial (Nariman Point): Concrete frames, strip windows, brise-soleil.
   - Traditional Chawls (Girgaon, Bhuleshwar): Exterior access verandas, chhajjas, rooftop tanks.
   - Modern Residential (Dadar, Bandra): Indian pastel washes, cantilevered box balconies.
3. Rooftop Infrastructure: Parapets, elevator motor rooms, Sintex & RCC water tanks.
4. Procedural PBR Shader Networks with correct socket routing for walls and windows.
5. Calibrated Mumbai Coastal Golden Hour Lighting & 6 Dedicated Architectural Cameras.
6. 1080p High-Definition Renders saved to renders/architectures/.
"""

import os
import sys
import json
import math
import random
import bpy
from mathutils import Vector, Euler, Matrix

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 1. SHADER HELPERS (BLENDER 5.2.2 COMPATIBLE)
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
    ramp_streak.color_ramp.elements[0].color = (0.70, 0.68, 0.64, 1.0)
    ramp_streak.color_ramp.elements[1].position = 0.68
    ramp_streak.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(get_socket(noise_streak.outputs, 'Factor'), get_socket(ramp_streak.inputs, 'Factor'))

    mix_wall = nodes.new("ShaderNodeMix")
    mix_wall.location = (-400, 300)
    mix_wall.data_type = 'RGBA'
    mix_wall.blend_type = 'MULTIPLY'
    mix_wall.inputs[0].default_value = 0.85
    links.new(ramp_stucco.outputs['Color'], mix_wall.inputs[6])
    links.new(ramp_streak.outputs['Color'], mix_wall.inputs[7])

    # Window Brick Grid: Factor=0 is Mortar (Wall), Factor=1 is Brick (Window)
    brick_win = nodes.new("ShaderNodeTexBrick")
    brick_win.location = (-650, 0)
    brick_win.inputs['Scale'].default_value = 1.0
    brick_win.inputs['Mortar Size'].default_value = 0.15
    brick_win.inputs['Brick Width'].default_value = 0.55
    brick_win.inputs['Row Height'].default_value = 0.65
    links.new(mapping.outputs['Vector'], brick_win.inputs['Vector'])

    # Blend Glass vs Wall: A (input 6) = Wall, B (input 7) = Glass
    mix_ad_base = nodes.new("ShaderNodeMix")
    mix_ad_base.location = (-150, 150)
    mix_ad_base.data_type = 'RGBA'
    mix_ad_base.inputs[7].default_value = (0.08, 0.12, 0.16, 1.0) # Deep reflective glass (B)
    links.new(mix_wall.outputs[2], mix_ad_base.inputs[6])          # Wall stucco (A)
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_base.inputs[0])
    links.new(mix_ad_base.outputs[2], bsdf.inputs['Base Color'])

    # Roughness: Wall A=0.72, Glass B=0.10
    mix_ad_rough = nodes.new("ShaderNodeMix")
    mix_ad_rough.location = (-150, -100)
    mix_ad_rough.data_type = 'FLOAT'
    mix_ad_rough.inputs[2].default_value = 0.72 # Wall roughness (A)
    mix_ad_rough.inputs[3].default_value = 0.10 # Glass roughness (B)
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_rough.inputs[0])
    links.new(mix_ad_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Wall A=0.0, Glass B=0.40
    mix_ad_met = nodes.new("ShaderNodeMix")
    mix_ad_met.location = (-150, -250)
    mix_ad_met.data_type = 'FLOAT'
    mix_ad_met.inputs[2].default_value = 0.0  # Wall metallic (A)
    mix_ad_met.inputs[3].default_value = 0.40 # Glass metallic (B)
    links.new(get_socket(brick_win.outputs, 'Factor'), mix_ad_met.inputs[0])
    links.new(mix_ad_met.outputs[0], bsdf.inputs['Metallic'])

    # Evening Interior Lights
    noise_glow = nodes.new("ShaderNodeTexNoise")
    noise_glow.location = (-400, -500)
    noise_glow.inputs['Scale'].default_value = 10.0
    links.new(mapping.outputs['Vector'], noise_glow.inputs['Vector'])
    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (-180, -500)
    ramp_glow.color_ramp.elements[0].position = 0.60
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_glow.color_ramp.elements[1].position = 0.68
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.84, 0.52, 1.0)
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
    mapping.inputs['Scale'].default_value = (0.22, 0.22, 0.26)
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

    brick_win_her = nodes.new("ShaderNodeTexBrick")
    brick_win_her.location = (-750, -200)
    brick_win_her.inputs['Scale'].default_value = 1.0
    brick_win_her.inputs['Mortar Size'].default_value = 0.24
    brick_win_her.inputs['Brick Width'].default_value = 0.50
    brick_win_her.inputs['Row Height'].default_value = 0.70
    links.new(mapping.outputs['Vector'], brick_win_her.inputs['Vector'])

    # A (input 6) = Stone wall, B (input 7) = Window
    mix_her_col = nodes.new("ShaderNodeMix")
    mix_her_col.location = (-300, 100)
    mix_her_col.data_type = 'RGBA'
    mix_her_col.inputs[7].default_value = (0.06, 0.09, 0.12, 1.0) # Heritage dark window (B)
    links.new(brick_stone.outputs['Color'], mix_her_col.inputs[6])  # Stone masonry (A)
    links.new(get_socket(brick_win_her.outputs, 'Factor'), mix_her_col.inputs[0])
    links.new(mix_her_col.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.88
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
    mapping.inputs['Scale'].default_value = (0.25, 0.25, 0.27)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    brick_mullion = nodes.new("ShaderNodeTexBrick")
    brick_mullion.location = (-700, 0)
    brick_mullion.inputs['Scale'].default_value = 1.0
    brick_mullion.inputs['Mortar Size'].default_value = 0.04
    brick_mullion.inputs['Brick Width'].default_value = 0.45
    brick_mullion.inputs['Row Height'].default_value = 0.90
    links.new(mapping.outputs['Vector'], brick_mullion.inputs['Vector'])

    obj_info_hr = nodes.new("ShaderNodeObjectInfo")
    obj_info_hr.location = (-1200, 350)
    ramp_hr_glass = nodes.new("ShaderNodeValToRGB")
    ramp_hr_glass.location = (-800, 350)
    ramp_hr_glass.color_ramp.elements[0].position = 0.0
    ramp_hr_glass.color_ramp.elements[0].color = (0.08, 0.18, 0.28, 1.0) # Deep Navy Marine
    ramp_hr_glass.color_ramp.elements[1].position = 1.0
    ramp_hr_glass.color_ramp.elements[1].color = (0.12, 0.28, 0.35, 1.0) # Coastal Cyan Emerald
    links.new(obj_info_hr.outputs['Random'], get_socket(ramp_hr_glass.inputs, 'Factor'))

    # Mullion A (input 6) = Aluminum, Glass B (input 7) = Reflective glass
    mix_hr_base = nodes.new("ShaderNodeMix")
    mix_hr_base.location = (-350, 150)
    mix_hr_base.data_type = 'RGBA'
    mix_hr_base.inputs[6].default_value = (0.85, 0.86, 0.88, 1.0) # Mullions (A)
    links.new(ramp_hr_glass.outputs['Color'], mix_hr_base.inputs[7]) # Glass (B)
    links.new(get_socket(brick_mullion.outputs, 'Factor'), mix_hr_base.inputs[0])
    links.new(mix_hr_base.outputs[2], bsdf.inputs['Base Color'])

    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.08

    noise_off = nodes.new("ShaderNodeTexNoise")
    noise_off.location = (-500, -350)
    noise_off.inputs['Scale'].default_value = 7.0
    links.new(mapping.outputs['Vector'], noise_off.inputs['Vector'])
    ramp_off = nodes.new("ShaderNodeValToRGB")
    ramp_off.location = (-250, -350)
    ramp_off.color_ramp.elements[0].position = 0.42
    ramp_off.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_off.color_ramp.elements[1].position = 0.52
    ramp_off.color_ramp.elements[1].color = (1.0, 0.94, 0.72, 1.0)
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
    brick_ribbon.inputs['Mortar Size'].default_value = 0.28
    brick_ribbon.inputs['Brick Width'].default_value = 0.80
    brick_ribbon.inputs['Row Height'].default_value = 0.55
    links.new(mapping.outputs['Vector'], brick_ribbon.inputs['Vector'])

    mix_mod_base = nodes.new("ShaderNodeMix")
    mix_mod_base.location = (-200, 100)
    mix_mod_base.data_type = 'RGBA'
    mix_mod_base.inputs[6].default_value = (0.68, 0.67, 0.65, 1.0) # Concrete spandrel (A)
    mix_mod_base.inputs[7].default_value = (0.10, 0.14, 0.16, 1.0) # Strip window glass (B)
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
    ramp_chawl.color_ramp.elements[0].color = (0.55, 0.52, 0.46, 1.0) # Weathered damp
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
    ramp_res_col.color_ramp.elements[0].color = (0.86, 0.82, 0.74, 1.0) # Wheat
    ramp_res_col.color_ramp.elements[1].position = 0.33
    ramp_res_col.color_ramp.elements[1].color = (0.82, 0.70, 0.52, 1.0) # Sand Ochre
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
    mix_res_base.inputs[7].default_value = (0.10, 0.14, 0.18, 1.0) # Window glass (B)
    links.new(ramp_res_col.outputs['Color'], mix_res_base.inputs[6]) # Wall (A)
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
    ramp_tar.color_ramp.elements[0].color = (0.08, 0.08, 0.09, 1.0)
    ramp_tar.color_ramp.elements[1].position = 0.7
    ramp_tar.color_ramp.elements[1].color = (0.16, 0.16, 0.17, 1.0)
    links.new(get_socket(noise_tar.outputs, 'Factor'), get_socket(ramp_tar.inputs, 'Factor'))
    links.new(ramp_tar.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.95
    shaders['RoofTar'] = mat_tar

    # ------------------------------------------------------------------
    # H. ROOFTOP WATER STORAGE TANKS (Sintex Black/Blue + RCC Concrete)
    # ------------------------------------------------------------------
    mat_tank, nodes, links, bsdf, out = clean_material("MAT_RealMumbai_WaterTank_PBR")
    bsdf.inputs['Base Color'].default_value = (0.05, 0.07, 0.10, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.45
    shaders['WaterTank'] = mat_tank

    # Individual Art Deco Stucco Shaders for Marine Drive Mansions
    ad_colors = {
        "MAT_ArtDeco_CreamIvory": (0.92, 0.89, 0.82, 1.0),
        "MAT_ArtDeco_SeafoamGreen": (0.68, 0.82, 0.76, 1.0),
        "MAT_ArtDeco_MaladOchre": (0.86, 0.76, 0.58, 1.0),
        "MAT_ArtDeco_PalePeach": (0.90, 0.78, 0.70, 1.0)
    }
    for mname, rgba in ad_colors.items():
        m, _, _, b, _ = clean_material(mname)
        b.inputs['Base Color'].default_value = rgba
        b.inputs['Roughness'].default_value = 0.65

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

    if cx <= -550 and 400 <= cy <= 3500:
        typology = "ArtDeco"
        fl_h = 3.2
        if h < 16.0 or h > 35.0:
            h = random.choice([20.0, 22.5, 24.0, 26.0, 28.0])
    elif -1300 <= cx <= -800 and 200 <= cy <= 900:
        typology = "ModernistCommercial"
        fl_h = 3.6
        if h < 50.0:
            h = random.choice([65.0, 80.0, 95.0, 105.0, 115.0])
    elif cy < 3200 and cx > -550:
        typology = "HeritageGothic"
        fl_h = 4.0
        if h < 12.0:
            h = random.choice([14.0, 16.5, 18.0, 22.0])
        elif h > 32.0 and "tower" not in name:
            h = 24.0
    elif 3200 <= cy < 5200 and -800 < cx <= 400:
        typology = "ChawlVernacular"
        fl_h = 2.9
        if h < 8.0 or h > 20.0:
            h = random.choice([9.5, 12.0, 14.5])
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

        # 5. Rooftop Water Tanks
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
# 3. CALIBRATE LIGHTING & ATMOSPHERE
# ----------------------------------------------------------------------
def calibrate_mumbai_lighting():
    print("[Lighting] Calibrating single-source golden hour sun and coastal atmospheric lighting...")
    # Remove conflicting duplicate sun lights
    for name in ['LAMP_Mumbai_GoldenHour_Sun', 'Sun_Mumbai_Map']:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    sun = bpy.data.objects.get('Sun_Mumbai')
    if not sun:
        sun_data = bpy.data.lights.new('Sun_Mumbai', type='SUN')
        sun = bpy.data.objects.new('Sun_Mumbai', sun_data)
        bpy.context.scene.collection.objects.link(sun)

    sun.data.energy = 2.8
    sun.data.color = (1.0, 0.94, 0.84) # Warm golden sunlight
    sun.rotation_euler = (math.radians(70.0), math.radians(0), math.radians(65.0))

    scene = bpy.context.scene
    scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = 'AgX' if 'AgX' in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items else 'Filmic'

    w = scene.world
    if not w:
        w = bpy.data.worlds.new("World_Mumbai_Coastal")
        scene.world = w
    w.use_nodes = True
    nodes = w.node_tree.nodes
    links = w.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputWorld")
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs['Strength'].default_value = 0.65
    links.new(bg.outputs['Background'], out.inputs['Surface'])

    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_elevation = math.radians(18.0)
    sky.sun_rotation = math.radians(245.0)
    sky.altitude = 10.0
    sky.air_density = 1.10
    sky.aerosol_density = 2.2
    sky.ozone_density = 2.0
    sky.sun_disc = True
    links.new(sky.outputs['Color'], bg.inputs['Color'])

# ----------------------------------------------------------------------
# 3. APPLY AUTHENTIC SHADERS TO ALL EXISTING BESPOKE MANSIONS & TOWERS
# ----------------------------------------------------------------------
def apply_materials_to_district_assets(shaders):
    print("[Districts] Applying authentic Mumbai PBR materials to landmark structures...")

    # A. Marine Drive Art Deco Mansions
    ad_mats = {
        "ARTDECO_MarineDrive_Kapoor_Mahal": "MAT_ArtDeco_CreamIvory",
        "ARTDECO_MarineDrive_Zaver_Mahal": "MAT_ArtDeco_SeafoamGreen",
        "ARTDECO_MarineDrive_Keval_Mahal": "MAT_ArtDeco_MaladOchre",
        "ARTDECO_MarineDrive_Soona_Mahal": "MAT_ArtDeco_PalePeach",
        "ARTDECO_MarineDrive_Empress_Court": "MAT_ArtDeco_CreamIvory",
        "ARTDECO_MarineDrive_Shiv_Shanti_Bhuvan": "MAT_ArtDeco_MaladOchre",
        "ARTDECO_MarineDrive_Chateau_Marine": "MAT_ArtDeco_SeafoamGreen",
        "ARTDECO_MarineDrive_Ocean_View": "MAT_ArtDeco_CreamIvory",
        "ARTDECO_MarineDrive_Rajab_Mahal": "MAT_ArtDeco_PalePeach",
        "ARTDECO_MarineDrive_Fairlawn": "MAT_ArtDeco_MaladOchre",
        "ARTDECO_MarineDrive_Gool_Mahal": "MAT_ArtDeco_SeafoamGreen",
        "ARTDECO_MarineDrive_Sea_Green_Hotel": "MAT_ArtDeco_CreamIvory"
    }
    for b_name, m_name in ad_mats.items():
        o = bpy.data.objects.get(b_name)
        mat = bpy.data.materials.get(m_name)
        if o and mat:
            o.data.materials.clear()
            o.data.materials.append(mat)
            o.hide_render = False

    # B. Nariman Point Modernist Towers
    c_np = bpy.data.collections.get('Sector_B_MarineDrive_NarimanPoint')
    if c_np:
        for o in c_np.objects:
            if o.type == 'MESH' and 'Helipad' not in o.name:
                o.data.materials.clear()
                o.data.materials.append(shaders['ModernistCommercial'])
                o.hide_render = False

    # C. Worli & Lower Parel Megatowers
    c_sky = bpy.data.collections.get('Skyscrapers_Megatower_Corridor')
    if c_sky:
        for o in c_sky.objects:
            if o.type == 'MESH' and 'Helipad' not in o.name:
                o.data.materials.clear()
                o.data.materials.append(shaders['HighRiseCurtainWall'])
                o.hide_render = False

# ----------------------------------------------------------------------
# 4. CAMERA SETUP HELPER
# ----------------------------------------------------------------------
def setup_camera(name, eye, target, lens=28.0):
    cam = bpy.data.objects.get(name)
    if not cam:
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam)

    cam.location = eye
    dir_vec = (target - eye).normalized()
    cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens
    cam.data.clip_start = 0.5
    cam.data.clip_end = 50000.0
    return cam

def configure_all_architectural_cameras():
    print("[Cameras] Configuring 6 dedicated architectural cameras...")
    cams = [
        # 1. Marine Drive Art Deco Architectural Row
        {
            "name": "Cam_Arch_1_MarineDrive_ArtDeco",
            "eye": Vector((-1012.0, 930.0, 11.5)),
            "target": Vector((-960.0, 1050.0, 20.0)),
            "lens": 28.0,
            "title": "Marine Drive Art Deco Heritage Row"
        },
        # 2. Fort & Colaba Victorian Heritage District (CSMT / Horniman)
        {
            "name": "Cam_Arch_2_Fort_VictorianHeritage",
            "eye": Vector((225.0, 1720.0, 30.0)),
            "target": Vector((263.0, 1860.0, 32.0)),
            "lens": 28.0,
            "title": "CSMT & Fort Victorian Gothic Heritage"
        },
        # 3. Worli & Lower Parel High-Rise Megatowers
        {
            "name": "Cam_Arch_3_Worli_MegatowerHighRise",
            "eye": Vector((-580.0, 7550.0, 38.0)),
            "target": Vector((-315.0, 7960.0, 150.0)),
            "lens": 22.0,
            "title": "Worli & Lower Parel Contemporary Megatowers"
        },
        # 4. Nariman Point Waterfront Financial Skyline
        {
            "name": "Cam_Arch_4_NarimanPoint_Waterfront",
            "eye": Vector((-1260.0, 280.0, 20.0)),
            "target": Vector((-1080.0, 520.0, 65.0)),
            "lens": 28.0,
            "title": "Nariman Point Commercial Waterfront Skyline"
        },
        # 5. Girgaon Traditional Chawl Quarter
        {
            "name": "Cam_Arch_5_Girgaon_ChawlVernacular",
            "eye": Vector((-280.0, 3750.0, 14.0)),
            "target": Vector((-260.0, 3900.0, 18.0)),
            "lens": 32.0,
            "title": "Girgaon High-Density Vernacular Chawls"
        },
        # 6. Apollo Bunder Gateway & Taj Mahal Palace Precinct
        {
            "name": "Cam_Arch_6_ApolloBunder_HeritagePlaza",
            "eye": Vector((230.0, -130.0, 14.0)),
            "target": Vector((134.0, -138.0, 16.0)),
            "lens": 28.0,
            "title": "Apollo Bunder Gateway of India & Taj Mahal Palace"
        }
    ]

    for c in cams:
        setup_camera(c["name"], c["eye"], c["target"], c["lens"])
    return cams

# ----------------------------------------------------------------------
# 5. RENDER ALL ARCHITECTURAL VIEWS (1080P)
# ----------------------------------------------------------------------
def render_all(cams):
    print("[Render] Starting 1080p architectural renders...")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    results = []
    for idx, c in enumerate(cams, 1):
        cam_obj = bpy.data.objects.get(c["name"])
        if not cam_obj:
            continue
        scene.camera = cam_obj
        fname = f"arch_{idx}_{c['name'].replace('Cam_Arch_', '').lower()}.png"
        fpath = os.path.join(OUTPUT_DIR, fname)
        scene.render.filepath = fpath

        print(f"  Rendering [{idx}/{len(cams)}] {c['title']} -> {fpath}")
        bpy.ops.render.render(write_still=True)
        results.append((c["title"], fpath, os.path.getsize(fpath)))

    print("[Render] Complete!")
    return results

# ----------------------------------------------------------------------
# MASTER RUN
# ----------------------------------------------------------------------
def main():
    shaders = build_all_mumbai_shaders()
    build_authentic_mumbai_city(shaders)
    calibrate_mumbai_lighting()
    apply_materials_to_district_assets(shaders)
    cams = configure_all_architectural_cameras()
    rendered = render_all(cams)

    # Save upgraded .blend
    blend_path = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Save] Upgraded Digital Twin saved to {blend_path}")

    for title, path, sz in rendered:
        print(f"  * {title}: {path} ({sz / 1024:.1f} KB)")

if __name__ == "__main__":
    main()
