'''
Author: Maonan Wang
Date: 2025-01-22 18:49:21
LastEditTime: 2025-01-22 19:41:11
LastEditors: Maonan Wang
Description: 在 Image 中添加 Accident 的场景
FilePath: /VLM-TSC/collect_data/collect_data/traffic_accidents.py
'''
import copy
import math
import random
# 这个应该是一个 class, 包含当前的状态 (是否事故，事故车 id，持续时间)
# 如果当前没有事故，则进行 sample
# - 首先 sample 到车辆的 id
# - 修改 state 添加事故车的形状
# - 对指定的车辆进行 stop

def generate_collision_vehicle(old_vehicle, new_veh_id):
    new_vehicle = copy.deepcopy(old_vehicle)

    # 提取旧车辆的信息
    x, y = old_vehicle['position']
    heading = old_vehicle['heading']
    length = old_vehicle['length']
    width = old_vehicle['width']

    # 计算新车辆的中心位置，确保在旧车辆尾部
    # 向后偏移旧车辆的半个长度再加上一个小偏移量
    offset_distance = length / 2 + 1  # 确保车辆不重合的偏移量
    angle_rad = math.radians(heading)
    new_x = x - offset_distance * math.cos(angle_rad)
    new_y = y - offset_distance * math.sin(angle_rad)

    # 新车辆的朝向，模拟追尾或换道
    angle_variation = random.choice(
            [random.uniform(-15, -5), random.uniform(5, 15)]
        )
    new_heading = (heading + angle_variation) % 360

    # 确保新角度不与旧角度相反
    if abs(new_heading - heading) > 150:
        new_heading = (new_heading + 180) % 360

    # 修改信息
    new_vehicle['id'] = new_veh_id
    new_vehicle['position'] = (new_x, new_y)
    new_vehicle['heading'] = new_heading
    new_vehicle['vehicle_type'] = 'police'

    return new_vehicle

def add_traffic_accident(states):
    vehicle_infos = states['vehicle'] # 获得车辆的信息
    vehicle_ids = list(vehicle_infos.keys()) # 获得当前所有车辆的 ids

    # 添加新的车辆信息
    for _veh_id in vehicle_ids:
        _veh_info = vehicle_infos[_veh_id] # 获得指定车辆的信息

        new_veh_id = f"{_veh_id}_accident"
        vehicle_infos[new_veh_id] = generate_collision_vehicle(_veh_info, new_veh_id)
    return states