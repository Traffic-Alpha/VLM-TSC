import os
import cv2
import numpy as np

from ultralytics import YOLO
from typing import List, Tuple, Dict

# 类型别名定义
BoundingBox = Tuple[float, float, float, float]  # (x, y, width, height)
Detection = Tuple[BoundingBox, float, str]  # (bbox, confidence, class_name)
ImageType = np.ndarray

def load_yolo_model(model_path: str = 'yolov8n.pt') -> YOLO:
    """加载YOLO模型
    """
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        raise RuntimeError(f"加载YOLO模型失败: {e}")

def load_image(image_path: str) -> ImageType:
    """加载图像
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法加载图像: {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def is_vehicle_class(class_name: str) -> bool:
    """判断类别是否为车辆, 只给车辆画框
    """
    vehicle_classes = {'car', 'truck', 'bus', 'motorcycle', 'vehicle'}
    return class_name in vehicle_classes

def filter_vehicle_detections(results) -> List[Detection]:
    """从YOLO结果中过滤出车辆检测
    """
    detections = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # 获取边界框坐标 (xyxy格式)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = box.conf[0].cpu().numpy()
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]
                
                # 过滤车辆类别
                if is_vehicle_class(class_name):
                    bbox = (float(x1), float(y1), float(x2 - x1), float(y2 - y1))
                    detections.append((bbox, float(confidence), class_name))
    
    return detections

def detect_vehicles(image: ImageType, model: YOLO, 
                   confidence_threshold: float = 0.25) -> List[Detection]:
    """
    检测图像中的车辆
    
    Args:
        image: 输入图像
        model: YOLO模型
        confidence_threshold: 置信度阈值
        
    Returns:
        车辆检测结果
    """
    # 进行推理
    results = model(image, conf=confidence_threshold, verbose=False)
    
    # 过滤车辆检测结果
    vehicle_detections = filter_vehicle_detections(results)
    
    return vehicle_detections

def print_detection_summary(detections: List[Detection]) -> None:
    """
    打印检测结果摘要
    
    Args:
        detections: 检测结果
    """
    if not detections:
        print("未检测到任何车辆")
        return
    
    vehicle_counts = {}
    confidences = []
    
    for _, confidence, class_name in detections:
        vehicle_counts[class_name] = vehicle_counts.get(class_name, 0) + 1
        confidences.append(confidence)
    
    print("\n=== 车辆检测结果 ===")
    for vehicle_type, count in vehicle_counts.items():
        print(f"{vehicle_type}: {count}辆")
    
    print(f"总计: {len(detections)}辆车")
    print(f"平均置信度: {np.mean(confidences):.3f}")
    print(f"最高置信度: {np.max(confidences):.3f}")
    print(f"最低置信度: {np.min(confidences):.3f}")

def save_detection_image(image: ImageType, detections: List[Detection], 
                        output_path: str, is_label:bool = False) -> None:
    """
    保存带检测框的图像
    
    Args:
        image: 原始图像
        detections: 检测结果
        output_path: 输出路径
    """
    # 转换为BGR格式用于OpenCV保存
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    colors = {
        'car': (0, 0, 255), 
        'truck': (255, 0, 0), 
        'bus': (0, 255, 0), 
        'motorcycle': (0, 165, 255),
        'vehicle': (128, 0, 128)
    }
    
    for bbox, confidence, class_name in detections:
        x, y, w, h = map(int, bbox)
        color = colors.get(class_name, (255, 255, 0))
        
        # 绘制边界框
        cv2.rectangle(image_bgr, (x, y), (x + w, y + h), color, 2)
        
        if is_label:
            # 添加标签
            label = f'{class_name} {confidence:.2f}'
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # 绘制标签背景
            cv2.rectangle(image_bgr, (x, y - label_size[1] - 10), 
                        (x + label_size[0], y), color, -1)
            
            # 绘制标签文字
            cv2.putText(image_bgr, label, (x, y - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    cv2.imwrite(output_path, image_bgr)
    print(f"检测结果已保存至: {output_path}")

def calculate_detection_statistics(detections: List[Detection]) -> Dict:
    """
    计算检测结果的统计信息
    
    Args:
        detections: 检测结果
        
    Returns:
        统计信息字典
    """
    if not detections:
        return {
            'total_vehicles': 0,
            'average_confidence': 0,
            'class_distribution': {},
            'max_confidence': 0,
            'min_confidence': 0
        }
    
    confidences = [confidence for _, confidence, _ in detections]
    class_names = [class_name for _, _, class_name in detections]
    
    # 计算类别分布
    class_distribution = {}
    for class_name in class_names:
        class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
    
    return {
        'total_vehicles': len(detections),
        'average_confidence': float(np.mean(confidences)),
        'max_confidence': float(np.max(confidences)),
        'min_confidence': float(np.min(confidences)),
        'class_distribution': class_distribution
    }

def process_single_image(image_path: str, model: YOLO, 
                        confidence_threshold: float = 0.25,
                        save_output: bool = True) -> Dict:
    """
    处理单张图像的完整流程
    
    Args:
        image_path: 图像路径
        model: YOLO模型
        confidence_threshold: 置信度阈值
        save_output: 是否保存输出图像
        
    Returns:
        处理结果字典
    """
    # 加载图像
    image = load_image(image_path)
    
    # 检测车辆
    detections = detect_vehicles(image, model, confidence_threshold)
    
    # 计算统计信息
    stats = calculate_detection_statistics(detections)
    
    # 打印摘要
    print_detection_summary(detections)
    
    # 保存结果图像, 存储一个 detected 图像
    if save_output:
        # 创建yolo_output文件夹（如果不存在）
        yolo_output_dir = os.path.join(os.path.dirname(os.path.dirname(image_path)), 'yolo_output')
        os.makedirs(yolo_output_dir, exist_ok=True)

        # 构建输出路径
        filename = os.path.basename(image_path).replace('.', '_detected.')
        output_path = os.path.join(yolo_output_dir, filename)

        save_detection_image(image, detections, output_path)
    
    return {
        'image': image,
        'detections': detections,
        'statistics': stats
    }

# 批量处理函数
def process_multiple_images(root_dir: List[str], 
                           confidence_threshold: float = 0.25) -> List[Dict]:
    """批量处理多张图像
    """
    print("正在加载YOLO模型...")
    model = load_yolo_model('yolo11x.pt')  # 可以使用 'yolov8s.pt', 'yolov8m.pt' 等

    for timestep in os.listdir(root_dir):
        timestep_path = os.path.join(root_dir, timestep, 'high_quality_rgb')
        if not os.path.isdir(timestep_path):
            continue
        
        # 处理目录下指定的 JPG 文件
        for img_file in sorted(os.listdir(timestep_path)):
            if img_file in ["2.png", "3.png"]:
                img_path = os.path.join(timestep_path, img_file)
                process_single_image(img_path, model, confidence_threshold, save_output=True)

            
if __name__ == "__main__":
    process_multiple_images("/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/India_Delhi_easy_high_density")