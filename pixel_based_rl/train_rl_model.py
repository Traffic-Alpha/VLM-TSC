'''
Author: Maonan Wang
Date: 2025-01-15 16:53:24
LastEditTime: 2025-01-16 15:57:38
LastEditors: Maonan Wang
Description: Train RL using pixel input
FilePath: /VLM-TSC/pixel_based_rl/train_rl_model.py
'''
import os
import torch
from loguru import logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger

from utils.make_env3d import make_env
from utils.custom_models import CustomModel
from utils.sb3_utils import VecNormalizeCallback, linear_schedule

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback

path_convert = get_abs_path(__file__)
logger.remove()
set_logger(path_convert('./'), file_log_level="INFO", terminal_log_level="WARNING")

if __name__ == '__main__':
    log_path = path_convert('./log/')
    model_path = path_convert('./models/')
    tensorboard_path = path_convert('./tensorboard/')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    if not os.path.exists(tensorboard_path):
        os.makedirs(tensorboard_path)
    
    # #########
    # Init Env
    # #########
    sumo_cfg = path_convert("../map/single_junction.sumocfg")
    scenario_glb_dir = path_convert(f"../map/3d_assets")
    params = {
        'tls_id':'htddj_gsndj',
        'num_seconds':400,
        'sumo_cfg':sumo_cfg,
        'scenario_glb_dir': scenario_glb_dir,
        'use_gui':False,
        'log_file':log_path,
    }
    env = SubprocVecEnv([make_env(env_index=f'{i}', **params) for i in range(3)])
    env = VecNormalize(env, norm_obs=False, norm_reward=True)

    # #########
    # Callback
    # #########
    checkpoint_callback = CheckpointCallback(
        save_freq=10000, # 多少个 step, 需要根据与环境的交互来决定
        save_path=model_path,
    )
    vec_normalize_callback = VecNormalizeCallback(
        save_freq=10000,
        save_path=model_path,
    ) # 保存环境参数
    callback_list = CallbackList([checkpoint_callback, vec_normalize_callback])

    # #########
    # Training
    # #########
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    policy_kwargs = dict(
        features_extractor_class=CustomModel,
        features_extractor_kwargs=dict(features_dim=512), # 输出特征维度, 接 MLP 输出决策
    )
    model = PPO(
                "CnnPolicy", 
                env, 
                batch_size=64,
                n_steps=300, n_epochs=5, # 每次间隔 n_epoch 去评估一次
                learning_rate=linear_schedule(1e-4),
                verbose=True, 
                policy_kwargs=policy_kwargs, 
                tensorboard_log=tensorboard_path, 
                device=device
            )
    model.learn(total_timesteps=3e5, tb_log_name='TSC-3D', callback=callback_list)
    
    # #################
    # 保存 model 和 env
    # #################
    env.save(f'{model_path}/last_vec_normalize.pkl')
    model.save(f'{model_path}/last_rl_model.zip')
    print('训练结束, 达到最大步数.')

    env.close()