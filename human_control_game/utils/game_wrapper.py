'''
Author: Maonan Wang
Date: 2025-03-31 17:10:14
LastEditTime: 2025-03-31 19:16:27
LastEditors: Maonan Wang
Description: Wrapper for TSC Game Env
FilePath: /VLM-TSC/human_control_game/utils/game_wrapper.py
'''
import numpy as np
import gymnasium as gym
from gymnasium.core import Env

class TSCGameEnvWrapper(gym.Wrapper):
    """TSC Game Env Wrapper for single junction with tls_id (human control)
    """
    def __init__(self, env: Env, tls_id:str) -> None:
        super().__init__(env)
        self.tls_id = tls_id
    
    # #########
    # Wrapper
    # #########
    def state_wrapper(self, state):
        """返回当前每个 movement 的 occupancy
        """
        vector = state['state']['tls']
        can_perform_action = vector[self.tls_id]['can_perform_action']

        pixel = state['pixel']
        junction_front_all = np.zeros((4, 720, 1280, 3), dtype=np.uint8)

        if pixel is not None: # 获得每一个时刻的 image
            for i, (_, image) in enumerate(pixel.items()):
                # 保存 junction_front_all 的原始数据
                if "junction_front_all" in image:
                    junction_front_all[i] = image['junction_front_all']
                else:
                    raise ValueError(f'Only support junction_front_all.')
        
        # 最终输出的图像
        output_pixel = {
            'junction_front_all': junction_front_all,
        }

        return output_pixel, can_perform_action
    
    # ###########
    # ENV Methods
    # ###########
    def reset(self, seed=1):
        """reset 时初始化. 初始的 Image 全部是 0
        """
        state =  self.env.reset()
        # 初始化路口静态信息
        self.movement_ids = state['state']['tls'][self.tls_id]['movement_ids']
        self.phase2movements = state['state']['tls'][self.tls_id]['phase2movements']
        
        # 处理路口动态信息
        pixel, can_perform_action = self.state_wrapper(state=state)

        return pixel

    def step(self, action: int):
        can_perform_action = False
        pixels = list() # 存储一段时间的内容
        while not can_perform_action:
            action = {self.tls_id: action} # 构建单路口 action 的动作
            
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            pixel, can_perform_action = self.state_wrapper(state=states) # 只需要最后一个时刻的图像
            pixels.append(pixel) # 存储每一个时刻的信息

        return pixels, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()