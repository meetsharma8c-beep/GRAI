"""
Mumbai Digital Twin Lighting Manager
====================================
Provides two authentic, physically calibrated lighting modes for Mumbai:
1. GOLDEN_HOUR: Rich afternoon coastal sunset over the Arabian Sea (~12 deg elevation).
2. QUEENS_NECKLACE_TWILIGHT: World-famous magic hour / dusk where the glowing ribbon
   of 277 golden streetlamps illuminates against the deep cobalt indigo sea and sky,
   with architectural floodlighting on Gateway of India, Taj Mahal Palace, and Sea Link.
"""
import bpy
import math
from mathutils import Vector

def setup_floodlight(name, loc, color, energy, light_type='POINT', radius=1.5):
    obj = bpy.data.objects.get(name)
    if not obj:
        ldata = bpy.data.lights.new(name=f"{name}_Data", type=light_type)
        obj = bpy.data.objects.new(name=name, object_data=ldata)
        # Link to Urban_Street_Lighting collection
        col = bpy.data.collections.get("Urban_Street_Lighting")
        if not col:
            col = bpy.context.scene.collection
        col.objects.link(obj)

    obj.location = Vector(loc)
    obj.data.color = color
    obj.data.energy = energy
    if hasattr(obj.data, 'shadow_soft_size'):
        obj.data.shadow_soft_size = radius
    return obj

def set_mode(mode='GOLDEN_HOUR'):
    scene = bpy.context.scene
    world = scene.world
    sky = None
    if world and world.use_nodes:
        for n in world.node_tree.nodes:
            if n.type == 'TEX_SKY':
                sky = n
                break

    sun = bpy.data.objects.get("Sun_Mumbai")
    mat_glow = bpy.data.materials.get("MAT_StreetLight_WarmGlow")
    bsdf_glow = mat_glow.node_tree.nodes.get("Principled BSDF") if (mat_glow and mat_glow.use_nodes) else None

    if mode == 'QUEENS_NECKLACE_TWILIGHT':
        print(">>> Activating QUEENS_NECKLACE_TWILIGHT Mode...")
        # 1. World Sky: Deep cobalt twilight with warm horizon fringe
        if sky:
            sky.sky_type = 'MULTIPLE_SCATTERING'
            sky.sun_elevation = -0.065 # ~3.7 degrees below horizon (Civil Twilight)
            sky.sun_rotation = -2.10
            sky.sun_intensity = 1.0
            sky.air_density = 1.30
            sky.aerosol_density = 1.75
            sky.ozone_density = 4.2 # Intense deep royal blue / indigo zenith
            sky.ground_albedo = 0.15

        # 2. Ambient twilight fill
        if sun:
            sun.data.energy = 0.25 # Faint cool twilight sky fill
            sun.data.color = (0.35, 0.50, 0.85)

        # 3. Marine Drive Streetlights: Glowing Amber-Gold Ribbon
        if bsdf_glow:
            bsdf_glow.inputs['Emission Color'].default_value = (1.0, 0.82, 0.40, 1.0)
            bsdf_glow.inputs['Emission Strength'].default_value = 24.0 # High bloom/emission for night

        # 4. Gateway of India Heritage Floodlighting
        setup_floodlight("LIGHT_Gateway_Flood_West", (215.0, -135.0, 4.0), (1.0, 0.86, 0.62), 1500.0, 'POINT', radius=3.0)
        setup_floodlight("LIGHT_Gateway_Flood_East", (240.0, -135.0, 4.0), (1.0, 0.86, 0.62), 1500.0, 'POINT', radius=3.0)

        # 5. Taj Mahal Palace Heritage Floodlighting
        setup_floodlight("LIGHT_Taj_Flood_Facade", (210.0, -85.0, 6.0), (1.0, 0.88, 0.72), 2200.0, 'POINT', radius=4.0)
        setup_floodlight("LIGHT_Taj_Dome_Glow", (200.0, -90.0, 42.0), (1.0, 0.40, 0.22), 900.0, 'POINT', radius=2.5)

        # 6. Sea Link Pylon Illumination
        setup_floodlight("LIGHT_SeaLink_Pylon_Bandra", (-1450.0, 12050.0, 45.0), (0.95, 0.96, 1.0), 3500.0, 'POINT', radius=5.0)

        # Tone Mapping for night illumination
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'Medium High Contrast'
        scene.view_settings.exposure = 0.2

    else: # GOLDEN_HOUR
        print(">>> Activating GOLDEN_HOUR Mode...")
        if sky:
            sky.sky_type = 'MULTIPLE_SCATTERING'
            sky.sun_elevation = 0.22 # ~12.6 degrees above horizon
            sky.sun_rotation = -2.10
            sky.sun_intensity = 1.0
            sky.air_density = 1.25
            sky.aerosol_density = 1.95
            sky.ozone_density = 3.5
            sky.ground_albedo = 0.20

        if sun:
            sun.data.energy = 4.6
            sun.data.color = (1.0, 0.85, 0.62)
            sun.data.angle = math.radians(3.8)
            sun.rotation_euler = (math.radians(77.4), math.radians(4.5), math.radians(-120.3))

        if bsdf_glow:
            bsdf_glow.inputs['Emission Color'].default_value = (1.0, 0.82, 0.45, 1.0)
            bsdf_glow.inputs['Emission Strength'].default_value = 8.0

        # Turn down floodlights for daytime
        for fname in ["LIGHT_Gateway_Flood_West", "LIGHT_Gateway_Flood_East", "LIGHT_Taj_Flood_Facade", "LIGHT_Taj_Dome_Glow", "LIGHT_SeaLink_Pylon_Bandra"]:
            fl = bpy.data.objects.get(fname)
            if fl:
                fl.data.energy = 0.0

        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'High Contrast'
        scene.view_settings.exposure = 0.0

    # Save to blendfile
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    return f"Switched scene lighting to: {mode}"

if __name__ == '__main__':
    msg = set_mode('QUEENS_NECKLACE_TWILIGHT')
    print(msg)
