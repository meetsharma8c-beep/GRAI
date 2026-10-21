"""
Master Production Render: Slower 96-Frame 360-Degree Orbit Around Jogging Character (No Vehicles)
"""
import bpy
import os
import time

def render_all_96_frames():
    scene = bpy.context.scene
    out_dir = "/tmp/jogging_360_frames"
    os.makedirs(out_dir, exist_ok=True)

    print(f"=== RENDERING 96 CYCLES FRAMES TO {out_dir} ===")
    t0 = time.time()
    for f in range(1, 97):
        scene.frame_set(f)
        frame_path = f"{out_dir}/frame_{f:04d}.png"
        scene.render.filepath = frame_path
        tf_start = time.time()
        bpy.ops.render.render(write_still=True)
        tf = time.time() - tf_start
        if f % 8 == 0 or f == 96:
            print(f"Rendered frame {f:02d}/96 ({tf:.2f}s) -> {frame_path}")

    total = time.time() - t0
    print(f"All 96 frames rendered successfully in {total:.1f}s ({total/96:.2f}s/frame average)!")

if __name__ == '__main__':
    render_all_96_frames()
