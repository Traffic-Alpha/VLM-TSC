'''
Author: Maonan Wang
Date: 2025-01-15 16:56:15
LastEditTime: 2025-01-16 14:27:19
LastEditors: Maonan Wang
Description: 检查 3D TSC 的环境 (state 和图片是否可以对应上)
FilePath: /VLM-TSC/pixel_based_rl/check_tsc3d.py
'''
import os
import cv2
import numpy as np
from loguru import logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from stable_baselines3.common.env_checker import check_env
from utils.make_env3d import make_env

def convert_rgb_to_bgr(image):
    # Convert an RGB image to BGR
    return image[:, :, ::-1]

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))


if __name__ == '__main__':
    tls_id = 'htddj_gsndj'
    sumo_cfg = path_convert("../map/single_junction.sumocfg")
    scenario_glb_dir = path_convert(f"../map/3d_assets")
    camera_dir = path_convert("./camera_output/")

    log_path = path_convert('./log/')
    tsc_env_generate = make_env(
        tls_id=tls_id,
        scenario_glb_dir=scenario_glb_dir,
        num_seconds=400,
        sumo_cfg=sumo_cfg, 
        use_gui=False,
        log_file=log_path,
        env_index=0,
    )
    tsc_env = tsc_env_generate()

    # Check Env
    print(tsc_env.observation_space.sample())
    print(tsc_env.action_space.n)
    check_env(tsc_env)

    # Simulation with environment
    dones = False
    step_idx = 0
    tsc_env.reset()
    while not dones:
        action = np.random.randint(4)
        states, rewards, truncated, dones, infos = tsc_env.step(action=action)
        logger.info(f"SIM: {infos['step_time']}; \n+Reward:{rewards}.")
        
        for i, camera_data in enumerate(states):
            image_path = os.path.join(camera_dir, f"{step_idx}_{i}.png")
            cv2.imwrite(image_path, convert_rgb_to_bgr(camera_data))
        
        step_idx += 1
        
    tsc_env.close()