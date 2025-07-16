'''
Author: Maonan Wang
Date: 2025-01-21 18:37:24
Description: 将路口信息处理为每个方向的信息
- tls 获得 in_road_heading, 按从小到大顺序, 就是 Image 的顺序
    - 获得 road 对应的 lane（可以计算车道数）
    - vehicles 筛选出当前 in_road 的车辆
    - 所有 phase 的信息, 和 this phase index
LastEditors: WANG Maonan
LastEditTime: 2025-07-16 17:13:45
'''
class TrafficState2DICT(object):
    def __init__(self, tls_id: str, raw_infos):
        """初始化类并计算不变的信息, 需要计算:
        1. in road ids
        2. out road ids
        因为我们图像包含四个方向, 每一个方向包含 in road & out road, 需要匹配方向对应的车道
        """
        self.tls_id = tls_id

        # 获得 incoming and outgoing lanes (这两个需要匹配)
        tls_info = raw_infos['state']['tls'][tls_id]
        self.sorted_in_road_ids = sorted(
            tls_info['in_roads_heading'], 
            key=tls_info['in_roads_heading'].get
        ) # 进入路口的车道 ID
        self.sorted_out_road_ids = self.__calculate_sorted_out_road_ids(tls_info) # 离开路口的车道 ID
    
    def __calculate_sorted_out_road_ids(self, tls_info):
        """计算并返回旋转后的 sorted_out_road_ids
        """
        out_roads_heading = tls_info['out_roads_heading']
        for out_road_id, angle in out_roads_heading.items():
            out_roads_heading[out_road_id] = (angle + 180) % 360
        return sorted(out_roads_heading, key=out_roads_heading.get)
    
    def __call__(self, raw_infos):
        return self.get_direction_info(raw_infos)
    
    # -----

    def get_direction_info(self, raw_infos):
        """将 info 转换为每个方向的信息
        """
        tls_info = raw_infos['state']['tls'][self.tls_id]
        vehicle_info = raw_infos['state']['vehicle']
        lane_info = raw_infos['state']['lane']

        direction_infos = {}
        for direction_idx, (_in_road_id, _out_road_id) in enumerate(zip(self.sorted_in_road_ids, self.sorted_out_road_ids)):
            _direction_info = {
                'in_road': _in_road_id,
                'out_road': _out_road_id,
                'in_lanes': {_lane_id:lane_info[_lane_id]['length'] for _lane_id in tls_info['roads_lanes'][_in_road_id]},
                'out_lanes': {_lane_id:lane_info[_lane_id]['length'] for _lane_id in tls_info['roads_lanes'][_out_road_id]},
                'current_phase': tls_info['this_phase_index'],
                'traffic_phase': tls_info['phase2movements'],
                'vehicles': self._get_direction_vehicles(_in_road_id, _out_road_id, vehicle_info)
            }
            direction_infos[direction_idx] = _direction_info
        return direction_infos

    def _get_direction_vehicles(self, in_road_id, out_road_id, vehicle_info):
        """筛选出当前 in_road 和 out_road 的车辆
        """
        direction_vehicles = {}
        for _veh_id, _veh_info in vehicle_info.items():
            if _veh_info['road_id'] in [in_road_id, out_road_id]:
                direction_vehicles[_veh_id] = {
                    'vehicle_type': _veh_info['vehicle_type'],
                    'road_id': _veh_info['road_id'],
                    'lane_id': _veh_info['lane_id'],
                    'lane_position': _veh_info['lane_position'],
                    'event': None  # TODO: 根据需要添加事件信息
                }
        return direction_vehicles