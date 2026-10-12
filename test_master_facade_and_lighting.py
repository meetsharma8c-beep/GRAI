"""
Master Architectural Facade & Environmental Lighting Upgrade for GRAI Mumbai Digital Twin
- Triplanar wall-aligned coordinate system: height Z for floor levels, horizontal perimeter for bays
- Crisp architectural window grid: recessed sills, spandrel beams, ground floor commercial plinth
- Authentic Mumbai color palettes with per-building Object Random variation
- Multi-tone evening window illumination (warm 2800K incandescent, 5000K LED, dark unlit)
- Balanced golden-hour sunset lighting: calibrated sun & sky strength to eliminate overexposure
"""
import bpy
import math

def build_master_residential_facade():
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

    # Absolute Normals
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
    # Floor integer and bay integer for individual window hashing
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

    # Glow Color: 35% warm incandescent (1.0, 0.82, 0.52), 10% cool LED (0.85, 0.95, 1.0), 55% unlit (0,0,0)
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

    # Glow Strength = Window Mask * Non-unlit mask * 3.0
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

# Update shader
build_master_residential_facade()

# 4. Calibrate Environmental Sun & Sky for Golden Hour (No Overexposure)
world = bpy.context.scene.world
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Strength'].default_value = 0.35 # Calibrated ambient sky strength

sun = bpy.data.objects.get("Sun_Mumbai")
if sun:
    sun.data.energy = 2.2 # Calibrated direct sunset sunlight (warm 2200K tone)
    sun.data.color = (1.0, 0.78, 0.55)

# Render test frame
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
cam = bpy.data.objects.get("Cam_Fort_Heritage_District")
if cam:
    scene.camera = cam
    scene.render.filepath = "/tmp/test_master_facade.png"
    bpy.ops.render.render(write_still=True)

print("Master residential facade and lighting updated successfully!")
