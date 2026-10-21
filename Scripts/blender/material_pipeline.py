#!/usr/bin/env python3
"""
GRAI Blender Material Pipeline
Creates physically plausible PBR material definitions (BSDF) for buildings,
roads, terrain, and water, calibrated to Mumbai basalt, asphalt, and concrete.
"""

import sys

def create_pbr_material(name: str, base_color: tuple, roughness: float = 0.7, metallic: float = 0.0, normal_strength: float = 0.1):
    import bpy
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    out_node.location = (400, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    # Subtle procedural micro-noise bump for realism
    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-600, -100)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-400, -100)
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 3.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new("ShaderNodeBump")
    bump.location = (-200, -100)
    bump.inputs['Strength'].default_value = normal_strength
    bump.inputs['Distance'].default_value = 0.5
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

def setup_material_library():
    import bpy
    print("[MaterialPipeline] Setting up PBR material library in Blender...")
    materials = {
        "MAT_Building_LEVEL_A_VERIFIED": ((0.75, 0.65, 0.52, 1.0), 0.75, 0.05, 0.15), # Kharodi yellow basalt / stone
        "MAT_Building_LEVEL_B_INFERRED": ((0.62, 0.60, 0.58, 1.0), 0.80, 0.02, 0.10), # Modernist plaster & concrete
        "MAT_Building_LEVEL_C_UNAVAILABLE": ((0.50, 0.49, 0.48, 1.0), 0.85, 0.00, 0.08), # Neutral matte tone
        "MAT_Road_Asphalt": ((0.12, 0.12, 0.13, 1.0), 0.88, 0.00, 0.20), # Weathered Mumbai coastal asphalt
        "MAT_Road_Motorway": ((0.10, 0.10, 0.11, 1.0), 0.85, 0.00, 0.15),
        "MAT_Road_Primary": ((0.14, 0.14, 0.15, 1.0), 0.88, 0.00, 0.18),
        "MAT_Road_Residential": ((0.16, 0.15, 0.15, 1.0), 0.90, 0.00, 0.22),
        "MAT_Terrain_PBR": ((0.28, 0.26, 0.24, 1.0), 0.90, 0.00, 0.12),
        "MAT_Arabian_Sea_PBR": ((0.02, 0.06, 0.10, 1.0), 0.10, 0.10, 0.05)
    }

    created = []
    for name, (color, rough, met, bump) in materials.items():
        mat = create_pbr_material(name, color, rough, met, bump)
        created.append(mat.name)

    print(f"[MaterialPipeline] Created {len(created)} PBR materials: {created}")
    return created

if __name__ == "__main__":
    setup_material_library()
