'''
Author: WANG Maonan
Date: 2025-06-30 15:37:30
LastEditors: WANG Maonan
Description: 将渲染的结果存储为 gif 文件
LastEditTime: 2025-07-14 12:38:56
'''
import os
import imageio
from PIL import Image
from tqdm import tqdm

from tshub.utils.get_abs_path import get_abs_path
path_convert = get_abs_path(__file__)

def create_gif_from_subdirs(
    root_dir, 
    image_name, 
    subfolder="", 
    output_dir="gifs", 
    gif_width=360, 
    fps=10, 
    palettesize=128,
    loop=0,  # 新增：0=无限循环，1=播放一次，2=播放两次，依此类推
    start_num=None,  # 开始的数字编号
    end_num=None,    # 结束的数字编号
    verbose=True,
):
    """
    Create GIFs from images with the same name in different subdirectories.
    
    Args:
        root_dir (str): Root directory containing numbered subdirectories (e.g., /1/, /2/, etc.)
        image_name (str): Name of the image file without extension (e.g., 'bev')
        subfolder (str, optional): Subfolder inside each numbered directory (e.g., "high_quality_rgb"). Defaults to "".
        output_dir (str, optional): Directory to save the output GIF (relative to root_dir). Defaults to "gifs".
        gif_width (int, optional): Width of the output GIF. Defaults to 360.
        fps (int, optional): Frames per second for the animation. Defaults to 10.
        palettesize (int, optional): Number of colors in the palette. Defaults to 128.
        loop (int, optional): Number of loops (0=infinite, 1=play once, etc.). Defaults to 0 (infinite loop).
        verbose (bool, optional): Whether to print progress. Defaults to True.
    """
    # Create output directory if it doesn't exist
    full_output_dir = os.path.join(root_dir, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)
    
    # Get all numbered subdirectories
    subdirs = sorted(
        [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.isdigit()],
        key=lambda x: int(x)
    )
    
    if not subdirs:
        raise ValueError(f"No numbered subdirectories found in {root_dir}")

    # Filter subdirectories based on start_num and end_num
    if start_num is not None:
        subdirs = [d for d in subdirs if int(d) >= start_num]
    if end_num is not None:
        subdirs = [d for d in subdirs if int(d) <= end_num]
    
    images_for_gif = []
    missing_images = []
    
    for subdir in tqdm(subdirs, desc="Processing images", disable=not verbose):
        # Construct image path (handle subfolder if provided)
        if subfolder:
            image_path = os.path.join(root_dir, subdir, subfolder, f"{image_name}.png")
        else:
            image_path = os.path.join(root_dir, subdir, f"{image_name}.png")
        
        if not os.path.exists(image_path):
            missing_images.append(image_path)
            continue
            
        with Image.open(image_path) as img:
            # Resize the image
            width_percent = (gif_width / float(img.size[0]))
            height_size = int((float(img.size[1]) * float(width_percent)))
            img_resized = img.resize((gif_width, height_size), Image.Resampling.LANCZOS)
            images_for_gif.append(img_resized)
    
    if not images_for_gif:
        raise FileNotFoundError(f"No images found matching {image_name}.png in {root_dir}")
    
    if missing_images and verbose:
        print(f"Warning: {len(missing_images)} images missing (e.g., {missing_images[0]})")
    
    # Save the GIF with loop control
    output_path = os.path.join(full_output_dir, f"{image_name}.gif")
    
    # Use imageio.get_writer() to set loop parameter
    with imageio.get_writer(
        output_path,
        mode='I',
        fps=fps,
        palettesize=palettesize,
        loop=loop,  # 关键：设置循环次数（0=无限循环）
    ) as writer:
        for img in images_for_gif:
            writer.append_data(img)
    
    if verbose:
        print(f"GIF saved successfully at {output_path}")
        print(f"Total frames: {len(images_for_gif)}")
        print(f"Loop: {'infinite' if loop == 0 else f'{loop} times'}")
    
    return output_path

# Example usage:
create_gif_from_subdirs(
    root_dir=path_convert("./exp_dataset/Hongkong_YMT_rl/"),
    subfolder="high_quality_rgb",
    image_name='cam_path_1',
    start_num=110,
    end_num=220,
)