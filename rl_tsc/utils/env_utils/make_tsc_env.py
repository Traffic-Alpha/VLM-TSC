'''
@Author: WANG Maonan
@Date: 2023-09-08 17:45:54
@Description: 创建 TSC Env + Wrapper
LastEditTime: 2025-07-10 17:06:27
'''
import gymnasium as gym
from utils.env_utils.tsc_env import TSCEnvironment
from utils.env_utils.tsc_wrapper import TSCEnvWrapper
from stable_baselines3.common.monitor import Monitor

def make_env(
        tls_id:str, num_seconds:int, 
        movement_num:int, phase_num:int,
        sumo_cfg:str, use_gui:bool,
        log_file:str, env_index:int,
    ):
    def _init() -> gym.Env: 
        tsc_scenario = TSCEnvironment(
            sumo_cfg=sumo_cfg, 
            num_seconds=num_seconds,
            tls_ids=[tls_id], 
            tls_action_type='choose_next_phase',
            use_gui=use_gui,
        )
        tsc_wrapper = TSCEnvWrapper(
            tsc_scenario, tls_id=tls_id, 
            movement_num=movement_num, phase_num=phase_num
        )
        return Monitor(tsc_wrapper, filename=f'{log_file}/{env_index}')
    
    return _init