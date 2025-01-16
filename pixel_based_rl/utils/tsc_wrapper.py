'''
Author: Maonan Wang
Date: 2025-01-15 18:33:20
LastEditTime: 2025-01-16 15:11:24
LastEditors: Maonan Wang
Description: TSC Wrapper for ENV 3D
+ state: 四个方向的图片
+ action: choose next phase
+ reward: 路口总的 waiting time
FilePath: /VLM-TSC/pixel_based_rl/utils/tsc_wrapper.py
'''
import numpy as np
import gymnasium as gym
from gymnasium.core import Env

class TSCEnvWrapper(gym.Wrapper):
    """TSC Env Wrapper for single junction with tls_id
    """
    def __init__(self, env: Env, tls_id:str) -> None:
        super().__init__(env)
        self.tls_id = tls_id

    @property
    def action_space(self):
        return gym.spaces.Discrete(4)
    
    @property
    def observation_space(self):
        obs_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=(4,240,360,3)
        ) # 4 个方向, 每个方向有一个图像大小是 
        return obs_space

    # #########
    # Wrapper
    # #########
    def state_wrapper(self, state):
        """返回当前每个 movement 的 occupancy
        """
        vector = state['state']['tls']
        pixel = state['pixel']

        can_perform_action = vector[self.tls_id]['can_perform_action']
        
        junction_pixel = np.zeros((4, 240, 360, 3), dtype=np.uint8)
        if (pixel is not None) and (can_perform_action):
            # 将 4 个方向的图像合并在一起
            for i, (_, image) in enumerate(pixel.items()):
                junction_pixel[i] = image['junction_front_all']

        return junction_pixel, can_perform_action
    
    def reward_wrapper(self, states) -> float:
        """返回整个路口的排队长度的平均值
        """
        total_waiting_time = 0
        for _, veh_info in states['state']['vehicle'].items():
            total_waiting_time += veh_info['waiting_time']
        return -total_waiting_time
    
    def info_wrapper(self, infos):
        """将 info 转换为 dict
        """
        infos['other'] = None
        return infos
    
    # ###########
    # ENV Methods
    # ###########
    def reset(self, seed=1):
        """reset 时初始化. 初始的 Image 全部是 0
        """
        state =  self.env.reset()
        pixel, can_perform_action = self.state_wrapper(state)
        return pixel, {'step_time':0}

    def step(self, action: int):
        can_perform_action = False
        while not can_perform_action:
            action = {self.tls_id: action} # 构建单路口 action 的动作
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            pixel, can_perform_action = self.state_wrapper(state=states) # 只需要最后一个时刻的图像
        
        rewards = self.reward_wrapper(states=states)
        infos = self.info_wrapper(infos) # info 需要转换为一个 dict

        return pixel, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()