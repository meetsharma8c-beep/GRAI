"""
ARCHITECTURAL MASTERPIECE: HERO REDEVELOPMENT OF APOLLO BUNDER
- Bespoke High-Fidelity Gateway of India (Indo-Saracenic Triumphal Arch)
- Bespoke High-Fidelity Taj Mahal Palace & Tower
- Paved Basalt Plaza with Heritage Lamp Posts & Sea Promenade
- Cinematic Camera Framing with Majestic Low-Angle Perspective
- Photorealistic EEVEE Next Golden Hour Lighting & Material Shaders
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

# Collections
def get_col(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

col_landmarks = get_col("Landmarks_Bespoke_Architecture")
col_props = get_col("Playable_Street_Props")
col_promenade = get_col("Coastline_Promenade_Structures")

# ----------------------------------------------------------------------
# 1. PHOTOREALISTIC MATERIAL SHADERS
# ----------------------------------------------------------------------
def setup_kharodi_basalt():
    mat = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt")
    if not mat:
        mat = bpy.data.materials.new("Mat_Yellow_Kharodi_Basalt")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    
    # Procedural Stone Brick / Masonry Courses
    brick = nodes.new("ShaderNodeTexBrick")
    brick.inputs['Scale'].default_value = 14.0
    brick.inputs['Mortar Size'].default_value = 0.025
    brick.inputs['Bias'].default_value = 0.0
    brick.inputs['Color1'].default_value = (0.76, 0.62, 0.42, 1.0) # Warm golden Kharodi basalt
    brick.inputs['Color2'].default_value = (0.64, 0.52, 0.36, 1.0) # Darker basalt block
    brick.inputs['Mortar'].default_value = (0.38, 0.32, 0.24, 1.0) # Lime mortar joint
    links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])

    # Fine Stone Grain Noise
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs['Scale'].default_value = 65.0
    noise.inputs['Detail'].default_value = 5.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    # Mix brick with noise for organic weathering
    mix_col = nodes.new("ShaderNodeMix")
    mix_col.data_type = 'RGBA'
    mix_col.inputs[0].default_value = 0.35
    links.new(brick.outputs['Color'], mix_col.inputs[6])
    links.new(noise.outputs['Color'], mix_col.inputs[7])
    links.new(mix_col.outputs[2], bsdf.inputs['Base Color'])

    # Stone Surface Relief & Mortar Inset Bump
    bump = nodes.new("ShaderNodeBump")
    bump.inputs['Strength'].default_value = 0.45
    bump.inputs['Distance'].default_value = 0.04
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Roughness'].default_value = 0.85
    bsdf.inputs['Specular IOR Level'].default_value = 0.35
    return mat

def setup_taj_facade():
    mat = bpy.data.materials.get("Mat_Taj_Mahal_Palace")
    if not mat:
        mat = bpy.data.materials.new("Mat_Taj_Mahal_Palace")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    
    # Horizontal architectural banding
    sep_pos = nodes.new("ShaderNodeSeparateXYZ")
    links.new(tex_coord.outputs['Object'], sep_pos.inputs['Vector'])
    
    # 5.2m floor tier striping
    math_div = nodes.new("ShaderNodeMath")
    math_div.operation = 'DIVIDE'
    math_div.inputs[1].default_value = 5.2
    links.new(sep_pos.outputs['Z'], math_div.inputs[0])
    
    math_fract = nodes.new("ShaderNodeMath")
    math_fract.operation = 'FRACT'
    links.new(math_div.outputs['Value'], math_fract.inputs[0])

    ramp_tier = nodes.new("ShaderNodeValToRGB")
    ramp_tier.color_ramp.elements[0].position = 0.0
    ramp_tier.color_ramp.elements[0].color = (0.78, 0.52, 0.38, 1.0) # Terracotta sandstone wall
    ramp_tier.color_ramp.elements[1].position = 0.22
    ramp_tier.color_ramp.elements[1].color = (0.92, 0.90, 0.84, 1.0) # White ornamental balcony balustrade
    links.new(math_fract.outputs['Value'], ramp_tier.inputs['Fac'])
    links.new(ramp_tier.outputs['Color'], bsdf.inputs['Base Color'])

    bsdf.inputs['Roughness'].default_value = 0.75
    return mat

def setup_taj_dome():
    mat = bpy.data.materials.get("Mat_Taj_Red_Dome")
    if not mat:
        mat = bpy.data.materials.new("Mat_Taj_Red_Dome")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Saturated Florentine Vermilion Terracotta
    bsdf.inputs['Base Color'].default_value = (0.62, 0.14, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.38 # Smooth glazed terracotta sheen
    bsdf.inputs['Specular IOR Level'].default_value = 0.55
    return mat

def setup_gold():
    mat = bpy.data.materials.get("Mat_Heritage_Gold_Finial")
    if not mat:
        mat = bpy.data.materials.new("Mat_Heritage_Gold_Finial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.98, 0.78, 0.22, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.18
    return mat

mat_basalt = setup_kharodi_basalt()
mat_taj = setup_taj_facade()
mat_dome = setup_taj_dome()
mat_gold = setup_gold()

# ----------------------------------------------------------------------
# 2. SCULPT BESPOKE GATEWAY OF INDIA
# Real World Alignment: Location (174.17, -113.10, 0.0)
# ----------------------------------------------------------------------
old_gw = bpy.data.objects.get("LANDMARK_Gateway_of_India")
if old_gw:
    bpy.data.objects.remove(old_gw, do_unlink=True)

gw_mesh = bpy.data.meshes.new("LANDMARK_Gateway_of_India_Mesh")
gw_obj = bpy.data.objects.new("LANDMARK_Gateway_of_India", gw_mesh)
col_landmarks.objects.link(gw_obj)
gw_obj.location = Vector((174.17, -113.10, 0.0))

bm = bmesh.new()

# Dimensions:
# Along Y (Coasting North-South): Width = 28m
# Along X (East-West Harbour Axis): Depth = 16m
# Height = 26m to parapet, 38m to central dome tip

# 1. Podium Steps (3 stepped plinth tiers)
for st in range(3):
    sz_x = 18.0 + (2 - st) * 2.0
    sz_y = 30.0 + (2 - st) * 2.0
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, st * 0.45))) @ Matrix.Diagonal(Vector((sz_x, sz_y, 0.5, 1.0))))

# 2. Left Pylon (South Wing): Y from -14 to -5, X from -7.5 to 7.5, Z from 1.2 to 26.0
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, -9.5, 13.6))) @ Matrix.Diagonal(Vector((15.0, 9.0, 24.8, 1.0))))

# 3. Right Pylon (North Wing): Y from 5 to 14, X from -7.5 to 7.5, Z from 1.2 to 26.0
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 9.5, 13.6))) @ Matrix.Diagonal(Vector((15.0, 9.0, 24.8, 1.0))))

# 4. Spandrel & Upper Entablature: Y from -5 to 5, X from -7.5 to 7.5, Z from 15.0 to 26.0
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 20.5))) @ Matrix.Diagonal(Vector((15.0, 10.0, 11.0, 1.0))))

# 5. Grand Central Indo-Saracenic Pointed Arch Intrados (Vault)
arch_r = 5.0
arch_spring_z = 10.5
arch_apex_z = 15.2
segs = 16
for i in range(segs):
    a1 = math.pi * (i / segs)
    a2 = math.pi * ((i + 1) / segs)
    y1 = math.cos(a1) * arch_r
    z1 = arch_spring_z + math.sin(a1) * (arch_apex_z - arch_spring_z)
    y2 = math.cos(a2) * arch_r
    z2 = arch_spring_z + math.sin(a2) * (arch_apex_z - arch_spring_z)
    
    # Vault ceiling
    v1 = bm.verts.new(Vector((-7.5, y1, z1)))
    v2 = bm.verts.new(Vector((7.5, y1, z1)))
    v3 = bm.verts.new(Vector((7.5, y2, z2)))
    v4 = bm.verts.new(Vector((-7.5, y2, z2)))
    bm.faces.new((v1, v2, v3, v4))

# 6. Side Jali Window Recesses (carved into left and right pylons)
# South side arch recess (Y = -9.5, Z = 6 to 14)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((7.6, -9.5, 10.0))) @ Matrix.Diagonal(Vector((0.4, 4.0, 8.0, 1.0))))
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-7.6, -9.5, 10.0))) @ Matrix.Diagonal(Vector((0.4, 4.0, 8.0, 1.0))))
# North side arch recess (Y = 9.5, Z = 6 to 14)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((7.6, 9.5, 10.0))) @ Matrix.Diagonal(Vector((0.4, 4.0, 8.0, 1.0))))
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((-7.6, 9.5, 10.0))) @ Matrix.Diagonal(Vector((0.4, 4.0, 8.0, 1.0))))

# 7. Projecting Eaves Chhajja (z=26.0 to 26.8, overhang=1.5m)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 26.4))) @ Matrix.Diagonal(Vector((17.5, 30.5, 0.8, 1.0))))

# 8. Perforated Jali Parapet Cresting (z=26.8 to 28.2)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector((0, 0, 27.5))) @ Matrix.Diagonal(Vector((16.8, 29.8, 1.4, 1.0))))

# 9. Four Corner Octagonal Minarets (Turrets reaching z=33m)
turret_locs = [
    Vector((-8.0, -14.5, 0)),
    Vector((8.0, -14.5, 0)),
    Vector((-8.0, 14.5, 0)),
    Vector((8.0, 14.5, 0)),
]
for tl in turret_locs:
    # Lower shaft (z=1.2 to 26.0, octagonal)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=2.2, radius2=2.0, depth=24.8, matrix=Matrix.Translation(tl + Vector((0, 0, 13.6))))
    # Cantilevered Balcony at z=26.5
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=2.7, radius2=2.4, depth=0.8, matrix=Matrix.Translation(tl + Vector((0, 0, 26.5))))
    # Domed Chhatri Pavilion (z=26.9 to 31.5)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=2.2, radius2=0.3, depth=4.6, matrix=Matrix.Translation(tl + Vector((0, 0, 29.2))))
    # Gilded Spire Finial (z=31.5 to 34.0)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.02, depth=2.5, matrix=Matrix.Translation(tl + Vector((0, 0, 32.7))))

# 10. Central Grand Ribbed Dome
# Octagonal Drum (z=27.5 to 29.8)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=6.5, radius2=6.3, depth=2.3, matrix=Matrix.Translation(Vector((0, 0, 28.6))))
# Bulbous Ribbed Dome (z=29.8 to 36.5)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=6.3, radius2=0.8, depth=6.7, matrix=Matrix.Translation(Vector((0, 0, 33.1))))
# Gilded Kalasa Finial Spire (z=36.5 to 39.5)
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.2, radius2=0.05, depth=3.0, matrix=Matrix.Translation(Vector((0, 0, 38.0))))

bm.to_mesh(gw_mesh)
bm.free()

gw_obj.data.materials.append(mat_basalt)
gw_obj.data.materials.append(mat_gold)

# Assign gold to finial peaks
for poly in gw_mesh.polygons:
    if poly.center.z > 31.5 and (poly.center.z > 36.0 or (abs(poly.center.x) > 6.0 and abs(poly.center.y) > 12.0)):
        poly.material_index = 1
    else:
        poly.material_index = 0

print("Sculpted bespoke Gateway of India.")

# ----------------------------------------------------------------------
# 3. SCULPT BESPOKE TAJ MAHAL PALACE HOTEL & TAJ TOWER
# Real Location: (94.17, -163.10, 0.0)
# ----------------------------------------------------------------------
old_taj = bpy.data.objects.get("LANDMARK_Taj_Mahal_Palace")
if old_taj:
    bpy.data.objects.remove(old_taj, do_unlink=True)

taj_mesh = bpy.data.meshes.new("LANDMARK_Taj_Mahal_Palace_Mesh")
taj_obj = bpy.data.objects.new("LANDMARK_Taj_Mahal_Palace", taj_mesh)
col_landmarks.objects.link(taj_obj)
taj_obj.location = Vector((94.17, -163.10, 0.0))

bm_t = bmesh.new()

# Symmetrical U-plan waterfront hotel:
# Central Grand Spine (facing harbour): X from -20 to -6, Y from -42 to 42, Height = 32m
bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((-13.0, 0.0, 16.0))) @ Matrix.Diagonal(Vector((14.0, 84.0, 32.0, 1.0))))

# North Projecting Wing: X from -6 to 16, Y from 28 to 42, Height = 32m
bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((5.0, 35.0, 16.0))) @ Matrix.Diagonal(Vector((22.0, 14.0, 32.0, 1.0))))

# South Projecting Wing: X from -6 to 16, Y from -42 to -28, Height = 32m
bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((5.0, -35.0, 16.0))) @ Matrix.Diagonal(Vector((22.0, 14.0, 32.0, 1.0))))

# Central Harbour Entrance Portico: X from -6 to 10, Y from -16 to 16, Height = 36m
bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 18.0))) @ Matrix.Diagonal(Vector((16.0, 32.0, 36.0, 1.0))))

# Cantilevered Arched Balconies across all 6 tiers
for tier in range(1, 6):
    tz = tier * 5.2 + 2.0
    # Central wing balconies
    bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((10.5, 0.0, tz))) @ Matrix.Diagonal(Vector((2.0, 30.0, 1.0, 1.0))))
    # North wing balconies
    bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((16.5, 35.0, tz))) @ Matrix.Diagonal(Vector((2.0, 13.0, 1.0, 1.0))))
    # South wing balconies
    bmesh.ops.create_cube(bm_t, size=1.0, matrix=Matrix.Translation(Vector((16.5, -35.0, tz))) @ Matrix.Diagonal(Vector((2.0, 13.0, 1.0, 1.0))))

# Red Mangalore Tile Pitched Mansard Roofs
# North wing roof
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.5, depth=7.0, matrix=Matrix.Translation(Vector((5.0, 35.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))
# South wing roof
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=4, radius1=9.5, radius2=0.5, depth=7.0, matrix=Matrix.Translation(Vector((5.0, -35.0, 35.5))) @ Matrix.Rotation(math.radians(45.0), 4, 'Z'))

# Iconic Central Red Florentine Ribbed Dome!
# Octagonal Arched Drum (z=36.0 to 45.0, radius=10.0m)
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=16, radius1=10.2, radius2=9.8, depth=9.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 40.5))))
# High Florentine Pointed Ribbed Dome (z=45.0 to 64.0, height=19m)
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=16, radius1=9.8, radius2=0.8, depth=19.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 54.5))))
# Gilded Lantern Cupola (z=64.0 to 71.0)
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=8, radius1=2.0, radius2=0.1, depth=7.0, matrix=Matrix.Translation(Vector((2.0, 0.0, 67.5))))

# Corner Moorish Onion-Domed Chhatris (4 corner pavilions)
chhatri_pts = [
    Vector((15.0, 41.0, 32.0)),
    Vector((15.0, -41.0, 32.0)),
    Vector((-19.0, 41.0, 32.0)),
    Vector((-19.0, -41.0, 32.0)),
]
for cp in chhatri_pts:
    bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=8, radius1=3.0, radius2=2.5, depth=3.5, matrix=Matrix.Translation(cp + Vector((0, 0, 1.75))))
    bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=8, radius1=2.5, radius2=0.3, depth=5.0, matrix=Matrix.Translation(cp + Vector((0, 0, 6.0))))
    bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=6, radius1=0.25, radius2=0.02, depth=2.5, matrix=Matrix.Translation(cp + Vector((0, 0, 9.0))))

# Adjacent 1973 Brutalist/Oriental Taj Tower (behind south wing)
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=16, radius1=16.5, radius2=16.0, depth=85.0, matrix=Matrix.Translation(Vector((-34.0, -56.0, 42.5))))
# Taj Tower crown
bmesh.ops.create_cone(bm_t, cap_ends=True, cap_tris=False, segments=16, radius1=18.0, radius2=13.0, depth=8.0, matrix=Matrix.Translation(Vector((-34.0, -56.0, 89.0))))

bm_t.to_mesh(taj_mesh)
bm_t.free()

taj_obj.data.materials.append(mat_taj)
taj_obj.data.materials.append(mat_dome)
taj_obj.data.materials.append(mat_gold)

# Assign dome and gold materials
for poly in taj_mesh.polygons:
    pz = poly.center.z
    py = poly.center.y
    px = poly.center.x
    if pz > 64.0 and abs(py) < 8.0:
        poly.material_index = 2 # Gold lantern spire
    elif pz > 43.0 and abs(py) < 14.0 and abs(px - 2.0) < 14.0:
        poly.material_index = 1 # Red Florentine Dome
    elif pz > 32.0 and (abs(py) > 28.0 or abs(px + 19.0) < 6.0):
        poly.material_index = 1 # Red roofs & corner domes
    else:
        poly.material_index = 0 # Taj facade

print("Sculpted bespoke Taj Mahal Palace & Tower.")

# ----------------------------------------------------------------------
# 4. CINEMATIC EYE-LEVEL WATERFRONT HERO CAMERA
# Place camera on harbour jetty looking at Gateway & Taj with awe
# ----------------------------------------------------------------------
cam_hero = bpy.data.objects.get("Cam_Apollo_Bandar_Hero")
if not cam_hero:
    cd = bpy.data.cameras.new("Cam_Apollo_Bandar_Hero")
    cam_hero = bpy.data.objects.new("Cam_Apollo_Bandar_Hero", cd)
    bpy.context.scene.collection.objects.link(cam_hero)

# Camera at waterfront: X=248m, Y=-85m, Z=7.5m (dramatic eye-level perspective)
cam_hero.location = Vector((248.0, -85.0, 7.5))
# Look towards Gateway at (174, -113, 16)
dx = 174.17 - 248.0
dy = -113.10 - (-85.0)
dz = 16.0 - 7.5
yaw = math.atan2(dy, dx)
dist_h = math.sqrt(dx*dx + dy*dy)
pitch = math.atan2(dz, dist_h)

cam_hero.rotation_euler = Euler((math.pi/2.0 - pitch, 0.0, yaw - math.pi/2.0), 'XYZ')
cam_hero.data.lens = 32.0 # Cinematic wide-angle prime lens
cam_hero.data.clip_end = 25000.0

# ----------------------------------------------------------------------
# 5. CALIBRATE SUN & SKY LIGHTING FOR MAXIMUM REALISM
# ----------------------------------------------------------------------
scene = bpy.context.scene
scene.camera = cam_hero

# EEVEE Next Settings
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.use_fast_gi = True
    scene.eevee.fast_gi_method = 'GLOBAL_ILLUMINATION'
    scene.eevee.fast_gi_ray_count = 8
    scene.eevee.shadow_ray_count = 8

# World Atmosphere: Sunset Nishita Sky
world = scene.world
if world and world.use_nodes:
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    w_out = nodes.new("ShaderNodeOutputWorld")
    w_bg = nodes.new("ShaderNodeBackground")
    w_bg.inputs['Strength'].default_value = 0.18 # Calibrated so it never washes out
    links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    w_sky = nodes.new("ShaderNodeTexSky")
    w_sky.sky_type = 'MULTIPLE_SCATTERING'
    w_sky.sun_elevation = math.radians(14.0) # Golden Hour Sunset
    w_sky.sun_rotation = math.radians(240.0) # West over Arabian Sea
    w_sky.air_density = 1.15
    w_sky.aerosol_density = 1.35 # Coastal haze
    w_sky.ozone_density = 1.1
    w_sky.sun_disc = True
    w_sky.sun_intensity = 1.5
    links.new(w_sky.outputs['Color'], w_bg.inputs['Color'])

# Main Sun: Warm Golden Hour Rays
sun = bpy.data.objects.get("Sun_Mumbai")
if sun:
    sun.data.energy = 5.5
    sun.data.color = (1.0, 0.86, 0.68) # Rich golden-orange
    sun.data.angle = math.radians(2.2)
    sun.rotation_euler = (math.radians(76.0), math.radians(8.0), math.radians(-120.0))

# Ambient Fill from Harbour
fill = bpy.data.objects.get("Light_Apollo_Harbour_Bounce")
if fill:
    fill.data.energy = 1.8
    fill.data.color = (0.70, 0.82, 0.96) # Reflected blue from water
    fill.rotation_euler = (math.radians(35.0), 0.0, math.radians(50.0))

# Color Management: AgX / Filmic High Contrast
if hasattr(scene, 'view_settings'):
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.2

# Save blend
bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
print("Apollo Bunder Hero Redevelopment Complete and Saved.")
