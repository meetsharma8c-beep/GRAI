"""
Render Definitive Raghunath Mattre: Tack-Sharp Hero Portrait & Full Body
"""
import bpy
import os
import shutil
from mathutils import Vector

def main():
    scene = bpy.context.scene
    col = bpy.data.collections.get("Character_Raghunath_Mattre")
    head_obj = bpy.data.objects.get("Raghunath_Head_Mesh")
    world_origin = Vector((-1007.0, 1100.0, 7.225))

    # 1. OPTIMIZE HERO PORTRAIT CAMERA
    cam_p = bpy.data.objects.get("Cam_Raghunath_Hero_Portrait")
    cam_p.data.lens = 75.0 # Beautiful portrait focal length
    # Frame from crown of hair (Z=1.85) down to chest/shirt pocket (Z=1.35)
    portrait_target = world_origin + Vector((0.0, -0.05, 1.620))
    cam_p.location = world_origin + Vector((0.02, -1.05, 1.620))
    cam_p.rotation_euler = (portrait_target - cam_p.location).to_track_quat('-Z', 'Y').to_euler()

    # Razor-sharp focus on the face
    cam_p.data.dof.use_dof = True
    cam_p.data.dof.focus_object = head_obj
    cam_p.data.dof.aperture_fstop = 5.6 # Deep enough depth of field for full facial sharpness

    # 2. OPTIMIZE FULL BODY CAMERA
    cam_fb = bpy.data.objects.get("Cam_Raghunath_Full_Body")
    cam_fb.data.lens = 42.0
    fullbody_target = world_origin + Vector((0.0, 0.0, 0.960))
    cam_fb.location = world_origin + Vector((0.05, -3.40, 1.050))
    cam_fb.rotation_euler = (fullbody_target - cam_fb.location).to_track_quat('-Z', 'Y').to_euler()
    cam_fb.data.dof.use_dof = False # Everything sharp from hair to sandals

    # 3. RENDER SETTINGS (CYCLES METAL GPU)
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices:
        d.use = True
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.view_settings.exposure = -0.2
    scene.view_settings.look = 'High Contrast'

    artifacts_dir = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012"
    renders_dir = "/Users/ms/Downloads/GRAI/renders"

    # RENDER 1: HERO PORTRAIT
    print(">>> RENDERING TACK-SHARP MASTER PORTRAIT (1080x1920)...")
    scene.camera = cam_p
    out_p = os.path.join(renders_dir, "raghunath_mattre_hero_portrait.png")
    scene.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_p, os.path.join(artifacts_dir, "raghunath_mattre_hero_portrait.png"))
    print(f">>> MASTER PORTRAIT SAVED: {out_p}")

    # RENDER 2: FULL BODY
    print(">>> RENDERING MASTER FULL BODY (1080x1920)...")
    scene.camera = cam_fb
    out_fb = os.path.join(renders_dir, "raghunath_mattre_full_body.png")
    scene.render.filepath = out_fb
    bpy.ops.render.render(write_still=True)
    shutil.copy2(out_fb, os.path.join(artifacts_dir, "raghunath_mattre_full_body.png"))
    print(f">>> MASTER FULL BODY SAVED: {out_fb}")

    # Save master blend
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')
    print(">>> MASTER BLEND SAVED WITH FINAL RAGHUNATH MATTRE!")

if __name__ == '__main__':
    main()
