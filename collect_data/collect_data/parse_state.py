'''
Author: Maonan Wang
Date: 2025-01-21 18:37:24
LastEditTime: 2025-01-21 20:11:37
LastEditors: Maonan Wang
Description: 获得图片对应的车辆信息
- tls 获得 in_road_heading, 按从小到大顺序, 就是 Image 的顺序
    - 获得 road 对应的 lane（可以计算车道数）
    - vehicles 筛选出当前 in_road 的车辆
    - 所有 phase 的信息, 和 this phase index
FilePath: /VLM-TSC/collect_data/collect_data/parse_state.py
'''
import copy

def get_direction_info(tls_id:str, raw_infos):
    """将 info 转换为每个方向的信息
    """
    # 把这个拆分为两个部分，有一些是不变的，可以不需要一直进行修改
    infos = None
    infos = copy.deepcopy(raw_infos)
    tls_info, vehicle_info = infos['state']['tls'][tls_id], infos['state']['vehicle']
    sorted_in_road_ids = sorted(tls_info['in_roads_heading'], key=tls_info['in_roads_heading'].get)

    for out_road_id, angle in tls_info['out_roads_heading'].items():
        tls_info['out_roads_heading'][out_road_id] = (angle + 180) % 360
    sorted_out_road_ids = sorted(tls_info['out_roads_heading'], key=tls_info['out_roads_heading'].get)
    
    # 关于 out road 需要 (angle+180)%360 才是对应的 road, 需要旋转 180
    direction_infos = dict()
    for direction_idx, (_in_road_id, _out_road_id) in enumerate(zip(sorted_in_road_ids, sorted_out_road_ids)):
        _direction_info = dict()
        # Road Information
        _direction_info['in_road'] = _in_road_id
        _direction_info['out_road'] = _out_road_id
        _direction_info['in_lanes'] = tls_info['roads_lanes'][_in_road_id]
        _direction_info['out_lanes'] = tls_info['roads_lanes'][_out_road_id]
        # Traffic Light Information
        _direction_info['current_phase'] = tls_info['this_phase_index']
        _direction_info['traffic_phase'] = tls_info['phase2movements']
        # Vehicles
        _direction_vehicles = dict()
        for _veh_id, _veh_info in vehicle_info.items():
            if (_veh_info['road_id'] in sorted_in_road_ids) or (_veh_info['road_id'] in sorted_out_road_ids):
                # 可视距离大致是 25m
                _direction_vehicles[_veh_id] = {
                    'vehicle_type': _veh_info['vehicle_type'],
                    'road_id': _veh_info['road_id'],
                    'lane_id': _veh_info['lane_id'],
                    'lane_position': _veh_info['lane_position'],
                    'event': None # TODO, 这里 event 是按照车辆统计，还是在 road 里面统计
                }
        _direction_info['vehicles'] = _direction_vehicles

        direction_infos[direction_idx] = _direction_info
    
    return direction_infos