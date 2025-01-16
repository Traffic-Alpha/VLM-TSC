'''
Author: Maonan Wang
Date: 2025-01-15 16:53:53
LastEditTime: 2025-01-16 14:37:42
LastEditors: Maonan Wang
Description: 信号灯控制环境 3D
FilePath: /VLM-TSC/pixel_based_rl/utils/tsc_env3d.py
'''
import gymnasium as gym

from typing import List, Dict
from tshub.tshub_env3d.tshub_env3d import Tshub3DEnvironment

class TSCEnvironment3D(gym.Env):
    def __init__(
            self, 
            sumo_cfg:str, scenario_glb_dir:str, 
            num_seconds:int, 
            tls_ids:List[str], tls_action_type:str, 
            use_gui:bool=False
        ) -> None:
        super().__init__()

        self.tsc_env = Tshub3DEnvironment(
            sumo_cfg=sumo_cfg,
            scenario_glb_dir=scenario_glb_dir,
            is_aircraft_builder_initialized=False, 
            is_vehicle_builder_initialized=True, # 用于获得 vehicle 的 waiting time 来计算 reward
            is_traffic_light_builder_initialized=True,
            tls_ids=tls_ids, 
            num_seconds=num_seconds,
            tls_action_type=tls_action_type,
            use_gui=use_gui,
            is_libsumo=(not use_gui), # 如果不开界面, 就是用 libsumo
            # 下面是用于渲染的参数
            render_mode="offscreen", # 如果设置了 use_render_pipeline, 此时只能是 onscreen
            debuger_print_node=False,
            debuger_spin_camera=False,
            sensor_config={
                'tls': ['junction_front_all']
            } # 需要渲染的图像
        )

    def reset(self):
        state_infos = self.tsc_env.reset()
        new_state = {'state': state_infos, 'pixel': None}
        return new_state
        
    def step(self, action:Dict[str, Dict[str, int]]):
        action = {'tls': action} # 这里只控制 tls 即可
        states, rewards, infos, dones, sensor_data = self.tsc_env.step(action)
        truncated = dones

        new_state = {'state': states, 'pixel': sensor_data}
        return new_state, rewards, truncated, dones, infos
    
    def close(self) -> None:
        self.tsc_env.close()