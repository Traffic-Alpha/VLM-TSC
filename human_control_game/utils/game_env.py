'''
Author: Maonan Wang
Date: 2025-03-31 16:11:07
LastEditTime: 2025-04-01 10:32:26
LastEditors: Maonan Wang
Description: 信号灯控制游戏
FilePath: /VLM-TSC/human_control_game/utils/game_env.py
'''
import gymnasium as gym

from typing import List, Dict, Callable, Any
from tshub.tshub_env3d.tshub_env3d import Tshub3DEnvironment

class TSCEnvironmentGame3D(gym.Env):
    def __init__(
            self, 
            sumo_cfg:str, net_file:str,
            trip_info:str, summary:str, statistic_output:str,
            scenario_glb_dir:str, 
            num_seconds:int, 
            tls_ids:List[str], tls_action_type:str, 
            preset="720P", resolution=0.5,
            use_gui:bool=False,
            modify_states_func:Callable[[Any], Any]=None # 用于修改 state, 制造车祸或是噪声
        ) -> None:
        super().__init__()
        
        self.tsc_env = Tshub3DEnvironment(
            sumo_cfg=sumo_cfg,
            net_file=net_file,
            scenario_glb_dir=scenario_glb_dir,
            trip_info=trip_info, summary=summary, statistic_output=statistic_output, # 存储性能比较
            tripinfo_output_unfinished=True,
            is_aircraft_builder_initialized=False,
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
            sensor_config={
                'tls': {
                    tls_ids[0]: { # 获得一个路口的信息
                        "tls_camera_height": 15,
                        "sensor_types":["junction_front_all"]
                    }
                },
            }, # 需要渲染的图像
            modify_states=modify_states_func
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