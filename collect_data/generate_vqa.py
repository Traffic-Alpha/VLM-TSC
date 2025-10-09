'''
Author: Maonan Wang
Date: 2025-03-21 11:49:45
Description: 根据 JSON 文件产生描述图片的 QA
@ 定性问题
-> 当前车道是否可以通行
-> 是否包含特殊车辆（根据特殊车辆距离远近给出一定内容, 同时给出车辆进入/离开路口）
-> 是否包含事故，导致车辆无法移动
@ 定量问题
-> 进口道每个车道有多少车
-> 出口道每个车道有多少车
LastEditors: WANG Maonan
LastEditTime: 2025-09-11 16:38:37
'''
import os
import json
from parse_infos.json2vqa import TrafficLightVQA
from tshub.utils.get_abs_path import get_abs_path

path_convert = get_abs_path(__file__)

def generate_and_save_vqa(root_dir, distance_mapping):
    """
    批量处理JSON目录结构并保存VQA结果到各timestep/qa目录
    
    Args:
        root_dir: 根目录路径 (包含timestep子目录)
        distance_mapping: 字典 {1: 100, 2: 200, 3: 50}
    """
    # 遍历每个timestep目录
    for timestep in os.listdir(root_dir):
        timestep_path = os.path.join(root_dir, timestep, 'annotations')
        if not os.path.isdir(timestep_path):
            continue
        
        # 创建 qa 目录
        qa_dir = os.path.join(timestep_path, '../QA')
        os.makedirs(qa_dir, exist_ok=True)
        
        # 处理该timestep下的每个JSON文件
        for json_file in sorted(os.listdir(timestep_path)):
            if not json_file.endswith('.json'):
                continue
                
            # 从文件名提取数字 (如"1.json" -> 1)
            file_num = int(os.path.splitext(json_file)[0])    
            # 获取对应的max_distance
            max_dist = distance_mapping.get(file_num, 100)  # 默认100
            
            # 加载JSON数据
            json_path = os.path.join(timestep_path, json_file)
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # 初始化并生成VQA数据
            vqa_results = TrafficLightVQA(
                data=data,
                max_distance=max_dist
            ).generate_all_questions()
            
            # 保存到qa目录 (保留原文件名)
            output_path = os.path.join(qa_dir, json_file)
            with open(output_path, 'w') as f:
                json.dump(vqa_results, f, indent=2)
            
            print(f"Generated: {os.path.join(timestep, 'qa', json_file)}")

if __name__ == "__main__":
    for i in [
        "SouthKorea_Songdo_easy_fluctuating_commuter_barrier",
        "SouthKorea_Songdo_easy_fluctuating_commuter_branch",
        "SouthKorea_Songdo_easy_fluctuating_commuter_crashed",
        "SouthKorea_Songdo_easy_fluctuating_commuter_none",
        "SouthKorea_Songdo_easy_fluctuating_commuter_pedestrain",
        
        "SouthKorea_Songdo_easy_increasing_demand_barrier",
        "SouthKorea_Songdo_easy_increasing_demand_branch",
        "SouthKorea_Songdo_easy_increasing_demand_crashed",
        "SouthKorea_Songdo_easy_increasing_demand_none",
        "SouthKorea_Songdo_easy_increasing_demand_pedestrain",

        "SouthKorea_Songdo_easy_random_perturbation_barrier",
        "SouthKorea_Songdo_easy_random_perturbation_branch",
        "SouthKorea_Songdo_easy_random_perturbation_crashed",
        "SouthKorea_Songdo_easy_random_perturbation_none",
        "SouthKorea_Songdo_easy_random_perturbation_pedestrain",
    ]:
        DATA_ROOT = path_convert(f"../exp_dataset/{i}")  # 包含timestep目录的根目录
        
        # 定义不同JSON文件对应的max_distance (使用数字键)
        DISTANCE_MAPPING = {
            0: 90, 
            1: 90, 
            2: 90,
            3: 90,
        } # 每个方向的观测距离
        
        # 生成并保存结果
        results = generate_and_save_vqa(DATA_ROOT, DISTANCE_MAPPING)