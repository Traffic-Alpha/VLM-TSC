'''
Author: Maonan Wang
Date: 2025-01-16 18:51:18
LastEditTime: 2025-01-16 19:49:03
LastEditors: Maonan Wang
Description: 加载 Vector State RL 模型, 控制信号的, 但是显示 Image
1. 定义一个环境，可以返回 state, 包括 vector 和 pixel
2. load model, 根据 vector state 返回 action
3. 保存 (pixel, action)
FilePath: /VLM-TSC/collect_data/collect_state_rl.py
'''
import os
import cv2
import torch
from stable_baselines3 import PPO

from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger

from utils.tsc_env3d import TSCEnvironment3D
from utils.tsc_wrapper import TSCEnvWrapper

def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))


def make_env(
        tls_id:str, 
        sumo_cfg:str, 
        scenario_glb_dir:str, 
        num_seconds:int, use_gui:bool,
    ):
    tsc_env = TSCEnvironment3D(
        sumo_cfg=sumo_cfg,
        scenario_glb_dir=scenario_glb_dir,
        num_seconds=num_seconds,
        tls_ids=[tls_id],
        tls_action_type='choose_next_phase',
        use_gui=use_gui
    )
    tsc_env = TSCEnvWrapper(tsc_env, tls_id=tls_id)

    return tsc_env

if __name__ == '__main__':
    tls_id = 'htddj_gsndj'
    sumo_cfg = path_convert("../map/single_junction.sumocfg")
    scenario_glb_dir = path_convert(f"../map/3d_assets")
    camera_dir = path_convert(f"./camera_output/")

    # 1. Load Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = path_convert("../state_based_rl/models/last_rl_model.zip")
    model = PPO.load(model_path, device=device)

    # 2. Init Env
    tsc_env = make_env(
        tls_id=tls_id,
        scenario_glb_dir=scenario_glb_dir,
        num_seconds=300,
        sumo_cfg=sumo_cfg, 
        use_gui=False,
    )

    # Interact with Environment
    dones = False
    step_idx = 0
    pixel, rl_state, _ = tsc_env.reset()
    while not dones:
        action, _ = model.predict(rl_state, deterministic=True)
        action = step_idx % 4
        states, rewards, truncated, dones, infos = tsc_env.step(action=action)
        rl_state, camera_data = states['rl_state'], states['pixel']

        for i, camera_data in enumerate(camera_data):
            image_path = os.path.join(camera_dir, f"{step_idx}_{i}.png")
            cv2.imwrite(image_path, convert_rgb_to_bgr(camera_data))
        
        step_idx += 1
        
    tsc_env.close()