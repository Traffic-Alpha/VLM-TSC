'''
Author: Maonan Wang
Date: 2025-01-15 18:25:07
LastEditTime: 2025-01-15 18:39:50
LastEditors: Maonan Wang
Description: 创建 TSC Env3D + Wrapper
FilePath: /VLM-TSC/pixel_based_rl/utils/make_env3d.py
'''
import gymnasium as gym
from utils.tsc_env3d import TSCEnvironment3D
from utils.tsc_wrapper import TSCEnvWrapper
from stable_baselines3.common.monitor import Monitor

def make_env(
        tls_id:str, scenario_glb_dir:str, 
        num_seconds:int, sumo_cfg:str, use_gui:bool,
        log_file:str, env_index:int,
        ):
    def _init() -> gym.Env: 
        tsc_scenario = TSCEnvironment3D(
            sumo_cfg=sumo_cfg, 
            scenario_glb_dir=scenario_glb_dir,
            num_seconds=num_seconds,
            tls_ids=[tls_id], 
            tls_action_type='choose_next_phase',
            use_gui=use_gui,
        )
        tsc_wrapper = TSCEnvWrapper(tsc_scenario, tls_id=tls_id)
        return Monitor(tsc_wrapper, filename=f'{log_file}/{env_index}')
    
    return _init