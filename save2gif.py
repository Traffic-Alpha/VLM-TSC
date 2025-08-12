'''
Author: WANG Maonan
Date: 2025-06-30 15:37:30
LastEditors: WANG Maonan
Description: 将渲染的结果存储为 gif 文件
LastEditTime: 2025-08-12 11:34:56
'''
import os
import imageio
from PIL import Image
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

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
    add_timestamp=False,  # 是否添加时间戳
    timestamp_format="Time: {}"  # 时间戳格式
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

            # 添加时间戳（新增功能）
            if add_timestamp:
                draw = ImageDraw.Draw(img_resized)
                try:
                    # 尝试加载字体（支持跨平台）
                    font = ImageFont.truetype("arial.ttf", max(12, int(img_resized.height * 0.04)))
                except:
                    # 回退到默认字体
                    font = ImageFont.load_default()
                
                # 准备时间戳文本
                timestamp_text = timestamp_format.format(subdir)
                bbox = draw.textbbox((0, 0), timestamp_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算位置（右上角）
                margin = int(img_resized.height * 0.02)
                position = (img_resized.width - text_width - margin, margin)
                
                # 添加背景框增强可读性
                bg_margin = 2
                bg_box = (
                    position[0] - bg_margin,
                    position[1] - bg_margin,
                    position[0] + text_width + bg_margin,
                    position[1] + text_height + bg_margin
                )
                draw.rectangle(bg_box, fill="black")
                
                # 添加时间戳文本
                draw.text(position, timestamp_text, fill="white", font=font)
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
for _image_name in ['0', '1', '2', 'bev']:
    create_gif_from_subdirs(
        root_dir=path_convert("./exp_dataset/France_Massy_easy_fluctuating_commuter_none/"),
        subfolder="high_quality_rgb",
        image_name=_image_name,
        start_num=20,
        end_num=600,
        add_timestamp=True
    )