'''
Author: Maonan Wang
Date: 2025-03-21 11:49:45
LastEditTime: 2025-05-19 14:38:01
LastEditors: Maonan Wang
Description: 将 JSON 文件转换为文本, 使用模板进行转换
FilePath: /VLM-TSC/collect_data/json_to_templated.py
'''
import os
import json
import random
from tshub.utils.get_abs_path import get_abs_path

path_convert = get_abs_path(__file__)


class TrafficQuestionFactory:
    def __init__(self, data, max_distance:float=30):
        """将 JSON 数据转换为基于模板的 QA 问题对, 这里 max_distance 是指统计的时候只保留这个范围内的车辆
        """
        self.max_distance = max_distance # 只保留 max_distance 范围内的车辆
        self.data = data
        self.in_road = data['in_road']
        self.out_road = data['out_road']
        self.in_lanes = data['in_lanes'] # 获得 in lanes 的 (id, 车道长度)
        self.out_lanes = data['out_lanes'] # out lanes 的 (id, 车道长度)
        self.vehicles = data['vehicles']
    
    # -----
    # Update Vehicle Information (将 lane position 转换为距离路口的距离)
    # -----
    def calculate_distance_to_intersection(self):
        """计算每个车辆到十字路口的距离，并将结果添加到车辆信息中。

        :param in_lanes: 包含 in lanes 的 lane id 和长度
        :param out_lanes: 包含 out lanes 的 lane id 和长度
        :param vehicles: 包含车辆的详细信息
        :return: 直接对 self.vehicles 进行更新
        """
        for vehicle_id, vehicle_info in self.vehicles.items():
            lane_id = vehicle_info['lane_id']
            lane_position = vehicle_info['lane_position']

            # 根据车道 ID 判断当前车辆是在 in lane 还是 out lane
            if lane_id in self.in_lanes:
                # 在 in lane 上，距离路口的距离 = 车道长度 - 当前车辆的位置
                distance_to_intersection = self.in_lanes[lane_id] - lane_position
            elif lane_id in self.out_lanes:
                # 在 out lane 上，距离路口的距离 = 当前车辆的位置
                distance_to_intersection = lane_position
            else:
                # 如果车道 ID 不在 in lanes 和 out lanes 中，距离设为 None
                distance_to_intersection = None

            # 将计算结果添加到车辆信息中
            vehicle_info['distance_to_intersection'] = distance_to_intersection
    
    # ------------
    # Generate VQA
    # ------------
    def generate_all_questions(self):
        self.calculate_distance_to_intersection() # 首先更新车辆到路口的距离
        questions = list()
        questions.extend(self._generate_qualitative()) # 定性问题
        questions.extend(self._generate_quantitative()) # 定量问题
        questions.extend(self._generate_comprehensive()) # 综合问题
        
        return questions
    
    def _generate_qualitative(self):
        """生成**定性** QA 对
        """
        return [
            self._generate_vehicle_types(),
            self._generate_special_vehicles(),
            self._generate_accident(),
            self._generate_lane_comparison(),
            self._generate_lane_empty()
        ]
    
    def _generate_quantitative(self):
        """生成**定量** QA 对
        """
        return [
            self._generate_total_lanes(),
            self._generate_total_vehicles(),
            self._generate_lane_type_count(),
            self._generate_lane_count()
        ]
    
    def _generate_comprehensive(self):
        """生成**综合** QA 对
        """
        return [
            self._generate_queue_check(),
            self._generate_congestion_level()
        ]

    # #############
    # 定性问题生成器
    # #############
    def _generate_vehicle_types(self):
        """询问场景内的车辆类型
        """
        question = "What types of vehicles are present in the image? (car, police car, ambulance)"
        vehicle_types = set(v['vehicle_type'] for v in self.vehicles.values()) # 获得所有的车辆类型
        answer = ', '.join(vehicle_types) if vehicle_types else 'None'
        return {'question': question, 'answer': answer}
    
    def _generate_special_vehicles(self):
        """是否存在特殊类型的车辆
        """
        question = "Does the image contain a police car or an ambulance?"
        has_special = any(v['vehicle_type'] in ['police', 'ambulance'] 
                         for v in self.vehicles.values())
        answer = "Yes" if has_special else "No"
        return {'question': question, 'answer': answer}
    
    def _generate_accident(self):
        """是否存在交通事故
        """
        question = "Is there any traffic accident in the image?"
        has_accident = any(v['event'] is not None for v in self.vehicles.values())
        answer = "Yes" if has_accident else "No"
        return {'question': question, 'answer': answer}
    
    def _generate_lane_comparison(self):
        """比较两个车道之间相对车辆数量
        """
        lane_numbers = sorted([int(l.split('_')[-1]) for l in self.in_lanes.keys()]) # 车道编号, 这里是从 0 开始的
        if len(lane_numbers) < 2:
            n, m = 0, 0
        else:
            n, m = random.sample(lane_numbers, 2)
        
        # 随机选择两个车道并计算车道内的车辆数
        lane_n_id = f"{self.in_road}_{n}"
        lane_m_id = f"{self.in_road}_{m}"
        count_n = sum(
            1 for v in self.vehicles.values() 
            if (v['lane_id'] == lane_n_id) and (v['distance_to_intersection'] <= self.max_distance)
        )
        count_m = sum(
            1 for v in self.vehicles.values() 
            if (v['lane_id'] == lane_m_id) and (v['distance_to_intersection'] <= self.max_distance)
        )
        
        if count_n > count_m:
            answer = f"Incoming lane {n} (Vehicle Number: {count_n}) > lane {m} (Vehicle Number: {count_m})"
        elif count_m > count_n:
            answer = f"Incoming lane {m} (Vehicle Number: {count_m}) > lane {n} (Vehicle Number: {count_n})"
        else:
            answer = "Equal occupancy"
        
        question = f"Which lane has higher occupancy between Incoming lane {n} and {m}?"
        return {'question': question, 'answer': answer}
    
    def _generate_lane_empty(self):
        """询问指定车道是否存有车辆
        """
        lane_type = random.choice(['Incoming', 'Outgoing'])
        if lane_type == 'Incoming':
            lanes = self.in_lanes
            road = self.in_road
        else:
            lanes = self.out_lanes
            road = self.out_road
        
        lane_number = random.randint(0, len(lanes)-1) # 车道号
        lane_id = f"{road}_{lane_number}"
        count = sum(
            1 for v in self.vehicles.values() 
            if (v['lane_id'] == lane_id) and (v['distance_to_intersection'] <= self.max_distance)
        ) # 统计车辆数
        
        question = f"Is the {lane_type} lane {lane_number} empty?"
        answer = "Yes" if count == 0 else f"No ({count} vehicles)"
        return {'question': question, 'answer': answer}

    # #############
    # 定量问题生成器
    # #############
    def _generate_total_lanes(self):
        """生成总的车道数, 具体到 incoming lanes 和 outgoing lanes, 说明 index 是从 0 开始的
        """
        total = len(self.in_lanes) + len(self.out_lanes)
        question = "How many lanes are there in total (including incoming and outgoing)?"
        answer = f"There are a total of {total} lanes, including {len(self.in_lanes)} incoming lanes and {len(self.out_lanes)} outgoing lanes."
        return {'question': question, 'answer': answer}
    
    def _generate_total_vehicles(self):
        """计算总的车辆数, 分别 incoming 和 outgoing 有多少车
        """
        incoming_vehicles = sum(
            1 for v in self.vehicles.values() 
            if (v['road_id'] == self.in_road) and (v['distance_to_intersection'] <= self.max_distance)
        ) # 统计进口道的车辆
        outgoing_vehicles = sum(
            1 for v in self.vehicles.values() 
            if (v['road_id'] == self.out_road) and (v['distance_to_intersection'] <= self.max_distance)
        ) # 统计出口道的车辆
        total = incoming_vehicles + outgoing_vehicles # 总的车辆数

        question = "How many vehicles are present in the image?"
        answer = f"There are a total of {total} vehicles, {incoming_vehicles} vehicles in incoming road and {outgoing_vehicles} vehicles in outgoing road."
        return {'question': question, 'answer': answer}

    def _generate_lane_type_count(self):
        """分别计算 incoming and outgoing 车道上的车辆
        """
        lane_type = random.choice(['Incoming', 'Outgoing'])
        if lane_type == 'Incoming':
            road = self.in_road
            lanes = self.in_lanes
        else:
            road = self.out_road
            lanes = self.out_lanes
        
        vehicle_number_each_lane = {}
        for lane_number in range(len(lanes)): # 随机一个车道
            lane_id = f"{road}_{lane_number}"
            count = sum(
                1 for v in self.vehicles.values() 
                if (v['lane_id'] == lane_id) and (v['distance_to_intersection'] <= self.max_distance)
            )
            vehicle_number_each_lane[lane_number] = count # 统计每一个 lane 对应的车辆数
        
        # 将 dict 转换为自然语言
        question = f"How many vehicles are on {lane_type}?"
        total_vehicles = sum(vehicle_number_each_lane.values())
    
        # 构建详细的车道信息
        lane_details =  []
        for lane, count in vehicle_number_each_lane.items():
            lane_details.append(f"{count} in lane-{lane}")
        
        # 构建自然语言描述
        if total_vehicles == 0:
            total_description = f"There are no vehicles on the {lane_type} roads."
        else:
            total_description = f"There are a total of {total_vehicles} vehicles on the {lane_type} roads."
        
        # 将车道信息连接成一个字符串
        lane_details_str = ", ".join(lane_details)
        
        # 最终的自然语言描述
        answer = f"{total_description} Specifically, {lane_details_str}."

        return {'question': question, 'answer': answer}
    
    def _generate_lane_count(self):
        """具体到某个车道的车辆数
        """
        lane_type = random.choice(['Incoming', 'Outgoing'])
        if lane_type == 'Incoming':
            road = self.in_road
            lanes = self.in_lanes
        else:
            road = self.out_road
            lanes = self.out_lanes
        
        lane_number = random.randint(0, len(lanes)-1) # 随机一个车道
        lane_id = f"{road}_{lane_number}"
        count = sum(
            1 for v in self.vehicles.values() 
            if (v['lane_id'] == lane_id) and (v['distance_to_intersection'] <= self.max_distance)
        )
        
        question = f"How many vehicles are on {lane_type} lane {lane_number}?"
        answer = f"There are total of {count} vehicles on {lane_type} lane {lane_number}."
        return {'question': question, 'answer': answer}

    # 综合问题生成器
    def _generate_queue_check(self):
        """是否有排队
        """
        question = "Is there vehicle queuing in the scene? (Based on density)"
        threshold = 3
        queue_exists = any(
            sum(1 for v in self.vehicles.values() if v['lane_id'] == lane_id) >= threshold
            for lane_id in self.in_lanes.keys() | self.out_lanes.keys()
        )
        answer = "Yes" if queue_exists else "No"
        return {'question': question, 'answer': answer}
    
    def _generate_congestion_level(self):
        """估计拥堵的程度, 这里不需要具体到车辆数, 而是按照拥堵程度进行划分
        """
        question = "What is the congestion level? (Options: None/Light/Moderate/Severe)"
        total_vehicles = len(self.vehicles)
        total_lanes = len(self.in_lanes) + len(self.out_lanes)
        avg = total_vehicles / total_lanes if total_lanes else 0
        
        if avg > 5:
            level = "Severe"
        elif avg > 3:
            level = "Moderate"
        elif avg > 1:
            level = "Light"
        else:
            level = "None"
        
        answer = f"{level} congestion"
        return {'question': question, 'answer': answer}


def process_json_files(input_folder, output_folder):
    """将转换的到的 QA 问题对存储在 txt 文件中
    """
    # 检查输出的文件夹是否存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            json_file_path = os.path.join(input_folder, filename)
            templated_file_path = os.path.join(output_folder, filename)

            # 解析 JSON 文件, 并生成基于模板的 QA
            with open(json_file_path, "r") as f:
                data = json.load(f)
            factory = TrafficQuestionFactory(data)
            qa_list = factory.generate_all_questions()

        with open(templated_file_path, 'w') as f:
            json.dump(qa_list, f, indent=4)

                    
if __name__ == "__main__":
    json_folder = path_convert("../qa_dataset/json")
    templated_folder = path_convert("../qa_dataset/templated")
    process_json_files(
        input_folder=json_folder,
        output_folder=templated_folder
    )