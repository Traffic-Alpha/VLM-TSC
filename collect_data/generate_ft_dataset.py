'''
Author: WANG Maonan
Date: 2025-08-19 17:41:38
LastEditors: WANG Maonan
Description: 根据现有数据, 产生 QwenVL FT 的数据集
LastEditTime: 2025-08-19 18:21:55
'''
import os
import json
import shutil

def process_dataset(input_dir: str, output_dir: str) -> None:
    """处理数据集，将其转换为 qwenvl 微调格式
    
    Args:
        input_dir: 输入数据集目录路径
        output_dir: 输出目录路径
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 存储所有转换后的数据
    all_data = []
    
    # 遍历输入目录中的所有 timestep 文件夹
    for timestep_dir in sorted(os.listdir(input_dir)):
        timestep_path = os.path.join(input_dir, timestep_dir)
        
        # 确保是目录
        if not os.path.isdir(timestep_path):
            continue
            
        # 检查必要的子目录是否存在
        rgb_dir = os.path.join(timestep_path, "high_quality_rgb")
        qa_dir = os.path.join(timestep_path, "QA")
        
        if not os.path.exists(rgb_dir) or not os.path.exists(qa_dir):
            print(f"警告: {timestep_dir} 缺少必要的子目录，跳过")
            continue
            
        # 处理每个图片文件
        for img_file in os.listdir(rgb_dir):
            if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_name = os.path.splitext(img_file)[0] # 图像文件名
                img_path = os.path.join(rgb_dir, img_file) # 图像的路径
                
                # 查找对应的 QA 文件
                qa_file = os.path.join(qa_dir, f"{img_name}.json")
                if not os.path.exists(qa_file):
                    print(f"警告: 找不到 {img_name} 的 QA 文件，跳过")
                    continue
                
                # 读取 QA 数据
                try:
                    with open(qa_file, 'r', encoding='utf-8') as f:
                        qa_data = json.load(f)
                except Exception as e:
                    print(f"错误: 无法读取 {qa_file}: {e}")
                    continue
                
                # 选择前三个问题
                selected_qa = qa_data[:3] if len(qa_data) > 3 else qa_data
                
                # 复制图片到输出目录
                output_img_dir = os.path.join(output_dir, "images")
                os.makedirs(output_img_dir, exist_ok=True)
                output_img_path = os.path.join(output_img_dir, f"{timestep_dir}_{img_file}")
                shutil.copy2(img_path, output_img_path)
                
                # 为每个问题创建对话条目
                relative_img_path = os.path.join("images", f"{timestep_dir}_{img_file}")
                
                for qa in selected_qa:
                    conversation = {
                        "image": relative_img_path,
                        "conversations": [
                            {
                                "from": "human",
                                "value": f"{qa['question']}\n<image>"
                            },
                            {
                                "from": "gpt",
                                "value": qa['answer']
                            }
                        ]
                    }
                    all_data.append(conversation)
    
    # 保存最终的 JSON 文件
    output_json_path = os.path.join(output_dir, "data.json")
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"处理完成! 共生成 {len(all_data)} 条对话记录")
    print(f"输出文件: {output_json_path}")

def main():
    input_directory = "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/exp_dataset/France_Massy_easy_random_perturbation_crashed"  # 输入数据集目录
    output_directory = "/home/tshub/Code_Project/2_Traffic/TrafficAlpha/VLM-TSC/ft_dataset/France_Massy_easy_random_perturbation_crashed"  # 输出目录
    
    print("开始处理数据集...")
    process_dataset(input_directory, output_directory)
    print("处理完成!")

if __name__ == "__main__":
    main()