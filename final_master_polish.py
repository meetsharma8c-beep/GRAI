def main():
    import bpy, math, mathutils

    print("Executing final master polish on camera framings and PBR textures...")

    # 1. Gateway of India Basalt Texture Scale Calibration
    # Monumental stone blocks: 1.2m wide x 0.6m high
    m_basalt = bpy.data.materials.get("Mat_Yellow_Kharodi_Basalt")
    if m_basalt and m_basalt.use_nodes:
        brick = m_basalt.node_tree.nodes.get("Brick Texture")
        if brick:
            brick.inputs['Scale'].default_value = 1.0 # 1m scale instead of 16.0!
            brick.inputs['Mortar Size'].default_value = 0.03
            brick.inputs['Color1'].default_value = (0.84, 0.68, 0.44, 1.0)
            brick.inputs['Color2'].default_value = (0.76, 0.60, 0.38, 1.0)
            brick.inputs['Mortar'].default_value = (0.35, 0.30, 0.24, 1.0)
        bump = m_basalt.node_tree.nodes.get("Bump")
        if bump:
            bump.inputs['Strength'].default_value = 0.45
            bump.inputs['Distance'].default_value = 0.2

    # 2. Apollo Bunder Hero Camera - Classic Postcard Angle
    # Lower, standing on the harbour pier, looking up at Gateway and Taj Palace
    cam_apollo = bpy.data.objects.get("Cam_Apollo_Bandar_Hero")
    if cam_apollo:
        cam_apollo.location = mathutils.Vector((230.0, -95.0, 9.5))
        target = mathutils.Vector((160.0, -125.0, 15.0))
        direction = target - cam_apollo.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_apollo.rotation_euler = rot_quat.to_euler()
        cam_apollo.data.lens = 32.0

    # 3. CSMT Heritage Camera - Unobstructed Grand View
    cam_csmt = bpy.data.objects.get("Cam_CSMT_Heritage")
    if cam_csmt:
        # Move forward past the foreground roof
        # CSMT facade is at (220, 1750, 20)
        cam_csmt.location = mathutils.Vector((165.0, 1715.0, 32.0))
        target_csmt = mathutils.Vector((210.0, 1755.0, 28.0))
        direction = target_csmt - cam_csmt.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_csmt.rotation_euler = rot_quat.to_euler()
        cam_csmt.data.lens = 35.0

    # 4. Save and export clean verification renders
    renders = [
        ("Cam_Apollo_Bandar_Hero", "/tmp/final_apollo_hero.png"),
        ("Cam_MarineDrive_QueensNecklace", "/tmp/final_marine_drive.png"),
        ("Cam_SeaLink_Hero", "/tmp/final_sealink_hero.png"),
        ("Cam_CSMT_Heritage", "/tmp/final_csmt_heritage.png"),
        ("Cam_Mumbai_Overview", "/tmp/final_mumbai_overview.png")
    ]

    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.engine = 'BLENDER_EEVEE'

    for cam_name, out_path in renders:
        cam_obj = bpy.data.objects.get(cam_name)
        if cam_obj:
            scene.camera = cam_obj
            scene.render.filepath = out_path
            bpy.ops.render.render(write_still=True)
            print(f"Rendered {cam_name} -> {out_path}")

    # Save Blendfile
    bpy.ops.wm.save_mainfile(filepath="/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend")
    print("Saved master blendfile: GRAI_Mumbai_Digital_Twin.blend.")

main()
