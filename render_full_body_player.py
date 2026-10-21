"""
Render Full-Body Action Hero Shots of the Player ("Me") on Marine Drive Road
============================================================================
1. Cam_Player_FullBody_FrontThreeQuarter:
   - Dynamic 3/4 cinematic action angle capturing full body (running sneakers, fitted joggers,
     bomber jacket, flexed arms, styled hair, face) jogging forward on the asphalt carriageway.
   - Background: Sweeping curve of Marine Drive, Queen's necklace street lamps, and twilight sky.
2. Cam_Player_ThirdPerson_Gameplay:
   - Iconic over-the-shoulder third-person open-world gameplay camera tracking the player.
"""
import bpy
import math
from mathutils import Vector

def render_full_body_player():
    print("=== CONFIGURING FULL BODY HERO PLAYER RENDERS ===")
    scene = bpy.context.scene

    # Focus target and root
    focus = bpy.data.objects.get("HUMAN_Focus_Target")
    root = bpy.data.objects.get("HUMAN_Root")

    # Set frame to frame 48 (dynamic stride phase with high knee and pumped arms)
    scene.frame_set(48)
    px, py, pz = root.matrix_world.translation if root else (-1007.0, 1100.0, 7.35)

    # 1. Full Body Front Three-Quarter Camera
    cam1_name = "Cam_Player_FullBody_Action"
    cam1 = bpy.data.objects.get(cam1_name)
    if not cam1:
        cdata = bpy.data.cameras.new(f"{cam1_name}_Data")
        cam1 = bpy.data.objects.new(cam1_name, cdata)
        bpy.context.scene.collection.objects.link(cam1)

    cam1.data.lens = 35.0 # 35mm wide cinematic action lens
    cam1.data.clip_start = 0.1
    cam1.data.clip_end = 25000.0
    cam1.data.dof.use_dof = True
    if focus:
        cam1.data.dof.focus_object = focus
    cam1.data.dof.aperture_fstop = 3.5

    # Position camera 4.5m ahead and 1.8m to the right (three-quarter view), low angle looking slightly up
    cam1.location = Vector((px + 1.60, py + 4.20, pz + 0.85))
    target1 = Vector((px, py, pz + 0.95))
    cam1.rotation_euler = (target1 - cam1.location).to_track_quat('-Z', 'Y').to_euler()

    # 2. Third-Person Over-The-Shoulder Camera
    cam2_name = "Cam_Player_ThirdPerson_Road"
    cam2 = bpy.data.objects.get(cam2_name)
    if not cam2:
        cdata = bpy.data.cameras.new(f"{cam2_name}_Data")
        cam2 = bpy.data.objects.new(cam2_name, cdata)
        bpy.context.scene.collection.objects.link(cam2)

    cam2.data.lens = 32.0
    cam2.data.clip_start = 0.1
    cam2.data.clip_end = 25000.0
    cam2.data.dof.use_dof = True
    if focus:
        cam2.data.dof.focus_object = focus
    cam2.data.dof.aperture_fstop = 4.0

    # Position camera 3.6m behind and slightly right (over right shoulder)
    cam2.location = Vector((px + 0.55, py - 3.40, pz + 1.65))
    target2 = Vector((px, py + 8.0, pz + 1.40))
    cam2.rotation_euler = (target2 - cam2.location).to_track_quat('-Z', 'Y').to_euler()

    # Render settings: Cycles Metal GPU
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True

    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.exposure = -0.75
    scene.view_settings.look = 'High Contrast'

    # Render View 1: Full Body Front Three-Quarter Action Shot
    scene.camera = cam1
    out1 = "/Users/ms/Downloads/GRAI/renders/hero_player_full_body_action.png"
    art1 = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/hero_player_full_body_action.png"
    scene.render.filepath = out1
    print("Rendering Full-Body Action Hero shot...")
    bpy.ops.render.render(write_still=True)

    # Render View 2: Over-The-Shoulder Third-Person View
    scene.camera = cam2
    out2 = "/Users/ms/Downloads/GRAI/renders/hero_player_third_person_road.png"
    art2 = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/hero_player_third_person_road.png"
    scene.render.filepath = out2
    print("Rendering Over-The-Shoulder Third-Person shot...")
    bpy.ops.render.render(write_still=True)

    # Copy to artifacts
    import shutil
    shutil.copy2(out1, art1)
    shutil.copy2(out2, art2)
    print("Copied both master renders to IDE artifacts!")

    # Save blendfile with full-body action camera active
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')

if __name__ == '__main__':
    render_full_body_player()
