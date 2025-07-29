'''
@Author: WANG Maonan
@Date: 2023-09-08 15:48:26
@Description: Train RL-based TSC
+ State Design: Junction Matrix
+ Action Design: Choose Next Phase 
+ Reward Design: Total Waiting Time
LastEditTime: 2025-07-29 15:18:17
'''
import os
import torch
from loguru import logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger

from utils.env_utils.make_tsc_env import make_env
from utils.training_utils.simple_int import IntersectionNet
from utils.training_utils.sb3_utils import VecNormalizeCallback, linear_schedule

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback

from CONFIG import SCENARIO_CONFIGS

path_convert = get_abs_path(__file__)
logger.remove()
set_logger(path_convert('./'), file_log_level="INFO")

if __name__ == '__main__':
    SCENARIO_IDX = "Beijing_Changjianglu_Test" # 可视化场景, SouthKorea_Songdo, Hongkong_YMT
    config = SCENARIO_CONFIGS.get(SCENARIO_IDX) # 获取特定场景的配置
    SCENARIO_NAME = config["SCENARIO_NAME"]
    SUMOCFG = config["SUMOCFG"] # config 路径名
    PHASE_NUMBER = config["PHASE_NUMBER"] # 绿灯相位数量, action space
    MOVEMENT_NUMBER = config["MOVEMENT_NUMBER"] # 有效 movement 的数量, observation space
    NUM_SECONDS = config["NUM_SECONDS"] # 仿真时间
    JUNCTION_NAME = config["JUNCTION_NAME"]
    
    log_path = path_convert(f'./{SCENARIO_IDX}_log/')
    model_path = path_convert(f'./{SCENARIO_IDX}_models/')
    tensorboard_path = path_convert(f'./{SCENARIO_IDX}_tensorboard/')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    if not os.path.exists(tensorboard_path):
        os.makedirs(tensorboard_path)
    
    # #########
    # Init Env
    # #########
    sumo_cfg = path_convert(f"../exp_networks/{SCENARIO_NAME}/{SUMOCFG}")
    params = {
        'tls_id':JUNCTION_NAME,
        'num_seconds':NUM_SECONDS,
        'phase_num': PHASE_NUMBER,
        'movement_num': MOVEMENT_NUMBER,
        'sumo_cfg':sumo_cfg,
        'use_gui':False,
        'log_file':log_path,
    }
    env = SubprocVecEnv([make_env(env_index=f'{i}', **params) for i in range(12)])
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
        features_extractor_class=IntersectionNet,
        features_extractor_kwargs=dict(features_dim=32),
    )
    model = PPO(
                "MlpPolicy", 
                env, 
                batch_size=64,
                n_steps=320, n_epochs=5, # 每次间隔 n_epoch 去评估一次
                learning_rate=linear_schedule(1e-3),
                verbose=True, 
                policy_kwargs=policy_kwargs, 
                tensorboard_log=tensorboard_path, 
                device=device
            )
    model.learn(total_timesteps=3e5, tb_log_name=f"{SCENARIO_IDX}", callback=callback_list)
    
    # #################
    # 保存 model 和 env
    # #################
    env.save(f'{model_path}/last_vec_normalize.pkl')
    model.save(f'{model_path}/last_rl_model.zip')
    print('训练结束, 达到最大步数.')

    env.close()