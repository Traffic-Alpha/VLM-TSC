'''
Author: WANG Maonan
Date: 2025-08-14 15:38:00
LastEditors: WANG Maonan
Description: 将 JSON 转换为 QA
LastEditTime: 2025-08-14 16:29:08
'''
# Distance thresholds in meters (adjustable)
CLOSE_RANGE = 30  # Clear visibility zone
MID_RANGE = 60 # Partial visibility

class TrafficLightVQA:
    def __init__(self, data, max_distance:float=30):
        """将 JSON 数据转换为基于模板的 QA 问题对, 这里 max_distance 是指统计的时候只保留这个范围内的车辆
        """
        self.max_distance = max_distance # 只统计 max_distance 范围内的车辆
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
        self.closest_vehicle_distance = 1e4 # 记录距离路口最近的车辆位置, 用于判断当前路口是否有车进入
        for vehicle_id, vehicle_info in self.vehicles.items():
            lane_id = vehicle_info['lane_id']
            lane_position = vehicle_info['lane_position']

            # 根据车道 ID 判断当前车辆是在 in lane 还是 out lane
            if lane_id in self.in_lanes:
                # 在 in lane 上，距离路口的距离 = 车道长度 - 当前车辆的位置
                distance_to_intersection = self.in_lanes[lane_id] - lane_position
                if distance_to_intersection < self.closest_vehicle_distance:
                    self.closest_vehicle_distance = distance_to_intersection

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
        # questions.extend(self._generate_comprehensive()) # 综合问题
        
        return questions
    
    def _generate_qualitative(self):
        """生成**定性** QA 对
        """
        return [
            self._describe_vehicle_behavior_by_traffic_light(), # 当前是否可以通行
            self._generate_existing_special_vehicles(), # 是否包含特殊车辆
            self._generate_existing_accident(), # 是否包含事故
        ]
    
    def _generate_quantitative(self):
        """生成**定量** QA 对
        """
        return [
            self._generate_total_lanes(), # 图片的车道数
            self._generate_total_vehicles_by_distance(), # 图片里面总的车辆数
            self._generate_lane_vehicle_distribution(lane_type='Incoming'), # Incoming 上每个车道的车的数量
            self._generate_lane_vehicle_distribution(lane_type='Outgoing'), # Outgoing 上每个车道的车的数量
        ]
    
    def _generate_comprehensive(self):
        """生成**综合** QA 对
        """
        pass

    # #############
    # 定性问题生成器
    # #############
    def _describe_vehicle_behavior_by_traffic_light(self):
        """Describe vehicle behavior based on known traffic light status.
        Note: Traffic light status is obtained from JSON data (not visible in image).
        
        Returns:
            dict: Contains the generated question and answer describing the scene
        """
        APPROACHING_THRESHOLD = 30
        question = "What are the vehicles in this lane doing? Are they moving or stopped?"
        
        # Get data with safety checks
        in_road = self.data.get('in_road', '')
        traffic_phase = self.data.get('traffic_phase', {})
        current_phase = str(self.data.get('current_phase', ''))
        
        # Determine if current road has green light
        has_green = False
        try:
            current_directions = traffic_phase.get(current_phase, [])
            controlled_lanes = {
                direction.split('--')[0] 
                for direction in current_directions if '--' in direction
            }
            has_green = in_road in controlled_lanes
        except Exception:
            pass
        
        # Generate description
        if self.closest_vehicle_distance >= self.max_distance:
            answer = "The lane is currently clear with no close vehicles near the intersection."
        elif self.closest_vehicle_distance <= APPROACHING_THRESHOLD:
            if has_green:
                answer = "Vehicles are flowing through the intersection with green light."
            else:
                answer = "Vehicles are fully stopped at the red light."
        else:
            if has_green:
                answer = f"Approaching vehicles are maintaining speed toward the green light."
            else:
                answer = f"Distant vehicles ({self.closest_vehicle_distance:.0f}m away) are beginning to slow for the red light."
        
        return {
            'question': question,
            'answer': answer,
        }

    def _generate_existing_special_vehicles(self):
        """生成关于特殊车辆存在与否的问题和答案
        1. 检查图像中是否存在特殊车辆(警车、消防车、救护车等)
        2. 并根据车辆距离路口的位置提供详细信息
        
        Returns:
            dict: 包含生成的问题和答案的字典
        """
        question = "Does the image contain any emergency vehicles such as police cars, ambulances, or fire trucks?"
        
        # 初始化答案为没有特殊车辆
        answer = "No, there are no emergency vehicles in the image."
        closest_distance = float('inf')
        closest_vehicle = None
        
        # 遍历所有车辆寻找特殊车辆
        for v in self.vehicles.values():
            if v['vehicle_type'].lower() in ['police', 'emergency', 'fire_engine']:
                # 更新最近的特殊车辆信息
                if v['distance_to_intersection'] < closest_distance:
                    closest_distance = v['distance_to_intersection']
                    closest_vehicle = v
        
        # 如果找到特殊车辆，构建详细回答
        if closest_vehicle:
            vehicle_type = closest_vehicle['vehicle_type']
            distance = closest_vehicle['distance_to_intersection']
            
            # 将车辆类型转换为更友好的名称
            type_mapping = {
                'police': 'police car',
                'emergency': 'ambulance',
                'fire_engine': 'fire truck',
            }
            friendly_type = type_mapping.get(vehicle_type, vehicle_type)
            
            if distance < self.max_distance:
                if distance < 50:
                    answer = f"Yes, there is a {friendly_type} approaching the junction (about {distance:.1f}m away)."
                else:
                    answer = f"Yes, there is a {friendly_type} in the area, but it's still over 50m away from the junction (about {distance:.1f}m)."
        
        return {'question': question, 'answer': answer}
    
    def _generate_existing_accident(self):
        """是否存在交通事故
        """
        ACCIDENT_TYPES = {
            'barrier_A': 'safety barrier',
            'barrier_B': 'safety barrier',
            'barrier_C': 'safety barrier',
            'barrier_D': 'safety barrier',
            'barrier_E': 'safety barrier',
            'tree_branch_1lane': 'fallen tree branch blocking lanes',
            'tree_branch_3lanes': 'fallen tree branch blocking multiple lanes',
            'pedestrian': 'pedestrian involved incident',
            'crash_vehicle_1lane': 'vehicle collision blocking the lane',
            'crash_vehicle_3lanes': 'multi-vehicle collision blocking multiple lanes',
        }
        
        question = "Is there any traffic accident or obstruction visible in the image?"
        
        # 查找所有事故/障碍物
        accidents = []
        for v in self.vehicles.values():
            if v['vehicle_type'] in ACCIDENT_TYPES:
                accident_desc = ACCIDENT_TYPES[v['vehicle_type']] # 事故的描述
                accidents.append(accident_desc)
        
        # 构建回答
        if accidents:
            if len(accidents) == 1:
                answer = f"Yes, there is {accidents[0]}."
            else:
                accident_list = ", ".join(accidents[:-1]) + " and " + accidents[-1]
                answer = f"Yes, there are multiple incidents: {accident_list}."
        else:
            answer = "No, there are no visible traffic accidents or obstructions."
        
        return {'question': question, 'answer': answer}
    

    # #############
    # 定量问题生成器
    # #############
    def _generate_total_lanes(self):
        """生成总的车道数, 具体到 incoming lanes 和 outgoing lanes
        """
        total = len(self.in_lanes) + len(self.out_lanes)
        question = "How many lanes are there in total (including incoming and outgoing)?"
        answer = f"There are a total of {total} lanes, including {len(self.in_lanes)} incoming lanes and {len(self.out_lanes)} outgoing lanes."
        return {'question': question, 'answer': answer}
    

    def _generate_total_vehicles_by_distance(self):
        """Count vehicles by distance ranges and road direction, with consideration for camera visibility
        
        Returns:
            dict: Contains question and detailed answer about vehicle distribution
        """
        # Initialize counters for each distance range
        incoming_counts = {'close': 0, 'mid': 0, 'far': 0}
        outgoing_counts = {'close': 0, 'mid': 0, 'far': 0}

        for v in self.vehicles.values():
            dist = v['distance_to_intersection']
            if dist > self.max_distance:
                continue  # Beyond reliable detection range
                
            if v['road_id'] == self.in_road:
                if dist <= CLOSE_RANGE:
                    incoming_counts['close'] += 1
                elif dist <= MID_RANGE:
                    incoming_counts['mid'] += 1
                else:
                    incoming_counts['far'] += 1
            elif v['road_id'] == self.out_road:
                if dist <= CLOSE_RANGE:
                    outgoing_counts['close'] += 1
                elif dist <= MID_RANGE:
                    outgoing_counts['mid'] += 1
                else:
                    outgoing_counts['far'] += 1

        # Generate natural language description
        question = "How many vehicles are visible in different areas of the image?"
        
        answer_parts = []
        for direction, counts in [('incoming', incoming_counts), ('outgoing', outgoing_counts)]:
            if sum(counts.values()) > 0:
                dir_text = (
                    f"{direction} road: {counts['close']} clear vehicles nearby, "
                    f"{counts['mid']} somewhat visible vehicles further out"
                )
                if counts['far'] > 0:
                    dir_text += f", and approximately {counts['far']} faint vehicles in the distance"
                
                if direction == 'incoming':
                    dir_text += '. Vehicles exiting the intersection are not counted;'
                answer_parts.append(dir_text)
        
        if not answer_parts:
            answer = "No vehicles are clearly visible in the image."
        else:
            total = sum(incoming_counts.values()) + sum(outgoing_counts.values())
            answer = (
                f"Camera detects {total} vehicles total. "
                f"{' '.join(answer_parts)}. "
                "Note: Distant vehicles may be less accurate due to limited visibility."
            )

        return {
            'question': question,
            'answer': answer,
        }

    def _generate_lane_vehicle_distribution(self, lane_type='Incoming'):
        """Count vehicles per lane with distance-based visibility tiers
        
        Args:
            lane_type: 'Incoming' or 'Outgoing'
        
        Returns:
            dict: Contains question and detailed answer about lane distribution
        """        
        # Select target lanes
        lanes = self.in_lanes if lane_type == 'Incoming' else self.out_lanes
        # Initialize lane statistics
        lane_stats = {
            lane_num: {
                'close': 0, # 0-30m
                'mid': 0, # 30-80m
                'far': 0, # 80-150m
                'total': 0
            }
            for lane_num in range(len(lanes))
        }

        # Count vehicles per distance tier
        for v in self.vehicles.values():
            dist = v['distance_to_intersection'] # 车辆的距离
            lane_id = v['lane_id']
            # 排除不在对应车道和观测不到的车辆
            if dist > self.max_distance or lane_id not in lanes:
                continue
            
            # Extract lane number from lane_id (format: "road_laneNum")
            _, lane_num_str = v['lane_id'].rsplit('_', 1)
            lane_num = int(lane_num_str) # 获得车道
                
            if lane_num in lane_stats:
                if dist <= CLOSE_RANGE:
                    lane_stats[lane_num]['close'] += 1
                elif dist <= MID_RANGE:
                    lane_stats[lane_num]['mid'] += 1
                else:
                    lane_stats[lane_num]['far'] += 1
                lane_stats[lane_num]['total'] += 1

        # Generate natural language description
        question = f"What is the vehicle distribution across {lane_type.lower()} lanes, considering visibility?"
        
        # Build lane-by-lane descriptions
        lane_descriptions = []
        for lane_num, counts in sorted(lane_stats.items()):
            if counts['total'] == 0:
                lane_desc = f"Lane {lane_num}: empty"
            else:
                parts = []
                if counts['close'] > 0:
                    parts.append(f"{counts['close']} clear")
                if counts['mid'] > 0:
                    parts.append(f"{counts['mid']} faint")
                if counts['far'] > 0:
                    parts.append(f"~{counts['far']} very faint")
                lane_desc = f"Lane {lane_num}: {'+'.join(parts)} vehicles"
            lane_descriptions.append(lane_desc)
        
        # Compose final answer
        total_vehicles = sum(v['total'] for v in lane_stats.values())
        
        if total_vehicles == 0:
            answer = f"No vehicles detected on {lane_type.lower()} lanes."
        else:
            if lane_type == 'Incoming':
                visibility_note = "Note: (1) Vehicles exiting the intersection are not counted; (2) Distant vehicles may be less accurate."
            else:
                visibility_note = "Note: Distant vehicles may be less accurate."
            answer = (
                f"Total {total_vehicles} vehicles across {len(lanes)} {lane_type.lower()} lanes. "
                f"{'; '.join(lane_descriptions)}. {visibility_note}"
            )

        return {
            'question': question,
            'answer': answer,
        }