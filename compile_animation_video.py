"""
Compile Rendered Frames into High-Definition Looping Video Animation
=====================================================================
Reads 48 frames from /tmp/running_frames/ and creates:
- human_running_mumbai_exploration.webp (24 fps smooth animated WebP)
- human_running_mumbai_exploration.gif (24 fps animated GIF)
Copies outputs to the project renders folder and artifact directory.
"""
import glob
import os
import shutil
from PIL import Image

def main():
    frame_files = sorted(glob.glob("/tmp/running_frames/frame_*.png"))
    print(f"Found {len(frame_files)} rendered animation frames.")
    if not frame_files:
        raise RuntimeError("No frames found!")

    # Load images
    frames = []
    for f in frame_files:
        img = Image.open(f)
        frames.append(img)

    out_dir = "/Users/ms/Downloads/GRAI/renders"
    os.makedirs(out_dir, exist_ok=True)
    brain_dir = "/Users/ms/.gemini/antigravity-ide/brain/bd8f0b40-a352-4ec1-a365-016f8f36c012"
    os.makedirs(brain_dir, exist_ok=True)

    # 1. Compile 24 FPS High-Resolution Animated WebP
    webp_path = os.path.join(out_dir, "human_running_mumbai_exploration.webp")
    # 41.67 ms per frame = 24 fps
    frames[0].save(
        webp_path,
        save_all=True,
        append_images=frames[1:],
        duration=42, # 24 fps
        loop=0,
        quality=92,
        method=6
    )
    print(f"Compiled WebP Video: {webp_path} ({os.path.getsize(webp_path)} bytes)")

    # 2. Compile Animated GIF (smaller scale for fast web display)
    gif_path = os.path.join(out_dir, "human_running_mumbai_exploration.gif")
    gif_frames = [f.resize((640, 360), Image.Resampling.LANCZOS).convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for f in frames]
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=42,
        loop=0,
        optimize=True
    )
    print(f"Compiled GIF Animation: {gif_path} ({os.path.getsize(gif_path)} bytes)")

    # Copy to Brain Artifact Directory
    shutil.copy(webp_path, brain_dir)
    shutil.copy(gif_path, brain_dir)
    print("Copied animations to artifact directory!")

if __name__ == '__main__':
    main()
