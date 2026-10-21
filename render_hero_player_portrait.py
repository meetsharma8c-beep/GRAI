"""
Render Master Hero Cinematic Shot of the Player ("Me") on Marine Drive Road
===========================================================================
- 50mm cinematic portrait lens with shallow depth of field (f/2.8 bokeh).
- Camera framed directly on the protagonist jogging on Netaji Subhash Road.
- Tack-sharp facial features, hair, athletic bomber jacket, running joggers, and sneakers.
- Golden-hour rim light and Arabian Sea twilight sunset in the background.
- Rendered in Full HD 1920x1080 with Cycles Metal GPU Path Tracing.
"""
import bpy
import math
from mathutils import Vector

def render_hero_player():
    print("=== CONFIGURING HERO PLAYER CINEMATIC SHOT ===")
    scene = bpy.context.scene

    # Character focus target
    focus = bpy.data.objects.get("HUMAN_Focus_Target")
    root = bpy.data.objects.get("HUMAN_Root")

    # Set frame to frame 48 (athletic jogging forward stance)
    scene.frame_set(48)

    # Create Hero Portrait Camera
    cam_name = "Cam_Hero_Player_CloseUp"
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        cdata = bpy.data.cameras.new(f"{cam_name}_Data")
        cam = bpy.data.objects.new(cam_name, cdata)
        bpy.context.scene.collection.objects.link(cam)

    cam.data.lens = 45.0 # 45mm cinematic portrait lens
    cam.data.clip_start = 0.1
    cam.data.clip_end = 25000.0
    cam.data.dof.use_dof = True
    if focus:
        cam.data.dof.focus_object = focus
    cam.data.dof.aperture_fstop = 2.8 # Creamy cinematic background blur

    # Position camera in front of the jogging player on Netaji Subhash Road
    # Player is at Y ~ 1100, camera at Y ~ 1103.8 (3.8m in front, head-height)
    if root:
        px, py, pz = root.matrix_world.translation
        cam.location = Vector((px + 0.15, py + 3.40, pz + 1.42))
        target = Vector((px, py, pz + 1.30))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

    scene.camera = cam

    # Cycles Metal GPU settings
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True

    scene.cycles.samples = 36 # High sample count for pristine face/skin detail
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.exposure = -0.75
    scene.view_settings.look = 'High Contrast'

    out_path = "/Users/ms/Downloads/GRAI/renders/hero_player_cinematic_render.png"
    artifact_path = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/hero_player_cinematic_render.png"
    scene.render.filepath = out_path

    print(f"Rendering Hero Player portrait to {out_path}...")
    bpy.ops.render.render(write_still=True)
    print("Render complete!")

    # Copy to artifacts
    import shutil
    shutil.copy2(out_path, artifact_path)
    print(f"Copied to artifact path: {artifact_path}")

    # Also save master blendfile with this camera active
    bpy.ops.wm.save_as_mainfile(filepath='/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend')

if __name__ == '__main__':
    render_hero_player()
