"""
Master Production Drone View Render: Whole Mumbai Peninsula Digital Twin
========================================================================
- True photorealistic Cycles Metal GPU Path Tracing on Apple Silicon M5.
- Fixed terrain shader (eliminated rainbow noise, applied realistic dark asphalt & parkland greens).
- Shimmering Arabian Sea with physical dielectric water, wave normal bump, and volume absorption.
- Glowing Queen's Necklace 277 amber luminaires twinkling along the entire 3.6km coastal crescent.
- Nariman Point modern glass towers, Marine Drive Art Deco blocks, and Bandra-Worli Sea Link.
- Rendered in Full HD 1920x1080 with AgX/Filmic High Contrast color grading.
"""
import bpy
import math
from mathutils import Vector

def setup_master_drone_render():
    print("=== CONFIGURING MASTER DRONE SCENE ===")
    scene = bpy.context.scene

    # 1. Hide all untextured proxy objects
    for name in ["Terrain_envelope", "GEO_ORIGIN_GATEWAY_OF_INDIA", "PLAYER_SPAWN_MARINEDRIVE"]:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True

    # 2. Perfect Terrain PBR Shader (Asphalt + Parkland Greens)
    tm = bpy.data.materials.get("MAT_Mumbai_Peninsula_SRTM_PBR")
    if tm and tm.node_tree:
        nt = tm.node_tree
        # Clean nodes
        nt.nodes.clear()
        
        out_node = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        
        tc = nt.nodes.new("ShaderNodeTexCoord")
        noise_macro = nt.nodes.new("ShaderNodeTexNoise")
        noise_macro.inputs['Scale'].default_value = 0.0015 # 600m macro city zones
        noise_macro.inputs['Detail'].default_value = 4.0
        
        noise_micro = nt.nodes.new("ShaderNodeTexNoise")
        noise_micro.inputs['Scale'].default_value = 0.05 # 20m micro streets/blocks
        noise_micro.inputs['Detail'].default_value = 6.0
        
        ramp_macro = nt.nodes.new("ShaderNodeValToRGB")
        # Asphalt dark grey to urban concrete
        ramp_macro.color_ramp.elements[0].position = 0.2
        ramp_macro.color_ramp.elements[0].color = (0.12, 0.13, 0.15, 1.0)
        ramp_macro.color_ramp.elements[1].position = 0.6
        ramp_macro.color_ramp.elements[1].color = (0.24, 0.25, 0.27, 1.0)
        
        ramp_green = nt.nodes.new("ShaderNodeValToRGB")
        # Parkland greens (Maidans, parks, Malabar Hill slopes)
        ramp_green.color_ramp.elements[0].position = 0.4
        ramp_green.color_ramp.elements[0].color = (0.13, 0.14, 0.16, 1.0)
        ramp_green.color_ramp.elements[1].position = 0.75
        ramp_green.color_ramp.elements[1].color = (0.11, 0.22, 0.10, 1.0)
        
        mix_color = nt.nodes.new("ShaderNodeMix")
        mix_color.data_type = 'RGBA'
        mix_color.inputs['Factor'].default_value = 0.35
        
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs['Strength'].default_value = 0.25
        
        # Link
        nt.links.new(tc.outputs['Object'], noise_macro.inputs['Vector'])
        nt.links.new(tc.outputs['Object'], noise_micro.inputs['Vector'])
        nt.links.new(noise_macro.outputs['Fac'], ramp_macro.inputs['Fac'])
        nt.links.new(noise_micro.outputs['Fac'], ramp_green.inputs['Fac'])
        nt.links.new(ramp_macro.outputs['Color'], mix_color.inputs['A'])
        nt.links.new(ramp_green.outputs['Color'], mix_color.inputs['B'])
        nt.links.new(mix_color.outputs['Result'], bsdf.inputs['Base Color'])
        nt.links.new(noise_micro.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        
        bsdf.inputs['Roughness'].default_value = 0.80
        nt.links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
        print("Configured realistic PBR terrain shader (no rainbow artifacts).")

    # 3. Boost Queen's Necklace Lights for Twinkling Aerial Vista
    for mat_name in ['MAT_QueensNecklace_Sodium_Glow', 'MAT_Lamp_Globe_Amber']:
        mat = bpy.data.materials.get(mat_name)
        if mat and mat.node_tree:
            for n in mat.node_tree.nodes:
                if n.type == 'EMISSION':
                    n.inputs['Strength'].default_value = 120.0
                elif n.type == 'BSDF_PRINCIPLED' and 'Emission Strength' in n.inputs:
                    n.inputs['Emission Strength'].default_value = 120.0

    # 4. Master Cinematic Drone Camera
    cam_name = "Cam_Drone_Whole_Mumbai_Master"
    cam = bpy.data.objects.get(cam_name)
    if not cam:
        cdata = bpy.data.cameras.new(f"{cam_name}_Data")
        cam = bpy.data.objects.new(cam_name, cdata)
        bpy.context.scene.collection.objects.link(cam)

    cam.data.lens = 23.0 # Epic wide aerial drone lens
    cam.data.clip_start = 1.0
    cam.data.clip_end = 50000.0

    # Position drone at optimal aerial vantage point:
    # Altitude 520m, positioned south-southwest over Back Bay entrance
    cam.location = Vector((-1550.0, -180.0, 520.0))
    # Target looking northeast towards the curve of Marine Drive and Worli
    target = Vector((-920.0, 1550.0, 50.0))
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    scene.camera = cam

    # 5. Cycles Metal GPU Production Engine
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'METAL'
    cprefs.get_devices()
    for d in cprefs.devices: d.use = True

    scene.cycles.samples = 32 # Crisp sampling for aerial fine details
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.view_settings.exposure = -0.75
    scene.view_settings.look = 'High Contrast'

    blend_file = '/Users/ms/Downloads/GRAI/GRAI_Mumbai_Digital_Twin.blend'
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"Master blendfile saved: {blend_file}")

def render_master_drone():
    scene = bpy.context.scene
    out_path = "/Users/ms/Downloads/GRAI/renders/whole_mumbai_drone_master_render.png"
    artifact_path = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012/whole_mumbai_drone_master_render.png"
    scene.render.filepath = out_path

    print(f"Rendering Whole Mumbai Master Drone View to {out_path}...")
    bpy.ops.render.render(write_still=True)
    print("Render complete!")

    # Copy to artifacts directory
    import shutil
    shutil.copy2(out_path, artifact_path)
    print(f"Copied to IDE artifact path: {artifact_path}")

if __name__ == '__main__':
    setup_master_drone_render()
    render_master_drone()
