"""
Compile 360-degree road walk animation frames into animated WebP and GIF.
"""
import glob
import os
import shutil
from PIL import Image

def compile_animation():
    frame_files = sorted(glob.glob("/tmp/running_360_frames/frame_*.png"))
    print(f"Found {len(frame_files)} rendered frames.")
    if not frame_files:
        print("No frames found to compile!")
        return

    frames = []
    for f in frame_files:
        im = Image.open(f)
        frames.append(im.convert("RGB"))

    # Destination directories
    renders_dir = "/Users/ms/Downloads/GRAI/renders"
    artifacts_dir = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012"
    os.makedirs(renders_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. High-Quality WebP Animation (24 fps -> duration = 41.67 ms, loop = 0)
    webp_path = os.path.join(renders_dir, "mumbai_player_360_road_walk.webp")
    frames[0].save(
        webp_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=42,
        loop=0,
        quality=90,
        method=6
    )
    print(f"WebP animation saved: {webp_path} ({os.path.getsize(webp_path)/1024/1024:.2f} MB)")

    # 2. Optimized GIF Animation (downscaled for quick loading)
    gif_path = os.path.join(renders_dir, "mumbai_player_360_road_walk.gif")
    gif_frames = [im.resize((960, 540), Image.Resampling.LANCZOS).convert("P", palette=Image.Palette.ADAPTIVE, colors=192) for im in frames]
    gif_frames[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=42,
        loop=0,
        optimize=True
    )
    print(f"GIF animation saved: {gif_path} ({os.path.getsize(gif_path)/1024/1024:.2f} MB)")

    # Copy to artifacts directory
    shutil.copy2(webp_path, os.path.join(artifacts_dir, "mumbai_player_360_road_walk.webp"))
    shutil.copy2(gif_path, os.path.join(artifacts_dir, "mumbai_player_360_road_walk.gif"))
    print("Copied animations to IDE artifact directory.")

if __name__ == '__main__':
    compile_animation()
