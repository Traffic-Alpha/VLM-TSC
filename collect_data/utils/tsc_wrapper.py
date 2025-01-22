'''
Author: Maonan Wang
Date: 2025-01-15 18:33:20
LastEditTime: 2025-01-22 18:27:56
LastEditors: Maonan Wang
Description: TSC Wrapper for ENV 3D
+ state: 四个方向的图片
+ action: choose next phase
+ reward: 路口总的 waiting time
FilePath: /VLM-TSC/collect_data/utils/tsc_wrapper.py
'''
import copy
import numpy as np
import gymnasium as gym
from gymnasium.core import Env
from collections import deque
from typing import Any, SupportsFloat, Tuple, Dict, List

class OccupancyList:
    def __init__(self) -> None:
        self.elements = []

    def add_element(self, element) -> None:
        if isinstance(element, list):
            if all(isinstance(e, float) for e in element):
                self.elements.append(element)
            else:
                raise ValueError("列表中的元素必须是浮点数类型")
        else:
            raise TypeError("添加的元素必须是列表类型")

    def clear_elements(self) -> None:
        self.elements = []

    def calculate_average(self) -> float:
        """计算一段时间的平均 occupancy
        """
        arr = np.array(self.elements)
        averages = np.mean(arr, axis=0, dtype=np.float32)/100
        self.clear_elements() # 清空列表
        return averages
    

class TSCEnvWrapper(gym.Wrapper):
    """TSC Env Wrapper for single junction with tls_id (collect data)
    """
    def __init__(self, env: Env, tls_id:str, max_states:int=5) -> None:
        super().__init__(env)
        self.tls_id = tls_id
        self.states = deque([self._get_initial_state()] * max_states, maxlen=max_states) # 队列
        self.movement_ids = None
        self.phase2movements = None
        self.occupancy = OccupancyList()

    def _get_initial_state(self) -> List[int]:
        # 返回初始状态，这里假设所有状态都为 0
        return [0]*12
    
    def get_state(self):
        return np.array(self.states, dtype=np.float32)
    
    # #########
    # Wrapper
    # #########
    def state_wrapper(self, state):
        """返回当前每个 movement 的 occupancy
        """
        vector = state['state']['tls']
        pixel = state['pixel']

        occupancy = vector[self.tls_id]['last_step_occupancy']
        can_perform_action = vector[self.tls_id]['can_perform_action']
        
        junction_pixel = np.zeros((4, 240, 360, 3), dtype=np.uint8)
        if (pixel is not None) and (can_perform_action):
            # 将 4 个方向的图像合并在一起
            for i, (_, image) in enumerate(pixel.items()):
                junction_pixel[i] = image['junction_front_all']

        return junction_pixel, occupancy, can_perform_action
    
    def reward_wrapper(self, states) -> float:
        """返回整个路口的排队长度的平均值
        """
        total_waiting_time = 0
        for _, veh_info in states['state']['vehicle'].items():
            total_waiting_time += veh_info['waiting_time']
        return -total_waiting_time
    
    def info_wrapper(self, infos, raw_state):
        """将 info 转换为 dict, 包含环境详细的信息
        """
        infos['state'] = copy.deepcopy(raw_state['state'])
        return infos
    
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
        pixel, occupancy, can_perform_action = self.state_wrapper(state=state)
        self.states.append(occupancy)
        rl_state = self.get_state()

        info = self.info_wrapper(infos={'step_time':0}, raw_state=state)
        return pixel, rl_state, info

    def step(self, action: int):
        can_perform_action = False
        while not can_perform_action:
            action = {self.tls_id: action} # 构建单路口 action 的动作
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            pixel, occupancy, can_perform_action = self.state_wrapper(state=states) # 只需要最后一个时刻的图像
            # 记录每一时刻的数据
            self.occupancy.add_element(occupancy)

        avg_occupancy = self.occupancy.calculate_average()
        rewards = self.reward_wrapper(states=states)
        infos = self.info_wrapper(infos=infos, raw_state=states) # info 需要转换为一个 dict
        self.states.append(avg_occupancy)
        rl_state = self.get_state() # 得到 state

        return {'rl_state':rl_state, 'pixel':pixel}, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()