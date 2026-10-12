"""
Polish Building Realism: Rich Palettes, Ground Contrast, Glass Reflections
- Fix: Blender color_ramp.elements has no .clear() — must remove elements individually
- Saturated authentic Mumbai building palettes
- Clean curtain wall glass tower shader (mirror reflections, no noise speckle)
- Dark urban ground for architectural contrast
- Rich golden-hour calibration
"""
import bpy
import math

def polish_residential_colors():
    """Update the existing residential color ramp with richer Mumbai tones."""
    mat = bpy.data.materials.get("MAT_Mumbai_Ultra_Residential")
    if not mat or not mat.use_nodes:
        return

    nodes = mat.node_tree.nodes

    # Find the wall palette color ramp (type VALTORGB near y=-400)
    ramp_wall = None
    for n in nodes:
        if n.type == 'VALTORGB' and n.location.y < -300 and n.location.x < 100:
            ramp_wall = n
            break

    if ramp_wall:
        cr = ramp_wall.color_ramp
        # Remove extra elements (keep first 2, they can't be deleted)
        while len(cr.elements) > 2:
            cr.elements.remove(cr.elements[-1])

        # Update the two permanent elements
        cr.elements[0].position = 0.0
        cr.elements[0].color = (0.84, 0.70, 0.46, 1.0)  # Rich Malad Ochre / Warm Mustard
        cr.elements[1].position = 0.25
        cr.elements[1].color = (0.68, 0.38, 0.26, 1.0)  # Indian Red Oxide Stucco

        # Add new elements
        e2 = cr.elements.new(0.50)
        e2.color = (0.86, 0.83, 0.74, 1.0)  # Heritage Ivory / Warm Cream
        e3 = cr.elements.new(0.72)
        e3.color = (0.45, 0.60, 0.55, 1.0)  # Coastal Sage Green
        e4 = cr.elements.new(0.88)
        e4.color = (0.74, 0.48, 0.34, 1.0)  # Weathered Terracotta Clay

    # Update glass darkness (find the facade color mix node)
    for n in nodes:
        if n.type == 'MIX' and hasattr(n, 'data_type') and n.data_type == 'RGBA':
            # Deep reflective glass color
            try:
                v7 = list(n.inputs[7].default_value)
                if v7[0] < 0.1 and v7[1] < 0.15 and v7[2] < 0.2 and n.location.x > 700:
                    n.inputs[7].default_value = (0.02, 0.05, 0.08, 1.0)
            except:
                pass
            # Dark roof tar
            try:
                v7 = list(n.inputs[7].default_value)
                if abs(v7[0] - 0.13) < 0.03 and abs(v7[1] - 0.14) < 0.03 and n.location.x > 1000:
                    n.inputs[7].default_value = (0.08, 0.09, 0.10, 1.0)
            except:
                pass

    print("Polished MAT_Mumbai_Ultra_Residential with rich authentic palettes.")

def polish_glass_tower():
    """Rebuild the glass tower shader for clean ribbon glass with mirror reflections."""
    mat = bpy.data.materials.get("MAT_Mumbai_Ultra_GlassTower")
    if not mat or not mat.use_nodes:
        return
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

    # Position Z for clean floor spandrel bands (3.8m commercial floor)
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

    # Spandrel band: 0..0.24 = aluminum, 0.24..1.0 = ribbon glass
    is_glass_h = nodes.new("ShaderNodeMath")
    is_glass_h.location = (-600, 0)
    is_glass_h.operation = 'GREATER_THAN'
    is_glass_h.inputs[1].default_value = 0.24
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

    # Curtain Wall Tint (Deep Marine Solar Glass)
    ramp_tint = nodes.new("ShaderNodeValToRGB")
    ramp_tint.location = (-400, -200)
    ramp_tint.color_ramp.elements[0].position = 0.0
    ramp_tint.color_ramp.elements[0].color = (0.02, 0.08, 0.16, 1.0)
    ramp_tint.color_ramp.elements[1].position = 1.0
    ramp_tint.color_ramp.elements[1].color = (0.05, 0.12, 0.18, 1.0)
    links.new(obj_info.outputs['Random'], ramp_tint.inputs['Fac'])

    # Spandrel vs Glass Color
    mix_curtain = nodes.new("ShaderNodeMix")
    mix_curtain.location = (-100, 0)
    mix_curtain.data_type = 'RGBA'
    mix_curtain.inputs[6].default_value = (0.24, 0.25, 0.28, 1.0)  # Anodized Aluminum
    links.new(ramp_tint.outputs['Color'], mix_curtain.inputs[7])
    links.new(is_glass.outputs['Value'], mix_curtain.inputs[0])

    # Final with Roof
    mix_final = nodes.new("ShaderNodeMix")
    mix_final.location = (200, 100)
    mix_final.data_type = 'RGBA'
    mix_final.inputs[7].default_value = (0.09, 0.10, 0.11, 1.0)
    links.new(mix_curtain.outputs[2], mix_final.inputs[6])
    links.new(roof_mask.outputs['Value'], mix_final.inputs[0])
    links.new(mix_final.outputs[2], bsdf.inputs['Base Color'])

    # Mirror Roughness: Glass = 0.02, Spandrel = 0.25, Roof = 0.90
    mix_rough = nodes.new("ShaderNodeMix")
    mix_rough.location = (200, -100)
    mix_rough.data_type = 'FLOAT'
    mix_rough.inputs[2].default_value = 0.25
    mix_rough.inputs[3].default_value = 0.02
    links.new(is_glass.outputs['Value'], mix_rough.inputs[0])

    mix_final_rough = nodes.new("ShaderNodeMix")
    mix_final_rough.location = (450, -100)
    mix_final_rough.data_type = 'FLOAT'
    mix_final_rough.inputs[3].default_value = 0.90
    links.new(mix_rough.outputs[0], mix_final_rough.inputs[2])
    links.new(roof_mask.outputs['Value'], mix_final_rough.inputs[0])
    links.new(mix_final_rough.outputs[0], bsdf.inputs['Roughness'])

    # Metallic: Spandrel = 0.85, Glass = 0.10
    mix_met = nodes.new("ShaderNodeMix")
    mix_met.location = (450, -250)
    mix_met.data_type = 'FLOAT'
    mix_met.inputs[2].default_value = 0.85
    mix_met.inputs[3].default_value = 0.10
    links.new(is_glass.outputs['Value'], mix_met.inputs[0])
    links.new(mix_met.outputs[0], bsdf.inputs['Metallic'])

    # Clean per-floor evening office glow (no noise speckle)
    floor_int = nodes.new("ShaderNodeMath")
    floor_int.location = (-600, -350)
    floor_int.operation = 'FLOOR'
    links.new(scale_floor.outputs['Value'], floor_int.inputs[0])

    floor_hash = nodes.new("ShaderNodeTexWhiteNoise")
    floor_hash.location = (-400, -450)
    floor_hash.noise_dimensions = '2D'
    combine_floor = nodes.new("ShaderNodeCombineXYZ")
    combine_floor.location = (-550, -450)
    links.new(floor_int.outputs['Value'], combine_floor.inputs['X'])
    links.new(obj_info.outputs['Random'], combine_floor.inputs['Y'])
    links.new(combine_floor.outputs['Vector'], floor_hash.inputs['Vector'])

    is_lit = nodes.new("ShaderNodeMath")
    is_lit.location = (-150, -450)
    is_lit.operation = 'GREATER_THAN'
    is_lit.inputs[1].default_value = 0.65
    links.new(floor_hash.outputs['Value'], is_lit.inputs[0])

    glow_mult = nodes.new("ShaderNodeMath")
    glow_mult.location = (150, -450)
    glow_mult.operation = 'MULTIPLY'
    links.new(is_glass.outputs['Value'], glow_mult.inputs[0])
    links.new(is_lit.outputs['Value'], glow_mult.inputs[1])

    glow_strength = nodes.new("ShaderNodeMath")
    glow_strength.location = (400, -450)
    glow_strength.operation = 'MULTIPLY'
    glow_strength.inputs[1].default_value = 3.5
    links.new(glow_mult.outputs['Value'], glow_strength.inputs[0])

    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.90, 0.72, 1.0)
        links.new(glow_strength.outputs['Value'], bsdf.inputs['Emission Strength'])

    print("Polished MAT_Mumbai_Ultra_GlassTower with clean mirror glass.")

def polish_ground_and_sea():
    """Darken ground and roads for maximum architectural contrast."""
    updates = {
        "MAT_Mumbai_Peninsula_Ground": ((0.13, 0.14, 0.15, 1.0), 0.92),
        "MAT_Road_Asphalt_Indian": ((0.11, 0.12, 0.13, 1.0), 0.85),
        "Mat_Asphalt_Road": ((0.11, 0.12, 0.13, 1.0), 0.85),
        "MAT_MarineDrive_PromenadeStone": ((0.72, 0.68, 0.60, 1.0), 0.80),
    }
    for mat_name, (base_col, rough) in updates.items():
        mat = bpy.data.materials.get(mat_name)
        if mat and mat.use_nodes:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs['Base Color'].default_value = base_col
                bsdf.inputs['Roughness'].default_value = rough

    # Deep Arabian Sea
    sea = bpy.data.materials.get("MAT_Arabian_Sea")
    if sea and sea.use_nodes:
        bsdf = sea.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.015, 0.08, 0.16, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.06
            bsdf.inputs['Metallic'].default_value = 0.15

    print("Polished ground, roads, promenade, and Arabian Sea.")

# Execute all polish functions
polish_residential_colors()
polish_glass_tower()
polish_ground_and_sea()

# Save
bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
print("Saved GRAI_Mumbai_Digital_Twin.blend with polished realism.")
