'''
Author: Maonan Wang
Date: 2025-01-15 18:33:20
LastEditTime: 2025-06-26 15:21:55
LastEditors: WANG Maonan
Description: TSC Wrapper for ENV 3D
FilePath: /VLM-TSC/collect_data/utils/tsc_wrapper.py
'''
import copy
import numpy as np
import gymnasium as gym
from gymnasium.core import Env

class TSCEnvWrapper(gym.Wrapper):
    def __init__(self, env: Env, tls_id:str, movement_num:int, max_states_length:int = 7) -> None:
        super().__init__(env)
        self.tls_id = tls_id
        self.movement_ids = None
        self.phase2movements = None

        # state 缓冲区
        self.max_states_length = max_states_length # state 的时间长度
        self.movement_num = movement_num
        self.buffer_idx = 0
        self.states = np.zeros(
            (self.max_states_length, self.movement_num, 6), 
            dtype=np.float32
        )
    
    # ########
    # Wrapper
    # ########
    def state_wrapper(self, state):
        """返回每个时刻每个 movement 的信息
        """
        vector = state['state']['tls'] # 占有率
        pixel = state['pixel'] # 传感器图像
        veh_3d_elements = state['veh_3d_elements'] # 车辆 3D 坐标 

        # 处理特征向量
        tls_state = vector[self.tls_id]
        process_obs = [] # 每一行是一个 movement 的信息, (num_movement, 6)
        for _movement_index, _movement_id in enumerate(self.movement_ids):
            occupancy = tls_state['last_step_occupancy'][_movement_index]/100
            direction_flags = self._direction_to_flags(tls_state['movement_directions'][_movement_id])
            lane_numbers = tls_state['movement_lane_numbers'][_movement_id]/5
            is_now_phase = int(tls_state['this_phase'][_movement_index])
            # 处理完毕一个 traffic phase 的信息
            process_obs.append([occupancy, is_now_phase, *direction_flags, lane_numbers]) # 后面两类变量不变
            
        can_perform_action = vector[self.tls_id]['can_perform_action']

        return pixel, process_obs, veh_3d_elements, can_perform_action
    
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
        infos['state'] = copy.deepcopy(raw_state['state']) # 复制当前环境的 state
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
        pixel, _, veh_3d_elements, _ = self.state_wrapper(state=state)

        info = self.info_wrapper(infos={'step_time':0}, raw_state=state)
        return self.states, pixel, veh_3d_elements, info

    def step(self, action: int):
        can_perform_action = False
        while not can_perform_action:
            action = {self.tls_id: action} # 构建单路口 action 的动作

            # 判断当前是否有事故, 如果没有事故则进行 sample
            # 随机选择一辆 25m 内的车辆，返回车辆 id，同时 sample 一个 15-30s 的事故持续时间
            # 利用 traci 将车辆设置为 stop
            # 在这个车辆附近再添加一辆新的车辆，但是需要重合
            # 如果当前存在事故且持续时间达到, 则去掉 stop 车辆，和新添加的车辆
            
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            pixel, process_obs, veh_3d_elements, can_perform_action = self.state_wrapper(state=states) # 只需要最后一个时刻的图像
            self.states[self.buffer_idx] = np.array(process_obs, dtype=np.float32)
            self.buffer_idx = (self.buffer_idx + 1) % self.max_states_length

        rewards = self.reward_wrapper(states=states)
        infos = self.info_wrapper(infos=infos, raw_state=states) # info 需要转换为一个 dict

        return {'rl_state':self.states, 'pixel':pixel, 'veh_3d_elements':veh_3d_elements}, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()

    def _direction_to_flags(self, direction):
        """
        Convert a direction string to a list of flags indicating the direction.

        :param direction: A string representing the direction (e.g., 's' for straight).
        :return: A list of flags for straight, left, and right.
        """
        return [
            1 if direction == 's' else 0,
            1 if direction == 'l' else 0,
            1 if direction == 'r' else 0
        ]