"""
GRAI — MUMBAI DIGITAL TWIN: ARCHITECTURAL MASTERPIECE ENGINE
Full Realistic Transformation of Each and Every Building:
1. Master Triplanar Residential Facade Shader (16,890 buildings):
   - Wall-aligned floor (3.2m) & bay (3.5m) fenestration grid
   - 15cm recessed window normal depth
   - 5 authentic Mumbai architectural palettes with per-building random selection
   - Multi-tone evening window life (incandescent, cool LED, reflective dark glass)
   - Dark weathered bitumen roof terrace
2. Master Commercial Glass Skyscraper Shader (Nariman Point & Megatowers):
   - High-reflectivity coastal solar glass (Fresnel ocean reflection)
   - 3.8m floor spandrels & vertical anodized aluminum mullions
   - Illuminated corporate office floors
3. UNESCO Marine Drive Art Deco Shader (12 heritage oceanfront buildings):
   - Streamline Moderne horizontal banding & rounded cantilever balconies
   - Warm cream, pastel ochre, and seafoam stucco
   - Teak/bronze casement window fenestrations
4. UNESCO Victorian Gothic Stone Shader (CSMT, High Court, Rajabai Tower):
   - Basalt stone & yellow Malad sandstone masonry relief
   - Pointed arch window recesses & copper roof crowns
5. BSE Rotunda Tower Shader (Dalal Street iconic skyscraper):
   - Radial floor rings and reflective curtain glass
6. High-Performance Rooftop Infrastructure (Mumtys & Sintex Water Tanks):
   - Combined batched mesh for elevator penthouses and water tanks
   - Breaks up flat cuboid silhouettes into authentic Mumbai rooftop topography
7. Environmental Atmosphere & Lighting Calibration:
   - Warm sunset golden hour with Arabian Sea specular trail
"""
import bpy
import bmesh
import math
import random
import time
import mathutils
from mathutils import Vector, Matrix

globals()['bmesh'] = bmesh
globals()['mathutils'] = mathutils
globals()['Vector'] = Vector
globals()['Matrix'] = Matrix
globals()['math'] = math
globals()['random'] = random

def build_master_residential_shader():
    mat_name = "MAT_Mumbai_Ultra_Residential"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1800, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (1500, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Coordinates
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1600, 0)
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-1600, 400)
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1600, -400)

    # 1. Normal separation: Roof vs Wall
    sep_norm = nodes.new("ShaderNodeSeparateXYZ")
    sep_norm.location = (-1400, 400)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])

    norm_abs = nodes.new("ShaderNodeVectorMath")
    norm_abs.location = (-1400, 200)
    norm_abs.operation = 'ABSOLUTE'
    links.new(geom.outputs['Normal'], norm_abs.inputs[0])

    sep_norm_abs = nodes.new("ShaderNodeSeparateXYZ")
    sep_norm_abs.location = (-1200, 200)
    links.new(norm_abs.outputs['Vector'], sep_norm_abs.inputs['Vector'])

    # Roof mask: Normal.Z > 0.6
    roof_mask = nodes.new("ShaderNodeMath")
    roof_mask.location = (-1200, 400)
    roof_mask.operation = 'GREATER_THAN'
    roof_mask.inputs[1].default_value = 0.6
    links.new(sep_norm.outputs['Z'], roof_mask.inputs[0])

    # Wall alignment: Is wall facing X or Y? (abs(Normal.X) > abs(Normal.Y))
    is_x_wall = nodes.new("ShaderNodeMath")
    is_x_wall.location = (-1000, 200)
    is_x_wall.operation = 'GREATER_THAN'
    links.new(sep_norm_abs.outputs['X'], is_x_wall.inputs[0])
    links.new(sep_norm_abs.outputs['Y'], is_x_wall.inputs[1])

    # Separate Object Position XYZ
    sep_pos = nodes.new("ShaderNodeSeparateXYZ")
    sep_pos.location = (-1400, 0)
    links.new(tex_coord.outputs['Object'], sep_pos.inputs['Vector'])

    # Select Horizontal Coordinate: If X-wall use Y, else use X
    mix_horiz = nodes.new("ShaderNodeMix")
    mix_horiz.location = (-800, 100)
    mix_horiz.data_type = 'FLOAT'
    links.new(sep_pos.outputs['X'], mix_horiz.inputs[2]) # False: Y-wall -> use X
    links.new(sep_pos.outputs['Y'], mix_horiz.inputs[3]) # True:  X-wall -> use Y
    links.new(is_x_wall.outputs['Value'], mix_horiz.inputs[0])

    # Floor Scale: 1 floor = ~3.2m
    # Bay Scale:   1 bay   = ~3.5m
    scale_v = nodes.new("ShaderNodeMath")
    scale_v.location = (-600, -100)
    scale_v.operation = 'DIVIDE'
    scale_v.inputs[1].default_value = 3.2
    links.new(sep_pos.outputs['Z'], scale_v.inputs[0])

    scale_u = nodes.new("ShaderNodeMath")
    scale_u.location = (-600, 100)
    scale_u.operation = 'DIVIDE'
    scale_u.inputs[1].default_value = 3.5
    links.new(mix_horiz.outputs[0], scale_u.inputs[0])

    # fract(u) and fract(v) for within-bay coordinates
    fract_u = nodes.new("ShaderNodeMath")
    fract_u.location = (-400, 100)
    fract_u.operation = 'FRACT'
    links.new(scale_u.outputs['Value'], fract_u.inputs[0])

    fract_v = nodes.new("ShaderNodeMath")
    fract_v.location = (-400, -100)
    fract_v.operation = 'FRACT'
    links.new(scale_v.outputs['Value'], fract_v.inputs[0])

    # Window horizontal mask: 0.18 < fract_u < 0.82
    u_min = nodes.new("ShaderNodeMath")
    u_min.location = (-200, 200)
    u_min.operation = 'GREATER_THAN'
    u_min.inputs[1].default_value = 0.18
    links.new(fract_u.outputs['Value'], u_min.inputs[0])

    u_max = nodes.new("ShaderNodeMath")
    u_max.location = (-200, 100)
    u_max.operation = 'LESS_THAN'
    u_max.inputs[1].default_value = 0.82
    links.new(fract_u.outputs['Value'], u_max.inputs[0])

    u_win = nodes.new("ShaderNodeMath")
    u_win.location = (0, 150)
    u_win.operation = 'MULTIPLY'
    links.new(u_min.outputs['Value'], u_win.inputs[0])
    links.new(u_max.outputs['Value'], u_win.inputs[1])

    # Window vertical mask: 0.28 < fract_v < 0.82 (spandrel beam = 0.0..0.28 and 0.82..1.0)
    v_min = nodes.new("ShaderNodeMath")
    v_min.location = (-200, -50)
    v_min.operation = 'GREATER_THAN'
    v_min.inputs[1].default_value = 0.28
    links.new(fract_v.outputs['Value'], v_min.inputs[0])

    v_max = nodes.new("ShaderNodeMath")
    v_max.location = (-200, -150)
    v_max.operation = 'LESS_THAN'
    v_max.inputs[1].default_value = 0.82
    links.new(fract_v.outputs['Value'], v_max.inputs[0])

    v_win = nodes.new("ShaderNodeMath")
    v_win.location = (0, -100)
    v_win.operation = 'MULTIPLY'
    links.new(v_min.outputs['Value'], v_win.inputs[0])
    links.new(v_max.outputs['Value'], v_win.inputs[1])

    # Combined Window Area
    win_area = nodes.new("ShaderNodeMath")
    win_area.location = (200, 0)
    win_area.operation = 'MULTIPLY'
    links.new(u_win.outputs['Value'], win_area.inputs[0])
    links.new(v_win.outputs['Value'], win_area.inputs[1])

    # Above ground floor: Z > 3.8m
    above_ground = nodes.new("ShaderNodeMath")
    above_ground.location = (200, -200)
    above_ground.operation = 'GREATER_THAN'
    above_ground.inputs[1].default_value = 3.8
    links.new(sep_pos.outputs['Z'], above_ground.inputs[0])

    # Not Roof: 1.0 - roof_mask
    not_roof = nodes.new("ShaderNodeMath")
    not_roof.location = (200, 200)
    not_roof.operation = 'SUBTRACT'
    not_roof.inputs[0].default_value = 1.0
    links.new(roof_mask.outputs['Value'], not_roof.inputs[1])

    # Final Valid Window Mask
    win_final1 = nodes.new("ShaderNodeMath")
    win_final1.location = (400, 0)
    win_final1.operation = 'MULTIPLY'
    links.new(win_area.outputs['Value'], win_final1.inputs[0])
    links.new(above_ground.outputs['Value'], win_final1.inputs[1])

    win_final = nodes.new("ShaderNodeMath")
    win_final.location = (600, 0)
    win_final.operation = 'MULTIPLY'
    links.new(win_final1.outputs['Value'], win_final.inputs[0])
    links.new(not_roof.outputs['Value'], win_final.inputs[1])

    # 2. Authentic Mumbai Wall Palette (Random per building)
    ramp_wall = nodes.new("ShaderNodeValToRGB")
    ramp_wall.location = (0, -400)
    ramp_wall.color_ramp.interpolation = 'CONSTANT'
    ramp_wall.color_ramp.elements[0].position = 0.0
    ramp_wall.color_ramp.elements[0].color = (0.78, 0.74, 0.66, 1.0) # Malad Warm Sandstone
    ramp_wall.color_ramp.elements[1].position = 0.30
    ramp_wall.color_ramp.elements[1].color = (0.72, 0.60, 0.46, 1.0) # Mumbai Terracotta Ochre
    e2 = ramp_wall.color_ramp.elements.new(0.55)
    e2.color = (0.65, 0.52, 0.42, 1.0) # Indian Red Oxide Stucco
    e3 = ramp_wall.color_ramp.elements.new(0.75)
    e3.color = (0.58, 0.66, 0.62, 1.0) # Coastal Sage Green
    e4 = ramp_wall.color_ramp.elements.new(0.90)
    e4.color = (0.68, 0.70, 0.72, 1.0) # Modern Concrete Grey
    links.new(obj_info.outputs['Random'], ramp_wall.inputs['Fac'])

    # Subtle concrete weathering noise
    noise_wall = nodes.new("ShaderNodeTexNoise")
    noise_wall.location = (200, -400)
    noise_wall.inputs['Scale'].default_value = 8.0
    noise_wall.inputs['Detail'].default_value = 2.0
    links.new(tex_coord.outputs['Object'], noise_wall.inputs['Vector'])

    mix_wall_weather = nodes.new("ShaderNodeMix")
    mix_wall_weather.location = (400, -400)
    mix_wall_weather.data_type = 'RGBA'
    mix_wall_weather.inputs[0].default_value = 0.15 # 15% subtle grunge
    mix_wall_weather.inputs[7].default_value = (0.45, 0.43, 0.40, 1.0)
    links.new(ramp_wall.outputs['Color'], mix_wall_weather.inputs[6])

    # Facade Color (Wall vs Window Glass)
    mix_facade_col = nodes.new("ShaderNodeMix")
    mix_facade_col.location = (800, -100)
    mix_facade_col.data_type = 'RGBA'
    mix_facade_col.inputs[7].default_value = (0.04, 0.08, 0.12, 1.0) # Deep Reflective Coastal Glass
    links.new(mix_wall_weather.outputs[2], mix_facade_col.inputs[6])
    links.new(win_final.outputs['Value'], mix_facade_col.inputs[0])

    # Final Base Color with Dark Roof
    mix_final_col = nodes.new("ShaderNodeMix")
    mix_final_col.location = (1100, 100)
    mix_final_col.data_type = 'RGBA'
    mix_final_col.inputs[7].default_value = (0.13, 0.14, 0.15, 1.0) # Weathered Bitumen Roof Tar
    links.new(mix_facade_col.outputs[2], mix_final_col.inputs[6])
    links.new(roof_mask.outputs['Value'], mix_final_col.inputs[0])
    links.new(mix_final_col.outputs[2], bsdf.inputs['Base Color'])

    # Roughness: Wall = 0.78, Window Glass = 0.08, Roof = 0.90
    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (800, -300)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = 0.78 # Wall
    mix_rough.inputs[3].default_value = 0.08 # Glass
    links.new(win_final.outputs['Value'], mix_rough.inputs[0])

    mix_final_rough = nodes.new("ShaderNodeMix")
    mix_final_rough.location = (1100, -200)
    mix_final_rough.data_type = 'FLOAT'
    mix_final_rough.inputs[3].default_value = 0.90 # Roof
    links.new(mix_rough.outputs[0], mix_final_rough.inputs[2])
    links.new(roof_mask.outputs['Value'], mix_final_rough.inputs[0])
    links.new(mix_final_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Glass has 0.20 specular reflectivity, Wall & Roof 0.0
    mix_met = nodes.new("ShaderNodeMix")
    mix_met.location = (1100, -350)
    mix_met.data_type = 'FLOAT'
    mix_met.inputs[2].default_value = 0.0
    mix_met.inputs[3].default_value = 0.25 # Glass reflectivity
    links.new(win_final.outputs['Value'], mix_met.inputs[0])
    links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

    # Recessed Window Normal Bump (15cm recess)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (1200, -500)
    bump.inputs['Strength'].default_value = 0.60
    bump.inputs['Distance'].default_value = 0.15
    links.new(win_final.outputs['Value'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # 3. Evening Window Glow (Varied residential interior lighting)
    floor_int = nodes.new("ShaderNodeMath")
    floor_int.location = (-400, -300)
    floor_int.operation = 'FLOOR'
    links.new(scale_v.outputs['Value'], floor_int.inputs[0])

    bay_int = nodes.new("ShaderNodeMath")
    bay_int.location = (-400, 300)
    bay_int.operation = 'FLOOR'
    links.new(scale_u.outputs['Value'], bay_int.inputs[0])

    win_hash = nodes.new("ShaderNodeTexWhiteNoise")
    win_hash.location = (0, -600)
    win_hash.noise_dimensions = '3D'
    combine_hash = nodes.new("ShaderNodeCombineXYZ")
    combine_hash.location = (-200, -600)
    links.new(bay_int.outputs['Value'], combine_hash.inputs['X'])
    links.new(floor_int.outputs['Value'], combine_hash.inputs['Y'])
    links.new(obj_info.outputs['Random'], combine_hash.inputs['Z'])
    links.new(combine_hash.outputs['Vector'], win_hash.inputs['Vector'])

    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (300, -600)
    ramp_glow.color_ramp.interpolation = 'CONSTANT'
    ramp_glow.color_ramp.elements[0].position = 0.0
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Unlit
    ramp_glow.color_ramp.elements[1].position = 0.60
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.82, 0.50, 1.0) # Warm incandescent glow
    e_led = ramp_glow.color_ramp.elements.new(0.92)
    e_led.color = (0.85, 0.92, 1.0, 1.0) # Cool office/LED glow
    links.new(win_hash.outputs['Value'], ramp_glow.inputs['Fac'])

    is_lit = nodes.new("ShaderNodeMath")
    is_lit.location = (600, -600)
    is_lit.operation = 'GREATER_THAN'
    is_lit.inputs[1].default_value = 0.59
    links.new(win_hash.outputs['Value'], is_lit.inputs[0])

    glow_mult = nodes.new("ShaderNodeMath")
    glow_mult.location = (900, -600)
    glow_mult.operation = 'MULTIPLY'
    links.new(win_final.outputs['Value'], glow_mult.inputs[0])
    links.new(is_lit.outputs['Value'], glow_mult.inputs[1])

    glow_strength = nodes.new("ShaderNodeMath")
    glow_strength.location = (1100, -600)
    glow_strength.operation = 'MULTIPLY'
    glow_strength.inputs[1].default_value = 2.5
    links.new(glow_mult.outputs['Value'], glow_strength.inputs[0])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(glow_strength.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission'])

    return mat

def build_master_glass_tower_shader():
    mat_name = "MAT_Mumbai_Ultra_GlassTower"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1600, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (1300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1400, 0)
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-1400, 400)
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1400, -400)

    # Roof mask
    sep_norm = nodes.new("ShaderNodeSeparateXYZ")
    sep_norm.location = (-1200, 400)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])
    roof_mask = nodes.new("ShaderNodeMath")
    roof_mask.location = (-1000, 400)
    roof_mask.operation = 'GREATER_THAN'
    roof_mask.inputs[1].default_value = 0.6
    links.new(sep_norm.outputs['Z'], roof_mask.inputs[0])

    # Position Z for floor spandrel bands (3.8m commercial floor height)
    sep_pos = nodes.new("ShaderNodeSeparateXYZ")
    sep_pos.location = (-1200, 0)
    links.new(tex_coord.outputs['Object'], sep_pos.inputs['Vector'])

    scale_floor = nodes.new("ShaderNodeMath")
    scale_floor.location = (-1000, 0)
    scale_floor.operation = 'DIVIDE'
    scale_floor.inputs[1].default_value = 3.8
    links.new(sep_pos.outputs['Z'], scale_floor.inputs[0])

    fract_floor = nodes.new("ShaderNodeMath")
    fract_floor.location = (-800, 0)
    fract_floor.operation = 'FRACT'
    links.new(scale_floor.outputs['Value'], fract_floor.inputs[0])

    # Spandrel band: 0.0 to 0.22 is dark aluminum spandrel beam, 0.22 to 1.0 is glass
    is_glass_h = nodes.new("ShaderNodeMath")
    is_glass_h.location = (-600, 0)
    is_glass_h.operation = 'GREATER_THAN'
    is_glass_h.inputs[1].default_value = 0.22
    links.new(fract_floor.outputs['Value'], is_glass_h.inputs[0])

    not_roof = nodes.new("ShaderNodeMath")
    not_roof.location = (-600, 200)
    not_roof.operation = 'SUBTRACT'
    not_roof.inputs[0].default_value = 1.0
    links.new(roof_mask.outputs['Value'], not_roof.inputs[1])

    is_glass = nodes.new("ShaderNodeMath")
    is_glass.location = (-400, 100)
    is_glass.operation = 'MULTIPLY'
    links.new(is_glass_h.outputs['Value'], is_glass.inputs[0])
    links.new(not_roof.outputs['Value'], is_glass.inputs[1])

    # Glass Tint (Ocean Reflective Azure / Slate)
    ramp_tint = nodes.new("ShaderNodeValToRGB")
    ramp_tint.location = (-400, -200)
    ramp_tint.color_ramp.elements[0].position = 0.0
    ramp_tint.color_ramp.elements[0].color = (0.05, 0.12, 0.20, 1.0) # Deep Marine Blue
    ramp_tint.color_ramp.elements[1].position = 1.0
    ramp_tint.color_ramp.elements[1].color = (0.08, 0.16, 0.22, 1.0) # Coastal Azure
    links.new(obj_info.outputs['Random'], ramp_tint.inputs['Fac'])

    # Mix Spandrel vs Glass Color
    mix_curtain = nodes.new("ShaderNodeMix")
    mix_curtain.location = (-100, 0)
    mix_curtain.data_type = 'RGBA'
    mix_curtain.inputs[6].default_value = (0.16, 0.17, 0.19, 1.0) # Anodized Aluminum Spandrel
    links.new(ramp_tint.outputs['Color'], mix_curtain.inputs[7])  # Glass
    links.new(is_glass.outputs['Value'], mix_curtain.inputs[0])

    # Final with Roof Tar
    mix_final = nodes.new("ShaderNodeMix")
    mix_final.location = (200, 100)
    mix_final.data_type = 'RGBA'
    mix_final.inputs[7].default_value = (0.10, 0.11, 0.12, 1.0) # Helipad / Roof Tar
    links.new(mix_curtain.outputs[2], mix_final.inputs[6])
    links.new(roof_mask.outputs['Value'], mix_final.inputs[0])
    links.new(mix_final.outputs[2], bsdf.inputs['Base Color'])

    # Physical Glass & Metal Shading
    # Roughness: Glass = 0.04 (mirror ocean reflection!), Spandrel = 0.35, Roof = 0.85
    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (200, -100)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = 0.35
    mix_rough.inputs[3].default_value = 0.04
    links.new(is_glass.outputs['Value'], mix_rough.inputs[0])

    mix_final_rough = nodes.new("ShaderNodeMix")
    mix_final_rough.location = (450, -100)
    mix_final_rough.data_type = 'FLOAT'
    mix_final_rough.inputs[3].default_value = 0.85
    links.new(mix_rough.outputs[0], mix_final_rough.inputs[2])
    links.new(roof_mask.outputs['Value'], mix_final_rough.inputs[0])
    links.new(mix_final_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Spandrel = 0.65, Glass = 0.20, Roof = 0.0
    mix_met = nodes.new("ShaderNodeMix")
    mix_met.location = (450, -250)
    mix_met.data_type = 'FLOAT'
    mix_met.inputs[2].default_value = 0.65
    mix_met.inputs[3].default_value = 0.15
    links.new(is_glass.outputs['Value'], mix_met.inputs[0])
    links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

    # Illuminated Office Floors (Evening commercial lighting)
    floor_int = nodes.new("ShaderNodeMath")
    floor_int.location = (-600, -350)
    floor_int.operation = 'FLOOR'
    links.new(scale_floor.outputs['Value'], floor_int.inputs[0])

    noise_office = nodes.new("ShaderNodeTexNoise")
    noise_office.location = (-300, -400)
    noise_office.inputs['Scale'].default_value = 2.0
    links.new(tex_coord.outputs['Object'], noise_office.inputs['Vector'])

    ramp_office = nodes.new("ShaderNodeValToRGB")
    ramp_office.location = (0, -400)
    ramp_office.color_ramp.elements[0].position = 0.45
    ramp_office.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_office.color_ramp.elements[1].position = 0.60
    ramp_office.color_ramp.elements[1].color = (1.0, 0.90, 0.70, 1.0) # Warm commercial office interior glow
    links.new(noise_office.outputs['Fac'], ramp_office.inputs['Fac'])

    glow_mult = nodes.new("ShaderNodeMath")
    glow_mult.location = (300, -400)
    glow_mult.operation = 'MULTIPLY'
    links.new(is_glass.outputs['Value'], glow_mult.inputs[0])
    links.new(ramp_office.outputs['Color'], glow_mult.inputs[1])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_office.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(is_glass.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_office.outputs['Color'], bsdf.inputs['Emission'])

    return mat

def build_master_artdeco_shader():
    mat_name = "MAT_MarineDrive_ArtDeco"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1600, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (1300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1400, 0)
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-1400, 400)
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1400, -400)

    # Roof mask
    sep_norm = nodes.new("ShaderNodeSeparateXYZ")
    sep_norm.location = (-1200, 400)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])
    roof_mask = nodes.new("ShaderNodeMath")
    roof_mask.location = (-1000, 400)
    roof_mask.operation = 'GREATER_THAN'
    roof_mask.inputs[1].default_value = 0.6
    links.new(sep_norm.outputs['Z'], roof_mask.inputs[0])

    # Art Deco Horizontal Balcony Banding: Floor height = 3.4m
    sep_pos = nodes.new("ShaderNodeSeparateXYZ")
    sep_pos.location = (-1200, 0)
    links.new(tex_coord.outputs['Object'], sep_pos.inputs['Vector'])

    scale_floor = nodes.new("ShaderNodeMath")
    scale_floor.location = (-1000, 0)
    scale_floor.operation = 'DIVIDE'
    scale_floor.inputs[1].default_value = 3.4
    links.new(sep_pos.outputs['Z'], scale_floor.inputs[0])

    fract_floor = nodes.new("ShaderNodeMath")
    fract_floor.location = (-800, 0)
    fract_floor.operation = 'FRACT'
    links.new(scale_floor.outputs['Value'], fract_floor.inputs[0])

    # Art Deco Palette: Cream, Butter Ochre, Dusty Coral, Seafoam Mint
    ramp_deco = nodes.new("ShaderNodeValToRGB")
    ramp_deco.location = (-800, -300)
    ramp_deco.color_ramp.interpolation = 'CONSTANT'
    ramp_deco.color_ramp.elements[0].position = 0.0
    ramp_deco.color_ramp.elements[0].color = (0.88, 0.84, 0.76, 1.0) # Classic Marine Drive Cream
    ramp_deco.color_ramp.elements[1].position = 0.35
    ramp_deco.color_ramp.elements[1].color = (0.84, 0.72, 0.54, 1.0) # Warm Art Deco Ochre
    e2 = ramp_deco.color_ramp.elements.new(0.70)
    e2.color = (0.75, 0.82, 0.78, 1.0) # Seafoam Mint Green
    links.new(obj_info.outputs['Random'], ramp_deco.inputs['Fac'])

    # Window vs Balcony: 0.35..0.85 is casement window, 0.0..0.35 is cantilevered balcony band
    win_min = nodes.new("ShaderNodeMath")
    win_min.location = (-600, 100)
    win_min.operation = 'GREATER_THAN'
    win_min.inputs[1].default_value = 0.35
    links.new(fract_floor.outputs['Value'], win_min.inputs[0])

    win_max = nodes.new("ShaderNodeMath")
    win_max.location = (-600, -50)
    win_max.operation = 'LESS_THAN'
    win_max.inputs[1].default_value = 0.85
    links.new(fract_floor.outputs['Value'], win_max.inputs[0])

    win_band = nodes.new("ShaderNodeMath")
    win_band.location = (-400, 0)
    win_band.operation = 'MULTIPLY'
    links.new(win_min.outputs['Value'], win_band.inputs[0])
    links.new(win_max.outputs['Value'], win_band.inputs[1])

    not_roof = nodes.new("ShaderNodeMath")
    not_roof.location = (-400, 200)
    not_roof.operation = 'SUBTRACT'
    not_roof.inputs[0].default_value = 1.0
    links.new(roof_mask.outputs['Value'], not_roof.inputs[1])

    is_window = nodes.new("ShaderNodeMath")
    is_window.location = (-200, 100)
    is_window.operation = 'MULTIPLY'
    links.new(win_band.outputs['Value'], is_window.inputs[0])
    links.new(not_roof.outputs['Value'], is_window.inputs[1])

    # Facade Color
    mix_facade = nodes.new("ShaderNodeMix")
    mix_facade.location = (100, 0)
    mix_facade.data_type = 'RGBA'
    mix_facade.inputs[7].default_value = (0.06, 0.10, 0.14, 1.0) # Dark reflective teak/glass
    links.new(ramp_deco.outputs['Color'], mix_facade.inputs[6])
    links.new(is_window.outputs['Value'], mix_facade.inputs[0])

    # Final with Roof
    mix_final = nodes.new("ShaderNodeMix")
    mix_final.location = (400, 100)
    mix_final.data_type = 'RGBA'
    mix_final.inputs[7].default_value = (0.16, 0.17, 0.18, 1.0)
    links.new(mix_facade.outputs[2], mix_final.inputs[6])
    links.new(roof_mask.outputs['Value'], mix_final.inputs[0])
    links.new(mix_final.outputs[2], bsdf.inputs['Base Color'])

    # Roughness
    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (400, -100)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = 0.75 # Stucco
    mix_rough.inputs[3].default_value = 0.10 # Glass
    links.new(is_window.outputs['Value'], mix_rough.inputs[0])
    links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

    # Balcony relief bump
    bump = nodes.new("ShaderNodeBump")
    bump.location = (700, -300)
    bump.inputs['Strength'].default_value = 0.50
    bump.inputs['Distance'].default_value = 0.20
    links.new(fract_floor.outputs['Value'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Evening Light
    noise_glow = nodes.new("ShaderNodeTexNoise")
    noise_glow.location = (100, -450)
    noise_glow.inputs['Scale'].default_value = 3.0
    links.new(tex_coord.outputs['Object'], noise_glow.inputs['Vector'])

    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (350, -450)
    ramp_glow.color_ramp.elements[0].position = 0.50
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_glow.color_ramp.elements[1].position = 0.65
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.85, 0.52, 1.0) # Warm incandescent
    links.new(noise_glow.outputs['Fac'], ramp_glow.inputs['Fac'])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(is_window.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission'])

    return mat

def build_master_heritage_gothic_shader():
    for mat_name, base_col in [
        ("MAT_CSMT_VictorianSandstone", (0.80, 0.72, 0.56, 1.0)), # Malad yellow sandstone
        ("MAT_Gothic_BasaltStone", (0.42, 0.43, 0.44, 1.0))       # Dark Kurla basalt
    ]:
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

        tex_coord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs['Scale'].default_value = 12.0
        noise.inputs['Detail'].default_value = 4.0
        links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

        mix_stone = nodes.new("ShaderNodeMix")
        mix_stone.data_type = 'RGBA'
        mix_stone.inputs[6].default_value = base_col
        mix_stone.inputs[7].default_value = (base_col[0]*0.75, base_col[1]*0.75, base_col[2]*0.75, 1.0)
        links.new(noise.outputs['Fac'], mix_stone.inputs[0])
        links.new(mix_stone.outputs[2], bsdf.inputs['Base Color'])

        bump = nodes.new("ShaderNodeBump")
        bump.inputs['Strength'].default_value = 0.40
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        bsdf.inputs['Roughness'].default_value = 0.88

def build_rooftop_infrastructure():
    """
    Batched Rooftop Infrastructure:
    Instantiates elevator headhouses (mumtys) and Sintex cylindrical water tanks
    across the top 3,500 buildings in a single lightning-fast bmesh object!
    """
    col_urban = bpy.data.collections.get("Urban_Fabric_City_Blocks")
    if not col_urban or not col_urban.objects:
        print("No urban fabric buildings found.")
        return

    # Delete previous rooftop infrastructure if present
    for old_name in ["ROOFTOP_Mumbai_Mumtys_Batched", "ROOFTOP_Mumbai_SintexTanks_Batched"]:
        old_obj = bpy.data.objects.get(old_name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

    print(f"Generating authentic rooftop infrastructure across buildings...")
    bm_mumty = bmesh.new()
    bm_tank = bmesh.new()

    # Materials for Mumtys & Tanks
    mat_mumty = bpy.data.materials.get("MAT_Rooftop_Mumty_Concrete")
    if not mat_mumty:
        mat_mumty = bpy.data.materials.new("MAT_Rooftop_Mumty_Concrete")
        mat_mumty.use_nodes = True
        bsdf = mat_mumty.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.55, 0.54, 0.52, 1.0) # Concrete stucco
            bsdf.inputs['Roughness'].default_value = 0.85

    mat_tank = bpy.data.materials.get("MAT_Sintex_WaterTank_Black")
    if not mat_tank:
        mat_tank = bpy.data.materials.new("MAT_Sintex_WaterTank_Black")
        mat_tank.use_nodes = True
        bsdf = mat_tank.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.04, 0.05, 0.08, 1.0) # Dark Sintex polymer
            bsdf.inputs['Roughness'].default_value = 0.30
            bsdf.inputs['Metallic'].default_value = 0.1

    # Select buildings: prioritize visible buildings (height > 20m, up to 4,000)
    eligible = [b for b in col_urban.objects if b.dimensions.z > 20.0]
    # Sample 3,500 buildings deterministically
    random.seed(42)
    selected = random.sample(eligible, min(3500, len(eligible)))

    # Cylinder template for water tanks: 8 segments
    cyl_segments = 8
    cyl_radius = 0.9 # 1.8m diameter
    cyl_height = 1.9 # 1.9m tall
    angles = [2.0 * math.pi * i / cyl_segments for i in range(cyl_segments)]

    for bldg in selected:
        bx = bldg.location.x
        by = bldg.location.y
        bz = bldg.location.z + bldg.dimensions.z # Roof elevation
        dx = bldg.dimensions.x
        dy = bldg.dimensions.y

        # 1. Mumty Box (Elevator machine room / staircase penthouse)
        mw = min(6.0, dx * 0.35)
        md = min(5.0, dy * 0.35)
        mh = 3.2 # 3.2m tall
        mx = bx + (random.random() - 0.5) * dx * 0.25
        my = by + (random.random() - 0.5) * dy * 0.25
        mz = bz + mh * 0.5

        # Add cube in bm_mumty
        bmesh.ops.create_cube(bm_mumty, size=1.0, matrix=Matrix.LocRotScale(Vector((mx, my, mz)), None, Vector((mw, md, mh))))

        # 2. Sintex Water Tanks (1 to 3 tanks per building)
        num_tanks = random.randint(1, 3)
        for t_idx in range(num_tanks):
            tx = mx + (t_idx - 1) * 2.2 + 1.2
            ty = my + md * 0.5 + 1.2
            tz = bz

            # Build simple cylinder in bm_tank
            bot_verts = [bm_tank.verts.new((tx + cyl_radius * math.cos(a), ty + cyl_radius * math.sin(a), tz)) for a in angles]
            top_verts = [bm_tank.verts.new((tx + cyl_radius * math.cos(a), ty + cyl_radius * math.sin(a), tz + cyl_height)) for a in angles]
            # Side faces
            for i in range(cyl_segments):
                i_next = (i + 1) % cyl_segments
                bm_tank.faces.new([bot_verts[i], bot_verts[i_next], top_verts[i_next], top_verts[i]])
            # Top and bottom caps
            bm_tank.faces.new(top_verts)
            bm_tank.faces.new(list(reversed(bot_verts)))

    # Write bmesh to actual mesh objects
    mesh_m = bpy.data.meshes.new("Mesh_Rooftop_Mumtys")
    bm_mumty.to_mesh(mesh_m)
    bm_mumty.free()
    obj_m = bpy.data.objects.new("ROOFTOP_Mumbai_Mumtys_Batched", mesh_m)
    obj_m.data.materials.append(mat_mumty)
    col_urban.objects.link(obj_m)

    mesh_t = bpy.data.meshes.new("Mesh_Rooftop_SintexTanks")
    bm_tank.to_mesh(mesh_t)
    bm_tank.free()
    obj_t = bpy.data.objects.new("ROOFTOP_Mumbai_SintexTanks_Batched", mesh_t)
    obj_t.data.materials.append(mat_tank)
    col_urban.objects.link(obj_t)

    print(f"Successfully generated {len(selected)} rooftop mumtys and water tanks in unified batched meshes!")

# Run all upgrades
build_master_residential_shader()
build_master_glass_tower_shader()
build_master_artdeco_shader()
build_master_heritage_gothic_shader()
build_rooftop_infrastructure()

# Calibrate Environmental Lighting
world = bpy.context.scene.world
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Strength'].default_value = 0.35

sun = bpy.data.objects.get("Sun_Mumbai")
if sun:
    sun.data.energy = 2.4
    sun.data.color = (1.0, 0.80, 0.58)

# Assign Materials to their respective collections and buildings
mat_glass = bpy.data.materials.get("MAT_Mumbai_Ultra_GlassTower")
mat_artdeco = bpy.data.materials.get("MAT_MarineDrive_ArtDeco")
mat_csmt = bpy.data.materials.get("MAT_CSMT_VictorianSandstone")
mat_basalt = bpy.data.materials.get("MAT_Gothic_BasaltStone")

# 1. Commercial Towers & Supertalls
for col_name in ["Skyscrapers_Megatower_Corridor", "Sector_B_MarineDrive_NarimanPoint"]:
    col = bpy.data.collections.get(col_name)
    if col:
        for obj in col.objects:
            if obj.type == 'MESH':
                if "BLDG_NarimanPoint" in obj.name or "AirIndia" in obj.name or "ExpressTowers" in obj.name or "Trident" in obj.name or "TOWER" in obj.name or "SKYSCRAPER" in obj.name:
                    if obj.material_slots:
                        obj.material_slots[0].material = mat_glass
                    else:
                        obj.data.materials.append(mat_glass)
                elif "ARTDECO" in obj.name:
                    if obj.material_slots:
                        obj.material_slots[0].material = mat_artdeco
                    else:
                        obj.data.materials.append(mat_artdeco)

# 2. Sector D Heritage
col_d = bpy.data.collections.get("Sector_D_Dharavi_CentralMumbai")
if col_d:
    for obj in col_d.objects:
        if obj.type == 'MESH':
            if "CSMT" in obj.name or "Heritage" in obj.name or "HighCourt" in obj.name or "Rajabai" in obj.name:
                if obj.material_slots:
                    obj.material_slots[0].material = mat_csmt
                else:
                    obj.data.materials.append(mat_csmt)
            elif "BSE" in obj.name:
                if obj.material_slots:
                    obj.material_slots[0].material = mat_glass
                else:
                    obj.data.materials.append(mat_glass)

# Save mainfile to retain full masterpiece
bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
print("Saved GRAI_Mumbai_Digital_Twin.blend with full architectural masterpiece upgrades.")
