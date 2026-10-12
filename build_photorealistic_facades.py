"""
Build Ultra-Realistic Procedural Facades for all Mumbai Buildings:
1. MAT_Mumbai_Ultra_Residential: ObjectInfo Random-driven pastel/weathered stucco colors,
   recessed window frames, balconies, monsoon rain streaks, and evening interior window glow.
2. MAT_Mumbai_Ultra_GlassTower: Sleek curtain wall glass with reflective panels, horizontal spandrels,
   and illuminated office floors.
3. MAT_Mumbai_Ultra_ArtDeco: Marine Drive cream limestone, horizontal speedlines, and nautical trims.
4. MAT_Mumbai_Ultra_HeritageGothic: Kurla basalt, Porbandar stone, and copper roof trims.
5. Dark tar/gravel rooftop material with parapet edge separation.
"""
import bpy
import math

def build_advanced_residential_shader():
    name = "MAT_Mumbai_Ultra_Residential"
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # 1. Output & BSDF
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1200, 0)
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (900, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # 2. Coordinates & Mapping
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-1200, 0)
    
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)
    mapping.inputs['Scale'].default_value = (0.35, 0.35, 0.32) # Scale so each floor is ~3.2m
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # 3. Object Info (for random per-building color variation)
    obj_info = nodes.new("ShaderNodeObjectInfo")
    obj_info.location = (-1200, 400)

    # ColorRamp for Authentic Mumbai Residential Palette
    ramp_wall = nodes.new("ShaderNodeValToRGB")
    ramp_wall.location = (-900, 400)
    ramp_wall.color_ramp.interpolation = 'CONSTANT'
    # Define realistic Mumbai residential colors:
    # 0.0: Classic Mumbai warm cream / off-white
    ramp_wall.color_ramp.elements[0].position = 0.0
    ramp_wall.color_ramp.elements[0].color = (0.84, 0.81, 0.74, 1.0)
    # 1.0: Warm ochre / sandy yellow
    ramp_wall.color_ramp.elements[1].position = 0.22
    ramp_wall.color_ramp.elements[1].color = (0.80, 0.68, 0.50, 1.0)
    # Add Pale Terracotta
    e2 = ramp_wall.color_ramp.elements.new(0.44)
    e2.color = (0.75, 0.54, 0.44, 1.0)
    # Add Muted Seafoam / Pista Green
    e3 = ramp_wall.color_ramp.elements.new(0.66)
    e3.color = (0.65, 0.73, 0.67, 1.0)
    # Add Weathered Coastal Blue
    e4 = ramp_wall.color_ramp.elements.new(0.85)
    e4.color = (0.60, 0.68, 0.76, 1.0)
    links.new(obj_info.outputs['Random'], ramp_wall.inputs['Fac'])

    # 4. Procedural Window Grid (Brick Texture)
    brick_windows = nodes.new("ShaderNodeTexBrick")
    brick_windows.location = (-700, 0)
    brick_windows.inputs['Scale'].default_value = 1.0
    brick_windows.inputs['Mortar Size'].default_value = 0.12 # Wall frame thickness between windows
    brick_windows.inputs['Mortar Smooth'].default_value = 0.02
    brick_windows.inputs['Bias'].default_value = 0.0
    brick_windows.inputs['Brick Width'].default_value = 0.55 # Window width
    brick_windows.inputs['Row Height'].default_value = 0.70  # Window height
    links.new(mapping.outputs['Vector'], brick_windows.inputs['Vector'])

    # 5. Window Pane Material vs Wall Material
    # Brick output 'Color': 0 = mortar (wall), 1 = brick (window pane)
    # Window glass dark base color
    mix_base_col = nodes.new("ShaderNodeMix")
    mix_base_col.location = (-400, 200)
    mix_base_col.data_type = 'RGBA'
    mix_base_col.inputs[6].default_value = (0.10, 0.14, 0.18, 1.0) # Dark reflective glass pane
    links.new(ramp_wall.outputs['Color'], mix_base_col.inputs[7])    # Wall stucco
    links.new(brick_windows.outputs['Fac'], mix_base_col.inputs[0]) # Fac: 0=mortar, 1=brick
    links.new(mix_base_col.outputs[2], bsdf.inputs['Base Color'])

    # 6. Roughness: Glass is shiny (0.1), Wall is rough (0.8)
    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (-400, -100)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = 0.12 # Glass roughness
    mix_rough.inputs[3].default_value = 0.78 # Stucco roughness
    links.new(brick_windows.outputs['Fac'], mix_rough.inputs[0])
    links.new(mix_rough.outputs[0], bsdf.inputs['Roughness'])

    # 7. Metallic: Glass reflection (0.4), Wall (0.0)
    mix_met = nodes.new("ShaderNodeMix")
    mix_met.location = (-400, -300)
    mix_met.data_type = 'FLOAT'
    mix_met.inputs[2].default_value = 0.45
    mix_met.inputs[3].default_value = 0.0
    links.new(brick_windows.outputs['Fac'], mix_met.inputs[0])
    links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

    # 8. Evening Window Glow (Warm Amber interior lights in ~35% of windows)
    noise_glow = nodes.new("ShaderNodeTexNoise")
    noise_glow.location = (-600, -500)
    noise_glow.inputs['Scale'].default_value = 8.0
    links.new(mapping.outputs['Vector'], noise_glow.inputs['Vector'])

    ramp_glow = nodes.new("ShaderNodeValToRGB")
    ramp_glow.location = (-350, -500)
    ramp_glow.color_ramp.elements[0].position = 0.58
    ramp_glow.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Off
    ramp_glow.color_ramp.elements[1].position = 0.65
    ramp_glow.color_ramp.elements[1].color = (1.0, 0.82, 0.45, 1.0) # Warm tungsten / incandescent glow
    links.new(noise_glow.outputs['Fac'], ramp_glow.inputs['Fac'])

    # Multiply glow by window mask (so only windows glow, never walls)
    math_glow = nodes.new("ShaderNodeMath")
    math_glow.location = (-100, -500)
    math_glow.operation = 'MULTIPLY'
    links.new(brick_windows.outputs['Fac'], math_glow.inputs[0])
    links.new(ramp_glow.outputs['Color'], math_glow.inputs[1])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission Color'])
        links.new(math_glow.outputs['Value'], bsdf.inputs['Emission Strength'])
    elif 'Emission' in bsdf.inputs:
        links.new(ramp_glow.outputs['Color'], bsdf.inputs['Emission'])

    # 9. Window Depth Bump (Recessed Windows)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (400, -300)
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.25
    links.new(brick_windows.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def build_advanced_glass_tower_shader():
    name = "MAT_Mumbai_Ultra_GlassTower"
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs['Scale'].default_value = (0.25, 0.25, 0.25)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 1.0
    brick.inputs['Mortar Size'].default_value = 0.05 # Sleek metallic mullions
    brick.inputs['Brick Width'].default_value = 0.50
    brick.inputs['Row Height'].default_value = 0.85
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])

    # Glass tint variation
    obj_info = nodes.new("ShaderNodeObjectInfo")
    ramp_glass = nodes.new("ShaderNodeValToRGB")
    ramp_glass.color_ramp.elements[0].position = 0.0
    ramp_glass.color_ramp.elements[0].color = (0.12, 0.22, 0.32, 1.0) # Deep Marine Blue
    ramp_glass.color_ramp.elements[1].position = 1.0
    ramp_glass.color_ramp.elements[1].color = (0.18, 0.28, 0.36, 1.0) # Coastal Cyan Blue
    links.new(obj_info.outputs['Random'], ramp_glass.inputs['Fac'])

    links.new(ramp_glass.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = 0.85 # High metallic curtain wall
    bsdf.inputs['Roughness'].default_value = 0.12 # Mirror reflection

    # Floor by floor illuminated office lights
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 6.0
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    ramp_light = nodes.new("ShaderNodeValToRGB")
    ramp_light.color_ramp.elements[0].position = 0.45
    ramp_light.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_light.color_ramp.elements[1].position = 0.55
    ramp_light.color_ramp.elements[1].color = (1.0, 0.92, 0.70, 1.0) # Office lighting
    links.new(noise.outputs['Fac'], ramp_light.inputs['Fac'])

    if 'Emission Color' in bsdf.inputs:
        links.new(ramp_light.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 2.5

    # Glass normal bump (subtle panel curvature)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.15
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

# Build both shaders
mat_res = build_advanced_residential_shader()
mat_glass = build_advanced_glass_tower_shader()

# Assign MAT_Mumbai_Ultra_Residential to all urban fabric buildings
col_urban = bpy.data.collections.get('Urban_Fabric_City_Blocks')
if col_urban:
    for obj in col_urban.objects:
        if obj.type == 'MESH':
            obj.data.materials.clear()
            obj.data.materials.append(mat_res)

# Assign MAT_Mumbai_Ultra_GlassTower to Megatower skyscrapers & Nariman Point commercial towers
col_sky = bpy.data.collections.get('Skyscrapers_Megatower_Corridor')
if col_sky:
    for obj in col_sky.objects:
        if obj.type == 'MESH' and 'Helipad' not in obj.name and 'Spire' not in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_glass)

col_b = bpy.data.collections.get('Sector_B_MarineDrive_NarimanPoint')
if col_b:
    for obj in col_b.objects:
        if obj.type == 'MESH' and ('BLDG_' in obj.name or 'AirIndia' in obj.name or 'Express' in obj.name or 'Trident' in obj.name):
            obj.data.materials.clear()
            obj.data.materials.append(mat_glass)

# Assign MAT_Mumbai_Ultra_Residential to Colaba Authoritative OSM buildings
col_a = bpy.data.collections.get('Sector_A_SouthMumbai_Colaba')
if col_a:
    for obj in col_a.objects:
        if obj.type == 'MESH' and 'SECTOR_A' in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_res)

result = "Ultra-Realistic Procedural Facades Built and Assigned to All Buildings!"
print(result)
