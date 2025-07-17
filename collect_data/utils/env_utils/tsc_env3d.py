'''
Author: Maonan Wang
Date: 2025-01-15 16:53:53
Description: 信号灯控制环境 3D
LastEditors: WANG Maonan
LastEditTime: 2025-07-17 15:42:31
'''
import gymnasium as gym
from loguru import logger
from typing import List, Dict, Any
from tshub.tshub_env3d.tshub_env3d import Tshub3DEnvironment

class TSCEnvironment3D(gym.Env):
    def __init__(
            self, 
            sumo_cfg:str, net_file:str,
            scenario_glb_dir:str, 
            num_seconds:int, 
            tls_ids:List[str], tls_action_type:str, 
            trip_info:str, # 车辆报告
            # accident & special vehicles
            accident_config:Dict[str, Any],
            special_vehicle_config:Dict[str, Any],
            # 3D Rendering
            preset="1080P", 
            resolution=0.5,
            use_gui:bool=False,
            aircraft_inits:Dict[str, Dict[str, Any]] = None, 
        ) -> None:
        super().__init__()
        # 定义环境信息
        self.tsc_env = Tshub3DEnvironment(
            sumo_cfg=sumo_cfg,
            net_file=net_file, # 需要 network 获得路网拓扑, 从而输出 JSON 文件
            scenario_glb_dir=scenario_glb_dir,
            is_aircraft_builder_initialized=True, # 用于获得路口俯视角度的画面
            aircraft_inits=aircraft_inits, # 飞行器信息, 用于获得路口的俯视信息
            is_vehicle_builder_initialized=True, # 用于获得 vehicle 的 waiting time 来计算 reward
            is_traffic_light_builder_initialized=True,
            is_map_builder_initialized=True,
            is_person_builder_initialized=False,
            tls_ids=tls_ids, 
            num_seconds=num_seconds,
            tls_action_type=tls_action_type,
            trip_info=trip_info,
            use_gui=use_gui,
            is_libsumo=(not use_gui), # 如果不开界面, 就是用 libsumo
            # 下面是用于渲染的参数
            preset=preset,
            resolution=resolution,
            render_mode="offscreen", # 如果设置了 use_render_pipeline, 此时只能是 onscreen
            debuger_print_node=False,
            debuger_spin_camera=False,
            should_count_vehicles=True, # 额外返回场景内车辆位置信息, 用于渲染
            sensor_config={
                'aircraft': {
                    "a1": {"sensor_types": ['aircraft_all']}
                },
                'tls': {
                    tls_ids[0]: {
                        "tls_camera_height": 15,
                        "sensor_types":["junction_front_all"]
                    }
                },
            }, # 需要渲染的图像
        )

        # 特殊事件的配置
        self.accident_configs = accident_config or []
        self.special_vehicle_configs = special_vehicle_config or []

    def reset(self):
        state_infos = self.tsc_env.reset()
        self.conn = self.tsc_env.tshub_env.sumo # 获得 sumo 连接
        new_state = {'state': state_infos, 'pixel': None, 'veh_3d_elements':None}

        # 创建所有事故车辆（立即创建，但设置出发时间）
        for accident in self.accident_configs:
            self._create_accident_vehicle(accident)
        
        # 创建所有特殊车辆（立即创建，但设置出发时间）
        for vehicle in self.special_vehicle_configs:
            self._create_special_vehicle(vehicle)

        return new_state
        
    def step(self, action:Dict[str, Dict[str, int]]):

        action = {
            'vehicle': dict(), 
            'tls': action
        } # 这里只控制 tls 即可
        states, rewards, infos, dones, sensor_datas = self.tsc_env.step(action)
        sensor_data = sensor_datas['image'] # 获得图片数据
        vehicle_elements = sensor_datas['veh_elements'] # 车辆数据
        truncated = dones

        new_state = {'state': states, 'pixel': sensor_data, 'veh_3d_elements':vehicle_elements}
        return new_state, rewards, truncated, dones, infos
    
    def close(self) -> None:
        self.tsc_env.close()
    
    # ====== 特殊场景创建 =======
    def _create_accident_vehicle(self, accident_config):
        """创建事故车辆（直接设置为路障状态）
        """
        veh_id = accident_config["id"]
        edge_id = accident_config["edge_id"]
        lane_index = accident_config["lane_index"]
        position = accident_config["position"]
        duration = accident_config["duration"]
        depart_time = accident_config["depart_time"]
        

        # 创建临时路线
        route_id = f"route_{veh_id}"
        self.conn.route.add(route_id, [edge_id])
        
        # 添加事故车辆（直接设置为路障类型）
        self.conn.vehicle.add(
            vehID=veh_id,
            routeID=route_id,
            typeID="safety_barriers",  # 直接设置为路障类型
            depart=depart_time,  # 在指定时间出现
            departLane=lane_index,
            departPos=position,  # 直接在目标位置出现 (车辆较多的时候无法马上出现)
            departSpeed=0
        )
        
        # 设置停止
        self.conn.vehicle.setStop(
            vehID=veh_id,
            edgeID=edge_id,
            pos=position,
            laneIndex=lane_index,
            duration=duration
        )

        logger.info(f"SIM: 事故路障 {veh_id} 将在 {depart_time} 秒出现在 {edge_id}-{lane_index} 的 {position} 米处")
        return True
    
    def _create_special_vehicle(self, vehicle_config):
        """创建特殊车辆（救护车、警车等）
        """
        veh_id = vehicle_config["id"]
        route_edges = vehicle_config["route"]
        vehicle_type = vehicle_config["type"]
        depart_time = vehicle_config["depart_time"]
        
        # 创建专用路线
        route_id = f"route_{veh_id}"
        self.conn.route.add(route_id, route_edges)
        
        # 添加特殊车辆
        self.conn.vehicle.add(
            vehID=veh_id,
            routeID=route_id,
            typeID=vehicle_type,
            depart=depart_time,  # 在指定时间出发
            departLane=0,  # 默认从第一车道出发
            departPos=0,
            departSpeed=0
        )
        
        logger.info(f"SIM: 特殊车辆 {veh_id} ({vehicle_type}) 将在 {depart_time}秒出发")
        return True