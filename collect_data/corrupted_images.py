'''
Author: WANG Maonan
Date: 2025-07-16 21:47:21
LastEditors: WANG Maonan
Description: 随机模拟摄像头损坏
    死像素(dead_pixels)：

        随机生成黑色像素点（占图像5%面积）

        模拟传感器CMOS/CCD物理损坏

    扫描线噪声(line_noise)：

        随机黑色水平横线

        模拟传输线路干扰

    颜色失真(color_distortion)：

        RGB通道错位偏移

        模拟色彩滤镜损坏

    局部黑屏(partial_blackout)：

        随机矩形区域完全黑屏

        模拟传感器局部模块失效

    随机噪声(random_noise)：

        高斯噪声污染

        模拟电子干扰或传输错误

    严重模糊(blurred)：

        高强度高斯模糊

        模拟镜头污染或焦距故障

    亮度闪烁(flicker)：

        随机亮度变化

        模拟电源不稳定

    完全失效(complete_failure)：

        纯色暗红图像

        模拟传感器完全停止工作
LastEditTime: 2025-07-16 21:49:45
'''
import os
import cv2
import random
import numpy as np

def simulate_corruption(image_path, output_dir="corrupted_images"):
    """模拟传感器损坏效果并保存损坏后的图像
    :param image_path: 原始传感器图像路径
    :param output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取原始图像
    original = cv2.imread(image_path)
    if original is None:
        raise FileNotFoundError(f"图像加载失败: {image_path}")
    
    # 定义损坏类型列表
    corruption_types = [
        "dead_pixels", "line_noise", "color_distortion",
        "partial_blackout", "random_noise", "blurred",
        "flicker", "complete_failure"
    ]
    # flicker, 亮度闪烁
    
    # 为每种损坏类型生成图像
    for corruption in corruption_types:
        corrupted = original.copy()
        
        if corruption == "dead_pixels":
            # 死像素效果
            height, width = corrupted.shape[:2]
            for _ in range(int(width * height * 0.25)):  # 25% 的像素损坏
                x = random.randint(0, width-1)
                y = random.randint(0, height-1)
                corrupted[y, x] = [0, 0, 0]  # 黑色死点
        
        elif corruption == "line_noise":
            # 扫描线噪声
            for i in range(0, corrupted.shape[0], 5):
                if random.random() > 0.7:
                    corrupted[i:i+2, :] = 0  # 黑色横线
        
        elif corruption == "color_distortion":
            # 颜色失真 (RGB通道偏移)
            b, g, r = cv2.split(corrupted)
            r = np.roll(r, random.randint(-20, 20), axis=1)
            g = np.roll(g, random.randint(-15, 15), axis=0)
            corrupted = cv2.merge((b, g, r))
        
        elif corruption == "partial_blackout":
            # 局部黑屏
            h, w = corrupted.shape[:2]
            x1 = random.randint(0, w//2)
            y1 = random.randint(0, h//2)
            x2 = random.randint(w//2, w)
            y2 = random.randint(h//2, h)
            corrupted[y1:y2, x1:x2] = 0
        
        elif corruption == "random_noise":
            # 随机噪声
            noise = np.random.normal(0, 50, corrupted.shape).astype(np.int32)
            corrupted = np.clip(corrupted + noise, 0, 255).astype(np.uint8)
        
        elif corruption == "blurred":
            # 严重模糊 (模拟镜头损坏)
            corrupted = cv2.GaussianBlur(corrupted, (25, 25), 0)
        
        elif corruption == "flicker":
            # 闪烁效果 (随机亮度变化)
            brightness = random.uniform(0.3, 1.5)
            corrupted = cv2.convertScaleAbs(corrupted, alpha=brightness, beta=0)
        
        elif corruption == "complete_failure":
            # 完全失效 (纯色图像)
            corrupted[:, :] = [random.randint(0, 50), 0, 0]  # 暗红色
        
        # 保存损坏后的图像
        filename = os.path.join(output_dir, f"{corruption}_{os.path.basename(image_path)}")
        cv2.imwrite(filename, corrupted)
        print(f"已生成: {filename}")

if __name__ == "__main__":
    # 使用示例
    input_image = "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/assets/speical_scenarios/cam_path_2.png"  # 替换为你的传感器图像路径
    simulate_corruption(input_image)