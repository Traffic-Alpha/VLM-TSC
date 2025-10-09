'''
Author: WANG Maonan
Date: 2025-10-09 16:57:14
LastEditors: WANG Maonan
Description: EXR深度图转灰度图转换器
LastEditTime: 2025-10-09 16:58:18
'''
import os
import cv2
import Imath
import OpenEXR
import argparse
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def read_exr_depth(exr_path, channel='R'):
    """
    读取EXR文件的深度通道
    
    参数:
        exr_path: EXR文件路径
        channel: 深度数据所在的通道，通常为'R'
    
    返回:
        depth_map: 深度图numpy数组
    """
    try:
        # 打开EXR文件
        exr_file = OpenEXR.InputFile(exr_path)
        
        # 获取文件头信息
        header = exr_file.header()
        
        # 获取数据窗口
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1
        
        # 读取指定通道
        channel_data = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
        
        # 转换为numpy数组
        depth_map = np.frombuffer(channel_data, dtype=np.float32)
        depth_map = depth_map.reshape(height, width)
        
        return depth_map
        
    except Exception as e:
        print(f"读取EXR文件失败: {e}")
        return None

def normalize_depth_for_display(depth_map, method='percentile', min_percentile=2, max_percentile=98):
    """
    将深度图归一化到0-255范围用于显示
    
    参数:
        depth_map: 原始深度图
        method: 归一化方法 ('percentile', 'minmax', 'log')
        min_percentile: 最小百分位数
        max_percentile: 最大百分位数
    
    返回:
        normalized: 归一化后的图像 (0-255, uint8)
    """
    # 处理无效值
    depth_map = np.nan_to_num(depth_map, nan=0.0, posinf=0.0, neginf=0.0)
    
    # 移除零值和无效值
    valid_depth = depth_map[depth_map > 0]
    
    if len(valid_depth) == 0:
        return np.zeros_like(depth_map, dtype=np.uint8)
    
    if method == 'percentile':
        # 使用百分位数来排除异常值
        vmin = np.percentile(valid_depth, min_percentile)
        vmax = np.percentile(valid_depth, max_percentile)
        
    elif method == 'minmax':
        # 使用最小最大值
        vmin = np.min(valid_depth)
        vmax = np.max(valid_depth)
        
    elif method == 'log':
        # 对数变换，适用于深度范围很大的情况
        valid_depth = np.log1p(valid_depth)
        vmin = np.percentile(valid_depth, min_percentile)
        vmax = np.percentile(valid_depth, max_percentile)
        depth_map = np.log1p(depth_map)
    
    else:
        raise ValueError("不支持的归一化方法")
    
    # 限制范围
    depth_map_clipped = np.clip(depth_map, vmin, vmax)
    
    # 线性归一化到0-255
    normalized = (depth_map_clipped - vmin) / (vmax - vmin) * 255
    normalized = np.clip(normalized, 0, 255).astype(np.uint8)
    
    return normalized

def apply_colormap(gray_image, colormap=cv2.COLORMAP_VIRIDIS):
    """
    应用伪彩色映射（可选）
    
    参数:
        gray_image: 灰度图像
        colormap: OpenCV色彩映射
    
    返回:
        colored: 伪彩色图像
    """
    colored = cv2.applyColorMap(gray_image, colormap)
    return colored

def save_comparison_figure(original_depth, normalized_gray, output_path, dpi=300):
    """
    保存对比图，用于论文展示
    
    参数:
        original_depth: 原始深度数据
        normalized_gray: 归一化后的灰度图
        output_path: 输出路径
        dpi: 输出分辨率
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # 原始深度图（伪彩色）
    im1 = ax1.imshow(original_depth, cmap='viridis')
    ax1.set_title('原始深度图 (伪彩色)', fontsize=12)
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, label='深度值')
    
    # 灰度图
    ax2.imshow(normalized_gray, cmap='gray')
    ax2.set_title('转换后的灰度图', fontsize=12)
    ax2.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', transparent=True)
    plt.close()

def convert_exr_to_grayscale(input_path, output_dir=None, 
                            normalization_method='percentile',
                            save_colored=False,
                            save_comparison=False,
                            output_format='png'):
    """
    主转换函数
    
    参数:
        input_path: 输入EXR文件路径
        output_dir: 输出目录
        normalization_method: 归一化方法
        save_colored: 是否保存伪彩色版本
        save_comparison: 是否保存对比图
        output_format: 输出格式 ('png', 'jpg', 'tiff')
    """
    
    # 读取EXR文件
    print(f"正在读取: {input_path}")
    depth_map = read_exr_depth(input_path)
    
    if depth_map is None:
        print("无法读取深度图，跳过该文件")
        return
    
    # 创建输出目录
    input_path = Path(input_path)
    if output_dir is None:
        output_dir = input_path.parent / 'output'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # 归一化深度图
    normalized_gray = normalize_depth_for_display(
        depth_map, 
        method=normalization_method
    )
    
    # 生成输出文件名
    stem = input_path.stem
    gray_output = output_dir / f"{stem}_gray.{output_format}"
    
    # 保存灰度图
    cv2.imwrite(str(gray_output), normalized_gray)
    print(f"已保存灰度图: {gray_output}")
    
    # 保存伪彩色版本（可选）
    if save_colored:
        colored = apply_colormap(normalized_gray)
        colored_output = output_dir / f"{stem}_colored.{output_format}"
        cv2.imwrite(str(colored_output), colored)
        print(f"已保存伪彩色图: {colored_output}")
    
    # 保存对比图（可选，用于论文）
    if save_comparison:
        comparison_output = output_dir / f"{stem}_comparison.{output_format}"
        save_comparison_figure(depth_map, normalized_gray, comparison_output)
        print(f"已保存对比图: {comparison_output}")
    
    # 打印统计信息
    valid_pixels = depth_map[depth_map > 0]
    if len(valid_pixels) > 0:
        print(f"深度范围: [{np.min(valid_pixels):.3f}, {np.max(valid_pixels):.3f}]")
        print(f"有效像素数: {len(valid_pixels)} / {depth_map.size}")

def batch_convert(input_dir, output_dir=None, **kwargs):
    """
    批量转换目录中的所有EXR文件
    """
    input_dir = Path(input_dir)
    exr_files = list(input_dir.glob("*.exr"))
    
    if not exr_files:
        print(f"在目录 {input_dir} 中未找到EXR文件")
        return
    
    print(f"找到 {len(exr_files)} 个EXR文件")
    
    for i, exr_file in enumerate(exr_files, 1):
        print(f"\n处理文件 {i}/{len(exr_files)}: {exr_file.name}")
        try:
            convert_exr_to_grayscale(exr_file, output_dir, **kwargs)
        except Exception as e:
            print(f"处理 {exr_file} 时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='EXR深度图转灰度图转换器')
    parser.add_argument('input', help='输入EXR文件或目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-m', '--method', default='percentile', 
                       choices=['percentile', 'minmax', 'log'],
                       help='归一化方法 (默认: percentile)')
    parser.add_argument('--colored', action='store_true',
                       help='同时保存伪彩色版本')
    parser.add_argument('--comparison', action='store_true',
                       help='保存对比图')
    parser.add_argument('--format', default='png', 
                       choices=['png', 'jpg', 'tiff'],
                       help='输出格式 (默认: png)')
    parser.add_argument('--batch', action='store_true',
                       help='批量处理目录中的所有EXR文件')
    
    args = parser.parse_args()
    
    if args.batch or os.path.isdir(args.input):
        batch_convert(
            args.input,
            args.output,
            normalization_method=args.method,
            save_colored=args.colored,
            save_comparison=args.comparison,
            output_format=args.format
        )
    else:
        convert_exr_to_grayscale(
            args.input,
            args.output,
            normalization_method=args.method,
            save_colored=args.colored,
            save_comparison=args.comparison,
            output_format=args.format
        )

if __name__ == "__main__":
    # 安装依赖:
    # pip install openexr numpy opencv-python matplotlib
    
    # 示例用法:
    print("EXR深度图转灰度图转换器")
    
    # 如果直接运行，显示使用说明
    import sys
    if len(sys.argv) == 1:
        print("\n使用示例:")
        print("1. 转换单个文件: python depth_to_gray.py input.exr -o output/")
        print("2. 批量转换: python depth_to_gray.py /path/to/exr/files --batch")
        print("3. 带伪彩色: python depth_to_gray.py input.exr --colored --comparison")
        print("\n使用 -h 查看所有选项")
    else:
        main()