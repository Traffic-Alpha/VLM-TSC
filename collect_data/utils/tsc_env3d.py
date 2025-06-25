'''
Author: Maonan Wang
Date: 2025-01-15 16:53:53
LastEditTime: 2025-06-25 17:32:08
LastEditors: WANG Maonan
Description: 信号灯控制环境 3D
FilePath: /VLM-TSC/collect_data/utils/tsc_env3d.py
'''
import gymnasium as gym

from typing import List, Dict, Callable, Any
from tshub.tshub_env3d.tshub_env3d import Tshub3DEnvironment

class TSCEnvironment3D(gym.Env):
    def __init__(
            self, 
            sumo_cfg:str, net_file:str,
            scenario_glb_dir:str, 
            num_seconds:int, 
            tls_ids:List[str], tls_action_type:str, 
            # 3D Rendering
            preset="1080P", 
            resolution=0.5,
            use_gui:bool=False,
            aircraft_inits:Dict[str, Dict[str, Any]] = None, 
            modify_states_func:Callable[[Any], Any]=None # 用于修改 state, 制造车祸或是噪声
        ) -> None:
        super().__init__()
        
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
            modify_states=modify_states_func
        )

    def reset(self):
        state_infos = self.tsc_env.reset()
        new_state = {'state': state_infos, 'pixel': None, 'veh_3d_elements':None}
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