'''
@Author: WANG Maonan
@Date: 2023-09-08 15:49:30
@Description: 处理 TSCHub ENV 中的 state, reward
+ state: 5 个时刻的每一个 movement 的 queue length
+ reward: Waiting Time
LastEditTime: 2025-09-08 16:25:12
'''
import numpy as np
import gymnasium as gym
from gymnasium.core import Env
from typing import Any, SupportsFloat, Tuple, Dict


class TSCEnvWrapper(gym.Wrapper):
    """TSC Env Wrapper for single junction with tls_id
    """
    def __init__(
            self, 
            env: Env, 
            tls_id:str, 
            movement_num:int, 
            phase_num:int,
            max_states_length:int = 7
        ) -> None:
        super().__init__(env)
        self.tls_id = tls_id
        self.movement_ids = None
        self.phase2movements = None
        self.in_roads = None # 进入路口的车道

        # state 缓冲区
        self.max_states_length = max_states_length # state 的时间长度
        self.movement_num = movement_num
        self.phase_num = phase_num
        self.buffer_idx = 0
        self.states = np.zeros(
            (self.max_states_length, self.movement_num, 7), 
            dtype=np.float32
        )
    
    @property
    def action_space(self):
        return gym.spaces.Discrete(self.phase_num)
    
    @property
    def observation_space(self):
        obs_space = gym.spaces.Box(
            low=np.zeros((self.max_states_length, self.movement_num, 7), dtype=np.float32),
            high=np.ones((self.max_states_length, self.movement_num, 7), dtype=np.float32),
            shape=(self.max_states_length, self.movement_num, 7)
        ) # self.states 是一个时间序列
        return obs_space
    
    # ########
    # Wrapper
    # ########
    def state_wrapper(self, state):
        """返回每个时刻每个 movement 的信息
        """
        vector = state['tls'] # 占有率

        # 处理特征向量
        tls_state = vector[self.tls_id]
        process_obs = [] # 每一行是一个 movement 的信息, (num_movement, 7)
        for _movement_index, _movement_id in enumerate(self.movement_ids):
            occupancy = tls_state['last_step_occupancy'][_movement_index]/100 # 占有率, 有车在上面也是占有
            queue_length = tls_state['jam_length_vehicle'][_movement_index]/10 # 车辆停止并且排队
            direction_flags = self._direction_to_flags(tls_state['movement_directions'][_movement_id])
            lane_numbers = tls_state['movement_lane_numbers'][_movement_id]/5
            is_now_phase = int(tls_state['this_phase'][_movement_index]) # s
            # 处理完毕一个 traffic phase 的信息
            process_obs.append([occupancy, queue_length, is_now_phase, *direction_flags, lane_numbers]) # 后面两类变量不变
            
        can_perform_action = vector[self.tls_id]['can_perform_action']

        return process_obs, can_perform_action
    
    def reward_wrapper(self, states) -> float:
        """返回基于平均等待时间的奖励
        """
        vehicle_data = states['vehicle']
        num_vehicles = len(vehicle_data)
        
        # 处理空路口情况（无车辆）
        if num_vehicles == 0:
            return 0.0  # 中性奖励，鼓励保持畅通状态
        
        # 计算总等待时间 (这里需要排除车辆离开路口之后, 进入出口车道, 此时累积等待时间就不要计算了)
        total_waiting_time = 0
        for _, veh_info in vehicle_data.items():
            if veh_info['road_id'] in self.in_roads: # 只统计进口道的车辆
                total_waiting_time += veh_info['accumulated_waiting_time']

        # 计算平均等待时间并返回负值（最小化等待）
        average_waiting_time = total_waiting_time / num_vehicles
        return -average_waiting_time

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
    # ###########
    # ENV Methods
    # ###########
    def reset(self, seed=1) -> Tuple[Any, Dict[str, Any]]:
        """reset 时初始化 (1) 静态信息; (2) 动态信息
        """
        state =  self.env.reset()

        # 初始化路口静态信息
        self.movement_ids = state['tls'][self.tls_id]['movement_ids']
        self.phase2movements = state['tls'][self.tls_id]['phase2movements']
        self.in_roads = state['tls'][self.tls_id]['in_roads']

        # 处理路口动态信息
        _, _ = self.state_wrapper(state=state)

        return self.states, {'step_time':0}
    
    def step(self, action: int) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        can_perform_action = False
        while not can_perform_action:
            action = {self.tls_id: action} # 构建单路口 action 的动作

            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            process_obs, can_perform_action = self.state_wrapper(state=states) # 处理每一帧的数据
            self.states[self.buffer_idx] = np.array(process_obs, dtype=np.float32)
            self.buffer_idx = (self.buffer_idx + 1) % self.max_states_length
        
        # 处理好的时序的 state
        rewards = self.reward_wrapper(states=states) # 计算 vehicle waiting time
        return self.states, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()