'''
Author: WANG Maonan
Date: 2025-07-16 17:15:37
LastEditors: WANG Maonan
Description: 根据 Infos 来计算专家动作, 具体的步骤为:
1. 根据 fromEdge_toEdge 获得 lane 对应的 traffic phase 
2. 检测 in lane 是否存在 emergency, police, fire_engine 且距离路口距离小于 20m，则将其修改为绿灯
3. 检测 in lane 存在 safety_barriers, 则将这个 traffic phase 进行 mask, 在剩下的相位进行选择
4. 如果是常规情况, 根据相位内车辆的数量进行决策
LastEditTime: 2025-12-19 14:21:57
'''
class ExpertTrafficSignalController:
    def __init__(self, tls_id: str, raw_infos):
        """特殊情况交通信号专家控制器
        """
        self.tls_id = tls_id

        self.phase2movements = raw_infos['state']['tls'][self.tls_id]['phase2movements']
        self.movement_lane_ids = raw_infos['state']['tls'][self.tls_id]['movement_lane_ids']
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
        
        # 2. 检查路障
        obstacle_phase = self._handle_obstacles(lane_vehicles)
        if obstacle_phase is not None:
            return obstacle_phase
        
        # 3. 没有特殊情况，计算每个相位的车辆数，返回车辆数最多的相位
        return self._select_phase_normal(lane_vehicles)
    
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
                speed = vehicle_data['speed'] # 车辆速度
                waiting_time = vehicle_data['waiting_time'] # 车辆等待事件
                position = lane_length - vehicle_data['lane_position'] # 车道长度 - 所在位置
                
                if lane_id not in lane_vehicles:
                    lane_vehicles[lane_id] = []
                
                lane_vehicles[lane_id].append({
                    'type': vehicle_type,
                    'position': position,
                    'speed': speed,
                    'waiting_time': waiting_time,
                })
        
        return lane_vehicles
    
    def _check_emergency_vehicles(self, lane_vehicles):
        """
        检查是否有需要优先通行的紧急车辆
        """
        EMERGENCY_TYPES = {'emergency', 'police', 'fire_engine'}
        EMERGENCY_THRESHOLD = 150  # 距离路口的距离
        
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
                        closest_phase = self.movement_phase.get(movement, None)
        
        return closest_phase
    
    def _handle_obstacles(self, lane_vehicles):
        """处理路障情况并选择最佳相位
        """
        OBSTACLE_TYPE = [
            'barrier_A', 'barrier_B', 'barrier_C', 'barrier_D', 'barrier_E',
            'tree_branch_1lane', 'tree_branch_3lanes', 'pedestrian', 
            'crash_vehicle_1lane', 'crash_vehicle_3lanes', 'other_accidents',
        ]
        QUEUE_THRESHOLD = 50  # 统计50米内的排队车辆
        
        # 识别有路障的车道
        blocked_lanes = set()
        for lane_id, vehicles in lane_vehicles.items():
            for vehicle in vehicles:
                if vehicle['type'] in OBSTACLE_TYPE:
                    blocked_lanes.add(lane_id)
                    break  # 一个车道有一个路障就足够
        
        # 没有路障时返回 None, 交还给 RL 决策
        if not blocked_lanes:
            return None
        
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
    
    def _select_phase_normal(self, lane_vehicles):
        """根据每个相位的车辆数选择相位
        
        Args:
            lane_vehicles: 按车道分组的车辆信息
            
        Returns:
            车辆数最多的相位
        """
        # 计算每个相位的车辆数
        phase_vehicle_count = {phase: 0 for phase in self.phase2movements.keys()}
        
        for phase, lanes in self.phase_lanes.items():
            for lane_id in lanes:
                # 统计该车道上的所有车辆（排除路障等障碍物）
                if lane_id in lane_vehicles:
                    for vehicle in lane_vehicles[lane_id]:
                        # 只统计正常车辆且正在排队的车辆数
                        if vehicle['speed']<0.1 and vehicle['type'] not in [
                            'barrier_A', 'barrier_B', 'barrier_C', 'barrier_D', 'barrier_E',
                            'tree_branch_1lane', 'tree_branch_3lanes', 'pedestrian',
                            'crash_vehicle_1lane', 'crash_vehicle_3lanes', 'other_accidents'
                        ]:
                            phase_vehicle_count[phase] += 1
                            
        # 返回车辆数最多的相位
        return max(phase_vehicle_count, key=phase_vehicle_count.get)