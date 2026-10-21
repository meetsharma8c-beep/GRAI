#!/usr/bin/env python3
"""
GRAI — Fix Road Textures, Single Physical Sunlight & Vibrant Authentic Colors
"""

import os
import math
import bpy
from mathutils import Vector, Euler

REPO_ROOT = "/Users/ms/Downloads/GRAI"
OUTPUT_DIR = os.path.join(REPO_ROOT, "renders/architectures")

def run():
    print("[ColorFix] Purging rogue lights and enforcing single tropical sun...")

    # 1. Remove rogue suns and daytime floodlights
    rogue_lights = [
        "Light_Apollo_Harbour_Bounce",
        "LIGHT_Fill_GoldenHour",
        "LIGHT_Gateway_Flood_East",
        "LIGHT_Gateway_Flood_West",
        "LIGHT_Taj_Flood_Facade",
        "LIGHT_Taj_Dome_Glow"
    ]
    for l_name in rogue_lights:
        l_obj = bpy.data.objects.get(l_name)
        if l_obj:
            print(f"  Removing rogue light: {l_name}")
            bpy.data.objects.remove(l_obj, do_unlink=True)

    # 2. Calibrate single Sun_Mumbai
    sun = bpy.data.objects.get("Sun_Mumbai")
    if not sun:
        s_data = bpy.data.lights.new("Sun_Mumbai", type='SUN')
        sun = bpy.data.objects.new("Sun_Mumbai", s_data)
        bpy.context.scene.collection.objects.link(sun)
    sun.data.energy = 3.6
    sun.data.color = (1.0, 0.90, 0.78)
    sun.data.angle = math.radians(0.8)
    sun.rotation_euler = Euler((math.radians(46.0), math.radians(14.0), math.radians(65.0)), 'XYZ')

    # Sky background strength
    world = bpy.context.scene.world
    if world and world.node_tree:
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs['Strength'].default_value = 0.50

    # Color management
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -1.25

    # 3. Configure all materials with rich authentic colors
    def set_principled_mat(mat_name, base_rgb, rough=0.75, metal=0.0):
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        bsdf.inputs['Base Color'].default_value = base_rgb
        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
        return mat

    # Asphalt Roads (Pitch-black tropical bitumen)
    asphalt_rgb = (0.052, 0.052, 0.058, 1.0)
    for m_name in [
        'MAT_MarineDrive_Asphalt_Master',
        'MAT_RealRoad_Asphalt',
        'MAT_RealMumbai_Road_Asphalt_Master',
        'MAT_SeaLink_HighwayAsphalt'
    ]:
        set_principled_mat(m_name, asphalt_rgb, rough=0.72)

    # Road Markings
    set_principled_mat('MAT_Road_White_Markings', (0.95, 0.95, 0.92, 1.0), rough=0.35)
    set_principled_mat('MAT_Road_Yellow_Median', (0.94, 0.72, 0.06, 1.0), rough=0.40)

    # BMC Curbs
    set_principled_mat('MAT_BMC_Curb_Black', (0.06, 0.06, 0.07, 1.0), rough=0.65)
    set_principled_mat('MAT_BMC_Curb_Yellow', (0.94, 0.72, 0.06, 1.0), rough=0.55)

    # Sidewalk Pavers (BMC terracotta red)
    paver_rgb = (0.52, 0.22, 0.16, 1.0)
    set_principled_mat('MAT_MarineDrive_Sidewalk_Pavers', paver_rgb, rough=0.82)
    set_principled_mat('MAT_RealMumbai_Sidewalk_Pavers', paver_rgb, rough=0.82)

    # Apollo Bunder Heritage Basalt Flagstone Plaza
    basalt_rgb = (0.36, 0.32, 0.25, 1.0)
    set_principled_mat('MAT_RealMumbai_Heritage_Basalt_Flagstone', basalt_rgb, rough=0.78)
    set_principled_mat('MAT_Plaza_Basalt_Flagstone', basalt_rgb, rough=0.78)

    # Seawall Concrete & Tetrapods
    set_principled_mat('MAT_MarineDrive_SeawallConcrete', (0.58, 0.56, 0.52, 1.0), rough=0.85)
    set_principled_mat('MAT_Concrete_Tetrapod_Marine', (0.36, 0.36, 0.37, 1.0), rough=0.88)
    set_principled_mat('MAT_RealMumbai_Promenade_Seawall', (0.58, 0.56, 0.52, 1.0), rough=0.85)

    # Urban Ground Plinth
    set_principled_mat('MAT_Mumbai_Peninsula_SRTM_PBR', (0.12, 0.12, 0.13, 1.0), rough=0.85)
    set_principled_mat('Mat_Mumbai_Real_Terrain', (0.12, 0.12, 0.13, 1.0), rough=0.85)

    # Gateway of India: Deep Golden Kharodi Basalt
    mat_gw = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt_Authentic")
    if not mat_gw:
        mat_gw = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt_Authentic")
    mat_gw.use_nodes = True
    nt_gw = mat_gw.node_tree
    nt_gw.nodes.clear()
    out_gw = nt_gw.nodes.new("ShaderNodeOutputMaterial")
    bsdf_gw = nt_gw.nodes.new("ShaderNodeBsdfPrincipled")
    nt_gw.links.new(bsdf_gw.outputs['BSDF'], out_gw.inputs['Surface'])
    # Rich golden Kharodi stone
    bsdf_gw.inputs['Base Color'].default_value = (0.58, 0.42, 0.22, 1.0)
    bsdf_gw.inputs['Roughness'].default_value = 0.85

    # Taj Mahal Palace
    set_principled_mat("Mat_Taj_Mahal_Palace_Cream", (0.76, 0.68, 0.54, 1.0), rough=0.75)
    set_principled_mat("Mat_Taj_Red_Dome_Authentic", (0.52, 0.06, 0.04, 1.0), rough=0.45)
    set_principled_mat("Mat_Taj_Tower_White", (0.76, 0.74, 0.70, 1.0), rough=0.65)

    # Marine Drive Art Deco Pastels
    set_principled_mat("MAT_RealMumbai_ArtDeco_Cream", (0.82, 0.76, 0.62, 1.0), rough=0.68)
    set_principled_mat("MAT_RealMumbai_ArtDeco_Ochre", (0.76, 0.48, 0.16, 1.0), rough=0.68)
    set_principled_mat("MAT_RealMumbai_ArtDeco_Seafoam", (0.22, 0.52, 0.42, 1.0), rough=0.68)
    set_principled_mat("MAT_RealMumbai_ArtDeco_Peach", (0.76, 0.38, 0.22, 1.0), rough=0.68)

    # CSMT Victorian Gothic Sandstone & Dome
    set_principled_mat("MAT_CSMT_VictorianSandstone", (0.66, 0.52, 0.32, 1.0), rough=0.82)
    set_principled_mat("MAT_CSMT_VerdigrisDome", (0.18, 0.52, 0.42, 1.0), rough=0.45, metal=0.35)

    # Rooftops
    set_principled_mat("MAT_RealMumbai_RoofTar_PBR", (0.06, 0.06, 0.07, 1.0), rough=0.95)
    set_principled_mat("MAT_Sintex_WaterTank_Black", (0.04, 0.04, 0.05, 1.0), rough=0.35)

    # Arabian Sea
    set_principled_mat("MAT_Arabian_Sea", (0.012, 0.055, 0.14, 1.0), rough=0.08)

    # Save blend
    blend_path = os.path.join(REPO_ROOT, "GRAI_Mumbai_Digital_Twin.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[Save] Saved color-calibrated master to {blend_path}")

    # Re-render critical views in Cycles
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    views = [
        ("arch_6_apollobunder_gateway_taj.png", "Cam_Arch_6_ApolloBunder_HeritagePlaza"),
        ("road_1_marinedrive_streetview.png", "Cam_Player_MarineDrive_Promenade"),
        ("arch_1_marinedrive_artdeco.png", "Cam_Arch_1_MarineDrive_ArtDeco"),
        ("arch_2_csmt_fort_gothic.png", "Cam_Arch_2_Fort_VictorianHeritage")
    ]

    for fname, cname in views:
        cam = bpy.data.objects.get(cname)
        if cam:
            scene.camera = cam
            out_p = os.path.join(OUTPUT_DIR, fname)
            scene.render.filepath = out_p
            print(f"  Rendering {fname}...")
            bpy.ops.render.render(write_still=True)
            print(f"    Saved: {out_p}")

if __name__ == "__main__":
    run()
