"""
GRAI — RAGHUNATH MATTRE V2: ANATOMICALLY CORRECT CHARACTER REBUILD
====================================================================
Fixes from V1:
- Seamless neck-to-head transition (no black gap)
- Proper anatomical torso proportions (not boxy/rectangular)
- Correct deep crimson/burgundy shirt color (not pink)
- Natural arm anatomy with proper shoulder-to-hand tapering
- Charcoal black jeans (not grey)
- Better body proportions overall
- Higher polygon count for smooth organic silhouette
- Cycles Metal GPU render with proper exposure/color management
"""
import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def rebuild_raghunath():
    print("=== REBUILDING RAGHUNATH MATTRE V2 — ANATOMICALLY CORRECT ===")
    blend_path = "/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend"
    if os.path.exists(blend_path) and bpy.data.filepath != blend_path:
        print(f"Loading {blend_path}...")
        bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    # 1. CLEANUP ALL PREVIOUS CHARACTER OBJECTS
    tags = ["Raghunath", "RAGHUNATH", "Hair", "Eye", "Shirt", "Jeans", "Sandal",
            "Necklace", "Cam_Face", "Cam_Render", "Light_Key", "Light_Fill",
            "Light_Rim", "Light_Ground", "Cam_Raghunath", "Chest_Skin",
            "Forearm", "Hand_", "Foot_", "BigToe", "Character_Raghunath"]
    for o in list(bpy.data.objects):
        if any(tag in o.name for tag in tags):
            bpy.data.objects.remove(o, do_unlink=True)

    # Clean orphan meshes
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)

    col_name = "Character_Raghunath_Mattre"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

    # 2. WORLD POSITION (On Marine Drive Netaji Subhash Road Surface)
    road_z = 7.238
    world_origin = Vector((-1007.0, 1100.0, road_z))

    # 3. PBR MATERIALS — CORRECTED COLORS
    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # A. Melanin Skin (Warm South Asian with SSS)
    mat_skin = get_or_create_mat("M_Raghunath_Skin_PBR")
    nt = mat_skin.node_tree
    nt.nodes.clear()
    bsdf_skin = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_skin = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_skin.outputs['BSDF'], out_skin.inputs['Surface'])
    bsdf_skin.inputs['Base Color'].default_value = (0.52, 0.34, 0.25, 1.0)
    bsdf_skin.inputs['Roughness'].default_value = 0.42
    if 'Specular IOR Level' in bsdf_skin.inputs:
        bsdf_skin.inputs['Specular IOR Level'].default_value = 0.45
    if 'Subsurface Weight' in bsdf_skin.inputs:
        bsdf_skin.inputs['Subsurface Weight'].default_value = 0.35
        if 'Subsurface Radius' in bsdf_skin.inputs:
            bsdf_skin.inputs['Subsurface Radius'].default_value = (0.42, 0.20, 0.12)

    # B. Deep Crimson/Burgundy Cotton Shirt — CORRECTED (NOT PINK!)
    mat_shirt = get_or_create_mat("M_Raghunath_Shirt_Burgundy")
    nt = mat_shirt.node_tree
    nt.nodes.clear()
    bsdf_shirt = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_shirt = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_shirt.outputs['BSDF'], out_shirt.inputs['Surface'])
    # Rich deep crimson — dark red, NOT pink, NOT bright red
    bsdf_shirt.inputs['Base Color'].default_value = (0.28, 0.025, 0.045, 1.0)
    bsdf_shirt.inputs['Roughness'].default_value = 0.80
    if 'Specular IOR Level' in bsdf_shirt.inputs:
        bsdf_shirt.inputs['Specular IOR Level'].default_value = 0.12
    if 'Sheen Weight' in bsdf_shirt.inputs:
        bsdf_shirt.inputs['Sheen Weight'].default_value = 0.60
        if 'Sheen Tint' in bsdf_shirt.inputs:
            bsdf_shirt.inputs['Sheen Tint'].default_value = (0.35, 0.05, 0.10, 1.0)

    # C. Charcoal Black Denim — CORRECTED (much darker)
    mat_jeans = get_or_create_mat("M_Raghunath_Jeans_Charcoal")
    nt = mat_jeans.node_tree
    nt.nodes.clear()
    bsdf_jeans = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_jeans = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_jeans.outputs['BSDF'], out_jeans.inputs['Surface'])
    bsdf_jeans.inputs['Base Color'].default_value = (0.022, 0.024, 0.028, 1.0)
    bsdf_jeans.inputs['Roughness'].default_value = 0.88
    if 'Specular IOR Level' in bsdf_jeans.inputs:
        bsdf_jeans.inputs['Specular IOR Level'].default_value = 0.12

    # D. Leather Sandals
    mat_leather = get_or_create_mat("M_Raghunath_Leather_Sandals")
    nt = mat_leather.node_tree
    nt.nodes.clear()
    bsdf_l = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_l = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_l.outputs['BSDF'], out_l.inputs['Surface'])
    bsdf_l.inputs['Base Color'].default_value = (0.045, 0.030, 0.022, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.40

    mat_sole = get_or_create_mat("M_Raghunath_Sandal_Sole")
    nt = mat_sole.node_tree
    nt.nodes.clear()
    bsdf_sole = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_sole = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_sole.outputs['BSDF'], out_sole.inputs['Surface'])
    bsdf_sole.inputs['Base Color'].default_value = (0.015, 0.015, 0.015, 1.0)
    bsdf_sole.inputs['Roughness'].default_value = 0.92

    # E. Cord Necklace
    mat_neck = get_or_create_mat("M_Raghunath_Necklace")
    nt = mat_neck.node_tree
    nt.nodes.clear()
    bsdf_neck = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out_neck = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf_neck.outputs['BSDF'], out_neck.inputs['Surface'])
    bsdf_neck.inputs['Base Color'].default_value = (0.010, 0.010, 0.010, 1.0)
    bsdf_neck.inputs['Roughness'].default_value = 0.50

    # ============================================================
    # 4. ANATOMICAL HEAD & LIKENESS PROJECTION
    # ============================================================
    print("Loading MetaHuman head mesh...")
    obj_path = "/Users/Shared/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Content/MeshFitting/Template/mean.obj"
    existing = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=obj_path)
    head_obj = [o for o in bpy.data.objects if o not in existing][0]
    head_obj.name = "Raghunath_Head_Mesh"
    col.objects.link(head_obj)
    if head_obj.name in scene.collection.objects:
        scene.collection.objects.unlink(head_obj)

    head_obj.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), 'XYZ')
    bpy.context.view_layer.objects.active = head_obj
    bpy.ops.object.transform_apply(rotation=True)
    head_obj.scale = (0.0102, 0.0102, 0.0102)
    bpy.ops.object.transform_apply(scale=True)

    # Clear custom normals
    try:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    except:
        pass
    for e in head_obj.data.edges:
        e.use_edge_sharp = False
    bpy.ops.object.shade_smooth()

    # Position head - chin at ~1.58m from ground, crown at ~1.83m
    head_obj.location = Vector((0.0, 0.0, 0.215))
    bpy.ops.object.transform_apply(location=True)

    # Find actual head mesh bounds for precise neck matching
    head_verts_z = [v.co.z for v in head_obj.data.vertices]
    head_bottom_z = min(head_verts_z)
    print(f"  Head mesh bottom Z: {head_bottom_z:.4f}")

    # Get head bottom ring radius for seamless neck connection
    neck_verts = [v for v in head_obj.data.vertices if v.co.z < head_bottom_z + 0.015]
    if neck_verts:
        neck_radii = [math.sqrt(v.co.x**2 + v.co.y**2) for v in neck_verts]
        head_neck_radius = max(neck_radii)
        head_neck_center_y = sum(v.co.y for v in neck_verts) / len(neck_verts)
    else:
        head_neck_radius = 0.065
        head_neck_center_y = -0.015
    print(f"  Head neck radius: {head_neck_radius:.4f}, center Y: {head_neck_center_y:.4f}")

    # Projector Camera for face texture
    proj_cam_name = "Cam_Face_Projector"
    cdata = bpy.data.cameras.new(f"{proj_cam_name}_Data")
    proj_cam = bpy.data.objects.new(proj_cam_name, cdata)
    col.objects.link(proj_cam)
    proj_cam.data.lens = 85.0
    proj_cam.data.sensor_width = 36.0

    face_center_z = 1.731
    proj_cam.location = Vector((0.0, -0.787, face_center_z))
    face_target = Vector((0.0, -0.08, face_center_z))
    proj_cam.rotation_euler = (face_target - proj_cam.location).to_track_quat('-Z', 'Y').to_euler()

    if "UV_HiresFace" not in head_obj.data.uv_layers:
        head_obj.data.uv_layers.new(name="UV_HiresFace")

    mod_uv = head_obj.modifiers.new(name="UVProject", type='UV_PROJECT')
    mod_uv.uv_layer = "UV_HiresFace"
    mod_uv.projectors[0].object = proj_cam
    mod_uv.aspect_x = 1024
    mod_uv.aspect_y = 1024

    # Photoreal Face Shader
    mat_face = get_or_create_mat("M_Raghunath_Face_Photoreal")
    nf = mat_face.node_tree.nodes
    nf.clear()
    lf = mat_face.node_tree.links

    n_uv = nf.new('ShaderNodeUVMap')
    n_uv.uv_map = "UV_HiresFace"
    n_tex = nf.new('ShaderNodeTexImage')
    face_img_path = '/Users/ms/Downloads/GRAI/renders/raghunath_face_hires.jpg'
    if os.path.exists(face_img_path):
        n_tex.image = bpy.data.images.load(face_img_path)
    n_tex.extension = 'CLIP'

    n_skin = nf.new('ShaderNodeRGB')
    n_skin.outputs['Color'].default_value = (0.52, 0.34, 0.25, 1.0)

    n_geom = nf.new('ShaderNodeNewGeometry')
    n_dot = nf.new('ShaderNodeVectorMath')
    n_dot.operation = 'DOT_PRODUCT'
    n_dot.inputs[1].default_value = (0.0, -1.0, 0.0)

    n_ramp = nf.new('ShaderNodeValToRGB')
    n_ramp.color_ramp.elements[0].position = 0.15
    n_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    n_ramp.color_ramp.elements[1].position = 0.55
    n_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    n_mix = nf.new('ShaderNodeMix')
    n_mix.data_type = 'RGBA'

    n_bsdf = nf.new('ShaderNodeBsdfPrincipled')
    n_bsdf.inputs['Roughness'].default_value = 0.40
    if 'Specular IOR Level' in n_bsdf.inputs:
        n_bsdf.inputs['Specular IOR Level'].default_value = 0.48
    if 'Subsurface Weight' in n_bsdf.inputs:
        n_bsdf.inputs['Subsurface Weight'].default_value = 0.35
        if 'Subsurface Radius' in n_bsdf.inputs:
            n_bsdf.inputs['Subsurface Radius'].default_value = (0.42, 0.20, 0.12)

    n_out = nf.new('ShaderNodeOutputMaterial')
    lf.new(n_uv.outputs['UV'], n_tex.inputs['Vector'])
    lf.new(n_geom.outputs['Normal'], n_dot.inputs[0])
    lf.new(n_dot.outputs['Value'], n_ramp.inputs['Fac'])
    lf.new(n_ramp.outputs['Color'], n_mix.inputs['Factor'])
    lf.new(n_skin.outputs['Color'], n_mix.inputs[6])
    lf.new(n_tex.outputs['Color'], n_mix.inputs[7])
    lf.new(n_mix.outputs[2], n_bsdf.inputs['Base Color'])
    lf.new(n_bsdf.outputs['BSDF'], n_out.inputs['Surface'])

    head_obj.data.materials.clear()
    head_obj.data.materials.append(mat_face)

    # ============================================================
    # 5. VOLUMINOUS DARK HAIR
    # ============================================================
    print("Sculpting hair...")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=28, radius=0.105,
                                          location=(0.0, 0.015, 1.80))
    hair_obj = bpy.context.active_object
    hair_obj.name = "Raghunath_Hair_Mesh"
    col.objects.link(hair_obj)
    if hair_obj.name in scene.collection.objects:
        scene.collection.objects.unlink(hair_obj)
    hair_obj.scale = (0.92, 1.06, 1.10)
    bpy.ops.object.transform_apply(scale=True)

    for v in hair_obj.data.vertices:
        if v.co.z > 1.77:
            h_fac = (v.co.z - 1.77) / 0.12
            v.co.y += 0.022 * h_fac
            v.co.x -= 0.016 * h_fac
            wave = math.sin(v.co.x * 45.0) * 0.005 + math.cos(v.co.y * 35.0) * 0.004
            v.co.z += wave
            v.co.x += math.sin(v.co.z * 55.0) * 0.003
        if v.co.y < -0.04 and v.co.z < 1.79:
            v.co.y += (1.79 - v.co.z) * 0.6
        if abs(v.co.x) > 0.082:
            v.co.x *= 0.92
        if v.co.y > 0.08:
            v.co.y = 0.08 + (v.co.y - 0.08) * 0.5
        if v.co.z > 1.84:
            v.co.z = 1.84 + (v.co.z - 1.84) * 0.35
        if v.co.z < 1.70:
            v.co.z = 1.70

    bpy.ops.object.shade_smooth()
    sub_hair = hair_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub_hair.levels = 1

    # Hair texture projection
    if "UV_HiresFace" not in hair_obj.data.uv_layers:
        hair_obj.data.uv_layers.new(name="UV_HiresFace")
    mod_huv = hair_obj.modifiers.new(name="UVProject", type='UV_PROJECT')
    mod_huv.uv_layer = "UV_HiresFace"
    mod_huv.projectors[0].object = proj_cam
    mod_huv.aspect_x = 1024
    mod_huv.aspect_y = 1024

    # Hair material
    mat_hair = get_or_create_mat("M_Raghunath_Hair_Master")
    nh = mat_hair.node_tree.nodes
    nh.clear()
    lh = mat_hair.node_tree.links
    nh_uv = nh.new('ShaderNodeUVMap')
    nh_uv.uv_map = "UV_HiresFace"
    nh_tex = nh.new('ShaderNodeTexImage')
    if os.path.exists(face_img_path):
        nh_tex.image = bpy.data.images.load(face_img_path)
    nh_tex.extension = 'CLIP'
    nh_dark = nh.new('ShaderNodeRGB')
    nh_dark.outputs['Color'].default_value = (0.012, 0.010, 0.009, 1.0)
    nh_geom = nh.new('ShaderNodeNewGeometry')
    nh_dot = nh.new('ShaderNodeVectorMath')
    nh_dot.operation = 'DOT_PRODUCT'
    nh_dot.inputs[1].default_value = (0.0, -1.0, 0.0)
    nh_ramp = nh.new('ShaderNodeValToRGB')
    nh_ramp.color_ramp.elements[0].position = 0.20
    nh_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    nh_ramp.color_ramp.elements[1].position = 0.60
    nh_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nh_mix = nh.new('ShaderNodeMix')
    nh_mix.data_type = 'RGBA'
    nh_bsdf = nh.new('ShaderNodeBsdfPrincipled')
    nh_bsdf.inputs['Roughness'].default_value = 0.45
    if 'Specular IOR Level' in nh_bsdf.inputs:
        nh_bsdf.inputs['Specular IOR Level'].default_value = 0.65
    nh_out = nh.new('ShaderNodeOutputMaterial')
    lh.new(nh_uv.outputs['UV'], nh_tex.inputs['Vector'])
    lh.new(nh_geom.outputs['Normal'], nh_dot.inputs[0])
    lh.new(nh_dot.outputs['Value'], nh_ramp.inputs['Fac'])
    lh.new(nh_ramp.outputs['Color'], nh_mix.inputs['Factor'])
    lh.new(nh_dark.outputs['Color'], nh_mix.inputs[6])
    lh.new(nh_tex.outputs['Color'], nh_mix.inputs[7])
    lh.new(nh_mix.outputs[2], nh_bsdf.inputs['Base Color'])
    lh.new(nh_bsdf.outputs['BSDF'], nh_out.inputs['Surface'])
    hair_obj.data.materials.clear()
    hair_obj.data.materials.append(mat_hair)

    # ============================================================
    # 6. LOFT MESH HELPER (Higher resolution)
    # ============================================================
    def make_loft_mesh(name, rings, mat, subsurf_level=2):
        me = bpy.data.meshes.new(f"{name}_Mesh")
        ob = bpy.data.objects.new(name, me)
        col.objects.link(ob)
        bm = bmesh.new()
        grid = []
        for ring in rings:
            row = [bm.verts.new(pt) for pt in ring]
            grid.append(row)
        for r in range(len(grid) - 1):
            N = len(grid[r])
            for i in range(N):
                next_i = (i + 1) % N
                bm.faces.new([grid[r][i], grid[r][next_i], grid[r+1][next_i], grid[r+1][i]])
        bm.to_mesh(me)
        bm.free()
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.shade_smooth()
        if subsurf_level > 0:
            sub = ob.modifiers.new(name="Subsurf", type='SUBSURF')
            sub.levels = subsurf_level
            sub.render_levels = subsurf_level
        ob.data.materials.append(mat)
        return ob

    N_circ = 32  # Higher res circles for smoother silhouette

    # ============================================================
    # 7. SEAMLESS NECK & UPPER CHEST SKIN
    # ============================================================
    print("Building seamless neck-to-body transition...")
    # Match the head bottom exactly to create seamless skin connection
    neck_top_z = head_bottom_z + 0.003  # Slight overlap with head mesh
    neck_rx = head_neck_radius * 1.02   # Slight overlap
    neck_ry = head_neck_radius * 0.90

    neck_skin_rings = []
    neck_levels = [
        # (z, rx, ry, y_offset) — seamless from head bottom down to collar
        (neck_top_z, neck_rx, neck_ry, head_neck_center_y),
        (neck_top_z - 0.015, neck_rx * 1.02, neck_ry * 1.02, head_neck_center_y - 0.003),
        (neck_top_z - 0.035, neck_rx * 1.05, neck_ry * 1.04, head_neck_center_y - 0.006),
        (neck_top_z - 0.055, neck_rx * 1.10, neck_ry * 1.08, head_neck_center_y - 0.008),
        (1.54, 0.085, 0.078, -0.015),  # Base of neck
        (1.49, 0.118, 0.098, -0.018),  # Jugular notch
        (1.44, 0.148, 0.108, -0.018),  # Clavicles
        (1.38, 0.175, 0.115, -0.015),  # Upper pectorals
        (1.34, 0.190, 0.120, -0.012),  # Pectoral muscle
    ]
    for z_lvl, rx, ry, y_off in neck_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            ring.append(Vector((rx * math.cos(theta), ry * math.sin(theta) + y_off, z_lvl)))
        neck_skin_rings.append(ring)
    make_loft_mesh("Raghunath_Neck_Chest_Skin", neck_skin_rings, mat_skin, subsurf_level=2)

    # ============================================================
    # 8. SHIRT TORSO — ANATOMICAL FIT (not boxy)
    # ============================================================
    print("Modeling fitted shirt torso...")
    shirt_rings = []
    # Organic elliptical cross-sections with natural body taper
    torso_levels = [
        # (z, front_rx, side_ry, y_offset)
        # Collar stand
        (1.52, 0.108, 0.098, -0.012),
        # Shoulder yoke
        (1.48, 0.178, 0.118, -0.008),
        # Armpit line
        (1.42, 0.200, 0.130, -0.005),
        # Upper chest
        (1.36, 0.208, 0.138, -0.005),
        # Chest / nipple line
        (1.30, 0.200, 0.135, -0.005),
        # Lower ribcage
        (1.22, 0.188, 0.125, -0.005),
        # Natural waist
        (1.14, 0.175, 0.118, -0.005),
        # Low waist / belt line
        (1.06, 0.178, 0.120, -0.005),
        # Hip zone where shirt hangs
        (0.99, 0.185, 0.128, -0.005),
        # Bottom hem — slight flare for untucked casual
        (0.94, 0.195, 0.135, -0.005),
        (0.91, 0.200, 0.140, -0.005),
    ]
    for z_lvl, rx, ry, y_off in torso_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            x = rx * math.cos(theta)
            y = ry * math.sin(theta) + y_off
            # Flatten back slightly, round front
            if y > 0:
                y *= 0.92  # Less depth at back
            ring.append(Vector((x, y, z_lvl)))
        shirt_rings.append(ring)
    make_loft_mesh("Raghunath_Shirt_Torso", shirt_rings, mat_shirt, subsurf_level=2)

    # Collar points
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.068, -0.110, 1.485))
        c_leaf = bpy.context.active_object
        c_leaf.name = f"Raghunath_Collar_{side}"
        col.objects.link(c_leaf)
        if c_leaf.name in scene.collection.objects:
            scene.collection.objects.unlink(c_leaf)
        c_leaf.scale = (0.042, 0.010, 0.035)
        c_leaf.rotation_euler = Euler((math.radians(26.0), sign * math.radians(-30.0), sign * math.radians(16.0)), 'XYZ')
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        c_leaf.data.materials.append(mat_shirt)

    # Chest pocket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.095, -0.140, 1.345))
    pocket = bpy.context.active_object
    pocket.name = "Raghunath_Shirt_Pocket"
    col.objects.link(pocket)
    if pocket.name in scene.collection.objects:
        scene.collection.objects.unlink(pocket)
    pocket.scale = (0.042, 0.004, 0.050)
    pocket.rotation_euler = Euler((math.radians(-6.0), math.radians(4.0), 0.0), 'XYZ')
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    pocket.data.materials.append(mat_shirt)

    # ============================================================
    # 9. ARMS WITH NATURAL ANATOMY
    # ============================================================
    print("Building anatomical arms...")
    n_arm = 20  # Higher res arm cross-sections

    for side, sign in [("L", 1.0), ("R", -1.0)]:
        # Sleeve: shoulder cap down to mid-forearm
        sleeve_rings = []
        sleeve_levels = [
            # (z, x_center, y_center, radius_x, radius_y) — elliptical for organic shape
            (1.44, sign * 0.195, -0.005, 0.060, 0.058),  # Shoulder cap
            (1.40, sign * 0.215, -0.005, 0.072, 0.068),  # Deltoid
            (1.36, sign * 0.225, -0.005, 0.070, 0.066),  # Upper arm
            (1.30, sign * 0.232, -0.005, 0.065, 0.062),  # Bicep
            (1.24, sign * 0.238, -0.008, 0.060, 0.058),  # Mid upper arm
            (1.20, sign * 0.242, -0.010, 0.058, 0.056),  # Rolled sleeve end
            (1.17, sign * 0.244, -0.012, 0.062, 0.060),  # Cuff roll (slightly larger)
        ]
        for z_lvl, xc, yc, rx_a, ry_a in sleeve_levels:
            ring = []
            for i in range(n_arm):
                theta = 2.0 * math.pi * i / n_arm
                px = xc + rx_a * math.cos(theta)
                py = yc + ry_a * math.sin(theta)
                ring.append(Vector((px, py, z_lvl)))
            sleeve_rings.append(ring)
        make_loft_mesh(f"Raghunath_Sleeve_{side}", sleeve_rings, mat_shirt, subsurf_level=2)

        # Rolled cuff torus
        cuff_z = 1.17
        cuff_x = sign * 0.244
        bpy.ops.mesh.primitive_torus_add(major_radius=0.058, minor_radius=0.010,
                                          location=(cuff_x, -0.012, cuff_z))
        cuff = bpy.context.active_object
        cuff.name = f"Raghunath_Cuff_{side}"
        col.objects.link(cuff)
        if cuff.name in scene.collection.objects:
            scene.collection.objects.unlink(cuff)
        bpy.ops.object.shade_smooth()
        cuff.data.materials.append(mat_shirt)

        # Anatomical forearm (skin from cuff to wrist)
        forearm_rings = []
        forearm_levels = [
            (1.16, sign * 0.245, -0.012, 0.050, 0.048),
            (1.10, sign * 0.248, -0.015, 0.046, 0.044),
            (1.02, sign * 0.252, -0.018, 0.042, 0.040),
            (0.95, sign * 0.255, -0.020, 0.038, 0.036),
            (0.90, sign * 0.257, -0.022, 0.035, 0.034),
            (0.86, sign * 0.258, -0.024, 0.032, 0.032),
        ]
        for z_lvl, xc, yc, rx_a, ry_a in forearm_levels:
            ring = []
            for i in range(n_arm):
                theta = 2.0 * math.pi * i / n_arm
                px = xc + rx_a * math.cos(theta)
                py = yc + ry_a * math.sin(theta)
                ring.append(Vector((px, py, z_lvl)))
            forearm_rings.append(ring)
        make_loft_mesh(f"Raghunath_Forearm_{side}", forearm_rings, mat_skin, subsurf_level=2)

        # Hands (relaxed at sides)
        hand_z = 0.82
        hand_x = sign * 0.260
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hand_x, -0.028, hand_z))
        hand = bpy.context.active_object
        hand.name = f"Raghunath_Hand_{side}"
        col.objects.link(hand)
        if hand.name in scene.collection.objects:
            scene.collection.objects.unlink(hand)
        hand.scale = (0.032, 0.018, 0.085)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sub_h = hand.modifiers.new(name="Subsurf", type='SUBSURF')
        sub_h.levels = 2
        hand.data.materials.append(mat_skin)

    # ============================================================
    # 10. NECKLACE
    # ============================================================
    print("Adding necklace...")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.078, minor_radius=0.0020,
                                      location=(0.0, -0.020, 1.492))
    neck_cord = bpy.context.active_object
    neck_cord.name = "Raghunath_Necklace_Cord"
    col.objects.link(neck_cord)
    if neck_cord.name in scene.collection.objects:
        scene.collection.objects.unlink(neck_cord)
    neck_cord.rotation_euler = Euler((math.radians(22.0), 0.0, 0.0), 'XYZ')
    bpy.ops.object.shade_smooth()
    neck_cord.data.materials.append(mat_neck)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0042, location=(0.0, -0.095, 1.460))
    pendant = bpy.context.active_object
    pendant.name = "Raghunath_Pendant"
    col.objects.link(pendant)
    if pendant.name in scene.collection.objects:
        scene.collection.objects.unlink(pendant)
    bpy.ops.object.shade_smooth()
    pendant.data.materials.append(mat_neck)

    # ============================================================
    # 11. CHARCOAL BLACK DENIM JEANS
    # ============================================================
    print("Modeling jeans...")
    # Pelvis/waist section
    jeans_pelvis_rings = []
    pelvis_levels = [
        (1.01, 0.180, 0.118, -0.005),
        (0.96, 0.185, 0.122, -0.005),
        (0.91, 0.192, 0.128, -0.005),
        (0.86, 0.198, 0.132, -0.005),
        (0.81, 0.200, 0.135, -0.005),
    ]
    for z_lvl, rx, ry, y_off in pelvis_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            ring.append(Vector((rx * math.cos(theta), ry * math.sin(theta) + y_off, z_lvl)))
        jeans_pelvis_rings.append(ring)
    make_loft_mesh("Raghunath_Jeans_Pelvis", jeans_pelvis_rings, mat_jeans, subsurf_level=2)

    # Individual legs
    n_leg = 20
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_rings = []
        leg_levels = [
            # (z, rx, ry, x_center, y_center)
            (0.82, 0.092, 0.092, sign * 0.100, -0.005),
            (0.74, 0.085, 0.085, sign * 0.103, -0.005),
            (0.65, 0.078, 0.080, sign * 0.105, -0.003),
            (0.56, 0.072, 0.075, sign * 0.107, 0.000),
            (0.46, 0.068, 0.072, sign * 0.108, 0.000),
            (0.36, 0.066, 0.068, sign * 0.110, -0.002),
            (0.26, 0.064, 0.066, sign * 0.112, -0.004),
            (0.18, 0.062, 0.064, sign * 0.113, -0.006),
            (0.10, 0.061, 0.062, sign * 0.114, -0.008),
            (0.06, 0.063, 0.063, sign * 0.114, -0.010),  # Slight cuff flare
        ]
        for z_lvl, rx, ry, xc, yc in leg_levels:
            ring = []
            for i in range(n_leg):
                theta = 2.0 * math.pi * i / n_leg
                ring.append(Vector((xc + rx * math.cos(theta), yc + ry * math.sin(theta), z_lvl)))
            leg_rings.append(ring)
        make_loft_mesh(f"Raghunath_Jeans_Leg_{side}", leg_rings, mat_jeans, subsurf_level=2)

    # ============================================================
    # 12. SANDALS & BARE FEET
    # ============================================================
    print("Modeling sandals and feet...")
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        foot_x = sign * 0.114
        foot_y = -0.010

        # Sole
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.02, 0.009))
        sole = bpy.context.active_object
        sole.name = f"Raghunath_Sole_{side}"
        col.objects.link(sole)
        if sole.name in scene.collection.objects:
            scene.collection.objects.unlink(sole)
        sole.scale = (0.090, 0.240, 0.016)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sub_sole = sole.modifiers.new(name="Subsurf", type='SUBSURF')
        sub_sole.levels = 1
        sole.data.materials.append(mat_sole)

        # Strap
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.03, 0.036))
        strap = bpy.context.active_object
        strap.name = f"Raghunath_Strap_{side}"
        col.objects.link(strap)
        if strap.name in scene.collection.objects:
            scene.collection.objects.unlink(strap)
        strap.scale = (0.090, 0.042, 0.010)
        strap.rotation_euler = Euler((math.radians(16.0), 0.0, 0.0), 'XYZ')
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        strap.data.materials.append(mat_leather)

        # Toe ring
        toe_x = foot_x + (sign * -0.020)
        toe_y = foot_y - 0.105
        bpy.ops.mesh.primitive_torus_add(major_radius=0.014, minor_radius=0.0032,
                                          location=(toe_x, toe_y, 0.020))
        toe_ring = bpy.context.active_object
        toe_ring.name = f"Raghunath_ToeRing_{side}"
        col.objects.link(toe_ring)
        if toe_ring.name in scene.collection.objects:
            scene.collection.objects.unlink(toe_ring)
        toe_ring.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), 'XYZ')
        bpy.ops.object.shade_smooth()
        toe_ring.data.materials.append(mat_leather)

        # Bare foot
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.025, 0.032))
        foot = bpy.context.active_object
        foot.name = f"Raghunath_Foot_{side}"
        col.objects.link(foot)
        if foot.name in scene.collection.objects:
            scene.collection.objects.unlink(foot)
        foot.scale = (0.078, 0.215, 0.038)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sub_f = foot.modifiers.new(name="Subsurf", type='SUBSURF')
        sub_f.levels = 1
        foot.data.materials.append(mat_skin)

    # ============================================================
    # 13. ROOT PARENTING
    # ============================================================
    print(f"Parenting to root at {world_origin}...")
    char_objects = [o for o in col.objects if "Cam_" not in o.name and "Light_" not in o.name]
    root_name = "Character_Raghunath_Root"
    root_empty = bpy.data.objects.get(root_name)
    if not root_empty:
        root_empty = bpy.data.objects.new(root_name, None)
        root_empty.empty_display_type = 'ARROWS'
        col.objects.link(root_empty)
    root_empty.location = world_origin

    for o in char_objects:
        if o != root_empty:
            o.parent = root_empty
    proj_cam.parent = root_empty

    # ============================================================
    # 14. CAMERAS & STUDIO LIGHTING
    # ============================================================
    print("Setting up cameras and studio lighting...")

    # Hero Portrait Camera
    cam_p = bpy.data.objects.get("Cam_Raghunath_Hero_Portrait")
    if not cam_p:
        cdata = bpy.data.cameras.new("Cam_Raghunath_Hero_Portrait_Data")
        cam_p = bpy.data.objects.new("Cam_Raghunath_Hero_Portrait", cdata)
        col.objects.link(cam_p)
    cam_p.data.lens = 72.0
    cam_p.data.clip_start = 0.1
    cam_p.data.clip_end = 25000.0
    cam_p.data.dof.use_dof = True
    cam_p.data.dof.focus_object = head_obj
    cam_p.data.dof.aperture_fstop = 5.6

    portrait_target = world_origin + Vector((0.0, -0.05, 1.620))
    cam_p.location = world_origin + Vector((0.02, -1.05, 1.620))
    cam_p.rotation_euler = (portrait_target - cam_p.location).to_track_quat('-Z', 'Y').to_euler()

    # Full Body Camera
    cam_fb = bpy.data.objects.get("Cam_Raghunath_Full_Body")
    if not cam_fb:
        cdata = bpy.data.cameras.new("Cam_Raghunath_Full_Body_Data")
        cam_fb = bpy.data.objects.new("Cam_Raghunath_Full_Body", cdata)
        col.objects.link(cam_fb)
    cam_fb.data.lens = 42.0
    cam_fb.data.clip_start = 0.1
    cam_fb.data.clip_end = 25000.0
    cam_fb.data.dof.use_dof = False

    fullbody_target = world_origin + Vector((0.0, 0.0, 0.960))
    cam_fb.location = world_origin + Vector((0.05, -3.40, 1.050))
    cam_fb.rotation_euler = (fullbody_target - cam_fb.location).to_track_quat('-Z', 'Y').to_euler()

    # Cinematic Street Camera (Wide 38mm view on Marine Drive)
    cam_street = bpy.data.objects.get("Cam_Raghunath_Cinematic_Street")
    if not cam_street:
        cdata = bpy.data.cameras.new("Cam_Raghunath_Cinematic_Street_Data")
        cam_street = bpy.data.objects.new("Cam_Raghunath_Cinematic_Street", cdata)
        col.objects.link(cam_street)
    cam_street.data.lens = 38.0
    cam_street.data.clip_start = 0.1
    cam_street.data.clip_end = 25000.0
    cam_street.data.dof.use_dof = True
    cam_street.data.dof.focus_object = head_obj
    cam_street.data.dof.aperture_fstop = 2.8
    street_target = world_origin + Vector((0.0, 0.0, 1.350))
    cam_street.location = world_origin + Vector((1.35, -2.60, 1.500))
    cam_street.rotation_euler = (street_target - cam_street.location).to_track_quat('-Z', 'Y').to_euler()

    # 4-Point Studio Lighting
    def create_light(name, light_type, location, energy, color, soft_size, target=None):
        l = bpy.data.objects.get(name)
        if not l:
            ldata = bpy.data.lights.new(f"{name}_Data", light_type)
            l = bpy.data.objects.new(name, ldata)
            col.objects.link(l)
        l.location = location
        l.data.energy = energy
        l.data.shadow_soft_size = soft_size
        l.data.color = color
        if target:
            l.rotation_euler = (target - location).to_track_quat('-Z', 'Y').to_euler()
        return l

    create_light("Light_Raghunath_Key", 'SPOT',
                 world_origin + Vector((-0.45, -1.20, 2.05)),
                 200.0, (1.0, 0.96, 0.92), 0.35, portrait_target)
    create_light("Light_Raghunath_Fill", 'POINT',
                 world_origin + Vector((0.65, -1.05, 1.65)),
                 80.0, (0.88, 0.92, 1.0), 0.50)
    create_light("Light_Raghunath_Rim", 'SPOT',
                 world_origin + Vector((0.35, 0.85, 2.25)),
                 260.0, (1.0, 0.90, 0.75), 0.20, portrait_target)
    create_light("Light_Raghunath_Ground", 'POINT',
                 world_origin + Vector((0.0, -2.0, 0.45)),
                 55.0, (0.95, 0.95, 1.0), 0.60)

    # ============================================================
    # 15. CYCLES METAL GPU RENDERING
    # ============================================================
    print("Configuring Cycles Metal GPU rendering...")
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons.get('cycles')
    if prefs:
        prefs.preferences.compute_device_type = 'METAL'
        prefs.preferences.get_devices()
        for d in prefs.preferences.devices:
            d.use = True
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'

    # Color management — CORRECTED to prevent washed out/pink colors
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = -0.3  # Slightly lower to preserve dark rich colors
    scene.view_settings.gamma = 1.0

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_depth = '16'
    scene.render.image_settings.compression = 15

    out_dir = "/Users/ms/Downloads/GRAI/renders"
    os.makedirs(out_dir, exist_ok=True)
    brain_renders = "/Users/ms/.gemini/antigravity-ide/brain/c8431605-a131-4036-979c-c27954fd5f10/renders"
    os.makedirs(brain_renders, exist_ok=True)
    import shutil

    # Render 1: Hero Portrait
    print("Rendering hero portrait...")
    scene.camera = cam_p
    p_path = os.path.join(out_dir, "raghunath_mattre_hero_portrait.png")
    scene.render.filepath = p_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(p_path, os.path.join(brain_renders, "raghunath_mattre_hero_portrait.png"))
    print("  Hero portrait saved!")

    # Render 2: Full Body
    print("Rendering full body...")
    scene.camera = cam_fb
    fb_path = os.path.join(out_dir, "raghunath_mattre_full_body.png")
    scene.render.filepath = fb_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(fb_path, os.path.join(brain_renders, "raghunath_mattre_full_body.png"))
    print("  Full body saved!")

    # Render 3: Cinematic Marine Drive Street Context
    print("Rendering cinematic street shot...")
    scene.camera = cam_street
    street_path = os.path.join(out_dir, "raghunath_mattre_cinematic_street.png")
    scene.render.filepath = street_path
    bpy.ops.render.render(write_still=True)
    shutil.copy2(street_path, os.path.join(brain_renders, "raghunath_mattre_cinematic_street.png"))
    print("  Cinematic street shot saved!")

    # ============================================================
    # 16. EXPORT UE5 FBX
    # ============================================================
    ue_dir = "/Users/ms/Downloads/GRAI/GRAI/Content/Characters/Raghunath"
    os.makedirs(ue_dir, exist_ok=True)
    fbx_path = os.path.join(ue_dir, "SKM_Raghunath_Mattre.fbx")

    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:
        if o.type == 'MESH':
            o.select_set(True)
    bpy.context.view_layer.objects.active = head_obj

    print(f"Exporting UE5 FBX to {fbx_path}...")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        object_types={'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE'
    )
    print("FBX export complete!")

    # Sync viewport
    scene.camera = cam_p
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'MATERIAL'
                s.region_3d.view_perspective = 'CAMERA'
                a.tag_redraw()

    # Save blend
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("=== RAGHUNATH MATTRE V2 COMPLETE ===")

if __name__ == '__main__':
    rebuild_raghunath()
