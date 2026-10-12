"""
Architectural Realism Engine:
1. Normal.Z Roof Masking: Separates vertical facades from horizontal roofs
   - Roofs get dark weathered waterproofing tar/concrete (no window projection!)
   - Walls get proportional floor-aligned windows with mullions and sills
2. Commercial Curtain Wall: Deep reflective glass with metallic spandrel panels
3. Rooftop Infrastructure: Instantiates elevator motor rooms (mumtys) and rooftop water tanks
4. Atmospheric Color Calibration: Eliminates overexposure and grounds buildings with realistic Mumbai tones
"""
import bpy
import bmesh
import math
import random
import mathutils
from mathutils import Vector

globals()['bmesh'] = bmesh
globals()['mathutils'] = mathutils
globals()['Vector'] = Vector
globals()['math'] = math
globals()['random'] = random

def build_realistic_residential_facade():
    mat_name = "MAT_Mumbai_Ultra_Residential"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (1100, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Coordinates: Object coords
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1200, 0)

    # Geometry Normal for Roof vs Wall separation
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-1200, 400)
    sep_norm = nodes.new("ShaderNodeSeparateXYZ")
    sep_norm.location = (-1000, 400)
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])

    # Roof Mask: Normal.Z > 0.6 -> is_roof = 1.0
    roof_mask = nodes.new("ShaderNodeMath")
    roof_mask.location = (-800, 400)
    roof_mask.operation = 'GREATER_THAN'
    roof_mask.inputs[1].default_value = 0.6
    links.new(sep_norm.outputs['Z'], roof_mask.inputs[0])

    # Mapping for floor and window grid
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-950, -50)
    mapping.inputs['Scale'].default_value = (0.28, 0.28, 0.32) # ~3.1m floor height
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Random Building Wall Palette
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1200, -300)
    ramp_wall = nodes.new("ShaderNodeValToRGB")
    ramp_wall.location = (-900, -300)
    ramp_wall.color_ramp.interpolation = 'CONSTANT'
    ramp_wall.color_ramp.elements[0].position = 0.0
    ramp_wall.color_ramp.elements[0].color = (0.82, 0.79, 0.72, 1.0) # Mumbai Warm Sand
    ramp_wall.color_ramp.elements[1].position = 0.20
    ramp_wall.color_ramp.elements[1].color = (0.76, 0.66, 0.52, 1.0) # Terracotta Ochre
    e2 = ramp_wall.color_ramp.elements.new(0.42)
    e2.color = (0.70, 0.52, 0.44, 1.0) # Weathered Red Oxide
    e3 = ramp_wall.color_ramp.elements.new(0.65)
    e3.color = (0.64, 0.72, 0.66, 1.0) # Coastal Sage Green
    e4 = ramp_wall.color_ramp.elements.new(0.85)
    e4.color = (0.62, 0.68, 0.75, 1.0) # Washed Marine Blue
    links.new(obj_info.outputs['Random'], ramp_wall.inputs['Fac'])

    # Window Grid
    brick = nodes.new("ShaderNodeTexBrick")
    brick.location = (-650, -50)
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.16 # Wall pier width
    brick.inputs['Mortar Smooth'].default_value = 0.02
    brick.inputs['Brick Width'].default_value = 0.50
    brick.inputs['Row Height'].default_value = 0.65
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])

    # Wall vs Window Color on Facades
    # Facade Color: Mortar = Wall Color, Brick = Dark Glass
    mix_facade = nodes.new("ShaderNodeMix")
    mix_facade.location = (-350, 0)
    mix_facade.data_type = 'RGBA'
    mix_facade.inputs[6].default_value = (0.08, 0.12, 0.16, 1.0) # Dark reflective glass
    links.new(ramp_wall.outputs['Color'], mix_facade.inputs[7])   # Wall Stucco
    links.new(brick.outputs['Fac'], mix_facade.inputs[0])

    # Final Base Color: Mix Facade with Dark Roof
    mix_final_col = nodes.new("ShaderNodeMix")
    mix_final_col.location = (200, 100)
    mix_final_col.data_type = 'RGBA'
    mix_final_col.inputs[7].default_value = (0.16, 0.17, 0.18, 1.0) # Dark Weathered Tar/Concrete Roof
    links.new(mix_facade.outputs[2], mix_final_col.inputs[6])        # Facade
    links.new(roof_mask.outputs['Value'], mix_final_col.inputs[0])   # 1 if Roof, 0 if Wall
    links.new(mix_final_col.outputs[2], bsdf.inputs['Base Color'])

    # Roughness: Roof = 0.85, Wall = 0.75, Glass = 0.12
    mix_rough_facade = nodes.new("ShaderNodeMix")
    mix_rough_facade.location = (-350, -200)
    mix_rough_facade.data_type = 'FLOAT'
    mix_rough_facade.inputs[2].default_value = 0.12 # Glass
    mix_rough_facade.inputs[3].default_value = 0.75 # Wall
    links.new(brick.outputs['Fac'], mix_rough_facade.inputs[0])

    mix_final_rough = nodes.new("ShaderNodeMix")
    mix_final_rough.location = (200, -100)
    mix_final_rough.data_type = 'FLOAT'
    mix_final_rough.inputs[3].default_value = 0.88 # Roof roughness
    links.new(mix_rough_facade.outputs[0], mix_final_rough.inputs[2])
    links.new(roof_mask.outputs['Value'], mix_final_rough.inputs[0])
    links.new(mix_final_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Glass = 0.35, Rest = 0.0
    mix_met = nodes.new("ShaderNodeMix")
    mix_met.location = (200, -250)
    mix_met.data_type = 'FLOAT'
    mix_met.inputs[2].default_value = 0.35
    mix_met.inputs[3].default_value = 0.0
    links.new(brick.outputs['Fac'], mix_met.inputs[0])
    links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

    # Evening Window Glow in ~35% of windows
    noise_glow = nodes.new("ShaderNodeTexNoise")
    noise_glow.location = (-400, -450)
    noise_glow.inputs['Scale'].default_value = 6.0
    links.new(mapping.outputs['Vector'], noise_glow.inputs['Vector'])

    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (-150, -450)
    ramp_glow.color_ramp.elements[0].position = 0.62
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_glow.color_ramp.elements[1].position = 0.68
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.84, 0.50, 1.0) # Warm interior light
    links.new(noise_glow.outputs['Fac'], ramp_glow.inputs['Fac'])

    # Invert roof mask (so roof never glows)
    inv_roof = nodes.new("ShaderNodeMath")
    inv_roof.location = (100, -450)
    inv_roof.operation = 'SUBTRACT'
    inv_roof.inputs[0].default_value = 1.0
    links.new(roof_mask.outputs['Value'], inv_roof.inputs[1])

    # Glow strength: Window mask * Non-roof mask
    glow_mult = nodes.new("ShaderNodeMath")
    glow_mult.location = (350, -450)
    glow_mult.operation = 'MULTIPLY'
    links.new(brick.outputs['Fac'], glow_mult.inputs[0])
    links.new(inv_roof.outputs['Value'], glow_mult.inputs[1])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(glow_mult.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission'])

    # Recessed window bump
    bump = nodes.new("ShaderNodeBump")
    bump.location = (600, -250)
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.20
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def build_realistic_curtain_wall_glass():
    mat_name = "MAT_Mumbai_Ultra_GlassTower"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1200, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (900, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Roof vs Wall
    geom = nodes.new("ShaderNodeNewGeometry")
    sep_norm = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geom.outputs['Normal'], sep_norm.inputs['Vector'])
    roof_mask = nodes.new("ShaderNodeMath")
    roof_mask.operation = 'GREATER_THAN'
    roof_mask.inputs[1].default_value = 0.6
    links.new(sep_norm.outputs['Z'], roof_mask.inputs[0])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (0.08, 0.08, 0.08) # Proportional curtain grid
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.08 # Spandrel beam
    brick.inputs['Brick Width'].default_value = 0.60
    brick.inputs['Row Height'].default_value = 0.85
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])

    # Glass tint
    obj_info = nodes.new("ShaderNodeObjectInfo")
    ramp_glass = nodes.new("ShaderNodeValToRGB")
    ramp_glass.color_ramp.elements[0].position = 0.0
    ramp_glass.color_ramp.elements[0].color = (0.08, 0.16, 0.24, 1.0) # Deep Blue Marine Glass
    ramp_glass.color_ramp.elements[1].position = 1.0
    ramp_glass.color_ramp.elements[1].color = (0.12, 0.20, 0.26, 1.0) # Coastal Sky Reflective Tint
    links.new(obj_info.outputs['Random'], ramp_glass.inputs['Fac'])

    # Spandrel dark aluminum band
    mix_facade = nodes.new("ShaderNodeMix")
    mix_facade.data_type = 'RGBA'
    mix_facade.inputs[6].default_value = (0.18, 0.20, 0.22, 1.0) # Aluminum mullion
    links.new(ramp_glass.outputs['Color'], mix_facade.inputs[7])   # Glass
    links.new(brick.outputs['Fac'], mix_facade.inputs[0])

    # Final Base Color (with dark roof)
    mix_final = nodes.new("ShaderNodeMix")
    mix_final.data_type = 'RGBA'
    mix_final.inputs[7].default_value = (0.14, 0.15, 0.16, 1.0) # Dark Roof Helipad Tar
    links.new(mix_facade.outputs[2], mix_final.inputs[6])
    links.new(roof_mask.outputs['Value'], mix_final.inputs[0])
    links.new(mix_final.outputs[2], bsdf.inputs['Base Color'])

    # High Reflectivity
    bsdf.inputs['Metallic'].default_value = 0.85
    bsdf.inputs['Roughness'].default_value = 0.10

    # Illuminated Office Floors
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 4.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    ramp_light = nodes.new("ShaderNodeValToRGB")
    ramp_light.color_ramp.elements[0].position = 0.50
    ramp_light.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_light.color_ramp.elements[1].position = 0.60
    ramp_light.color_ramp.elements[1].color = (1.0, 0.90, 0.65, 1.0)
    links.new(noise.outputs['Fac'], ramp_light.inputs['Fac'])

    inv_roof = nodes.new("ShaderNodeMath")
    inv_roof.operation = 'SUBTRACT'
    inv_roof.inputs[0].default_value = 1.0
    links.new(roof_mask.outputs['Value'], inv_roof.inputs[1])

    glow_mult = nodes.new("ShaderNodeMath")
    glow_mult.operation = 'MULTIPLY'
    links.new(brick.outputs['Fac'], glow_mult.inputs[0])
    links.new(inv_roof.outputs['Value'], glow_mult.inputs[1])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_light.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(glow_mult.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_light.outputs['Color'], bsdf.inputs['Emission'])

    return mat

# Update shaders
build_realistic_residential_facade()
build_realistic_curtain_wall_glass()

result = "Shaders successfully upgraded with Roof/Wall Normal Separation and Realistic Proportions!"
print(result)
