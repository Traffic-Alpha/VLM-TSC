'''
Author: WANG Maonan
Date: 2025-07-16 17:15:37
LastEditors: WANG Maonan
Description: 根据 Infos 来计算专家动作, 具体的步骤为:
1. 根据 fromEdge_toEdge 获得 lane 对应的 traffic phase 
2. 检测 in lane 是否存在 emergency, police, fire_engine 且距离路口距离小于 20m，则将其修改为绿灯
3. 检测 in lane 存在 safety_barriers, 则将这个 traffic phase 进行 mask

现在你是一个 Python 专家，请你帮助我写出一个专家策略的类给信号灯控制，根据当前环境的信息作出决策，需要有两个特殊场景
1. 当前某个车道存在特殊车辆
2. 当某个车道由于路障无法通行
于是你的思路是类在初始化的时候，首先获得每个 in lane 对应的 traffic phase 和 lane 的长度
你有每个 traffic phase 对应的 movment
'phase2movements': {0: ['1200878753#0--s', '1200878753#0--l', '102454134#0--s'], 1: ['30658263#0--s', '960661806#0--s'], 2: ['30658263#0--r']}
同时你有每一个 movement 对应的车道，如下所是：
'movement_lane_ids': {'1200878753#0--s': ['1200878753#0_0', '1200878753#0_1'], '1200878753#0--l': ['1200878753#0_2', '1200878753#0_2'], '30658263#0--r': ['30658263#0_0', '30658263#0_0'], '30658263#0--s': ['30658263#0_1', '30658263#0_1', '30658263#0_2'], '102454134#0--s': ['102454134#0_0', '102454134#0_1', '102454134#0_2'], '960661806#0--s': ['960661806#0_0', '960661806#0_1', '960661806#0_2']}
同时你还有一个 dict 记录每个 lane 的长度

根据上面的信息你可以获得每个 in lane 所属于的 movement

接着你分析每个时刻的车辆信息，
如果在 in lane 存在 emergency, police, fire_engine，且接近路口，则快速给予绿灯使其通行；
检测 in lane 存在 safety_barriers, 则将这个 traffic phase 进行 mask，在剩下的 traffic phase 选择等待车辆多的 traffic phase
最后输出 traffic phase index
LastEditTime: 2025-07-16 17:17:52
'''

class ExpertTrafficSignalController:
    def __init__(self, tls_id: str, raw_infos):
        """特殊情况交通信号专家控制器
        """
        self.tls_id = tls_id

        self.phase2movements = raw_infos['state']['tls']['J1']['phase2movements']
        self.movement_lane_ids = raw_infos['state']['tls']['J1']['movement_lane_ids']
        self.lane_lengths = raw_infos['state']['lane']
        
        # 构建车道到 movement 的映射
        self.lane_movement = {} # {'1200878753#0_1': '1200878753#0--s', '1200878753#0_0': '1200878753#0--s', ...}
        for movement, lanes in self.movement_lane_ids.items():
            for lane in lanes:
                if lane in self.lane_movement:
                    raise ValueError(f"Lane {lane} is associated with multiple movements")
                self.lane_movement[lane] = movement
        
        # 构建 movement 到相位的映射
        self.movement_phase = {} # {'102454134#0--s': 0, '1200878753#0--s': 0, '1200878753#0--l': 0, '30658263#0--s': 1, '960661806#0--s': 1, '30658263#0--r': 2}
        for phase, movements in self.phase2movements.items():
            for movement in movements:
                if movement in self.movement_phase:
                    raise ValueError(f"Movement {movement} is associated with multiple phases")
                self.movement_phase[movement] = phase
        
        # 构建相位到车道的映射
        self.phase_lanes = {} # {0: {'102454134#0_0', '1200878753#0_0', ...}, 1: {'960661806#0_0', '960661806#0_1', ...}, 2: {'30658263#0_0'}}
        for phase, movements in self.phase2movements.items():
            lanes = set()
            for movement in movements:
                if movement in self.movement_lane_ids:
                    lanes.update(self.movement_lane_ids[movement])
            self.phase_lanes[phase] = lanes
    
    def decide(self, vehicle_info):
        """根据当前车辆信息做出决策
        """
        # 将车辆信息转换为按车道分组的格式
        lane_vehicles = self._group_vehicles_by_lane(vehicle_info)
        
        # 1. 检查特殊车辆 (紧急车辆)
        emergency_phase = self._check_emergency_vehicles(lane_vehicles)
        if emergency_phase is not None:
            return emergency_phase
        
        # 2. 检查路障并选择最佳相位
        return self._handle_obstacles(lane_vehicles)
    
    def _group_vehicles_by_lane(self, vehicle_info):
        """将车辆信息按车道分组
        """
        lane_vehicles = {}
        for vehicle_data in vehicle_info.values():
            lane_id = vehicle_data['lane_id']
            # 只统计 in lanes 的车辆
            if lane_id in self.lane_movement:
                lane_length = self.lane_lengths[lane_id]['length']
                vehicle_type = vehicle_data['vehicle_type']
                position = lane_length - vehicle_data['lane_position'] # 车道长度 - 所在位置
                
                if lane_id not in lane_vehicles:
                    lane_vehicles[lane_id] = []
                
                lane_vehicles[lane_id].append({
                    'type': vehicle_type,
                    'position': position
                })
        
        return lane_vehicles
    
    def _check_emergency_vehicles(self, lane_vehicles):
        """
        检查是否有需要优先通行的紧急车辆
        """
        EMERGENCY_TYPES = {'emergency', 'police', 'fire_engine'}
        EMERGENCY_THRESHOLD = 30  # 距离路口30米内视为紧急
        
        closest_vehicle_dist = float('inf')
        closest_phase = None
        
        for lane_id, vehicles in lane_vehicles.items():
            # 跳过无效车道
            if lane_id not in self.lane_movement:
                continue
            
            for vehicle in vehicles:
                if (vehicle['type'] in EMERGENCY_TYPES and 
                    vehicle['position'] < EMERGENCY_THRESHOLD):
                    
                    # 获取车辆到路口的实际距离
                    distance = vehicle['position']
                    
                    # 更新最近紧急车辆信息
                    if distance < closest_vehicle_dist:
                        closest_vehicle_dist = distance
                        movement = self.lane_movement[lane_id]
                        closest_phase = self.movement_phase[movement]
        
        return closest_phase
    
    def _handle_obstacles(self, lane_vehicles):
        """
        处理路障情况并选择最佳相位
        """
        OBSTACLE_TYPE = 'safety_barriers'
        QUEUE_THRESHOLD = 50  # 统计50米内的排队车辆
        
        # 识别有路障的车道
        blocked_lanes = set()
        for lane_id, vehicles in lane_vehicles.items():
            for vehicle in vehicles:
                if vehicle['type'] == OBSTACLE_TYPE:
                    blocked_lanes.add(lane_id)
                    break  # 一个车道有一个路障就足够
        
        # 确定可用的相位 (没有路障的相位)
        valid_phases = []
        for phase, lanes in self.phase_lanes.items():
            # 检查相位是否包含被阻塞的车道
            if not any(lane in blocked_lanes for lane in lanes):
                valid_phases.append(phase)
        
        # 如果没有可用相位，使用默认的第一个相位
        if not valid_phases:
            return min(self.phase2movements.keys())
        
        # 计算每个有效相位的排队车辆数
        phase_queues = {phase: 0 for phase in valid_phases}
        
        for phase in valid_phases:
            for lane_id in self.phase_lanes[phase]:
                # 只统计有车辆信息的车道
                if lane_id in lane_vehicles:
                    for vehicle in lane_vehicles[lane_id]:
                        # 跳过路障和超过阈值的车辆
                        if (vehicle['type'] != OBSTACLE_TYPE and 
                            vehicle['position'] <= QUEUE_THRESHOLD):
                            phase_queues[phase] += 1
        
        # 选择排队车辆最多的相位
        return max(phase_queues, key=phase_queues.get)