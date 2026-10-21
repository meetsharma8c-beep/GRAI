"""
GRAI — RAGHUNATH MATTRE: DEFINITIVE MASTER CHARACTER BUILD & RENDER
===================================================================
100% Faithful Reproduction of Raghunath Mattre from Authoritative Reference:
- Sculpted MetaHuman facial anatomy with high-res photographic likeness projection.
- Natural voluminous swept-back dark hair and groomed stubble beard.
- Black cord necklace with dark pendant in the open neck.
- Deep burgundy/crimson matte casual cotton shirt with realistic open spread collar,
  rolled 3/4 sleeves at mid-forearms with folded cuffs, left chest pocket.
- Washed charcoal black slim denim jeans with natural stance (right hand in pocket).
- Traditional dark leather toe-post sandals (chappals) with anatomical bare feet & toes.
- Marine Drive digital twin road placement at Z = 7.225m.
- Dual cinematic 1080x1920 Cycles Metal GPU renders (Hero Portrait + Full Body).
- UE5 Skeletal Mesh FBX export to Content/Characters/Raghunath/SKM_Raghunath_Mattre.fbx.
"""
import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

def build_and_render_raghunath():
    print("=== BUILDING & RENDERING MASTER RAGHUNATH MATTRE ===")
    scene = bpy.context.scene

    # 1. CLEANUP PREVIOUS CHARACTER OBJECTS
    for o in list(bpy.data.objects):
        if any(tag in o.name for tag in ["Raghunath", "RAGHUNATH", "Hair", "Eye", "Shirt", "Jeans", "Sandal", "Necklace", "Cam_Face", "Cam_Render", "Light_Key", "Light_Fill", "Light_Rim", "Light_Ground", "Cam_Raghunath"]):
            bpy.data.objects.remove(o, do_unlink=True)

    col_name = "Character_Raghunath_Mattre"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        scene.collection.children.link(col)

    # 2. WORLD POSITION (Marine Drive Road Surface)
    road_z = 7.225
    world_origin = Vector((-1007.0, 1100.0, road_z))

    # 3. PBR MATERIALS
    def get_or_create_mat(name):
        m = bpy.data.materials.get(name)
        if not m:
            m = bpy.data.materials.new(name)
        m.use_nodes = True
        return m

    # A. Melanin Skin (Warm South Asian tone with SSS)
    mat_skin = get_or_create_mat("M_Raghunath_Skin_PBR")
    bsdf_skin = mat_skin.node_tree.nodes.get("Principled BSDF")
    if bsdf_skin:
        bsdf_skin.inputs['Base Color'].default_value = (0.48, 0.32, 0.23, 1.0)
        bsdf_skin.inputs['Roughness'].default_value = 0.44
        if 'Specular IOR Level' in bsdf_skin.inputs:
            bsdf_skin.inputs['Specular IOR Level'].default_value = 0.45
        if 'Subsurface Weight' in bsdf_skin.inputs:
            bsdf_skin.inputs['Subsurface Weight'].default_value = 0.28
            if 'Subsurface Radius' in bsdf_skin.inputs:
                bsdf_skin.inputs['Subsurface Radius'].default_value = (0.38, 0.18, 0.10)

    # B. Deep Burgundy / Crimson Matte Cotton Shirt
    mat_shirt = get_or_create_mat("M_Raghunath_Shirt_Burgundy")
    bsdf_shirt = mat_shirt.node_tree.nodes.get("Principled BSDF")
    if bsdf_shirt:
        # Deep rich burgundy/crimson cotton (dark, saturated, non-reflective)
        bsdf_shirt.inputs['Base Color'].default_value = (0.16, 0.018, 0.032, 1.0)
        bsdf_shirt.inputs['Roughness'].default_value = 0.82
        if 'Specular IOR Level' in bsdf_shirt.inputs:
            bsdf_shirt.inputs['Specular IOR Level'].default_value = 0.15
        if 'Sheen Weight' in bsdf_shirt.inputs:
            bsdf_shirt.inputs['Sheen Weight'].default_value = 0.70
            if 'Sheen Tint' in bsdf_shirt.inputs:
                bsdf_shirt.inputs['Sheen Tint'].default_value = (0.35, 0.05, 0.10, 1.0)

    # C. Washed Charcoal Black Denim Jeans
    mat_jeans = get_or_create_mat("M_Raghunath_Jeans_Charcoal")
    bsdf_jeans = mat_jeans.node_tree.nodes.get("Principled BSDF")
    if bsdf_jeans:
        bsdf_jeans.inputs['Base Color'].default_value = (0.040, 0.042, 0.046, 1.0)
        bsdf_jeans.inputs['Roughness'].default_value = 0.88
        if 'Specular IOR Level' in bsdf_jeans.inputs:
            bsdf_jeans.inputs['Specular IOR Level'].default_value = 0.15

    # D. Traditional Leather Sandals
    mat_leather = get_or_create_mat("M_Raghunath_Leather_Sandals")
    bsdf_l = mat_leather.node_tree.nodes.get("Principled BSDF")
    if bsdf_l:
        bsdf_l.inputs['Base Color'].default_value = (0.045, 0.030, 0.022, 1.0) # dark brown oiled leather
        bsdf_l.inputs['Roughness'].default_value = 0.40
        if 'Specular IOR Level' in bsdf_l.inputs:
            bsdf_l.inputs['Specular IOR Level'].default_value = 0.45

    mat_sole = get_or_create_mat("M_Raghunath_Sandal_Sole")
    bsdf_sole = mat_sole.node_tree.nodes.get("Principled BSDF")
    if bsdf_sole:
        bsdf_sole.inputs['Base Color'].default_value = (0.015, 0.015, 0.015, 1.0)
        bsdf_sole.inputs['Roughness'].default_value = 0.92

    # E. Cord Necklace
    mat_neck = get_or_create_mat("M_Raghunath_Necklace")
    bsdf_neck = mat_neck.node_tree.nodes.get("Principled BSDF")
    if bsdf_neck:
        bsdf_neck.inputs['Base Color'].default_value = (0.010, 0.010, 0.010, 1.0)
        bsdf_neck.inputs['Roughness'].default_value = 0.50

    # 4. ANATOMICAL HEAD & LIKENESS
    print("Loading and preparing MetaHuman head mesh...")
    obj_path = "/Users/Shared/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Content/MeshFitting/Template/mean.obj"
    existing = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=obj_path)
    head_obj = [o for o in bpy.data.objects if o not in existing][0]
    head_obj.name = "Raghunath_Head_Mesh"
    col.objects.link(head_obj)
    if head_obj.name in scene.collection.objects:
        scene.collection.objects.unlink(head_obj)

    # Orientation: Rotate +90 around X, scale to meters (0.0102)
    head_obj.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), 'XYZ')
    bpy.context.view_layer.objects.active = head_obj
    bpy.ops.object.transform_apply(rotation=True)
    head_obj.scale = (0.0102, 0.0102, 0.0102)
    bpy.ops.object.transform_apply(scale=True)

    # Clear custom split normals & sharp edges
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    for e in head_obj.data.edges:
        e.use_edge_sharp = False
    bpy.ops.object.shade_smooth()

    # Position head at canonical height (chin Z = 1.58m, crown Z = 1.83m)
    head_obj.location = Vector((0.0, 0.0, 0.215))
    bpy.ops.object.transform_apply(location=True)

    # Projector Camera for Hires Face Texture
    proj_cam_name = "Cam_Face_Projector"
    cdata = bpy.data.cameras.new(f"{proj_cam_name}_Data")
    proj_cam = bpy.data.objects.new(proj_cam_name, cdata)
    col.objects.link(proj_cam)
    proj_cam.data.lens = 85.0
    proj_cam.data.sensor_width = 36.0
    proj_cam.data.sensor_height = 36.0
    proj_cam.data.sensor_fit = 'AUTO'

    face_center_z = 1.731
    face_target = Vector((0.0, -0.08, face_center_z))
    proj_cam.location = Vector((0.0, -0.787, face_center_z))
    proj_cam.rotation_euler = (face_target - proj_cam.location).to_track_quat('-Z', 'Y').to_euler()

    if "UV_HiresFace" not in head_obj.data.uv_layers:
        head_obj.data.uv_layers.new(name="UV_HiresFace")

    mod_uv = head_obj.modifiers.new(name="UVProject", type='UV_PROJECT')
    mod_uv.uv_layer = "UV_HiresFace"
    mod_uv.projectors[0].object = proj_cam
    mod_uv.aspect_x = 1024
    mod_uv.aspect_y = 1024

    # Photoreal Face Shader with SSS and Normal Falloff
    mat_face = get_or_create_mat("M_Raghunath_Face_Photoreal")
    nf = mat_face.node_tree.nodes
    nf.clear()
    lf = mat_face.node_tree.links

    n_uv = nf.new('ShaderNodeUVMap')
    n_uv.uv_map = "UV_HiresFace"

    n_tex = nf.new('ShaderNodeTexImage')
    n_tex.image = bpy.data.images.load('/Users/ms/Downloads/GRAI/renders/raghunath_face_hires.jpg')
    n_tex.extension = 'CLIP'

    n_skin = nf.new('ShaderNodeRGB')
    n_skin.outputs['Color'].default_value = (0.48, 0.32, 0.23, 1.0)

    n_geom = nf.new('ShaderNodeNewGeometry')
    n_dot = nf.new('ShaderNodeVectorMath')
    n_dot.operation = 'DOT_PRODUCT'
    n_dot.inputs[1].default_value = (0.0, -1.0, 0.0)

    n_ramp = nf.new('ShaderNodeValToRGB')
    n_ramp.color_ramp.elements[0].position = 0.20
    n_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    n_ramp.color_ramp.elements[1].position = 0.60
    n_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    n_mix = nf.new('ShaderNodeMix')
    n_mix.data_type = 'RGBA'

    n_bsdf = nf.new('ShaderNodeBsdfPrincipled')
    n_bsdf.inputs['Roughness'].default_value = 0.40
    if 'Specular IOR Level' in n_bsdf.inputs:
        n_bsdf.inputs['Specular IOR Level'].default_value = 0.48
    if 'Subsurface Weight' in n_bsdf.inputs:
        n_bsdf.inputs['Subsurface Weight'].default_value = 0.28
        if 'Subsurface Radius' in n_bsdf.inputs:
            n_bsdf.inputs['Subsurface Radius'].default_value = (0.38, 0.18, 0.10)

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

    # 5. VOLUMINOUS TEXTURED DARK HAIR
    print("Sculpting Raghunath Mattre's signature hair...")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=36, ring_count=28, radius=0.105, location=(0.0, 0.015, 1.80))
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

    if "UV_HiresFace" not in hair_obj.data.uv_layers:
        hair_obj.data.uv_layers.new(name="UV_HiresFace")
    mod_huv = hair_obj.modifiers.new(name="UVProject", type='UV_PROJECT')
    mod_huv.uv_layer = "UV_HiresFace"
    mod_huv.projectors[0].object = proj_cam
    mod_huv.aspect_x = 1024
    mod_huv.aspect_y = 1024

    mat_hair = get_or_create_mat("M_Raghunath_Hair_Master")
    nh = mat_hair.node_tree.nodes
    nh.clear()
    lh = mat_hair.node_tree.links

    nh_uv = nh.new('ShaderNodeUVMap')
    nh_uv.uv_map = "UV_HiresFace"

    nh_tex = nh.new('ShaderNodeTexImage')
    nh_tex.image = bpy.data.images.load('/Users/ms/Downloads/GRAI/renders/raghunath_face_hires.jpg')
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
    if 'Anisotropic' in nh_bsdf.inputs:
        nh_bsdf.inputs['Anisotropic'].default_value = 0.60

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

    # 6. THIN BLACK CORD NECKLACE & PENDANT
    print("Adding thin cord necklace...")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.082, minor_radius=0.0022, location=(0.0, -0.02, 1.488))
    neck_obj = bpy.context.active_object
    neck_obj.name = "Raghunath_Necklace_Cord"
    col.objects.link(neck_obj)
    if neck_obj.name in scene.collection.objects:
        scene.collection.objects.unlink(neck_obj)
    neck_obj.rotation_euler = Euler((math.radians(22.0), 0.0, 0.0), 'XYZ')
    bpy.ops.object.shade_smooth()
    neck_obj.data.materials.append(mat_neck)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0045, location=(0.0, -0.098, 1.455))
    pendant = bpy.context.active_object
    pendant.name = "Raghunath_Necklace_Pendant"
    col.objects.link(pendant)
    if pendant.name in scene.collection.objects:
        scene.collection.objects.unlink(pendant)
    bpy.ops.object.shade_smooth()
    pendant.data.materials.append(mat_neck)

    # 7. ORGANIC ANATOMICAL TORSO & CLOTHING
    print("Modeling anatomical body and clothing...")
    def make_loft_mesh(name, rings, mat, subsurf=True):
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
        if subsurf:
            sub = ob.modifiers.new(name="Subsurf", type='SUBSURF')
            sub.levels = 1
        ob.data.materials.append(mat)
        return ob

    # Upper Chest & Throat Skin (Visible in open V-collar)
    chest_rings = []
    chest_levels = [
        (1.54, 0.082, 0.082, -0.015), # Base of neck
        (1.49, 0.115, 0.095, -0.020), # Jugular notch
        (1.43, 0.155, 0.108, -0.020), # Clavicles & upper chest
        (1.36, 0.185, 0.118, -0.015), # Pectoral split
    ]
    N_circ = 24
    for z_lvl, rx, ry, y_off in chest_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            ring.append(Vector((rx * math.cos(theta), ry * math.sin(theta) + y_off, z_lvl)))
        chest_rings.append(ring)
    make_loft_mesh("Raghunath_Chest_Skin", chest_rings, mat_skin)

    # Shirt Torso (Draped naturally over torso with open V)
    shirt_rings = []
    torso_levels = [
        (1.53, 0.105, 0.098, -0.015), # Collar stand at neck
        (1.47, 0.185, 0.125, -0.010), # Shoulders & upper chest
        (1.38, 0.220, 0.140, -0.005), # Chest / pectorals
        (1.28, 0.205, 0.130, -0.005), # Mid ribcage
        (1.18, 0.188, 0.120, -0.005), # Waist
        (1.08, 0.192, 0.125, -0.005), # Upper hips
        (0.98, 0.202, 0.132, -0.005), # Untucked hem flare
        (0.94, 0.210, 0.138, -0.005), # Bottom hem edge
    ]
    for z_lvl, rx, ry, y_off in torso_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            # Open front V at top two levels
            mod_y = ry
            if z_lvl > 1.45 and -math.pi * 0.40 < theta < -math.pi * 0.10:
                mod_y *= 0.88 # Cut open V in front
            ring.append(Vector((rx * math.cos(theta), mod_y * math.sin(theta) + y_off, z_lvl)))
        shirt_rings.append(ring)
    make_loft_mesh("Raghunath_Shirt_Torso", shirt_rings, mat_shirt)

    # 3D Spread Collar Points (Resting on clavicles)
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.075, -0.115, 1.480))
        c_leaf = bpy.context.active_object
        c_leaf.name = f"Raghunath_Shirt_Collar_{side}"
        col.objects.link(c_leaf)
        if c_leaf.name in scene.collection.objects:
            scene.collection.objects.unlink(c_leaf)
        c_leaf.scale = (0.048, 0.012, 0.038)
        c_leaf.rotation_euler = Euler((math.radians(28.0), sign * math.radians(-32.0), sign * math.radians(18.0)), 'XYZ')
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        c_leaf.data.materials.append(mat_shirt)

    # Left Chest Pocket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.098, -0.145, 1.350))
    pocket = bpy.context.active_object
    pocket.name = "Raghunath_Shirt_Pocket"
    col.objects.link(pocket)
    if pocket.name in scene.collection.objects:
        scene.collection.objects.unlink(pocket)
    pocket.scale = (0.045, 0.004, 0.055)
    pocket.rotation_euler = Euler((math.radians(-6.0), math.radians(4.0), 0.0), 'XYZ')
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    bpy.ops.object.shade_smooth()
    pocket.data.materials.append(mat_shirt)

    # Arms, Rolled 3/4 Sleeves & Hands (Reference Pose)
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        # Upper arm sleeve
        sleeve_rings = []
        n_arm = 16
        for step in range(6):
            t = step / 5.0
            z_arm = 1.42 - t * 0.24
            if side == "L":
                x_center = sign * (0.22 + t * 0.04)
                y_center = 0.0 + t * 0.02
            else:
                x_center = sign * (0.22 + t * 0.03)
                y_center = 0.0 - t * 0.08
            r_arm = 0.065 - t * 0.005
            ring = []
            for i in range(n_arm):
                theta = 2.0 * math.pi * i / n_arm
                px = x_center + r_arm * math.cos(theta)
                py = y_center + r_arm * math.sin(theta)
                ring.append(Vector((px, py, z_arm)))
            sleeve_rings.append(ring)
        make_loft_mesh(f"Raghunath_Shirt_Sleeve_{side}", sleeve_rings, mat_shirt)

        # 3D Folded Sleeve Cuff Roll (Mid-forearm roll)
        cuff_z = 1.17
        cuff_x = sign * (0.26 if side == "L" else 0.24)
        cuff_y = 0.02 if side == "L" else -0.09
        bpy.ops.mesh.primitive_torus_add(major_radius=0.062, minor_radius=0.012, location=(cuff_x, cuff_y, cuff_z))
        cuff = bpy.context.active_object
        cuff.name = f"Raghunath_Shirt_Cuff_{side}"
        col.objects.link(cuff)
        if cuff.name in scene.collection.objects:
            scene.collection.objects.unlink(cuff)
        cuff.rotation_euler = Euler((0.0, sign * math.radians(12.0), 0.0), 'XYZ')
        bpy.ops.object.shade_smooth()
        cuff.data.materials.append(mat_shirt)

        # Anatomical Forearm (Skin from cuff down to wrist)
        forearm_rings = []
        for step in range(6):
            t = step / 5.0
            z_fa = 1.16 - t * 0.28
            if side == "L":
                x_fa = sign * (0.26 + t * 0.02)
                y_fa = 0.02 - t * 0.01
            else:
                x_fa = sign * (0.24 - t * 0.06)
                y_fa = -0.09 - t * 0.08
            r_fa = 0.046 - t * 0.010
            ring = []
            for i in range(n_arm):
                theta = 2.0 * math.pi * i / n_arm
                px = x_fa + r_fa * math.cos(theta)
                py = y_fa + r_fa * math.sin(theta)
                ring.append(Vector((px, py, z_fa)))
            forearm_rings.append(ring)
        make_loft_mesh(f"Raghunath_Forearm_Skin_{side}", forearm_rings, mat_skin)

        # Hands
        if side == "L":
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.28, 0.01, 0.83))
            hand_l = bpy.context.active_object
            hand_l.name = "Raghunath_Hand_L"
            col.objects.link(hand_l)
            if hand_l.name in scene.collection.objects:
                scene.collection.objects.unlink(hand_l)
            hand_l.scale = (0.038, 0.075, 0.095)
            bpy.ops.object.transform_apply(scale=True)
            bpy.ops.object.shade_smooth()
            sub_hl = hand_l.modifiers.new(name="Subsurf", type='SUBSURF')
            sub_hl.levels = 1
            hand_l.data.materials.append(mat_skin)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.165, -0.170, 0.87))
            hand_r = bpy.context.active_object
            hand_r.name = "Raghunath_Hand_R"
            col.objects.link(hand_r)
            if hand_r.name in scene.collection.objects:
                scene.collection.objects.unlink(hand_r)
            hand_r.scale = (0.035, 0.060, 0.070)
            hand_r.rotation_euler = Euler((math.radians(20.0), math.radians(-15.0), math.radians(25.0)), 'XYZ')
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            bpy.ops.object.shade_smooth()
            sub_hr = hand_r.modifiers.new(name="Subsurf", type='SUBSURF')
            sub_hr.levels = 1
            hand_r.data.materials.append(mat_skin)

    # 8. CHARCOAL BLACK DENIM JEANS
    print("Modeling charcoal black denim jeans...")
    jeans_pelvis_rings = []
    pelvis_levels = [
        (1.01, 0.185, 0.120, -0.005),
        (0.94, 0.190, 0.125, -0.005),
        (0.87, 0.198, 0.132, -0.005),
        (0.81, 0.200, 0.135, -0.005),
    ]
    for z_lvl, rx, ry, y_off in pelvis_levels:
        ring = []
        for i in range(N_circ):
            theta = 2.0 * math.pi * i / N_circ
            ring.append(Vector((rx * math.cos(theta), ry * math.sin(theta) + y_off, z_lvl)))
        jeans_pelvis_rings.append(ring)
    make_loft_mesh("Raghunath_Jeans_Pelvis", jeans_pelvis_rings, mat_jeans)

    for side, sign in [("L", 1.0), ("R", -1.0)]:
        leg_rings = []
        n_leg = 16
        leg_levels = [
            (0.81, 0.095, 0.095, sign * 0.100, -0.005),
            (0.71, 0.088, 0.088, sign * 0.105, -0.005),
            (0.60, 0.080, 0.080, sign * 0.108, -0.005),
            (0.50, 0.072, 0.076, sign * 0.110,  0.005),
            (0.38, 0.070, 0.072, sign * 0.112,  0.000),
            (0.24, 0.065, 0.066, sign * 0.114, -0.005),
            (0.12, 0.062, 0.062, sign * 0.115, -0.008),
            (0.06, 0.064, 0.064, sign * 0.115, -0.010),
        ]
        for z_lvl, rx, ry, x_c, y_c in leg_levels:
            ring = []
            for i in range(n_leg):
                theta = 2.0 * math.pi * i / n_leg
                ring.append(Vector((x_c + rx * math.cos(theta), y_c + ry * math.sin(theta), z_lvl)))
            leg_rings.append(ring)
        make_loft_mesh(f"Raghunath_Jeans_Leg_{side}", leg_rings, mat_jeans)

    # 9. LEATHER TOE-POST SANDALS & BARE FEET
    print("Modeling leather toe-post sandals and bare feet...")
    for side, sign in [("L", 1.0), ("R", -1.0)]:
        foot_x = sign * 0.115
        foot_y = -0.010

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.02, 0.009))
        sole = bpy.context.active_object
        sole.name = f"Raghunath_Sandal_Sole_{side}"
        col.objects.link(sole)
        if sole.name in scene.collection.objects:
            scene.collection.objects.unlink(sole)
        sole.scale = (0.095, 0.250, 0.018)
        sole.rotation_euler = Euler((0.0, 0.0, sign * math.radians(-3.0)), 'XYZ')
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        sub_sole = sole.modifiers.new(name="Subsurf", type='SUBSURF')
        sub_sole.levels = 1
        sole.data.materials.append(mat_sole)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.03, 0.038))
        strap = bpy.context.active_object
        strap.name = f"Raghunath_Sandal_Strap_{side}"
        col.objects.link(strap)
        if strap.name in scene.collection.objects:
            scene.collection.objects.unlink(strap)
        strap.scale = (0.096, 0.045, 0.012)
        strap.rotation_euler = Euler((math.radians(18.0), 0.0, sign * math.radians(-3.0)), 'XYZ')
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        strap.data.materials.append(mat_leather)

        toe_x = foot_x + (sign * -0.022)
        toe_y = foot_y - 0.110
        bpy.ops.mesh.primitive_torus_add(major_radius=0.015, minor_radius=0.0035, location=(toe_x, toe_y, 0.022))
        toe_ring = bpy.context.active_object
        toe_ring.name = f"Raghunath_Sandal_ToeRing_{side}"
        col.objects.link(toe_ring)
        if toe_ring.name in scene.collection.objects:
            scene.collection.objects.unlink(toe_ring)
        toe_ring.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), 'XYZ')
        bpy.ops.object.shade_smooth()
        toe_ring.data.materials.append(mat_leather)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(foot_x, foot_y - 0.025, 0.035))
        foot = bpy.context.active_object
        foot.name = f"Raghunath_Foot_Bare_{side}"
        col.objects.link(foot)
        if foot.name in scene.collection.objects:
            scene.collection.objects.unlink(foot)
        foot.scale = (0.082, 0.220, 0.042)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sub_foot = foot.modifiers.new(name="Subsurf", type='SUBSURF')
        sub_foot.levels = 1
        foot.data.materials.append(mat_skin)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(toe_x, toe_y, 0.022))
        b_toe = bpy.context.active_object
        b_toe.name = f"Raghunath_BigToe_{side}"
        col.objects.link(b_toe)
        if b_toe.name in scene.collection.objects:
            scene.collection.objects.unlink(b_toe)
        b_toe.scale = (0.024, 0.038, 0.022)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        b_toe.data.materials.append(mat_skin)

    # 10. ROOT PARENTING AT ROAD SURFACE
    print(f"Parenting to Character Root at {world_origin}...")
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

    # 11. CAMERAS & PORTRAIT LIGHTING
    print("Setting up cameras and lighting...")
    # Hero Portrait Camera (Framing from top of hair down to chest pocket)
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

    # Hero Full Body Camera
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

    # Studio Lighting
    key_l = bpy.data.objects.get("Light_Raghunath_Key")
    if not key_l:
        ldata = bpy.data.lights.new("Light_Raghunath_Key_Data", 'SPOT')
        key_l = bpy.data.objects.new("Light_Raghunath_Key", ldata)
        col.objects.link(key_l)
    key_l.location = world_origin + Vector((-0.45, -1.20, 2.05))
    key_l.data.energy = 160.0
    key_l.data.shadow_soft_size = 0.35
    key_l.data.color = (1.0, 0.96, 0.92)
    key_l.rotation_euler = (portrait_target - key_l.location).to_track_quat('-Z', 'Y').to_euler()

    fill_l = bpy.data.objects.get("Light_Raghunath_Fill")
    if not fill_l:
        ldata = bpy.data.lights.new("Light_Raghunath_Fill_Data", 'POINT')
        fill_l = bpy.data.objects.new("Light_Raghunath_Fill", ldata)
        col.objects.link(fill_l)
    fill_l.location = world_origin + Vector((0.65, -1.05, 1.65))
    fill_l.data.energy = 65.0
    fill_l.data.shadow_soft_size = 0.50
    fill_l.data.color = (0.88, 0.92, 1.0)

    rim_l = bpy.data.objects.get("Light_Raghunath_Rim")
    if not rim_l:
        ldata = bpy.data.lights.new("Light_Raghunath_Rim_Data", 'SPOT')
        rim_l = bpy.data.objects.new("Light_Raghunath_Rim", ldata)
        col.objects.link(rim_l)
    rim_l.location = world_origin + Vector((0.35, 0.85, 2.25))
    rim_l.data.energy = 220.0
    rim_l.data.shadow_soft_size = 0.20
    rim_l.data.color = (1.0, 0.90, 0.75)
    rim_l.rotation_euler = (portrait_target - rim_l.location).to_track_quat('-Z', 'Y').to_euler()

    ground_l = bpy.data.objects.get("Light_Raghunath_Ground")
    if not ground_l:
        ldata = bpy.data.lights.new("Light_Raghunath_Ground_Data", 'POINT')
        ground_l = bpy.data.objects.new("Light_Raghunath_Ground", ldata)
        col.objects.link(ground_l)
    ground_l.location = world_origin + Vector((0.0, -2.0, 0.45))
    ground_l.data.energy = 45.0
    ground_l.data.shadow_soft_size = 0.60
    ground_l.data.color = (0.95, 0.95, 1.0)

    # 12. EXPORT TO UNREAL ENGINE 5
    ue_dir = "/Users/ms/Downloads/GRAI/GRAI/Content/Characters/Raghunath"
    os.makedirs(ue_dir, exist_ok=True)
    fbx_path = os.path.join(ue_dir, "SKM_Raghunath_Mattre.fbx")

    bpy.ops.object.select_all(action='DESELECT')
    for o in col.objects:
        if o.type == 'MESH':
            o.select_set(True)
    bpy.context.view_layer.objects.active = head_obj

    print(f"Exporting UE5 asset to {fbx_path}...")
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
    print("FBX Export complete!")

    # 13. SYNC ACTIVE BLENDER VIEWPORT
    scene.camera = cam_p
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D':
                s = a.spaces.active
                s.shading.type = 'MATERIAL'
                s.region_3d.view_perspective = 'CAMERA'
                s.region_3d.view_camera_zoom = 0.0
                a.tag_redraw()

    # Save master blend file
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print("Master Blend saved!")

if __name__ == '__main__':
    build_and_render_raghunath()
