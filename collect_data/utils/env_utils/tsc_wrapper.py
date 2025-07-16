'''
Author: Maonan Wang
Date: 2025-01-15 18:33:20
Description: TSC Wrapper for ENV 3D (collect data)
LastEditors: WANG Maonan
LastEditTime: 2025-07-16 19:09:51
'''
import os
import cv2
import copy
import numpy as np
import gymnasium as gym
from gymnasium.core import Env

from utils.save_vector import save_states
from parse_infos.parse_direction_infos import TrafficState2DICT # 将环境信息转换为 JSON
from tshub.utils.format_dict import save_str_to_json

def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

class TSCEnvWrapper(gym.Wrapper):
    def __init__(
            self, 
            env: Env, 
            tls_id:str, 
            movement_num:int, 
            phase_num:int,
            max_states_length:int = 7, 
            base_path: str = None
        ) -> None:
        super().__init__(env)
        self.tls_id = tls_id
        self.movement_ids = None
        self.phase2movements = None

        # state 缓冲区
        self.max_states_length = max_states_length # state 的时间长度
        self.movement_num = movement_num
        self.phase_num = phase_num
        self.buffer_idx = 0
        self.states = np.zeros(
            (self.max_states_length, self.movement_num, 6), 
            dtype=np.float32
        )

        # 每个 step 的信息保存 (图片&JSON)
        self.base_path = base_path
        self.step_idx = 0
        self.can_perform_action_infos = {}

    # ########
    # RL Space
    # ########
    @property
    def action_space(self):
        return gym.spaces.Discrete(self.phase_num)
    
    @property
    def observation_space(self):
        obs_space = gym.spaces.Box(
            low=np.zeros((self.max_states_length, self.movement_num, 6), dtype=np.float32),
            high=np.ones((self.max_states_length, self.movement_num, 6), dtype=np.float32),
            shape=(self.max_states_length, self.movement_num, 6)
        ) # self.states 是一个时间序列
        return obs_space
    
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
    def reset(self, seed=1):
        """reset 时初始化. 初始的 Image 全部是 0
        """
        self.step_idx = 0
        self.can_perform_action_infos = {} # 最后存储全局信息
        state = self.env.reset()

        # 初始化路口静态信息
        self.movement_ids = state['state']['tls'][self.tls_id]['movement_ids']
        self.phase2movements = state['state']['tls'][self.tls_id]['phase2movements']
        
        # 处理路口动态信息
        _, _, _, _ = self.state_wrapper(state=state)

        info = self.info_wrapper(infos={'step_time':0}, raw_state=state)

        # 初始化路口信息, 特征转换器
        self.traffic_state_to_dict = TrafficState2DICT(self.tls_id, info)
        return self.states, info

    def step(self, action: int):
        can_perform_action = False
        action = {self.tls_id: action} # 构建单路口 action 的动作
        while not can_perform_action:
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            pixel, process_obs, veh_3d_elements, can_perform_action = self.state_wrapper(state=states) # 只需要最后一个时刻的图像
            self.states[self.buffer_idx] = np.array(process_obs, dtype=np.float32)
            self.buffer_idx = (self.buffer_idx + 1) % self.max_states_length

            # #################
            # 存储每一个时刻的数据
            # #################

            # info 包含环境完整的信息, 用于转换为 json
            infos = self.info_wrapper(infos=infos, raw_state=states) # info 需要转换为一个 dict
            direction_infos = self.traffic_state_to_dict(infos)

            step_data_path = os.path.join(self.base_path, f"{self.step_idx}")
            low_quality_rgb_path = os.path.join(step_data_path, "low_quality_rgb")
            annotations_path = os.path.join(step_data_path, "annotations") # 存储每一个方向对应的 JSON 文件

            for _path in [step_data_path, low_quality_rgb_path, annotations_path]:
                if not os.path.exists(_path):
                    os.makedirs(_path)

            # -> 每个 step 的总体数据
            step_infp = {
                "time_step": infos['step_time'],
                "action": action[self.tls_id],
                "can_perform_action": can_perform_action
            }
            save_str_to_json(step_infp, os.path.join(step_data_path, "step_info.json"))

            # -> 存储 Vector (RL 的 state)
            save_states(states=self.states, filename=os.path.join(step_data_path, "state_vector.npy"))

            # -> 存储车辆数据
            save_str_to_json(veh_3d_elements, os.path.join(step_data_path, "3d_vehs.json"))

            # -> 存储传感器数据 (图片)
            for element_id, cameras in pixel.items():
                # Iterate over each camera type
                for camera_type, image_array in cameras.items():
                    # Save the numpy array as an image
                    image_path = os.path.join(low_quality_rgb_path, f"{element_id}_{camera_type}.png")
                    cv2.imwrite(image_path, convert_rgb_to_bgr(image_array))

            # -> 存储每个方向的 JSON 数据
            for direction_idx, direction_info in direction_infos.items():
                json_path = os.path.join(annotations_path, f"{direction_idx}.json")
                save_str_to_json(direction_info, json_path)
            
            self.can_perform_action_infos[self.step_idx] = can_perform_action
            self.step_idx += 1

        # 需要返回动作的时候才计算 reward
        rewards = self.reward_wrapper(states=states)

        return self.states, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()